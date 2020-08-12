#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Combines annotations that spread over multiple lines, into oneliners.
def Create_Oneliners(lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import Find_Next_Line

    result = []
    line = 0
    while line < len(lines):
        if re.search("^ *--" + spark_symbol + " *accept ", \
                     lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *assert ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *check ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *declare ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *derives ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *function ", \
                  lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *global ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *hide ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *inherit ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *initializes ", \
                  lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *own ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *post ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *pre ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *pre ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *return ", lines[line], re.I) or \
        re.search("^ *--" + spark_symbol + " *type ", lines[line], re.I):
            #Statement introduces an annotation.
            new_line = lines[line]

            if re.search("^ *--" + spark_symbol + " *function ", \
                         lines[line], re.I):
                #Statement introduces a proof function.
                found_return = 0
                next_line = line
                while not found_return:
                    #We haven't found the return part yet.
                    if re.search("return", lines[next_line], re.I):
                        found_return = 1
                    else:
                        next_line = Find_Next_Line(lines, next_line)
                        new_line = new_line + re.sub("^ *--" + spark_symbol + \
                        " *", " ", lines[next_line])
                next_line = Find_Next_Line(lines, next_line)
                while re.search("^ *--" + spark_symbol + "  ", \
                                lines[next_line]):
                    #next_line is a continuation of the annotation.
                    new_line = new_line + re.sub("^ *--" + spark_symbol + \
                    "  ", " ", lines[next_line])
                    next_line = Find_Next_Line(lines, next_line)
            else:
                #Statement introduces something other than a proof function.
                next_line = Find_Next_Line(lines, line)
                while re.search("^ *--" + spark_symbol + "  ", \
                                lines[next_line]):
                    #next_line is a continuation of the annotation.
                    new_line = new_line + re.sub("^ *--" + spark_symbol + \
                                                 " *", " ", lines[next_line])
                    next_line = Find_Next_Line(lines, next_line)

            #Appending the new unified line.
            result.append(new_line)

            #Copying over comments and blank lines.
            line = line + 1
            while line < next_line:
                if not lines[line].strip() or \
                ( re.search("^ *--", lines[line]) and not \
                re.search("^ *--" + spark_symbol, lines[line]) ):
                    result.append(lines[line])
                line = line + 1
        else:
            #Statement does NOT introduce an annotation so append it directly.
            result.append(lines[line])
            line = line + 1
    return result


#Performs some pre processing.
def Pre_Process(lines):
    import re
    from conv_conf import spark_symbol
    from Utilities import Insert_After

    #Move comments that are in annotations to a line of their own.
    length = len(lines)
    for line in reversed(range(length)):
        if "--" + spark_symbol in lines[line]:
            a, b = lines[line].split("--" + spark_symbol, 1)
            indent = a
            if "--" in b:
                c, d = b.split("--", 1)
                d = indent + "   --" + d
                lines[line] = a + "--" + spark_symbol + c
                lines = Insert_After(lines, d, line)

    for line in range(len(lines)):
        #Remove SPARK lines that contain no annotations whatsoever.
        lines[line] = re.sub("^ *--" + spark_symbol + " *$", "", lines[line])

        #Remove trailing whitespaces.
        lines[line] = re.sub(" *$", "", lines[line])

        #Perform additional transformations on stuff inside annotations.
        if re.search("^ *--" + spark_symbol, lines[line]):
            #Remove spaces that appear directly before ','.
            lines[line] = re.sub(" *,", ",", lines[line])

            #Remove spaces that appear directly before ';'.
            lines[line] = re.sub(" *;", ";", lines[line])

            #Remove spaces that appear directly before '&'.
            lines[line] = re.sub(" *&", "&", lines[line])

            #Remove spaces that appear directly before ')'
            #if ")" is not the first non-space character.
            if not re.search("^ *\)", lines[line]):
                lines[line] = re.sub(" *\)", ")", lines[line])

            #Remove spaces that appear directly after '('.
            lines[line] = re.sub("\( *", "(", lines[line])

            #Ensures that a single space follows every ','.
            lines[line] = re.sub(", *", ", ", lines[line])

            #Remove spaces that appear directly before or after '.'.
            lines[line] = re.sub(" *\. *", ".", lines[line])

            #Remove trailing whitespaces (might introduced some ourselves).
            lines[line] = re.sub(" *$", "", lines[line])

        #Ensures that two spaces follow every "--#" except from the ones that
        #introduce NEW annotations
        lines[line] = re.sub("--" + spark_symbol, "--" + spark_symbol + "  ",\
        lines[line])

        #List of all possible SPARK annotations
        spark_anns = ["accept", "assert", "check", "declare", "derives", \
                      "function", "global", "hide", "inherit", "initializes",\
                      "main_program", "own", "post", "pre", "return", "type"]

        for el in spark_anns:
            lines[line] = re.sub("--" + spark_symbol + " *" + el + " +", \
            "--" + spark_symbol + " " + el + " ", lines[line], re.I)

            lines[line] = re.sub("--" + spark_symbol + " *" + el + "$", \
            "--" + spark_symbol + " " + el + " ", lines[line], re.I)

            lines[line] = re.sub("--" + spark_symbol + " *" + el + ";", \
            "--" + spark_symbol + " " + el + ";", lines[line], re.I)

    #Invoking the Create_Oneliners function.
    lines = Create_Oneliners(lines)

    return lines
