
# flask is the library and Flask is the class 
from flask import Flask
from flask import Flask, render_template, request, session  # allows Flask to remember the user's logins
from flask import render_template #  render template is a function that load and display html  forms
from flask import request  # get info that submitted by users
import sqlite3  #  its a python module siconnect python to SQLite 
from werkzeug.security import generate_password_hash, check_password_hash  # a python library for build pass security
# geneate.. will convert password into secure hash before saving in SQlite
import time  # track the 60 seconds

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)  # create a flask application
import os
app.secret_key = os.environ["FLASK_SECRET_KEY"]


#  function to create database or update
def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()   # Create a cursor to execute SQL commands
# Execute SQL command to create a table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS  users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            locked_until REAL DEFAULT 0
        )
 """)
# add more columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "failed_attempts" not in columns:
        cursor.execute(
           "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0"
        )
    if "locked_until" not in columns :
        cursor.execute(
            "ALTER TABLE users ADD COLUMN locked_until INTEGER DEFAULT 0"
        )
    
    connection.commit()
    connection.close()



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    answer = request.form["security_answer"]


    if len(password) < 8:
        return render_template("message.html", message="Password must be at least 8 characters.")

    if not password[0].isupper():
        return render_template("message.html",message= "The first letter of the password must be uppercase.")
        
    hashed_password = generate_password_hash(password)
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

       
    try:
        cursor.execute(
            "INSERT INTO users (username, password, security_answer) VALUES (?, ?, ?)",
            (username, hashed_password, answer)
        )

        connection.commit()
        message = "Account created successfully."

    except sqlite3.IntegrityError:
        message = "Username already exists."
   
    connection.close()
    return render_template("message.html", message=message)


 # connects the webside URL to a python function 
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Get password, failed attempts, and lock time from database
    cursor.execute(
        "SELECT password, failed_attempts, locked_until FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    # Check if user exists
    if user is None:
        connection.close()
        return render_template("message.html", message = "Invalid username or password.")

    stored_password = user[0]  # Password hash in database
    failed_attempts = user[1]  # Number of wrong passwords
    locked_until = user[2]     # Time when account lock expires

    # Check if the account is still locked
    if locked_until > time.time():
        remaining_seconds = int(locked_until - time.time()) + 1
        connection.close()
        return render_template(
    "message.html", message=f"Your account is locked. Try again in {remaining_seconds} seconds."
)
    # Check if the password is correct
    if check_password_hash(stored_password, password):

        # Reset failed attempts and lock time after successful login
        cursor.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = 0 WHERE username = ?",
            (username,)
        )

        connection.commit()
        connection.close()

        return render_template("message.html", message="Login successful.")

    else:
        # Increase failed attempts after a wrong password
        failed_attempts += 1

        # Lock the account after 3 wrong attempts
        if failed_attempts >= 3:
            locked_until = time.time() + 60

            cursor.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = ? WHERE username = ?",
                (locked_until, username)
            )
        

            connection.commit()
            connection.close()

            return render_template("message.html",message = "Your account has been locked for 60 seconds.")

        # Save the new failed attempt count
        cursor.execute(
            "UPDATE users SET failed_attempts = ? WHERE username = ?",
            (failed_attempts, username)
        )

        connection.commit()
        connection.close()

        return render_template("message.html", message="Invalid username or password.")


@app.route("/reset", methods=["POST"])
def reset():
    username = request.form["username"]
    answer = request.form["security_answer"]
    new_password = request.form["new_password"]
    # Check if the new password has at least 8 characters
    if len(new_password) < 8:
      return "Password must be at least 8 characters."

# Check if the first character is uppercase
    if not new_password[0].isupper():
      return "The first letter of the password must be uppercase."

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT security_answer FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return render_template("message.html", message="Invalid username or password.")

    if answer != user[0]:
        connection.close()
        return render_template("message.html", message="Security answer is incorrect.")
    
    hashed_password = generate_password_hash(new_password)
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hashed_password, username)
    )

    connection.commit()
    connection.close()
    return render_template("message.html", message= "Password reset successfully.")
create_database()
if __name__ == "__main__":
    app.run(debug=True)