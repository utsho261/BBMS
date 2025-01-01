import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from PIL import Image, ImageTk
import re

class Database:
    @classmethod
    def connect_to_database(cls):
        return mysql.connector.connect(host="localhost", user="root", password="", database="bloodbank")

class Doner:
    def add_doner(self, notebook):
        doner_window = tk.Toplevel()
        doner_window.title("Add Donor")
        doner_window.geometry("400x400")

        header = tk.Label(doner_window, text="Add Donor", bg="#2c3e50", fg="white", font=("Arial", 18, "bold"), padx=20, pady=10)
        header.grid(row=0, column=0, columnspan=2, sticky="we")

        form_frame = tk.Frame(doner_window, bg="#f4f4f9")
        form_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

        tk.Label(form_frame, text="Name", bg="#f4f4f9", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_entry = tk.Entry(form_frame, font=("Arial", 12))
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Age", bg="#f4f4f9", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        age_entry = tk.Entry(form_frame, font=("Arial", 12))
        age_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Blood Group", bg="#f4f4f9", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        blood_group_combobox = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], state="readonly", font=("Arial", 12))
        blood_group_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="City", bg="#f4f4f9", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        city_combobox = ttk.Combobox(form_frame, values=get_districts(), state="readonly", font=("Arial", 12))
        city_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Contact Number", bg="#f4f4f9", font=("Arial", 12)).grid(row=4, column=0, padx=10,
                                                                                           pady=10, sticky="w")
        number_entry = tk.Entry(form_frame, font=("Arial", 12))
        number_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Buttons
        button_frame = tk.Frame(doner_window, bg="#f4f4f9")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        add_button = tk.Button(button_frame, text="Add Donor", command=lambda: self.validate_doner_data(
            name_entry.get(), age_entry.get(), blood_group_combobox.get(), city_combobox.get(), number_entry.get(),doner_window
        ), bg="#27ae60", fg="white", font=("Arial", 12), padx=20, pady=10)
        add_button.grid(row=0, column=1, padx=10)

        back_button = tk.Button(button_frame, text="Close", command=lambda: self.close_doner_window(doner_window),bg="#c0392b",fg="white", font=("Arial", 12), padx=20, pady=10)
        back_button.grid(row=0, column=0, padx=10)



    def close_doner_window(self, window):
        window.destroy()
    def validate_doner_data(self, name, age, bloodgroup, city, number,doner_window):
        if not name or not age or not bloodgroup or not city or not number:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not self.validate_number(number):
            messagebox.showerror("Error", "Please enter a valid Bangladeshi contact number.")
            return

        self.add_doner_to_db(name, age, bloodgroup, city, number)
        self.close_doner_window(doner_window)

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

        self.doner_table = ttk.Treeview(show_doner_window, columns=("ID", "Name", "Age", "Blood Group", "City",
                                                                    "Contact Number"), show="headings")
        self.doner_table.heading("ID", text="ID")
        self.doner_table.heading("Name", text="Name")
        self.doner_table.heading("Age", text="Age")
        self.doner_table.heading("Blood Group", text="Blood Group")
        self.doner_table.heading("City", text="City")
        self.doner_table.heading("Contact Number", text="Contact Number")
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
        donation_window = tk.Toplevel()
        donation_window.title("Add Donation")
        donation_window.geometry("400x400")

        header = tk.Label(donation_window, text="Add Donation", bg="#2c3e50", fg="white", font=("Arial", 18, "bold"), padx=20, pady=10)
        header.grid(row=0, column=0, columnspan=2, sticky="we")

        form_frame = tk.Frame(donation_window, bg="#f4f4f9")
        form_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

        tk.Label(form_frame, text="Donor ID", bg="#f4f4f9", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        doner_id_entry = tk.Entry(form_frame, font=("Arial", 12))
        doner_id_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Date", bg="#f4f4f9", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Unit", bg="#f4f4f9", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        unit_entry = tk.Entry(form_frame, font=("Arial", 12))
        unit_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        button_frame = tk.Frame(donation_window, bg="#f4f4f9")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        add_button = tk.Button(button_frame, text="Add Donation", command=lambda: self.add_donation_to_db(
            doner_id_entry.get(), date_entry.get(), unit_entry.get(), donation_window
        ), bg="#27ae60", fg="white", font=("Arial", 12), padx=20, pady=10)
        add_button.grid(row=0, column=1, padx=10)

        back_button = tk.Button(button_frame, text="Close", command=lambda: self.close_donation_window(donation_window), bg="#c0392b", fg="white", font=("Arial", 12), padx=20, pady=10)
        back_button.grid(row=0, column=0, padx=10)

    def close_donation_window(self, window):
        window.destroy()
    def add_donation_to_db(self, doner_id, date, unit, donation_window):
        db = Database.connect_to_database()
        cursor = db.cursor()

        try:
            # Convert unit to integer
            unit = int(unit)

            # Fetch donor details
            cursor.execute("SELECT Age, (SELECT MAX(Date) FROM Donation WHERE DonerID = %s) AS LastDonation FROM Doner WHERE Id = %s", (doner_id, doner_id))
            donor_data = cursor.fetchone()

            if not donor_data:
                messagebox.showerror("Error", "Donor ID not found.")
                return

            age, last_donation_date = donor_data

            # Validate age
            if age < 18:
                messagebox.showerror("Error", "Donor must be 18 years or older to donate.")
                return

            # Validate last donation date
            if last_donation_date:
                from datetime import datetime, timedelta

                last_donation_date = datetime.strptime(str(last_donation_date), "%m/%d/%y")
                next_eligible_date = last_donation_date + timedelta(days=90)
                current_date = datetime.strptime(date, "%m/%d/%y")

                if current_date < next_eligible_date:
                    messagebox.showerror(
                        "Error",
                        f"Donor can donate again after {next_eligible_date.strftime('%m/%d/%y')}."
                    )
                    return

            # Fetch donor's blood group
            cursor.execute("SELECT BloodGroup FROM Doner WHERE Id = %s", (doner_id,))
            blood_group = cursor.fetchone()

            if not blood_group:
                messagebox.showerror("Error", "Blood group not found for this donor.")
                return

            blood_group = blood_group[0]

            # Insert donation record
            cursor.execute(
                "INSERT INTO Donation (DonerID, Date, Unit) VALUES (%s, %s, %s)",
                (doner_id, date, unit)
            )

            # Update blood stock
            cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
            result = cursor.fetchone()

            if result:
                existing_unit = int(result[0])
                new_unit = existing_unit + unit
                cursor.execute("UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s", (new_unit, blood_group))
            else:
                cursor.execute("INSERT INTO BloodStock (BloodGroup, Unit) VALUES (%s, %s)", (blood_group, unit))

            db.commit()
            messagebox.showinfo("Success", "Donation added successfully.")
            self.close_donation_window(donation_window)

        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
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

    def update_blood_stock(self):
        def submit_update():
            blood_group = blood_group_var.get()
            unit_change = unit_var.get()
            operation = operation_var.get()  # Get the selected operation (Add or Minus)

            if blood_group and unit_change.isdigit():
                try:
                    cursor = db.cursor()
                    # Fetch the current stock
                    cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
                    current_stock = cursor.fetchone()

                    if current_stock is None:
                        tk.messagebox.showerror("Error", "Blood group not found!")
                        return

                    current_stock = current_stock[0]
                    if operation == "Add":
                        new_stock = current_stock + int(unit_change)
                    elif operation == "Minus":
                        new_stock = current_stock - int(unit_change)

                    # Check if new stock is non-negative
                    if new_stock < 0:
                        tk.messagebox.showerror("Error", "Resulting stock cannot be negative!")
                        return

                    # Update the stock
                    cursor.execute(
                        "UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s",
                        (new_stock, blood_group)
                    )
                    db.commit()
                    tk.messagebox.showinfo("Success", "Blood stock updated successfully!")
                    update_window.destroy()
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to update stock: {e}")
            else:
                tk.messagebox.showerror("Error", "Please enter a valid number for the unit!")

        db = Database.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT BloodGroup FROM BloodStock")
        blood_groups = [row[0] for row in cursor.fetchall()]

        update_window = tk.Toplevel()
        update_window.title("Update Blood Stock")

        tk.Label(update_window, text="Select Blood Group:").pack(pady=5)
        blood_group_var = tk.StringVar()
        blood_group_menu = ttk.Combobox(update_window, textvariable=blood_group_var, values=blood_groups, state="readonly")
        blood_group_menu.pack(pady=5)

        tk.Label(update_window, text="Operation:").pack(pady=5)
        operation_var = tk.StringVar(value="Add")  # Default operation is Add
        add_radio = ttk.Radiobutton(update_window, text="Add", variable=operation_var, value="Add")
        minus_radio = ttk.Radiobutton(update_window, text="Minus", variable=operation_var, value="Minus")
        add_radio.pack()
        minus_radio.pack()

        tk.Label(update_window, text="Enter Unit:").pack(pady=5)
        unit_var = tk.StringVar()
        unit_entry = ttk.Entry(update_window, textvariable=unit_var)
        unit_entry.pack(pady=5)

        submit_button = ttk.Button(update_window, text="Update", command=submit_update)
        submit_button.pack(pady=10)


    def close_show_window(self, window):
        window.destroy()
    def show_requests(self):
        db = Database.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM request_blood")
        rows = cursor.fetchall()
        db.close()

        show_requests_window = tk.Tk()
        show_requests_window.title("Blood Requests")

        show_requests_window.geometry("800x500")

        frame = tk.Frame(show_requests_window)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        columns = ["Id", "Name", "Blood Group", "Unit", "Reason", "City", "Contact Number", "Date", "Status"]

        tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=70, anchor="center")

        tree.pack(pady=10, fill='both', expand=True)

        for row in rows:
            tree.insert('', tk.END, values=row)

        action_label = tk.Label(frame, text="Select Action")
        action_label.pack(padx=5, pady=5)

        action_combobox = ttk.Combobox(frame, values=["Accept", "Reject"])
        action_combobox.pack(padx=5, pady=5)

        submit_button = tk.Button(frame, text="Submit", command=lambda: self.handle_request(show_requests_window,tree,action_combobox.get()))
        submit_button.pack(padx=5, pady=10)

    def handle_request(self,window,tree, action):
        try:
            selected_item = tree.selection()[0]
            request_id = tree.item(selected_item)['values'][0]

            if action not in ["Accept", "Reject"]:
                messagebox.showerror("Error", "Please select an action (Accept or Reject).")
                return

            db = Database.connect_to_database()
            cursor = db.cursor()

            cursor.execute("SELECT BloodGroup, Unit FROM request_blood WHERE Id = %s", (request_id,))
            request_details = cursor.fetchone()
            blood_group, requested_units = request_details

            if action == "Accept":
                cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (blood_group,))
                stock_units = cursor.fetchone()[0]

                if stock_units >= requested_units:
                    new_stock_units = stock_units - requested_units
                    cursor.execute("UPDATE BloodStock SET Unit = %s WHERE BloodGroup = %s", (new_stock_units, blood_group))

                    cursor.execute("UPDATE request_blood SET Status = 'Accepted' WHERE Id = %s", (request_id,))
                    db.commit()
                    messagebox.showinfo("Success", "Request accepted and blood stock updated.")
                    self.close_show_window(window)
                else:
                    messagebox.showerror("Error", "Insufficient blood units in stock.")

            elif action == "Reject":
                cursor.execute("UPDATE request_blood SET Status = 'Rejected' WHERE Id = %s", (request_id,))
                db.commit()
                messagebox.showinfo("Request Rejected", "The request has been rejected.")
                self.close_show_window(window)

            db.close()
        except IndexError:
            messagebox.showerror("Error", "Please select a request to process.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class RequestBlood:
    def request_blood(self, notebook):
        request_window = tk.Toplevel()
        request_window.title("Request Blood")
        request_window.geometry("400x500")

        header = tk.Label(request_window, text="Request Blood", bg="#2c3e50", fg="white", font=("Arial", 18, "bold"), padx=20, pady=10)
        header.grid(row=0, column=0, columnspan=2, sticky="we")

        form_frame = tk.Frame(request_window, bg="#f4f4f9")
        form_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

        tk.Label(form_frame, text="Name", bg="#f4f4f9", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_entry = tk.Entry(form_frame, font=("Arial", 12))
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Blood Group", bg="#f4f4f9", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        blood_group_combobox = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
                                            state="readonly", font=("Arial", 12))
        blood_group_combobox.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Unit", bg="#f4f4f9", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        unit_entry = tk.Entry(form_frame, font=("Arial", 12))
        unit_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Reason", bg="#f4f4f9", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        reason_combobox = ttk.Combobox(form_frame, values=["Accident", "Surgery", "Pregnancy", "Chronic illness", "Others"], font=("Arial", 12))
        reason_combobox.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="City", bg="#f4f4f9", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        city_combobox = ttk.Combobox(form_frame, values=get_districts(), state="readonly", font=("Arial", 12))
        city_combobox.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Contact Number", bg="#f4f4f9", font=("Arial", 12)).grid(row=5, column=0, padx=10,
                                                                                    pady=10, sticky="w")
        number_entry = tk.Entry(form_frame, font=("Arial", 12))
        number_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        tk.Label(form_frame, text="Date", bg="#f4f4f9", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="w")
        date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=6, column=1, padx=10, pady=10)

        button_frame = tk.Frame(request_window, bg="#f4f4f9")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        submit_button = tk.Button(button_frame, text="Submit Request", command=lambda: self.add_blood_request(
            name_entry.get(), blood_group_combobox.get(), unit_entry.get(), reason_combobox.get(),
            city_combobox.get(), number_entry.get(), date_entry.get_date(), request_window
        ), bg="#27ae60", fg="white", font=("Arial", 12), padx=20, pady=10)
        submit_button.grid(row=0, column=1, padx=10)

        close_button = tk.Button(button_frame, text="Close", command=lambda: self.close_request_window(request_window),
                                 bg="#c0392b", fg="white", font=("Arial", 12), padx=20, pady=10)
        close_button.grid(row=0, column=0, padx=10)

    def close_request_window(self, window):
        window.destroy()

    def add_blood_request(self, name, bloodgroup, unit, reason, city, number, date, request_window):
        try:
            unit = int(unit)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for Unit")
            return

        if not re.match(r"^(017|013|018|016|015|019)\d{8}$", number):
            messagebox.showerror("Invalid Input", "Please enter a valid Bangladeshi contact number")
            return

        db = Database.connect_to_database()
        cursor = db.cursor()

        cursor.execute("SELECT Unit FROM BloodStock WHERE BloodGroup = %s", (bloodgroup,))
        result = cursor.fetchone()

        if result and result[0] >= unit:
            cursor.execute("""INSERT INTO request_blood (Name, BloodGroup, Unit, Reason, City, Number, Date, Status) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, 'Processing')""",
                           (name, bloodgroup, unit, reason, city, number, date))
            db.commit()
            messagebox.showinfo("Success", "Blood request added. Status: Processing")
        else:
            # Find nearest donor
            cursor.execute("""SELECT Name, City, BloodGroup, Number FROM Doner WHERE BloodGroup = %s""",
                           (bloodgroup,))
            donor_data = cursor.fetchall()

            if donor_data:
                # Function to display one donor at a time
                def show_donor(index=0):
                    if index < len(donor_data):
                        donor = donor_data[index]
                        donor_info = f"Name: {donor[0]}\nCity: {donor[1]}\nBlood Group: {donor[2]}\nContact: {donor[3]}"
                        if messagebox.askyesno("Nearest Donor", f"{donor_info}\n\nShow next donor?"):
                            show_donor(index + 1)
                    else:
                        messagebox.showinfo("No More Donors", "You have viewed all available donors.")

                show_donor()
            else:
                if not result or result[0] == 0:
                    messagebox.showerror("Error", "Blood stock is empty and no nearest donor is available.")
                else:
                    messagebox.showinfo("Blood Not Available", "No nearest donor found.")

        request_window.destroy()




    def show_status(self):
        db = Database.connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT Name, BloodGroup, Unit, Reason, City, Date, Status FROM request_blood")
        rows = cursor.fetchall()
        status_window = tk.Toplevel()
        status_window.title("Show Status")

        frame = tk.Frame(status_window)
        frame.pack(padx=10, pady=10)

        columns = ("Name", "BloodGroup", "Unit", "Reason", "City", "Date", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        tree.heading("Name", text="Name")
        tree.heading("BloodGroup", text="Blood Group")
        tree.heading("Unit", text="Unit")
        tree.heading("Reason", text="Reason")
        tree.heading("City", text="City")
        tree.heading("Date", text="Date")
        tree.heading("Status", text="Status")

        tree.column("Name", width=150, anchor="center")
        tree.column("BloodGroup", width=150, anchor="center")
        tree.column("Unit", width=100, anchor="center")
        tree.column("Reason", width=100, anchor="center")
        tree.column("City", width=100, anchor="center")
        tree.column("Date", width=100, anchor="center")
        tree.column("Status", width=100, anchor="center")
        tree.pack()

        for row in rows:
            tree.insert("", tk.END, values=row)




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
        if not validate_username(username):
            messagebox.showerror("Error", "Username must be at least 4 characters long.")
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

def validate_username(username):
    pattern = r'^[a-z][a-z0-9]{3,}$'

    if re.match(pattern, username):
        return True

def admin_panel(root, notebook):
    admin_frame = tk.Frame(notebook, bg="#f0f2f5", width=800, height=600)
    set_background(admin_frame, "BG.jpg")
    notebook.add(admin_frame, text="Admin Panel")

    title_label = tk.Label(admin_frame, text="Admin Dashboard", font=("Helvetica", 24, "bold"), bg="#f0f2f5", fg="#333")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    doner_button = ttk.Button(admin_frame, text="Doner", command=lambda: toggle_doner_options(doner_options_frame))
    doner_button.grid(row=1, column=0, padx=20, pady=10, sticky='w')

    doner_options_frame = tk.Frame(admin_frame, bg="#ffffff", relief="groove", bd=2)
    doner_options_frame.grid(row=2, column=0, padx=20, pady=5, sticky='w')
    doner_options_frame.grid_remove()

    ttk.Button(doner_options_frame, text="Add Doner", command=lambda: Doner().add_doner(notebook)).grid(row=0, column=0, padx=20, pady=10)
    ttk.Button(doner_options_frame, text="Show Doners", command=Doner().show_doners).grid(row=0, column=1, padx=20, pady=10)

    donation_button = ttk.Button(admin_frame, text="Donation", command=lambda: toggle_donation_options(donation_options_frame))
    donation_button.grid(row=3, column=0, padx=20, pady=10, sticky='w')

    donation_options_frame = tk.Frame(admin_frame, bg="#ffffff", relief="groove", bd=2)
    donation_options_frame.grid(row=4, column=0, padx=20, pady=5, sticky='w')
    donation_options_frame.grid_remove()

    ttk.Button(donation_options_frame, text="Add Donation", command=lambda: Donation().add_donation(notebook)).grid(row=0, column=0, padx=20, pady=10)
    ttk.Button(donation_options_frame, text="Show Donations", command=Donation().show_donations).grid(row=0, column=1, padx=20, pady=10)

    ttk.Button(admin_frame, text="Show Blood Stock", command=BloodStock().show_blood_stock).grid(row=5, column=0, padx=20, pady=10, sticky='w')
    ttk.Button(admin_frame, text="Update Blood Stock", command=BloodStock().update_blood_stock).grid(row=6, column=0, padx=20, pady=10, sticky='w')
    ttk.Button(admin_frame, text="Show Requests", command=BloodStock().show_requests).grid(row=7, column=0, padx=20, pady=10, sticky='w')

    logout_button = ttk.Button(admin_frame, text="Log Out", command=lambda: logout(root, notebook))
    logout_button.grid(row=8, column=0, padx=20, pady=20, sticky='w')

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('TLabel', font=('Helvetica', 12))
    style.map('TButton', background=[('active', '#d9534f'), ('!active', '#007bff')], foreground=[('active', '#ffffff')])


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
    user_frame = tk.Frame(notebook, bg="#f0f2f5", width=800, height=600)
    set_background(user_frame, "BG.jpg")
    notebook.add(user_frame, text="User Panel")

    title_label = tk.Label(user_frame, text="User Dashboard", font=("Helvetica", 24, "bold"), bg="#f0f2f5", fg="#333")
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    request_blood_button = ttk.Button(user_frame, text="Request Blood",
                                      command=lambda: toggle_request_options(request_options_frame))
    request_blood_button.grid(row=1, column=0, padx=20, pady=10, sticky='w')

    request_options_frame = tk.Frame(user_frame, bg="#ffffff", relief="groove", bd=2)
    request_options_frame.grid(row=2, column=0, padx=20, pady=5, sticky='w')
    request_options_frame.grid_remove()

    ttk.Button(request_options_frame, text="Make a Request",
               command=lambda: RequestBlood().request_blood(notebook)).grid(row=0, column=0, padx=20, pady=10)
    ttk.Button(request_options_frame, text="View Request Status",
               command=RequestBlood().show_status).grid(row=0, column=1, padx=20, pady=10)

    ttk.Button(user_frame, text="View Blood Stock", command=BloodStock().show_blood_stock).grid(row=3, column=0, padx=20,
                                                                                                pady=10, sticky='w')
    logout_button = ttk.Button(user_frame, text="Log Out", command=lambda: logout(root, notebook))
    logout_button.grid(row=4, column=0, padx=20, pady=20, sticky='w')

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('TLabel', font=('Helvetica', 12))
    style.map('TButton', background=[('active', '#5bc0de'), ('!active', '#337ab7')], foreground=[('active', '#ffffff')])

def toggle_request_options(frame):
    if frame.winfo_viewable():
        frame.grid_remove()
    else:
        frame.grid()


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
        "Bagerhat", "Bandarban","Barisal", "Bhola", "Bogura", "Brahmanbaria",
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
    root.geometry("850x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    main_menu(root, notebook)

    root.mainloop()
