#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Removes "--# inherit" annotations.
#If the unit is not in set file_with, create a with clause instead.
def Remove_Inherit(lines, file_with):
    import re
    from conv_conf import spark_symbol, retain_original_annotations
    from Utilities import Insert_After

    for line in reversed(range(len(lines))):
        m = re.search("^(?P<blank> *)--" + spark_symbol + " inherit (?P<units>.*);", lines[line], re.I)
        curline = line
        if m:
            blank = m.group('blank')
            units = m.group('units')
            m = re.search("(?P<unit>[\w\.]+)[,; $](?P<units>.*)", units, re.I)

            while m:
                unit = m.group('unit')
                units = m.group('units')
                if retain_original_annotations:
                    if unit.lower() not in file_with:
                        newline = blank + "with " + unit + "; use " + unit + ";"
                        lines = Insert_After(lines, newline, curline)
                        curline += 1
                else:
                    if unit.lower() not in file_with:
                        newline = blank + "with " + unit + "; use " + unit + ";"
                        if curline == line:
                            lines[line] = newline
                        else:
                            lines = Insert_After(lines, newline, curline-1)
                        curline += 1
                m = re.search("(?P<unit>[\w\.]+)[,; $](?P<units>.*)", units, re.I)

            #Delete line if not insertion happened and annotations are not kept.
            if curline == line and not retain_original_annotations:
                del lines[line]

    return lines
