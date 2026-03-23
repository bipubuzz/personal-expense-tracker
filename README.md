# Personal Expense Tracker

A web-based expense tracking application built with Flask that helps users manage their personal finances, track spending habits, and visualize expense analytics.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

## Features

### User Features
- **User Authentication**: Secure login and registration system with password hashing
- **Dashboard**: Overview of daily, monthly, and total expenses with visual charts
- **Add Expenses**: Record expenses with amount, category, description, and date
- **View All Expenses**: Browse, search, and filter expenses with advanced filtering options
- **Edit/Delete Expenses**: Update or remove expense records
- **Reports & Analytics**: 
  - Category-wise expense breakdown with donut charts
  - Timeline view of spending patterns
  - Monthly comparison charts
- **Compare Months**: Compare expenses between two different months
- **Profile Management**: Update username and change password
- **Account Management**: Delete account and all associated data

### Admin Features
- **Admin Dashboard**: Overview of all users and expenses
- **User Management**: View all registered users with their recent activity
- **Inactive User Detection**: Identify users inactive for 6+ months
- **User Deletion**: Remove users and their data from the system

## Tech Stack

- **Backend**: Flask 3.0.0
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js for data visualization
- **Security**: Werkzeug password hashing (PBKDF2-SHA256)

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server (running on localhost:3306)
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/bipubuzz/personal-expense-tracker.git
   cd personal-expense-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the MySQL database**
   
   Create a database named `expense_tracker`:
   ```sql
   CREATE DATABASE expense_tracker;
   ```

6. **Update database credentials** (if needed)
   
   Edit `app.py` and modify the database URI:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://username:password@localhost:3306/expense_tracker'
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:5000/`

## Default Credentials

### Admin Access
- **Username**: `admin`
- **Password**: `admin`

### User Access
- Register a new account through the `/register` page

## Project Structure

```
personal-expense-tracker/
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── static/                     # Static files
│   ├── style.css              # Custom styles
│   └── js/
│       ├── script.js          # Main JavaScript
│       └── chart.js           # Chart configuration
└── templates/                  # HTML templates
    ├── layout.html            # Base template
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── dashboard.html         # User dashboard
    ├── addexpense.html        # Add expense form
    ├── allexpense.html        # View all expenses
    ├── reports.html           # Analytics page
    ├── compare.html           # Month comparison
    ├── profile.html           # User profile
    ├── adminlayout.html       # Admin base template
    ├── adminlogin.html        # Admin login
    └── admindashboard.html    # Admin dashboard
```

## Usage Guide

### Adding an Expense
1. Log in to your account
2. Click "Add Expense" from the navigation
3. Fill in the amount, category, description, and date
4. Click "Save" to record the expense

### Viewing Reports
1. Navigate to "Reports" from the menu
2. View category breakdown, timeline, and monthly charts


### Comparing Months
1. Go to "Compare" page
2. Select two months from the dropdown menus
3. View side-by-side comparison with difference calculation

### Admin Panel
1. Navigate to `/admin/login`
2. Log in with admin credentials
3. View all users 
4. Manage users (view/delete)

## Database Schema

### Tables

**user**
- `id` (Primary Key)
- `username`
- `email` (Unique)
- `password` (Hashed)

**admin**
- `id` (Primary Key)
- `username`
- `password` (Hashed)

**expensestb**
- `id` (Primary Key)
- `user_email` (Foreign Key → user.email)
- `amount`
- `category`
- `description`
- `date`

## Security Features

- Password hashing using PBKDF2-SHA256
- Session-based authentication
- SQL injection prevention via SQLAlchemy ORM
- User ownership validation for expense operations


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask framework and community
- Chart.js for data visualization
- Werkzeug for password hashing

## Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/bipubuzz/personal-expense-tracker/issues).
