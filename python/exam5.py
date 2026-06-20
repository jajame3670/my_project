Id = int(input("your id: "))
name = input("your name: ")
surename = input("your surename: ")
salary = float(input("your salary: "))
OT = float(input("your OT: "))
fa = float(input("your fa: "))
print("=====================")
total = salary+OT+fa
if total > 1000000:
    tax = total*0.1
    total_salary = total-tax
    print("your id: ", Id)
    print("your name and surename: ", name, surename)
    print("your salary: ", salary)
    print("your OT: ", OT)
    print("your fa: ", fa)
    print("=====================")
    print("income = ", total)
    print("tax = ", tax)
    print("total_salary = " ,total_salary)
elif total > 850000:
    tax = total*0.07
    total_salary = total-tax
    print("your id: ", Id)
    print("your name and surename: ", name, surename)
    print("your salary: ", salary)
    print("your OT: ", OT)
    print("your fa: ", fa)
    print("=====================")
    print("income = ", total)
    print("tax = ", tax)
    print("total_salary = " ,total_salary)
else:
    tax = 0
    total_salary = total-tax
    print("your id: ", Id)
    print("your name and surename: ", name, surename)
    print("your salary: ", salary)
    print("your OT: ", OT)
    print("your fa: ", fa)
    print("=====================")
    print("income = ", total)
    print("tax = ", tax)
    print("total_salary = " ,total_salary)

