"""
PDF Invoice Generation Service for Psychology Clinic
Uses reportlab to generate professional invoice PDFs with Australian compliance
"""

from io import BytesIO
from decimal import Decimal
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas
from django.conf import settings
from django.utils import timezone


class InvoicePDFService:
    """
    Service for generating professional invoice PDFs
    Includes Australian GST compliance, Medicare information, and clinic branding
    """
    
    def __init__(self):
        """Initialize PDF service with clinic information"""
        self.clinic_name = getattr(settings, 'CLINIC_NAME', 'Psychology Clinic')
        self.clinic_address = getattr(settings, 'CLINIC_ADDRESS', '')
        self.clinic_phone = getattr(settings, 'CLINIC_PHONE', '')
        self.clinic_email = getattr(settings, 'CLINIC_EMAIL', '')
        self.clinic_website = getattr(settings, 'CLINIC_WEBSITE', '')
        self.clinic_abn = getattr(settings, 'CLINIC_ABN', '')
        self.gst_rate = getattr(settings, 'GST_RATE', 0.10)
    
    def generate_invoice_pdf(self, invoice):
        """
        Generate PDF invoice for an invoice instance
        
        Args:
            invoice: Invoice model instance
            
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build PDF content
        story = []
        
        # Add header
        story.extend(self._create_header(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add invoice details
        story.extend(self._create_invoice_details(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add patient information
        story.extend(self._create_patient_info(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add service details
        story.extend(self._create_service_details(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add financial breakdown
        story.extend(self._create_financial_breakdown(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add payment information
        story.extend(self._create_payment_info(invoice))
        story.append(Spacer(1, 10*mm))
        
        # Add footer
        story.extend(self._create_footer(invoice))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        buffer.seek(0)
        return buffer
    
    def _create_header(self, invoice):
        """Create invoice header with clinic information"""
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Header content
        header_data = [
            [Paragraph(f"<b>{self.clinic_name}</b>", title_style), ""],
        ]
        
        # Add clinic details if available
        clinic_details = []
        if self.clinic_address:
            clinic_details.append(self.clinic_address)
        if self.clinic_phone:
            clinic_details.append(f"Phone: {self.clinic_phone}")
        if self.clinic_email:
            clinic_details.append(f"Email: {self.clinic_email}")
        if self.clinic_website:
            clinic_details.append(f"Website: {self.clinic_website}")
        if self.clinic_abn:
            clinic_details.append(f"ABN: {self.clinic_abn}")
        
        if clinic_details:
            details_text = "<br/>".join(clinic_details)
            header_data.append([Paragraph(details_text, styles['Normal']), ""])
        
        # Add "INVOICE" label on the right
        invoice_label_style = ParagraphStyle(
            'InvoiceLabel',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#1a5490'),
            alignment=TA_RIGHT
        )
        header_data[0][1] = Paragraph("<b>INVOICE</b>", invoice_label_style)
        
        # Create table
        header_table = Table(header_data, colWidths=[120*mm, 60*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        return [header_table]
    
    def _create_invoice_details(self, invoice):
        """Create invoice number and date section"""
        styles = getSampleStyleSheet()
        
        invoice_date = invoice.service_date.strftime('%d %B %Y')
        due_date = invoice.due_date.strftime('%d %B %Y')
        created_date = invoice.created_at.strftime('%d %B %Y')
        
        details_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Invoice Date:', invoice_date],
            ['Due Date:', due_date],
            ['Status:', invoice.get_status_display().upper()],
        ]
        
        if invoice.paid_date:
            details_data.append(['Paid Date:', invoice.paid_date.strftime('%d %B %Y')])
        
        details_table = Table(details_data, colWidths=[50*mm, 130*mm])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return [details_table]
    
    def _create_patient_info(self, invoice):
        """Create patient information section"""
        styles = getSampleStyleSheet()
        
        patient = invoice.patient
        
        patient_data = [
            ['Bill To:', ''],
            ['Name:', patient.get_full_name()],
            ['Email:', patient.email],
        ]
        
        if patient.phone_number:
            patient_data.append(['Phone:', patient.phone_number])
        
        if hasattr(patient, 'patientprofile'):
            profile = patient.patientprofile
            if profile.emergency_contact_name:
                patient_data.append(['Emergency Contact:', profile.emergency_contact_name])
        
        if patient.medicare_number:
            patient_data.append(['Medicare Number:', patient.medicare_number])
        
        # Add address if available
        if patient.address_line_1:
            address_parts = [patient.address_line_1]
            if patient.suburb:
                address_parts.append(patient.suburb)
            if patient.state:
                address_parts.append(patient.state)
            if patient.postcode:
                address_parts.append(patient.postcode)
            patient_data.append(['Address:', ', '.join(address_parts)])
        
        patient_table = Table(patient_data, colWidths=[50*mm, 130*mm])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
        ]))
        
        return [patient_table]
    
    def _create_service_details(self, invoice):
        """Create service details table"""
        styles = getSampleStyleSheet()
        
        appointment = invoice.appointment
        psychologist = appointment.psychologist
        
        # Get psychologist title if available
        psychologist_name = psychologist.get_full_name()
        if hasattr(psychologist, 'psychologist_profile') and psychologist.psychologist_profile.title:
            psychologist_name = f"{psychologist.psychologist_profile.title} {psychologist_name}"
        
        service_data = [
            ['Description', 'Details'],
            [
                'Service:',
                invoice.service_description
            ],
            [
                'Service Date:',
                invoice.service_date.strftime('%d %B %Y')
            ],
            [
                'Psychologist:',
                psychologist_name
            ],
            [
                'Session Type:',
                appointment.get_session_type_display()
            ],
            [
                'Duration:',
                f"{appointment.duration_minutes} minutes"
            ],
        ]
        
        if invoice.medicare_item_number:
            service_data.append([
                'Medicare Item:',
                f"{invoice.medicare_item_number.item_number} - {invoice.medicare_item_number.description}"
            ])
        
        service_table = Table(service_data, colWidths=[50*mm, 130*mm])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        return [service_table]
    
    def _create_financial_breakdown(self, invoice):
        """Create financial breakdown table with GST and Medicare"""
        styles = getSampleStyleSheet()
        
        # Format currency
        def format_currency(amount):
            return f"${float(amount):.2f}"
        
        financial_data = [
            ['Item', 'Amount (AUD)'],
            ['Subtotal (ex. GST):', format_currency(invoice.subtotal_amount)],
            [f'GST ({int(self.gst_rate * 100)}%):', format_currency(invoice.gst_amount)],
            ['Total (inc. GST):', format_currency(invoice.total_amount)],
        ]
        
        if invoice.medicare_rebate > 0:
            financial_data.append(['Medicare Rebate:', f"-{format_currency(invoice.medicare_rebate)}"])
        
        financial_data.append([
            '<b>Amount Due:</b>',
            f"<b>{format_currency(invoice.out_of_pocket)}</b>"
        ])
        
        financial_table = Table(financial_data, colWidths=[130*mm, 50*mm])
        financial_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8e8e8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.grey),
        ]))
        
        return [financial_table]
    
    def _create_payment_info(self, invoice):
        """Create payment information section"""
        styles = getSampleStyleSheet()
        
        payment_info = []
        
        if invoice.status == 'paid' and invoice.paid_date:
            payment_info.append(Paragraph(
                f"<b>Payment Status:</b> Paid on {invoice.paid_date.strftime('%d %B %Y')}",
                styles['Normal']
            ))
        else:
            payment_info.append(Paragraph(
                f"<b>Payment Due:</b> {invoice.due_date.strftime('%d %B %Y')}",
                styles['Normal']
            ))
        
        if invoice.status == 'overdue' or invoice.is_overdue:
            overdue_style = ParagraphStyle(
                'Overdue',
                parent=styles['Normal'],
                textColor=colors.red,
                fontSize=12,
                fontName='Helvetica-Bold'
            )
            payment_info.append(Paragraph(
                "<b>⚠️ OVERDUE - Please pay immediately</b>",
                overdue_style
            ))
        
        payment_info.append(Spacer(1, 5*mm))
        payment_info.append(Paragraph(
            "<b>Payment Methods:</b>",
            styles['Normal']
        ))
        payment_info.append(Paragraph(
            "• Credit/Debit Card (via online portal)<br/>"
            "• Bank Transfer<br/>"
            "• Medicare (if applicable)<br/>"
            "• Cash (in-person only)",
            styles['Normal']
        ))
        
        return payment_info
    
    def _create_footer(self, invoice):
        """Create footer with terms and conditions"""
        styles = getSampleStyleSheet()
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer_text = []
        
        if self.clinic_abn:
            footer_text.append(f"ABN: {self.clinic_abn}")
        
        footer_text.append("This invoice includes GST as required by Australian tax law.")
        footer_text.append("Payment is due within 30 days of invoice date unless otherwise specified.")
        
        if invoice.medicare_rebate > 0:
            footer_text.append("Medicare rebate has been applied to this invoice.")
        
        footer_text.append("For payment inquiries, please contact us at the details above.")
        
        footer_content = [Spacer(1, 10*mm)]
        footer_content.append(Paragraph("<br/>".join(footer_text), footer_style))
        
        return footer_content
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page number to PDF pages"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(190*mm, 10*mm, text)
        canvas_obj.restoreState()

