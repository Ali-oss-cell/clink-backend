# Test Twilio Video Configuration

## Quick Test Commands

Copy and paste these commands **one at a time** into the Python shell (no indentation):

```python
from appointments.video_service import get_video_service
```

```python
video_service = get_video_service()
```

```python
result = video_service.validate_credentials()
```

```python
print(result)
```

---

## Expected Output

If everything is configured correctly, you should see:

```python
{
    'valid': True,
    'account_sid': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'account_status': 'active',
    'account_type': 'Full',
    'api_key_valid': True,
    'api_key_error': None,
    'credentials_match': True
}
```

---

## Troubleshooting

### If `api_key_valid: False`:
- Check that `TWILIO_API_SECRET` is correct in `.env`
- Verify API Key SID matches the Account SID
- Try creating a new API Key

### If `valid: False`:
- Check that `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are correct
- Verify credentials are in `.env` file
- Restart Gunicorn: `sudo systemctl restart gunicorn`

