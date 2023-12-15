from typing import Literal
import smtplib
from email.utils import *
from email.message import EmailMessage
from jinja2 import select_autoescape, Environment, FileSystemLoader
from app.models import Borrow
from app.config import settings


env = Environment(
    loader=FileSystemLoader(settings.EMAIL_TEMPLATES_DIR),
    autoescape=select_autoescape()
)


sender_name: str = settings.EMAILS_FROM_NAME
from_email: str = settings.EMAILS_FROM_EMAIL


def reset_password_email(email: str, otp: str):
    template = env.get_template("password-reset.html")
    content = template.render(email=email, otp=otp)

    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["To"] = email
    msg["From"] = formataddr((sender_name, from_email))
    msg.add_alternative(content, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.sendmail(from_email, email, msg.as_string())


def borrow_due_reminder(borrows: list[Borrow]):

    with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        template = env.get_template("borrow_due_reminder.html")
        for borrow in borrows:
            borrower = borrow.borrower
            content = template.render(name=borrower.name, items=borrow.items,
                                      due_date=borrow.due_date.strftime("%d %B, %Y"))
            to_addr = borrower.email
            msg = EmailMessage()
            msg["Subject"] = "Attention! Library borrow due date reminder"
            msg["From"] = formataddr((sender_name, from_email))
            msg["To"] = to_addr
            msg.add_alternative(content, subtype="html")
            smtp.sendmail(from_email, to_addr, msg.as_string())


def borrow_notification(borrow: Borrow, action_type: Literal['ISSUE', 'RENEW', 'RETURN']):
    template = None
    msg = EmailMessage()
    if action_type == 'ISSUE':
        template = env.get_template("borrow_order_conf.html")
        msg["Subject"] = "New Borrow Issue Conformation"

    elif action_type == 'RETURN':
        template = env.get_template("borrow_return_conf.html")
        msg["Subject"] = "Your borrowings were successfully returned"

    else:
        template = env.get_template("borrow_renew_conf.html")
        msg["Subject"] = "Borrow renew request conformation"


    content = template.render(items=borrow.items, name=borrow.borrower.name,
                              issue_date=borrow.issue_date.strftime("%d %B, %Y"),
                              due_date=borrow.due_date.strftime("%d %B, %Y"), id=borrow.id)
    # print(content)
    msg["From"] = formataddr((sender_name, from_email))
    msg["To"] = borrow.borrower.email
    msg.add_alternative(content, subtype="html")
    with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.sendmail(from_email, borrow.borrower.email, msg.as_string())


def confirm_email(email: str, otp: str):

    template = env.get_template("confirm_email.html")
    content = template.render(email=email, otp=otp)

    msg = EmailMessage()
    msg["Subject"] = "Confirm your email"
    msg["To"] = email
    msg["From"] = formataddr((sender_name, from_email))
    msg.add_alternative(content, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.sendmail(from_email, email, msg.as_string())
