import csv
import os
import traceback
from datetime import date, datetime

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


def log_error(error):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        file.write(str(error) + "\n")
        file.write(traceback.format_exc() + "\n")


def notify(text):
    print("\a")
    print(f"[NOTIFICATION] {text}")


def set_time_format(use_24_hour):
    global time_format_24
    time_format_24 = use_24_hour


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
    return int((minutes / 60) * rate)


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
    if ask_filename:
        filename = input("Enter CSV filename: ").strip() or EMPLOYEE_FILE
    filename = filename or EMPLOYEE_FILE
    if not os.path.exists(filename):
        if ask_filename:
            print("File Not Found")
        return

    try:
        employees.clear()
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
    if ask_filename:
        filename = input("Enter history CSV filename: ").strip() or HISTORY_FILE
    filename = filename or HISTORY_FILE
    if not os.path.exists(filename):
        if ask_filename:
            print("File Not Found")
        return

    try:
        attendance_history.clear()
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


def startup_load():
    load_employee_data(EMPLOYEE_FILE, ask_filename=False)
    load_attendance_history(HISTORY_FILE, ask_filename=False)
