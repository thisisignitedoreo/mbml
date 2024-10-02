#!/bin/sh

nuitka --onefile --enable-plugin=pyside6 main.py --windows-console-mode=disable

