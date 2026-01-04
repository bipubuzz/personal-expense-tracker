
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/expense_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'  # Secret key for session management

# Initialize database
db = SQLAlchemy(app)



# DATABASE MODELS (TABLES)


class User(db.Model):
    """User table: Stores user account information"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class expensestb(db.Model):
    """Expenses table: Stores all expense records"""
    __tablename__ = 'expensestb'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), db.ForeignKey('user.email'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Link to User table
    user = db.relationship('User', backref='session_data', foreign_keys=[user_email])

# Create all database tables
with app.app_context():
    db.create_all()

# ============================================
# ROUTES (WEB PAGES)
# ============================================

@app.route('/')
def dashboard():
    """Home page - Shows dashboard with expense overview"""
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))
    user_email = session['email']
    # Query user expenses
    expenses = expensestb.query.filter_by(user_email=user_email).order_by(expensestb.date.desc()).all()

    total_amount = sum((expense.amount or 0) for expense in expenses)
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    today_total = 0.0
    month_total = 0.0
    now = datetime.utcnow()
    for expense in expenses:
        # normalize date to date object
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

    # Category breakdown
    category_totals = {}
    for e in expenses:
        cat = e.category or 'Other'
        category_totals[cat] = category_totals.get(cat, 0) + (e.amount or 0)

    # Top categories
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_cats[:3]

    # Recent expenses (limit 5)
    recent_expenses = expenses[:5]

    # Prepare data for donut chart
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
    """Login page - User authentication"""
    # If already logged in, go to dashboard
    if 'email' in session:
        return redirect(url_for('dashboard'))
    
    # Handle form submission
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists with matching email and password
        user = User.query.filter_by(email=email, password=password).first()
        
        if user:
            # Login successful: Save user info in session
            session['email'] = email
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            # Login failed: Show error message
            return render_template('login.html', error='Invalid email or password')
    
    # Show login page (GET request)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page - Create new user account"""
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already exists')
        
        # Create new user account
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to login page after successful registration
        return redirect(url_for('login'))
    
    # Show registration page (GET request)
    return render_template('register.html')



@app.route('/logout')
def logout():
    """Logout - Clear session and return to login"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/reports')
def reports():
    """Reports page - View expense reports and analytics"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['email']
    expenses = expensestb.query.filter_by(user_email=user_email).all()
    
    category_totals = {}
    total_amount = 0.0
    timeline_totals = {}
    
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
    
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())
    
    time_labels = sorted(timeline_totals.keys())
    time_amounts = [timeline_totals[d] for d in time_labels]
    
    bar_labels = categories
    bar_amounts = amounts
    
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
    """All Expenses page - View all expenses for logged-in user with filtering"""
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
                         end_date=end_date)

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense - Remove expense from database"""
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
    """Update an existing expense with form data from the add/edit popup"""
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
            expense.date = datetime.strptime(date_val, '%Y-%m-%d').date()
        except Exception:
            pass

    db.session.commit()
    return redirect(url_for('allexpense'))


@app.route('/addexpense', methods=['GET', 'POST'])
def add_expense():
    """Add Expense - Create a new expense record"""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        
        # Create new expense object
        new_expense = expensestb(
            user_email=session['email'],
            amount=amount,
            category=category,
            description=description,
            date=date
        )
        
        # Save to database
        db.session.add(new_expense)
        db.session.commit()
        
        # Redirect to dashboard after adding expense
        return redirect(url_for('dashboard'))

# ============================================
# RUN THE APPLICATION
# ============================================
if __name__ == '__main__':
    app.run(debug=True)  # debug=True shows errors in browser (only for development)