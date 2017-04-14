#!/usr/bin/env python
# -----------------------------------------------------------------------------
# @file     modegenDriver.py
# @brief    driver script for PHM's modegen
# @author   David Hale
# @date     2017-02-08
# @modified 2017-02-08 DH
# 
# This script invokes the PHM modegen.
# -----------------------------------------------------------------------------

import sys
sys.dont_write_bytecode = True
sys.tracebacklimit=0
import fileinput
import wavgen

# -----------------------------------------------------------------------------
# @fn     main
# @brief  
# @param  source, name of the input .wdl file without the .wdl part
# @return none
# -----------------------------------------------------------------------------
def main(source, toplot):
    """
    """
    input  = source+".wdl"
    output = source
    if toplot.upper() == "FALSE" or toplot.upper() == "NO" or \
       toplot.upper() == "F"     or toplot.upper() == "N"  or toplot.upper() == "0":
        wavgen.GenerateFigs = False
    elif toplot.upper() == "TRUE" or toplot.upper() == "YES" or \
         toplot.upper() == "T"    or toplot.upper() == "Y"   or toplot.upper() == "1":
        wavgen.GenerateFigs = True
    else:
        print("warning: invalid plotting option specified, defaulting to True")
        wavgen.GenerateFigs = True

    wavgen.loadWDL(input, output)
    plt.show(block=True)

# -----------------------------------------------------------------------------
#           __main__
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # check for correct number of args passed
    # don't count the zeroeth arg, as it is my name
    if len(sys.argv[1:]) == 2:
#       main(sys.argv[1], sys.argv[2])
        wavgen.modegen(sys.argv[1], sys.argv[2]).write("a")
        sys.exit(0)
    else:
        print("error: wavgenDriver.py got %d argument(s) but expecting 2" % (len(sys.argv[1:])))
        sys.exit(1)