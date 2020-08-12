#! /usr/bin/env python
# Copyright (C) 2013, Altran UK Limited

#The converted file will have the same as the original followed by extension.
extension = ".orig"

#When changing the file in place, the extension is used to store the original
#file.
in_place = False

#The spark symbol ('#' by default) that follows the ada comments ("--") can be
#changed here.
spark_symbol = "#"

#Enables the convertion of "and" into "and then" and "or" into "or else".
#By default it is disabled (0). Set to anything but '0' in order to enable.
and_then_or_else = 0

#Retain original annotations when retain_original_annotations is set to
#anything but 0.
retain_original_annotations = 0

#------------------------------------------------------------------------------
#The following settings should be set to True only when
#retain_original_annotations is 0, otherwise they may not have the intended
#effect.

#Discard Refined_Global, Refined_Depends and Refined_Post instead of generating
#them.
discard_refined_annotations = True

#Discard Global and Depends instead of generating them.
discard_flow_annotations = False

#Discard Assert_And_Cut True instead of generating them.
discard_assert_and_cut_true = True
