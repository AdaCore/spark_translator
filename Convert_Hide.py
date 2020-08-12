#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# hide" annotations.
def Convert_Hide(lines):
    import re
    from conv_conf import spark_symbol, retain_original_annotations
    from Utilities import Insert_After

    #Creating a list that contains the rows that introduce "--# hide"
    #annotations.
    hide_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " hide *", lines[line], re.I):
            hide_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (hide_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        lines[line] = re.sub("--" + spark_symbol + " hide.*", \
                             "pragma SPARK_Mode (Off);", lines[line], re.I)

        if retain_original_annotations:
            #We keep the original annotation.
            lines = Insert_After(lines, lines[line], line)
            lines[line] = original_line

    return lines
