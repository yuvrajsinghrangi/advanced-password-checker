import re
import random
import string
import requests
import hashlib
from tkinter import *
from tkinter import messagebox
from cryptography.fernet import Fernet

# Encryption setup for password history
key = Fernet.generate_key()  # In production, save this securely
cipher = Fernet(key)

# File to save password history
HISTORY_FILE = "password_history.enc"

# Function to check password strength
def check_password_strength(password):
    length_error = len(password) < 12
    uppercase_error = not any(char.isupper() for char in password)
    lowercase_error = not any(char.islower() for char in password)
    digit_error = not any(char.isdigit() for char in password)
    special_char_error = not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    
    score = 0
    if not length_error: score += 2
    if not uppercase_error: score += 2
    if not lowercase_error: score += 2
    if not digit_error: score += 2
    if not special_char_error: score += 2
    
    errors = {
        "Too short (minimum 12 characters)": length_error,
        "Missing uppercase letter": uppercase_error,
        "Missing lowercase letter": lowercase_error,
        "Missing number": digit_error,
        "Missing special character": special_char_error,
    }
    suggestions = [msg for msg, error in errors.items() if error]
    return score, suggestions

# Function to check if password is breached
def is_password_breached(password):
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)
    if response.status_code == 200:
        hashes = response.text.splitlines()
        for h in hashes:
            if h.split(':')[0] == suffix:
                return True
    return False

# Function to generate a strong password
def generate_password(length=16):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))

# Save password history
def save_password_history(password, strength):
    encrypted_data = cipher.encrypt(f"{password} - {strength}\n".encode())
    with open(HISTORY_FILE, "ab") as file:
        file.write(encrypted_data + b"\n")

# Read password history
def load_password_history():
    try:
        with open(HISTORY_FILE, "rb") as file:
            encrypted_lines = file.readlines()
        return [cipher.decrypt(line.strip()).decode() for line in encrypted_lines]
    except FileNotFoundError:
        return []

# GUI Functions
def evaluate_password(event=None):
    password = password_entry.get()
    score, suggestions = check_password_strength(password)
    breached = is_password_breached(password)
    
    # Update feedback
    strength_label.config(text=f"Strength: {'Weak' if score < 8 else 'Strong'}")
    
    suggestion_text = "\n".join(suggestions)
    if breached:
        suggestion_text += "\nWARNING: This password is breached!"
    suggestions_label.config(text=suggestion_text)
    
    save_password_history(password, 'Strong' if score >= 8 else 'Weak')

def display_generated_password():
    strong_password = generate_password()
    password_entry.delete(0, END)
    password_entry.insert(0, strong_password)
    messagebox.showinfo("Generated Password", f"Your generated password is:\n{strong_password}")

def show_history():
    history = load_password_history()
    messagebox.showinfo("Password History", "\n".join(history))

# Tkinter GUI setup
root = Tk()
root.title("Advanced Password Strength Checker")
root.geometry("600x400")
root.configure(bg="#ffffff")

# Title
Label(root, text="Advanced Password Strength Checker", font=("Arial", 16, "bold"), bg="#FFFFFF").pack(pady=10)

# Password input field
Label(root, text="Enter your password:", font=("Arial", 12), bg="#FFFFFF").pack(pady=5)
password_entry = Entry(root, show="*", font=("Arial", 12), width=30)
password_entry.pack(pady=5)
password_entry.bind("<KeyRelease>", evaluate_password)

# Buttons
Button(root, text="Generate Strong Password", command=display_generated_password, font=("Arial", 10), bg="#007BFF", fg="Black").pack(pady=5)
Button(root, text="Show Password History", command=show_history, font=("Arial", 10), bg="#28a745", fg="Black").pack(pady=5)


# Footer with credit
Label(root, text="Made by Yuvraj Singh Rangi", font=("Arial", 10), bg="#ffffff").pack(side="bottom", pady=10)

# Run the GUI
root.mainloop()
