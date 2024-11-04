# Blood Bank Management System

## Overview

The Blood Bank Management System (BBMS) is a Python-based desktop application designed to manage and streamline blood donation and distribution processes. This system handles donor information, blood stock management, donation tracking, and patient blood requests, providing a user-friendly interface for efficient operation.

## Features

- **Donor Management**: Add and manage donor details, including name, age, blood group, city, and contact information.
- **Blood Stock Management**: View and update current blood stock by blood group and available quantity.
- **Donation Tracking**: Record and manage blood donations, including donor details, donation date, and quantity.
- **Patient Requests**: Handle patient blood requests, update the request status based on blood availability, and suggest nearest donors if stock is insufficient.
- **Request Approval/Rejection**: Admins can approve or reject patient requests, with stock automatically updated for approved requests.

## Technologies Used

- **Python**: Programming language used for the application.
- **Tkinter**: For creating the graphical user interface (GUI).
- **MySQL**: For database management, accessed via MySQL Connector.

## Setup and Installation

### Prerequisites

- Python 3.x (with Tkinter installed)
- MySQL (XAMPP or any MySQL server)
- MySQL Connector for Python (`pip install mysql-connector-python`)

### Database Setup

1. **Create a Database**: Create a database named `bloodbank` in MySQL.
2. **Create Tables**: Execute the following SQL scripts to create the necessary tables:

   ```sql
   CREATE TABLE Admin (
       Id INT AUTO_INCREMENT PRIMARY KEY,
       Username VARCHAR(100) NOT NULL UNIQUE,
       Password VARCHAR(255) NOT NULL
   );
   
   -- Create User table
   CREATE TABLE User (
       Id INT AUTO_INCREMENT PRIMARY KEY,
       Username VARCHAR(100) NOT NULL UNIQUE,
       Password VARCHAR(255) NOT NULL
   );

   -- Create Doner table
   CREATE TABLE Doner (
       Id INT AUTO_INCREMENT PRIMARY KEY,
       Name VARCHAR(100) NOT NULL,
       Age INT NOT NULL,
       BloodGroup VARCHAR(10) NOT NULL,
       City VARCHAR(100) NOT NULL,
       Number VARCHAR(15) NOT NULL
   );

   -- Create BloodStock table
   CREATE TABLE BloodStock (
       BloodGroup VARCHAR(10) PRIMARY KEY,
       Unit INT NOT NULL
   );

   -- Create Donation table
   CREATE TABLE Donation (
       Serial INT AUTO_INCREMENT PRIMARY KEY,
       DonerID INT NOT NULL,
       Date DATE NOT NULL,
       Unit INT NOT NULL,
       FOREIGN KEY (DonerID) REFERENCES Doner(Id) ON DELETE CASCADE
   );

   -- Create Request_Blood table
   CREATE TABLE Request_Blood (
       Id INT AUTO_INCREMENT PRIMARY KEY,
       Name VARCHAR(100) NOT NULL,
       BloodGroup VARCHAR(10) NOT NULL,
       Unit INT NOT NULL,
       Reason VARCHAR(255),
       City VARCHAR(100) NOT NULL,
       Number VARCHAR(15) NOT NULL,
       Date DATE NOT NULL,
       Status ENUM('Processing', 'Accepted', 'Rejected') NOT NULL DEFAULT 'Processing'
   );

   -- Insert initial blood stock values
   INSERT INTO BloodStock (BloodGroup, Unit) VALUES 
   ('A+', 0),
   ('A-', 0),
   ('B+', 0),
   ('B-', 0),
   ('AB+', 0),
   ('AB-', 0),
   ('O+', 0),
   ('O-', 0);
   ```

### Running the Project

1. **Clone the repository**: Clone this project to your local machine.
2. **Install Python dependencies**: Ensure you have the necessary Python packages installed:
   ```bash
   pip install mysql-connector-python
   ```
3. **Configure MySQL**: Ensure your MySQL server is running, and the `bloodbank` database is set up with the provided tables.
4. **Install tkcalendar**: Open your terminal and run the following command to install tkcalendar:
   ```bash
   pip install tkcalendar
   ```
5. **Install Pillow (for PIL, Image, and ImageTk)**: To handle image manipulation, install the Pillow library:
   ```bash
   pip install Pillow
   ```   
6. **Run the Application**: Execute the `main.py` file to launch the Blood Bank Management System interface.

   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Entry point of the application.

## Conclusion

The Blood Bank Management System simplifies blood management processes by efficiently managing blood stock, donor details, donations, and patient requests. With a user-friendly interface, it helps blood banks operate smoothly and handle critical needs more effectively.
