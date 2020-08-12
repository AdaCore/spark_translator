#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Removes blank lines and lines that just contain spaces.
def Remove_Blank_Lines(lines):
    for line in reversed(range(len(lines))):
        #Strip whitespace. This should leave nothing if line is empty.
        if not lines[line].strip():
             del lines[line]

    return lines
