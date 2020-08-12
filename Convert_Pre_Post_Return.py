#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# pre", "--# post" and "--# return" annotations.
def Convert_Pre_Post_Return(lines, subprograms_pre, subprograms_post, \
                            subprograms_return, file_name):
    import re
    from conv_conf import spark_symbol, discard_refined_annotations, \
                          retain_original_annotations
    from Utilities import In_Spec, Convert_And_Or, Convert_Equivalents, \
                          Convert_Implies, Convert_Tildas, \
                          Find_Previous_Ada_Line, First_Aspect, \
                          Pre_Process_Operators, Subprogram_Name, \
                          Place_Converted_Line, Package_Type


    group_converted_annotations = 1

    #Start of processing of "--# pre" annotations.
    #Creating a list that contains rows that introduce "--# pre" annotations.
    pre_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " pre ", lines[line], re.I):
            pre_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (pre_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        add_comma = 0 #Initialize add_comma.
        add_with  = 0 #Initialize add_with.

        #Convert implies ("->") in this line.
        lines[line] = Convert_Implies(lines[line])
        #Convert equivalents ("<->") in this line.
        lines[line] = Convert_Equivalents(lines[line])
        #Convert tildas (it also proceses "[" and "]")
        lines[line] = Convert_Tildas(lines[line])

        start, end = lines[line].split("--" + spark_symbol + " pre ", 1)
        key = (file_name + Subprogram_Name (lines, line)).lower()
        if key not in subprograms_pre:
            #Adding Subprogram_Name to the list.
            subprograms_pre.append(key)
            #Processing "--# pre" in subroutine's spec.
            if First_Aspect(lines, line):
                #If "--# pre" is the first aspect of the procedure, then we:
                #  1) remove the ';' from the procedure line.
                #  2) note that we have to prepend a "with".
                previous_line = Find_Previous_Ada_Line(lines, line)
                lines[previous_line] = re.sub(";$", "", lines[previous_line])
                add_with = 1
            else:
                #There is another aspect before the "--# pre" so we:
                #  1) note that we need to add a ',' to the previous aspect.
                add_comma = 1
            start = start + "        Pre     => " + end

        else:
            #Processing "--# pre" in package body.
            #There is no refined precondition, discard this annotation.
            del lines[line]
            continue

        lines[line] = re.sub("; *$", "", start)

        #Convert "or" into "or else" and "and" into "and then".
        lines[line] = Convert_And_Or(lines[line])

        #Annotations at package spec need to have a ';' in the end.
        if In_Spec (lines, line):
            #Processing "--# global" in procedure's spec.
            lines[line] = lines[line] + ";"

        lines = Place_Converted_Line(lines, line, lines[line], original_line,\
        add_comma, add_with, group_converted_annotations, True)
    #End of processing of "--# pre" annotations.



    #Start of processing of "--# post" annotations.
    #Creating a list that contains rows that introduce "--# post" annotations.
    post_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " post ", lines[line], re.I):
            post_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (post_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        add_comma = 0 #Initialize add_comma.
        add_with  = 0 #Initialize add_with.

        #Convert implies ("->") in this line.
        lines[line] = Convert_Implies(lines[line])
        #Convert equivalents ("<->") in this line.
        lines[line] = Convert_Equivalents(lines[line])
        #Convert tildas ("~").
        lines[line] = Convert_Tildas (lines[line])

        start, end = lines[line].split("--" + spark_symbol + " post ", 1)

        key = (file_name + Subprogram_Name (lines, line)).lower()
        if key not in subprograms_post:
            #Adding Subprogram_Name to the list.
            subprograms_post.append(key)
            #Processing "--# post" in subroutine's spec.
            if First_Aspect(lines, line):
                #If "--# post" is the first aspect of the procedure, then we:
                #  1) remove the ";" from the procedure line.
                #  2) note that we have to prepend a "with".
                previous_line = Find_Previous_Ada_Line(lines, line)
                lines[previous_line] = re.sub("; *$", "", lines[previous_line])
                add_with = 1
            else:
                #There is another aspect before the "--# post" so we:
                #  1) note that we need to add a ',' to the previous aspect.
                add_comma = 1
            start = start + "        Post    => " + end
        else:
            #Processing "--# post" in package body.
            if First_Aspect(lines, line):
                #If "--# post" is the first aspect of the procedure, then we:
                #  1) note that we have to prepend a "with".
                add_with = 1
            else:
                #There is another aspect before the "--# post" so we:
                #  1) note that we need to add a ',' to the previous aspect.
                add_comma = 1

            if discard_refined_annotations:
                if not retain_original_annotations:
                    del lines[line]
                continue

            start = start + "        Refined_Post    => " + end

        lines[line] = re.sub("; *$", "", start)

        #Convert "or" into "or else" and "and" into "and then".
        lines[line] = Convert_And_Or(lines[line])

        #Annotations at package spec need to have a ';' in the end.
        if In_Spec (lines, line):
            #Processing "--# global" in procedure's spec.
            lines[line] = lines[line] + ";"

        lines = Place_Converted_Line(lines, line, lines[line], original_line,\
        add_comma, add_with, group_converted_annotations, True)
    #End of processing of "--# post" annotations.



    #Start of processing of "--# return" annotations.
    #Creating a list that contains rows that introduce "--# return" annotations.
    return_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " return ", lines[line], re.I):
            return_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (return_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        add_comma = 0 #Initialize add_comma.
        add_with  = 0 #Initialize add_with.

        #Convert implies ("->") in this line.
        lines[line] = Convert_Implies(lines[line])
        #Convert equivalents ("<->") in this line.
        lines[line] = Convert_Equivalents(lines[line])
        #Convert tildas ("~").
        lines[line] = Convert_Tildas (lines[line])
        #Pre processing the line (mainly putting spaces around parentheses).
        lines[line] = Pre_Process_Operators(lines[line])

        #Work out the name of the function followed by 'Result.
        name_tick_result = Subprogram_Name (lines, line) + "'Result"

        start, end = lines[line].split("--" + spark_symbol + " return ", 1)
        words = end.split()

        key = (file_name + Subprogram_Name (lines, line)).lower()
        if key not in subprograms_return:
            #Adding Subprogram_Name to the list.
            subprograms_return.append(key)
            #Processing "--# return" in subroutine's spec.
            if First_Aspect(lines, line):
                #If "--# return" is the first aspect of the function, then we:
                #  1) remove the ';' from the function line.
                #  2) note that we have to prepend a "with".
                previous_line = Find_Previous_Ada_Line(lines, line)
                lines[previous_line] = re.sub("; *$", "", lines[previous_line])
                add_with = 1
            else:
                #There is another aspect before the "--# return" so we:
                #  1) note that we need to add a ',' to the previous aspect.
                add_comma = 1
            start = start + "        Post    => "

            #Checking if "--# return" annotation introduces a result variable.
            if len(words) > 1:
                if words[1] == "=>":
                    words = end.split()
                    for i in range(2, len(words) - 1):
                        if words[i] == words[0]:
                            start = start + name_tick_result + " "
                        elif re.search("^" + words[0], words[i]) \
                        and not re.search("^" + words[0] + "[a-zA-Z0-9]", \
                        words[i]):
                            start = start + re.sub("^" + words[0], \
                            name_tick_result, words[i])  + " "
                        else:
                            start = start + words[i] + " "
                    start = start + words[len(words) - 1]
                else:
                    start = start + name_tick_result + " = " + end
            else:
                start = start + name_tick_result + " = " + end
        else:
            #Processing "--# return" in package body.
            if First_Aspect(lines, line):
                #If "--# return" is the first aspect of the function, then we:
                #  1) note that we have to prepend a "with".
                add_with = 1
            else:
                #There is another aspect before the "--# return" so we:
                #  1) note that we need to add a ',' to the previous aspect.
                add_comma = 1
            start = start + "        Refined_Post    => "

            #Checking if "--# return" annotation introduces a result variable.
            if words[1] == "=>":
                words = end.split()
                for i in range(2, len(words) - 1):
                    if words[i] == words[0]:
                        start = start + name_tick_result + " "
                    elif re.search("^" + words[0], words[i]) \
                    and not re.search("^" + words[0] + "[a-zA-Z0-9]", \
                    words[i]):
                        start = start + re.sub("^" + words[0], \
                        name_tick_result, words[i])  + " "
                    else:
                        start = start + words[i] + " "
                start = start + words[len(words) - 1]
            else:
                start = start + name_tick_result + " = " + end

        lines[line] = re.sub("; *$", "", start)
        lines[line] = re.sub(" *$", "", lines[line])

        #Convert "or" into "or else" and "and" into "and then".
        lines[line] = Convert_And_Or(lines[line])
        #Ensures that no space appears directly before ')'.
        lines[line] = re.sub(" *\)", ")", lines[line])
        #Ensures that no space appears directly after '('.
        lines[line] = re.sub("\( *", "(", lines[line])

        #Annotations at package spec need to have a ';' in the end.
        if In_Spec (lines, line):
            #Processing "--# global" in procedure's spec.
            lines[line] = lines[line] + ";"

        lines = Place_Converted_Line(lines, line, lines[line], original_line,\
                                     add_comma, add_with, \
                                     group_converted_annotations, True)
    #End of processing of "--# return" annotations.

    return lines
