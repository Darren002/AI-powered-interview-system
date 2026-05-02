import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

class EmailService:
    """
    Email service for sending assessment notifications.
    
    To enable:
    1. Set environment variables in .env:
       - SMTP_HOST=smtp.gmail.com
       - SMTP_PORT=587
       - SMTP_USER=your-email@gmail.com
       - SMTP_PASSWORD=your-app-password
       - FROM_NAME=CyberHire AI
    
    2. Or use a transactional email service (SendGrid, Resend, etc.)
    """
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_name = os.getenv('FROM_NAME', 'CyberHire AI')
        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)
    
    def send_completion_email(self, to_email: str, candidate_name: str, score: float, percentage: float) -> bool:
        """
        Send interview completion email to candidate
        
        Args:
            to_email: Candidate's email
            candidate_name: Candidate's name
            score: Overall score (0-25)
            percentage: Percentage score
            
        Returns:
            True if sent successfully, False otherwise
        """
        
        if not self.enabled:
            print(f"[Email] Would send completion email to {to_email}")
            print(f"[Email] Score: {score:.1f}/25 ({percentage:.0f}%)")
            return True
        
        # Determine rating
        if percentage >= 80:
            rating = "Outstanding"
        elif percentage >= 60:
            rating = "Strong"
        elif percentage >= 40:
            rating = "Qualified"
        else:
            rating = "Needs Development"
        
        subject = f"CyberHire AI Assessment Complete - Your Results"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #14b8a6, #0d9488); color: white; padding: 30px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .score-box {{ background: white; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0; }}
                .score {{ font-size: 48px; font-weight: bold; color: #14b8a6; }}
                .rating {{ font-size: 24px; color: #666; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>CyberHire AI</h1>
                    <p>Assessment Complete</p>
                </div>
                <div class="content">
                    <h2>Hi {candidate_name},</h2>
                    
                    <p>Thank you for completing the CyberHire AI assessment. Your results are ready!</p>
                    
                    <div class="score-box">
                        <div class="score">{score:.1f}/25</div>
                        <div class="rating">{rating}</div>
                        <p>{percentage:.0f}%</p>
                    </div>
                    
                    <p>Your detailed assessment report is available in the HR dashboard. 
                    The HR team will review your results and get back to you soon.</p>
                    
                    <p>If you have any questions, please contact the HR team directly.</p>
                    
                    <p>Best regards,<br>The CyberHire AI Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from CyberHire AI Assessment System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Hi {candidate_name},
        
        Thank you for completing the CyberHire AI assessment. Your results are ready!
        
        Your Score: {score:.1f}/25 ({percentage:.0f}%)
        Rating: {rating}
        
        Your detailed assessment report is available in the HR dashboard. 
        The HR team will review your results and get back to you soon.
        
        Best regards,
        The CyberHire AI Team
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Internal method to send email via SMTP"""
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.smtp_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Connect to SMTP server and send
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"[Email] Sent completion email to {to_email}")
            return True
            
        except Exception as e:
            print(f"[Email] Failed to send email: {e}")
            return False


# Global instance
email_service = EmailService()


def send_completion_email(to_email: str, candidate_name: str, score: float, percentage: float) -> bool:
    """Convenience function to send completion email"""
    return email_service.send_completion_email(to_email, candidate_name, score, percentage)
