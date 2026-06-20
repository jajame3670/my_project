import hashlib

import database as db

ADMIN_ID = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("123".encode()).hexdigest()

current_user = None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def verify_password(input_password, stored_password):
    if is_hash(stored_password):
        return hash_password(input_password) == stored_password
    return input_password == stored_password


def get_current_user():
    return current_user


def set_current_user(emp_id):
    global current_user
    current_user = emp_id


def clear_current_user():
    global current_user
    current_user = None


def admin_login(on_success):
    print("\n========== ADMIN LOGIN ==========")
    admin_id = input("ID: ")
    password = input("Password: ")
    if admin_id == ADMIN_ID and hash_password(password) == ADMIN_PASSWORD_HASH:
        print("Admin Login Successful")
        on_success()
    else:
        print("Wrong Admin ID or Password")


def employee_authenticate():
    emp_id = input("ID: ").strip()
    password = input("Password: ")
    employee = db.find_employee(emp_id)

    if not employee or not verify_password(password, employee.get("password", "")):
        print("Wrong ID or Password")
        return None

    if not is_hash(employee.get("password", "")):
        employee["password"] = hash_password(password)
        db.auto_save()
        print("Password upgraded to encrypted format.")

    return employee
