# OCR-search

Searching for a text in scanned files using OCR.</br>
If the document has a table, then the program determines the structure of the table and recognizes the contents.</br>
The original document (image/PDF) can be rotated to any angle.</br>
The search is also performed in files of other formats, if these files are present in the target directory.</br>
Supported formats: **pdf/png/jpeg/jpg/tif/doc/docx/odt/xls/xlsx/ods/txt**</br>
Works on Windows, Linux 

## Use

The program starts without any parameters. Uses settings from config file.</br>
You need to set at least one parameter in search.conf: the 'search' parameter specifies what to search for.</br>
If you do not specify a search directory, the current directory will be used.

### Prerequisites

##### for Windows10 (Linux):
1. python 3.9 (or later)
2. tesseract-ocr-w64-setup-v5.2.0.20220712.exe</br>
   2.1. PATH environment variable: "D:\Tesseract" (specify the directory selected during installation)</br>
   2.2. Add file with prefered language (ukr.traineddata) to "D:\Tesseract\tessdata"</br>
   (for Linux: apt-get install tesseract-ocr)
3. pip install pytesseract
4. poppler and pdf2image</br>
      4.1. install Poppler (release 22.12.0-0 or later)
        for Windows: <https://github.com/oschwartz10612/poppler-windows/releases></br>
        Extract Poppler to "D:\Poppler\poppler-22.12.0\" (or any other folder) and add PATH:</br>
        "D:\Poppler\poppler-22.12.0\Library\bin"</br>
      4.2. pip install pdf2image
5. pip install filetype
6. for 'XLS/XLSX' file format:</br>
    pip install pandas</br>
    pip install xlrd
7. for 'DOCX' file format:</br>
    pip install docx2python
8. pip install opencv
9. for 'DOC' file format:</br>
    Download and unpack antiword to c:\antiword.</br> 
    Set the PATH and add Environment Variable:</br>
        ANTIWORDHOME = c:\antiword</br>
        PATH = c:\antiword
    (for Linux: apt-get install antiword)
10. pip install progress
11. for 'ods/odt' file format:</br>
    pip install odfpy

### Run
For Windows: to generate exe file:
```
pyinstaller.exe --onefile search.py
search.exe
```
or run:
```
search.py
```

### Example

![example](/screenshot/scrsh.png)


## Versioning
    v3.3

## Author
* **Svitlana Viblaia**


## License

This project is licensed under the MIT License.
