
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import mysql.connector
from database import connect_to_database
from gui import set_background, admin_panel, user_panel, create_account, go_back, login

# Main Menu function
def main_menu(root, notebook):
    # Remove existing frames
    for widget in notebook.winfo_children():
        widget.destroy()

    root.title("Blood Bank Management System")

    # Create the main frame for the login
    main_frame = tk.Frame(notebook, width=800, height=600)
    main_frame.pack_propagate(False)  # Prevent frame from resizing to fit its children

    # Set background image
    set_background(main_frame, "BG.jpg")

    notebook.add(main_frame, text="Login")

    tk.Label(main_frame, text="Username", bg="white").grid(row=0, column=0, padx=10, pady=10)
    global username_entry, password_entry
    username_entry = tk.Entry(main_frame)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Password", bg="white").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(main_frame, show='*')
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(main_frame, text="Login", command=lambda: login(root, notebook, main_frame)).grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(main_frame, text="Create Account", command=lambda: create_account(notebook)).grid(row=3, column=0, columnspan=2, pady=10)

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    main_menu(root, notebook)  # Load the main menu with background
    root.mainloop()
