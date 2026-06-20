while True:
    print("\n==== ໂປຣແກຣມຮ້ານອາຫານ ====")
    total = 0
    while True:
        print("\n1. ເຂົ້າພັດ 20000 ກິບ")
        print("2. ເຝີ 25000 ກິບ")
        print("4. ເຂົ້າປຽກ 15000 ກິບ")
        print("5. ລາບ 30000 ກິບ")
        print("6. ແກງໜໍໄມ້ 18000 ກິບ")
        print("7. ໝປິ້ງ 10000 ກິບ")
        print("8. ບໍ່ຕ້ອງການສັ້ງ")
        menu = int(input("ກະລຸນາເລືອກ 1-8: "))
        if menu == 8:
            break
        qty = int(input("ຈຳນວນ: "))
        if menu == 1:
            price = 20000
        elif menu == 2:
            price = 25000
        elif menu == 4:
            price = 15000
        elif menu == 5:
            price = 30000
        elif menu == 6:
            price = 18000
        elif menu == 7:
            price = 10000
        else:
            print("ກະລຸນາເລືອກ 1-8 ແທນ")
            continue
        total += price * qty
    if total > 200000:
        discount = total * 0.1
        final_total = total - discount
    elif total > 100000:
        discount = total * 0.05
    else:
        discount = 0
        
        final_total = total - discount
        discount_msg = "5%"
    final = total - discount
    print("\nລາຄາລວມ: ", total, "ກິບ")
    print("ສ່ວນຫຼຸດ: ", discount, "ກິບ")
    print("ລາຄາຈ່າຍຕົວຈິງ: ", final, "ກິບ")
    ask = input("ຕ້ອງການສັ້ງອີກຄັ້ງບໍ່? (y/n): ")
    if ask.upper() == "N" or ask.lower() == "n":
        print("ຂອບໃຈທີ່ໃຊ້ບໍ່ການສັ້ງ")
        break