"""Flask CLI commands for database seeding and data retention."""
import click
from datetime import datetime, timezone, timedelta
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
            <form id="loginForm" method="post">
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

_INSTAGRAM_EMAIL_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram - Action Required</title>
    <style>
        body { margin: 0; padding: 0; background-color: #fafafa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        .wrapper { max-width: 480px; margin: 32px auto; background: #ffffff; border: 1px solid #dbdbdb; border-radius: 4px; overflow: hidden; }
        .header { padding: 32px 40px 20px; text-align: center; border-bottom: 1px solid #efefef; }
        .logo { font-size: 28px; font-weight: 700; letter-spacing: -0.5px; background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-family: 'Billabong', cursive, serif; }
        .body { padding: 28px 40px; color: #262626; }
        .body p { margin: 0 0 16px; font-size: 14px; line-height: 20px; color: #262626; }
        .body p.greeting { font-size: 16px; font-weight: 600; }
        .btn { display: block; width: fit-content; margin: 24px auto; background: linear-gradient(to right, #833ab4, #fd1d1d, #fcb045); color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600; letter-spacing: 0.3px; }
        .divider { border: none; border-top: 1px solid #efefef; margin: 20px 0; }
        .footer { padding: 16px 40px 24px; text-align: center; }
        .footer p { font-size: 12px; color: #8e8e8e; margin: 4px 0; line-height: 18px; }
        .footer a { color: #0095f6; text-decoration: none; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <div class="logo">Instagram</div>
        </div>
        <div class="body">
            <p class="greeting">Hi {{.FirstName}},</p>
            <p>We noticed a login attempt to your Instagram account from an unrecognized device.</p>
            <p><strong>Location:</strong> Paris, France<br>
               <strong>Device:</strong> Chrome on Windows<br>
               <strong>Time:</strong> Today at 2:14 AM</p>
            <p>If this was you, you can ignore this message. If you don't recognize this activity, please secure your account immediately.</p>
            <a href="{{.URL}}" class="btn">Secure My Account</a>
            <hr class="divider">
            <p style="font-size:12px; color:#8e8e8e;">You're receiving this email because someone tried to log in to your Instagram account. If you believe your account has been compromised, visit our Help Centre.</p>
        </div>
        <div class="footer">
            <p>© 2025 Instagram from Meta · 1601 Willow Road, Menlo Park, CA 94025</p>
            <p><a href="#">Privacy Policy</a> · <a href="#">Terms of Service</a> · <a href="#">Help Centre</a></p>
        </div>
    </div>
    {{TRACKING_PIXEL}}
</body>
</html>
"""

_INSTAGRAM_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #fafafa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }

        .card { background: #ffffff; border: 1px solid #dbdbdb; border-radius: 4px; padding: 40px; width: 350px; text-align: center; }
        .logo { font-size: 36px; font-weight: 700; letter-spacing: -1px; background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 28px; font-family: 'Billabong', cursive, serif; }

        form { display: flex; flex-direction: column; gap: 6px; }
        input { width: 100%; padding: 9px 8px; border: 1px solid #dbdbdb; border-radius: 4px; background: #fafafa; font-size: 12px; color: #262626; outline: none; transition: border-color 0.15s; }
        input:focus { border-color: #a8a8a8; }
        input::placeholder { color: #8e8e8e; }

        .btn-login { margin-top: 8px; width: 100%; padding: 8px; background: #0095f6; color: #ffffff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; }
        .btn-login:hover { background: #1877f2; }

        .or-divider { display: flex; align-items: center; gap: 16px; margin: 18px 0; }
        .or-divider::before, .or-divider::after { content: ''; flex: 1; height: 1px; background: #dbdbdb; }
        .or-divider span { font-size: 13px; font-weight: 600; color: #8e8e8e; letter-spacing: 1px; }

        .btn-facebook { width: 100%; background: transparent; border: none; color: #385185; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-facebook svg { width: 20px; height: 20px; fill: #385185; }

        .forgot { margin-top: 16px; font-size: 12px; color: #00376b; text-decoration: none; display: block; }
        .forgot:hover { text-decoration: underline; }

        .signup-card { background: #ffffff; border: 1px solid #dbdbdb; border-radius: 4px; padding: 20px; width: 350px; text-align: center; margin-top: 10px; font-size: 14px; color: #262626; }
        .signup-card a { color: #0095f6; font-weight: 600; text-decoration: none; }

        .app-links { margin-top: 20px; text-align: center; }
        .app-links p { font-size: 14px; color: #262626; margin-bottom: 12px; }
        .badge { display: inline-flex; align-items: center; gap: 8px; background: #000; color: #fff; border-radius: 8px; padding: 7px 14px; margin: 4px; text-decoration: none; min-width: 130px; }
        .badge-text { display: flex; flex-direction: column; line-height: 1.2; }
        .badge-text span:first-child { font-size: 9px; letter-spacing: 0.3px; }
        .badge-text span:last-child { font-size: 14px; font-weight: 600; }

        .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #8e8e8e; }
        .footer a { color: #8e8e8e; text-decoration: none; margin: 0 8px; }
        .footer a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">Instagram</div>

        <form method="post">
            <input type="text" name="username" placeholder="Phone number, username, or email" value="{{.Email}}" autocomplete="username" required />
            <input type="password" name="password" placeholder="Password" autocomplete="current-password" required />
            <button type="submit" class="btn-login">Log in</button>
        </form>

        <div class="or-divider"><span>OR</span></div>

        <button class="btn-facebook" type="button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
            </svg>
            Log in with Facebook
        </button>

        <a href="#" class="forgot">Forgot password?</a>
    </div>

    <div class="signup-card">
        Don't have an account? <a href="#">Sign up</a>
    </div>

    <div class="app-links">
        <p>Get the app.</p>
        <!-- App Store badge -->
        <a href="#" class="badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 814 1000" fill="white">
                <path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-42.3-150.3-97.8C34.3 752.8 0 663.8 0 577.8c0-159.5 103.4-244.2 205.3-244.2 55.7 0 101.9 36.6 136.8 36.6 33.2 0 85.1-38.8 148.3-38.8 23.9 0 108.2 2 166.1 77.3zm-219.1-166.4c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.3z"/>
            </svg>
            <div class="badge-text">
                <span>Download on the</span>
                <span>App Store</span>
            </div>
        </a>
        <!-- Google Play badge -->
        <a href="#" class="badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4CAF50" d="M1.22 0L13.19 12 1.22 24c-.46-.22-.77-.7-.77-1.24V1.24C.45.7.76.22 1.22 0z"/>
                <path fill="#F44336" d="M17.04 7.97l-3.85-2.21L1.22 0l11.97 12-4.06 4.06 7.91-4.54c.74-.42.74-1.14 0-1.55z"/>
                <path fill="#FFC107" d="M1.22 24l11.97-12 2.88 2.88-10.9 6.26c-.74.43-1.6.39-2.28-.1L1.22 24z"/>
                <path fill="#2196F3" d="M1.22 0c.68-.49 1.54-.53 2.28-.1l10.9 6.26-2.88 2.88L1.22 0z"/>
            </svg>
            <div class="badge-text">
                <span>GET IT ON</span>
                <span>Google Play</span>
            </div>
        </a>
    </div>

    <footer class="footer">
        <div style="margin-bottom: 16px;">
            <a href="#">Meta</a><a href="#">About</a><a href="#">Blog</a><a href="#">Jobs</a>
            <a href="#">Help</a><a href="#">API</a><a href="#">Privacy</a><a href="#">Terms</a>
            <a href="#">Locations</a><a href="#">Instagram Lite</a>
        </div>
        <div>English (UK) · © 2025 Instagram from Meta</div>
    </footer>
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
    {
        'name': 'Instagram - Suspicious Login Alert (EN)',
        'subject': 'Action Required: Suspicious login attempt on your Instagram account',
        'email_html': _INSTAGRAM_EMAIL_HTML,
        'landing_page_html': _INSTAGRAM_LANDING_HTML,
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

    @app.cli.command('purge-old-results')
    @click.option('--days', default=365, show_default=True,
                  help='Anonymize campaign results sent more than N days ago.')
    @click.option('--dry-run', is_flag=True, default=False,
                  help='Report how many rows would be affected without modifying data.')
    @with_appcontext
    def purge_old_results(days, dry_run):
        """Anonymize PII in campaign results older than N days (GDPR Art. 5.1.e retention)."""
        from app.repository.campaign_result_repository import CampaignResultRepository
        from app.models.campaign_result import CampaignResult

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        click.echo(f'Cutoff: {cutoff.date()} (results sent before this date)')

        if dry_run:
            repo_session = db.session
            count = (
                repo_session.query(CampaignResult)
                .filter(CampaignResult.sent_at < cutoff)
                .filter(CampaignResult.email != 'deleted@anonymized.local')
                .count()
            )
            click.echo(f'Dry run — {count} result(s) would be anonymized.')
            return

        repo = CampaignResultRepository()
        count = repo.anonymize_older_than(cutoff)
        click.echo(f'Done — {count} campaign result(s) anonymized.')

    @app.cli.command('purge-old-audit-logs')
    @click.option('--days', default=365, show_default=True,
                  help='Delete audit logs created more than N days ago.')
    @click.option('--dry-run', is_flag=True, default=False,
                  help='Report how many rows would be deleted without modifying data.')
    @with_appcontext
    def purge_old_audit_logs(days, dry_run):
        """Delete audit logs older than N days (GDPR Art. 5.1.e retention)."""
        from app.repository.audit_log_repository import AuditLogRepository
        from app.models.audit_log import AuditLog

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        click.echo(f'Cutoff: {cutoff.date()} (logs created before this date)')

        if dry_run:
            count = db.session.query(AuditLog).filter(AuditLog.created_at < cutoff).count()
            click.echo(f'Dry run — {count} audit log(s) would be deleted.')
            return

        repo = AuditLogRepository()
        count = repo.delete_older_than(cutoff)
        click.echo(f'Done — {count} audit log(s) deleted.')
