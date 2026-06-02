"""SMTP email delivery for phishing campaigns.

Sends multipart/alternative emails (plain-text + HTML) via smtplib.
Supports both STARTTLS (port 587) and implicit SSL (port 465) depending on
the MAIL_USE_SSL config flag.

SMTP credentials and URLs are read from Flask config:
  MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL,
  MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_TIMEOUT, APP_BASE_URL

Delivery failures are logged and return False without raising — the caller
(CampaignService) records the successful count and continues to the next target.
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from socket import timeout as SocketTimeout

from flask import current_app

logger = logging.getLogger(__name__)

TRACKING_PIXEL_HTML = (
    '<img src="{pixel_url}" width="1" height="1" '
    'style="display:none;border:0;" alt="" />'
)


def send_phishing_email(email: str, first_name: str, last_name: str,
                        position: str, tracking_token: str,
                        subject: str, email_html: str) -> bool:
    """Send a phishing simulation email to one target.

    Replaces placeholders in both subject and email_html before sending.

    Tracking placeholders:
      {{TRACKING_PIXEL}} → 1×1 transparent tracking pixel img tag
      {{CLICK_URL}}      → click-tracking redirect URL
      {{.URL}}           → click-tracking redirect URL (alias for {{CLICK_URL}})

    Personalisation placeholders:
      {{.Email}}         → target's email address
      {{.FirstName}}     → target's first name
      {{.LastName}}      → target's last name
      {{.Position}}      → target's job position

    Returns True if the message was accepted by the SMTP server, False otherwise.
    """
    base_url = current_app.config['APP_BASE_URL'].rstrip('/')
    pixel_url = f"{base_url}/track/o/{tracking_token}"
    click_url = f"{base_url}/track/c/{tracking_token}"

    personalisation = {
        '{{.Email}}': email,
        '{{.FirstName}}': first_name,
        '{{.LastName}}': last_name,
        '{{.Position}}': position or '',
    }

    def apply_placeholders(text: str) -> str:
        pixel_tag = TRACKING_PIXEL_HTML.format(pixel_url=pixel_url)
        text = text.replace('{{TRACKING_PIXEL}}', pixel_tag)
        text = text.replace('{{CLICK_URL}}', click_url)
        text = text.replace('{{.URL}}', click_url)
        for placeholder, value in personalisation.items():
            text = text.replace(placeholder, value)
        return text

    html_body = apply_placeholders(email_html)
    rendered_subject = apply_placeholders(subject)

    mail_from = current_app.config['MAIL_FROM']
    domain = mail_from.split('@')[-1] if '@' in mail_from else 'phishnet.local'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = rendered_subject
    msg['From'] = mail_from
    msg['To'] = email
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = make_msgid(domain=domain)

    plain_text = f"Hi {first_name},\n\nPlease visit: {click_url}"
    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    mail_server = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']
    mail_username = current_app.config['MAIL_USERNAME']
    mail_password = current_app.config['MAIL_PASSWORD']
    use_tls = current_app.config['MAIL_USE_TLS']
    use_ssl = current_app.config.get('MAIL_USE_SSL', False)
    timeout = current_app.config.get('MAIL_TIMEOUT', 30)

    try:
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(mail_server, mail_port, timeout=timeout) as smtp:
            if use_tls and not use_ssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            if mail_username and mail_password:
                smtp.login(mail_username, mail_password)
            smtp.send_message(msg)

        logger.info("Phishing email sent to %s (token=%s)", email, tracking_token)
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP authentication failed for %s: %s", email, e)
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("Recipient refused by SMTP server for %s: %s", email, e)
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending to %s: %s", email, e)
    except SocketTimeout:
        logger.error("SMTP connection timed out sending to %s (server=%s, timeout=%ss)",
                     email, mail_server, timeout)
    except OSError as e:
        logger.error("Network error sending to %s: %s", email, e)

    return False
