#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# global" annotations.
def Convert_Global(lines, subprograms_global, file_name):
    import re
    from conv_conf import spark_symbol, discard_refined_annotations, \
                          retain_original_annotations, discard_flow_annotations
    from Utilities import In_Spec, Find_Previous_Ada_Line, \
                          Subprogram_Name, Place_Converted_Line

    group_converted_annotations = 1

    #Creating a list that contains the rows that introduce "--# global"
    #annotations.
    global_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " global ", lines[line], re.I):
            global_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (global_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        start, end = lines[line].split("--" + spark_symbol + " global ", 1)
        words = end.split()

        #If a procedure has a "--# global", it is always the first annotation.
        key = (file_name + Subprogram_Name (lines, line)).lower()
        if key not in subprograms_global:
            #Adding Subprogram_Name to the list.
            subprograms_global.append(key)
            #Possibly discard it
            if discard_flow_annotations:
                if not retain_original_annotations:
                    del lines[line]
                continue
            #Since we are at the package spec we need to:
            #   1) remove the ';' from the end of the procedure line.
            #   2) introduce the "with".
            previous_line = Find_Previous_Ada_Line(lines, line)
            lines[previous_line] = re.sub("; *$", "", lines[previous_line])
            start = start + "   with Global  => "
        else:
            if discard_refined_annotations or discard_flow_annotations:
                if not retain_original_annotations:
                    del lines[line]
                continue

            #Since we are at the package body we need to:
            #   1) introduce the "with".
            start = start + "   with Refined_Global  => "

        #Add padding to separate the aspect on multiple lines, while preserving
        #alignment.
        aspect_padding = ' ' * len(start)
        mode_padding = ' ' * 11
        newline = '\n' #Automatically changed by Python to '\r\n' on windows
        small_padding = newline + aspect_padding
        def big_padding():
            return small_padding + mode_padding

        #The following 4 lists will hold the moded variables introduced by
        #"--# global".
        in_vars       = []
        out_vars      = []
        in_out_vars   = []
        modeless_vars = []

        word = 0
        while word < len(words):
            if words[word] == "in": #Found an "in".
                if words[word + 1] == "out":
                    #Found an "in out".
                    word = word + 2
                    while ";" not in words[word]:
                        in_out_vars.append(words[word].replace(",", ""))
                        word = word + 1
                    in_out_vars.append(words[word].replace(";", ""))
                    word = word + 1
                else:
                    #Found just an "in".
                    word = word + 1
                    while ";" not in words[word]:
                        in_vars.append(words[word].replace(",", ""))
                        word = word + 1
                    in_vars.append(words[word].replace(";", ""))
                    word = word + 1
            elif words[word] == "out":
                #Found just an "out".
                word = word + 1
                while ";" not in words[word]:
                    out_vars.append(words[word].replace(",", ""))
                    word = word + 1
                out_vars.append(words[word].replace(";", ""))
                word = word + 1
            else:
                #Found a default argument (equivalent to "in" but not
                #explicitly stated).
                while ";" not in words[word]:
                    modeless_vars.append(words[word].replace(",", ""))
                    word = word + 1
                modeless_vars.append(words[word].replace(";", ""))
                word = word + 1

        #Writing modeless variables.
        if len(modeless_vars) == 1:
            #These is a single modeless variable.
            start = start + modeless_vars[0]
        elif len(modeless_vars) > 1:
            #There are many modeless variables.
            start = start + "("
            for modeless_var in range(0, len(modeless_vars) - 1):
                start = start + modeless_vars[modeless_var] + ", "
            start = start + modeless_vars[len(modeless_vars) - 1] + ")"

        #If we have moded global variables then we need an opening parenthesis.
        if len(in_vars) + len(out_vars) + len(in_out_vars) > 0:
            start = start + "("
            mode_padding += ' '

        #Writing in_vars.
        if len(in_vars) == 1:
            #These is a single global in variable.
            start = start + "Input  => " + in_vars[0]
            if len(out_vars) + len(in_out_vars) > 0:
                start = start + ", "
        elif len(in_vars) > 1:
            #There are many global in variables.
            start = start + "Input  => ("
            start = start + in_vars[0] + ", "
            for in_var in range(1, len(in_vars) - 1):
                start = start + big_padding()
                start = start + in_vars[in_var] + ", "
            start = start + big_padding()
            start = start + in_vars[len(in_vars) - 1] + ")"
            if len(out_vars) + len(in_out_vars) > 0:
                start = start + ", "
                start = start + small_padding + ' '

        #Writing out_vars.
        if len(out_vars) == 1:
            #These is a single global out variable.
            start = start + "Output => " + out_vars[0]
            if len(in_out_vars) > 0:
                start = start + ", "
        elif len(out_vars) > 1:
            #There are many global out variables.
            start = start + "Output => ("
            start = start + out_vars[0] + ", "
            for out_var in range(1, len(out_vars) - 1):
                start = start + big_padding()
                start = start + out_vars[out_var] + ", "
            start = start + big_padding()
            start = start + out_vars[len(out_vars) - 1] + ")"
            if len(in_out_vars) > 0:
                start = start + ", "
                start = start + small_padding + ' '

        #Writing in_out_vars.
        if len(in_out_vars) == 1:
            #These is a single global in_out variable.
            start = start + "In_Out => " + in_out_vars[0]
        elif len(in_out_vars) > 1:
            #There are many global in_out variables.
            start = start + "In_Out => ("
            start = start + in_out_vars[0] + ", "
            for in_out_var in range(1, len(in_out_vars) - 1):
                start = start + big_padding()
                start = start + in_out_vars[in_out_var] + ", "
            start = start + big_padding()
            start = start + in_out_vars[len(in_out_vars) - 1] + ")"

        #If we have moded global variables then we need a closing parenthesis.
        if len(in_vars) + len(out_vars) + len(in_out_vars) > 0:
            start = start + ")"

        #"--# global" annotations at package spec need to have a ';' in the
        #end.
        if In_Spec (lines, line):
            #Processing "--# global" in procedure's spec.
            start = start + ";"

        lines = Place_Converted_Line(lines, line, start, original_line, \
        0, 0, group_converted_annotations, True)

    return lines
