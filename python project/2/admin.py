import csv
import json

import database as db
import employee


def show_menu(title, options):
    print(f"\n========== {title} ==========")
    for key, text in options.items():
        print(f"{key}. {text}")
    return input("Select: ")


def timer_settings():
    while True:
        choice = show_menu("TIMER SETTINGS", {
            "1": "Use 12 Hour Format",
            "2": "Use 24 Hour Format",
            "3": "Back",
        })
        if choice == "1":
            db.set_time_format(False)
            print("12 Hour Format Enabled")
        elif choice == "2":
            db.set_time_format(True)
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
            employee.update_employee_time("work_time")
        elif choice == "2":
            employee.update_employee_time("break_time")
        elif choice == "3":
            employee.update_employee_time("ot_time")
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
            employee.show_all_employee_data()
        elif choice == "2":
            employee.add_employee_data()
        elif choice == "3":
            employee.delete_employee_data()
        elif choice == "4":
            employee.update_employee_data()
        elif choice == "5":
            db.save_employee_data()
            db.save_attendance_history()
        elif choice == "6":
            db.load_employee_data()
            db.load_attendance_history()
        elif choice == "7":
            employee.search_employee()
        elif choice == "8":
            employee.sort_employee()
        elif choice == "9":
            break
        else:
            print("Invalid Selection")


def show_attendance_history():
    if not db.attendance_history:
        print("No Attendance History")
        return

    print("\n========== ATTENDANCE HISTORY ==========")
    emp_id = input("Employee ID (blank = all): ").strip()
    for item in db.attendance_history:
        if emp_id and item.get("id") != emp_id:
            continue
        print("--------------------------------")
        print(f"ID              : {item.get('id', '')}")
        print(f"Date            : {item.get('date', '')}")
        print(f"Login           : {item.get('login', '')}")
        print(f"Logout          : {item.get('logout', '')}")
        print(f"Late            : {db.format_time_diff(int(item.get('late', 0) or 0))}")
        print(f"Worked          : {db.format_time_diff(int(item.get('worked_minutes', 0) or 0))}")
        print(f"OT              : {db.format_time_diff(int(item.get('ot_minutes', 0) or 0))}")
        print(f"OT Pay          : {item.get('ot_pay', 0)}")
        print(f"Deduction       : {item.get('deduction', 0)}")
        print(f"Break           : {db.format_time_diff(int(item.get('break_minutes', 0) or 0))}")
        print(f"Early Leave     : {db.format_time_diff(int(item.get('early_leave', 0) or 0))}")


def statistics_system():
    print("\n========== STATISTICS ==========")
    if not db.employees:
        print("No Employee Data")
        return

    most_late = max(db.employees, key=lambda emp: int(emp.get("late_time", 0) or 0))
    closed_records = [item for item in db.attendance_history if item.get("logout")]
    total_work = sum(int(item.get("worked_minutes", 0) or 0) for item in closed_records)
    total_ot = sum(int(item.get("ot_minutes", 0) or 0) for item in closed_records)
    avg_work = total_work // len(closed_records) if closed_records else 0

    print(f"Most late employee: {most_late.get('name', '')} ({most_late.get('late_time', 0)} time(s))")
    print(f"Average work time : {db.format_time_diff(avg_work)}")
    print(f"Total OT hours    : {db.format_time_diff(total_ot)}")


def monthly_report():
    print("\n========== MONTHLY REPORT ==========")
    year_month = input("Month (YYYY-MM, blank = current): ").strip() or db.today_text()[:7]

    total_salary = 0
    total_ot = 0
    total_ot_pay = 0
    late_count = 0
    total_deduction = 0

    for emp in db.employees:
        db.update_employee_month_total(emp, year_month)
        total_salary += int(emp.get("total_money", 0) or 0)

    for item in db.attendance_history:
        if item.get("date", "").startswith(year_month):
            total_ot += int(item.get("ot_minutes", 0) or 0)
            total_ot_pay += int(item.get("ot_pay", 0) or 0)
            total_deduction += int(item.get("deduction", 0) or 0)
            if int(item.get("late", 0) or 0) > 0:
                late_count += 1

    db.auto_save()
    print(f"Month          : {year_month}")
    print(f"Total Salary   : {total_salary}")
    print(f"Total OT       : {db.format_time_diff(total_ot)}")
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
    for emp in db.employees:
        db.update_employee_month_total(emp, year_month)
        lines.append(
            f"{emp.get('id')} | {emp.get('name')} | {emp.get('department')} | "
            f"Salary: {emp.get('total_money')} | Late: {emp.get('late_time')} | Leave: {emp.get('leave_days')}"
        )

    lines.append("")
    lines.append("Attendance:")
    for item in db.attendance_history:
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
    year_month = input("Month (YYYY-MM, blank = current): ").strip() or db.today_text()[:7]

    try:
        if choice == "1":
            filename = f"monthly_report_{year_month}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Department", "Total Salary", "Late Count", "Leave Days"])
                for emp in db.employees:
                    db.update_employee_month_total(emp, year_month)
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
        db.log_error(error)
        print(f"Export failed: {error}")


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
            employee.apply_leave()
        elif choice == "5":
            report_menu()
        elif choice == "6":
            break
        else:
            print("Invalid Selection")
