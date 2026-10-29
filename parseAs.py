#!/usr/bin/env python3

import sys
import llParser

findFile = "genC"
def parseParamFlags(lis,tag,value):
    global findFile
    if(tag in lis):
        lis.remove(tag)
        findFile = value
parseParamFlags(sys.argv,"-c"  ,"genC")
parseParamFlags(sys.argv,"-gcc","genC")
parseParamFlags(sys.argv,"-py" ,"genPy")

def main():
    ruleFile = sys.argv[1]
    with open(ruleFile,"r")as fptr:
        data = fptr.read()
    p = llParser.Parser(data)
    fl = __import__("genParsers." + findFile).__dict__[findFile]
    fl.llParser = llParser
    fl.runMakeParser(p)



if(__name__ == "__main__" and len(sys.argv)  > 1):main()
elif(__name__ == "__main__"):print("get [rule file]")

