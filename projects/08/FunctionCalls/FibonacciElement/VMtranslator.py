import os
import sys

class VMTranslator:
    """
    translate a .vm file into a .asm file which contains assembly code for hack machine
    """
    def __init__(self, file_path):
        """
        open the file & filter the blanks and comments
        @attr self.vm_filename (str): input file
        @attr self.asm_filename (str): output file
        @attr self.rela_path (str): relative path for the output_file
        @attr self.codes (list of str): a list contains clean vm code with no blank or comments
        @attr self.asm_codes(list of str): a list contains assembly codes generated from self.codes
        """
        #super(VMTranslator,self).__init__()
        self.vm_filename=os.path.basename(file_path)
        self.rela_path=file_path[:-len(self.vm_filename)]
        self.asm_filename=self.vm_filename[:-3]+".asm"
        self.codes=[]
        self.asm_codes=[]
        self.asm_func=[]
        self.arith_dict={
        "not":"!","neg":"-","add":"+","sub":"-","and":"&","or":"|",
        "eq":"JNE","lt":"JGE","gt":"JLE",
        }
        self.mapping={
        "local":"LCL","argument":"ARG","this":"THIS","that":"THAT",
        "temp":"5","pointer":"3",
        }
        self.symbol_index=0
        if(os.path.isfile(file_path)):
            self.predispose(file_path)
            self.parse(self.vm_filename[:-3])
        else:
            for file in os.listdir(file_path):
                name=os.path.basename(file_path)
                if name[-2:]=="vm":
                    self.predispose(file)
                    self.parse(self.vm_filename[:-3])
    
    def predispose(self,file_path):
        self.vm_filename=os.path.basename(file_path)
        suffix=self.vm_filename[-2:]
        assert suffix=="vm","please choose an input named like xxx.vm"
        with open(file_path,'r') as file:
            for line in file:
                _line=line.strip()
                if len(_line)==0 or _line[0]=="/":
                    continue
                if _line.find('/')!=-1:
                    _line=_line[:_line.find('/')]
                self.codes.append(_line.strip())
                self.file_name=os.path.basename(file_path)
                

    def parse(self,file_name):
        """
        for each line in self.codes, generate its corresponding assembly codes
        """
        call_num=1
        for code in self.codes:
            part=code.split()
            if len(part)==1 and part[0]!="return": # arithmetic commands
                self.asm_codes+=self.C_arith(part[0])
            elif part[0]=="push": # push command
                self.asm_codes+=self.C_push(part[1:])
            elif part[0]=="pop": # pop command
                self.asm_codes+=self.C_pop(part[1:])
            elif part[0]=="label":
                label="("+part[1]+")"
                self.asm_codes+=[label]
            elif part[0]=="goto":
                at="@"+part[1]
                self.asm_codes+=[at,"0;JMP"]
            elif part[0]=="if-goto":
                self.asm_codes+=self.C_if_jump(part[1:])
            elif part[0]=="function":
                self.asm_codes+=self.C_func(part[1:])
            elif part[0]=="return":
                self.asm_codes+=self.C_return(part[0],file_name,call_num)
            elif part[0]=="call":
                self.asm_codes+=self.C_call(part[1:],file_name,call_num)
    
    def C_call(self,command,file_name,call_num):
        label="("+command[0]+"$ret."+str(call_num)+")"
        asm_code+=["@"+label,"D=A","@SP","A=M","M=D","@SP","M=M+1"]
        asm_code+=["@LCL","D=M","@SP","A=M","M=D","@SP","M=M+1"]
        asm_code+=["@ARG","D=M","@SP","A=M","M=D","@SP","M=M+1"]
        asm_code+=["@THIS","D=M","@SP","A=M","M=D","@SP","M=M+1"]
        asm_code+=["@THAT","D=M","@SP","A=M","M=D","@SP","M=M+1"]
        asm_code+=["@R5","D=A","@SP","D=M-D","@R"+command[1],"D=D-A","@ARG","M=D"]
        asm_code+=["@SP","D=M","@LCL","M=D"]
        at="@"+command[0]
        self.asm_code+=[at,"0;JMP"]
        asm_code+=[label]
        call_num+=1
    
    def C_return(self,command):
    
        #frame(tmp1)=LCL
        asm_code=["@LCL","D=M","@R13","M=D"]
        
        #retAddr(tmp2)@LCL-5
        asm_code+=["@R5","A=D-A","D=M","@R14","M=D"]
        
        #argument0=return value(pop())
        asm_code+=["@SP","AM=M-1","D=M","@ARG","A=M","M=D"]
        
        #SP=arg+1
        asm_code+=["@ARG","D=M","@SP","M=D+1"]
        
        #restores THAT for the caller
        asm_code+=["@R13","A=M-1","D=M","@THAT","M=D"]
        
        #restores THIS
        asm_code+=["@R2","D=A","@R13","A=M-D","D=M","@THIS","M=D"]
        
        #restores ARG
        asm_code+=["@R3","D=A","@R13","A=M-D","D=M","@ARG","M=D"]
        
        #restores LCL
        asm_code+=["@R4","D=A","@R13","A=M-D","D=M","@LCL","M=D"]
        
        #goto return address
        asm_code+=["@R14","A=M"]
        
        
        return asm_code
        
    
    def C_if_jump(self,command):
        jump_pos="@"+command[0]
        asm_code=["@SP","AM=M-1","D=M",jump_pos,"D;JNE"]
        return asm_code
    
    def C_func(self,command):
        """
        generate assembly codes for function definition commands
        """
        self.asm_func+=command[0]
        asm_code=["("+command[0]+")"]
        times=int(command[1])
        while times>0:
            asm_code+=["@SP","M=M+1"]
            times-=1
        return asm_code
        

    def C_arith(self,command):
        """
        generate assembly codes for arithmetic commands
        @para command (str): the arithmetic command to be translated
        """
        if command in ["not","neg"]: # one argument command
            spec="M="+self.arith_dict[command]+"M"
            asm_code=["@SP","A=M-1",spec]
        elif command in ["add","sub","and","or"]:
            spec="M=M"+self.arith_dict[command]+"D"
            asm_code=["@SP","AM=M-1","D=M","A=A-1",spec]
        elif command in ["eq","gt","lt"]:
            symbol=command+"_"+str(self.symbol_index)
            symbol1="@"+symbol
            symbol2="("+symbol+")"
            spec="D;"+self.arith_dict[command]
            asm_code=["@SP","AM=M-1","D=M","A=A-1","D=M-D","M=0",symbol1,spec,"@SP","A=M-1","M=-1",symbol2]
            self.symbol_index+=1
        return asm_code
        
    def C_push(self,command):
        """
        generate assembly codes for push commands
        @para command (list of str): the push command to be translated
        """
        # put the value which will be pushed into the stack in D
        asm_code=[]
        if command[0]=="constant":
            asm_code=["@"+command[1],"D=A"]
        elif command[0] in ["local","argument","this","that"]:
            asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"A=M+D","D=M"]
        elif command[0] in ["temp","pointer"]:
            asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"A=A+D","D=M"]
        elif command[0] == "static":
            symbol="@"+self.vm_filename[:-3]+"."+command[1]
            asm_code=[symbol,"D=M"]

        # put the value in D into *SP, then SP++
        return asm_code+["@SP","A=M","M=D","@SP","M=M+1"]

    def C_pop(self,command):
        """
        generate assembly codes for pop commands
        @para command (list of str): the pop command to be translated
        """
        #compute the address
        if command[0] in ["local","argument","this","that"]:
            asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"D=M+D","@R15","M=D"]
        elif command[0] in ["temp","pointer"]:
            asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"D=A+D","@R15","M=D"]
        elif command[0] == "static":
            symbol="@"+self.vm_filename[:-3]+"."+command[1]
            asm_code=[symbol,"D=M","@R15","M=D"]

        # put the value *SP into M[address],then SP--
        return asm_code+["@SP","AM=M-1","D=M","@R15","A=M","M=D"]

    def save_file(self):
        """
        save self.asm_codes into Xxx.asm file
        """
        output_path=os.path.join(self.rela_path,self.asm_filename)
        with open(output_path,'w') as file:
            for line in self.asm_codes:
                file.write(line+'\n')

def main():
    file_path=sys.argv[1]
    vmtranslator=VMTranslator(file_path)
    vmtranslator.save_file()

if __name__ == '__main__':
    main()
