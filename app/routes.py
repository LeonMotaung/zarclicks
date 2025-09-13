    
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
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL', 'info@detwet.com')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')  # Define upload folder

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Input sanitization function
def sanitize_input(value):
    if not value:
        return ''
    bad_chars = ['<', '>', '&', ';', 'script', 'alert']
    for char in bad_chars:
        value = value.replace(char, '')
    return value.strip()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/blog')
def blog():
    return render_template('blog.html')

@main_bp.route('/rank')
def rank():
    return render_template('rank.html')

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in request.cookies:
        return redirect(url_for('main.login_page'))
    return render_template('dashboard.html')

@main_bp.route('/services')
def services():
    return render_template('services.html')

@main_bp.route('/api')
def api():
    return render_template('api.html')

@main_bp.route('/api/doc')
def api_doc():
    return render_template('doc.html')

# Normal route for manual navigation
@main_bp.route("/404")
def not_found_page():
    return render_template("404.html"), 404

# Global 404 error handler
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

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

            if not GMAIL_USER or not GMAIL_APP_PASSWORD:
                return jsonify({'success': False, 'message': 'Email configuration is missing.'}), 500

            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = GMAIL_USER
            msg['To'] = TO_EMAIL
            msg['Subject'] = f"Contact Form Submission: {subject}"

            text_body = f"""
            New message from 1nFloU Contact Form:
            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """
            msg.attach(MIMEText(text_body, 'plain'))

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
                                <tr>
                                    <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                                        <img src="{BASE_URL}/static/images/logo.png" alt="1nFloU Logo" style="max-width: 150px; height: auto;">
                                        <h1 style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 20px 0 10px;">New Contact Form Submission</h1>
                                    </td>
                                </tr>
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
                                <tr>
                                    <td style="background-color: #f8fafc; padding: 20px; text-align: center; font-size: 14px; color: #6b7280;">
                                        <p style="margin: 0 0 10px;">Sent from <a href="{BASE_URL}" style="color: #6366f1; text-decoration: none;">1nFloU</a></p>
                                        <p style="margin: 0;">12 Vermeer, Bellville, Cape Town, South Africa, 7530</p>
                                        <p style="margin: 0;"><a href="mailto:info@detwet.com" style="color: #6366f1; text-decoration: none;">info@detwet.com</a> | <a href="tel:+27848662418" style="color: #6366f1; text-decoration: none;">+27 84 866 2418</a></p>
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

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.send_message(msg)

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

    return render_template('contact.html')

@main_bp.route('/register_page', methods=['GET'])
def register_page():
    return render_template('register.html')

@main_bp.route('/register', methods=['POST'], endpoint='user_register')
def register():
    try:
        user_type = sanitize_input(request.form.get('user_type'))
        full_name = sanitize_input(request.form.get('full_name'))
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = sanitize_input(request.form.get('phone'))
        location = sanitize_input(request.form.get('location'))
        terms = request.form.get('terms')

        # Server-side validation
        if not all([full_name, email, password, confirm_password, phone, location]) or terms != 'on':
            flash('All fields are required and you must agree to terms.', 'danger')
            return redirect(url_for('main.register_page'))

        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        if not email_pattern.match(email):
            flash('Invalid email address.', 'danger')
            return redirect(url_for('main.register_page'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.register_page'))

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('main.register_page'))

        if user_type not in ['brand', 'influencer']:
            flash('Invalid user type.', 'danger')
            return redirect(url_for('main.register_page'))

        # Check if email exists
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register_page'))

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Handle common file upload: profile picture
        profile_picture = ''
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                profile_picture = filename

        user_data = {
            'user_type': user_type,
            'full_name': full_name,
            'email': email,
            'password': hashed_password,
            'phone': phone,
            'location': location,
            'profile_picture': profile_picture,
            'created_at': datetime.utcnow(),
            'terms_agreed': True
        }

        if user_type == 'influencer':
            username = sanitize_input(request.form.get('username'))
            primary_platform = request.form.getlist('primary_platform')
            social_links = [sanitize_input(link.strip()) for link in request.form.get('social_links', '').split(',') if link.strip()]
            follower_count = request.form.get('follower_count')
            niche = sanitize_input(request.form.get('niche'))
            bio = sanitize_input(request.form.get('bio'))

            # Handle portfolio upload
            portfolio = ''
            if 'portfolio' in request.files:
                file = request.files['portfolio']
                if file and allowed_file(file.filename):
                    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    portfolio = filename

            if not all([username, follower_count, niche]):
                flash('All influencer fields are required.', 'danger')
                return redirect(url_for('main.register_page'))

            try:
                follower_count = int(follower_count)
                if follower_count <= 0:
                    flash('Follower count must be a positive number.', 'danger')
                    return redirect(url_for('main.register_page'))
            except ValueError:
                flash('Invalid follower count.', 'danger')
                return redirect(url_for('main.register_page'))

            user_data.update({
                'username': username,
                'primary_platform': primary_platform,
                'social_links': social_links,
                'follower_count': follower_count,
                'niche': niche,
                'bio': bio,
                'portfolio': portfolio
            })

        elif user_type == 'brand':
            brand_name = sanitize_input(request.form.get('brand_name'))
            website = sanitize_input(request.form.get('website'))
            industry = sanitize_input(request.form.get('industry'))
            company_size = sanitize_input(request.form.get('company_size'))
            budget_range = sanitize_input(request.form.get('budget_range'))
            preferred_niches = request.form.getlist('preferred_niches')
            brand_bio = sanitize_input(request.form.get('brand_bio'))

            if not all([brand_name, industry]):
                flash('All brand fields are required.', 'danger')
                return redirect(url_for('main.register_page'))

            user_data.update({
                'brand_name': brand_name,
                'website': website,
                'industry': industry,
                'company_size': company_size,
                'budget_range': budget_range,
                'preferred_niches': preferred_niches,
                'brand_bio': brand_bio
            })

        mongo.db.users.insert_one(user_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login_page'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('main.register_page'))

@main_bp.route('/login_page', methods=['GET'])
def login_page():
    return render_template('login.html')
    
@main_bp.route('/login_page', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)

        # Server-side validation
        if not all([email, password]):
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        if not email_pattern.match(email):
            return jsonify({'success': False, 'message': 'Invalid email address.'}), 400

        # Find user in MongoDB
        user = mongo.db.users.find_one({'email': email})
        if not user:
            return jsonify({'success': False, 'message': 'No account found with that email.'}), 401

        # Verify password
        if 'password' not in user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'success': False, 'message': 'Incorrect password.'}), 401

        # Successful login (return user data for client-side handling)
        user_data = {
            'full_name': user['full_name'],
            'email': user['email'],
            'user_type': user['user_type']
        }
        return jsonify({'success': True, 'message': 'Login successful!', 'user': user_data})

    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

