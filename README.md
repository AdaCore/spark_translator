Important note: the Translator tool is meant to help existing projects
developed in SPARK 2005 or earlier transition to SPARK 2014. It has
been developed to automate most of the translation work and it is
expected that the rest of the translation will have to be performed
manually. This means in particular that the Translator will be suitable
for one-time translations and not for fully automated and regular SPARK
2005 to SPARK 2014 translations. While we welcome questions,
suggestions or even patches on this tool, we cannot guarantee
improvements or bug fixes.

The Translator is a python script that consists of:
   *  Convert.py  (This is the main script that calls all other scripts)
   *  Convert_Assert.py
   *  Convert_Check.py
   *  Convert_Derives.py
   *  Convert_Global.py
   *  Convert_Hide.py
   *  Convert_Initializes.py
   *  Convert_Own.py
   *  Convert_Pre_Post_Return.py
   *  Pre_Process.py
   *  Remove_Blank_Lines.py
   *  Remove_Inherit.py
   *  Utilities.py
   *  conv_conf.py (This is the configurations file)

In order to run the Translator one needs the following:
   *  Python has to be installed (not provided).
   *  sparkformat has to be installed (and in the OS's path).
   *  All of the aforementioned scripts have to be under the same directory.

How to invoke the Translator:
   The Translator takes as arguments a list of files and/or
   directories. It then gathers all files that end in ".ads", ".adb"
   or ".ada" that are either directly present in the arguments list or
   under a given directory and converts them from SPARK 2005 to SPARK 2014.

   For example, to convert:

      *  a file named test.adb which is under the current directory:

            python ./Convert.py test.adb

      *  all files that end in ".ads", ".adb" and ".ada" which are
         under directory "Examples":

            python ./Convert.py some_path/Examples

      *  all files ending in ".adb" under directory "Examples":

            python ./Convert.py some_path/*.adb

      *  all files ending in ".ads" under directory "specs" and files
         "test.ads", "test.adb" and "test.ada" which are under the
         current directory:

            python ./Convert.py some_path/specs/*.ads test.ad?

Things to keep in mind:
   *  The Translator assumes that the files that it tries to convert are
      proper SPARK files. If it is called on an invalid SPARK file, it may
      very well crash.
   *  The original files are not overwritten. Instead a new file with the
      extension ".out" is created right next to the original file.
   *  The Translator is a work in progress and is far from perfect! A list of
      known limitations is included below.

How to disable some translation:
   It may be useful in some situations to disable certain features of the
   translation. The easiest way to achieve this is by commenting out the line
   in Convert.py that corresponds to that particular conversion. For example,
   putting a '#' in front of
       "lines = Convert_Global          (lines)"
   would prevent conversion of "--# global" annotations.

Known limitations:
   The following limitations are known (note that this list is not meant to
   be exhaustive):

   *  Does not convert proof functions
   *  Does not deal with user rules
   *  Does not deal with Integrity
   *  Does not convert "--# accept"
   *  Does not translate automatically the following kind of construct:
        type FileSizeT is range 0 .. 10;
        --# assert FileSizeT'Base is Integer;

        into:

        type FileSizeT is new Integer range 0 .. 10;
   *  Body stubs are not converted properly
   *  In Utilities, function First_Aspect may malfunction if
      the previous line happens to contain a "=>".
   *  Does not insert brackets around "if" and "for" expressions
   *  Does not attempt to refine abstract state into constituents using Part_of
