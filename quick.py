#!/usr/bin/env python3

import sys
import time
import llParser

llParser.DEBUG_FLAG = "-D" in sys.argv
if(llParser.DEBUG_FLAG):sys.argv.remove("-D")

def main():
    ruleFile = sys.argv[1]
    with open(ruleFile,"r")as fptr:
        data = fptr.read()
    p = llParser.Parser(data)
    if(len(sys.argv) < 3):
        for ru in p.rules:
            print(ru)
        return
    testFile = sys.argv[2]
    with open(testFile,"r")as fptr:
        data = fptr.read()
    print(p.parse(data))



if(__name__ == "__main__" and len(sys.argv)  > 1):main()
if(__name__ == "__main__" and len(sys.argv) == 0):
    print("get [rule file] [test file]")
