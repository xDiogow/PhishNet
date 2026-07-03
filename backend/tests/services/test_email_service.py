"""Tests for email_service helper functions and SMTP dispatch."""
import smtplib
import socket
import pytest
from unittest.mock import patch, MagicMock

from app.services.email_service import (
    _html_to_plain,
    _replace_placeholders,
    send_phishing_email,
    send_invitation_email,
)


# ---------------------------------------------------------------------------
# _html_to_plain
# ---------------------------------------------------------------------------

class TestHtmlToPlain:
    def test_strips_html_tags(self):
        result = _html_to_plain("<p>Hello <b>World</b></p>")
        assert "<p>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "World" in result

    def test_skips_script_content(self):
        result = _html_to_plain("<p>Safe</p><script>alert(1)</script>")
        assert "alert(1)" not in result
        assert "Safe" in result

    def test_skips_style_content(self):
        result = _html_to_plain("<style>.foo{color:red}</style><p>Text</p>")
        assert ".foo" not in result
        assert "Text" in result

    def test_returns_empty_for_empty_input(self):
        assert _html_to_plain("") == ""


# ---------------------------------------------------------------------------
# _replace_placeholders
# ---------------------------------------------------------------------------

class TestReplacePlaceholders:
    BASE_URL = "http://localhost:5000"
    PIXEL_URL = f"{BASE_URL}/px/abc123"
    CLICK_URL = f"{BASE_URL}/r/abc123"
    PERSONALISATION = {
        '{{.FirstName}}': 'Alice',
        '{{.LastName}}': 'Smith',
        '{{.Email}}': 'alice@example.com',
        '{{.Position}}': 'Engineer',
    }

    def test_tracking_pixel_replaced(self):
        text = "{{TRACKING_PIXEL}}"
        result = _replace_placeholders(text, self.PIXEL_URL, self.CLICK_URL, self.PERSONALISATION)
        assert "{{TRACKING_PIXEL}}" not in result
        assert "<img" in result
        assert self.PIXEL_URL in result

    def test_click_url_replaced(self):
        text = "Click here: {{CLICK_URL}}"
        result = _replace_placeholders(text, self.PIXEL_URL, self.CLICK_URL, self.PERSONALISATION)
        assert "{{CLICK_URL}}" not in result
        assert self.CLICK_URL in result

    def test_dot_url_replaced(self):
        text = "{{.URL}}"
        result = _replace_placeholders(text, self.PIXEL_URL, self.CLICK_URL, self.PERSONALISATION)
        assert "{{.URL}}" not in result
        assert self.CLICK_URL in result

    def test_personalisation_replaced(self):
        text = "Hi {{.FirstName}} {{.LastName}}, your email is {{.Email}}"
        result = _replace_placeholders(text, self.PIXEL_URL, self.CLICK_URL, self.PERSONALISATION)
        assert "{{.FirstName}}" not in result
        assert "{{.LastName}}" not in result
        assert "Alice" in result
        assert "Smith" in result
        assert "alice@example.com" in result


# ---------------------------------------------------------------------------
# send_phishing_email — SMTP mocking
#
# email_service._send_via_smtp does:
#   smtp = smtplib.SMTP(host, port, timeout=t)  ← returns mock_smtp.return_value
#   with smtp:                                   ← calls __enter__/__exit__ on it
#       smtp.send_message(msg)                   ← called on smtp (return_value), NOT __enter__ result
# ---------------------------------------------------------------------------

class TestSendPhishingEmail:

    def _smtp_mock(self):
        """Return a patched smtplib.SMTP whose return_value acts as smtp instance."""
        mock_smtp = MagicMock()
        # __exit__ must return falsy so exceptions propagate out of `with smtp:`
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        return mock_smtp

    def test_send_phishing_email_success(self, app):
        mock_smtp = self._smtp_mock()
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_phishing_email(
                    email="target@example.com",
                    first_name="Alice",
                    last_name="Smith",
                    position="Engineer",
                    tracking_token="tok-abc",
                    subject="Hello {{.FirstName}}",
                    email_html="<p>Hi {{.FirstName}}!</p>{{TRACKING_PIXEL}}",
                )
        assert result is True
        mock_smtp.return_value.send_message.assert_called_once()

    def test_send_phishing_email_auth_error(self, app):
        mock_smtp = self._smtp_mock()
        mock_smtp.return_value.send_message.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Auth failed"
        )
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_phishing_email(
                    email="target@example.com",
                    first_name="Alice",
                    last_name="Smith",
                    position="Engineer",
                    tracking_token="tok-xyz",
                    subject="Test",
                    email_html="<p>Body</p>",
                )
        assert result is False

    def test_send_phishing_email_timeout(self, app):
        """socket.timeout raised when connecting to SMTP server."""
        mock_smtp = MagicMock(side_effect=socket.timeout("timed out"))
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_phishing_email(
                    email="target@example.com",
                    first_name="Alice",
                    last_name="Smith",
                    position="",
                    tracking_token="tok-timeout",
                    subject="Test",
                    email_html="<p>Body</p>",
                )
        assert result is False

    def test_send_phishing_email_smtp_exception(self, app):
        mock_smtp = self._smtp_mock()
        mock_smtp.return_value.send_message.side_effect = smtplib.SMTPException(
            "Something went wrong"
        )
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_phishing_email(
                    email="target@example.com",
                    first_name="Alice",
                    last_name="Smith",
                    position="",
                    tracking_token="tok-err",
                    subject="Test",
                    email_html="<p>Body</p>",
                )
        assert result is False

    def test_send_phishing_email_recipients_refused(self, app):
        mock_smtp = self._smtp_mock()
        mock_smtp.return_value.send_message.side_effect = smtplib.SMTPRecipientsRefused(
            {"target@example.com": (550, b"User unknown")}
        )
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_phishing_email(
                    email="target@example.com",
                    first_name="Alice",
                    last_name="Smith",
                    position="",
                    tracking_token="tok-refused",
                    subject="Test",
                    email_html="<p>Body</p>",
                )
        assert result is False

    def test_send_phishing_email_ssl_mode(self, app):
        """When MAIL_USE_SSL=True, SMTP_SSL is used instead of SMTP."""
        mock_smtp_ssl = MagicMock()
        mock_smtp_ssl.return_value.__exit__ = MagicMock(return_value=False)
        with app.app_context():
            app.config['MAIL_USE_SSL'] = True
            app.config['MAIL_USE_TLS'] = False
            try:
                with patch('smtplib.SMTP_SSL', mock_smtp_ssl):
                    result = send_phishing_email(
                        email="target@example.com",
                        first_name="Alice",
                        last_name="Smith",
                        position="",
                        tracking_token="tok-ssl",
                        subject="Test",
                        email_html="<p>Body</p>",
                    )
            finally:
                app.config['MAIL_USE_SSL'] = False
                app.config['MAIL_USE_TLS'] = True
        assert result is True
        mock_smtp_ssl.return_value.send_message.assert_called_once()


# ---------------------------------------------------------------------------
# send_invitation_email
# ---------------------------------------------------------------------------

class TestSendInvitationEmail:

    def test_send_invitation_email_success(self, app):
        mock_smtp = MagicMock()
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_invitation_email(
                    email="newuser@example.com",
                    invitation_code="INV-ABC123",
                    base_url="http://localhost:5173",
                )
        assert result is True
        mock_smtp.return_value.send_message.assert_called_once()

    def test_send_invitation_email_smtp_failure(self, app):
        """Network error when connecting raises OSError — should return False."""
        mock_smtp = MagicMock(side_effect=OSError("Network error"))
        with app.app_context():
            with patch('smtplib.SMTP', mock_smtp):
                result = send_invitation_email(
                    email="newuser@example.com",
                    invitation_code="INV-FAIL",
                    base_url="http://localhost:5173",
                )
        assert result is False
