#!/usr/bin/env python3

import sys
import llParser

findFile = "genC"
fileOut  = "-"
def parseParamFlags(lis,tag,value):
    global findFile, fileOut
    if(tag in lis):
        lis.remove(tag)
        findFile = value
parseParamFlags(sys.argv,"-c"  ,"genC" )
parseParamFlags(sys.argv,"-gcc","genC" )
parseParamFlags(sys.argv,"-py" ,"genPy")

if("-o" in sys.argv):
    ind = sys.argv.index("-o")
    if(len(sys.argv) <= ind + 1):
        print("No Argument after Flag \"-o\"")
        exit(1)
    fileOut = sys.argv[ind + 1]

def main():
    ruleFile = sys.argv[1]
    with open(ruleFile,"r")as fptr:
        data = fptr.read()
    p = llParser.Parser(data)
    fl = __import__("genParsers." + findFile).__dict__[findFile]
    fl.llParser = llParser
    fileData = fl.runMakeParser(p)
    if(fileOut == "-"):print(fileData)
    else:
        with open(fileOut,"w")as fptr:
            fptr.write(fileData)



if(__name__ == "__main__" and len(sys.argv)  > 1):main()
elif(__name__ == "__main__"):print("get [rule file]")

