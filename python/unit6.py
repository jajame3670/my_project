value = "123"
while True:
    data = input("passwd: ")
    if data == value:
        print("Password correct!")
        break
    else:
        print("Incorrect password. Please try again.")