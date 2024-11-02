import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk

# Database connection
def connect_to_database():
    return mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")

def set_background(frame, image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(frame, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Set the label to cover the whole frame

# Navigation Functions
def go_back(notebook):
    current_tab_index = notebook.index(notebook.select())
    if current_tab_index > 0:
        notebook.select(notebook.tabs()[current_tab_index - 1])

# Authentication and role-based access
def authenticate_user(username, password):
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT Role FROM User WHERE Username = %s AND Password = %s", (username, password))
    role = cursor.fetchone()
    db.close()
    return role[0] if role else None

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

def logout(root, notebook):
    # Destroy all current frames in the notebook
    for widget in notebook.winfo_children():
        widget.destroy()
    # Return to the main login screen
    main_menu(root, notebook)

def create_account(notebook):
    # Create a new frame for the account creation
    account_frame = tk.Frame(notebook, width=800, height=600)
    account_frame.pack_propagate(False)  # Prevent frame from resizing to fit its children
    set_background(account_frame, "BG.jpg")

    # Add the new frame as a tab in the notebook
    notebook.add(account_frame, text="Create Account")

    # Create the account creation UI elements
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

def switch_to_tab(notebook, tab_name):
    for tab in notebook.tabs():
        if notebook.tab(tab, "text") == tab_name:
            notebook.select(tab)
            return

def save_account(username, password, role, notebook):
    if username and password and role:
        db = connect_to_database()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO User (Username, Password, Role) VALUES (%s, %s, %s)", (username, password, role))
            db.commit()
            messagebox.showinfo("Success", "Account created successfully")
            go_back(notebook)  # Go back to the previous tab
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        db.close()
    else:
        messagebox.showwarning("Warning", "Please fill all fields")

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

# Admin and User Panels
def admin_panel(root, notebook):
    admin_frame = tk.Frame(notebook, width=800, height=600)
    admin_frame.pack_propagate(False)

    set_background(admin_frame, "BG.jpg")

    notebook.add(admin_frame, text="Admin Panel")

    # Doner Button
    doner_button = tk.Button(admin_frame, text="Doner", command=lambda: toggle_doner_options(doner_options_frame))
    doner_button.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    # Doner Options Frame
    doner_options_frame = tk.Frame(admin_frame)
    doner_options_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')
    doner_options_frame.grid_remove()  # Initially hidden

    tk.Button(doner_options_frame, text="Add Doner", command=lambda: add_doner(notebook)).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(doner_options_frame, text="Show Doners", command=show_doners).grid(row=0, column=1, padx=10, pady=5)

    # Donation Button
    donation_button = tk.Button(admin_frame, text="Donation", command=lambda: toggle_donation_options(donation_options_frame))
    donation_button.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    # Donation Options Frame
    donation_options_frame = tk.Frame(admin_frame)
    donation_options_frame.grid(row=4, column=0, padx=10, pady=5, sticky='w')
    donation_options_frame.grid_remove()  # Initially hidden

    tk.Button(donation_options_frame, text="Add Donation", command=lambda: add_donation(notebook)).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(donation_options_frame, text="Show Donations", command=show_donations).grid(row=0, column=1, padx=10, pady=5)

    # Other Options
    tk.Button(admin_frame, text="Show Blood Stock", command=show_blood_stock).grid(row=5, column=0, padx=10, pady=10, sticky='w')
    tk.Button(admin_frame, text="Show Requests", command=show_requests).grid(row=6, column=0, padx=10, pady=10, sticky='w')
    tk.Button(admin_frame, text="Log Out", command=lambda: logout(root, notebook)).grid(row=7, column=0, padx=10, pady=10, sticky='w')

def toggle_doner_options(frame):
    if frame.winfo_ismapped():
        frame.grid_remove()
    else:
        frame.grid()

def toggle_donation_options(frame):
    if frame.winfo_ismapped():
        frame.grid_remove()
    else:
        frame.grid()
def user_panel(root, notebook):
    user_frame = tk.Frame(notebook, width=800, height=600)
    user_frame.pack_propagate(False)

    set_background(user_frame, "BG.jpg")

    notebook.add(user_frame, text="User Panel")

    tk.Button(user_frame, text="Request Blood", command=lambda: request_blood(notebook)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Button(user_frame, text="Show Blood Stock", command=show_blood_stock).grid(row=1, column=0, padx=10, pady=10, sticky='w')
    tk.Button(user_frame, text="Show Status", command=show_status).grid(row=2, column=0, padx=10, pady=10, sticky='w')

    tk.Button(user_frame, text="Log Out", command=lambda: logout(root, notebook)).grid(row=3, column=0, padx=10, pady=10, sticky='w')

# Doner and Donation Management
def add_doner(notebook):
    doner_frame = tk.Frame(notebook, width=800, height=600)
    doner_frame.pack_propagate(False)

    # Set background image
    set_background(doner_frame, "BG.jpg")

    notebook.add(doner_frame, text="Add Doner")

    tk.Label(doner_frame, text="Name", bg="white").grid(row=0, column=0, padx=10, pady=10)
    name_entry = tk.Entry(doner_frame)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(doner_frame, text="Age", bg="white").grid(row=1, column=0, padx=10, pady=10)
    age_entry = tk.Entry(doner_frame)
    age_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(doner_frame, text="Blood Group", bg="white").grid(row=2, column=0, padx=10, pady=10)
    blood_group_combobox = ttk.Combobox(doner_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    blood_group_combobox.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(doner_frame, text="City", bg="white").grid(row=3, column=0, padx=10, pady=10)
    city_combobox = ttk.Combobox(doner_frame, values=get_districts())
    city_combobox.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(doner_frame, text="Number", bg="white").grid(row=4, column=0, padx=10, pady=10)
    number_entry = tk.Entry(doner_frame)
    number_entry.grid(row=4, column=1, padx=10, pady=10)

    tk.Button(doner_frame, text="Add Doner", command=lambda: add_doner_to_db(name_entry.get(), age_entry.get(), blood_group_combobox.get(), city_combobox.get(), number_entry.get())).grid(row=5, column=0, columnspan=2, pady=10)

def add_doner_to_db(name, age, bloodgroup, city, number):
    db = connect_to_database()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Doner (Name, Age, BloodGroup, City, Number) VALUES (%s, %s, %s, %s, %s)", (name, age, bloodgroup, city, number))
        db.commit()
        messagebox.showinfo("Success", "Doner added successfully")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    db.close()

def add_donation(notebook):
    donation_frame = tk.Frame(notebook, width=800, height=600)
    donation_frame.pack_propagate(False)  # Prevent frame from resizing to fit its children
    set_background(donation_frame, "BG.jpg")
    notebook.add(donation_frame, text="Add Donation")

    tk.Label(donation_frame, text="Doner ID").grid(row=0, column=0, padx=10, pady=10)
    doner_id_entry = tk.Entry(donation_frame)
    doner_id_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(donation_frame, text="Date").grid(row=1, column=0, padx=10, pady=10)
    date_entry = DateEntry(donation_frame)
    date_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(donation_frame, text="Unit").grid(row=2, column=0, padx=10, pady=10)
    unit_entry = tk.Entry(donation_frame)
    unit_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Button(donation_frame, text="Add Donation", command=lambda: add_donation_to_db(doner_id_entry.get(), date_entry.get_date(), unit_entry.get())).grid(row=3, column=0, columnspan=2, pady=10)

def add_donation_to_db(doner_id, date, unit):
    db = connect_to_database()
    cursor = db.cursor()
    try:
        # Convert the unit to an integer
        unit = int(unit)

        # Add the donation to the Donation table
        cursor.execute("INSERT INTO Donation (DonerID, Date, Unit) VALUES (%s, %s, %s)", (doner_id, date, unit))
        db.commit()

        # Get the blood group of the doner
        cursor.execute("SELECT BloodGroup FROM Doner WHERE Id = %s", (doner_id,))
        blood_group = cursor.fetchone()

        if blood_group:
            blood_group = blood_group[0]

            # Check if the blood group exists in the BloodStock table
            cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
            result = cursor.fetchone()

            if result:
                # Convert the existing unit to an integer
                existing_unit = int(result[0])
                # Update the unit if the blood group exists
                new_unit = existing_unit + unit
                cursor.execute("UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s", (new_unit, blood_group))
            else:
                # Insert a new record if the blood group does not exist
                cursor.execute("INSERT INTO BloodStock (BloodGroup, Unit) VALUES (%s, %s)", (blood_group, unit))

            db.commit()
            messagebox.showinfo("Success", "Donation added and BloodStock updated successfully")
        else:
            messagebox.showerror("Error", "Doner not found")

    except ValueError:
        messagebox.showerror("Error", "Unit must be an integer")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        db.close()

# Display and Query Functions
def show_doners():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Doner")
    rows = cursor.fetchall()
    db.close()

    display_table(rows, ["ID", "Name", "Age", "Blood Group", "City", "Number"], "Doner Details")

def show_status():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT Name, BloodGroup, Unit, Reason, City, Date, Status FROM request_blood")
    rows = cursor.fetchall()
    db.close()

    display_table(rows, ["Name", "Blood Group", "Unit", "Reason", "City", "Date", "Status"], "View Status")

def fetch_donations():
    global connection, cursor
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='bloodbank',
            user='root',
            password=''
        )
        cursor = connection.cursor()
        query = """SELECT Donation.Serial, Doner.Id AS DonerId, Doner.Name, Doner.BloodGroup, 
                   Donation.Unit, Donation.Date 
                   FROM Donation 
                   INNER JOIN Doner ON Donation.DonerId = Doner.Id"""
        cursor.execute(query)
        donations = cursor.fetchall()
        return donations
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_donations():
    donations = fetch_donations()

    app = tk.Tk()
    app.title("Blood Bank Management System")

    frame = tk.Frame(app)
    frame.pack(padx=10, pady=10)

    columns = ("Serial", "DonerId", "Name", "BloodGroup", "Unit", "Date")
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.heading("Serial", text="Serial")
    tree.heading("DonerId", text="DonerId")
    tree.heading("Name", text="Name")
    tree.heading("BloodGroup", text="BloodGroup")
    tree.heading("Unit", text="Unit")
    tree.heading("Date", text="Date")

    tree.pack()

    for donation in donations:
        tree.insert('', tk.END, values=donation)

    app.mainloop()

def show_blood_stock():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM BloodStock")
    rows = cursor.fetchall()
    db.close()
    display_table(rows, ["Blood Group", "Unit"], "Blood Stock")

def request_blood(notebook):
    request_frame = tk.Frame(notebook, width=800, height=600)
    request_frame.pack_propagate(False)
    notebook.add(request_frame, text="Request Blood")

    tk.Label(request_frame, text="Name").grid(row=0, column=0, padx=10, pady=10)
    name_entry = tk.Entry(request_frame)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="Blood Group").grid(row=1, column=0, padx=10, pady=10)
    blood_group_combobox = ttk.Combobox(request_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    blood_group_combobox.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="Unit").grid(row=2, column=0, padx=10, pady=10)
    unit_entry = tk.Entry(request_frame)
    unit_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="Reason").grid(row=3, column=0, padx=10, pady=10)
    reason_combobox = ttk.Combobox(request_frame, values=["Accident", "Surgery", "Pregnancy", "Chronic illness", "Others"])
    reason_combobox.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="City").grid(row=4, column=0, padx=10, pady=10)
    city_combobox = ttk.Combobox(request_frame, values=get_districts())
    city_combobox.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="Number").grid(row=5, column=0, padx=10, pady=10)
    number_entry = tk.Entry(request_frame)
    number_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(request_frame, text="Date").grid(row=6, column=0, padx=10, pady=10)
    date_entry = DateEntry(request_frame)
    date_entry.grid(row=6, column=1, padx=10, pady=10)

    tk.Button(request_frame, text="Submit Request", command=lambda: add_blood_request(
        name_entry.get(), blood_group_combobox.get(), int(unit_entry.get()), reason_combobox.get(),
        city_combobox.get(), number_entry.get(), date_entry.get_date())
              ).grid(row=7, column=0, columnspan=2, pady=10)

def add_blood_request(name, bloodgroup, unit, reason, city, number, date):
    db = connect_to_database()
    cursor = db.cursor()

    cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (bloodgroup,))
    result = cursor.fetchone()

    if result and result[0] >= unit:
        cursor.execute("""
            INSERT INTO request_blood (Name, BloodGroup, Unit, Reason, City, Number, Date, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Processing')
        """, (name, bloodgroup, unit, reason, city, number, date))
        db.commit()
        messagebox.showinfo("Success", "Blood request added. Status: Processing")
    else:
        cursor.execute("""
            SELECT Name, City, Number FROM Doner 
            WHERE BloodGroup = %s AND City = %s
        """, (bloodgroup, city))
        donors = cursor.fetchall()
        if donors:
            donor_info = "\n".join([f"{d[0]}, {d[1]}, {d[2]}" for d in donors])
            messagebox.showinfo("Nearest Donors", f"Donors available in your city:\n{donor_info}")
        else:
            messagebox.showinfo("No Donors", "No donors available in your city.")

        cursor.execute("""
            INSERT INTO request_blood (Name, BloodGroup, Unit, Reason, City, Number, Date, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Rejected')
        """, (name, bloodgroup, unit, reason, city, number, date))
        db.commit()
        messagebox.showinfo("Rejected", "Blood request rejected due to insufficient stock.")

    db.close()

def show_requests():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM request_blood")
    rows = cursor.fetchall()
    db.close()

    # Create a new window for showing the requests
    app = tk.Tk()
    app.title("Blood Requests")

    # Adjust the size of the window to a more manageable size
    app.geometry("800x500")  # Set the size to 600x400 (width x height)

    frame = tk.Frame(app)
    frame.pack(padx=10, pady=10, fill='both', expand=True)  # Use 'fill' and 'expand' for better layout

    # Columns for Treeview
    columns = ["Id", "Name", "Blood Group", "Unit", "Reason", "City", "Number", "Date", "Status"]

    # Create the Treeview with a fixed height so that it fits within the window
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)  # Set height to 8 rows visible

    # Set column headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=70, anchor="center")  # Set a reasonable width for each column

    # Pack the Treeview and enable scrolling
    tree.pack(pady=10, fill='both', expand=True)

    # Insert rows into the Treeview
    for row in rows:
        tree.insert('', tk.END, values=row)

    # Adding dropdown for Accept/Reject using pack instead of grid
    action_label = tk.Label(frame, text="Select Action")
    action_label.pack(padx=5, pady=5)

    action_combobox = ttk.Combobox(frame, values=["Accept", "Reject"])
    action_combobox.pack(padx=5, pady=5)

    # Submit button to handle request
    submit_button = tk.Button(frame, text="Submit", command=lambda: handle_request(tree, action_combobox.get()))
    submit_button.pack(padx=5, pady=10)

    app.mainloop()

def handle_request(tree, action):
    try:
        selected_item = tree.selection()[0]
        request_id = tree.item(selected_item)['values'][0]  # Get the request ID of the selected row

        if action not in ["Accept", "Reject"]:
            messagebox.showerror("Error", "Please select an action (Accept or Reject).")
            return

        db = connect_to_database()
        cursor = db.cursor()

        # Fetch request details
        cursor.execute("SELECT BloodGroup, Unit FROM request_blood WHERE Id = %s", (request_id,))
        request_details = cursor.fetchone()
        blood_group, requested_units = request_details

        if action == "Accept":
            # Fetch available units in blood stock
            cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
            stock_units = cursor.fetchone()[0]

            if stock_units >= requested_units:
                # Reduce units from stock
                new_stock_units = stock_units - requested_units
                cursor.execute("UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s", (new_stock_units, blood_group))

                # Update request status to "Accepted"
                cursor.execute("UPDATE request_blood SET Status = 'Accepted' WHERE Id = %s", (request_id,))
                db.commit()
                messagebox.showinfo("Success", "Request accepted and blood stock updated.")
            else:
                messagebox.showerror("Error", "Insufficient blood units in stock.")

        elif action == "Reject":
            # Update request status to "Rejected"
            cursor.execute("UPDATE request_blood SET Status = 'Rejected' WHERE Id = %s", (request_id,))
            db.commit()
            messagebox.showinfo("Request Rejected", "The request has been rejected.")

        db.close()
    except IndexError:
        messagebox.showerror("Error", "Please select a request to process.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def get_districts():
    return [
        "Bagerhat", "Bandarban", "Bhola", "Bogura", "Brahmanbaria",
        "Chapai Nawabganj", "Chandpur", "Chittagong", "Chuadanga", "Comilla",
        "Cox's Bazar", "Dhaka", "Dinajpur", "Faridpur", "Feni",
        "Gaibandha", "Gazipur", "Gopalganj", "Habiganj", "Jamalpur",
        "Jashore", "Jhalokati", "Jhenaidah", "Joypurhat", "Khagrachhari",
        "Khulna", "Kishoreganj", "Kurigram", "Kushtia", "Lakshmipur",
        "Lalmonirhat", "Madaripur", "Magura", "Manikganj", "Meherpur",
        "Moulvibazar", "Munshiganj", "Mymensingh", "Naogaon", "Narail",
        "Narayanganj", "Narsingdi", "Natore", "Netrokona", "Nilphamari",
        "Noakhali", "Pabna", "Panchagarh", "Patuakhali", "Pirojpur",
        "Rajbari", "Rajshahi", "Rangamati", "Rangpur", "Satkhira",
        "Shariatpur", "Sherpur", "Sirajganj", "Sunamganj", "Sylhet",
        "Tangail", "Thakurgaon"
    ]


def display_table(rows, columns, title):
    table_window = tk.Toplevel()
    table_window.title(title)

    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='w')

    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(expand=True, fill='both')

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    main_menu(root, notebook)  # Load the main menu with background

    root.mainloop()