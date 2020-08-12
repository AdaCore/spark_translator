#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# check" annotations into Assert pragmas.
def Convert_Check(lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import Convert_And_Or, Convert_Equivalents, \
                          Convert_Implies, Convert_Tildas, \
                          Place_Converted_Line

    add_comma                   = 0
    add_with                    = 0
    group_converted_annotations = 0

    #Creating a list that contains rows that introduce "--# own" annotations.
    check_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " check ", lines[line], re.I):
            check_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (check_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        #Convert implies ("->") in this line.
        lines[line] = Convert_Implies(lines[line])
        #Convert equivalents ("<->") in this line.
        lines[line] = Convert_Equivalents(lines[line])
        #Convert tildas ("~").
        lines[line] = Convert_Tildas(lines[line])
        #Convert "or" into "or else" and "and" into "and then".
        lines[line] = Convert_And_Or(lines[line])
        #Convert "%" into "'Loop_Entry".
        lines[line] = lines[line].replace("%", "'Loop_Entry");
        #Turning "--# check ... ;" into "pragma Assert ( ... );".
        lines[line] = re.sub("--" + spark_symbol + " check ", \
                             "pragma Assert (", lines[line], re.I)
        lines[line] = re.sub(";$", ");", lines[line])

        lines = Place_Converted_Line(lines, line, lines[line], original_line, \
                                     add_comma, add_with, \
                                     group_converted_annotations)

    return lines
