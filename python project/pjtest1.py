# ==========================================================
# EMPLOYEE WORK TIMER SYSTEM
# CONSOLE VERSION
#
# Features:
# - Employee Login
# - Admin Login
# - Late Detection
# - Work / Break / OT Time
# - Employee Database
# - CSV Save / Load
# - 12H / 24H Clock
#
# ADMIN LOGIN
# ID       : admin
# PASSWORD : 123
#
# No external library required
# ==========================================================

import csv
from datetime import datetime
from functools import reduce

# ==========================================================
# CONFIGURATION
# ==========================================================

ADMIN_ID = "admin"
ADMIN_PASSWORD = "123"
time_format_24 = True
employees = []

# Menu mapping for cleaner code
MENU_ACTIONS = {}

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def get_time():
    now = datetime.now()
    fmt = "%H:%M:%S" if time_format_24 else "%I:%M:%S %p"
    return now.strftime(fmt)

def notify(text):
    print("\a")
    print(f"[NOTIFICATION] {text}")

def find_employee(emp_id):
    return next((emp for emp in employees if emp["id"] == emp_id), None)

def input_time(prompt="Set Time (HH:MM): "):
    return input(prompt)

def time_to_minutes(time_str):
    """Convert HH:MM format to total minutes"""
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 0

def format_time_diff(minutes):
    """Format time difference as hours and minutes"""
    return f"{minutes // 60} hour(s) {minutes % 60} minute(s)"

def input_int(prompt, default=0):
    try:
        return int(input(prompt))
    except ValueError:
        return default

def calculate_late_deduction(late_minutes):
    if late_minutes <= 60:
        return 0
    late_hours = late_minutes // 60
    return 15000 * late_hours

def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================================
# EMPLOYEE LOGIN
# ==========================================================

def employee_login():
    print("\n========== EMPLOYEE LOGIN ==========")
    emp_id = input("ID: ")
    password = input("Password: ")
    
    employee = find_employee(emp_id)
    if not employee or employee["password"] != password:
        print("Wrong ID or Password")
        return

    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    work_minutes = time_to_minutes(employee.get("work_time", "08:00"))
    previous_total = int(employee.get("total_money", employee.get("income_per_month", 0)))

    if current_minutes <= work_minutes:
        late = 0
        print("\nLogin Successful\nYou are ON TIME")
    else:
        late = current_minutes - work_minutes
        print(f"\nLogin Successful\nYou are LATE\nLate: {format_time_diff(late)}")

    deduction = calculate_late_deduction(late)
    late_flag = 1 if late > 0 else 0
    new_total = previous_total - deduction

    print(f"Income per month: {employee.get('income_per_month', 0)}")
    print(f"Previous total money: {previous_total}")
    if deduction > 0:
        print(f"Late deduction: {deduction} money")
    else:
        print("Late deduction: 0 money")
    print(f"New total money: {new_total}")

    employee["login_time"] = get_current_datetime()
    employee["late_time"] = late_flag
    employee["total_money"] = new_total
    notify("Work Started")

# ==========================================================
# EMPLOYEE DATA MANAGEMENT
# ==========================================================

def show_all_employee_data():
    if not employees:
        print("No Employee Data")
        return
    print("\n========== EMPLOYEE DATA ==========")
    for emp in employees:
        print("--------------------------------")
        for key in ["name", "id", "password", "department", "work_time", "break_time", "ot_time", "income_per_month", "total_money", "late_time", "login_time"]:
            print(f"{key.replace('_', ' ').title():15}: {emp.get(key, '')}")

def add_employee_data():
    print("\n========== ADD EMPLOYEE ==========")
    income = input_int("Income per month: ")
    emp = {
        "name": input("Name: "),
        "id": input("Employee ID: "),
        "password": input("Password: "),
        "department": input("Department: "),
        "work_time": "08:00",
        "break_time": "12:00",
        "ot_time": "18:00",
        "income_per_month": income,
        "total_money": income,
        "late_time": 0,
        "login_time": ""
    }
    employees.append(emp)
    print("Employee Added")

def delete_employee_data():
    emp_id = input("Employee ID: ")
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    employees.remove(employee)
    print("Employee Deleted")

def update_employee_data():
    emp_id = input("Employee ID: ")
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    print("\n========== UPDATE EMPLOYEE ==========")
    employee["name"] = input("New Name: ")
    employee["password"] = input("New Password: ")
    employee["department"] = input("New Department: ")
    employee["income_per_month"] = input_int(
        "New Income per month: ", employee.get("income_per_month", 0)
    )
    if "total_money" not in employee:
        employee["total_money"] = employee["income_per_month"]
    print("Employee Updated")

def update_employee_time(field_name):
    """Generic function for updating work/break/OT times"""
    emp_id = input("Employee ID: ")
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    employee[field_name] = input(f"Set {field_name.replace('_', ' ').title()} (HH:MM): ")
    print(f"{field_name.replace('_', ' ').title()} Updated")

# ==========================================================
# CSV OPERATIONS
# ==========================================================

def save_employee_data():
    filename = input("Enter CSV filename: ")
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "ID", "Password", "Department", "Work Time", "Break Time", "OT Time", "Income Per Month", "Total Money", "Late Time", "Login Time"])
            for emp in employees:
                writer.writerow([emp.get(k, "") for k in ["name", "id", "password", "department", "work_time", "break_time", "ot_time", "income_per_month", "total_money", "late_time", "login_time"]])
        print("Employee Data Saved")
    except Exception as e:
        print(f"Error saving file: {e}")

def load_employee_data():
    global employees
    filename = input("Enter CSV filename: ")
    employees = []
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            keys = ["name", "id", "password", "department", "work_time", "break_time", "ot_time", "income_per_month", "total_money", "late_time", "login_time"]
            employees = []
            for row in reader:
                emp = dict(zip(keys, row))
                emp["income_per_month"] = int(emp.get("income_per_month", 0)) if emp.get("income_per_month", "") else 0
                emp["total_money"] = int(emp.get("total_money", emp["income_per_month"])) if emp.get("total_money", "") else emp["income_per_month"]
                emp["late_time"] = int(emp.get("late_time", 0)) if emp.get("late_time", "") else 0
                employees.append(emp)
        print("Employee Data Loaded")
    except FileNotFoundError:
        print("File Not Found")

# ==========================================================
# MENU SYSTEM
# ==========================================================

def show_menu(title, options):
    """Generic menu display function"""
    print(f"\n========== {title} ==========")
    for key, text in options.items():
        print(f"{key}. {text}")
    return input("Select: ")

def handle_menu(title, options, actions):
    """Generic menu handler"""
    while True:
        choice = show_menu(title, options)
        if choice in actions:
            if choice == list(options.keys())[-1]:  # Back option
                break
            actions[choice]()
        else:
            print("Invalid Selection")

def timer_settings():
    options = {"1": "Use 12 Hour Format", "2": "Use 24 Hour Format", "3": "Back"}
    actions = {
        "1": lambda: globals().__setitem__('time_format_24', False) or print("12 Hour Format Enabled"),
        "2": lambda: globals().__setitem__('time_format_24', True) or print("24 Hour Format Enabled"),
        "3": lambda: None
    }
    while True:
        choice = show_menu("TIMER SETTINGS", options)
        if choice == "1":
            globals()['time_format_24'] = False
            print("12 Hour Format Enabled")
        elif choice == "2":
            globals()['time_format_24'] = True
            print("24 Hour Format Enabled")
        elif choice == "3":
            break

def database_settings():
    options = {"1": "Employee Work Time Data Set", "2": "Employee Break Time Data Set", "3": "Employee OT Time Data Set", "4": "Back"}
    actions = {
        "1": lambda: update_employee_time("work_time"),
        "2": lambda: update_employee_time("break_time"),
        "3": lambda: update_employee_time("ot_time"),
        "4": lambda: None
    }
    while True:
        choice = show_menu("DATABASE SETTINGS", options)
        if choice in actions and choice != "4":
            actions[choice]()
        elif choice == "4":
            break

def database_functions():
    options = {"1": "Show All Employee Data", "2": "Add New Employee Data", "3": "Delete Employee Data", "4": "Update Employee Data", "5": "Save Employee Data", "6": "Load Employee Data", "7": "Back"}
    actions = {
        "1": show_all_employee_data,
        "2": add_employee_data,
        "3": delete_employee_data,
        "4": update_employee_data,
        "5": save_employee_data,
        "6": load_employee_data,
        "7": lambda: None
    }
    while True:
        choice = show_menu("DATABASE FUNCTIONS", options)
        if choice in actions and choice != "7":
            actions[choice]()
        elif choice == "7":
            break

def admin_menu():
    options = {"1": "Timer Settings", "2": "Database Settings", "3": "Database Functions", "4": "Back"}
    actions = {
        "1": timer_settings,
        "2": database_settings,
        "3": database_functions,
        "4": lambda: None
    }
    while True:
        choice = show_menu("ADMIN MENU", options)
        if choice in actions and choice != "4":
            actions[choice]()
        elif choice == "4":
            break

# ==========================================================
# ADMIN & MAIN LOGIN
# ==========================================================

def admin_login():
    print("\n========== ADMIN LOGIN ==========")
    if input("ID: ") == ADMIN_ID and input("Password: ") == ADMIN_PASSWORD:
        print("Admin Login Successful")
        admin_menu()
    else:
        print("Wrong Admin ID or Password")

def main():
    while True:
        print("\n================================")
        print(" EMPLOYEE LOGIN SYSTEM ")
        print("================================")
        options = {"1": "Employee Login", "2": "Admin Login", "3": "Exit"}
        for k, v in options.items():
            print(f"{k}. {v}")
        
        choice = input("Select: ")
        if choice == "1":
            employee_login()
        elif choice == "2":
            admin_login()
        elif choice == "3":
            print("Program Closed")
            break
        else:
            print("Invalid Selection")

# ==========================================================
# START PROGRAM
# ==========================================================

if __name__ == "__main__":
    main()