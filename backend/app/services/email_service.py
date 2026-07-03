import smtplib
import logging
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from html.parser import HTMLParser
from socket import timeout as SocketTimeout

from flask import current_app

logger = logging.getLogger(__name__)


class _TextExtractor(HTMLParser):
    """Strip HTML tags and collapse whitespace into readable plain text."""
    _SKIP = {'style', 'script', 'head'}

    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1
        if tag in ('br', 'p', 'div', 'tr', 'h1', 'h2', 'h3', 'li'):
            self._parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self._SKIP:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self):
        raw = ''.join(self._parts)
        lines = [ln.strip() for ln in raw.splitlines()]
        # Collapse 3+ blank lines into 2
        result = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))
        return result.strip()


def _html_to_plain(html):
    p = _TextExtractor()
    p.feed(html)
    return p.get_text()


TRACKING_PIXEL_HTML = (
    '<img src="{pixel_url}" width="1" height="1" '
    'style="display:none;border:0;" alt="" />'
)


def _replace_placeholders(text, pixel_url, click_url, personalisation):
    """Replace all template placeholders in the given text and return the result."""
    pixel_tag = TRACKING_PIXEL_HTML.format(pixel_url=pixel_url)
    text = text.replace('{{TRACKING_PIXEL}}', pixel_tag)
    text = text.replace('{{CLICK_URL}}', click_url)
    text = text.replace('{{.URL}}', click_url)
    for placeholder, value in personalisation.items():
        text = text.replace(placeholder, value)
    text = text.replace('{{REPORT_URL}}', '')
    return text


def _send_via_smtp(msg):
    """Connect to the SMTP server from Flask config and send a message. Returns True on success."""
    mail_server = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']
    mail_username = current_app.config['MAIL_USERNAME']
    mail_password = current_app.config['MAIL_PASSWORD']
    use_tls = current_app.config['MAIL_USE_TLS']
    use_ssl = current_app.config.get('MAIL_USE_SSL', False)
    timeout = current_app.config.get('MAIL_TIMEOUT', 30)

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(mail_server, mail_port, timeout=timeout)
        else:
            smtp = smtplib.SMTP(mail_server, mail_port, timeout=timeout)

        with smtp:
            if use_tls and not use_ssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            if mail_username and mail_password:
                smtp.login(mail_username, mail_password)
            smtp.send_message(msg)

        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP authentication failed: %s", e)
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("Recipient refused by SMTP server: %s", e)
    except smtplib.SMTPException as e:
        logger.error("SMTP error: %s", e)
    except SocketTimeout:
        logger.error("SMTP connection timed out (server=%s, timeout=%ss)", mail_server, timeout)
    except OSError as e:
        logger.error("Network error: %s", e)

    return False


def send_phishing_email(email, first_name, last_name, position, tracking_token, subject, email_html):
    """Send a phishing simulation email to one target. Returns True if accepted by SMTP."""
    base_url = current_app.config['APP_BASE_URL'].rstrip('/')
    pixel_url = f"{base_url}/px/{tracking_token}"
    click_url = f"{base_url}/r/{tracking_token}"
    report_url = f"{base_url}/report/{tracking_token}"

    personalisation = {
        '{{.Email}}': email,
        '{{.FirstName}}': first_name,
        '{{.LastName}}': last_name,
        '{{.Position}}': position or '',
        '{{REPORT_URL}}': report_url,
    }

    html_body = _replace_placeholders(email_html, pixel_url, click_url, personalisation)
    rendered_subject = _replace_placeholders(subject, pixel_url, click_url, personalisation)

    mail_from = current_app.config['MAIL_FROM']
    domain = mail_from.split('@')[-1]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = rendered_subject
    msg['From'] = mail_from
    msg['To'] = email
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = make_msgid(domain=domain)

    plain_text = _html_to_plain(html_body)
    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    result = _send_via_smtp(msg)
    if result:
        logger.info("Phishing email sent to %s (token=%s)", email, tracking_token)
    return result


def send_invitation_email(email, invitation_code, base_url):
    """Send a team invitation email. Returns True if accepted by SMTP."""
    register_url = f"{base_url.rstrip('/')}/register?code={invitation_code}"

    subject = "You've been invited to join PhishNet"
    html_body = f"""
<html><body style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
  <h2 style="color:#1e40af">You're invited to PhishNet</h2>
  <p>You have been invited to join a PhishNet workspace.</p>
  <p style="margin:24px 0">
    <a href="{register_url}"
       style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold">
      Accept invitation
    </a>
  </p>
  <p style="color:#6b7280;font-size:13px">
    Or use invitation code: <strong>{invitation_code}</strong><br>
    at <a href="{base_url}/register">{base_url}/register</a>
  </p>
</body></html>
"""
    plain_body = (
        f"You've been invited to PhishNet.\n\n"
        f"Register at: {register_url}\n\n"
        f"Or use invitation code: {invitation_code}\n"
        f"at {base_url}/register"
    )

    mail_from = current_app.config['MAIL_FROM']
    domain = mail_from.split('@')[-1]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = email
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = make_msgid(domain=domain)
    msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    result = _send_via_smtp(msg)
    if result:
        logger.info("Invitation email sent to %s", email)
    return result
