# Password Authentication System

This project is a simple password-based authentication system using Python Flask, HTML, CSS, and SQLite.

## Features:
- User registration
- User login
- Password hashing with a unique salt for each password
- Generic error messages for incorrect login information
- Account locking for 60 seconds after 3 failed login attempts
- Password reset using a security question
- Password must have at least 8 characters and start with an uppercase letter

## How to Run:
1. Open the project folder in VS Code.
2. Open the terminal.
3. Install Flask and python-dotenv:
   ```
   pip install flask python-dotenv
   ```
4. Create a `.env` file with a `FLASK_SECRET_KEY`.
5. Run:
   ```
   python login.py
   ```
6. Open:
   http://127.0.0.1:5000

## How to Test:
1. Register a new username and password.
2. Log in using the same username and password.
3. Enter the wrong password 3 times to lock the account.
4. Try logging in during the 60-second lock.
5. After 60 seconds, log in with the correct password.
6. Use Reset Password to change the password.
7. Log in again using the new password.

