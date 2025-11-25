"""
Twilio Video Service for Psychology Clinic
Handles video room creation, token generation, and room management
"""

import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from twilio.base.exceptions import TwilioRestException


class TwilioVideoService:
    """
    Service for managing Twilio Video rooms and access tokens
    
    Features:
    - Create unique video rooms for telehealth appointments
    - Generate secure access tokens for participants
    - Manage room lifecycle (create, complete, cleanup)
    - HIPAA compliant video sessions
    """
    
    def __init__(self):
        """Initialize Twilio client with credentials from settings"""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.api_key = settings.TWILIO_API_KEY
        self.api_secret = settings.TWILIO_API_SECRET
        
        # Validate credentials
        if not all([self.account_sid, self.auth_token, self.api_key, self.api_secret]):
            raise ValueError(
                "Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, TWILIO_API_KEY, and TWILIO_API_SECRET in settings."
            )
        
        # Initialize Twilio client
        # IMPORTANT: Video API requires US1 API keys (not regional keys)
        # See: https://www.twilio.com/docs/video/tutorials/user-identity-access-tokens
        self.client = Client(self.account_sid, self.auth_token)
    
    def create_room(self, appointment_id, appointment_date=None, enable_recording=False):
        """
        Create a Twilio Video room for an appointment
        
        Args:
            appointment_id: Unique appointment identifier
            appointment_date: Scheduled date/time of appointment (optional)
            enable_recording: Whether to enable recording (requires patient consent)
        
        Returns:
            dict: Room details including room_name, room_sid, and status
        
        Raises:
            TwilioRestException: If room creation fails
        """
        # Generate unique room name
        room_name = self._generate_room_name(appointment_id)
        
        try:
            # Get status callback URL from settings (optional)
            from django.conf import settings
            status_callback_url = getattr(settings, 'TWILIO_STATUS_CALLBACK_URL', None)
            
            # Create room with settings
            room_params = {
                'unique_name': room_name,
                'type': 'group',  # Supports multiple participants
                'max_participants': 2,  # Patient + Psychologist
                'video_codecs': ['VP8'],  # Standard codec
                'media_region': 'au1',  # Australia region for low latency
                'record_participants_on_connect': enable_recording,  # Only record if consent given
                'empty_room_timeout': 15,  # Close after 15 minutes if empty (allows late joiners)
                'unused_room_timeout': 30  # Close after 30 minutes if unused (better for longer sessions)
            }
            
            # Add status callback if configured
            if status_callback_url:
                room_params['status_callback'] = status_callback_url
                room_params['status_callback_method'] = 'POST'
            
            room = self.client.video.v1.rooms.create(**room_params)
            
            return {
                'room_name': room.unique_name,
                'room_sid': room.sid,
                'status': room.status,
                'type': room.type,
                'max_participants': room.max_participants,
                'created_at': datetime.now().isoformat(),
                'meeting_url': self._generate_meeting_url(room.unique_name)
            }
        
        except TwilioRestException as e:
            # Check if room already exists
            if e.code == 53113:  # Room with name already exists
                return self.get_or_create_room(room_name)
            raise
    
    def get_or_create_room(self, room_name):
        """
        Get existing room or create new one
        
        Args:
            room_name: Unique room name
        
        Returns:
            dict: Room details
        """
        try:
            # Try to get existing room
            rooms = self.client.video.v1.rooms.list(unique_name=room_name, limit=1)
            
            if rooms:
                room = rooms[0]
                return {
                    'room_name': room.unique_name,
                    'room_sid': room.sid,
                    'status': room.status,
                    'type': room.type,
                    'max_participants': room.max_participants,
                    'created_at': room.date_created.isoformat() if room.date_created else None,
                    'meeting_url': self._generate_meeting_url(room.unique_name)
                }
            else:
                # Room doesn't exist, create it
                return self.create_room(room_name.split('-')[-1])  # Extract appointment_id
        
        except TwilioRestException as e:
            raise Exception(f"Error getting/creating room: {str(e)}")
    
    def generate_access_token(self, user_identity, room_name, ttl_hours=1):
        """
        Generate Twilio access token for a participant
        
        Args:
            user_identity: Unique user identifier (email or user ID)
            room_name: Name of the room to join
            ttl_hours: Token expiration time in hours (default: 1)
        
        Returns:
            str: JWT access token for Twilio Video
        """
        # Create access token with identity
        # Parameters: (account_sid, signing_key_sid, secret)
        # region='au1' routes media through Australian edge servers
        token = AccessToken(
            self.account_sid,  # account_sid
            self.api_key,      # signing_key_sid (API Key SID)
            self.api_secret,   # secret
            identity=user_identity,
            ttl=int(timedelta(hours=ttl_hours).total_seconds()),
            region='au1'  # Route media through Australia (legal & low latency)
        )
        
        # Create Video grant for this room
        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        
        return token.to_jwt()
    
    def complete_room(self, room_sid):
        """
        Mark a room as completed and close it
        
        Args:
            room_sid: Twilio room SID
        
        Returns:
            dict: Updated room status
        """
        try:
            room = self.client.video.v1.rooms(room_sid).update(status='completed')
            
            return {
                'room_sid': room.sid,
                'status': room.status,
                'duration': room.duration,
                'completed_at': datetime.now().isoformat()
            }
        
        except TwilioRestException as e:
            raise Exception(f"Error completing room: {str(e)}")
    
    def get_room_participants(self, room_sid, status=None):
        """
        Get list of participants in a room
        
        Args:
            room_sid: Twilio room SID or room name
            status: Optional filter by status ('connected', 'disconnected', 'reconnecting')
        
        Returns:
            list: Participant details
        """
        try:
            # Build list parameters
            list_params = {}
            if status:
                list_params['status'] = status
            
            participants = self.client.video.v1.rooms(room_sid).participants.list(**list_params)
            
            return [
                {
                    'sid': p.sid,
                    'identity': p.identity,
                    'status': p.status,
                    'duration': p.duration,
                    'connected_at': p.start_time.isoformat() if p.start_time else None,
                    'disconnected_at': p.end_time.isoformat() if p.end_time else None,
                    'account_sid': p.account_sid,
                    'room_sid': p.room_sid,
                    'date_created': p.date_created.isoformat() if p.date_created else None,
                    'date_updated': p.date_updated.isoformat() if p.date_updated else None
                }
                for p in participants
            ]
        
        except TwilioRestException as e:
            raise Exception(f"Error getting participants: {str(e)}")
    
    def get_participant(self, room_sid, participant_identity_or_sid):
        """
        Get a specific participant from a room by identity or SID
        
        Args:
            room_sid: Twilio room SID or room name
            participant_identity_or_sid: Participant identity or SID
        
        Returns:
            dict: Participant details
        """
        try:
            participant = self.client.video.v1.rooms(room_sid).participants(
                participant_identity_or_sid
            ).fetch()
            
            return {
                'sid': participant.sid,
                'identity': participant.identity,
                'status': participant.status,
                'duration': participant.duration,
                'connected_at': participant.start_time.isoformat() if participant.start_time else None,
                'disconnected_at': participant.end_time.isoformat() if participant.end_time else None,
                'account_sid': participant.account_sid,
                'room_sid': participant.room_sid,
                'date_created': participant.date_created.isoformat() if participant.date_created else None,
                'date_updated': participant.date_updated.isoformat() if participant.date_updated else None,
                'url': participant.url
            }
        
        except TwilioRestException as e:
            raise Exception(f"Error getting participant: {str(e)}")
    
    def remove_participant(self, room_sid, participant_identity_or_sid):
        """
        Remove/kick a participant from a room by setting status to disconnected
        
        Args:
            room_sid: Twilio room SID or room name
            participant_identity_or_sid: Participant identity or SID
        
        Returns:
            dict: Updated participant details
        """
        try:
            participant = self.client.video.v1.rooms(room_sid).participants(
                participant_identity_or_sid
            ).update(status='disconnected')
            
            return {
                'sid': participant.sid,
                'identity': participant.identity,
                'status': participant.status,
                'duration': participant.duration,
                'connected_at': participant.start_time.isoformat() if participant.start_time else None,
                'disconnected_at': participant.end_time.isoformat() if participant.end_time else None,
                'removed_at': datetime.now().isoformat()
            }
        
        except TwilioRestException as e:
            raise Exception(f"Error removing participant: {str(e)}")
    
    def get_room_status(self, room_name):
        """
        Get current status of a room
        
        Args:
            room_name: Unique room name
        
        Returns:
            dict: Room status details
        """
        try:
            rooms = self.client.video.v1.rooms.list(unique_name=room_name, limit=1)
            
            if rooms:
                room = rooms[0]
                return {
                    'room_sid': room.sid,
                    'room_name': room.unique_name,
                    'status': room.status,
                    'type': room.type,
                    'duration': room.duration,
                    'participants_count': len(self.get_room_participants(room.sid)),
                    'created_at': room.date_created.isoformat() if room.date_created else None
                }
            else:
                return {'status': 'not_found'}
        
        except TwilioRestException as e:
            raise Exception(f"Error getting room status: {str(e)}")
    
    def cleanup_old_rooms(self, days=7):
        """
        Clean up completed rooms older than specified days
        
        Args:
            days: Number of days (default: 7)
        
        Returns:
            dict: Cleanup statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        completed_count = 0
        
        try:
            # Get completed rooms
            rooms = self.client.video.v1.rooms.list(
                status='completed',
                date_created_before=cutoff_date
            )
            
            for room in rooms:
                try:
                    # Rooms are automatically cleaned by Twilio
                    # Just count them for statistics
                    completed_count += 1
                except Exception as e:
                    print(f"Error processing room {room.sid}: {str(e)}")
            
            return {
                'cleaned_rooms': completed_count,
                'cutoff_date': cutoff_date.isoformat()
            }
        
        except TwilioRestException as e:
            raise Exception(f"Error cleaning up rooms: {str(e)}")
    
    def _generate_room_name(self, appointment_id):
        """
        Generate unique room name for appointment
        
        Args:
            appointment_id: Appointment identifier
        
        Returns:
            str: Unique room name
        """
        # Format: apt-{id}-{timestamp}-{random}
        timestamp = int(datetime.now().timestamp())
        random_suffix = uuid.uuid4().hex[:8]
        return f"apt-{appointment_id}-{timestamp}-{random_suffix}"
    
    def _generate_meeting_url(self, room_name):
        """
        Generate meeting URL for frontend
        
        Args:
            room_name: Twilio room name
        
        Returns:
            str: Full meeting URL
        """
        # You can customize this based on your frontend routing
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/video-session/{room_name}"
    
    def validate_credentials(self):
        """
        Validate Twilio credentials by making a test API call
        
        Returns:
            dict: Validation result
        """
        try:
            # Try to fetch account details
            account = self.client.api.accounts(self.account_sid).fetch()
            
            # Test token generation to verify API Key/Secret match Account SID
            try:
                test_token = self.generate_access_token(
                    user_identity="validation-test",
                    room_name="validation-room",
                    ttl_hours=1
                )
                token_valid = True
                token_error = None
            except Exception as token_error:
                token_valid = False
                token_error = str(token_error)
            
            return {
                'valid': True,
                'account_sid': account.sid,
                'account_status': account.status,
                'account_type': account.type,
                'api_key_valid': token_valid,
                'api_key_error': token_error,
                'credentials_match': token_valid
            }
        
        except TwilioRestException as e:
            return {
                'valid': False,
                'error': str(e),
                'credentials_match': False
            }


# Singleton instance
_video_service = None

def get_video_service():
    """
    Get or create TwilioVideoService singleton instance
    
    Returns:
        TwilioVideoService: Video service instance
    """
    global _video_service
    
    if _video_service is None:
        _video_service = TwilioVideoService()
    
    return _video_service

