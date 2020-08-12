#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# initializes" annotations.
def Convert_Initializes(lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import First_Aspect, Package_Type, \
                          Find_Previous_Ada_Line, Place_Converted_Line

    group_converted_annotations = 1

    #Creating a list that contains the rows that introduce "--# initializes"
    #annotations.
    initializes_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " initializes ", \
                     lines[line], re.I):
            initializes_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (initializes_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        add_comma = 0 #Initialize add_comma.
        add_with  = 0 #Initialize add_with.

        start, end = lines[line].split("--" + spark_symbol + " initializes ", 1)
        words = end.split()
        start = start + "        Initializes    => "

        if First_Aspect (lines, line):
            #If this is the first aspect that we come across, then we:
            #  1) note that we have to prepend a "with".
            add_with = 1
        else:
            #If this is NOT the first aspect we come across, then we:
            #  1) note that we have to add a ',' to the previous aspect.
            add_comma = 1

        #If we have more than 1 element that is being initialized,
        #then we need to put an opening parenthesis at the beginning.
        if len(words) > 1 :
            start = start + "("

        word = 0
        while word < len(words):
            if ";" in words[word]:
                start = start + words[word].replace(";", "")
                if word != len(words) - 1:
                    start = start + " "
                word = word + 1
            else:
                start = start + words[word]
                if word != len(words) - 1:
                    start = start + " "
                word = word + 1

        #If we have more than 1 element that is being initialized,
        #then we need to put a closing parenthesis at the end.
        if len(words) > 1:
            start = start + ")"

        lines = Place_Converted_Line(lines, line, start, original_line, \
                                     add_comma, add_with, \
                                     group_converted_annotations)

    return lines
