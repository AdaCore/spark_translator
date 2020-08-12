#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#Takes as arguments a list of files/directories that are to be converted.

import re
from shutil     import copyfile
from os         import path, walk
from sys        import argv, exit
from subprocess import call
import shutil


if len(argv) == 1:
    #If no arguments were given. Then we print an example of a proper
    #invocation and exit.
    print "Proper Usage:", argv[0], \
    "file_or_dir_1 file_or_dir_2 file_or_dir_3 ..."

    exit (-1)
else:
    files = [] #Initializing list of files that we need to convert.
    for argument in range (1, len(argv)):
        if path.isdir(argv[argument]):
            #If argument is a directory.
            for p, d, f in walk(argv[argument]):
                for a_file in f:
                    if re.search ("\.ad[abs]$", a_file, re.I):
                        files.append(path.join(p, a_file))
        elif path.isfile(argv[argument]) and \
        re.search ("\.ad[abs]$", argv [argument], re.I):
            #If argument is a file that ends in ".ads", ".adb", or ".ada".
            files.append(argv[argument])
        else:
            #Argument is neither a valid file, nor a directory.
            print "Argument ", argv[argument], \
            " is neither a valid file, nor a directory."

            continue


if len(files) == 0:
    #No ".ads", ".adb" or ".ada" files were found, hence we exit.
    print "No \".ads\", \".adb\" or \".ada\" files were found. Exiting..."
    exit (-1)


from conv_conf               import extension
from Remove_Blank_Lines      import Remove_Blank_Lines
from Pre_Process             import Pre_Process
from Remove_Inherit          import Remove_Inherit
from Convert_Own             import Convert_Own
from Convert_Initializes     import Convert_Initializes
from Convert_Global          import Convert_Global
from Convert_Derives         import Convert_Derives
from Convert_Pre_Post_Return import Convert_Pre_Post_Return
from Convert_Check           import Convert_Check
from Convert_Assert          import Convert_Assert
from Convert_Hide            import Convert_Hide
from conv_conf               import in_place


#Initialize lists of subprograms found. If a subprogram's name is not in its
#respective list, then we are dealing with the conversion of this annotation
#in the spec of the subprogram. Otherwise, we are in the subprogram's body.
subprograms_global  = []
subprograms_derives = []
subprograms_pre     = []
subprograms_post    = []
subprograms_return  = []


files.sort(key=path.basename) #Alphabetically sort list of files.


#Iterate through files and convert them. We go in reverse so as to convert
#"ads" files before "adb" files.
for a_file in reversed (files):
    #Call sparkformat on a copy (converted_file) of the original file.
    converted_file = a_file + extension
    copyfile(a_file, converted_file)
    call(["sparkformat", "-add_modes", converted_file])

    #Open converted_file and read all its lines.
    fd = open(converted_file, "rU") #Opening file descriptor for reading.
    lines = fd.read().splitlines()  #Reading all lines of the file.
    fd.close()                      #Closing file descriptor.

    f_name = re.sub ("\.ad.", ":", path.basename(a_file))

    print a_file

    file_with = set()
    for line in lines:
        m = re.match(" *with ([\w\.]+)", line, re.I)
        if m:
            file_with.add(m.group(1).lower())

    #lines = Remove_Blank_Lines      (lines)
    lines = Pre_Process             (lines)
    lines = Remove_Inherit          (lines, file_with)
    lines = Convert_Own             (lines)
    lines = Convert_Initializes     (lines)
    lines = Convert_Global          (lines, subprograms_global, f_name)
    lines = Convert_Derives         (lines, subprograms_derives, f_name)
    lines = Convert_Pre_Post_Return (lines, subprograms_pre, \
                                     subprograms_post, subprograms_return, \
                                     f_name)
    lines = Convert_Check           (lines)
    lines = Convert_Assert          (lines)
    lines = Convert_Hide            (lines)

    if in_place:
        #Move the file to the converted_file
        shutil.copyfile(a_file, converted_file)
        #Use a_file as the converted_file
        converted_file = a_file

    #Creating a new file and writing the converted code in it.
    fd = open(converted_file, "w")   #Opening file descriptor for writing.
    for line in range(len(lines)):
        fd.write(lines[line] + "\n") #Writing line and moving to next one.
    fd.close()                       #Closing file descriptor.

    #Use adapp to make our output look nice. adapp currently does not work on
    #SPARK 2014.
