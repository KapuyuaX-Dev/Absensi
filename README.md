# Absensi Robotic Python App
This project created with python virtual environment

## To use build version
1. clone this github repository
2. run main.exe in Absensi\dist\main

## To activate virtual environment
1. clone this github repository
2. cd Absensi
3. type in powersheel ".\src\Scripts\activate"
4. add your library using pip install requirement.txt

## To build your own executable file
1. clone this github repository
2. cd Absensi
3. type "pyinstaller --noconsole --onedir --add-data "D:/Data Rifqi/ROBOTIK/RISET/project absensi/Absensi/src/Lib/site-packages/customtkinter;customtkinter/" main.py" in powersheel
4. add folder with name "data" in "Absensi\dist\main"