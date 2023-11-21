import os
import sys
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class JackCompiler:
    def __init__(self, jack_codes):
        self.jack_codes = jack_codes
        self.part = []
        self.codes = []
        self.tokens = []
        self.label_num = 0
        self.writer = VMWriter()
        self.keywords = [
            "class",
            "constructor",
            "function",
            "method",
            "field",
            "static",
            "var",
            "int",
            "char",
            "boolean",
            "void",
            "true",
            "false",
            "null",
            "this",
            "let",
            "do",
            "if",
            "else",
            "while",
            "return",
        ]
        self.symbols = [
            "{",
            "}",
            "(",
            ")",
            "[",
            "]",
            ".",
            ",",
            ";",
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
            "~",
        ]

    def token_type(self, token):
        if token in self.keywords:
            return "KEYWORD"
        elif token in self.symbols:
            return "SYMBOL"
        elif token.isdigit():
            return "INT"
        elif token[0] == '"':
            return "STR"
        else:
            return "IDENTIFIER"

    def write_token(self, token):
        self.part += [token]

    def tokenize(self):
        for code in self.jack_codes:
            i = 0
            while i < len(code):
                j = i
                if j < len(code) and code[i] == '"':
                    j = j + 1
                    while code[j] != '"':
                        j = j + 1
                    self.tokens += [self.write_token(code[i + 1 : j])]
                    i = j + 1
                    continue
                while j < len(code) and code[j] != " " and code[j] not in self.symbols:
                    j = j + 1
                if j < len(code) and code[j] == " " and i != j:
                    self.tokens += [self.write_token(code[i:j])]
                    i = j
                elif j < len(code) and code[j] in self.symbols:
                    if i != j:
                        self.tokens += [self.write_token(code[i:j])]
                    self.tokens += [self.write_token(code[j])]
                    i = j
                i = i + 1

    def compileClass(self):
        print(self.part)
        #'class'
        self.part.pop(0)
        # class name
        class_name = self.part.pop(0)
        # {
        self.part.pop(0)
        self.table = SymbolTable()
        self.table.cur_class = class_name
        while self.part[0] != "}":
            if self.part[0] == "static" or self.part[0] == "field":
                self.compileClassVarDec()
                # print(1)
            elif self.part[0] in ["constructor", "function", "method"]:
                if self.part[0] == "method":
                    is_method = True
                else:
                    is_method = False
                self.table.start_subroutine(is_method)
                self.compileSubroutineDec(class_name)
            else:
                break
        # }
        self.part.pop(0)

    def compileClassVarDec(self):
        # field or static
        kind = self.part.pop(0)
        type = self.part.pop(0)
        name = self.part.pop(0)
        self.table.define(name, type, kind)
        # more variables
        while self.part[0] == ",":
            self.part.pop(0)
            name = self.part.pop(0)
            self.table.define(name, type, kind)
        # ;
        self.part.pop(0)

    def compileSubroutineDec(self, class_name):
        # constructor/function/method
        keyword = self.part.pop(0)
        # return type
        self.part.pop(0)
        # subroutine name
        subroutine_name = class_name + "." + self.part.pop(0)
        self.table.subroutine = subroutine_name
        # (
        self.part.pop(0)
        para_num = 0
        # parameterList
        while self.part[0] != ")":
            type = self.part.pop(0)
            name = self.part.pop(0)
            para_num += 1
            self.table.define(name, type, "argument")
            if self.part[0] == ",":
                self.part.pop(0)
        # )
        self.part.pop(0)
        self.compileSubroutineBody(subroutine_name, keyword)

    def compileSubroutineBody(self, subroutine_name, keyword):
        # {
        self.part.pop(0)
        # varDec
        while self.part[0] == "var":
            self.compileVarDec()
        local_count = self.table.varCount("local")
        self.codes += [self.writer.writeFunction(subroutine_name, str(local_count))]
        if keyword == "constructor":
            self.codes += [
                self.writer.writePush("constant", self.table.varCount("field"))
            ]
            self.codes += [self.writer.writeCall("Memory.alloc", 1)]
            self.codes += [self.writer.writePop("pointer", 0)]
        if keyword == "method":
            self.codes += [self.writer.writePush("argument", "0")]
            self.codes += [self.writer.writePop("pointer", "0")]
        # statements
        self.compileStatements()
        # }
        self.part.pop(0)

    def compileStatements(self):
        while self.part[0] != "}":
            if self.part[0] == "let":
                self.compileLet()
            elif self.part[0] == "if":
                self.compileIf()
            elif self.part[0] == "while":
                self.compileWhile()
            elif self.part[0] == "do":
                self.compileDo()
            elif self.part[0] == "return":
                self.compileReturn()

    def compileLet(self):
        # print(self.codes)
        # let
        self.part.pop(0)
        if self.part[1] == "[":
            self.compileArray()
            print(self.codes)
            return
        varName = self.part.pop(0)
        kind = self.table.kindOf(varName)
        index = self.table.indexOf(varName)
        # =
        self.part.pop(0)
        # expression
        self.compileExpression()
        # ;
        self.part.pop(0)
        self.codes += [self.writer.writePop(kind, str(index))]

    def compileIf(self):
        # if
        self.part.pop(0)
        # (
        self.part.pop(0)
        # expression
        self.compileExpression()
        self.codes += ["not"]
        label1 = "L" + str(self.label_num)
        self.label_num += 1
        label2 = "L" + str(self.label_num)
        self.label_num += 1
        self.codes += [self.writer.writeIf(label1)]
        # )
        self.part.pop(0)
        # {
        self.part.pop(0)
        # statements
        self.compileStatements()
        self.codes += [self.writer.writeGoto(label2)]
        self.codes += [self.writer.writeLabel(label1)]
        # }
        self.part.pop(0)
        if self.part[0] == "else":
            # else
            self.part.pop(0)
            # {
            self.part.pop(0)
            # statements
            self.compileStatements()
            # }
            self.part.pop(0)
        self.codes += [self.writer.writeLabel(label2)]
        # print(self.codes)

    def compileWhile(self):
        label1 = "L" + str(self.label_num)
        self.label_num += 1
        label2 = "L" + str(self.label_num)
        self.label_num += 1
        self.codes += [self.writer.writeLabel(label1)]
        # while
        self.part.pop(0)
        # (
        self.part.pop(0)
        # expression
        self.compileExpression()
        # )
        self.part.pop(0)
        self.codes += ["not"]
        self.codes += [self.writer.writeIf(label2)]
        # {
        self.part.pop(0)
        # statements
        self.compileStatements()
        # }
        self.part.pop(0)
        self.codes += [self.writer.writeGoto(label1)]
        self.codes += [self.writer.writeLabel(label2)]
        # print(self.codes)

    def compileSubroutineCall(self):
        subroutine_name = ""
        object_name = ""
        have_this = False
        if self.part[1] == ".":
            object_name = self.part[0]
            if self.table.record_of(object_name):
                self.compileVar()
                have_this = True
                object_name = self.table.typeOf(object_name)
            else:
                self.part.pop(0)
            # .
            self.part.pop(0)
            subroutine_name = object_name + "." + self.part.pop(0)
        else:
            if self.table.typeOf("this") != None:
                self.codes += [self.writer.writePush("pointer", "0")]
                object_type = self.table.typeOf("this")
                have_this = True
                subroutine_name = object_type + "." + self.part.pop(0)
            else:
                self.codes += [self.writer.writePush("pointer", "0")]
                class_name = self.table.cur_class
                have_this = True
                subroutine_name = class_name + "." + self.part.pop(0)
        # (
        self.part.pop(0)
        i = 0
        if self.part[0] == ")":
            num = 0
        else:
            num = 1
        # calculate the number of arguments
        while self.part[i] != ";":
            if self.part[i] == ",":
                num += 1
            i += 1
        if have_this == True:
            num += 1
        # expressionList
        self.compileExpressionList()
        # )
        self.part.pop(0)
        self.codes += [self.writer.writeCall(subroutine_name, str(num))]

    def compileDo(self):
        # do
        self.part.pop(0)
        # subroutineCall
        self.compileSubroutineCall()
        self.codes += [self.writer.writePop("temp", "0")]
        # ;
        self.part.pop(0)
        # print(self.codes)

    def compileExpressionList(self):
        while self.part[0] != ")":
            self.compileExpression()
            if self.part[0] == ",":
                self.part.pop(0)

    def compileReturn(self):
        # return
        self.part.pop(0)
        # expression
        if self.part[0] != ";":
            self.compileExpression()
        else:
            self.codes += [self.writer.writePush("constant", "0")]
        # ;
        self.part.pop(0)
        self.codes += [self.writer.writeReturn()]

    def compileVarDec(self):
        # var
        kind = self.part.pop(0)
        # type
        type = self.part.pop(0)
        # varName
        name = self.part.pop(0)
        self.table.define(name, type, "local")
        while self.part[0] == ",":
            # ,
            self.part.pop(0)
            # varName
            name = self.part.pop(0)
            self.table.define(name, type, "local")
        # ;
        self.part.pop(0)

    def compileVar(self):
        if self.part[0] == "true":
            self.codes += [self.writer.writePush("constant", 1)]
            self.codes += [self.writer.writeArithmetic("-")]
            self.part.pop(0)
        elif self.part[0] == "null" or self.part[0] == "false":
            self.codes += [self.writer.writePush("constant", 0)]
            self.part.pop(0)
        elif self.token_type(self.part[0]) == "INT":
            self.codes += [self.writer.writePush("constant", self.part.pop(0))]
        elif self.part[0] == "this":
            self.codes += [self.writer.writePush("pointer", 0)]
            self.part.pop(0)
        elif self.table.record_of(self.part[0]):
            name = self.part.pop(0)
            kind = self.table.kindOf(name)
            index = self.table.indexOf(name)
            self.codes += [self.writer.writePush(kind, str(index))]
        else:
            self.compileString()

    def compileString(self):
        cur_string = self.part[0]
        self.codes += [self.writer.writePush("constant", str(len(cur_string)))]
        self.codes += [self.writer.writeCall("String.new", 1)]
        i = 0
        for c in cur_string:
            self.codes += [self.writer.writePush("constant", ord(c))]
            self.codes += [self.writer.writeCall("String.appendChar", 2)]
        self.part.pop(0)

    def compileArray(self):
        # the name of the array
        self.compileVar()
        # [
        self.part.pop(0)
        # ex1
        self.compileExpression()
        # top stack value=address of arr[ex1]
        self.codes += ["add"]
        # ]
        self.part.pop(0)
        # =
        self.part.pop(0)
        # ex2
        self.compileExpression()
        # temp0=ex2
        self.codes += [self.writer.writePop("temp", 0)]
        self.codes += [self.writer.writePop("pointer", 1)]
        self.codes += [self.writer.writePush("temp", 0)]
        self.codes += [self.writer.writePop("that", 0)]
        # ;
        self.part.pop(0)

    def compileTerm(self):
        # call a subroutine
        if self.part[1] == ".":
            self.compileSubroutineCall()
        elif self.part[0] == "(":
            # (
            self.part.pop(0)
            while self.part[0] != ")":
                self.compileExpression()
            # )
            self.part.pop(0)
        # unaryOp term
        elif self.part[0] in ["~", "-"]:
            unary_op = self.part.pop(0)
            self.compileTerm()
            self.codes += [self.writer.writeArithmetic(unary_op)]
        # array
        elif self.part[1] == "[":
            # array name
            self.compileVar()
            # [
            self.part.pop(0)
            # expression
            self.compileExpression()
            # ]
            self.part.pop(0)
            self.codes += ["add"]
            self.codes += [self.writer.writePop("pointer", 1)]
            self.codes += [self.writer.writePush("that", 0)]
        # a constant or a var
        else:
            self.compileVar()

    def compileExpression(self):
        self.compileTerm()
        while self.part[0] in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            # +...
            op = self.part.pop(0)
            # term
            self.compileTerm()
            self.codes += [self.writer.writeOp(op)]
