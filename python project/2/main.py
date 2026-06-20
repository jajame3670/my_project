import auth
import admin
import database as db
import employee


def show_menu(title, options):
    print(f"\n========== {title} ==========")
    for key, text in options.items():
        print(f"{key}. {text}")
    return input("Select: ")


def main():
    db.startup_load()
    while True:
        try:
            print("\n================================")
            print(" EMPLOYEE LOGIN SYSTEM ")
            print("================================")
            print("Current Time:", db.get_time())
            choice = show_menu("MAIN MENU", {
                "1": "Employee Menu",
                "2": "Admin Login",
                "3": "Exit",
            })
            if choice == "1":
                employee.employee_menu()
            elif choice == "2":
                auth.admin_login(admin.admin_menu)
            elif choice == "3":
                db.auto_save()
                print("Program Closed")
                break
            else:
                print("Invalid Selection")
        except Exception as error:
            db.log_error(error)
            print(f"System error saved to {db.ERROR_LOG_FILE}: {error}")


if __name__ == "__main__":
    main()
