#!/usr/bin/python3
# -----------------------------------------------------------------------
# Searching for text in scanned documents, spreadsheets, and other files
# in a specified directory. Supported formats:
# pdf/png/jpeg/jpg/tif/doc/docx/odt/xls/xlsx/ods/txt
# Return the coordinates of the first occurrence in the protocol.
# ------------------------------------------------------------------------
import os
from datetime import datetime
import filetype as ft
from mds import mod_doc as doc
from mds import mod_xls as xls
from mds import mod_txt as txt
from mds import mod_pdf as graphic

conf = dict({"target": "", "dirsch": "", "subdir": 0, "remove_noise": 0, "cp": "UTF-8"})
kodi = ["utf-8", "utf-16", "ANSI", "1251"]
type_ext =  (("pdf",1), ("png",2), ("jpeg",2), ("jpg",2), ("tif",2), ("tiff",2), ("doc",3), ("docx",3), ("odt",3), ("xls",4), ("xlsx",4), ("ods",4))
total_files = [['pdf',0],['xls/xlsx',0],['doc/docx',0],['txt',0],['image',0]]
pattern_found = [['pdf',0],['xls/xlsx',0],['doc/docx',0],['txt',0],['image',0]]
os.system("")

def main():
    global log
    try:
        log = open(r"search.log", "w+", encoding="utf-8")
    except:
        print("Can't create log file")
        return
    t_start = datetime.now()
    if read_config() == 0:
        log.write(" ".join(("Search pattern:", conf["target"])))
        log.write("\nWas found in files:")
        log.write("\n"+ "-"*120 +"\n")
        log.write("   page (sheet)  |   row   |  column  |   File\n")
        log.write("      number     |         |          |       \n")
        log.write("-"*120 +"\n")
        try:
            os.chdir(conf["dirsch"])
        except:
            print("Unable to change directory: ", conf["dirsch"], "Check parameter `dirsch` in search.conf")
            return
        start(conf)
        log.close()
        print("----------------------+--------------+--------------+--------------+----------+-----------")
        print("                      |     Pdf      | Xls/Xlsx/Ods | Doc/Docx/Odt |   Txt    |  Images")
        print("----------------------+--------------+--------------+--------------+----------+-----------")
        print("\033[94m"+"Total files processed"+"\033[0m"+" |", str(total_files[0][1]).rjust(9), str(total_files[1][1]).rjust(13), str(total_files[2][1]).rjust(13), str(total_files[3][1]).rjust(12), str(total_files[4][1]).rjust(10))
        print("\033[92m"+"Pattern was found"+"\033[0m"+"     |", str(pattern_found[0][1]).rjust(9), str(pattern_found[1][1]).rjust(13), str(pattern_found[2][1]).rjust(13), str(pattern_found[3][1]).rjust(12), str(pattern_found[4][1]).rjust(10))
        print("----------------------+-------------------------------------------------------------------")
        t_end = datetime.now()
        total = 0
        for i in range(0, len(total_files)):
            total = total + total_files[i][1]
        print("Total files processed:", total)
        print("Time start  :", t_start.strftime("%H:%M:%S"))
        print("Time finish :", t_end.strftime("%H:%M:%S"))
        print("\033[95m"+"Protocol: search.log"+"\033[0m")
        input("Done. Press Enter to exit ...")

def read_config():
    try:
        with open(r"search.conf", "r", encoding="utf-8") as cfg_file:
            p = fill_dict(cfg_file, conf)
    except FileNotFoundError:
        p = create_config()
    return p

def create_config():
    try:
        with open(r"search.conf", "w", encoding="utf-8") as cfg_file:
            cfg_file.write("# Set a search value:\n# For example: some Text 1234567890\nsearch:\n\n# Set a search path. If empty, the current directory will be used.\n# For example: C: or C:\dir1\dir2 or /tmp/dir1/dir2\ndirsch:\n\n# Set value to 1 to search in subdirectories, otherwise 0:\nsubdir: 1\n\n# Set value to 1 to remove noise from the image. Used for images with poor quality.\n# It's takes extra time during PDF/Img files processing:\nremove_noise: 0\n\n# Set codepage. Default: UTF-8. For Cyrillic use: cp1251\ncodepage: UTF-8\n")
            cfg_file.close()
            print("Set values in search.conf")
            return 1
    except:
        print("Cant't create search.conf in the current directory")
        return -1

def fill_dict(cfg_file, conf):
    for line in cfg_file:
        if line[0] != '#':
            i = 0
            par = ""
            znach = ""
            if (line.lstrip()).rstrip() != "":
                while line[i] != ':':
                    par = "".join((par,line[i]))
                    i = i + 1 
                znach = ((line[i+1:-1]).lstrip()).rstrip()

                if par == "search":
                    if znach == "":
                        print("Set search pattern (`search` in file search.conf)")
                        return -1
                    else:
                        conf["target"] = znach
                elif par == "dirsch":
                    if znach == "":
                        conf["dirsch"] = os.getcwd()
                    else:
                        conf["dirsch"] = znach
                elif par == "subdir":
                    try:
                        sd = int(znach)
                    except:
                        print("The parametr `subdir` in the file search.conf must have a numeric value and equal to 0 or 1")
                        return -1
                    if sd not in [0,1]:
                        print("The parametr `subdir` in the file search.conf must equal to 0 or 1")
                        return -1
                    else:
                        conf["subdir"] = sd
                elif par == "remove_noise":
                    try:
                        noise = int(znach)
                    except:
                        print("The parametr `remove_noise` in the file search.conf must have a numeric value and equal to 0 or 1")
                        return -1
                    if noise not in [0,1]:
                        print("The parametr `remove_noise` in the file search.conf must equal to 0 or 1")
                        return -1
                    else:
                        conf["remove_noise"] = noise
                elif par == "codepage":
                    if znach == "":
                        conf["cp"] = 'UTF-8'
                    else:
                        conf["cp"] = znach
    return 0

def start(conf):
    print("\033[92m" + "Search pattern set:", conf["target"], "\033[0m")
    if conf["remove_noise"] == 1:
        print("\033[95m"+"The noise removal option is set, the process will be slower", "\033[0m")
    if conf["subdir"] == 0:
        print("\033[44m" + "Processing files in the directory:", conf["dirsch"], "\033[0m")
        for f in os.scandir(conf["dirsch"]):
            if not f.is_dir():
                call_file(conf["dirsch"], f.name)
    else:
        for (p,d,f) in os.walk(conf["dirsch"]):
            print("\033[44m" + "Processing files in the directory:", p, "\033[0m")
            for i in range(len(f)):
                call_file(p, f[i])

def call_file(f_path, f_name):
    if f_path != conf["dirsch"]:
        os.chdir(f_path)
    try:
        f_type = ft.guess(f_name)
    except:
        print("Can't open file: ", os.path.abspath(f_name))
    else:
        if f_type == None:
            for k in kodi:
                try:
                    with open(f_name, "r", encoding=k) as f:
                        position = txt.search_in_txt(f, conf["target"])
                        total_files[3][1] = total_files[3][1] + 1
                        if len(position) > 0:
                            out_to_log(log, f_name, position)
                            pattern_found[3][1] = pattern_found[3][1] + 1
                        break
                except:
                    pass
        else:
            t = ft.get_type(mime=f_type.mime)
            func_number = 0
            for i in range(0,len(type_ext)):
                ext = type_ext[i][0]
                if t.is_extension(ext):
                    func_number = type_ext[i][1]
                    break
            if func_number > 0:
                if func_number == 1:
                    position = graphic.search_in_pdf(f_name, conf["target"], conf["remove_noise"])
                    total_files[0][1] = total_files[0][1] + 1
                    if len(position) > 0:
                        out_to_log(log, f_name, position)
                        pattern_found[0][1] = pattern_found[0][1] + 1
                elif func_number == 2:
                    position = graphic.search_in_image(f_name, conf["target"], conf["remove_noise"])
                    total_files[4][1] = total_files[4][1] + 1
                    if len(position) > 0:
                        out_to_log(log, f_name, position)
                        pattern_found[4][1] = pattern_found[4][1] + 1
                elif func_number == 3:
                    position = doc.search_in_doc(f_name, conf["target"], conf["cp"])
                    total_files[2][1] = total_files[2][1] + 1
                    if len(position) > 0:
                        out_to_log(log, f_name, position)
                        pattern_found[2][1] = pattern_found[2][1] + 1
                elif func_number == 4:
                    position = xls.search_in_xls(f_name, conf["target"])
                    total_files[1][1] = total_files[1][1] + 1
                    if len(position) > 0:
                        out_to_log(log, f_name, position)
                        pattern_found[1][1] = pattern_found[1][1] + 1

def out_to_log(log, f_name, position):
    if position[0] > 0:
        arkush = str(position[0])
    else:
        arkush = ""
    if position[1] > 0:
        row = str(position[1])
    else:
        row = ""
    if position[2] > 0:
        col = str(position[2])
    else:
        col = ""

    log.write(arkush.rjust(12))
    log.write(row.rjust(12))
    log.write(col.rjust(12))
    log.write("".join(("     ",os.path.abspath(f_name),"\n")))


if __name__ == '__main__':
    main()

