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
def makeInitFunction(p:llParser.Parser,ruName:str,prefix:str="llPar_") -> (str,str,str):
    funName = prefix + ruName
    progBod = f"ParserNode *{funName}(uint8_t *data,ParserNodeLocation loc,int64_t length)"
    progSig = progBod + ";\n"
    progBod += "{\n" #}
    for x in p.registered.get(ruName,list()):
        varName = randName()
        progBod += f" ParserNode *{varName} = {x.store}(data,loc,length);\n"
        progBod += f" if({varName})return {varName};\n"
    progBod += " return NULL;\n"
    progBod += "\x7d\n"
    return funName,progSig,progBod

def makeHeadProg(msg:str) -> str:
    return f"/* {msg} */" + """
#include"parserNode.h"
"""
def makeHeadFunction(p:llParser.Parser,name:str) -> (str,str,str):
    funName = name
    progBod = f"ParserNode *{funName}(uint8_t *data,int64_t length)"
    progSig = progBod + ";\n"
    progBod += "{\n" #}
    progBod += f" return {p.store['_']}(data,parser_location_new(),length);\n"
    progBod += "\x7d\n"
    return funName,progSig,progBod
def makeLetterParser(ruLet:llParser.Letter) -> (str,str):
    name = randName()
    tester = f"  int {name} = 0;\n"
    isFirst = True
    loll = [ord(i) for i in ruLet.allowList]
    while len(loll) > 0:
        lw = min(loll)
        cnt = 0
        while lw + cnt in loll:
            loll.remove(lw + cnt)
            cnt += 1
        tester += "  "
        if(isFirst):isFirst = False
        else       :tester += "else "
        if(cnt == 1):tester += f"if(data[offset] == {lw})"
        else        :tester += f"if(data[offset] >= {lw} && data[offset] < {lw + cnt})"
        tester += f"{{{name} = 1;}}\n"
    if(ruLet.invert):
        tester += f"  {name} = !{name};\n"
    return name,tester

def makeWordParser(p:llParser.Parser,ru:llParser.Word) -> (str,str,str):
    funName = ru.store
    progBod = f"ParserNode *{funName}(uint8_t *data,ParserNodeLocation loc,int64_t length)"
    progSig = progBod + ";\n"
    progBod += "{\n int64_t offset = loc.idx;\n"#}
    for let in ru.expr:
        nam,fun = makeLetterParser(let)
        if(let.repeat == llParser.REPEAT_MAY):
            progBod += fun
            progBod += f" if({nam} && offset < length){{offset++;}}\n"
        elif(let.repeat == llParser.REPEAT_NO):
            progBod += fun
            progBod += f" if({nam} && offset < length){{offset++;}}else{{return NULL;}}\n"
        elif(let.repeat == llParser.REPEAT_WITH):
            progBod += " while(1){\n"#}
            progBod += fun
            progBod += f" if(!{nam} || offset >= length){{break;}}\n"
            progBod += " offset++;\n"
            progBod += " \x7d\n"
        elif(let.repeat == llParser.REPEAT_WO):
            didRepeat = randName()
            progBod += f" int {didRepeat} = 0;\n"
            progBod += " while(1){\n"#}
            progBod += fun
            progBod += f" if(!{nam} || offset >= length){{break;}}\n"
            progBod += " offset++;\n"
            progBod += f" {didRepeat}=1;\n"
            progBod += " \x7d\n"
            progBod += f" if(!{didRepeat}){{return NULL;}}\n"
        else:
            print(nam,fun,let)

    progBod += f" ParserNode *node = parser_node_fromRange(data,&loc,offset,\"{ru.name}\");\n"
    progBod += " return node;\n"
    progBod += "\x7d\n"
    return funName,progSig,progBod

def makeListParser(p:llParser.Parser,ru:llParser.Word) -> (str,str,str):
    funName = ru.store
    progBod = f"ParserNode *{funName}(uint8_t *data,ParserNodeLocation loc,int64_t length)"
    progSig = progBod + ";\n"
    progBod += "{\n"#}
    progBod += f" ParserNode *node = parser_node_new(data,&loc,\"{ru.name}\");\n"
    for subWord in ru.expr:
        varName = randName()
        callingName = p.store.get(subWord.word,None)
        if(callingName is None):
            progBod += "return NULL;\n"
            break
        progBod += f" ParserNode *{varName} = {callingName}(data,loc,length);\n"
        if(llParser.FLAG_UNFOLD in subWord.op):
            progBod += f" if({varName}){{parser_node_appendChildrenOf(&node,{varName});}}\n"
        elif(llParser.FLAG_HIDE not in subWord.op):
            progBod += f" if({varName}){{parser_node_appendChild(&node,{varName});}}\n"
        if(llParser.FLAG_OPTION not in subWord.op):
            progBod += f" if(!{varName}){{parser_node_free(node);return NULL;}}\n"
        if(llParser.FLAG_RAW in subWord.op):
            progBod += f" if({varName}){{node->isRaw = 1;}}\n"
        progBod += f" if({varName}){{parser_location_setAfter(&loc,&({varName}->location));}}\n"
        if(llParser.FLAG_HIDE in subWord.op):
            progBod += f" parser_node_free({varName});\n"
        # TODO
    progBod += " parser_node_setRange(node,&loc);\n"
    progBod += " return node;\n"
    progBod += "\x7d\n"
    return funName,progSig,progBod

PREFIX = "parser__"
def runMakeParser(p:llParser.Parser) -> str:
    definitions  = list()
    declarations = list()
    for idx,ru in enumerate(p.rules):
        makeVisitAll(ru,prefix=PREFIX,suffix=str(idx))
    p.store = dict()
    for ruName in p.registered:
        fuName,defi,decl = makeInitFunction(p,ruName,prefix=PREFIX)
        definitions.append(defi)
        declarations.append(decl)
        p.store[ruName] = fuName
    for ru in p.rules:
        if(ru.op == "="):
            fuName,defi,decl = makeWordParser(p,ru)
            definitions.append(defi)
            declarations.append(decl)
        elif(ru.op == ">"):
            fuName,defi,decl = makeListParser(p,ru)
            definitions.append(defi)
            declarations.append(decl)
    #
    if True:
        headFunc,defi,decl = makeHeadFunction(p,PREFIX[:-1]+"Parser")
        definitions.insert(0,defi)
        declarations.append(decl)
    fileData = makeHeadProg("This was generated") + "\n"
    fileData += "".join(definitions) + "\n"
    fileData += "".join(declarations)
    print(fileData)
    print(headFunc)
    print("gcc [FileName] -Wall -Wextra -g -fPIC -shared -o [output].so")
    return fileData

