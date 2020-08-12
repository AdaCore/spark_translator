#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited


#Returns True if this corresponds to the special assert in the middle
#of the loop head, just before the loop keyword.
def Special_Assert_Before_Loop(lines, line):
    import re
    from Utilities import Find_Previous_Ada_Line, Find_Next_Ada_Line

    prev_line = Find_Previous_Ada_Line(lines, line)
    prev_prev_line = Find_Previous_Ada_Line(lines, prev_line)
    next_line = Find_Next_Ada_Line(lines, line)

    #We loop for the start of the loop on the two previous Ada lines.
    #This is a heuristic...
    return re.match(" *loop( +|$)", lines[next_line], re.I) and \
        (re.match(" *(for|while) +", lines[prev_line], re.I) or \
         re.match(" *(for|while) +", lines[prev_prev_line], re.I))


#Returns 1 if the line is inside a loop and 0 otherwise.
#Takes as a parameter a list of lines and the number of
#the line that we are interested in.
def In_Loop(lines, line):
    import re
    from Utilities import Find_Previous_Ada_Line

    #Handle special case of assert annotation just before the loop keyword.
    if Special_Assert_Before_Loop(lines, line):
        return 1

    counter = 0

    prev_line = Find_Previous_Ada_Line(lines, line)
    while not re.search("^ *function *", lines[prev_line], re.I) and \
    not re.search("^ *procedure *", lines[prev_line], re.I) and \
    not re.search("^ *(private *)?package *", lines[prev_line], re.I):
        if re.search("--", lines[prev_line]):
            #There are comments in the previous line.
            no_comments, discard = lines[prev_line].split("--", 1)
        else:
            #There are NO comments in the previous line.
            no_comments = lines[prev_line]

        if re.search("end +loop", no_comments, re.I):
            counter = counter - 1
        elif re.search(" loop ", no_comments, re.I) or \
        re.search(" loop$", no_comments, re.I) or \
        re.search("\)loop ", no_comments, re.I) or \
        re.search("\)loop$", no_comments, re.I):
            counter = counter + 1
            if counter > 0:
                #If counter becomes greater than 0, then we are inside a loop.
                return 1

        prev_line = Find_Previous_Ada_Line(lines, prev_line)

    #If we reach this point, then we are NOT inside a loop.
    return 0


#Converts assertions that are located in between the "while" and the "loop"
#keywords of a loop. For example:
#  while cond
#    --# assert inv;
#  loop
#           ||
#           \/
#  loop
#    pragma Loop_Invariant (Inv);
#    exit when not (cond);
#All assertions that are editted by this function must be excluded from any
#subsequent convertion. The exclude_while_lines list contains those lines.
def Convert_Squized_Assertions (lines, exclude_while_lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import Find_Next_Line, Find_Previous_Ada_Line, \
                          Convert_And_Or, Convert_Equivalents, \
                          Convert_Implies, Convert_Tildas, Package_Type, \
                          Insert_After, Place_Converted_Line

    def Loop_In_Line (line):
        code_part, comments_delim, comments_part = line.partition("--")

        if re.search (" loop ", code_part, re.I) or \
        re.search (" loop$", code_part, re.I) or \
        re.search ("\)loop ", code_part, re.I) or \
        re.search ("\)loop$", code_part, re.I):
            return True

        return False

    #Creating list that contains lines that introduce "while" loops.
    while_lines = []
    for line in range(len(lines)):
        if re.search("^ *while *$", lines[line], re.I) or \
        re.search("^ *while ", lines[line], re.I) or \
        re.search("^ *while\(", lines[line], re.I):
            while_lines.append(line)

    #Iterate over "while" loops and convert squized assertions.
    for line in reversed (while_lines):

        #Figure out if this while loop has a squized assertion.
        has_squized_assertion = False
        current = line
        while not Loop_In_Line (lines[current]):
            if re.search("--" + spark_symbol + " * assert", \
                         lines[current], re.I):
                #Found "--# assert" in between "while" and "loop".
                has_squized_assertion = True
                assertion_line = current

            current = Find_Next_Line (lines, current)

        #Proceed to the next while loop if there is no squized assertion here.
        if not has_squized_assertion:
            continue

        #Variable current now holds the line where "loop" was found.
        loop_line = current

        #We have to move all comments after the loop_line while preserving
        #their order.
        indent, discard = lines[loop_line].split("loop", 1)
        for l in reversed (range (line, loop_line + 1)):
            if "--" in lines[l] and \
            "--" + spark_symbol not in lines[l]:
                a, b = lines[l].split("--", 1)
                lines[l] = re.sub(" *$", "", a)
                lines = Insert_After(lines, \
                                     indent + "   " + "--" + b, \
                                     loop_line)

        #Put all conditions of the while loop on a single line.
        last_cond_line = Find_Previous_Ada_Line (lines, assertion_line)
        countdown = last_cond_line - line
        while countdown > 0:
            lines[line] = lines[line] + \
                          re.sub(" +", " ", \
                          lines[line + 1])
            del lines[line + 1]
            countdown = countdown - 1

        #If a line is left empty after removing the comment, then
        #delete the line altogether.
        for l in reversed (range (line, loop_line + 1)):
            if re.search ("^ *$", lines[l]):
                del lines[l]

        #Copy the condition and make a backup of the original assertion.
        condition = re.sub ("^ *while *", "", lines[line], re.I)
        assertion_line = Find_Next_Line(lines, line)
        assertion = lines[assertion_line]
        loop_line = Find_Next_Line(lines, assertion_line)

        #Edit the invariant
        invariant = re.sub ("^ *--" + spark_symbol + " *assert *", "",
                            assertion, re.I)
        #Convert implies ("->") in this line.
        invariant = Convert_Implies(invariant)
        #Convert equivalents ("<->") in this line.
        invariant = Convert_Equivalents(invariant)
        #Convert tildas ("~").
        invariant = Convert_Tildas(invariant)
        #Convert "%" into "'Loop_Entry".
        invariant = invariant.replace("%", "'Loop_Entry");
        invariant = re.sub(";*$", "", invariant)

        #Change "while cond" into "loop".
        lines[line] = re.sub("while.*$", "loop", lines[line], re.I)
        #Change the "loop" into "   exit when not (cond);".
        lines[loop_line] = re.sub("loop", "   exit when not ("  + \
                                  condition + ");", lines[loop_line], re.I)
        #Convert the assertion line.
        add_comma                   = 0
        add_with                    = 0
        group_converted_annotations = 0

        editted_line = re.sub("--" + spark_symbol + " *assert.*$", \
                              " pragma Loop_Invariant (" + invariant + ");",\
                              lines[assertion_line], re.I)
        lines = Place_Converted_Line(lines, assertion_line, editted_line, \
                                     lines[assertion_line], add_comma, \
                                     add_with, group_converted_annotations)

        #Add line to the list of lines that must be excluded from further
        #convertion.
        exclude_while_lines.append(assertion_line)

    return lines


#Converts "--# assert" annotations. It calls Convert_Squized_Assertion first.
def Convert_Assert (lines):
    import re
    from conv_conf import spark_symbol, discard_assert_and_cut_true, \
                          retain_original_annotations
    from Utilities import Convert_And_Or, Convert_Equivalents, \
                          Convert_Implies, Convert_Tildas, Package_Type, \
                          Place_Converted_Line, Find_Next_Ada_Line

    #Convert squized assertions before doing anything else.
    exclude_while_lines = []
    lines = Convert_Squized_Assertions (lines, exclude_while_lines)

    add_comma                   = 0
    add_with                    = 0
    group_converted_annotations = 0

    #Creating list that contains lines that introduce "--# assert" annotations.
    assert_lines = []
    for line in range(len(lines)):
        if (line not in exclude_while_lines) and \
        re.search("^ *--" + spark_symbol + " assert ", lines[line], re.I):
            assert_lines.append(line)

    #Iterating through the list and converting the annotations.
    for line in reversed (assert_lines):
        #Store the original line in case retain_original_annotations is set.
        original_line = lines[line]

        #Deal specially with annotations on base type of signed integer types.
        #These cannot be mimicked as annotations in SPARK 2014. Instead the type
        #definition has to be modified. As we'd rather not modify the code, leave
        #it as it is and remove the annotation.
        m = re.search("(\w+'base) is (\w+)", original_line, re.I)
        if m:
            if not retain_original_annotations:
                del lines[line]
            continue

        #Convert implies ("->") in this line.
        lines[line] = Convert_Implies(lines[line])
        #Convert equivalents ("<->") in this line.
        lines[line] = Convert_Equivalents(lines[line])
        #Convert tildas ("~").
        lines[line] = Convert_Tildas(lines[line])
        #Convert "%" into "'Loop_Entry".
        lines[line] = lines[line].replace("%", "'Loop_Entry");

        if In_Loop(lines, line):
            newline = re.sub("--" +  spark_symbol + " *assert *", \
                             "pragma Loop_Invariant (", lines[line], re.I)
            if Special_Assert_Before_Loop(lines, line):
                next_line = Find_Next_Ada_Line(lines, line)
                lines[line] = lines[next_line]
                lines[next_line] = newline
                lines[next_line] = re.sub(";$", ");", lines[next_line])
            else:
                #"--# assert" is inside a loop.
                lines[line] = newline
                lines[line] = re.sub(";$", ");", lines[line])
        else:
            #"--# assert" is NOT inside a loop.
            if discard_assert_and_cut_true and \
               re.search("assert +true *;", original_line, re.I):
                del lines[line]

            lines[line] = re.sub("--" +  spark_symbol + " *assert *", \
                                 "pragma Assert_And_Cut (", lines[line], re.I)
            lines[line] = re.sub(";$", ");", lines[line])

        #Convert "or" into "or else" and "and" into "and then".
        lines[line] = Convert_And_Or(lines[line])

        lines = Place_Converted_Line(lines, line, lines[line], original_line, \
                                     add_comma, add_with, \
                                     group_converted_annotations)

    return lines
