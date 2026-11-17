import sqlite3
import io
import base64

import pyotp
import qrcode

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from flask_bcrypt import Bcrypt

from app.database import get_db_connection
from app.security import login_required, role_required


main = Blueprint('main', __name__)
bcrypt = Bcrypt()


# ==========================================
# COMPLETE LOGIN AFTER OTP VERIFICATION
# ==========================================

def complete_login(user):

    session.clear()

    session['user_id'] = user['user_id']
    session['user_name'] = user['full_name']
    session['full_name'] = user['full_name']
    session['user_role'] = user['role']

    flash('Login successful!')

    return redirect(url_for('main.home'))


# ==========================================
# HOME PAGE AND DASHBOARD REDIRECTION
# ==========================================

@main.route('/')
def home():

    if 'user_id' not in session:
        return render_template('index.html')

    user_role = session.get('user_role')

    if user_role == 'student':

        connection = get_db_connection()

        try:
            user_id = session['user_id']

            total_tickets = connection.execute(
                """
                SELECT COUNT(*)
                FROM tickets
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()[0]

            pending_tickets = connection.execute(
                """
                SELECT COUNT(*)
                FROM tickets
                WHERE user_id = ? AND status = 'Pending'
                """,
                (user_id,)
            ).fetchone()[0]

            resolved_tickets = connection.execute(
                """
                SELECT COUNT(*)
                FROM tickets
                WHERE user_id = ? AND status = 'Resolved'
                """,
                (user_id,)
            ).fetchone()[0]

            recent_tickets = connection.execute(
                """
                SELECT *
                FROM tickets
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (user_id,)
            ).fetchall()

        finally:
            connection.close()

        return render_template(
            'dashboard/student_dashboard.html',
            total_tickets=total_tickets,
            pending_tickets=pending_tickets,
            resolved_tickets=resolved_tickets,
            recent_tickets=recent_tickets
        )

    elif user_role == 'technician':
        return redirect(url_for('main.technician_dashboard'))

    elif user_role == 'admin':
        return redirect(url_for('main.admin_dashboard'))

    return "Welcome! Your dashboard is coming soon."


# ==========================================
# USER REGISTRATION
# ==========================================

@main.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').lower()

        if not full_name or not email or not password:
            flash('Please complete all required fields.')
            return redirect(url_for('main.register'))

        if role not in ('student', 'staff'):
            flash('Please select a valid account type.')
            return redirect(url_for('main.register'))

        if len(password) < 12:
            flash('Password must contain at least 12 characters.')
            return redirect(url_for('main.register'))

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users
                (full_name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, email, password_hash, role)
            )

            connection.commit()

            flash('Account created successfully! Please log in.')
            return redirect(url_for('main.login'))

        except sqlite3.IntegrityError:
            flash(
                'This email is already registered. '
                'Please use another email.'
            )
            return redirect(url_for('main.register'))

        except Exception:
            current_app.logger.exception('Registration failed')
            flash('Registration failed. Please try again.')
            return redirect(url_for('main.register'))

        finally:
            connection.close()

    return render_template('register.html')


# ==========================================
# USER LOGIN - PASSWORD VERIFICATION
# ==========================================

@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        connection = get_db_connection()

        try:
            user = connection.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if user and bcrypt.check_password_hash(
            user['password_hash'], password
        ):

            # Store temporary login information only.
            # The user is NOT authenticated yet.

            session.clear()

            session['pending_user_id'] = user['user_id']

            if user['otp_enabled'] == 1:
                return redirect(url_for('main.verify_otp'))

            return redirect(url_for('main.setup_otp'))

        flash('Invalid email or password.')
        return redirect(url_for('main.login'))

    return render_template('login.html')


# ==========================================
# SET UP GOOGLE AUTHENTICATOR
# ==========================================

@main.route('/setup-otp', methods=['GET', 'POST'])
def setup_otp():

    pending_user_id = session.get('pending_user_id')

    if not pending_user_id:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (pending_user_id,)
        ).fetchone()

        if user is None:
            session.clear()
            flash('Account not found.')
            return redirect(url_for('main.login'))

        if user['otp_enabled'] == 1:
            return redirect(url_for('main.verify_otp'))

        secret = user['otp_secret']

        if not secret:

            secret = pyotp.random_base32()

            connection.execute(
                """
                UPDATE users
                SET otp_secret = ?
                WHERE user_id = ?
                """,
                (secret, pending_user_id)
            )

            connection.commit()

        if request.method == 'POST':

            entered_code = request.form.get('otp_code', '').strip()

            totp = pyotp.TOTP(secret)

            if totp.verify(entered_code, valid_window=1):

                connection.execute(
                    """
                    UPDATE users
                    SET otp_enabled = 1
                    WHERE user_id = ?
                    """,
                    (pending_user_id,)
                )

                connection.commit()

                return complete_login(user)

            flash('Incorrect verification code. Please try again.')

        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
            name=user['email'],
            issuer_name='Secure Campus HelpDesk'
        )

        qr = qrcode.make(provisioning_uri)

        image_buffer = io.BytesIO()
        qr.save(image_buffer, format='PNG')

        qr_code = base64.b64encode(
            image_buffer.getvalue()
        ).decode('utf-8')

        return render_template(
            'setup_otp.html',
            qr_code=qr_code,
            secret=secret
        )

    finally:
        connection.close()


# ==========================================
# VERIFY GOOGLE AUTHENTICATOR OTP
# ==========================================

@main.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():

    pending_user_id = session.get('pending_user_id')

    if not pending_user_id:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (pending_user_id,)
        ).fetchone()

        if user is None:
            session.clear()
            flash('Account not found.')
            return redirect(url_for('main.login'))

        if not user['otp_enabled'] or not user['otp_secret']:
            return redirect(url_for('main.setup_otp'))

        if request.method == 'POST':

            entered_code = request.form.get('otp_code', '').strip()

            totp = pyotp.TOTP(user['otp_secret'])

            if totp.verify(entered_code, valid_window=1):
                return complete_login(user)

            flash('Invalid OTP code. Please try again.')

    finally:
        connection.close()

    return render_template('verify_otp.html')


# ==========================================
# USER LOGOUT
# ==========================================

@main.route('/logout', methods=['GET'])
def logout():

    session.clear()

    flash('You have been logged out successfully.')

    return redirect(url_for('main.login'))


# ==========================================
# SUBMIT SUPPORT TICKET
# ==========================================

@main.route('/submit-ticket', methods=['GET', 'POST'])
@login_required
@role_required('student', 'staff')
def submit_ticket():

    if request.method == 'POST':

        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        allowed_categories = (
            'Network/Wi-Fi',
            'Computer/Hardware',
            'Software Installation',
            'Student Portal',
            'Password Reset',
            'Printer/Scanner',
            'Email Access'
        )

        if not title or not description or category not in allowed_categories:
            flash('Please complete all ticket fields correctly.')
            return redirect(url_for('main.submit_ticket'))

        if len(title) > 150:
            flash('Ticket title must not exceed 150 characters.')
            return redirect(url_for('main.submit_ticket'))

        if len(description) > 5000:
            flash('Ticket description must not exceed 5000 characters.')
            return redirect(url_for('main.submit_ticket'))

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO tickets
                (user_id, title, description, category, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session['user_id'],
                    title,
                    description,
                    category,
                    'Pending'
                )
            )

            connection.commit()

            flash('Your support ticket has been submitted successfully!')

            return redirect(url_for('main.my_tickets'))

        except Exception:
            current_app.logger.exception('Ticket submission failed')
            flash('Unable to submit your ticket. Please try again.')
            return redirect(url_for('main.submit_ticket'))

        finally:
            connection.close()

    return render_template('dashboard/submit_ticket.html')


# ==========================================
# MY TICKETS PAGE
# ==========================================

@main.route('/my-tickets')
@login_required
def my_tickets():

    connection = get_db_connection()

    try:
        tickets = connection.execute(
            """
            SELECT *
            FROM tickets
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (session['user_id'],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        'dashboard/my_tickets.html',
        tickets=tickets
    )


# ==========================================
# TECHNICIAN DASHBOARD
# ==========================================

@main.route('/technician-dashboard')
@login_required
@role_required('technician')
def technician_dashboard():

    technician_id = session['user_id']

    connection = get_db_connection()

    try:
        tickets = connection.execute(
            """
            SELECT
                tickets.*,
                users.full_name AS requester_name
            FROM tickets
            JOIN users
            ON tickets.user_id = users.user_id
            WHERE tickets.assigned_to = ?
            ORDER BY tickets.created_at DESC
            """,
            (technician_id,)
        ).fetchall()

        total_tickets = connection.execute(
            """
            SELECT COUNT(*) FROM tickets
            WHERE assigned_to = ?
            """,
            (technician_id,)
        ).fetchone()[0]

        pending_tickets = connection.execute(
            """
            SELECT COUNT(*) FROM tickets
            WHERE assigned_to = ? AND status = 'Pending'
            """,
            (technician_id,)
        ).fetchone()[0]

        in_progress_tickets = connection.execute(
            """
            SELECT COUNT(*) FROM tickets
            WHERE assigned_to = ? AND status = 'In Progress'
            """,
            (technician_id,)
        ).fetchone()[0]

        resolved_tickets = connection.execute(
            """
            SELECT COUNT(*) FROM tickets
            WHERE assigned_to = ? AND status = 'Resolved'
            """,
            (technician_id,)
        ).fetchone()[0]

    finally:
        connection.close()

    return render_template(
        'technician/technician_dashboard.html',
        tickets=tickets,
        total_tickets=total_tickets,
        pending_tickets=pending_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets
    )


# ==========================================
# TECHNICIAN: UPDATE TICKET STATUS
# ==========================================

@main.route(
    '/technician/ticket/<int:ticket_id>/update',
    methods=['POST']
)
@main.route('/technician/update-ticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required('technician')
def update_ticket_status(ticket_id):

    new_status = request.form.get('status', '')

    allowed_statuses = (
        'Pending',
        'In Progress',
        'Resolved',
        'Closed'
    )

    if new_status not in allowed_statuses:
        flash('Invalid ticket status.')
        return redirect(url_for('main.technician_dashboard'))

    connection = get_db_connection()

    try:
        ticket = connection.execute(
            """
            SELECT ticket_id
            FROM tickets
            WHERE ticket_id = ?
            AND assigned_to = ?
            """,
            (ticket_id, session['user_id'])
        ).fetchone()

        if ticket is None:
            flash('Ticket not found or not assigned to you.')
            return redirect(url_for('main.technician_dashboard'))

        connection.execute(
            """
            UPDATE tickets
            SET status = ?
            WHERE ticket_id = ?
            AND assigned_to = ?
            """,
            (new_status, ticket_id, session['user_id'])
        )

        connection.commit()

        flash('Ticket status updated successfully!')

    finally:
        connection.close()

    return redirect(url_for('main.technician_dashboard'))


# ==========================================
# ADMIN DASHBOARD AND TICKET MONITORING
# ==========================================

@main.route('/admin-dashboard')
@login_required
@role_required('admin')
def admin_dashboard():

    selected_status = request.args.get('status', 'All')

    allowed_statuses = (
        'All',
        'Pending',
        'In Progress',
        'Resolved',
        'Closed'
    )

    if selected_status not in allowed_statuses:
        selected_status = 'All'

    connection = get_db_connection()

    try:
        total_users = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        total_students = connection.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'student'"
        ).fetchone()[0]

        total_technicians = connection.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'technician'"
        ).fetchone()[0]

        total_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

        pending_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Pending'"
        ).fetchone()[0]

        in_progress_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'In Progress'"
        ).fetchone()[0]

        resolved_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'"
        ).fetchone()[0]

        closed_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'Closed'"
        ).fetchone()[0]

        users = connection.execute(
            """
            SELECT user_id, full_name, email, role
            FROM users
            ORDER BY user_id DESC
            """
        ).fetchall()

        technicians = connection.execute(
            """
            SELECT user_id, full_name
            FROM users
            WHERE role = 'technician'
            ORDER BY full_name ASC
            """
        ).fetchall()

        tickets = connection.execute(
            """
            SELECT
                tickets.*,
                requester.full_name AS requester_name,
                technician.full_name AS technician_name
            FROM tickets
            JOIN users AS requester
                ON tickets.user_id = requester.user_id
            LEFT JOIN users AS technician
                ON tickets.assigned_to = technician.user_id
            WHERE (? = 'All' OR tickets.status = ?)
            ORDER BY tickets.created_at DESC
            """,
            (selected_status, selected_status)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        'admin/admin_dashboard.html',
        total_users=total_users,
        total_students=total_students,
        total_technicians=total_technicians,
        total_tickets=total_tickets,
        pending_tickets=pending_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        closed_tickets=closed_tickets,
        pending_count=pending_tickets,
        in_progress_count=in_progress_tickets,
        resolved_count=resolved_tickets,
        closed_count=closed_tickets,
        users=users,
        technicians=technicians,
        tickets=tickets,
        selected_status=selected_status
    )


# ==========================================
# ADMIN: CHANGE USER ROLE
# ==========================================

@main.route(
    '/admin/user/<int:user_id>/change-role',
    methods=['POST']
)
@login_required
@role_required('admin')
def change_user_role(user_id):

    new_role = request.form.get('role', '').lower()

    allowed_roles = ('student', 'staff', 'technician')

    if new_role not in allowed_roles:
        flash('Invalid user role selected.')
        return redirect(url_for('main.admin_dashboard'))

    if user_id == session['user_id']:
        flash('You cannot change your own administrator role.')
        return redirect(url_for('main.admin_dashboard'))

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        if user is None:
            flash('User not found.')

        elif user['role'] == 'admin':
            flash('Administrator accounts cannot be changed here.')

        else:
            connection.execute(
                """
                UPDATE users
                SET role = ?
                WHERE user_id = ?
                """,
                (new_role, user_id)
            )

            connection.commit()

            flash('User role updated successfully!')

    finally:
        connection.close()

    return redirect(url_for('main.admin_dashboard'))


# ==========================================
# ADMIN: ASSIGN TICKET
# ==========================================

@main.route('/admin/assign-ticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required('admin')
def assign_ticket(ticket_id):

    technician_id = request.form.get('technician_id')

    connection = get_db_connection()

    try:
        technician = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ? AND role = 'technician'
            """,
            (technician_id,)
        ).fetchone()

        if technician is None:
            flash('Please select a valid technician.')

        else:
            connection.execute(
                """
                UPDATE tickets
                SET assigned_to = ?
                WHERE ticket_id = ?
                """,
                (technician_id, ticket_id)
            )

            connection.commit()
            flash('Ticket assigned successfully!')

    finally:
        connection.close()

    return redirect(url_for('main.admin_dashboard'))