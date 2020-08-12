#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Converts "or" into "or else" and "and" into "and then".
def Convert_And_Or(line):
    import re
    from conv_conf import and_then_or_else

    if and_then_or_else:
        line = re.sub(" +or +", " or else ", line, re.I)
        line = re.sub("^( *)or +", "\1or else ", line, re.I)
        line = re.sub(" +or *$", " or else ", line, re.I)
        line = re.sub(" +and +", " and then ", line, re.I)
        line = re.sub("^( *)and +", "\1and then ", line, re.I)
        line = re.sub(" +and *$", " and then ", line, re.I)

    return line


#Converts a "A <-> B" into equals "(A) = (B)".
def Convert_Equivalents(line):
    import re

    if not re.search("<->", line):
        return line

    line = Pre_Process_Operators(line) #Processing the operators of the line.

    words = line.split()
    word = 0
    add_opening_parenthesis_at = []
    add_closing_parenthesis_at = []
    while word < len(words):
        if words[word] == "<->":
            #Equivalent found.

            #Finding where the leftmost parenthesis has to open.
            distance = 1
            parentheses = 0
            lookback = 2
            while lookback > 0 and parentheses >= 0:
                #Variable bypassed_parentheses becomes '1' if we
                #just bypassed some parentheses.
                bypassed_parentheses = 0 #Initializing "bypassed_parentheses".
                #Bypassing parentheses.
                if parentheses > 0:
                    while parentheses > 0:
                        if words[word - distance] == ")":
                            parentheses = parentheses + 1
                        elif words[word - distance] == "(":
                            parentheses = parentheses - 1
                        distance = distance + 1
                    lookback = lookback - 1
                    bypassed_parentheses = 1

                #Checking the lookback.
                if words[word - distance] == ")":
                    parentheses = parentheses + 1
                elif words[word - distance] == "(":
                    parentheses = parentheses - 1
                elif words[word - distance] in ["not", "abs", "->", "<->"]:
                    #Found "not", "abs", "->" or "<->". We do nothing!
                    #These lines have to remain here! Commenting them out
                    #will allow the if statement to proceed to other
                    #control flows, which we do not want if we stumble upon
                    #one of these words.
                    lookback = lookback
                elif words[word - distance] in ["and", "or", "xor"]:
                    #Found "and", "or" or "xor".
                    lookback = lookback + 1
                elif words[word - distance] in ["+", "-", "*", "/", \
                "**", "=", "/=", "<", ">", ">=", "<=", "mod", "div"]:
                    #Found '+', '-', '*', '/', "**", '=', "/=", '<', '>', ">=",
                    #"<=", "mod", "div".
                    lookback = lookback + 1
                else:
                    #We found a variable, a function or a special word (pre,
                    #post, return, check, assert).
                    if not bypassed_parentheses or \
                    words[word - distance] in ["pre", "post", "return", \
                    "check", "assert", "=>"]:
                        #If we did't just bypass some parentheses or if we
                        #bumped into a special word.
                        lookback = lookback - 1

                distance = distance + 1

            #Adding leftmost opening parenthesis.
            add_opening_parenthesis_at.append(word - distance + 2)
            #Adding closing parenthesis at the end of the previous word.
            add_closing_parenthesis_at.append(word - 1)

            #Finding where the rightmost parenthesis has to close.
            distance = 1
            parentheses = 0
            lookback = 2
            while lookback > 0 and parentheses <= 0:
                #Variable bypassed_parentheses becomes '1' if we
                #just bypassed some parentheses.
                bypassed_parentheses = 0 #Initializing "bypassed_parentheses".
                #Bypassing parentheses.
                if parentheses < 0:
                    while parentheses < 0:
                        if ")" in words[word + distance]:
                            parentheses = parentheses + 1
                        elif "(" in words[word + distance]:
                            parentheses = parentheses - 1
                        distance = distance + 1
                    lookback = lookback - 1
                    bypassed_parentheses = 1

                #Checking the lookback.
                if ")" in words[word + distance]:
                    parentheses = parentheses + 1
                elif "(" in words[word + distance]:
                    parentheses = parentheses - 1
                elif words[word + distance] in ["not", "abs", "->", "<->"]:
                    #Found "not", "abs", "->" or "<->". We do nothing!
                    #These lines have to remain here! Commenting them out
                    #will allow the if statement to proceed to other
                    #control flows, which we do not want if we stumble upon
                    #one of these words.
                    lookback = lookback
                elif words[word + distance] in ["and", "or", "xor"]:
                    #Found "and", "or" or "xor".
                    lookback = lookback + 1
                elif words[word + distance] in ["+", "-", "*", "/", \
                "**", "=", "/=", "<", ">", ">=", "<=", "mod", "div"]:
                    #Found '+', '-', '*', '/', "**", '=', "/=", '<', '>', ">=",
                    #"<=", "mod", "div".
                    lookback = lookback + 1
                elif ";" in words[word + distance]:
                    lookback = lookback - 1
                    distance = distance - 1
                else:
                    #We found a variable, a function or a special word (pre,
                    #post, return, check, assert).
                    if not bypassed_parentheses or \
                    words[word + distance] in ["pre", "post", "return", \
                    "check", "assert", "=>"]:
                        #If we did't just bypass some parentheses or if we
                        #bumped into a special word.
                        lookback = lookback - 1

                distance = distance + 1

            #Adding rightmost closing parenthesis.
            add_closing_parenthesis_at.append(word + distance - 1)
            #Adding opening parenthesis at the beginning of the next word.
            add_opening_parenthesis_at.append(word + 1)


        word = word + 1

    #Adding "("s.
    for i in add_opening_parenthesis_at:
        words[i] = "(" + words[i]
    #Adding ")"s.
    for i in add_closing_parenthesis_at:
        words[i] = words[i] + ")"

    #Adding initial spaces in front of variable "new_line".
    tmp = 0
    new_line = ""
    while tmp < len(line):
        if line[tmp] == " ":
            new_line = new_line + " "
            tmp = tmp + 1
        else:
            break
    #Converting "<->"s to "="s and constructing the output line.
    for i in range(len(words) - 1):
        if words[i] == "<->":
            new_line = new_line + "= "
        else:
            new_line = new_line + words[i] + " "
    new_line = new_line + words[len(words) - 1]

    #Ensures that no space appears directly before ';'.
    new_line = re.sub(" *;", ";", new_line)
    #Ensures that no space appears directly before ')'.
    new_line = re.sub(" *\)", ")", new_line)
    #Ensures that no space appears directly after '('.
    new_line = re.sub("\( *", "(", new_line)

    return new_line


#Converts a line's implies ("->") into "if ... then" statements.
def Convert_Implies(line):
    import re

    if not re.search("->", line):
        return line

    line = Pre_Process_Operators(line) #Processing the operators of the line.

    words = line.split()
    word = 0
    add_if_at = []
    while word < len(words):
        if words[word] == "->":
        #Implies found.
            distance = 1
            parentheses = 0
            lookback = 2
            while lookback > 0 and parentheses >= 0:
                #Variable bypassed_parentheses becomes '1' if we
                #just bypassed some parentheses.
                bypassed_parentheses = 0 #Initializing "bypassed_parentheses".
                #Bypassing parentheses.
                if parentheses > 0:
                    while parentheses > 0:
                        if words[word - distance] == ")":
                            parentheses = parentheses + 1
                        elif words[word - distance] == "(":
                            parentheses = parentheses - 1
                        distance = distance + 1
                    lookback = lookback - 1
                    bypassed_parentheses = 1

                #Checking the lookback.
                if words[word - distance] == ")":
                    parentheses = parentheses + 1
                elif words[word - distance] == "(":
                    parentheses = parentheses - 1
                elif words[word - distance] in ["not", "abs", "->", "<->"]:
                    #Found "not", "abs", "->" or "<->". We do nothing!
                    #These lines have to remain here! Commenting them out
                    #will allow the if statement to proceed to other
                    #control flows, which we do not want if we stumble upon
                    #one of these words.
                    lookback = lookback
                elif words[word - distance] in ["and", "or", "xor"]:
                    #Found "and", "or" or "xor".
                    lookback = lookback + 1
                elif words[word - distance] in ["+", "-", "*", "/", \
                "**", "=", "/=", "<", ">", ">=", "<=", "mod", "div"]:
                    #Found '+', '-', '*', '/', "**", '=', "/=", '<', '>', ">=",
                    #"<=", "mod", "div".
                    lookback = lookback + 1
                else:
                    #We found a variable, a function or a special word (pre,
                    #post, return, check, assert).
                    if not bypassed_parentheses or \
                    words[word - distance] in ["pre", "post", "return", \
                    "check", "assert", "=>"]:
                        #If we did't just bypass some parentheses or if we
                        #bumped into a special word.
                        lookback = lookback - 1

                distance = distance + 1

            add_if_at.append(word - distance + 1)

        word = word + 1

    #Adding "if"s.
    add_if_at.sort(key=int)
    for i in range(len(add_if_at)):
        words = Insert_After(words, "if", add_if_at[i] + i)
    #Adding initial spaces in front of variable "new_line".
    tmp = 0
    new_line = ""
    while tmp < len(line):
        if line[tmp] == " ":
            new_line = new_line + " "
            tmp = tmp + 1
        else:
            break
    #Converting "->"s to "then"s and constructing the output line.
    for i in range(len(words) - 1):
        if words[i] == "->":
            new_line = new_line + "then "
        else:
            new_line = new_line + words[i] + " "
    new_line = new_line + words[len(words) - 1]

    #Ensures that no space appears directly before ';'.
    new_line = re.sub(" *;", ";", new_line)
    #Ensures that no space appears directly before ')'.
    new_line = re.sub(" *\)", ")", new_line)
    #Ensures that no space appears directly after '('.
    new_line = re.sub("\( *", "(", new_line)

    return new_line


#Converts tildas '~' into 'Old.
#It also turns "[...]" into "'Update(...)".
def Convert_Tildas(line):
    import re

    line = re.sub("~ *\[", "'Old'Update (", line)
    line = re.sub("\[", "'Update (", line)
    line = re.sub("]", ")", line)
    if re.search(";$", line):
        line = re.sub(";", ",", line)
        line = re.sub(",$", ";", line)
    else:
        line = re.sub(";", ",", line)
    line = re.sub("~", "'Old", line)
    return line


#Checks if the aspect at line "line" is the first aspect of the corresponding
#subroutine. Returns '1' if it is and '0' if it is not.
def First_Aspect(lines, line):
    import re
    from conv_conf import spark_symbol, retain_original_annotations

    prev_line = line
    while 1:
        prev_line = Find_Previous_Line(lines, prev_line)
        NCP = Get_Non_Comments_Part (lines[prev_line])

        #We only check the non-comments part
        for word in NCP:
            if re.search("^function$", word, re.I) or \
            re.search("^procedure$", word, re.I) or \
            re.search("^package$", word, re.I):
                 return 1

        #We check the entire line.
        if (retain_original_annotations and \
        "--" + spark_symbol in lines[prev_line]):
            return 0

        #We only check the non-comments part
        for word in NCP:
            if (not retain_original_annotations and "=>" in word):
                return 0


#Finds the next non-empty, non-comment line.
def Find_Next_Line(lines, line):
    import re
    from conv_conf import spark_symbol

    next_line = line + 1
    while not lines[next_line].strip() or \
    ( re.search("^ *--", lines[next_line]) and \
    not re.search("^ *--" + spark_symbol, lines[next_line]) ):
        next_line = next_line + 1

    return next_line


#Finds the next ada line.
def Find_Next_Ada_Line(lines, line):
    import re
    from conv_conf import spark_symbol

    next_ada_line = Find_Next_Line (lines, line)
    while re.search("^ *--" + spark_symbol, lines[next_ada_line]):
        next_ada_line = Find_Next_Line(lines, next_ada_line)

    return next_ada_line


#Finds the previous non-empty, non-comment line.
def Find_Previous_Line(lines, line):
    import re
    from conv_conf import spark_symbol

    previous_line = line - 1
    while not lines[previous_line].strip() or \
    ( re.search("^ *--", lines[previous_line]) and \
    not re.search("^ *--" + spark_symbol, lines[previous_line]) ):
        previous_line = previous_line - 1

    return previous_line


#Finds the previous ada line.
def Find_Previous_Ada_Line(lines, line):
    import re
    from conv_conf import spark_symbol

    previous_ada_line = Find_Previous_Line(lines, line)
    while re.search("^ *--" + spark_symbol, lines[previous_ada_line]):
        previous_ada_line = Find_Previous_Line(lines, previous_ada_line)

    return previous_ada_line


#Returns the non-comments part of a line.
def Get_Non_Comments_Part (line):
    if (len(line.split()) > 1) and ("--" in line):
        non_comments_part, dont_care = line.split ("--", 1)
        return non_comments_part.split()

    return line.split()


#Inserts "insert_item" in list "items" after the element at position
#"insert_after_this".
def Insert_After(items, insert_item, insert_after_this):
    result = []
    for item in range(len(items)):
        result.append(items[item])
        if item == insert_after_this:
            result.append(insert_item)
    return result


#Returns 1 if line number "line" lies in the specs of a subroutine and 0 if
#it lies in the body.
def In_Spec(lines, line):
    import re
    from conv_conf import spark_symbol, retain_original_annotations

    if retain_original_annotations:
        #We keep the original annotations so there might be some new
        #aspects following (generated from the conversion of previous
        #annotations).
        annotations_before = 0
        previous_ada_line = Find_Previous_Ada_Line (lines, line)
        previous_line = Find_Previous_Line (lines, line)

        #Calculate how many annotations precede the annotation that
        #is currently being converted.
        while previous_line != previous_ada_line:
            if not re.search ("^ *--" + spark_symbol + " *accept", \
                              lines[previous_line], re.I) and \
            not re.search ("^ *--" + spark_symbol + " *declare", \
                           lines[previous_line], re.I) and \
            not re.search ("^ *--" + spark_symbol + " *inherit", \
                           lines[previous_line], re.I) and \
            not re.search ("^ *--" + spark_symbol + " *main_program", \
                           lines[previous_line], re.I) and \
            not re.search ("^ *--" + spark_symbol + " *type", \
                           lines[previous_line], re.I):
                #Since the above annotations are not converted, we should
                #NOT increase annotations_before if any of them is found.
                annotations_before = annotations_before + 1

            previous_line = Find_Previous_Line (lines, previous_line)

        next_ada_line = Find_Next_Ada_Line (lines, line)

        for I in range (annotations_before):
            next_ada_line = Find_Next_Ada_Line(lines, next_ada_line)
    else:
        next_ada_line = Find_Next_Ada_Line(lines, line)

    if re.match(" *is( |$)", lines[next_ada_line], re.I):
        return 0;
    else:
        return 1;


#Returns the type (spec or body) of the package that encloses the statement
#that lies at line "line". Returns 0 for spec and 1 for body.
def Package_Type(lines, line):
    import re
    from conv_conf import spark_symbol

    prev_line = Find_Previous_Line(lines, line) #Initializing prev_line.
    ended_packages = []                         #Initializing ended_packages.

    while True:
        if re.search("^ *end ", lines[prev_line], re.I):
            words = lines[prev_line].split()
            ended_packages.append(words[1].replace(";", ""))
        elif re.search("^ *package +", lines[prev_line], re.I):
            #Find a line starting with "package".
            words = lines[prev_line].split()
            if words[1] == "body":
                if words[2] not in ended_packages:
                    #We have not found the end of that package.
                    #This means that our line is in it.
                    return 1
            else:
                if words[1] not in ended_packages:
                    #We have not found the end of that package.
                    #This means that our line is in it.
                    return 0
        elif re.search("^ *private +package +", lines[prev_line], re.I):
            #Found a line starting with "private package".
            words = lines[prev_line].split()
            if words[2] == "body":
                if words[3] not in ended_packages:
                    #We have not found the end of that package.
                    #This means that our line is in it.
                    return 1
            else:
                if words[2] not in ended_packages:
                    #We have not found the end of that package.
                    #This means that our line is in it.
                    return 0
        elif re.search("^ *--" + spark_symbol + " *main_program *", \
                       lines[prev_line], re.I):
            #Found "--# main_program". So we assume that we are in a package
            #spec.
            return 0
        #Separate only occur in bodies
        elif re.match(" *separate( +|$)", lines[prev_line], re.I):
            return 1;

        #Moving on to the previous line.
        prev_line = Find_Previous_Line(lines, prev_line)


#Pre processes the operators of the line.
def Pre_Process_Operators(line):
    import re

    #Ensures that single space appears before ';'.
    line = re.sub(" *;", " ;", line)

    #Ensures that single space appears before ')'.
    line = re.sub(" *\) *", " ) ", line)

    #Ensures that single space follows every '('.
    line = re.sub(" *\( *", " ( ", line)

    #Ensures that single spaces surround '+'.
    line = re.sub(" *\+ *", " + ", line)

    #Ensures that single spaces surround '-'.
    line = re.sub(" +- +", " - ", line)

    #Ensures that single spaces surround '*'.
    line = re.sub(" *\* *", " * ", line)

    #Ensures that single spaces surround '='.
    line = re.sub(" *= *", " = ", line)

    #Ensures that single spaces surround '/'.
    line = re.sub(" */ *", " / ", line)

    #Ensures that single spaces surround '<'.
    line = re.sub(" *< *", " < ", line)

    #Ensures that single spaces surround '>'.
    line = re.sub(" *> *", " > ", line)

    #Ensures that single spaces surround "/=".
    line = re.sub(" */ *= *", " /= ", line)

    #Ensures that single spaces surround ">=".
    line = re.sub(" *> *= *", " >= ", line)

    #Ensures that single spaces surround "**".
    line = re.sub(" *\* *\* *", " ** ", line)

    #Ensures that single spaces surround "=>".
    line = re.sub(" *= *> *", " => ", line)

    #Ensures that single spaces surround "<=".
    line = re.sub(" *< *= *", " <= ", line)

    #Ensures that "->" is surrounded by single spaces.
    line = re.sub(" *- *> *", " -> ", line)

    #Ensures that "<->" is surrounded by single spaces.
    line = re.sub(" *< *- *> *", " <-> ", line)

    return line


#Returns the name of the procedure/function that encloses the statement that
#lies at line "line".
def Subprogram_Name(lines, line):
    import re

    prev_line = Find_Previous_Line(lines, line)
    NCP = Get_Non_Comments_Part (lines[prev_line])
    found = 0
    while not found:
        for word in range (len (NCP)):
            if re.search ("^function$", NCP [word], re.I) or \
            re.search ("^procedure$", NCP [word], re.I):
                found = 1
                name = NCP [word + 1]
                break
        if not found:
            prev_line = Find_Previous_Line(lines, prev_line)
            NCP = Get_Non_Comments_Part (lines[prev_line])

    if "(" in name:
        name, dont_care = name.split("(", 1)
    elif ";" in name:
        name, dont_care = name.split(";", 1)

    return name


#Appropriately places converted_line (with line number "line_number").
#Additionally:
#  1) If add_comma is set we add a ',' at the end of the previous ada line (or
#     replace final ';').
#  2) If add_with is set we add a "with" at the beginning of converted_line.
def Place_Converted_Line(lines, line_number, converted_line, original_line, \
   add_comma, add_with, group_converted_annotations, move_separate_up=False):
    import re
    from conv_conf import spark_symbol, retain_original_annotations

    if add_with:
        #add a "with" at the front of converted_line
        converted_line = re.sub ("^( *)", "\g<1>with ", converted_line)
        converted_line = re.sub ("^     ", "", converted_line)

    if retain_original_annotations:
        #We need to keep the original annotations
        annotations_before = 0
        previous_ada_line = Find_Previous_Ada_Line (lines, line_number)
        previous_line = Find_Previous_Line (lines, line_number)

        if group_converted_annotations:
            #We have to group the converted annotations together. This is
            #used when we convert Global, Depends, Post, Pre.

            #Calculate how many annotations precede the annotation that
            #is currently being converted.
            while previous_line != previous_ada_line:
                if not re.search ("^ *--" + spark_symbol + " *accept", \
                                  lines[previous_line], re.I) and \
                not re.search ("^ *--" + spark_symbol + " *declare", \
                               lines[previous_line], re.I) and \
                not re.search ("^ *--" + spark_symbol + " *inherit", \
                               lines[previous_line], re.I) and \
                not re.search ("^ *--" + spark_symbol + " *main_program", \
                               lines[previous_line], re.I) and \
                not re.search ("^ *--" + spark_symbol + " *type", \
                               lines[previous_line], re.I):
                    #Since the above annotations are not converted, we should
                    #NOT increase annotations_before if any of them is found.
                    annotations_before = annotations_before + 1

                previous_line = Find_Previous_Line (lines, previous_line)

            lines[line_number] = original_line #Restoring original line.

            place_at = Find_Next_Line (lines, line_number)
            while re.search ("^ *--" + spark_symbol + " *global", \
                             lines[place_at], re.I)\
            or re.search ("^ *--" + spark_symbol + " *derives", \
                          lines[place_at], re.I)\
            or re.search ("^ *--" + spark_symbol + " *pre", \
                          lines[place_at], re.I)\
            or re.search ("^ *--" + spark_symbol + " *post", \
                          lines[place_at], re.I) \
            or re.search ("^ *--" + spark_symbol + " *return", \
                          lines[place_at], re.I) \
            or re.search ("^ *--" + spark_symbol + " *own", \
                          lines[place_at], re.I) \
            or re.search ("^ *--" + spark_symbol + " *initializes", \
                          lines[place_at], re.I):
                #Skip all RELATED subsequent annotations
                #RELATED = [global, derives, pre, post, return, own,
                #           initializes]
                place_at = Find_Next_Line (lines, place_at)

            #Skipped one too many.
            place_at = Find_Previous_Line (lines, place_at)

            #Skip as many lines as the number of Annotations_Before.
            for I in range (annotations_before):
                place_at = Find_Next_Ada_Line (lines, place_at);

            if add_comma:
                #add a ',' at end of previous ada line (or replace final ';').
                lines[place_at] = re.sub("; *$", ",", lines[place_at])
                lines[place_at] = lines[place_at].rstrip(",") + ","
        else:
            lines[line_number] = original_line #Restoring original line.

            place_at = line_number

        lines = Insert_After(lines, converted_line, place_at)
    else:
        #We replace the original line with the converted one.

        if add_comma:
            #add a ',' at end of previous ada line (or replace final ';').
            prev = Find_Previous_Ada_Line (lines, line_number)
            lines[prev] = re.sub("; *$", ",", lines[prev])
            lines[prev] = lines[prev].rstrip(",") + ","

        def has_old_subprogram_contract(line):
            return re.search ("^ *--" + spark_symbol + " *global", \
                              line, re.I)\
                or re.search ("^ *--" + spark_symbol + " *derives", \
                              line, re.I)\
                or re.search ("^ *--" + spark_symbol + " *pre", \
                              line, re.I)\
                or re.search ("^ *--" + spark_symbol + " *post", \
                              line, re.I) \
                or re.search ("^ *--" + spark_symbol + " *return", \
                              line, re.I)

        #Move the separate declaration part before any contracts.
        #Possibly do the same when keeping original contracts above.
        if move_separate_up:
            next_line = Find_Next_Ada_Line (lines, line_number)
            if re.match(" *is +separate *;", lines[next_line], re.I):
                with_line = line_number
                if not (add_with or re.match(" *with ", converted_line, re.I)):
                    while not re.match(" *with ", lines[with_line], re.I):
                        with_line = Find_Previous_Ada_Line (lines, with_line)
                for line in range(with_line,line_number): # CHECK RANGE
                    lines[line+1] = lines[line]
                lines[with_line] = re.sub("; *$", "", lines[next_line])
                lines[next_line] = ""
                lines[line_number+1] = converted_line.rstrip(" ") + ";"
            else:
                lines[line_number] = converted_line
        else:
            lines[line_number] = converted_line

    return lines
