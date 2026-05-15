import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class FreeEmailSender:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def send_email(self, subject, body, recipient_email):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))  

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            print(f"Email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

def get_email_content(email_type):
    email_templates = {
        "welcome": {
            "subject": "Welcome to Nexivo!",
            "html_body": "<h1>Welcome!</h1><p>Thank you for joining Nexivo. We are excited to have you!</p>",
        },
        "payment": {
            "subject": "Payment Confirmation",
            "html_body": "<h1>Payment Successful</h1><p>Your payment has been received. Thank you for your purchase!</p>",
        },
        "support": {
            "subject": "Customer Support Request",
            "html_body": "<h1>Support Request Received</h1><p>Our team will get back to you shortly. Thank you for reaching out!</p>",
        },
    }

    return email_templates.get(email_type, {"subject": "Default Subject", "html_body": "Default Body"}).values()

def main():
    smtp_server = "smtp.gmail.com"  
    smtp_port = 587  
    email = "shakshamshakshamsingh@gmail.com"  
    password = ""

    email_sender = FreeEmailSender(smtp_server, smtp_port, email, password)

    email_types = ["welcome", "payment", "support"]
    recipient_email = "srijan2004.4apr@gmai.com"  

    for email_type in email_types:
        subject, html_body = get_email_content(email_type)
        if email_sender.send_email(subject, html_body, recipient_email):
            print(f"Email ({email_type}) sent successfully.")
        else:
            print(f"Failed to send {email_type} email.")

if __name__ == "__main__":
    main()
