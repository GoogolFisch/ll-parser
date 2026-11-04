llParser = None
PREFIX = "_"

randCounter = 0
def randName(prefix:str="_") -> str:
    global randCounter
    name = prefix + hex(randCounter)[1:]
    randCounter += 1
    return name

def makeVisitAll(ru:llParser.Word,prefix:str="_",suffix:str="")->(str):
    funName = prefix + ru.name + suffix
    ru.store = funName
    return funName
def makeInitFunction(p:llParser.Parser,ruName:str,prefix:str="llPar_") -> (str,str):
    funName = prefix + ruName
    progBod = f"  def {funName}(data:str,loc:Location):\n"
    for x in p.registered.get(ruName,list()):
        varName = randName()
        progBod += f"    {varName} = {x.store}(data,loc,length);\n"
        progBod += f"    if({varName}):return {varName}\n"
    progBod += "    return None\n"
    return funName,progBod
def makeHeadProg(msg:str) -> str:
    return f"\"\"\" \n{msg}\n\"\"\"\n" + """
class Location:
    __slots__ = ("row","col","idx","endRow","endCol","endIdx")
    def __init__(self):
        self.row = self.col = self.endRow = self.endCol = 1
        self.idx = self.endIdx = 0
    def incr(self):
        self.idx += 1
        self.col += 1
        self.endIdx = self.idx
        self.endCol = self.col
    def incrLine(self):
        self.col  = 1
        self.row += 1
        self.endIdx = self.idx
        self.endCol = self.col
    def setRange(self,other:Location):
        self.endIdx = other.endIdx
        self.endCol = other.endCol
        self.endRow = other.endRow
    def update(self,other:Location):
        self.idx = other.endIdx
        self.row = other.endRow
        self.col = other.endCol
    def copy(self):
        l = Location()
        l.row = self.row
        l.col = self.col
        l.idx = self.idx
        l.endRow = self.endRow
        l.endCol = self.endCol
        l.endIdx = self.endIdx
        return l
class Node:
    __slots__ = ("__dict__","isRaw","data","name","loc","children")
    def __init__(self,data:str,name:str,loc:Location):
        self.data = data
        self.name = name
        self.loc  = loc
        self.children = list()
        self.isRaw = False
    @staticmethod
    def fromRange(data:str,name:str,loc:Location,next:int):
        n = Node(data,name,loc.copy())
        n.loc.endIdx = next
        n.loc.endRow = loc.row
        n.loc.endCol = loc.col
        for i in range(n.loc.idx,n.loc.endIdx):
            n.loc.endCol += 1
            if(data[i] == "\n"):
                n.loc.endCol = 1
                n.loc.endRow += 1
        n.isRaw = True
        return n
    def addChild(self,child:Node):
        self.children.append(child)
    def addChildrenOf(self,child):
        self.children += child.children
    def setRange(self,loc:Location):
        self.endIdx = loc.endIdx
        self.endRow = loc.endRow
        self.endCol = loc.endCol
    def print(self,indent:int=0):
        s = " "*indent + f"<{self.loc} {self.name} "
        if(self.isRaw):
            s += f"{self.data[self.loc.idx:self.loc.endIdx]}"
        for ch in self.children:
            s += "\\n" + ch.print(indet + 1)
        s += ">"

class Parser:
"""

def makeLetterParser(ruLet:llParser.Letter,indent:int=3) -> (str,str):
    name = randName()
    ind = "  " * indent
    tester = f"{ind}{name} = False\n"
    isFirst = True
    loll = [ord(i) for i in ruLet.allowList]
    while len(loll) > 0:
        lw = min(loll)
        cnt = 0
        while lw + cnt in loll:
            loll.remove(lw + cnt)
            cnt += 1
        tester += ind
        if(isFirst):isFirst = False
        else       :tester += "el"
        if(cnt == 1):tester += f"if(ord(data[offset]) == {lw}):"
        else        :tester += f"if(ord(data[offset]) >= {lw} && ord(data[offset]) < {lw + cnt}):"
        tester += f"{name} = True\n"
    if(ruLet.invert):
        tester += f"{ind}{name} = not {name}\n"
    return name,tester

def makeWordParser(p:llParser.Parser,ru:llParser.Word) -> (str,str):
    funName = ru.store
    progBod = f"  def {funName}(data:str,loc:Location):\n"
    progBod += "    offset = loc.idx\n"#}
    for let in ru.expr:
        if(let.repeat == llParser.REPEAT_MAY):
            nam,fun = makeLetterParser(let,2)
            progBod += fun
            progBod += f"    if({nam} and offset < len(data)):offset += 1\n"
        elif(let.repeat == llParser.REPEAT_NO):
            nam,fun = makeLetterParser(let,2)
            progBod += fun
            progBod += f"    if({nam} and offset < len(data)):offset += 1\n"
            progBod += f"    else:return None\n"
        elif(let.repeat == llParser.REPEAT_WITH):
            nam,fun = makeLetterParser(let,3)
            progBod +=  "    while(True):\n"#}
            progBod += fun
            progBod += f"      if(not {nam} or offset >= len(data)):break\n"
            progBod +=  "      offset += 1\n"
        elif(let.repeat == llParser.REPEAT_WO):
            nam,fun = makeLetterParser(let,3)
            didRepeat = randName()
            progBod += f"    {didRepeat} = False\n"
            progBod +=  "    while(True):\n"#}
            progBod += fun
            progBod += f"      if(not {nam} or offset >= len(data)):break\n"
            progBod +=  "      offset += 1\n"
            progBod += f"      {didRepeat}=True\n"
            progBod += f"    if(not {didRepeat})return None\n"
        else:
            print(nam,fun,let)

    progBod += "    return node\n"
    return funName,progBod

def makeListParser(p:llParser.Parser,ru:llParser.Word) -> (str,str,str):
    funName = ru.store
    progBod  = f"  def {funName}(data:str,loc:Location):\n"
    progBod += f"    node = Node(data,loc,\"{ru.name}\")\n"
    for subWord in ru.expr:
        varName = randName()
        callingName = p.store.get(subWord.word,None)
        if(callingName is None):
            progBod += "    return None\n"
            break
        progBod += f"    {varName} = {callingName}(data,loc)\n"
        if(llParser.FLAG_UNFOLD in subWord.op):
            progBod += f"    if({varName}):node.appendChild({varName})\n"
        elif(llParser.FLAG_HIDE not in subWord.op):
            progBod += f"    if({varName}):node.appendChildrenOf({varName})\n"
        if(llParser.FLAG_OPTION not in subWord.op):
            progBod += f"    if(not {varName}):return None\n"
        if(llParser.FLAG_RAW in subWord.op):
            progBod += f"    if({varName}):node.isRaw = True\n"
        progBod += f"    if({varName}):loc = node.getAfter()\n"
        # TODO
    progBod += "    node.setRange(loc)\n"
    progBod += "    return node\n"
    return funName,progBod

def runMakeParser(p:llParser.Parser) -> str:
    declarations = list()
    for idx,ru in enumerate(p.rules):
        makeVisitAll(ru,prefix=PREFIX,suffix=str(idx))
    p.store = dict()
    for ruName in p.registered:
        fuName,decl = makeInitFunction(p,ruName,prefix=PREFIX)
        declarations.append(decl)
        p.store[ruName] = fuName
    for ru in p.rules:
        if(ru.op == "="):
            fuName,decl = makeWordParser(p,ru)
            declarations.append(decl)
        elif(ru.op == ">"):
            fuName,decl = makeListParser(p,ru)
            declarations.append(decl)
    #
    fileData = makeHeadProg("This was generated") + "\n"
    fileData += "".join(declarations)
    print(fileData)
    return fileData

