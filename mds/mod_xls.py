import os
import pandas as pd
import progress.bar as pb
from . import mod_utl as utl

os.system("")

def search_in_xls(f_name, target):
    position = ()
    try:
        book = pd.ExcelFile(f_name)
    except:
        print("Can't open file: ", os.path.absname(f_name))
    else:
        print("\033[96m" + "File:", f_name, "\033[0m")
        bar = pb.Bar("\033[93m" + "      sheet processing ..."+"\033[0m", fill='#', max=len(book.sheet_names), suffix='%(percent)d%%')
        p = -1
        for sheet in range(0, len(book.sheet_names)):
            try:
                tab = pd.read_excel(f_name, book.sheet_names[sheet])
            except:
                print("\033[96m" + "\n      Can't read the sheet:", book.sheet_names[sheet], "\033[0m")
                break
            else:
                if tab.shape[0]>3000 or tab.shape[1]>1000:
                    print("\033[96m" + "\n      The number of columns or rows on the sheet"+"\033[0m"+"\033[93m", book.sheet_names[sheet], "\033[0m"+"\033[96m" +"is too large"+"\033[0m")
                else:
                    df = pd.DataFrame(tab)
                    for i in range(df.shape[0]):
                        for j in range(df.shape[1]):
                            try:
                                s = utl.normolize_string(str(df.iat[i,j]))
                                p = (s.upper()).rfind(target.upper())
                            except:
                                pass
                            if p >= 0:
                                break
                        if p >= 0:
                           break
                    bar.next()
            if p >= 0:
                bar.finish()
                position = (sheet+1,(i+2),(j+1))
                print("\033[92m" + "      [Found]" + "\033[0m")
                break
        if p < 0:
            bar.finish()
    return position
