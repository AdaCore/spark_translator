#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "--# own" annotations.
def Convert_Own(lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import Package_Type, Place_Converted_Line

    add_comma                   = 0
    add_with                    = 0
    group_converted_annotations = 1

    #Creating list of rows introducing "--# own" annotations.
    own_lines = []
    for line in range(len(lines)):
        if re.search("^ *--" + spark_symbol + " own ", lines[line], re.I):
            own_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (own_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        #Remove the ": Type" part.
        without_columns = re.sub(" *: *[^ ;,]*", "", lines[line])
        #Change all ';' into ',' except for the very last one.
        without_columns = re.sub(";", ",", without_columns)
        without_columns = re.sub(",$", ";", without_columns)

        start, end  = without_columns.split("--" + spark_symbol + " own ", 1)
        words = end.split()

        if not Package_Type (lines, line):
            #Processing "--# own" in package spec.
            start = start + "   with Abstract_State => "

            #If we have more than 2 abstract state elemenents,
            #then we need to put an opening parenthesis at the beginning.
            if len(words) > 2 or \
            (len(words) == 2 and not ("in" in words or "out" in words)):
                start = start + "("

            word = 0
            while word < len(words):
                if words[word] == "in":
                    #Found an "in".
                    if ";" in words[word + 1] or ";" in words[word + 2]:
                        start = start + "(" + words[word + 1].replace(";", "")\
                        + " with External => Async_Writers)"
                    else:
                        start = start + "(" + words[word + 1].replace(",", "")\
                        + " with External => Async_Writers),"
                        if word != len(words) - 2:
                            start = start + " "
                    word = word + 2
                elif words[word] == "out":
                    #Found an "out".
                    if ";" in words[word + 1] or ";" in words[word + 2]:
                        start = start + "(" + words[word + 1].replace(";", "")\
                        + " with External => Async_Readers)"
                    else:
                        start = start + "(" + words[word + 1].replace(",", "")\
                        + " with External => Async_Readers),"
                        if word != len(words) - 2:
                            start = start + " "
                    word = word + 2
                else:
                    #Found some other word. So we just append the word and
                    #remove the ';' if there is one.
                    if ";" in words[word]:
                        start = start + words[word].replace(";", "")
                    else:
                        start = start + words[word]
                        if word != len(words) - 1:
                            start = start + " "
                    word = word + 1
            #If we have more than 2 abstract state elemenents,
            #then we need to put a closing parenthesis at the end.
            if len(words) > 2 or \
            (len(words) == 2 and not ("in" in words or "out" in words)):
                 start = start + ")"
        else:
            #Processing "--# own" in package body.
            start = start + "   with Refined_State => ("

            word = 0
            at_left_handside = 1
            while word < len(words):
                if at_left_handside:
                    start = start + words[word] + " => "
                    at_left_handside = 0
                    more_than_one_constituents = 0
                    word = word + 2
                else:
                    if words[word] in ["in", "out"]:
                        #Found an "in" or an "out". Skipping one word.
                        word = word + 1

                    #Found some other word. So we just append the word and
                    #remove the ';' if there is one.
                    if "," in words[word]:
                        #There are more constituents to come.
                        if not more_than_one_constituents:
                            start = start + "("
                            more_than_one_constituents = 1
                        start = start + words[word] + " "
                    elif "&" in words[word]:
                        #Final constituent of this refined state.
                        start = start + words[word].replace("&", "")
                        if more_than_one_constituents:
                            start = start + ")"
                        at_left_handside = 1
                        start = start + ", "
                    elif ";" in words[word]:
                        #Final constituent of the annotation.
                        start = start + words[word].replace(";", "")
                        if more_than_one_constituents:
                            start = start + ")"
                        at_left_handside = 1
                    else:
                        start = start + words[word]
                    word = word + 1
            #Closing the first parenthesis that we added.
            start = start + ")"

        lines = Place_Converted_Line(lines, line, start, original_line, \
                                     add_comma, add_with, \
                                     group_converted_annotations)

    return lines
