from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import mongo  # Import mongo from the main app module
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from datetime import datetime
import bcrypt

main_bp = Blueprint('main', __name__)

# Gmail SMTP configuration
GMAIL_USER = os.getenv('GMAIL_USER')  # Use environment variable
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # Use environment variable
TO_EMAIL = os.getenv('TO_EMAIL', 'info@detwet.com')  # Recipient email address

# Input sanitization function
def sanitize_input(value):
    if not value:
        return ''
    # Remove potentially dangerous characters
    bad_chars = ['<', '>', '&', ';', 'script', 'alert']
    for char in bad_chars:
        value = value.replace(char, '')
    return value.strip()

@main_bp.route('/')
def index():
    users = list(mongo.db.users.find().limit(5))
    return render_template('index.html', users=users)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get form data
            name = sanitize_input(request.form.get('name', ''))
            email = sanitize_input(request.form.get('email', ''))
            subject = sanitize_input(request.form.get('subject', ''))
            message = sanitize_input(request.form.get('message', ''))

            # Server-side validation
            if not all([name, email, subject, message]):
                return jsonify({'success': False, 'message': 'All fields are required.'}), 400

            email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_pattern.match(email):
                return jsonify({'success': False, 'message': 'Invalid email address.'}), 400

            if len(message) < 2:
                return jsonify({'success': False, 'message': 'Message must be at least 2 characters long.'}), 400

            # Verify Gmail credentials
            if not GMAIL_USER or not GMAIL_APP_PASSWORD:
                return jsonify({'success': False, 'message': 'Email configuration is missing.'}), 500

            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = GMAIL_USER
            msg['To'] = TO_EMAIL
            msg['Subject'] = f"Contact Form Submission: {subject}"

            # Plain text fallback
            text_body = f"""
            New message from 1nFloU Contact Form:

            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """
            msg.attach(MIMEText(text_body, 'plain'))

            # Styled HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>1nFloU Contact Form Submission</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; background-color: #f8fafc; color: #1f2937; line-height: 1.6;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; padding: 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); overflow: hidden;">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                                        <img src="{os.getenv('BASE_URL', 'http://localhost:5000')}/static/images/logo.webp" alt="1nFloU Logo" style="max-width: 150px; height: auto;">
                                        <h1 style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 20px 0 10px;">New Contact Form Submission</h1>
                                    </td>
                                </tr>
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 30px;">
                                        <h2 style="font-size: 20px; font-weight: 600; color: #1f2937; margin-bottom: 20px;">Message Details</h2>
                                        <table width="100%" cellpadding="10" cellspacing="0" style="font-size: 16px; color: #1f2937;">
                                            <tr>
                                                <td style="width: 100px; font-weight: 600; color: #6366f1;">Name:</td>
                                                <td>{name}</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: 600; color: #6366f1;">Email:</td>
                                                <td><a href="mailto:{email}" style="color: #6366f1; text-decoration: none;">{email}</a></td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: 600; color: #6366f1;">Subject:</td>
                                                <td>{subject}</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: 600; color: #6366f1;">Message:</td>
                                                <td style="white-space: pre-wrap;">{message}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #f8fafc; padding: 20px; text-align: center; font-size: 14px; color: #6b7280;">
                                        <p style="margin: 0 0 10px;">Sent from <a href="{os.getenv('BASE_URL', 'http://localhost:5000')}" style="color: #6366f1; text-decoration: none;">1nFloU</a></p>
                                        <p style="margin: 0;">12 Vermeer, Bellville, Cape Town, South Africa, 7530</p>
                                        <p style="margin: 0;"><a href="mailto:info@detwet.com" style="color: #6366f1; text-decoration: none;">info@detwet.com</a> | <a href="tel:+27848662418" style="color: #6366f1; text-decoration: none;">+27 84 866 2418</a></p>
                                        <div style="margin-top: 20px;">
                                            <a href="#" style="margin: 0 10px; color: #6b7280; text-decoration: none;"><i style="font-family: 'Font Awesome 6 Free'; font-weight: 900;">&#xf09a;</i></a>
                                            <a href="#" style="margin: 0 10px; color: #6b7280; text-decoration: none;"><i style="font-family: 'Font Awesome 6 Free'; font-weight: 900;">&#xf16d;</i></a>
                                            <a href="#" style="margin: 0 10px; color: #6b7280; text-decoration: none;"><i style="font-family: 'Font Awesome 6 Free'; font-weight: 900;">&#xf099;</i></a>
                                            <a href="#" style="margin: 0 10px; color: #6b7280; text-decoration: none;"><i style="font-family: 'Font Awesome 6 Free'; font-weight: 900;">&#xf167;</i></a>
                                            <a href="#" style="margin: 0 10px; color: #6b7280; text-decoration: none;"><i style="font-family: 'Font Awesome 6 Free'; font-weight: 900;">&#xf1e8;</i></a>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # Connect to Gmail SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(msg)

            # Store contact submission in MongoDB (optional)
            mongo.db.contacts.insert_one({
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow()
            })

            return jsonify({'success': True, 'message': 'Message sent successfully!'})

        except smtplib.SMTPAuthenticationError:
            return jsonify({'success': False, 'message': 'Authentication failed. Please check your Gmail credentials.'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
    
    # Handle GET request to render the contact page
    return render_template('contact.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = sanitize_input(request.form.get('email', ''))
            password = request.form.get('password', '')

            # Server-side validation
            if not all([email, password]):
                flash('Email and password are required.', 'error')
                return redirect(url_for('main.login'))

            email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_pattern.match(email):
                flash('Invalid email address.', 'error')
                return redirect(url_for('main.login'))

            # Find user in MongoDB
            user = mongo.db.users.find_one({'email': email})
            if not user:
                flash('No account found with that email.', 'error')
                return redirect(url_for('main.login'))

            # Verify password
            if 'password' not in user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
                flash('Incorrect password.', 'error')
                return redirect(url_for('main.login'))

            # Successful login (for now, redirect to index; add session management later)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('main.login'))

    # Handle GET request to render the login page
    return render_template('login.html')

@main_bp.route('/add_user', methods=['POST'])
def add_user():
    try:
        name = sanitize_input(request.form.get('name', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')

        # Server-side validation
        if not all([name, email, password]):
            flash('Name, email, and password are required.', 'error')
            return redirect(url_for('main.index'))

        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        if not email_pattern.match(email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('main.index'))

        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return redirect(url_for('main.index'))

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        
        result = mongo.db.users.insert_one(user_data)
        flash('User added successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    except Exception as e:
        flash(f'Error adding user: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/api/users', methods=['GET'])
def api_users():
    # Example response, replace with actual logic as needed
    return {'users': []}