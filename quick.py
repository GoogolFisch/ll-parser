#!/usr/bin/env python3

import sys

def lenWord(sting:str)->int:
    for i,v in enumerate(sting):
        if(not (v.isalnum() or v == "_")):
            return i
    return len(sting)
def lenSpace(sting:str)->int:
    for i,v in enumerate(sting):
        if(v in " \t\n\r"):continue
        return i
    return len(sting)

litSymbolMap = {".":("",True),",":("\n",True)," ":(" ",False),"_":("_",False)}
def whatLiteral(sting:str)->tuple(str,str,bool):
    l = len(sting)
    if(l == 0):
        print("Error, why do I get no input :(") #)
    if(l > 1 and sting[0] == "\\"):
        if(sting[1] in "`~!@#$%^&*()-=+[{}];:'\"\\|,./<>?"):
            return sting[:2],sting[1],False
        if(sting[1] in "01234567"):
            idx = 1
            while(len(sting) > idx and sting[idx].isnum()):
                idx += 1
            return sting[:idx],chr(int(sting[1:idx],8)),False
        if(sting[1] == "n"):return sting[:2],"\n",False
        if(sting[1] == "s"):return sting[:2], " ",False
        if(sting[1] == "t"):return sting[:2],"\t",False
        return None,None,None
    if(sting[0].isalnum()):return sting[0],sting[0],False
    arg,inv = litSymbolMap.get(sting[0],(None,None))
    if(arg is not None):
        return sting[0],arg,inv
    return None,None,None


class Position:
    __slots__ = ("row","column","index","startIdx","endidx")
    def __init__(self):
        self.row      = 1
        self.column   = 1
        self.index    = 0
        self.startIdx = 0
        self.endIdx   = 0

    def incr(self):
        self.index += 1
        self.column += 1

    def clone(self) -> Position:
        p = Position()
        p.row      = self.row
        p.column   = self.column
        p.index    = self.index
        p.startIdx = self.startIdx
        p.endIdx   = self.endIdx
        return p

REPEAT_MAY = 0
REPEAT_NO = 1
REPEAT_WITH = 2
REPEAT_WO = 3

class Letter:
    __slots__ = ("allowList","repeat","invert")
    def __init__(self,lit:iter=tuple(),invert:bool=False):
        self.allowList = list(lit)
        self.invert    = invert
        self.repeat    = 1

    def isIn(self,char):
        return self.invert != (char in self.allowList)

    def join(self,other:Letter):
        if(self.invert and other.invert):
            for x in self.allowList.copy():
                if(x not in other.allowList):
                    self.allowList.remove(x)
        elif(self.invert):
            for x in self.allowList.copy():
                if(x in other.allowList):
                    self.allowList.remove(x)
        elif(other.invert):
            inverse = other.allowList.copy()
            for x in self.allowList:
                if(x in other.allowList):
                    inverse.remove(x)
            self.invert = True
            self.allowList = inverse
        else:
            for x in other.allowList:
                if(x not in self.allowList):
                    self.allowList.append(x)

    def range(self,other:Letter):
        myMin = min([ord(x) for x in self .allowList])
        otMax = max([ord(x) for x in other.allowList])
        for x in range(myMin,otMax + 1):
            cx = chr(x)
            if(cx not in self.allowList):
                self.allowList.append(cx)

    def __str__(self):
        outStr = " ^"[self.invert]
        outStr += "[" + "".join(self.allowList) + "]"
        outStr += "? *+"[self.repeat]
        return outStr


class Word:
    __slots__ = ("op","name","expr")
    def __init__(self,line:str):
        i = lenWord(line)
        self.name = line[:i]
        line = line[i:]
        #
        i = lenSpace(line)
        self.op = line[i]
        line = line[i+1:]
        #
        if  (self.op == "="):self.parseLetter(line)
        elif(self.op == ">"):self.parseList  (line)
        else:self.expr = None

    def parseList(self,line):
        self.expr = list()
        while len(line) > 0:
            l = lenSpace(line)
            if(l > 0):line = line[l:];continue
            l = lenWord(line)
            if(l > 0):
                word = list()
                word.append(line[:l])
                line = line[l:]
                if(len(line) > 0 and line[0] in "*?"):
                    word.append(line[0])
                    line = line[1:]
                self.expr.append(tuple(word))
                continue
            print(f"ListError, {ord(line[0])} {line}")
            line = line[1:]

    def parseLetter(self,line):
        self.expr = list()
        while len(line) > 0:
            l = lenSpace(line)
            if(l > 0):line = line[l:];continue

            letter = None
            w,lit,inv = whatLiteral(line)
            if(w is not None):
                letter = Letter(lit,inv)
                line = line[len(w):]
            if(len(line) > 0 and line[0] == "["): # ]
                invert = line[1] == '^'
                line = line[invert + 1:]
                letter = Letter()
                while(len(line) > 0):
                    if(line[0] == "\x5d"):
                        line = line[1:]
                        break
                    w,lit,i = whatLiteral(line)
                    if(w is None):
                        print("Err",line[0],ord(line[0]))
                        line = line[1:]
                        continue
                    subL = Letter(lit,False)
                    line = line[len(w):]
                    if(line[0] != "-"):
                        letter.join(subL)
                        continue
                    line = line[1:]
                    w,lit,i = whatLiteral(line)
                    if(w is None):
                        print(line[0],ord(line[0]))
                        continue
                    topL = Letter(lit,False)
                    subL.range(topL)
                    letter.join(subL)
                if(invert):
                    letter.invert = invert

            if(letter is not None):
                if(len(line) > 0 and line[0] in "?+*"):
                    letter.repeat = "? *+".index(line[0])
                    line = line[1:]
                self.expr.append(letter)
                continue
            print(f"LetterError, {ord(line[0])} {line}")
            line = line[1:]

    def __str__(self):
        outStr = f"{self.name} {self.op} {{" #}}
        for x in self.expr:
            outStr += str(x) + ","
        outStr += "{}"[1]
        if(self.op == "="):
            return outStr
        if(self.op == ">"):
            return outStr

class Node:
    __slots__ = ("name","position","raw","child")
    def __init__(self,name,pos):
        self.name  = name
        self.pos   = pos
        self.child = list()
        self.raw   = ""

    def cascade(self,indent:int=0):
        outStr  = ("  " * indent)
        outStr += f"<{self.name} {self.position} {self.raw} "
        indent += 1
        for x in self.child:
            outStr += "\n" + ("  " * indent) + x.cascade(indent)
        return outStr + ">"

class Parser:
    __slots__ = ("rules")
    def __init__(self,ruleBook:str):
        lrule = ruleBook.split("\n")
        self.rules = list()
        for ln in lrule:
            if(ln.startswith("//")):continue
            if(len(ln) < 2):continue
            w = Word(ln)
            if(w.expr is None):
                print(ln)
            self.rules.append(w)


def main():
    ruleFile = sys.argv[1]
    with open(ruleFile,"r")as fptr:
        data = fptr.read()
    p = Parser(data)
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
    print("get [rule file] and then [test file]")
