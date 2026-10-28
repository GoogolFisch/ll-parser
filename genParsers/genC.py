llParser = None

randCounter = 0
def randName(prefix:str="_") -> str:
    global randCounter
    name = prefix + hex(randCounter)[1:]
    randCounter += 1
    return name


def makeVisitAll(ru:llParser.Word,prefix:str="llPar_",suffix:str="")->(str):
    funName = prefix + ru.name + suffix
    ru.store = funName
    return funName

def makeHeadProg(msg:str) -> str:
    return f"/* {msg} */" + """
#include"parserNode.h"
"""
def makeLetterParser(ruLet:llParser.Letter) -> (str,str):
    name = randName()
    tester = f"int {name} = 0;\n"
    isFirst = True
    loll = [ord(i) for i in ruLet.allowList]
    while len(loll) > 0:
        lw = min(loll)
        cnt = 0
        while lw + cnt in loll:
            loll.remove(lw + cnt)
            cnt += 1
        if(isFirst):isFirst = False
        else       :tester += "else "
        if(cnt == 1):tester += f"if(data[offset] == {lw})"
        else        :tester += f"if(data[offset] >= {lw} && data[offset] < {lw + cnt})"
        tester += f"{{{name} = 1;}}\n"
    if(ruLet.invert):
        tester += f"{name} = !{name};\n"
    return name,tester

def makeWordParser(ru:llParser.Word) -> (str,str,str):
    funName = ru.store
    progBod = f"ParserNode *{funName}(uint8_t *data,ParserNodeLocation loc,int64_t length)"
    progSig = progBod + ";\n"
    progBod += "{\nint64_t offset = loc.idx;\n"#}
    for let in ru.expr:
        nam,fun = makeLetterParser(let)
        if(let.repeat == llParser.REPEAT_MAY):
            progBod += fun
            progBod += f"if({nam} && offset < length){{offset++;}}\n"
        elif(let.repeat == llParser.REPEAT_NO):
            progBod += fun
            progBod += f"if({nam} && offset < length){{offset++;}}else{{return NULL;}}\n"
        elif(let.repeat == llParser.REPEAT_WITH):
            progBod += "while(1){\n"#}
            progBod += fun
            progBod += f"if(!{nam} || offset >= length){{offset--;break;}}\n"
            progBod += "offset++;\n"
            progBod += "\x7d\n"
        elif(let.repeat == llParser.REPEAT_WO):
            didRepeat = randName()
            progBod += f"int {didRepeat} = 0;"
            progBod += "while(1){\n"#}
            progBod += fun
            progBod += f"if(!{nam} || offset >= length){{offset--;break;}}\n"
            progBod += "offset++;\n"
            progBod += "didRepeat=1;"
            progBod += "\x7d\n"
            progBod += f"if(!{didRepeat}){{return NULL;}}\n"
        else:
            print(nam,fun,let)

    progBod += "ParserNode *node = parser_node_fromRange(data,loc,offset);\n"
    progBod += "return node;\n"
    progBod += "\x7d"
    return funName,progSig,progBod

def makeListParser(ru:llParser.Word) -> (str,str,str):
    funName = ru.store
    progBod = f"ParserNode *{funName}(uint8_t *data,ParserNodeLocation loc)"
    progSig = progBod + ";\n"
    progBod += "{\n"#}
    for subWord in ru.expr:
        pass

    progBod += "return loc;\n"
    progBod += "\x7d"
    return funName,progSig,progBod

def runMakeParser(p:llParser.Parser):
    definitions  = list()
    declarations = list()
    for idx,ru in enumerate(p.rules):
        makeVisitAll(ru,prefix="parser__",suffix=str(idx))
    for ru in p.rules:
        if(ru.op == "="):
            fuName,defi,decl = makeWordParser(ru)
            definitions.append(defi)
            declarations.append(decl)
        print(ru)

    print("\n".join(definitions))

