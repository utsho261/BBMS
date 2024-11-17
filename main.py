import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from PIL import Image, ImageTk

class Database:
    @classmethod
    def connect_to_database(cls):
        return mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")

class Doner:
    def add_doner(self, notebook):
        doner_frame = tk.Frame(notebook, width=800, height=600)
        set_background(doner_frame, "BG.jpg")
        notebook.add(doner_frame, text="Add Doner")

        tk.Label(doner_frame, text="Name", bg="white").grid(row=0, column=0, padx=10, pady=10)
        name_entry = tk.Entry(doner_frame)
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(doner_frame, text="Age", bg="white").grid(row=1, column=0, padx=10, pady=10)
        age_entry = tk.Entry(doner_frame)
        age_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(doner_frame, text="Blood Group", bg="white").grid(row=2, column=0, padx=10, pady=10)
        blood_group_combobox = ttk.Combobox(doner_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly")
        blood_group_combobox.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(doner_frame, text="City", bg="white").grid(row=3, column=0, padx=10, pady=10)
        city_combobox = ttk.Combobox(doner_frame, values=get_districts(), state="readonly")
        city_combobox.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(doner_frame, text="Number", bg="white").grid(row=4, column=0, padx=10, pady=10)
        number_entry = tk.Entry(doner_frame)
        number_entry.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(doner_frame, text="Add Doner", command=lambda: self.validate_doner_data(name_entry.get(), age_entry.get(), blood_group_combobox.get(), city_combobox.get(), number_entry.get())).grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(doner_frame, text="Back", width=10, command=lambda: go_back(notebook)).grid(row=6, column=0, columnspan=2, pady=10)

    def validate_doner_data(self, name, age, bloodgroup, city, number):
        if not name or not age or not bloodgroup or not city or not number:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not self.validate_number(number):
            messagebox.showerror("Error", "Invalid number. Must start with 017, 013, 018, 015, 019, or 016 and be 11 digits long.")
            return

        self.add_doner_to_db(name, age, bloodgroup, city, number)

    def validate_number(self, number):
        valid_starts = ["017", "013", "018", "015", "019", "016"]
        return number.startswith(tuple(valid_starts)) and len(number) == 11

    def add_doner_to_db(self, name, age, bloodgroup, city, number):
        db = Database().connect_to_database()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO Doner (Name, Age, BloodGroup, City, Number) VALUES (%s, %s, %s, %s, %s)", (name, age, bloodgroup, city, number))
            db.commit()
            messagebox.showinfo("Success", "Doner added successfully")
            close_current_tab(notebook)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        db.close()

    def show_doners(self):
        show_doner_window = tk.Toplevel()
        show_doner_window.title("Doner Details")

        tk.Label(show_doner_window, text="Filter by Blood Group:").grid(row=0, column=0, padx=(10, 20), pady=(10, 20))
        blood_group_filter_combobox = ttk.Combobox(show_doner_window, values=["All", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly")
        blood_group_filter_combobox.set("All")
        blood_group_filter_combobox.grid(row=0, column=0, padx=(300, 20), pady=(10, 20))

        tk.Label(show_doner_window, text="Filter by City:").grid(row=0, column=1, padx=10, pady=10)
        city_filter_combobox = ttk.Combobox(show_doner_window, values=["All"] + get_districts(), state="readonly")
        city_filter_combobox.set("All")
        city_filter_combobox.grid(row=0, column=1, padx=(300, 20), pady=(10, 20))

        blood_group_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_doners(blood_group_filter_combobox.get(), city_filter_combobox.get(), show_doner_window))
        city_filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.filter_doners(blood_group_filter_combobox.get(), city_filter_combobox.get(), show_doner_window))

        self.doner_table = ttk.Treeview(show_doner_window, columns=("ID", "Name", "Age", "Blood Group", "City", "Number"), show="headings")
        self.doner_table.heading("ID", text="ID")
        self.doner_table.heading("Name", text="Name")
        self.doner_table.heading("Age", text="Age")
        self.doner_table.heading("Blood Group", text="Blood Group")
        self.doner_table.heading("City", text="City")
        self.doner_table.heading("Number", text="Number")
        self.doner_table.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.load_doners("All", "All", show_doner_window)
    def filter_doners(self, blood_group, city, window):
        self.load_doners(blood_group, city, window)
    def load_doners(self, blood_group, city, window):
        db = Database().connect_to_database()
        cursor = db.cursor()

        query = "SELECT * FROM Doner WHERE (%s = 'All' OR BloodGroup = %s) AND (%s = 'All' OR City = %s)"
        cursor.execute(query, (blood_group, blood_group, city, city))

        rows = cursor.fetchall()
        db.close()

        for row in self.doner_table.get_children():
            self.doner_table.delete(row)
        for row in rows:
            self.doner_table.insert("", "end", values=row)


class Donation:
    def add_donation(self, notebook):
        donation_frame = tk.Frame(notebook, width=800, height=600)
        set_background(donation_frame, "BG.jpg")
        notebook.add(donation_frame, text="Add Donation")

        tk.Label(donation_frame, text="Doner ID").grid(row=0, column=0, padx=10, pady=10)
        doner_id_entry = tk.Entry(donation_frame)
        doner_id_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(donation_frame, text="Date").grid(row=1, column=0, padx=10, pady=10)
        date_entry = DateEntry(donation_frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2)
        date_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(donation_frame, text="Unit").grid(row=2, column=0, padx=10, pady=10)
        unit_entry = tk.Entry(donation_frame)
        unit_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(donation_frame, text="Add Donation", command=lambda: self.add_donation_to_db(
            doner_id_entry.get(), date_entry.get(), unit_entry.get())
                  ).grid(row=3, column=1,  pady=10)
        tk.Button(donation_frame, text="Back", width=10, command=lambda: go_back(notebook)).grid(row=4, column=0, pady=10)

    def add_donation_to_db(self, doner_id, date, unit):
        db = Database.connect_to_database()
        cursor = db.cursor()

        try:
            unit = int(unit)

            cursor.execute(
                "INSERT INTO Donation (DonerID, Date, Unit) VALUES (%s, %s, %s)",
                (doner_id, date, unit)
            )
            cursor.execute("SELECT BloodGroup FROM Doner WHERE Id = %s", (doner_id,))
            blood_group = cursor.fetchone()

            if blood_group:
                blood_group = blood_group[0]

                cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
                result = cursor.fetchone()

                if result:
                    existing_unit = int(result[0])
                    new_unit = existing_unit + unit
                    cursor.execute("UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s", (new_unit, blood_group))
                else:
                    cursor.execute("INSERT INTO BloodStock (BloodGroup, Unit) VALUES (%s, %s)", (blood_group, unit))

            db.commit()
            messagebox.showinfo("Success", "Donation added successfully")
            close_current_tab(notebook)

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            db.close()



    def show_donations(self):
        db = Database.connect_to_database()
        cursor = db.cursor()

        try:
            query = """
            SELECT Donation.Serial, Doner.Id AS DonerId, Doner.Name, Doner.BloodGroup, 
                   Donation.Unit, Donation.Date 
            FROM Donation 
            INNER JOIN Doner ON Donation.DonerId = Doner.Id
            """
            cursor.execute(query)
            donations = cursor.fetchall()

            app = tk.Tk()
            app.title("Donation Details")
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

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching donations: {err}")
        finally:
            db.close()

class BloodStock:
    def show_blood_stock(self):
        db = Database.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM BloodStock")
        rows = cursor.fetchall()

        stock_window = tk.Toplevel()
        stock_window.title("Blood Stock Details")

        frame = tk.Frame(stock_window)
        frame.pack(padx=10, pady=10)

        columns = ("BloodGroup", "Unit")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("BloodGroup", text="Blood Group")
        tree.heading("Unit", text="Unit")
        tree.column("BloodGroup", width=150, anchor="center")
        tree.column("Unit", width=100, anchor="center")
        tree.pack()

        for row in rows:
            tree.insert("", tk.END, values=row)


    def show_requests(self):
        pass

class RequestBlood:
    def request_blood(self, notebook):
        pass

    def add_blood_request(self, name, bloodgroup, unit, reason, city, number, date):
        pass

    def show_status(self):
        pass

def set_background(frame, image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((800, 500), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(frame, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def go_back(notebook):
    current_tab_index = notebook.index(notebook.select())
    if current_tab_index > 0:
        notebook.forget(current_tab_index)
        previous_tab_index = current_tab_index - 1
        notebook.select(previous_tab_index)

def close_current_tab(notebook):
    current_tab_index = notebook.index(notebook.select())
    notebook.forget(current_tab_index)

class Authenticator:
    def authenticate_user(self, username, password):
        db = Database().connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT 'Admin' FROM Admin WHERE Username = %s AND Password = %s", (username, password))
        admin = cursor.fetchone()

        if admin:
            db.close()
            return 'Admin'

        cursor.execute("SELECT 'User' FROM User WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()

        db.close()
        return 'User' if user else None

def login(root, notebook, frame):
    username = username_entry.get()
    password = password_entry.get()
    role = Authenticator().authenticate_user(username, password)

    if role == 'Admin':
        admin_panel(root, notebook)
        frame.destroy()
    elif role == 'User':
        user_panel(root, notebook)
        frame.destroy()
    else:
        messagebox.showerror("Error", "Invalid username or password")

def logout(root, notebook):
    for widget in notebook.winfo_children():
        widget.destroy()
    main_menu(root, notebook)

def create_account(notebook):
    role_selection_frame = tk.Frame(notebook, width=800, height=600)
    set_background(role_selection_frame, "BG.jpg")

    notebook.add(role_selection_frame, text="Create Account")
    notebook.select(role_selection_frame)

    tk.Label(role_selection_frame, text="Select Account Type", font=("Arial", 14)).pack(pady=20)

    admin_button = tk.Button(role_selection_frame, text="Admin", width=20, command=lambda: switch_to_admin_form(role_selection_frame, notebook))
    admin_button.pack(pady=10)

    user_button = tk.Button(role_selection_frame, text="User", width=20, command=lambda: switch_to_user_form(role_selection_frame, notebook))
    user_button.pack(pady=10)

    tk.Button(role_selection_frame, text="Back", width=20, command=lambda: go_back(notebook)).pack(pady=10)

def switch_to_admin_form(frame, notebook):
    for widget in frame.winfo_children():
        widget.destroy()

    set_background(frame, "BG.jpg")

    tk.Label(frame, text="Admin Account Creation", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame, text="Username").pack(pady=10)
    username_entry = tk.Entry(frame)
    username_entry.pack(pady=10)

    tk.Label(frame, text="Password").pack(pady=10)
    password_entry = tk.Entry(frame, show='*')
    password_entry.pack(pady=10)

    tk.Button(frame, text="Create Admin Account", command=lambda: save_account(username_entry.get(), password_entry.get(), "Admin", notebook)).pack(pady=10)
    tk.Button(frame, text="Back", command=lambda: go_back(notebook)).pack(pady=10)


def switch_to_user_form(frame, notebook):
    for widget in frame.winfo_children():
        widget.destroy()

    set_background(frame, "BG.jpg")
    tk.Label(frame, text="User Account Creation", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame, text="Username").pack(pady=10)
    username_entry = tk.Entry(frame)
    username_entry.pack(pady=10)

    tk.Label(frame, text="Password").pack(pady=10)
    password_entry = tk.Entry(frame, show='*')
    password_entry.pack(pady=10)

    tk.Button(frame, text="Create User Account", command=lambda: save_account(username_entry.get(), password_entry.get(), "User", notebook)).pack(pady=10)

    tk.Button(frame, text="Back", command=lambda: go_back(notebook)).pack(pady=10)

def save_account(username, password, role, notebook):
    if username and password and role:
        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 4 characters long.")
            return

        db = Database.connect_to_database()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT Username FROM Admin WHERE Username = %s UNION SELECT Username FROM User WHERE Username = %s", (username, username))
            existing_user = cursor.fetchone()

            if existing_user:
                messagebox.showwarning("Warning", "Username already exists")
                return

            if role == "Admin":
                cursor.execute("INSERT INTO Admin (Username, Password) VALUES (%s, %s)", (username, password))
            elif role == "User":
                cursor.execute("INSERT INTO User (Username, Password) VALUES (%s, %s)", (username, password))

            db.commit()
            messagebox.showinfo("Success", "Account created successfully")
            close_current_tab(notebook)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        db.close()
    else:
        messagebox.showwarning("Warning", "Please fill all fields")

def validate_password(password):
    return len(password) >= 4

def admin_panel(root, notebook):
    admin_frame = tk.Frame(notebook, width=800, height=600)
    set_background(admin_frame, "BG.jpg")

    notebook.add(admin_frame, text="Admin Panel")

    doner_button = tk.Button(admin_frame, text="Doner", command=lambda: toggle_doner_options(doner_options_frame))
    doner_button.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    doner_options_frame = tk.Frame(admin_frame)
    doner_options_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')
    doner_options_frame.grid_remove()

    tk.Button(doner_options_frame, text="Add Doner", command=lambda: Doner().add_doner(notebook)).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(doner_options_frame, text="Show Doners", command=Doner().show_doners).grid(row=0, column=1, padx=10, pady=5)


    donation_button = tk.Button(admin_frame, text="Donation", command=lambda: toggle_donation_options(donation_options_frame))
    donation_button.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    donation_options_frame = tk.Frame(admin_frame)
    donation_options_frame.grid(row=4, column=0, padx=10, pady=5, sticky='w')
    donation_options_frame.grid_remove()

    tk.Button(donation_options_frame, text="Add Donation", command=lambda: Donation().add_donation(notebook)).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(donation_options_frame, text="Show Donations", command=Donation().show_donations).grid(row=0, column=1, padx=10, pady=5)

    tk.Button(admin_frame, text="Show Blood Stock", command=BloodStock().show_blood_stock).grid(row=5, column=0, padx=10, pady=10, sticky='w')
    tk.Button(admin_frame, text="Show Requests", command=BloodStock().show_requests).grid(row=6, column=0, padx=10, pady=10, sticky='w')
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
    set_background(user_frame, "BG.jpg")

    notebook.add(user_frame, text="User Panel")

    tk.Button(user_frame, text="Request Blood", command=lambda: RequestBlood().request_blood(notebook)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Button(user_frame, text="Show Blood Stock", command=BloodStock().show_blood_stock).grid(row=1, column=0, padx=10, pady=10, sticky='w')
    tk.Button(user_frame, text="Show Status", command=RequestBlood().show_status).grid(row=2, column=0, padx=10, pady=10, sticky='w')

    tk.Button(user_frame, text="Log Out", command=lambda: logout(root, notebook)).grid(row=3, column=0, padx=10, pady=10, sticky='w')

def main_menu(root, notebook):
    root.title("Blood Bank Management System")

    main_frame = tk.Frame(notebook, width=400, height=200)

    set_background(main_frame, "BG.jpg")

    notebook.add(main_frame, text="Login")

    title_label = tk.Label(main_frame, text="Welcome to Blood Bank Management System", bg="white", font=("Arial", 14))
    title_label.grid(row=0, column=1, columnspan=2, pady=(10, 20))

    tk.Label(main_frame, text="Username:", bg="white", font=("Arial", 12)).grid(row=1, column=1, padx=(40,20), pady=(10, 20), sticky="w")

    global username_entry, password_entry
    username_entry = tk.Entry(main_frame, font=("Arial", 12))
    username_entry.grid(row=1, column=1, padx=(110,20), pady=(10, 20))

    tk.Label(main_frame, text="Password:", bg="white", font=("Arial", 12)).grid(row=2, column=1,  padx=(40,20), pady=(10, 20), sticky="w")
    password_entry = tk.Entry(main_frame, show='*', font=("Arial", 12))
    password_entry.grid(row=2, column=1, padx=(110,20), pady=(10,20))

    tk.Button(main_frame, text="Sign Up", font=("Arial", 12), command=lambda: create_account(notebook)).grid(row=3, column=1, padx=(10,20), pady=(10, 20))
    tk.Button(main_frame, text="Log In", font=("Arial", 12), command=lambda: login(root, notebook, main_frame)).grid(row=3, column=1, padx=(190,20), pady=(10, 20))

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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    main_menu(root, notebook)

    root.mainloop()
