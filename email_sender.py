import smtplib
from email.message import EmailMessage


def email_sender(sender,sender_pass,recipient,message):


    # 2. Compose the Message
    msg = EmailMessage()
    msg["Subject"] = "Hello from Python!"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(message)

    # 3. Securely Send the Email
    try:
    # Connect to the Gmail SMTP server using SSL (Port 465)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, sender_pass)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")