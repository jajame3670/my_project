cont = 1
total = 0
steps = []
while cont in range(1, 21):
    steps.append(str(cont))
    total += cont
    cont += 1
print("ຂັ້ນຕອນ: "+"+".join(steps))
print("ຜົນລວມ: ", total)