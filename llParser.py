
DEBUG_FLAG = False

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
        if(sting[1] == "r"):return sting[:2],"\r",False
        if(sting[1] == "b"):return sting[:2],"\b",False
        return None,None,None
    if(sting[0].isalnum()):return sting[0],sting[0],False
    arg,inv = litSymbolMap.get(sting[0],(None,None))
    if(arg is not None):
        return sting[0],arg,inv
    return None,None,None


class Position:
    __slots__ = ("row","column","index","endIdx","endRow","endCol")
    def __init__(self):
        self.row      = 1
        self.column   = 1
        self.index    = 0
        self.endIdx   = 0
        self.endRow   = 1
        self.endCol   = 1

    def incr(self):
        self.index += 1
        self.column += 1
        self.endIdx   = self.index
        self.endCol   = self.column

    def incrLine(self):
        self.column = 1
        self.row += 1
        self.endCol   = self.column
        self.endRow   = self.row

    def setRange(self,other:Position):
        self.endIdx = other.endIdx
        self.endRow = other.endRow
        self.endCol = other.endCol

    def update(self,other:Position):
        self.row      = other.row
        self.column   = other.column
        self.index    = other.index
        self.endIdx   = other.endIdx
        self.endRow   = other.endRow
        self.endCol   = other.endCol

    def copy(self) -> Position:
        p = Position()
        p.update(self)
        return p

    def get(self,data:str):
        if(len(data) <= self.index):return None
        return data[self.index]

    def getRange(self,data:str):
        return data[self.index:self.endIdx]

    def __str__(self):
        return f"<{self.row}:{self.column}-{self.endRow}:{self.endCol} {self.index} {self.endIdx}>"

REPEAT   = "? *+"
REPEAT__ = "?*+"
REPEAT_MAY  = 0
REPEAT_NO   = 1
REPEAT_WITH = 2
REPEAT_WO   = 3

class Letter:
    __slots__ = ("allowList","repeat","invert")
    def __init__(self,lit:iter=tuple(),invert:bool=False):
        self.allowList = list(lit)
        self.invert    = invert
        self.repeat    = 1

    def isIn(self,char):
        return self.invert != (char in self.allowList)

    def canConsume(self,count:int) -> bool:
        if(self.repeat == REPEAT_MAY  and count == 0):return True
        if(self.repeat == REPEAT_NO   and count == 0):return True
        if(self.repeat == REPEAT_WITH               ):return True
        if(self.repeat == REPEAT_WO                 ):return True
        return False

    def isSatisfied(self,count:int):
        if(self.repeat == REPEAT_MAY  and count  < 2):return True
        if(self.repeat == REPEAT_NO   and count == 1):return True
        if(self.repeat == REPEAT_WITH               ):return True
        if(self.repeat == REPEAT_WO   and count  > 0):return True
        return False

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
        outStr += REPEAT[self.repeat]
        return outStr

FLAG   = " *?.@#"
FLAG__ = "*?.@#"
FLAG_NONE      = 0
FLAG_UNFOLD    = 1
FLAG_OPTION    = 2
FLAG_HIDE      = 3
FLAG_RAW       = 4
FLAG_COPY      = 5

class SubWord:
    __slots__ = ("word","op")
    def __init__(self,word:str):
        self.word = word
        self.op   = list()

    def __str__(self):
        outStr = f"{self.word}{''.join([FLAG[x] for x in self.op])}"
        return outStr

class Word:
    __slots__ = ("op","name","expr","store")
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
                word = SubWord(line[:l])
                line = line[l:]
                while(len(line) > 0 and line[0] in FLAG__):
                    word.op.append(FLAG.index(line[0]))
                    line = line[1:]
                self.expr.append(word)
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
            elif(len(line) > 0 and line[0] == "["): # ]
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
                if(len(line) > 0 and line[0] in REPEAT__):
                    letter.repeat = REPEAT.index(line[0])
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
    __slots__ = ("parent","name","pos","iter","raw","child")
    def __init__(self,parent:Parser,name:str="_",pos = Position()):
        self.parent = parent
        self.name   = name
        self.pos    = pos
        self.iter   = pos.copy()
        self.child  = list()
        self.raw    = ""

    def _parseRule(self,data:str,rule:Word) -> bool|(-1):
        if(rule.op == ">"):
            return self._parseWord(data,rule)
        if(rule.op == "="):
            return self._parseLetter(data,rule)

    def _parseLetter(self,data:str,rule:Word) -> bool:
        pos = self.iter
        for let in rule.expr:
            counter = 0
            while(let.canConsume(counter)):
                dat = pos.get(data)
                if(dat is None):break
                if(not let.isIn(dat)):
                    break
                counter += 1
                pos.incr()
                if(dat == "\n"):pos.incrLine()
            if(not let.isSatisfied(counter)):
                return False
        self.pos.setRange(pos)
        self.raw = self.pos.getRange(data)
        return True

    def _parseWord(self,data:str,rule:Word) -> bool|(-1):
        pos = self.iter
        for wrd in rule.expr:
            if(DEBUG_FLAG):print(f" {wrd} {pos}")
            lower = Node(self.parent,wrd.word,pos.copy())
            work = lower.parse(data)
            if(DEBUG_FLAG):print(f"-{wrd} {pos} {work}")
            if(not work):
                if(FLAG_OPTION not in wrd.op):
                    return False
                continue
            pos.update(lower.iter)
            if(FLAG_RAW  in wrd.op):
                lower.raw = lower.pos.getRange(data)
            if  (FLAG_HIDE in wrd.op):pass
            elif(FLAG_NONE in wrd.op):
                self.child.append(lower)
            elif(FLAG_UNFOLD in wrd.op):
                self.child += lower.child
            else:
                self.child.append(lower)
            if(FLAG_COPY in wrd.op):
                self.name = lower.name
        self.pos.setRange(pos)
        return True

    def parse(self,data:str):
        for r in self.parent.registered.get(self.name,list()):
            self.iter.update(self.pos)
            self.child.clear()
            o = self._parseRule(data,r)
            if(o == -1):
                return False
            if(o):
                return True
        return False

    def cascade(self,indent:int=0):
        #outStr  = ("  " * indent)
        outStr = f"<{self.name} {self.pos} {self.raw} "
        indent += 1
        for x in self.child:
            outStr += "\n" + ("  " * indent) + x.cascade(indent)
        return outStr + ">"

    def __iter__(self):
        return self.child.__iter__()

    def __getitem__(self,idx):
        return self.child[idx]

    def __len__(self):return len(self.child)

    def __str__(self):return self.cascade()

class Parser:
    __slots__ = ("rules","store","registered")
    def __init__(self,ruleBook:str):
        lrule = ruleBook.split("\n")
        self.rules = list()
        self.registered = dict()
        for ln in lrule:
            if(ln.startswith("//")):continue
            if(len(ln) < 2):continue
            w = Word(ln)
            if(w.expr is None):
                print(ln)
            self.rules.append(w)
        for x in self.rules:
            r = self.registered.get(x.name,None)
            if(r is None):
                r = list()
                self.registered[x.name] = r
            r.append(x)


    def parse(self,data:str):
        n = Node(self)
        worked = n.parse(data)
        if(not worked):
            return None
        return n
