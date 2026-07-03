"""Flask CLI commands for database seeding and data retention."""
import click
from datetime import datetime, timezone, timedelta
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
    <div style="text-align:center;padding:12px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:24px;">
      Suspicious? <a href="{{REPORT_URL}}" style="color:#999;">Report this email</a>
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


_LINKEDIN_EMAIL_HTML = """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LinkedIn</title></head>
<body style="margin:0;padding:0;background-color:#f3f2ef;" bgcolor="#f3f2ef">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f3f2ef">
<tr><td align="center" style="padding:20px 16px;">
<table width="552" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width:552px;width:100%;border:1px solid #e0dfdc;">

  <!-- Header -->
  <tr>
    <td style="padding:14px 24px;border-bottom:1px solid #e0dfdc;" bgcolor="#ffffff">
      <table cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="background-color:#0A66C2;padding:3px 6px;font-family:Georgia,serif;font-size:16px;font-weight:700;color:#ffffff;line-height:1.3;">in</td>
        <td style="padding-left:5px;font-family:Arial,Helvetica,sans-serif;font-size:19px;font-weight:700;color:#0A66C2;vertical-align:middle;line-height:1;">LinkedIn</td>
      </tr></table>
    </td>
  </tr>

  <!-- Body -->
  <tr><td style="padding:24px 24px 8px;" bgcolor="#ffffff">
    <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:20px;color:#000000;">Hi {{.FirstName}},</p>
    <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:20px;color:#000000;">Your profile appeared in <strong>14 searches</strong> this week. A recruiter from <strong>Accenture</strong> viewed your profile and may want to connect.</p>
  </td></tr>

  <!-- Viewer card -->
  <tr><td style="padding:0 24px 16px;" bgcolor="#ffffff">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e0dfdc;">
      <tr>
        <td width="72" style="padding:16px 12px 16px 16px;vertical-align:top;">
          <table cellpadding="0" cellspacing="0" border="0"><tr>
            <td width="48" height="48" bgcolor="#0A66C2" style="border-radius:50%;text-align:center;vertical-align:middle;font-family:Arial,sans-serif;font-size:20px;font-weight:700;color:#ffffff;line-height:48px;">A</td>
          </tr></table>
        </td>
        <td style="padding:16px 16px 16px 0;vertical-align:top;">
          <p style="margin:0 0 2px;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;color:#000000;line-height:20px;">Recruiter at Accenture</p>
          <p style="margin:0 0 2px;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#666666;line-height:16px;">Senior Talent Acquisition &middot; Paris, France</p>
          <p style="margin:4px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#666666;line-height:16px;">This viewer has a private profile</p>
        </td>
      </tr>
    </table>
  </td></tr>

  <tr><td style="padding:0 24px 8px;" bgcolor="#ffffff">
    <p style="margin:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:20px;color:#000000;">Upgrading to Premium gives you full access to see everyone who viewed your profile in the last 90 days &mdash; including this recruiter. <strong>Your free preview expires in 24 hours.</strong></p>
  </td></tr>

  <!-- CTA -->
  <tr><td style="padding:4px 24px 20px;" bgcolor="#ffffff">
    <table cellpadding="0" cellspacing="0" border="0"><tr>
      <td bgcolor="#0A66C2" style="border-radius:24px;">
        <a href="{{.URL}}" style="display:inline-block;padding:10px 22px;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;">See who viewed your profile</a>
      </td>
    </tr></table>
  </td></tr>

  <tr><td style="padding:0 24px 20px;border-top:1px solid #e0dfdc;" bgcolor="#ffffff">
    <p style="margin:12px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:18px;color:#666666;">You are receiving this email because you set your profile view privacy to &ldquo;Your name and headline&rdquo;.</p>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:16px 24px;" bgcolor="#f3f2ef">
    <p style="margin:0 0 6px;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:700;color:#0A66C2;">LinkedIn</p>
    <p style="margin:0 0 3px;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#666666;line-height:16px;">This email was sent to {{.Email}}.</p>
    <p style="margin:0 0 3px;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#666666;line-height:16px;"><a href="#" style="color:#0A66C2;text-decoration:none;">Unsubscribe</a> &nbsp;&middot;&nbsp; <a href="#" style="color:#0A66C2;text-decoration:none;">Help</a> &nbsp;&middot;&nbsp; <a href="#" style="color:#0A66C2;text-decoration:none;">Privacy Policy</a></p>
    <p style="margin:4px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#666666;line-height:16px;">&copy; 2025 LinkedIn Corporation, 1000 West Maude Avenue, Sunnyvale, CA 94085. All rights reserved.</p>
  </td></tr>

</table>
</td></tr>
</table>
<div style="text-align:center;padding:12px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:24px;">
  Suspicious? <a href="{{REPORT_URL}}" style="color:#999;">Report this email</a>
</div>
{{TRACKING_PIXEL}}
</body>
</html>
"""

_LINKEDIN_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedIn: Log In or Sign Up</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{background-color:#f3f2ef;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;min-height:100vh}
    nav{background:#ffffff;padding:0 24px;height:52px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,.08);position:sticky;top:0;z-index:10}
    .nav-logo{display:flex;align-items:center}
    .nav-logo svg{color:#0A66C2}
    .nav-links{display:flex;align-items:center;gap:4px}
    .nav-links a{font-size:16px;font-weight:600;color:#000000;text-decoration:none;padding:8px 16px;border-radius:24px}
    .nav-links .btn-join{border:1.5px solid #0A66C2;color:#0A66C2;border-radius:24px}
    .nav-links .btn-join:hover{background:#eef3f8}
    .wrap{max-width:1128px;margin:0 auto;padding:60px 24px 0;display:flex;align-items:center;justify-content:space-between;gap:32px}
    .hero-text{flex:1;max-width:520px}
    .hero-text h1{font-size:52px;font-weight:400;color:#8f5849;line-height:1.15;font-family:Georgia,'Times New Roman',Times,serif}
    .hero-art{flex-shrink:0;margin-right:-24px;margin-top:-20px;overflow:hidden;width:430px}
    .hero-art svg{display:block;width:100%}
    .main-row{max-width:1128px;margin:0 auto;padding:0 24px 60px;display:flex;align-items:flex-start;justify-content:flex-end}
    .card{background:#ffffff;border-radius:8px;padding:32px;width:400px;box-shadow:0 4px 12px rgba(0,0,0,.15);margin-top:-220px;position:relative;z-index:5;flex-shrink:0}
    @media(max-width:900px){.wrap{flex-direction:column;padding-top:40px}.hero-art{display:none}.hero-text h1{font-size:36px}.main-row{justify-content:center}.card{margin-top:24px}}
    .card h2{font-size:28px;font-weight:600;color:#000;margin-bottom:20px}
    .google-btn{width:100%;padding:12px;border:1.5px solid #9ba3af;border-radius:24px;background:#ffffff;font-size:16px;font-weight:600;color:#000;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:10px}
    .google-btn:hover{background:#f0f0f0}
    .sep{display:flex;align-items:center;gap:8px;margin:16px 0;color:#666;font-size:14px}
    .sep::before,.sep::after{content:'';flex:1;height:1px;background:#d9d9d9}
    .field{margin-bottom:12px}
    .field label{display:block;font-size:14px;font-weight:600;color:#000;margin-bottom:4px}
    .field input{width:100%;padding:14px 16px;border:1.5px solid #9ba3af;border-radius:4px;font-size:16px;color:#000;outline:none}
    .field input:focus{border-color:#0A66C2;box-shadow:0 0 0 1px #0A66C2}
    .pass-wrap{position:relative}
    .pass-wrap input{padding-right:56px}
    .show-btn{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;font-size:14px;font-weight:600;color:#0A66C2;cursor:pointer}
    .forgot{display:block;text-align:center;font-size:14px;font-weight:600;color:#0A66C2;text-decoration:none;margin:8px 0 4px}
    .btn-primary{width:100%;padding:14px;background:#0A66C2;color:#fff;border:none;border-radius:24px;font-size:16px;font-weight:600;cursor:pointer;margin-top:16px}
    .btn-primary:hover{background:#004182}
    .join-now{text-align:center;margin-top:20px;font-size:15px;color:#000}
    .join-now::before,.join-now::after{content:'';display:inline-block;height:1px;width:80px;background:#d9d9d9;vertical-align:middle;margin:0 8px}
    .join-now a{color:#0A66C2;font-weight:700;text-decoration:none}
  </style>
</head>
<body>
  <nav>
    <div class="nav-logo">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="34" height="34" fill="#0A66C2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
    </div>
    <div class="nav-links">
      <a href="#" class="btn-join">Join now</a>
    </div>
  </nav>

  <div class="wrap">
    <div class="hero-text">
      <h1>Welcome to your professional community</h1>
    </div>
    <div class="hero-art" aria-hidden="true">
      <!-- Decorative network illustration placeholder -->
      <svg viewBox="0 0 450 420" xmlns="http://www.w3.org/2000/svg">
        <circle cx="80" cy="80" r="36" fill="#e8c9a0" opacity=".9"/>
        <circle cx="220" cy="50" r="28" fill="#c5a880" opacity=".8"/>
        <circle cx="370" cy="100" r="32" fill="#d4aa75" opacity=".85"/>
        <circle cx="150" cy="200" r="30" fill="#e0bb90" opacity=".8"/>
        <circle cx="300" cy="180" r="26" fill="#c8955c" opacity=".75"/>
        <circle cx="60" cy="300" r="34" fill="#ddb07a" opacity=".9"/>
        <circle cx="390" cy="260" r="30" fill="#c99055" opacity=".8"/>
        <line x1="80" y1="80" x2="220" y2="50" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="220" y1="50" x2="370" y2="100" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="80" y1="80" x2="150" y2="200" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="220" y1="50" x2="300" y2="180" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="370" y1="100" x2="390" y2="260" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="150" y1="200" x2="60" y2="300" stroke="#c8a070" stroke-width="2" opacity=".4"/>
        <line x1="300" y1="180" x2="390" y2="260" stroke="#c8a070" stroke-width="2" opacity=".4"/>
      </svg>
    </div>
  </div>

  <div class="main-row">
    <div class="card">
      <h2>Sign in</h2>
      <button class="google-btn" type="button">
        <svg width="20" height="20" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        Continue with Google
      </button>
      <div class="sep">or</div>
      <form method="post">
        <div class="field">
          <label for="username">Email or phone</label>
          <input type="text" id="username" name="username" autocomplete="username" required />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <div class="pass-wrap">
            <input type="password" id="password" name="password" autocomplete="current-password" required />
            <button class="show-btn" type="button" onclick="var p=document.getElementById('password');this.textContent=p.type==='password'?(p.type='text','Hide'):(p.type='password','Show')">Show</button>
          </div>
        </div>
        <a href="#" class="forgot">Forgot password?</a>
        <button type="submit" class="btn-primary">Sign in</button>
      </form>
      <div class="join-now">New to LinkedIn? <a href="#">Join now</a></div>
    </div>
  </div>
</body>
</html>
"""

_ZOOM_EMAIL_HTML = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Zoom</title>
</head>
<body style="margin:0;padding:0;background-color:#f8f9fa;" bgcolor="#f8f9fa">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f9fa">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width:600px;width:100%;">

  <!-- Header -->
  <tr>
    <td style="padding:20px 32px;border-bottom:1px solid #e5e5e5;" bgcolor="#ffffff">
      <span style="font-family:Arial,Helvetica,sans-serif;font-size:26px;font-weight:700;color:#0B5CFF;letter-spacing:-0.5px;">zoom</span>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:36px 32px 24px;" bgcolor="#ffffff">

      <!-- Urgent banner -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
        <tr>
          <td style="padding:12px 16px;background-color:#fff3cd;border-left:4px solid #f59e0b;">
            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:700;color:#92400e;">ACTION REQUIRED &mdash; Your recording will be permanently deleted in less than 24 hours</p>
          </td>
        </tr>
      </table>

      <h1 style="margin:0 0 16px 0;font-family:Arial,Helvetica,sans-serif;font-size:22px;font-weight:700;color:#1f2d3d;line-height:30px;">Your cloud recording is expiring today</h1>
      <p style="margin:0 0 16px 0;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:24px;color:#555568;">Hi {{.FirstName}},</p>
      <p style="margin:0 0 20px 0;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:24px;color:#555568;">Your Zoom storage limit has been reached. The following cloud recording is scheduled for <strong style="color:#c0392b;">automatic permanent deletion today</strong>. Sign in now to download or move it to a safe location.</p>

      <!-- Meeting details -->
      <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f9fa" style="margin-bottom:24px;">
        <tr>
          <td style="padding:20px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td width="120" style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#747487;border-bottom:1px solid #e5e5e5;">Topic</td>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:600;color:#1f2d3d;border-bottom:1px solid #e5e5e5;">Weekly Team Sync</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#747487;border-bottom:1px solid #e5e5e5;">Date</td>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:600;color:#1f2d3d;border-bottom:1px solid #e5e5e5;">Today at 10:00 AM</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#747487;border-bottom:1px solid #e5e5e5;">Duration</td>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:600;color:#1f2d3d;border-bottom:1px solid #e5e5e5;">47 minutes</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:700;color:#c0392b;">Deletes in</td>
                <td style="padding:6px 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:700;color:#c0392b;">&lt; 24 hours</td>
              </tr>
            </table>
          </td>
        </tr>
      </table>

      <!-- CTA -->
      <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
        <tr>
          <td align="center" bgcolor="#0B5CFF" style="border-radius:6px;">
            <a href="{{.URL}}" style="display:inline-block;padding:14px 36px;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;">Save Recording Now</a>
          </td>
        </tr>
      </table>
      <p style="margin:0 0 24px 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:18px;color:#c0392b;font-weight:600;">Once deleted, this recording cannot be recovered.</p>
      <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:18px;color:#999;">If the button above doesn't work, paste this URL into your browser: <a href="{{.URL}}" style="color:#0B5CFF;text-decoration:none;word-break:break-all;">{{.URL}}</a></p>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:20px 32px;border-top:1px solid #e5e5e5;" bgcolor="#f8f9fa">
      <p style="margin:0 0 4px 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#747487;text-align:center;">&copy; 2025 Zoom Video Communications, Inc. All rights reserved.</p>
      <p style="margin:0 0 4px 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#747487;text-align:center;">55 Almaden Blvd, San Jose, CA 95113</p>
      <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#747487;text-align:center;"><a href="#" style="color:#0B5CFF;">Unsubscribe</a> &nbsp;&middot;&nbsp; <a href="#" style="color:#0B5CFF;">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="#" style="color:#0B5CFF;">Terms</a></p>
    </td>
  </tr>

</table>
</td></tr>
</table>
<div style="text-align:center;padding:12px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:24px;">
  Suspicious? <a href="{{REPORT_URL}}" style="color:#999;">Report this email</a>
</div>
{{TRACKING_PIXEL}}
</body>
</html>
"""

_ZOOM_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zoom – Sign In</title>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{background:#f8f8f8;font-family:Lato,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;min-height:100vh;display:flex;flex-direction:column;color:#232333}
    header{background:#ffffff;border-bottom:1px solid #e8e8e8;padding:0 32px;height:64px;display:flex;align-items:center;justify-content:space-between}
    .logo{display:flex;align-items:center;gap:6px}
    .logo-icon{background:#0B5CFF;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center}
    .logo-icon svg{display:block}
    .logo-text{font-size:22px;font-weight:700;color:#232333;letter-spacing:-.5px}
    .header-links{display:flex;align-items:center;gap:16px;font-size:14px}
    .header-links a{color:#232333;text-decoration:none;font-weight:500}
    .header-links .btn-plans{background:#0B5CFF;color:#fff;padding:8px 18px;border-radius:6px;font-weight:600;font-size:14px}
    .header-links .btn-plans:hover{background:#0040cc}
    .main{flex:1;display:flex;align-items:center;justify-content:center;padding:48px 24px}
    .card{background:#ffffff;border:1px solid #e0e0e0;border-radius:12px;padding:44px 52px;width:100%;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
    .card h1{font-size:28px;font-weight:700;color:#232333;text-align:center;margin-bottom:32px}
    .oauth-btn{width:100%;padding:12px 16px;border:1.5px solid #d0d0d0;border-radius:8px;background:#ffffff;font-size:15px;font-weight:500;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:10px;color:#232333;transition:background .15s}
    .oauth-btn:hover{background:#f5f5f5}
    .sso-btn{width:100%;padding:12px 16px;border:1.5px solid #d0d0d0;border-radius:8px;background:#ffffff;font-size:15px;font-weight:500;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;color:#232333;transition:background .15s}
    .sso-btn:hover{background:#f5f5f5}
    .sep{display:flex;align-items:center;gap:12px;margin:18px 0;color:#9696a8;font-size:14px}
    .sep::before,.sep::after{content:'';flex:1;height:1px;background:#e0e0e0}
    .field{margin-bottom:16px}
    .field label{display:block;font-size:14px;font-weight:600;color:#232333;margin-bottom:6px}
    .field input{width:100%;padding:12px 14px;border:1.5px solid #d0d0d0;border-radius:8px;font-size:15px;color:#232333;outline:none;transition:border-color .15s}
    .field input:focus{border-color:#0B5CFF;box-shadow:0 0 0 2px rgba(11,92,255,.12)}
    .forgot-row{text-align:right;margin-top:4px}
    .forgot-row a{font-size:13px;color:#0B5CFF;text-decoration:none;font-weight:600}
    .btn-signin{width:100%;padding:14px;background:#0B5CFF;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;margin-top:20px;transition:background .15s}
    .btn-signin:hover{background:#0040cc}
    .signup-row{text-align:center;margin-top:20px;font-size:14px;color:#747487}
    .signup-row a{color:#0B5CFF;font-weight:600;text-decoration:none}
    footer{text-align:center;padding:20px 24px;border-top:1px solid #e8e8e8;background:#fff;font-size:12px;color:#9696a8}
    footer a{color:#9696a8;text-decoration:none;margin:0 8px}
    footer a:hover{text-decoration:underline}
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <div class="logo-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="4" fill="#0B5CFF"/><path d="M4 8.5A1.5 1.5 0 0 1 5.5 7h7A1.5 1.5 0 0 1 14 8.5v7A1.5 1.5 0 0 1 12.5 17h-7A1.5 1.5 0 0 1 4 15.5v-7z" fill="#fff"/><path d="M15.5 10.2l3.8-2.5A.8.8 0 0 1 20.5 8.4v7.2a.8.8 0 0 1-1.2.7l-3.8-2.5V10.2z" fill="#fff"/></svg>
      </div>
      <span class="logo-text">Zoom</span>
    </div>
    <div class="header-links">
      <a href="#">Plans &amp; Pricing</a>
      <a href="#">Support</a>
      <a href="#" class="btn-plans">Sign Up Free</a>
    </div>
  </header>
  <div class="main">
    <div class="card">
      <h1>Sign In</h1>
      <button class="oauth-btn" type="button">
        <svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
        Sign in with Google
      </button>
      <button class="sso-btn" type="button">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#232333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><circle cx="12" cy="16" r="1" fill="#232333" stroke="none"/></svg>
        Sign in with SSO
      </button>
      <div class="sep">or</div>
      <form method="post">
        <div class="field">
          <label for="email">Email Address</label>
          <input type="email" id="email" name="email" autocomplete="email" required />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" autocomplete="current-password" required />
          <div class="forgot-row"><a href="#">Forgot password?</a></div>
        </div>
        <button type="submit" class="btn-signin">Sign In</button>
      </form>
      <div class="signup-row">Don't have an account? <a href="#">Sign Up Free</a></div>
    </div>
  </div>
  <footer>
    <div style="margin-bottom:8px;">Copyright &copy;2025 Zoom Video Communications, Inc. All rights reserved.</div>
    <a href="#">Privacy</a><a href="#">Legal</a><a href="#">Cookie Preferences</a><a href="#">Accessibility</a>
  </footer>
</body>
</html>
"""

_NETFLIX_EMAIL_HTML = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Netflix</title>
</head>
<body style="margin:0;padding:0;background-color:#ffffff;" bgcolor="#ffffff">
<table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width:600px;width:100%;">

  <!-- Black header with NETFLIX logo -->
  <tr>
    <td align="center" bgcolor="#000000" style="padding:18px 40px;">
      <span style="font-family:'Arial Black',Arial,sans-serif;font-size:32px;font-weight:900;color:#E50914;letter-spacing:-1px;">NETFLIX</span>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:40px 40px 0 40px;" bgcolor="#ffffff">
      <h1 style="margin:0 0 20px 0;font-family:Helvetica,Arial,sans-serif;font-size:24px;font-weight:700;color:#000000;line-height:32px;">Your Netflix membership is on hold</h1>
      <p style="margin:0 0 16px 0;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:24px;color:#333333;">Hi {{.FirstName}},</p>
      <p style="margin:0 0 16px 0;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:24px;color:#333333;">We were unable to process your payment. Your access to Netflix has been temporarily suspended. To continue watching without interruption, please update your billing information before your next billing date.</p>
    </td>
  </tr>

  <!-- Info box -->
  <tr>
    <td style="padding:0 40px 20px 40px;" bgcolor="#ffffff">
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="border-left:4px solid #E50914;padding:16px 20px;background-color:#fff5f5;">
            <p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:22px;color:#333333;">
              <strong>Account:</strong> {{.Email}}<br>
              <strong>Issue:</strong> Payment method declined<br>
              <strong>Next retry:</strong> In 3 days &mdash; <strong style="color:#E50914;">update now to avoid cancellation</strong>
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 20px 40px;" bgcolor="#ffffff">
      <table cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="center" bgcolor="#E50914" style="border-radius:4px;">
            <a href="{{.URL}}" style="display:inline-block;padding:14px 32px;font-family:Helvetica,Arial,sans-serif;font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;">Update Payment Info</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="padding:0 40px 36px 40px;" bgcolor="#ffffff">
      <p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#737373;">If you believe your payment details are already up to date or have any questions, please <a href="#" style="color:#0071EB;text-decoration:none;">contact us</a>.</p>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:24px 40px;" bgcolor="#f3f3f3">
      <p style="margin:0 0 8px 0;font-family:Helvetica,Arial,sans-serif;font-size:18px;font-weight:900;color:#E50914;font-family:'Arial Black',Arial,sans-serif;">NETFLIX</p>
      <p style="margin:0 0 4px 0;font-family:Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#737373;">This email was sent to {{.Email}}.</p>
      <p style="margin:0 0 4px 0;font-family:Helvetica,Arial,sans-serif;font-size:12px;line-height:18px;color:#737373;">Netflix International B.V., Papendorpseweg 100, 3528 BJ Utrecht, Netherlands</p>
      <p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#737373;">
        <a href="#" style="color:#0071EB;text-decoration:none;">Help Centre</a> &nbsp;&middot;&nbsp;
        <a href="#" style="color:#0071EB;text-decoration:none;">Privacy</a> &nbsp;&middot;&nbsp;
        <a href="#" style="color:#0071EB;text-decoration:none;">Legal Notices</a>
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
<div style="text-align:center;padding:12px;font-size:11px;color:#999;border-top:1px solid #eee;margin-top:24px;">
  Suspicious? <a href="{{REPORT_URL}}" style="color:#999;">Report this email</a>
</div>
{{TRACKING_PIXEL}}
</body>
</html>
"""

_NETFLIX_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Netflix - Sign In</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #000000; font-family: Helvetica Neue, Helvetica, Arial, sans-serif; min-height: 100vh; position: relative; }
    .bg { position: fixed; inset: 0; background: url('https://assets.nflxext.com/ffe/siteui/vlv3/f841d4c7-10e1-40af-bcae-07a3f8dc141a/web/FR-en-20240101-popsignuptwoweeks-perspective_alpha_website_large.jpg') center/cover no-repeat; opacity: .5; z-index: 0; }
    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 1; }
    header { position: relative; z-index: 2; padding: 20px 48px; }
    .logo { color: #E50914; font-size: 36px; font-weight: 900; letter-spacing: -1px; font-family: Arial Black, Arial, sans-serif; }
    .main { position: relative; z-index: 2; display: flex; align-items: flex-start; justify-content: center; padding: 20px 24px 60px; min-height: calc(100vh - 76px); }
    .card { background: rgba(0,0,0,.75); border-radius: 4px; padding: 60px 68px 40px; width: 450px; }
    .card h1 { font-size: 32px; font-weight: 700; color: #ffffff; margin-bottom: 28px; }
    .form-group { margin-bottom: 16px; position: relative; }
    .form-group input { width: 100%; height: 50px; padding: 16px 20px 0 20px; background: #333333; border: none; border-radius: 4px; font-size: 16px; color: #ffffff; outline: none; }
    .form-group input:focus { background: #454545; }
    .form-group label { position: absolute; left: 20px; top: 50%; transform: translateY(-50%); color: #8c8c8c; font-size: 14px; pointer-events: none; transition: all .15s; }
    .form-group input:focus + label, .form-group input:not(:placeholder-shown) + label { top: 12px; font-size: 11px; transform: none; }
    .btn-signin { width: 100%; padding: 16px; background: #E50914; color: #ffffff; border: none; border-radius: 4px; font-size: 16px; font-weight: 700; cursor: pointer; margin: 8px 0 20px; }
    .btn-signin:hover { background: #f6121d; }
    .remember { display: flex; align-items: center; justify-content: space-between; font-size: 13px; color: #b3b3b3; margin-bottom: 20px; }
    .remember label { display: flex; align-items: center; gap: 6px; cursor: pointer; }
    .remember a { color: #b3b3b3; text-decoration: none; }
    .remember a:hover { text-decoration: underline; }
    .signup { font-size: 16px; color: #737373; margin-top: 16px; }
    .signup a { color: #ffffff; text-decoration: none; }
    .signup a:hover { text-decoration: underline; }
    .recaptcha { font-size: 13px; color: #8c8c8c; margin-top: 16px; line-height: 18px; }
    .recaptcha a { color: #0071EB; text-decoration: none; }
    footer { position: relative; z-index: 2; background: rgba(0,0,0,.75); padding: 24px 48px; }
    footer p { font-size: 13px; color: #737373; margin-bottom: 16px; }
    footer .links { display: flex; flex-wrap: wrap; gap: 12px 24px; }
    footer .links a { font-size: 13px; color: #737373; text-decoration: none; }
    footer .links a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="bg"></div>
  <div class="overlay"></div>
  <header>
    <span class="logo">NETFLIX</span>
  </header>
  <div class="main">
    <div class="card">
      <h1>Sign In</h1>
      <form method="post">
        <div class="form-group">
          <input type="email" id="email" name="email" placeholder=" " autocomplete="email" required />
          <label for="email">Email or phone number</label>
        </div>
        <div class="form-group">
          <input type="password" id="password" name="password" placeholder=" " autocomplete="current-password" required />
          <label for="password">Password</label>
        </div>
        <button type="submit" class="btn-signin">Sign In</button>
        <div class="remember">
          <label><input type="checkbox" name="remember" /> Remember me</label>
          <a href="#">Need help?</a>
        </div>
      </form>
      <div class="signup">New to Netflix? <a href="#">Sign up now</a>.</div>
      <p class="recaptcha">This page is protected by Google reCAPTCHA to ensure you're not a bot. <a href="#">Learn more.</a></p>
    </div>
  </div>
  <footer>
    <p>Questions? Call 00 800 7234 7234</p>
    <div class="links">
      <a href="#">FAQ</a><a href="#">Help Centre</a><a href="#">Terms of Use</a>
      <a href="#">Privacy</a><a href="#">Cookie Preferences</a><a href="#">Corporate Information</a>
    </div>
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
        'name': 'LinkedIn - Profile View Notification (EN)',
        'subject': 'Someone at Accenture viewed your profile',
        'email_html': _LINKEDIN_EMAIL_HTML,
        'landing_page_html': _LINKEDIN_LANDING_HTML,
    },
    {
        'name': 'Zoom - Cloud Recording Available (EN)',
        'subject': 'Your cloud recording is now available — Weekly Team Sync',
        'email_html': _ZOOM_EMAIL_HTML,
        'landing_page_html': _ZOOM_LANDING_HTML,
    },
    {
        'name': 'Netflix - Membership On Hold (EN)',
        'subject': 'Your Netflix membership is on hold',
        'email_html': _NETFLIX_EMAIL_HTML,
        'landing_page_html': _NETFLIX_LANDING_HTML,
    },
]


def register_commands(app):
    """Register Flask CLI commands with the app."""

    @app.cli.command('seed-templates')
    @click.option('--force', is_flag=True, default=False, help='Update HTML of existing templates.')
    @with_appcontext
    def seed_templates(force):
        """Pre-install built-in phishing templates (idempotent)."""
        admin = db.session.query(User).filter_by(is_admin=True).first()
        if admin is None:
            admin = db.session.query(User).first()
        if admin is None:
            click.echo('No users found — create an admin account first.', err=True)
            return

        inserted = 0
        updated = 0
        for tpl in _TEMPLATES:
            exists = db.session.query(Template).filter_by(name=tpl['name']).first()
            if exists:
                if force:
                    exists.email_html = tpl['email_html']
                    exists.landing_page_html = tpl['landing_page_html']
                    exists.subject = tpl['subject']
                    updated += 1
                    click.echo(f"  update {tpl['name']}")
                else:
                    click.echo(f"  skip  {tpl['name']} (already exists)")
                continue
            db.session.add(Template(
                name=tpl['name'],
                subject=tpl['subject'],
                email_html=tpl['email_html'],
                landing_page_html=tpl['landing_page_html'],
                created_by_user_id=admin.id,
            ))
            inserted += 1
            click.echo(f"  add   {tpl['name']}")

        if inserted or updated:
            db.session.commit()

        click.echo(f'Done — {inserted} template(s) inserted, {updated} updated.')

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
