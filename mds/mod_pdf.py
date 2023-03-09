import os
import re
import cv2
import math
import numpy as np
import pdf2image as im
import pytesseract as pt
import progress.bar as pb
from . import mod_utl as utl

os.system("")

def search_in_pdf(pdf_name, target, denoise):
    global curent_page, total_page
    position = ()
    print("\033[94m" + "File:", pdf_name, "\033[0m")
    print("\033[94m" + "      Converting file ..." + "\033[0m", end=' ', flush=True)
    try:
        pdf_pages = im.convert_from_path(pdf_name, 300)
        print("\033[94m"+"[Ok]"+ "\033[0m")
    except:
        print("Can't convert file")
        return position
    total_page = len(pdf_pages)
    for curent_page, image in enumerate(pdf_pages):
        img_name = 'Img.png'
        image.save(img_name, "PNG")
        binary = prepare_image(img_name, denoise)
        os.remove(img_name)
        if cv2.countNonZero(binary) != 0:
            binary = rotate_image(binary)
            if recognize_image(binary, target) == 1:
                print("\033[92m" + "      [Found]" + "\033[0m")
                position = (curent_page+1, 0, 0)
                break
    return position

def search_in_image(image_name, target, denoise):
    global curent_page, total_page
    position = ()
    curent_page = 0
    total_page = 1
    print("\033[94m" + "File:", image_name, "\033[0m")
    binary = prepare_image(image_name, denoise)
    if cv2.countNonZero(binary) != 0:
        binary = rotate_image(binary)
        if recognize_image(binary, target) == 1:
            print("\033[92m" + "      [Found]" + "\033[0m")
            position = (1, 0, 0)
    return position

def locate_table_struct(binary):
    coord_of_cells = []
    rows, cols = binary.shape[:2]
    scale_x = 40
    scale_y = 30
    if rows < 700:
        scale_x = scale_x / 10
        scale_y = scale_y / 10

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // int(scale_x), 1))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_col = cv2.dilate(eroded, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // int(scale_y)))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_row = cv2.dilate(eroded, kernel, iterations=1)

    bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)
    y_set, x_set = np.where(bitwise_and > 0)
    if len(y_set) > 1 and len(x_set) > 1:
        coord_of_cells = get_table_cells(x_set,y_set)
    return coord_of_cells

def get_table_cells(x_set, y_set):
    xy = []
    points = []
    a1_points = []
    coord = []

    for i in range(0, len(x_set)):
        xy.append([x_set[i],y_set[i]])
    length = len(xy)
    for i in range(0, length):
        tmp = []
        if i >= length:
            break
        else:
            x1 = xy[i][0]
            y1 = xy[i][1]
            tmp.append(xy[i])
            j = i + 1
            while j < length:
                if ((xy[j][0] < x1+5) and (xy[j][0] > x1-5)) and ((xy[j][1] < y1+5) and (xy[j][1] > y1-5)):
                    tmp.append(xy[j])
                    xy.remove(xy[j])
                    length = len(xy)
                else:
                    j = j + 1
            x2 = y2 = 0
            for k in range(0, len(tmp)):
                x2 = x2 + tmp[k][0]
                y2 = y2 + tmp[k][1]
            x3 = x2 // len(tmp)
            y3 = y2 // len(tmp)
            points.append([x3,y3])
    L = len(points)
    half_cell = j = 0
    for i in range(0, L):
        if j > 0:
            i = j
        if i >= L:
            break
        else:
            t = []
            t.append(points[i])
            y_fix = points[i][1]
            j = i + 1
            while j < L:
                if (points[j][1] < y_fix+20) and (points[j][1] > y_fix-20):
                    t.append(points[j])
                    j = j + 1
                else:
                    break
            t.sort(key=lambda col: (col[0], col[1]))
            a1_points.append(t)
            if len(t) == 1:
                half_cell = half_cell + 1
    if half_cell <= 1:
        rows = len(a1_points)
        for row in range(0, rows):
            for elem in range(0, len(a1_points[row])-1):
                X = a1_points[row][elem][0]
                Y = a1_points[row][elem][1]
                X_compare = 0
                try:
                    X_compare = a1_points[row][elem+1][0]
                except:
                    X_compare = -1
                found_point = 0
                for row_next in range(row+1, rows):
                    for i in range(0, len(a1_points[row_next])):
                        X_test = a1_points[row_next][i][0]
                        if (X_test < X+20) and (X_test > X-20):
                            try:
                                Y_right = a1_points[row_next][i+1][1]
                                X_right = a1_points[row_next][i+1][0]
                                found_point = 1
                            except:
                                continue
                            break
                    if found_point == 1:
                        break
                if found_point == 1:
                    if X_compare < X_right:
                        X_max = X_right
                    else:
                        X_max = X_compare
                    coord.append([[X,Y],[X_max,Y_right]])
    return coord

def prepare_image(img_name, denoise):
    angle_flt = 0
    angles_float = []
    try:
        rgb = cv2.imread(img_name, 1)
    except:
        print("\nCan't open file:", img_name)
    if denoise == 1:
        print("\033[94m" + "      page "+str(curent_page+1)+"/"+str(total_page)+":" + "\033[0m"+"\033[93m"+" denoising ..."+"\033[0m", end=' ', flush=True)
        # parament N3 == 5. This is a kernel, try change:
        rgb = cv2.fastNlMeansDenoisingColored(rgb, None, 5, 20, 7, 21)
        print("\033[94m"+"[Ok]"+ "\033[0m")
    bar = pb.Bar("\033[94m" + "      page "+str(curent_page+1)+"/"+str(total_page)+":" + "\033[0m"+"\033[93m"+" prepare image ..."+"\033[0m", fill='#', max=3, suffix='%(percent)d%%')
    gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
    binary_edges = cv2.Canny(binary, 100, 100, apertureSize=3, L2gradient=True)
    lines = cv2.HoughLinesP(binary_edges, 1,  math.pi/180.0, 100, minLineLength=100, maxLineGap=5)
    bar.next()
    if type(lines) == np.ndarray:
        for i in range (0, len(lines)):
            for x1,y1,x2,y2 in lines[i]:
                if (x2-x1) != 0:
                    angle = np.rad2deg(np.arctan((y2-y1)/(x2-x1)))
                    angles_float.append(angle)
                    cv2.line(rgb,(x1,y1), (x2,y2), (255,0,0), 3)
        if len(angles_float) > 1:
            mas = []
            mas.append([angles_float[0],1])
            for i in range(1, len(angles_float)):
                flag = 0
                for j in range(0, len(mas)):
                    if mas[j][0] == angles_float[i]:
                        mas[j][1] = mas[j][1] + 1
                        flag = 1
                        break
                if flag == 0:
                    mas.append([angles_float[i],1])
            maxx = mas[0][1]
            angle_flt = mas[0][0]
            for i in range(1, len(mas)):
                if mas[i][1] > maxx:
                    maxx = mas[i][1]
                    angle_flt = mas[i][0]
    bar.next()
    if cv2.countNonZero(binary) != 0:
        if angle_flt != 0:
            rows, cols = binary.shape[:2]
            x1,y1 = tuple(np.array(binary.shape[1::-1])/2)
            if abs(angle_flt) < 45:
                if cols > rows:
                    a = x1
                    b = y1
                else:
                    a = y1
                    b = x1
                c = cols
                d = rows
            else:
                if angle_flt > 0:
                    a = b = x1
                if angle_flt < 0:
                    a = b = y1
                c = rows
                d = cols
            rotate_matr = cv2.getRotationMatrix2D((int(a),int(b)), angle_flt, 1.0)
            binary = cv2.warpAffine(binary, rotate_matr, (int(c),int(d)))
    bar.next()
    return binary

def rotate_image(binary):
    bar = pb.Bar("\033[94m" + "      page "+str(curent_page+1)+"/"+str(total_page)+":" + "\033[0m"+"\033[93m"+" rotation check ..."+"\033[0m", fill='#', max=4, suffix='%(percent)d%%')
    x = y = 0
    kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT,(30,10))
    dilated_1 = cv2.dilate(binary, kernel_1, iterations=1)
    contours, hierarchy = cv2.findContours(dilated_1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    bar.next()
    for contour in contours:
        [x_coord, y_coord, w, h] = cv2.boundingRect(contour)
        if w < 100 or h < 50:
            continue 
        else:
            if w > h:
                x = x + 1
            else:
                y = y + 1
    if y > x:
        # This is 90 or 270:
        rows, cols = binary.shape[:2]
        x1,y1 = tuple(np.array(binary.shape[1::-1])/2)
        rotate_matr = cv2.getRotationMatrix2D((int(x1),int(x1)), 90, 1.0)
        binary = cv2.warpAffine(binary, rotate_matr, (int(rows),int(cols)))
    bar.next()
    try:
        osd = pt.image_to_osd(binary)
        angle_pt = re.search('(?<=Rotate: )\d+', osd).group(0)
    except:
        angle_pt = 0
    bar.next()
    if int(angle_pt) == 180:
        rows, cols = binary.shape[:2]
        x1,y1 = tuple(np.array(binary.shape[1::-1])/2)
        rotate_matr = cv2.getRotationMatrix2D((int(x1),int(y1)), int(angle_pt), 1.0)
        binary = cv2.warpAffine(binary, rotate_matr, (int(cols),int(rows)))
    bar.next()
    return binary

def recognize_image(binary, zrazok):
    rows, cols = binary.shape[:2]
    found_templ = 0
    arr_cont = []
    coord_of_cells = locate_table_struct(binary)
    if len(coord_of_cells) > 2:
        bar = pb.Bar("\033[94m" + "      page "+str(curent_page+1)+"/"+str(total_page)+":" + "\033[0m"+"\033[93m"+" table processing ..."+"\033[0m", fill='#', max=len(coord_of_cells), suffix='%(percent)d%%')
        rows, cols = binary.shape[:2]
        for i in range(0, len(coord_of_cells)):
            x =  coord_of_cells[i][0][0]
            y =  coord_of_cells[i][0][1]
            x1 = coord_of_cells[i][1][0]
            y1 = coord_of_cells[i][1][1]
            if (x1-x)>40 and (y1-y)>40:
                try:
                    crop_cell = binary[y:y1,x:x1]
                    txt = pt.image_to_string(crop_cell, lang="ukr+eng")
                    r_string = utl.normolize_string(txt)
                    poz = (r_string.upper()).find(zrazok.upper())
                    if poz != -1:
                        found_templ = 1
                        break
                except:
                    pass
            bar.next()
    if found_templ == 0:
        kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT,(55,15))
        dilated_1 = cv2.dilate(binary, kernel_1, iterations=1)
        contours, hierarchy = cv2.findContours(dilated_1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            [x_coord, y_coord, w, h] = cv2.boundingRect(contour)
            if w < 200 or h < 50:
                continue 
            else:
                if x_coord < 80 and y_coord < 80 and ((x_coord+w) >= (cols-80)) and ((y_coord+h) >= (rows-80)):
                    pass
                else:
                    arr_cont.append([x_coord, y_coord, x_coord+w, y_coord+h])
        bar = pb.Bar("\033[94m" + "      page "+str(curent_page+1)+"/"+str(total_page)+":" + "\033[0m"+"\033[93m"+" recognition and search ..."+"\033[0m", fill='#', max=len(arr_cont), suffix='%(percent)d%%')
        for i in range(0, len(arr_cont)):
            if not contour_content_table(arr_cont[i], coord_of_cells):
                try:
                    crop_contour = binary[arr_cont[i][1]:arr_cont[i][3], arr_cont[i][0]:arr_cont[i][2]]
                    txt = pt.image_to_string(crop_contour, lang="ukr+eng")
                    r_string = utl.normolize_string(txt)
                    poz = (r_string.upper()).find(zrazok.upper()) 
                    if poz != -1:
                        found_templ = 1
                        break
                except:
                    pass
            bar.next()
    bar.finish()
    return found_templ

def contour_content_table(contour, coord_of_cells):
    table_found = found_top_x = found_top_y = found_down_x = found_down_y = 0
    top_x  = contour[0]
    top_y  = contour[1]
    down_x = contour[2]
    down_y = contour[3]

    while top_x < down_x:
        for i in range(0, len(coord_of_cells)):
            if coord_of_cells[i][0][0] == top_x:
                found_top_x = top_x
                break
        if found_top_x:
            break
        else:
            top_x = top_x + 1
    if found_top_x:
        while top_y < down_y:
            for i in range(0, len(coord_of_cells)):
                if (coord_of_cells[i][0][1] == top_y) and (coord_of_cells[i][0][0] == found_top_x):
                    found_top_y = top_y
                    break
            if found_top_y:
                break
            else:
                top_y = top_y + 1
        if found_top_y:
            while down_x > contour[0]:
                for i in range(0, len(coord_of_cells)):
                    if coord_of_cells[i][1][0] == down_x:
                        found_down_x = down_x
                        break
                if found_down_x:
                    break
                else:
                    down_x = down_x - 1
            if found_down_x:
                while down_y > contour[1]:
                    for i in range(0, len(coord_of_cells)):
                        if (coord_of_cells[i][1][1] == down_y) and (coord_of_cells[i][1][0] == found_down_x):
                            found_down_y = down_y
                            break
                    if found_down_y:
                        table_found = 1
                        break
                    else:
                        down_y = down_y - 1
    return table_found

