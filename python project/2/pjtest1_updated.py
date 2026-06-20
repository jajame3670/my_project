# ==========================================================
# EMPLOYEE WORK TIMER SYSTEM
# CONSOLE VERSION - UPGRADED
#
# Added:
# - Login / Logout session flow
# - Attendance history
# - Real OT pay calculation
# - Break start / end
# - Leave, role, shift, holiday systems
# - Password hashing with hashlib
# - Auto save after every data change
# - Search, sort, statistics, monthly report, export
# - Time validation and error logging
# ==========================================================

import csv
import hashlib
import json
import os
import traceback
from datetime import date, datetime

# ==========================================================
# CONFIGURATION
# ==========================================================

ADMIN_ID = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("123".encode()).hexdigest()

EMPLOYEE_FILE = "employees.csv"
HISTORY_FILE = "attendance_history.csv"
ERROR_LOG_FILE = "error.log"

STANDARD_BREAK_MINUTES = 60
BREAK_DEDUCTION_PER_HOUR = 15000
LATE_DEDUCTION_PER_HOUR = 15000
DEFAULT_OT_PAY_PER_HOUR = 20000

time_format_24 = True
employees = []
attendance_history = []
current_user = None

SHIFTS = {
    "Morning": {"work_time": "08:00", "break_time": "12:00", "ot_time": "17:00"},
    "Night": {"work_time": "20:00", "break_time": "00:00", "ot_time": "05:00"},
}

HOLIDAYS = {
    "2026-01-01",
    "2026-04-13",
    "2026-04-14",
    "2026-04-15",
    "2026-05-01",
    "2026-12-31",
}

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def log_error(error):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        file.write(str(error) + "\n")
        file.write(traceback.format_exc() + "\n")


def notify(text):
    print("\a")
    print(f"[NOTIFICATION] {text}")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def verify_password(input_password, stored_password):
    if is_hash(stored_password):
        return hash_password(input_password) == stored_password
    return input_password == stored_password


def get_time():
    now = datetime.now()
    fmt = "%H:%M:%S" if time_format_24 else "%I:%M:%S %p"
    return now.strftime(fmt)


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return date.today().strftime("%Y-%m-%d")


def validate_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def input_time(prompt="Set Time (HH:MM): ", default=None):
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        if validate_time(value):
            return value
        print("Invalid time. Please use HH:MM, for example 08:30")


def time_to_minutes(time_str):
    if not validate_time(time_str):
        return 0
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def datetime_to_minutes(dt):
    return dt.hour * 60 + dt.minute


def minutes_between(start_minutes, end_minutes):
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    return end_minutes - start_minutes


def format_time_diff(minutes):
    return f"{minutes // 60} hour(s) {minutes % 60} minute(s)"


def input_int(prompt, default=0):
    value = input(prompt).strip()
    if value == "":
        return default
    try:
        return int(value)
    except ValueError:
        print(f"Invalid number. Using {default}")
        return default


def calculate_hour_money(minutes, rate):
    if minutes <= 0:
        return 0
    hours = minutes / 60
    return int(hours * rate)


def calculate_late_deduction(late_minutes):
    if late_minutes <= 60:
        return 0
    late_hours = late_minutes // 60
    return LATE_DEDUCTION_PER_HOUR * late_hours


def calculate_break_deduction(over_minutes):
    return calculate_hour_money(over_minutes, BREAK_DEDUCTION_PER_HOUR)


def find_employee(emp_id):
    return next((emp for emp in employees if emp.get("id") == emp_id), None)


def ensure_employee_defaults(employee):
    income = int(employee.get("income_per_month", 0) or 0)
    employee.setdefault("name", "")
    employee.setdefault("id", "")
    employee.setdefault("password", "")
    employee.setdefault("department", "")
    employee.setdefault("role", "Staff")
    employee.setdefault("shift", "Morning")
    employee.setdefault("work_time", SHIFTS["Morning"]["work_time"])
    employee.setdefault("break_time", SHIFTS["Morning"]["break_time"])
    employee.setdefault("ot_time", SHIFTS["Morning"]["ot_time"])
    employee.setdefault("income_per_month", income)
    employee.setdefault("total_money", income)
    employee.setdefault("late_time", 0)
    employee.setdefault("login_time", "")
    employee.setdefault("logout_time", "")
    employee.setdefault("leave_days", 5)
    employee.setdefault("ot_pay_per_hour", DEFAULT_OT_PAY_PER_HOUR)
    employee.setdefault("manager_id", "")
    return employee


def visible_employee(employee):
    safe = dict(employee)
    safe["password"] = "(encrypted)"
    return safe


def get_open_attendance(emp_id):
    for item in reversed(attendance_history):
        if item.get("id") == emp_id and item.get("logout", "") == "":
            return item
    return None


def is_holiday(day_text):
    return day_text in HOLIDAYS


def update_employee_month_total(employee, year_month=None):
    if year_month is None:
        year_month = today_text()[:7]

    income = int(employee.get("income_per_month", 0) or 0)
    total_ot_pay = 0
    total_deduction = 0

    for item in attendance_history:
        if item.get("id") == employee.get("id") and item.get("date", "").startswith(year_month):
            total_ot_pay += int(item.get("ot_pay", 0) or 0)
            total_deduction += int(item.get("deduction", 0) or 0)

    employee["total_money"] = income + total_ot_pay - total_deduction


def auto_save():
    save_employee_data(EMPLOYEE_FILE, ask_filename=False)
    save_attendance_history(HISTORY_FILE, ask_filename=False)

# ==========================================================
# CSV OPERATIONS
# ==========================================================

EMPLOYEE_KEYS = [
    "name", "id", "password", "department", "role", "shift", "work_time",
    "break_time", "ot_time", "income_per_month", "total_money", "late_time",
    "login_time", "logout_time", "leave_days", "ot_pay_per_hour", "manager_id"
]

HISTORY_KEYS = [
    "id", "date", "login", "logout", "late", "worked_minutes", "ot_minutes",
    "ot_pay", "deduction", "break_minutes", "break_over_minutes", "early_leave",
    "holiday", "break_start"
]


def save_employee_data(filename=None, ask_filename=True):
    if ask_filename:
        filename = input("Enter CSV filename: ").strip() or EMPLOYEE_FILE
    filename = filename or EMPLOYEE_FILE
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=EMPLOYEE_KEYS)
            writer.writeheader()
            for emp in employees:
                ensure_employee_defaults(emp)
                writer.writerow({key: emp.get(key, "") for key in EMPLOYEE_KEYS})
        if ask_filename:
            print("Employee Data Saved")
    except Exception as error:
        log_error(error)
        print(f"Error saving employee file: {error}")


def load_employee_data(filename=None, ask_filename=True):
    global employees
    if ask_filename:
        filename = input("Enter CSV filename: ").strip() or EMPLOYEE_FILE
    filename = filename or EMPLOYEE_FILE
    if not os.path.exists(filename):
        if ask_filename:
            print("File Not Found")
        return

    try:
        employees = []
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                emp = ensure_employee_defaults(row)
                for key in ["income_per_month", "total_money", "late_time", "leave_days", "ot_pay_per_hour"]:
                    emp[key] = int(emp.get(key, 0) or 0)
                employees.append(emp)
        if ask_filename:
            print("Employee Data Loaded")
    except Exception as error:
        log_error(error)
        print(f"Error loading employee file: {error}")


def save_attendance_history(filename=None, ask_filename=True):
    if ask_filename:
        filename = input("Enter history CSV filename: ").strip() or HISTORY_FILE
    filename = filename or HISTORY_FILE
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=HISTORY_KEYS)
            writer.writeheader()
            for item in attendance_history:
                writer.writerow({key: item.get(key, "") for key in HISTORY_KEYS})
        if ask_filename:
            print("Attendance History Saved")
    except Exception as error:
        log_error(error)
        print(f"Error saving history file: {error}")


def load_attendance_history(filename=None, ask_filename=True):
    global attendance_history
    if ask_filename:
        filename = input("Enter history CSV filename: ").strip() or HISTORY_FILE
    filename = filename or HISTORY_FILE
    if not os.path.exists(filename):
        if ask_filename:
            print("File Not Found")
        return

    try:
        attendance_history = []
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                for key in ["late", "worked_minutes", "ot_minutes", "ot_pay", "deduction", "break_minutes", "break_over_minutes", "early_leave"]:
                    row[key] = int(row.get(key, 0) or 0)
                attendance_history.append(row)
        if ask_filename:
            print("Attendance History Loaded")
    except Exception as error:
        log_error(error)
        print(f"Error loading history file: {error}")

# ==========================================================
# EMPLOYEE SYSTEM
# ==========================================================

def employee_login():
    global current_user
    print("\n========== EMPLOYEE LOGIN ==========")
    emp_id = input("ID: ").strip()
    password = input("Password: ")

    employee = find_employee(emp_id)
    if not employee or not verify_password(password, employee.get("password", "")):
        print("Wrong ID or Password")
        return

    if not is_hash(employee.get("password", "")):
        employee["password"] = hash_password(password)
        print("Password upgraded to encrypted format.")

    if get_open_attendance(emp_id):
        print("You already logged in and have not logged out yet.")
        current_user = emp_id
        return

    now = datetime.now()
    current_minutes = datetime_to_minutes(now)
    work_minutes = time_to_minutes(employee.get("work_time", "08:00"))
    day_text = today_text()

    if is_holiday(day_text):
        late = 0
        print("\nLogin Successful\nToday is a holiday. Late check skipped.")
    elif current_minutes <= work_minutes:
        late = 0
        print("\nLogin Successful\nYou are ON TIME")
    else:
        late = current_minutes - work_minutes
        print(f"\nLogin Successful\nYou are LATE\nLate: {format_time_diff(late)}")

    attendance_history.append({
        "id": emp_id,
        "date": day_text,
        "login": now.strftime("%H:%M"),
        "logout": "",
        "late": late,
        "worked_minutes": 0,
        "ot_minutes": 0,
        "ot_pay": 0,
        "deduction": calculate_late_deduction(late),
        "break_minutes": 0,
        "break_over_minutes": 0,
        "early_leave": 0,
        "holiday": "yes" if is_holiday(day_text) else "no",
        "break_start": "",
    })

    employee["login_time"] = get_current_datetime()
    employee["logout_time"] = ""
    employee["late_time"] = int(employee.get("late_time", 0) or 0) + (1 if late > 0 else 0)
    current_user = emp_id
    auto_save()
    notify("Work Started")


def employee_logout():
    global current_user
    print("\n========== EMPLOYEE LOGOUT ==========")
    emp_id = current_user or input("Employee ID: ").strip()
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return

    record = get_open_attendance(emp_id)
    if not record:
        print("No active login found.")
        return

    if record.get("break_start"):
        print("Please end break before logout.")
        return

    now = datetime.now()
    logout_minutes = datetime_to_minutes(now)
    login_minutes = time_to_minutes(record.get("login", "00:00"))
    ot_minutes_base = time_to_minutes(employee.get("ot_time", "17:00"))

    worked_minutes = max(0, minutes_between(login_minutes, logout_minutes) - int(record.get("break_minutes", 0) or 0))
    ot_minutes = max(0, minutes_between(ot_minutes_base, logout_minutes))
    early_leave = 0 if logout_minutes >= ot_minutes_base else ot_minutes_base - logout_minutes

    ot_rate = int(employee.get("ot_pay_per_hour", DEFAULT_OT_PAY_PER_HOUR) or 0)
    if record.get("holiday") == "yes":
        ot_rate *= 2
    ot_pay = calculate_hour_money(ot_minutes, ot_rate)

    total_deduction = int(record.get("deduction", 0) or 0) + calculate_break_deduction(int(record.get("break_over_minutes", 0) or 0))

    record["logout"] = now.strftime("%H:%M")
    record["worked_minutes"] = worked_minutes
    record["ot_minutes"] = ot_minutes
    record["ot_pay"] = ot_pay
    record["deduction"] = total_deduction
    record["early_leave"] = early_leave

    employee["logout_time"] = get_current_datetime()
    update_employee_month_total(employee)
    current_user = None
    auto_save()

    print(f"Worked: {format_time_diff(worked_minutes)}")
    print(f"OT: {format_time_diff(ot_minutes)}")
    print(f"Extra Pay: {ot_pay}")
    print(f"Deduction: {total_deduction}")
    if early_leave:
        print(f"Early leave: {format_time_diff(early_leave)}")
    notify("Work Ended")


def start_break():
    emp_id = current_user or input("Employee ID: ").strip()
    record = get_open_attendance(emp_id)
    if not record:
        print("Please login before starting break.")
        return
    if record.get("break_start"):
        print("Break already started.")
        return
    record["break_start"] = datetime.now().strftime("%H:%M")
    auto_save()
    print("Break started.")


def end_break():
    emp_id = current_user or input("Employee ID: ").strip()
    record = get_open_attendance(emp_id)
    if not record or not record.get("break_start"):
        print("No active break found.")
        return

    start_minutes = time_to_minutes(record["break_start"])
    end_minutes = datetime_to_minutes(datetime.now())
    break_minutes = minutes_between(start_minutes, end_minutes)
    total_break = int(record.get("break_minutes", 0) or 0) + break_minutes
    over_minutes = max(0, total_break - STANDARD_BREAK_MINUTES)

    record["break_minutes"] = total_break
    record["break_over_minutes"] = over_minutes
    record["break_start"] = ""
    auto_save()
    print(f"Break ended. Total break: {format_time_diff(total_break)}")
    if over_minutes:
        print(f"Break over limit: {format_time_diff(over_minutes)}")


def apply_leave():
    print("\n========== LEAVE SYSTEM ==========")
    emp_id = input("Employee ID: ").strip()
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return

    print("1. Sick Leave")
    print("2. Vacation Leave")
    print("3. Emergency Leave")
    leave_choice = input("Select leave type: ")
    leave_types = {"1": "Sick Leave", "2": "Vacation Leave", "3": "Emergency Leave"}
    leave_type = leave_types.get(leave_choice)
    if not leave_type:
        print("Invalid leave type")
        return

    days = input_int("Leave days: ", 1)
    remain = int(employee.get("leave_days", 0) or 0)
    if days <= 0:
        print("Leave days must be more than 0")
        return
    if days > remain:
        print(f"Not enough leave days. Remaining: {remain}")
        return

    employee["leave_days"] = remain - days
    auto_save()
    print(f"{leave_type} approved. Remaining leave days: {employee['leave_days']}")

# ==========================================================
# EMPLOYEE DATA MANAGEMENT
# ==========================================================

def show_all_employee_data(data=None):
    data = data if data is not None else employees
    if not data:
        print("No Employee Data")
        return
    print("\n========== EMPLOYEE DATA ==========")
    keys = [
        "name", "id", "password", "department", "role", "shift", "work_time",
        "break_time", "ot_time", "income_per_month", "total_money",
        "late_time", "login_time", "logout_time", "leave_days", "ot_pay_per_hour",
        "manager_id"
    ]
    for emp in data:
        print("--------------------------------")
        safe = visible_employee(emp)
        for key in keys:
            print(f"{key.replace('_', ' ').title():18}: {safe.get(key, '')}")


def add_employee_data():
    print("\n========== ADD EMPLOYEE ==========")
    emp_id = input("Employee ID: ").strip()
    if find_employee(emp_id):
        print("Employee ID already exists.")
        return

    shift = input("Shift (Morning/Night): ").strip().title() or "Morning"
    if shift not in SHIFTS:
        shift = "Morning"

    income = input_int("Income per month: ")
    role = input("Role (Staff/Manager/HR): ").strip().title() or "Staff"
    password = input("Password: ")
    emp = {
        "name": input("Name: "),
        "id": emp_id,
        "password": hash_password(password),
        "department": input("Department: "),
        "role": role,
        "shift": shift,
        "work_time": SHIFTS[shift]["work_time"],
        "break_time": SHIFTS[shift]["break_time"],
        "ot_time": SHIFTS[shift]["ot_time"],
        "income_per_month": income,
        "total_money": income,
        "late_time": 0,
        "login_time": "",
        "logout_time": "",
        "leave_days": input_int("Leave days: ", 5),
        "ot_pay_per_hour": input_int("OT pay per hour: ", DEFAULT_OT_PAY_PER_HOUR),
        "manager_id": input("Manager ID (optional): "),
    }
    employees.append(ensure_employee_defaults(emp))
    auto_save()
    print("Employee Added")


def delete_employee_data():
    emp_id = input("Employee ID: ").strip()
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    employees.remove(employee)
    auto_save()
    print("Employee Deleted")


def update_employee_data():
    emp_id = input("Employee ID: ").strip()
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return

    print("\n========== UPDATE EMPLOYEE ==========")
    employee["name"] = input("New Name: ") or employee.get("name", "")
    new_password = input("New Password (blank = keep old): ")
    if new_password:
        employee["password"] = hash_password(new_password)
    employee["department"] = input("New Department: ") or employee.get("department", "")
    employee["role"] = input("New Role (Staff/Manager/HR): ") or employee.get("role", "Staff")
    employee["shift"] = input("New Shift (Morning/Night): ") or employee.get("shift", "Morning")
    employee["income_per_month"] = input_int("New Income per month: ", int(employee.get("income_per_month", 0) or 0))
    employee["leave_days"] = input_int("New Leave days: ", int(employee.get("leave_days", 5) or 5))
    employee["ot_pay_per_hour"] = input_int("New OT pay per hour: ", int(employee.get("ot_pay_per_hour", DEFAULT_OT_PAY_PER_HOUR) or 0))
    employee["manager_id"] = input("New Manager ID: ") or employee.get("manager_id", "")
    update_employee_month_total(employee)
    auto_save()
    print("Employee Updated")


def update_employee_time(field_name):
    emp_id = input("Employee ID: ").strip()
    employee = find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    employee[field_name] = input_time(f"Set {field_name.replace('_', ' ').title()} (HH:MM): ", employee.get(field_name, "08:00"))
    auto_save()
    print(f"{field_name.replace('_', ' ').title()} Updated")


def search_employee():
    print("\n========== SEARCH EMPLOYEE ==========")
    print("1. Search by ID")
    print("2. Search by Name")
    print("3. Search by Department")
    choice = input("Select: ")
    keyword = input("Keyword: ").strip().lower()

    if choice == "1":
        result = [emp for emp in employees if keyword in emp.get("id", "").lower()]
    elif choice == "2":
        result = [emp for emp in employees if keyword in emp.get("name", "").lower()]
    elif choice == "3":
        result = [emp for emp in employees if keyword in emp.get("department", "").lower()]
    else:
        print("Invalid Selection")
        return
    show_all_employee_data(result)


def sort_employee():
    print("\n========== SORT EMPLOYEE ==========")
    print("1. Sort by Late")
    print("2. Sort by Salary")
    print("3. Sort by Department")
    choice = input("Select: ")
    if choice == "1":
        data = sorted(employees, key=lambda emp: int(emp.get("late_time", 0) or 0), reverse=True)
    elif choice == "2":
        data = sorted(employees, key=lambda emp: int(emp.get("total_money", 0) or 0), reverse=True)
    elif choice == "3":
        data = sorted(employees, key=lambda emp: emp.get("department", ""))
    else:
        print("Invalid Selection")
        return
    show_all_employee_data(data)

# ==========================================================
# REPORTS
# ==========================================================

def show_attendance_history():
    if not attendance_history:
        print("No Attendance History")
        return

    print("\n========== ATTENDANCE HISTORY ==========")
    emp_id = input("Employee ID (blank = all): ").strip()
    for item in attendance_history:
        if emp_id and item.get("id") != emp_id:
            continue
        print("--------------------------------")
        print(f"ID              : {item.get('id', '')}")
        print(f"Date            : {item.get('date', '')}")
        print(f"Login           : {item.get('login', '')}")
        print(f"Logout          : {item.get('logout', '')}")
        print(f"Late            : {format_time_diff(int(item.get('late', 0) or 0))}")
        print(f"Worked          : {format_time_diff(int(item.get('worked_minutes', 0) or 0))}")
        print(f"OT              : {format_time_diff(int(item.get('ot_minutes', 0) or 0))}")
        print(f"OT Pay          : {item.get('ot_pay', 0)}")
        print(f"Deduction       : {item.get('deduction', 0)}")
        print(f"Break           : {format_time_diff(int(item.get('break_minutes', 0) or 0))}")
        print(f"Early Leave     : {format_time_diff(int(item.get('early_leave', 0) or 0))}")


def statistics_system():
    print("\n========== STATISTICS ==========")
    if not employees:
        print("No Employee Data")
        return

    most_late = max(employees, key=lambda emp: int(emp.get("late_time", 0) or 0))
    closed_records = [item for item in attendance_history if item.get("logout")]
    total_work = sum(int(item.get("worked_minutes", 0) or 0) for item in closed_records)
    total_ot = sum(int(item.get("ot_minutes", 0) or 0) for item in closed_records)
    avg_work = total_work // len(closed_records) if closed_records else 0

    print(f"Most late employee: {most_late.get('name', '')} ({most_late.get('late_time', 0)} time(s))")
    print(f"Average work time : {format_time_diff(avg_work)}")
    print(f"Total OT hours    : {format_time_diff(total_ot)}")


def monthly_report():
    print("\n========== MONTHLY REPORT ==========")
    year_month = input("Month (YYYY-MM, blank = current): ").strip() or today_text()[:7]

    total_salary = 0
    total_ot = 0
    total_ot_pay = 0
    late_count = 0
    total_deduction = 0

    for emp in employees:
        update_employee_month_total(emp, year_month)
        total_salary += int(emp.get("total_money", 0) or 0)

    for item in attendance_history:
        if item.get("date", "").startswith(year_month):
            total_ot += int(item.get("ot_minutes", 0) or 0)
            total_ot_pay += int(item.get("ot_pay", 0) or 0)
            total_deduction += int(item.get("deduction", 0) or 0)
            if int(item.get("late", 0) or 0) > 0:
                late_count += 1

    auto_save()
    print(f"Month          : {year_month}")
    print(f"Total Salary   : {total_salary}")
    print(f"Total OT       : {format_time_diff(total_ot)}")
    print(f"Total OT Pay   : {total_ot_pay}")
    print(f"Late Count     : {late_count}")
    print(f"Deduction      : {total_deduction}")


def build_report_text(year_month):
    lines = [
        "MONTHLY REPORT",
        f"Month: {year_month}",
        "",
        "Employees:",
    ]
    for emp in employees:
        update_employee_month_total(emp, year_month)
        lines.append(
            f"{emp.get('id')} | {emp.get('name')} | {emp.get('department')} | "
            f"Salary: {emp.get('total_money')} | Late: {emp.get('late_time')} | Leave: {emp.get('leave_days')}"
        )

    lines.append("")
    lines.append("Attendance:")
    for item in attendance_history:
        if item.get("date", "").startswith(year_month):
            lines.append(json.dumps(item, ensure_ascii=False))
    return "\n".join(lines)


def pdf_escape(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(filename, text):
    lines = text.splitlines()[:45]
    content_lines = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
    for line in lines:
        content_lines.append(f"({pdf_escape(line[:95])}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii"))

    with open(filename, "wb") as file:
        file.write(pdf)


def export_report():
    print("\n========== EXPORT REPORT ==========")
    print("1. CSV")
    print("2. TXT")
    print("3. PDF")
    choice = input("Select: ")
    year_month = input("Month (YYYY-MM, blank = current): ").strip() or today_text()[:7]

    try:
        if choice == "1":
            filename = f"monthly_report_{year_month}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Department", "Total Salary", "Late Count", "Leave Days"])
                for emp in employees:
                    update_employee_month_total(emp, year_month)
                    writer.writerow([
                        emp.get("id"), emp.get("name"), emp.get("department"),
                        emp.get("total_money"), emp.get("late_time"), emp.get("leave_days")
                    ])
            print(f"Exported: {filename}")
        elif choice == "2":
            filename = f"monthly_report_{year_month}.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(build_report_text(year_month))
            print(f"Exported: {filename}")
        elif choice == "3":
            filename = f"monthly_report_{year_month}.pdf"
            write_simple_pdf(filename, build_report_text(year_month))
            print(f"Exported: {filename}")
        else:
            print("Invalid Selection")
    except Exception as error:
        log_error(error)
        print(f"Export failed: {error}")

# ==========================================================
# MENU SYSTEM
# ==========================================================

def show_menu(title, options):
    print(f"\n========== {title} ==========")
    for key, text in options.items():
        print(f"{key}. {text}")
    return input("Select: ")


def timer_settings():
    global time_format_24
    while True:
        choice = show_menu("TIMER SETTINGS", {
            "1": "Use 12 Hour Format",
            "2": "Use 24 Hour Format",
            "3": "Back",
        })
        if choice == "1":
            time_format_24 = False
            print("12 Hour Format Enabled")
        elif choice == "2":
            time_format_24 = True
            print("24 Hour Format Enabled")
        elif choice == "3":
            break
        else:
            print("Invalid Selection")


def database_settings():
    while True:
        choice = show_menu("DATABASE SETTINGS", {
            "1": "Employee Work Time Data Set",
            "2": "Employee Break Time Data Set",
            "3": "Employee OT Time Data Set",
            "4": "Back",
        })
        if choice == "1":
            update_employee_time("work_time")
        elif choice == "2":
            update_employee_time("break_time")
        elif choice == "3":
            update_employee_time("ot_time")
        elif choice == "4":
            break
        else:
            print("Invalid Selection")


def database_functions():
    while True:
        choice = show_menu("DATABASE FUNCTIONS", {
            "1": "Show All Employee Data",
            "2": "Add New Employee Data",
            "3": "Delete Employee Data",
            "4": "Update Employee Data",
            "5": "Save Employee Data",
            "6": "Load Employee Data",
            "7": "Search Employee",
            "8": "Sort Employee",
            "9": "Back",
        })
        if choice == "1":
            show_all_employee_data()
        elif choice == "2":
            add_employee_data()
        elif choice == "3":
            delete_employee_data()
        elif choice == "4":
            update_employee_data()
        elif choice == "5":
            save_employee_data()
            save_attendance_history()
        elif choice == "6":
            load_employee_data()
            load_attendance_history()
        elif choice == "7":
            search_employee()
        elif choice == "8":
            sort_employee()
        elif choice == "9":
            break
        else:
            print("Invalid Selection")


def report_menu():
    while True:
        choice = show_menu("REPORT MENU", {
            "1": "Attendance History",
            "2": "Statistics",
            "3": "Monthly Report",
            "4": "Export Report",
            "5": "Back",
        })
        if choice == "1":
            show_attendance_history()
        elif choice == "2":
            statistics_system()
        elif choice == "3":
            monthly_report()
        elif choice == "4":
            export_report()
        elif choice == "5":
            break
        else:
            print("Invalid Selection")


def admin_menu():
    while True:
        choice = show_menu("ADMIN MENU", {
            "1": "Timer Settings",
            "2": "Database Settings",
            "3": "Database Functions",
            "4": "Leave System",
            "5": "Reports",
            "6": "Back",
        })
        if choice == "1":
            timer_settings()
        elif choice == "2":
            database_settings()
        elif choice == "3":
            database_functions()
        elif choice == "4":
            apply_leave()
        elif choice == "5":
            report_menu()
        elif choice == "6":
            break
        else:
            print("Invalid Selection")


def employee_menu():
    while True:
        choice = show_menu("EMPLOYEE MENU", {
            "1": "Login",
            "2": "Logout",
            "3": "Start Break",
            "4": "End Break",
            "5": "Back",
        })
        if choice == "1":
            employee_login()
        elif choice == "2":
            employee_logout()
        elif choice == "3":
            start_break()
        elif choice == "4":
            end_break()
        elif choice == "5":
            break
        else:
            print("Invalid Selection")

# ==========================================================
# ADMIN & MAIN LOGIN
# ==========================================================

def admin_login():
    print("\n========== ADMIN LOGIN ==========")
    admin_id = input("ID: ")
    password = input("Password: ")
    if admin_id == ADMIN_ID and hash_password(password) == ADMIN_PASSWORD_HASH:
        print("Admin Login Successful")
        admin_menu()
    else:
        print("Wrong Admin ID or Password")


def startup_load():
    load_employee_data(EMPLOYEE_FILE, ask_filename=False)
    load_attendance_history(HISTORY_FILE, ask_filename=False)


def main():
    startup_load()
    while True:
        try:
            print("\n================================")
            print(" EMPLOYEE LOGIN SYSTEM ")
            print("================================")
            print("Current Time:", get_time())
            choice = show_menu("MAIN MENU", {
                "1": "Employee Menu",
                "2": "Admin Login",
                "3": "Exit",
            })
            if choice == "1":
                employee_menu()
            elif choice == "2":
                admin_login()
            elif choice == "3":
                auto_save()
                print("Program Closed")
                break
            else:
                print("Invalid Selection")
        except Exception as error:
            log_error(error)
            print(f"System error saved to {ERROR_LOG_FILE}: {error}")

# ==========================================================
# START PROGRAM
# ==========================================================

if __name__ == "__main__":
    main()
