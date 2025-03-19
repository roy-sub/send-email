from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict

app = FastAPI(title="Email Sender API")

class EmailRequest(BaseModel):
    sender_email: str
    password: str
    receiver_email: EmailStr
    subject: str
    body: str
    smtp_server: str
    smtp_port: int

def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    if not email or '@' not in email:
        return False
    
    multimedia_extensions = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "avif", "mp4", 
                           "mkv", "avi", "mov", "wmv", "flv", "mpeg"]
    email_extension = email.split(".")[-1].lower()
    return email_extension not in multimedia_extensions

def send_email(
    sender_email: str,
    receiver_email: str,
    subject: str,
    body: str,
    password: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> Dict[str, any]:

    try:
        # Create a multipart message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS for security
            server.starttls()
            
            # Authentication
            server.login(sender_email, password)
            
            # Send the email
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            
        return {"success": True, "message": "Email sent successfully"}
    
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}

@app.post("/send-email/", response_model=Dict[str, any])
async def send_email_endpoint(email_data: EmailRequest):
    # Additional validation beyond Pydantic's EmailStr
    if not is_valid_email(email_data.receiver_email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Send the email
    result = send_email(
        sender_email=email_data.sender_email,
        receiver_email=email_data.receiver_email,
        subject=email_data.subject,
        body=email_data.body,
        password=email_data.password,
        smtp_server=email_data.smtp_server,
        smtp_port=email_data.smtp_port
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.get("/")
async def root():
    return {"message": "Email Sender API is running. Use /send-email/ endpoint to send emails."}
