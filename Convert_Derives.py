#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# derives" annotations.
def Convert_Derives (lines, subprograms_derives, file_name):
    import re
    from conv_conf import spark_symbol, discard_refined_annotations, \
                          retain_original_annotations, discard_flow_annotations
    from Utilities import First_Aspect, Find_Previous_Ada_Line, \
                          In_Spec, Subprogram_Name, Place_Converted_Line

    group_converted_annotations = 1

    #Creating a list that contains the rows that introduce "--# derives"
    #annotations.
    derives_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " derives ", lines[line], re.I):
            derives_lines.append(line)
        elif re.search("^ *--" + spark_symbol + " *derives;", \
                       lines[line], re.I):
            #Special case of "--# derives ;".
            derives_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (derives_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        add_comma = 0 #Initialize add_comma.
        add_with  = 0 #Initialize add_with.

        if re.search("^ *--" + spark_symbol + " *derives;", lines[line], re.I):
            #Special case of "--# derives ;".
            key = (file_name + Subprogram_Name (lines, line)).lower()
            if key not in subprograms_derives:
                #Adding Subprogram_Name to the list.
                subprograms_derives.append(key)

                #Keep Derives => null as indication of no effect.

                #Processing "--# derives;" in subroutine's spec.
                if First_Aspect(lines, line):
                    #If "--# derives" is the first annotation of the procedure,
                    #then we:
                    #  1) remove the ';' from the procedure line.
                    #  2) note that we'll have to add a "with".
                    previous_line = Find_Previous_Ada_Line(lines, line)
                    lines[previous_line] = re.sub("; *$", "", \
                                                  lines[previous_line])
                    add_with = 1
                else:
                    #There's another annotation before the "--# derives" so we:
                    #  1) note that we'll have to replace the final ';' of the
                    #     previous line with a ','.
                    add_comma = 1

                lines[line] = re.sub("--" + spark_symbol + " *derives;", \
                                     "        Depends => null", lines[line], \
                                     re.I)

                if In_Spec (lines, line):
                      #Processing "--# derives" in spec.
                      lines[line] = lines[line] + ";"
            else:
                if discard_refined_annotations or discard_flow_annotations:
                    if not retain_original_annotations:
                        del lines[line]
                    continue

                #Processing "--# derives;" in package body.
                if First_Aspect(lines, line):
                    #If "--# derives" is the first annotation of the procedure,
                    #then we:
                    #  1) note that we'll have to add a "with".
                    add_with = 1
                else:
                    #There's another annotation before the "--# derives" so we:
                    #  1) note that we'll have to add a ',' at the end of the
                    #     previous annotation.
                    add_comma = 1

                lines[line] = re.sub("--" + spark_symbol + " *derives;", \
                                     "        Refined_Depends => null", \
                                     lines[line], re.I)

            lines = Place_Converted_Line(lines, line, lines[line], \
                                         original_line, add_comma, add_with, \
                                         group_converted_annotations, True)

            continue

        start, end = lines[line].split("--" + spark_symbol + " derives ", 1)
        words = end.split()

        key = (file_name + Subprogram_Name (lines, line)).lower()
        if key not in subprograms_derives:
            #Adding Subprogram_Name to the list.
            subprograms_derives.append(key)

            #Possibly discard it
            if discard_flow_annotations:
                if not retain_original_annotations:
                    del lines[line]
                continue

            #Processing "--# derives" in subroutine's spec.
            if First_Aspect(lines, line):
                #If "--# derives" is the first annotation of the procedure, we:
                #  1) remove the ';' from the procedure line.
                #  2) note that we'll have to add a "with".
                previous_line = Find_Previous_Ada_Line(lines, line)
                lines[previous_line] = re.sub("; *$", "", lines[previous_line])
                add_with = 1
            else:
                #There's another annotation before the "--# derives" so we:
                #  1) note that we'll have to replace the final ';' of the
                #     previous line with a ','.
                add_comma = 1

            start = start + "        Depends => ("
        else:
            if discard_refined_annotations or discard_flow_annotations:
                if not retain_original_annotations:
                    del lines[line]
                continue

            #Processing "--# derives" in package body.
            if First_Aspect(lines, line):
                #If "--# derives" is the first annotation of the procedure, we:
                #  1) note that we'll have to add a with.
                add_with = 1
            else:
                #There is another annotation before the "--# derives" so we:
                #  1) note that we'll have to add a ',' at the end of the
                #     previous annotation.
                add_comma = 1

            start = start + "        Refined_Depends => ("

        #Compute the initial value of arrow_padding
        depend_padding = 0
        word = 0
        while word < len(words):
            dep_padding = 0
            if words[word + 1] in ("from", "from;", "from&"):
                #Single variable preceeds "from" (no parentheses needed).
                dep_padding = len(words[word] + " => ")

            else:
                #More than one variables preceed "from". We add parentheses.

                while not words[word] in ("from", "from;", "from&"):
                    dep_padding = max(dep_padding, len(words[word]))
                    word = word + 1

                dep_padding += len("() => ")

            #Get past this dependency
            while "&" not in words[word] and \
            ";" not in words[word]:
                word = word + 1

            word = word + 1

            if dep_padding > depend_padding:
                depend_padding = dep_padding

        #Add padding to separate the aspect on multiple lines, while preserving
        #alignment.
        aspect_padding = ' ' * len(start)
        arrow_padding = ' ' * depend_padding
        newline = '\n' #Automatically changed by Python to '\r\n' on windows
        small_padding = newline + aspect_padding
        big_padding = small_padding + arrow_padding + ' '

        word = 0
        while word < len(words):
            depend = ''
            if word != 0:
                start += small_padding
            if words[word + 1] in ("from", "from;", "from&"):
                #Single variable preceeds "from" (no parentheses needed).
                depend += words[word]
                depend += ' ' * (len(arrow_padding) - len (words[word]) - len(" => "))
                depend += " =>"

                if words[word + 1] == "from;":
                    depend += " null"
                    word = word + 2
                    start += depend
                    continue
                elif words[word + 1] == "from&":
                    depend += " null, "
                    word = word + 2
                    start += depend
                    continue

                word = word + 2

                if "*" in words[word]:
                    depend += "+"
                else:
                    depend += " "

                added_parentheses = 0

                if "&" in words[word]:
                    #Only one variable follows "from" (no parentheses needed)
                    depend += words[word].replace("&", ",").replace("*",\
                    "null") + " "
                    word = word + 1
                elif ";" in words[word]:
                    #Only one variable follows "from" and it is the last word
                    #of the line.
                    depend += words[word].replace(";", "").replace("*",\
                    "null")
                    word = word + 1
                else:
                    #More than one variables follow "from".
                    if "*" in words[word]:
                        #First word contains '*'. Checking if second has a ','.
                        if "," in words[word + 1]:
                            #Parentheses needed
                            depend += "("
                            added_parentheses = 1
                        word = word + 1

                        first = True
                        while "&" not in words[word] and \
                        ";" not in words[word]:
                            if not first:
                                depend += big_padding
                            first = False
                            depend += words[word] + " "
                            word = word + 1

                        if "&" in words[word]:
                            if words[word] != "&":
                                if not first:
                                    depend += big_padding
                            if added_parentheses:
                                depend += words[word].replace("&", "") +\
                                ")," + " "
                            else:
                                depend += words[word].replace("&", "") +\
                                "," + " "
                        else:
                            if not first:
                                depend += big_padding
                            if added_parentheses:
                                depend += words[word].replace(";", "") +\
                                ")"
                            else:
                                depend += words[word].replace(";", "")
                    else:
                        #If the first variable is not '*', we add parentheses.
                        depend += "("

                        first = True
                        while "&" not in words[word] and \
                        ";" not in words[word]:
                            if not first:
                                depend += big_padding
                            first = False
                            depend += words[word] + " "
                            word = word + 1

                        if "&" in words[word]:
                            if words[word] != "&":
                                if not first:
                                    depend += big_padding
                            depend += words[word].replace("&", "") + \
                            ")," + " "
                        else:
                            if not first:
                                depend += big_padding
                            depend += words[word].replace(";", "") + ")"

                    word = word + 1
            else:
                #More than one variables preceed "from". We add parentheses.
                depend += "("

                first = True
                while not words[word + 1] in ("from", "from;", "from&"):
                    if not first:
                        depend += small_padding + ' '
                    first = False
                    depend += words[word] + " "
                    word = word + 1

                depend += small_padding + ' '
                depend += words[word] + ")"
                depend += ' ' * (len(arrow_padding) - len (words[word]) - len("() => "))
                depend += " =>"

                if words[word + 1] == "from;":
                    depend += " null"
                    word = word + 2
                    start += depend
                    continue
                elif words[word + 1] == "from&":
                    depend += " null, "
                    word = word + 2
                    start += depend
                    continue

                word = word + 2

                if "*" in words[word]:
                    depend += "+"
                else:
                    depend += " "

                added_parentheses = 0

                if "&" in words[word]:
                    #Only one variable follows "from" (no parentheses needed)
                    depend += words[word].replace("&", ",").replace("*",\
                    "null") + " "
                    word = word + 1
                elif ";" in words[word]:
                    #Only one variable follows "from" and it is the last word
                    #of the line.
                    depend += words[word].replace(";", "").replace("*",\
                    "null")
                    word = word + 1
                else:
                    #More than one variables follow "from".
                    if "*" in words[word]:
                        #First word contains '*'. Checking if second has a ','.
                        if "," in words[word + 1]:
                            #We need parentheses
                            depend += "("
                            added_parentheses = 1
                        word = word + 1

                        first = True
                        while "&" not in words[word] and \
                        ";" not in words[word]:
                            if not first:
                                depend += big_padding
                            first = False
                            depend += words[word] + " "
                            word = word + 1

                        if "&" in words[word]:
                            if words[word] != "&":
                                if not first:
                                    depend += big_padding
                            if added_parentheses:
                                depend += words[word].replace("&", "") +\
                                ")," + " "
                            else:
                                depend += words[word].replace("&", "") +\
                                "," + " "
                        else:
                            if not first:
                                depend += big_padding
                            if added_parentheses:
                                depend += words[word].replace(";", "") +\
                                ")"
                            else:
                                depend += words[word].replace(";", "")
                    else:
                        #If the first variable is not '*', we add parentheses.
                        depend += "("

                        first = True
                        while "&" not in words[word] and ";" not in words[word]:
                            if not first:
                                depend += big_padding
                            first = False
                            depend += words[word] + " "
                            word = word + 1

                        if "&" in words[word]:
                            if words[word] != "&":
                                if not first:
                                    depend += big_padding
                            depend += words[word].replace("&", "") +\
                            ")," + " "
                        else:
                            if not first:
                                depend += big_padding
                            depend += words[word].replace(";", "") + ")"

                    word = word + 1

            start += depend

        #We add the closing parenthesis.
        start = start + ")"

        #"--# derives" annotations in package spec need a ';' at the end.
        if In_Spec (lines, line):
            #Processing "--# derives" in spec.
            start = start + ";"

        lines = Place_Converted_Line(lines, line, start, original_line, \
        add_comma, add_with, group_converted_annotations, True)

    return lines
