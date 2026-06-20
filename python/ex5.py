menu = """ ==== ໂປຣແກຣມຮ້ານອາຫານ ====
1. ເຂົ້າພັດ 20000 ກິບ
2. ເຝີ 25000 ກິບ
4. ເຂົ້າປຽກ 15000 ກິບ
5. ລາບ 30000 ກິບ
6. ແກງໜໍໄມ້ 18000 ກິບ
7. ໝປິ້ງ 10000 ກິບ
8. ບໍ່ຕ້ອງການສັ້ງ
==============================="""
grand_total = 0
orders = []
while True:
    print(menu)
    choice = input("ເລືອກເລກ: ")
    if choice == "1":
        print("ເຈົ້າເລື່ອກ: ເຂົ້າພັດ")
        num = input("ຈຳນວນ: ")
        total = int(num) * 20000
    elif choice == "2":
        print("ເຈົ້າເລື່ອກ: ເຝີ")
        num = input("ຈຳນວນ: ")
        total = int(num) * 25000
    elif choice == "4":
        print("ເຈົ້າເລື່ອກ: ເຂົ້າປຽກ")
        num = input("ຈຳນວນ: ")
        total = int(num) * 15000
    elif choice == "5":
        print("ເຈົ້າເລື່ອກ: ລາບ")
        num = input("ຈຳນວນ: ")
        total = int(num) * 30000
    elif choice == "6":
        print("ເຈົ້າເລື່ອກ: ແກງໜໍໄມ້")
        num = input("ຈຳນວນ: ")
        total = int(num) * 18000
    elif choice == "7":
        print("ເຈົ້າເລື່ອກ: ໝປິ້ງ")
        num = input("ຈຳນວນ: ")
        total = int(num) * 10000
    elif choice == "8":
        confirm = input("ແນ່ໃຈບໍ? (y/n): ")
        if confirm.lower() == "y":
            print("\n--- ສະຫຼຸບການສັ່ງ ---")
            for order in orders:
                print(order)
                print("---")
            print(f"ລວມທັງຫມົດທີ່ຕ້ອງຈ່າຍ: {grand_total} ກີບ")
            break
        else:
            continue
    else:
        print("ເລືອກເລກ 1, 2, 3, 4, 5, 6, 7 ຫຼື 8 ແທນ")
        continue
    if total > 200000:
        eq = total * 0.1
        final_total = total - eq
        discount_msg = "10%"
    elif total > 100000:
        eq = total * 0.05
        final_total = total - eq
        discount_msg = "5%"
    else:
        final_total = total
        discount_msg = "0%"
    grand_total += final_total
    sumary = """ການເລືອກເລກ: {}
    ຈໍານວນ: {}
    ລາຄາທັງຫມົດ: {} ກີບ
    ສ່ວນຫຼຸດ: {}
    ຈໍານວນທີ່ຕ້ອງຈ່າຍສຸດທ້າຍ: {} ກີບ
    ລວມທັງຫມົດຈົນເຖິງຕອນນີ້: {} ກີບ""".format(choice, num, total, discount_msg, final_total, grand_total)
    orders.append(sumary)
    more_choice = input("ເຈົ້າຕ້ອງຫຍັງຕື່ມບໍ່? (y/n): ")
    if more_choice.lower() == "n":
        confirm = input("ແນ່ໃຈບໍ? (y/n): ")
        if confirm.lower() == "y":
            print("\n--- ສະຫຼຸບການສັ່ງ ---")
            for order in orders:
                print(order)
                print("---")
            print(f"ລວມທັງຫມົດທີ່ຕ້ອງຈ່າຍ: {grand_total} ກີບ")
            break
        else:
            continue