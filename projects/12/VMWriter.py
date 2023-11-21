import os
import sys


class VMWriter:
    def __init__(self):
        self.arithmetic = {
            "+": "add",
            "*": "call Math.multiply 2",
            "/": "call Math.divide 2",
            "-": "sub",
            ">": "gt",
            "<": "lt",
            "&": "and",
            "|": "or",
            "=": "eq",
        }

    def writePush(self, segment, index):
        if segment == "field":
            segment = "this"
        return "push " + segment + " " + str(index)

    def writePop(self, segment, index):
        if segment == "field":
            segment = "this"
        return "pop " + segment + " " + str(index)

    def writeArithmetic(self, command):
        if command == "~":
            return "not"
        else:
            return "neg"

    def writeOp(self, command):
        return self.arithmetic[command]

    def writeLabel(self, label):
        return "label " + str(label)

    def writeGoto(self, label):
        return "goto " + str(label)

    def writeIf(self, label):
        return "if-goto " + str(label)

    def writeCall(self, name, nArgs):
        return "call " + name + " " + str(nArgs)

    def writeFunction(self, name, nArgs):
        return "function " + name + " " + str(nArgs)

    def writeReturn(self):
        return "return"
