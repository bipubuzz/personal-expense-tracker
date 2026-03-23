
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/expense_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'

# Initialize database
db = SQLAlchemy(app)


# DATABASE MODELS

class User(db.Model):
    # User table
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class admintb(db.Model):
    # admin table
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class expensestb(db.Model):
    # Expenses table
    __tablename__ = 'expensestb'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), db.ForeignKey('user.email'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    user = db.relationship('User', backref='expenses', foreign_keys=[user_email])

# Create tables
with app.app_context():
    
    db.create_all() 
    default_admin = admintb.query.first()
    if not default_admin:
        new_admin = admintb(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'))
        db.session.add(new_admin)
    db.session.commit()



@app.route('/')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    expenses = expensestb.query.filter_by(user_email=user_email).order_by(expensestb.date.desc()).all()
    
    total_amount = sum((expense.amount or 0) for expense in expenses)
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    today_total = 0.0
    month_total = 0.0
    now = datetime.utcnow()
    
    for expense in expenses:
        d = expense.date
        try:
            if isinstance(d, str):
                d_obj = datetime.strptime(d, '%Y-%m-%d').date()
            else:
                d_obj = d
        except Exception:
            d_obj = None
        
        if d_obj:
            if d_obj.strftime('%Y-%m-%d') == today_str:
                today_total += (expense.amount or 0)
            if d_obj.year == now.year and d_obj.month == now.month:
                month_total += (expense.amount or 0)
    
    category_totals = {}
    for e in expenses:
        cat = e.category 
        category_totals[cat] = category_totals.get(cat, 0) + (e.amount or 0)
    
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_cats[:3]
    recent_expenses = expenses[:5]
    donut_labels = [c for c, _ in sorted_cats]
    donut_amounts = [a for _, a in sorted_cats]
    
    return render_template('dashboard.html',
                         today_total=today_total,
                         month_total=month_total,
                         total_amount=total_amount,
                         expense_count=len(expenses),
                         donut_labels=donut_labels,
                         donut_amounts=donut_amounts,
                         top_categories=top_categories,
                         recent_expenses=recent_expenses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['email'] = email
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already exists')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reports')
def reports():
    # Reports page - View expense reports and analytics
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    expenses = expensestb.query.filter_by(user_email=user_email).all()
    
    category_totals = {}
    total_amount = 0.0
    timeline_totals = {}
    monthly_totals = {}
    
    for expense in expenses:
        category = (expense.category or 'Other')
        try:
            amount = float(expense.amount)
        except Exception:
            amount = 0.0
        
        # Sum by category
        category_totals[category] = category_totals.get(category, 0.0) + amount
        total_amount += amount
        
        # Sum by date for timeline
        date_val = expense.date
        try:
            if isinstance(date_val, str):
                date_key = date_val
            else:
                date_key = date_val.strftime('%Y-%m-%d')
        except Exception:
            date_key = datetime.utcnow().strftime('%Y-%m-%d')
        timeline_totals[date_key] = timeline_totals.get(date_key, 0.0) + amount
        
        # Sum by month for bar chart
        try:
            if isinstance(date_val, str):
                month_key = date_val[:7]  # YYYY-MM format
            else:
                month_key = date_val.strftime('%Y-%m')
        except Exception:
            month_key = datetime.utcnow().strftime('%Y-%m')
        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + amount
    
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())
    
    time_labels = sorted(timeline_totals.keys())
    time_amounts = [timeline_totals[d] for d in time_labels]
    
    # Bar chart data - by month
    bar_labels = sorted(monthly_totals.keys())
    bar_amounts = [monthly_totals[month] for month in bar_labels]
    
    return render_template(
        'reports.html', 
        categories=categories,
        amounts=amounts,
        total_amount=total_amount,
        expense_count=len(expenses),
        time_labels=time_labels,
        time_amounts=time_amounts,
        bar_labels=bar_labels,
        bar_amounts=bar_amounts
    )

@app.route('/allexpense', methods=['GET', 'POST'])
def allexpense():
    # All Expenses page - View all expenses for logged-in user with filtering
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Get logged-in user's email
    user_email = session['email']
    
    # Start with base query for this user
    query = expensestb.query.filter_by(user_email=user_email)
    
    # Get filter parameters from form (POST request)
    # Initialize with empty/default values for GET requests
    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        category = request.form.get('category', 'all').strip()
        min_amount = request.form.get('min-amount', '').strip()
        max_amount = request.form.get('max-amount', '').strip()
        start_date = request.form.get('start-date', '').strip()
        end_date = request.form.get('end-date', '').strip()
    else:
        # GET request - initialize with empty values (no filters applied)
        search_term = ''
        category = 'all'
        min_amount = ''
        max_amount = ''
        start_date = ''
        end_date = ''
    
    # Apply filters
    # Category filter
    if category and category != 'all':
        query = query.filter(expensestb.category == category)
    
    # Search filter (description or category)
    if search_term:
        query = query.filter(
            db.or_(
                expensestb.description.like(f'%{search_term}%'),
                expensestb.category.like(f'%{search_term}%')
            )
        )
    
    # Amount range filter
    if min_amount:
        try:
            min_val = float(min_amount)
            query = query.filter(expensestb.amount >= min_val)
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_val = float(max_amount)
            query = query.filter(expensestb.amount <= max_val)
        except ValueError:
            pass
    
    # Date range filter
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(expensestb.date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(expensestb.date <= end_dt)
        except ValueError:
            pass
    
    # Get filtered expenses, sorted by date (newest first)
    expenses = query.order_by(expensestb.date.desc()).all()
    
    # Calculate total amount of filtered expenses
    total = sum(expense.amount for expense in expenses)
    
    # Pass expenses, total, and current filter values to template
    return render_template('allexpense.html', 
                         expenses=expenses, 
                         total=total,
                         search_term=search_term,
                         selected_category=category, 
                         min_amount=min_amount,
                         max_amount=max_amount,
                         start_date=start_date,
                         end_date=end_date,
                         today=datetime.utcnow().strftime('%Y-%m-%d'))

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    # Compare expenses between two months
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    
    # Get all user expenses
    all_expenses = expensestb.query.filter_by(user_email=user_email).all()
    
    # Generate list of available months from user's expenses
    available_months = set()
    for expense in all_expenses:
        date_obj = expense.date
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        month_key = date_obj.strftime('%Y-%m')
        available_months.add(month_key)
    
    # Sort months in descending order (most recent first)
    available_months = sorted(list(available_months), reverse=True)
    
    # Get selected months from form or use defaults
    if request.method == 'POST':
        month1 = request.form.get('month1')
        month2 = request.form.get('month2')
    else:
        # Default to two most recent months if available
        month1 = available_months[0] if len(available_months) > 0 else None
        month2 = available_months[1] if len(available_months) > 1 else None
    
    # Calculate totals and daily data for both months
    month1_total = 0.0
    month2_total = 0.0
    month1_daily = {}
    month2_daily = {}
    
    if month1:
        for expense in all_expenses:
            date_obj = expense.date
            if isinstance(date_obj, str):
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            expense_month = date_obj.strftime('%Y-%m')
            
            if expense_month == month1:
                month1_total += float(expense.amount or 0)
                day_key = date_obj.strftime('%Y-%m-%d')
                month1_daily[day_key] = month1_daily.get(day_key, 0.0) + float(expense.amount or 0)
    
    if month2:
        for expense in all_expenses:
            date_obj = expense.date
            if isinstance(date_obj, str):
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            expense_month = date_obj.strftime('%Y-%m')
            
            if expense_month == month2:
                month2_total += float(expense.amount or 0)
                day_key = date_obj.strftime('%Y-%m-%d')
                month2_daily[day_key] = month2_daily.get(day_key, 0.0) + float(expense.amount or 0)
    
    # Calculate difference
    difference = month1_total - month2_total
    
    # Prepare timeline data (combine both months)
    timeline_labels = sorted(list(set(list(month1_daily.keys()) + list(month2_daily.keys()))))
    month1_timeline = [month1_daily.get(date, 0) for date in timeline_labels]
    month2_timeline = [month2_daily.get(date, 0) for date in timeline_labels]
    
    # Format month names for display
    month1_name = datetime.strptime(month1 + '-01', '%Y-%m-%d').strftime('%B %Y') if month1 else 'N/A'
    month2_name = datetime.strptime(month2 + '-01', '%Y-%m-%d').strftime('%B %Y') if month2 else 'N/A'
    
    return render_template('compare.html',
                         available_months=available_months,
                         selected_month1=month1,
                         selected_month2=month2,
                         month1_name=month1_name,
                         month2_name=month2_name,
                         month1_total=month1_total,
                         month2_total=month2_total,
                         difference=difference,
                         timeline_labels=timeline_labels,
                         month1_timeline=month1_timeline,
                         month2_timeline=month2_timeline)

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    # Delete an expense - Remove expense from database
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Find the expense by ID
    expense = expensestb.query.get(expense_id)
    
    # Security check: Make sure expense belongs to logged-in user
    if expense and expense.user_email != session['email']:
        return redirect(url_for('allexpense'))
    
    # Delete expense from database
    if expense:
        db.session.delete(expense)
        db.session.commit()
    
    # Return to all expenses page
    return redirect(url_for('allexpense'))


@app.route('/update_expense/<int:expense_id>', methods=['POST'])
def update_expense(expense_id):
    # Update an existing expense with form data from the add/edit popup
    if 'email' not in session:
        return redirect(url_for('login'))

    expense = expensestb.query.get(expense_id)
    if not expense:
        return redirect(url_for('allexpense'))

    # security: ensure owner
    if expense.user_email != session.get('email'):
        return redirect(url_for('allexpense'))

    # get form fields
    try:
        amount = float(request.form.get('amount') or 0)
    except ValueError:
        amount = expense.amount
    category = request.form.get('category') or expense.category
    description = request.form.get('description') or expense.description
    date_val = request.form.get('date') or None

    expense.amount = amount
    expense.category = category
    expense.description = description
    if date_val:
        try:
            new_date = datetime.strptime(date_val, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            
            # Only update if date is not in the future
            if new_date <= today:
                expense.date = new_date
            # If date is in future, keep the old date (ignore update)
        except Exception:
            pass

    db.session.commit()
    return redirect(url_for('allexpense'))

@app.route('/addexpense', methods=['GET', 'POST'])
def add_expense():
    # Add Expense - Create a new expense record
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date_str = request.form['date']
        
        # Validate date is not in the future
        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            
            if expense_date > today:
                return redirect(url_for('dashboard'))
        except ValueError:
            # Invalid date format
            return redirect(url_for('dashboard'))
        
        # Create new expense object
        new_expense = expensestb(
            user_email=session['email'],
            amount=amount,
            category=category,
            description=description,
            date=expense_date
        )
        
        # Save to database
        db.session.add(new_expense)
        db.session.commit()
        
        # Redirect to dashboard after adding expense
        return redirect(url_for('dashboard'))


@app.route('/profile')
def profile():
    # Profile page - View and edit user profile information
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    # Update user profile - Change username
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return redirect(url_for('login'))
    
    new_username = request.form.get('username', '').strip()
    
    if new_username:
        user.username = new_username
        session['username'] = new_username
        db.session.commit()
    
    return redirect(url_for('profile'))


@app.route('/change_password', methods=['POST'])
def change_password():
    # Change user password
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Verify current password
    if not check_password_hash(user.password, current_password):
        return render_template('profile.html', user=user, password_error='Current password is incorrect')
    
    # Check if new passwords match
    if new_password != confirm_password:
        return render_template('profile.html', user=user, password_error='New passwords do not match')
    
    # Check if new password is not empty
    if not new_password or len(new_password) < 6:
        return render_template('profile.html', user=user, password_error='New password must be at least 6 characters')
    
    # Update password
    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    
    return render_template('profile.html', user=user, password_success='Password changed successfully')


@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Delete user account and all associated data
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return redirect(url_for('login'))
    
    # Delete all expenses for this user
    expensestb.query.filter_by(user_email=user_email).delete()
    
    # Delete the user account
    db.session.delete(user)
    db.session.commit()
    
    # Clear session
    session.clear()
    
    return redirect(url_for('login'))


@app.route('/delete_all_expenses', methods=['POST'])
def delete_all_expenses():
    # Delete all expenses for the current user
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    
    # Delete all expenses for this user
    expensestb.query.filter_by(user_email=user_email).delete()
    db.session.commit()
    
    return redirect(url_for('profile'))


# Admin routes - Admin login, dashboard, user management
@app.route('/admin')
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Redirect if already logged in as admin
    if 'admin' in session:
        return redirect(url_for('admin_dashboard'))
    
    # Handle form submission
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        admin = admintb.query.filter_by(username=name).first()

        if admin and check_password_hash(admin.password, password):
            session['admin'] = name
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('adminlogin.html', error='Invalid username or password')
        
    return render_template('adminlogin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if admin is logged in
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Get all regular users (from User table)
    all_users = User.query.all()
    
    # Get all expenses sorted by date (most recent first)
    all_expenses = expensestb.query.order_by(expensestb.date.desc()).all()
    
    # Calculate statistics
    total_users = len(all_users)
    total_expenses_count = len(all_expenses)
    
    # Calculate 6 months ago for inactivity check
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    six_months_ago_date = six_months_ago.date()
    
    # Get most recent expense date for each user
    user_recent_expense = {}
    for expense in all_expenses:
        email = expense.user_email
        if email not in user_recent_expense:
            # Store the most recent expense date for this user
            user_recent_expense[email] = expense.date
    
    # Build user data with recent expense info
    users_with_data = []
    for user in all_users:
        recent_expense_date = user_recent_expense.get(user.email, None)
        
        # Check if inactive (no expense OR last expense > 6 months ago)
        is_inactive = False
        if not recent_expense_date:
            # No expenses at all - inactive
            is_inactive = True
        else:
            # Convert to date if it's a string
            if isinstance(recent_expense_date, str):
                try:
                    recent_expense_date = datetime.strptime(recent_expense_date, '%Y-%m-%d').date()
                except:
                    pass
            
            # Compare dates - if last expense is older than 6 months ago, inactive
            if recent_expense_date < six_months_ago_date:
                is_inactive = True
        
        users_with_data.append({
            'username': user.username,
            'email': user.email,
            'recent_expense': recent_expense_date,
            'is_inactive': is_inactive
        })
    
    # Build simplified expense data (user email, username, date only)
    expenses_data = []
    user_email_to_name = {user.email: user.username for user in all_users}
    
    for expense in all_expenses:
        expenses_data.append({
            'user_email': expense.user_email,
            'username': user_email_to_name.get(expense.user_email, 'Unknown'),
            'date': expense.date
        })
    
    return render_template('admindashboard.html',
                         users=users_with_data,
                         expenses=expenses_data,
                         total_users=total_users,
                         total_expenses_count=total_expenses_count,
                         )
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))



@app.route('/admin/delete-user/<user_email>', methods=['POST'])
def delete_user(user_email):
    # Check if admin is logged in
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Find user by email
    user = User.query.filter_by(email=user_email).first()
    
    if user:
        # Delete all expenses for this user first
        expensestb.query.filter_by(user_email=user_email).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
    
    # Redirect back to admin dashboard
    return redirect(url_for('admin_dashboard'))

# ============================================
# RUN THE APPLICATION
# ============================================
if __name__ == '__main__':
    app.run(debug=True)  # debug=True shows errors in browser (only for development)