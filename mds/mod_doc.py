import os
from docx2python import docx2python
from odf.opendocument import load
from odf import text, teletype

os.system("")

def search_in_doc(f_name, zrazok, code_page):
    position = ()
    print("\033[96m" + "File:", f_name, "\033[0m")
    if f_name.endswith('.docx'):
        try:
            docum = docx2python(f_name)
            docum.body_runs
            for i in range(0, len(docum.body_runs)):
                s = str(docum.body_runs[i])
                poz = (s.upper()).find(zrazok.upper())
                if poz != -1:
                    print("\033[92m" + "      [Found]" + "\033[0m")
                    position = (0,0,0)
                    break
        except:
            print("Can't process file: ", os.path.abspath(f_name))
    elif f_name.endswith('.doc'):
        if code_page[0:2] == 'cp':
            kod = code_page[2:]
        else:
            kod = code_page
        try:
            os.system("antiword -m \"" + code_page + "\".txt \"" + f_name + "\" > tmp.txt 2>&1")
            with open("tmp.txt", "r", encoding=kod) as f_tmp:
                for line in f_tmp:
                    poz = (line.upper()).find(zrazok.upper())
                    if poz != -1:
                        print("\033[92m" + "      [Found]" + "\033[0m")
                        position = (0,0,0)
                        break
            os.remove("tmp.txt")
        except:
            print("Can't process file: ", os.path.abspath(f_name))
    elif f_name.endswith('.odt'):
        try:
            my_doc = load(f_name)
            all_part = my_doc.getElementsByType(text.P)
            for i in range(0, len(all_part)):
                s = teletype.extractText(all_part[i])
                poz = (s.upper()).find(zrazok.upper())
                if poz != -1:
                    print("\033[92m" + "      [Found]" + "\033[0m")
                    position = (0,0,0)
                    break
        except:
            print("Can't process file: ", os.path.abspath(f_name))
    return position

