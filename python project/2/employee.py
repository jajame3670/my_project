from datetime import datetime

import auth
import database as db


def employee_login():
    print("\n========== EMPLOYEE LOGIN ==========")
    employee = auth.employee_authenticate()
    if not employee:
        return

    emp_id = employee.get("id")
    if db.get_open_attendance(emp_id):
        print("You already logged in and have not logged out yet.")
        auth.set_current_user(emp_id)
        return

    now = datetime.now()
    current_minutes = db.datetime_to_minutes(now)
    work_minutes = db.time_to_minutes(employee.get("work_time", "08:00"))
    day_text = db.today_text()

    if db.is_holiday(day_text):
        late = 0
        print("\nLogin Successful\nToday is a holiday. Late check skipped.")
    elif current_minutes <= work_minutes:
        late = 0
        print("\nLogin Successful\nYou are ON TIME")
    else:
        late = current_minutes - work_minutes
        print(f"\nLogin Successful\nYou are LATE\nLate: {db.format_time_diff(late)}")

    db.attendance_history.append({
        "id": emp_id,
        "date": day_text,
        "login": now.strftime("%H:%M"),
        "logout": "",
        "late": late,
        "worked_minutes": 0,
        "ot_minutes": 0,
        "ot_pay": 0,
        "deduction": db.calculate_late_deduction(late),
        "break_minutes": 0,
        "break_over_minutes": 0,
        "early_leave": 0,
        "holiday": "yes" if db.is_holiday(day_text) else "no",
        "break_start": "",
    })

    employee["login_time"] = db.get_current_datetime()
    employee["logout_time"] = ""
    employee["late_time"] = int(employee.get("late_time", 0) or 0) + (1 if late > 0 else 0)
    auth.set_current_user(emp_id)
    db.auto_save()
    db.notify("Work Started")


def employee_logout():
    print("\n========== EMPLOYEE LOGOUT ==========")
    emp_id = auth.get_current_user() or input("Employee ID: ").strip()
    employee = db.find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return

    record = db.get_open_attendance(emp_id)
    if not record:
        print("No active login found.")
        return

    if record.get("break_start"):
        print("Please end break before logout.")
        return

    now = datetime.now()
    logout_minutes = db.datetime_to_minutes(now)
    login_minutes = db.time_to_minutes(record.get("login", "00:00"))
    ot_minutes_base = db.time_to_minutes(employee.get("ot_time", "17:00"))

    worked_minutes = max(0, db.minutes_between(login_minutes, logout_minutes) - int(record.get("break_minutes", 0) or 0))
    ot_minutes = max(0, db.minutes_between(ot_minutes_base, logout_minutes))
    early_leave = 0 if logout_minutes >= ot_minutes_base else ot_minutes_base - logout_minutes

    ot_rate = int(employee.get("ot_pay_per_hour", db.DEFAULT_OT_PAY_PER_HOUR) or 0)
    if record.get("holiday") == "yes":
        ot_rate *= 2
    ot_pay = db.calculate_hour_money(ot_minutes, ot_rate)

    total_deduction = int(record.get("deduction", 0) or 0) + db.calculate_break_deduction(int(record.get("break_over_minutes", 0) or 0))

    record["logout"] = now.strftime("%H:%M")
    record["worked_minutes"] = worked_minutes
    record["ot_minutes"] = ot_minutes
    record["ot_pay"] = ot_pay
    record["deduction"] = total_deduction
    record["early_leave"] = early_leave

    employee["logout_time"] = db.get_current_datetime()
    db.update_employee_month_total(employee)
    auth.clear_current_user()
    db.auto_save()

    print(f"Worked: {db.format_time_diff(worked_minutes)}")
    print(f"OT: {db.format_time_diff(ot_minutes)}")
    print(f"Extra Pay: {ot_pay}")
    print(f"Deduction: {total_deduction}")
    if early_leave:
        print(f"Early leave: {db.format_time_diff(early_leave)}")
    db.notify("Work Ended")


def start_break():
    emp_id = auth.get_current_user() or input("Employee ID: ").strip()
    record = db.get_open_attendance(emp_id)
    if not record:
        print("Please login before starting break.")
        return
    if record.get("break_start"):
        print("Break already started.")
        return
    record["break_start"] = datetime.now().strftime("%H:%M")
    db.auto_save()
    print("Break started.")


def end_break():
    emp_id = auth.get_current_user() or input("Employee ID: ").strip()
    record = db.get_open_attendance(emp_id)
    if not record or not record.get("break_start"):
        print("No active break found.")
        return

    start_minutes = db.time_to_minutes(record["break_start"])
    end_minutes = db.datetime_to_minutes(datetime.now())
    break_minutes = db.minutes_between(start_minutes, end_minutes)
    total_break = int(record.get("break_minutes", 0) or 0) + break_minutes
    over_minutes = max(0, total_break - db.STANDARD_BREAK_MINUTES)

    record["break_minutes"] = total_break
    record["break_over_minutes"] = over_minutes
    record["break_start"] = ""
    db.auto_save()
    print(f"Break ended. Total break: {db.format_time_diff(total_break)}")
    if over_minutes:
        print(f"Break over limit: {db.format_time_diff(over_minutes)}")


def apply_leave():
    print("\n========== LEAVE SYSTEM ==========")
    emp_id = input("Employee ID: ").strip()
    employee = db.find_employee(emp_id)
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

    days = db.input_int("Leave days: ", 1)
    remain = int(employee.get("leave_days", 0) or 0)
    if days <= 0:
        print("Leave days must be more than 0")
        return
    if days > remain:
        print(f"Not enough leave days. Remaining: {remain}")
        return

    employee["leave_days"] = remain - days
    db.auto_save()
    print(f"{leave_type} approved. Remaining leave days: {employee['leave_days']}")


def show_all_employee_data(data=None):
    data = data if data is not None else db.employees
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
        safe = db.visible_employee(emp)
        for key in keys:
            print(f"{key.replace('_', ' ').title():18}: {safe.get(key, '')}")


def add_employee_data():
    print("\n========== ADD EMPLOYEE ==========")
    emp_id = input("Employee ID: ").strip()
    if db.find_employee(emp_id):
        print("Employee ID already exists.")
        return

    shift = input("Shift (Morning/Night): ").strip().title() or "Morning"
    if shift not in db.SHIFTS:
        shift = "Morning"

    income = db.input_int("Income per month: ")
    role = input("Role (Staff/Manager/HR): ").strip().title() or "Staff"
    password = input("Password: ")
    emp = {
        "name": input("Name: "),
        "id": emp_id,
        "password": auth.hash_password(password),
        "department": input("Department: "),
        "role": role,
        "shift": shift,
        "work_time": db.SHIFTS[shift]["work_time"],
        "break_time": db.SHIFTS[shift]["break_time"],
        "ot_time": db.SHIFTS[shift]["ot_time"],
        "income_per_month": income,
        "total_money": income,
        "late_time": 0,
        "login_time": "",
        "logout_time": "",
        "leave_days": db.input_int("Leave days: ", 5),
        "ot_pay_per_hour": db.input_int("OT pay per hour: ", db.DEFAULT_OT_PAY_PER_HOUR),
        "manager_id": input("Manager ID (optional): "),
    }
    db.employees.append(db.ensure_employee_defaults(emp))
    db.auto_save()
    print("Employee Added")


def delete_employee_data():
    emp_id = input("Employee ID: ").strip()
    employee = db.find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    db.employees.remove(employee)
    db.auto_save()
    print("Employee Deleted")


def update_employee_data():
    emp_id = input("Employee ID: ").strip()
    employee = db.find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return

    print("\n========== UPDATE EMPLOYEE ==========")
    employee["name"] = input("New Name: ") or employee.get("name", "")
    new_password = input("New Password (blank = keep old): ")
    if new_password:
        employee["password"] = auth.hash_password(new_password)
    employee["department"] = input("New Department: ") or employee.get("department", "")
    employee["role"] = input("New Role (Staff/Manager/HR): ") or employee.get("role", "Staff")
    employee["shift"] = input("New Shift (Morning/Night): ") or employee.get("shift", "Morning")
    employee["income_per_month"] = db.input_int("New Income per month: ", int(employee.get("income_per_month", 0) or 0))
    employee["leave_days"] = db.input_int("New Leave days: ", int(employee.get("leave_days", 5) or 5))
    employee["ot_pay_per_hour"] = db.input_int("New OT pay per hour: ", int(employee.get("ot_pay_per_hour", db.DEFAULT_OT_PAY_PER_HOUR) or 0))
    employee["manager_id"] = input("New Manager ID: ") or employee.get("manager_id", "")
    db.update_employee_month_total(employee)
    db.auto_save()
    print("Employee Updated")


def update_employee_time(field_name):
    emp_id = input("Employee ID: ").strip()
    employee = db.find_employee(emp_id)
    if not employee:
        print("Employee Not Found")
        return
    employee[field_name] = db.input_time(f"Set {field_name.replace('_', ' ').title()} (HH:MM): ", employee.get(field_name, "08:00"))
    db.auto_save()
    print(f"{field_name.replace('_', ' ').title()} Updated")


def search_employee():
    print("\n========== SEARCH EMPLOYEE ==========")
    print("1. Search by ID")
    print("2. Search by Name")
    print("3. Search by Department")
    choice = input("Select: ")
    keyword = input("Keyword: ").strip().lower()

    if choice == "1":
        result = [emp for emp in db.employees if keyword in emp.get("id", "").lower()]
    elif choice == "2":
        result = [emp for emp in db.employees if keyword in emp.get("name", "").lower()]
    elif choice == "3":
        result = [emp for emp in db.employees if keyword in emp.get("department", "").lower()]
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
        data = sorted(db.employees, key=lambda emp: int(emp.get("late_time", 0) or 0), reverse=True)
    elif choice == "2":
        data = sorted(db.employees, key=lambda emp: int(emp.get("total_money", 0) or 0), reverse=True)
    elif choice == "3":
        data = sorted(db.employees, key=lambda emp: emp.get("department", ""))
    else:
        print("Invalid Selection")
        return
    show_all_employee_data(data)


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


def show_menu(title, options):
    print(f"\n========== {title} ==========")
    for key, text in options.items():
        print(f"{key}. {text}")
    return input("Select: ")
