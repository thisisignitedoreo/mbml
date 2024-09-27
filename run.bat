@echo off
pyside6-rcc main.qrc -o main_rc.py
pyside6-uic main.ui -o ui.py
python main.py