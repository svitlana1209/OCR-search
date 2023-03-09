import os
os.system("")

def search_in_txt(f_name, target):
    position = ()
    print("\033[96m" + "File:", f_name.name, "\033[0m")
    stroka = 1
    for line in f_name:
        poz = (line.upper()).find(target.upper())
        if poz != -1:
            print("\033[92m" + "      [Found]" + "\033[0m")
            position = (0,(stroka),(poz+1))
            break
        stroka = stroka + 1
    return position

