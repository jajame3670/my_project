a = int(input("Enter a number: "))
b = int(input("Enter b number: "))
print("======================")
print("Menu: ")
print("1. Z = a^4-2a^3*b+b^3")
print("2. q = a^2+a^3*b^4+b^2")
print("3. r = a^4-b^3")
print("======================")

please = input("Please enter your programme: ")
if please == "z" or please == "Z":
    z = a**4-2*(a**3)*b+b**3
    print("Z = ", z)
elif please == "q" or please == "Q":
    q = a**2+a**3*b**4+b**2
    print("q = ", q)
elif please == "r" or please == "R":
    r = a**4-b**3
    print("r = ", r)
else:
    print("error")
print("end")