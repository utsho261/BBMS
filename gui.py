
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from database import connect_to_database

# Function to set background
def set_background(frame, image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(frame, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Function to navigate back in tabs
def go_back(notebook):
    current_tab_index = notebook.index(notebook.select())
    if current_tab_index > 0:
        notebook.select(notebook.tabs()[current_tab_index - 1])

# Function for authentication
def authenticate_user(username, password):
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT Role FROM User WHERE Username = %s AND Password = %s", (username, password))
    role = cursor.fetchone()
    db.close()
    return role[0] if role else None

# Function for login process
def login(root, notebook, frame):
    username = username_entry.get()
    password = password_entry.get()
    role = authenticate_user(username, password)

    if role == 'Admin':
        admin_panel(root, notebook)
        frame.destroy()  # Destroy the current frame
    elif role == 'User':
        user_panel(root, notebook)
        frame.destroy()  # Destroy the current frame
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Function for logout
def logout(root, notebook):
    for widget in notebook.winfo_children():
        widget.destroy()
    main_menu(root, notebook)

# Function to create a new account
def create_account(notebook):
    account_frame = tk.Frame(notebook, width=800, height=600)
    account_frame.pack_propagate(False)
    set_background(account_frame, "BG.jpg")
    notebook.add(account_frame, text="Create Account")

    tk.Label(account_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(account_frame)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(account_frame, text="Role").grid(row=1, column=0, padx=10, pady=10)
    role_combobox = ttk.Combobox(account_frame, values=["User", "Admin"])
    role_combobox.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(account_frame, text="Password").grid(row=2, column=0, padx=10, pady=10)
    password_entry = tk.Entry(account_frame, show='*')
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Button(account_frame, text="Create Account", command=lambda: save_account(username_entry.get(), password_entry.get(), role_combobox.get(), notebook)).grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(account_frame, text="Back", command=lambda: go_back(notebook)).grid(row=4, column=0, columnspan=2, pady=10)

# Function to save account
def save_account(username, password, role, notebook):
    if username and password and role:
        db = connect_to_database()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO User (Username, Password, Role) VALUES (%s, %s, %s)", (username, password, role))
            db.commit()
            messagebox.showinfo("Success", "Account created successfully")
            go_back(notebook)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        db.close()
    else:
        messagebox.showwarning("Warning", "Please fill all fields")

# Admin and User Panels
def admin_panel(root, notebook):
    admin_frame = tk.Frame(notebook, width=800, height=600)
    admin_frame.pack_propagate(False)
    set_background(admin_frame, "BG.jpg")
    notebook.add(admin_frame, text="Admin Panel")
    # Other admin features

def user_panel(root, notebook):
    user_frame = tk.Frame(notebook, width=800, height=600)
    user_frame.pack_propagate(False)
    set_background(user_frame, "BG.jpg")
    notebook.add(user_frame, text="User Panel")
    # Other user features
