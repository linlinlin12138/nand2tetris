import sys
import os

class VMtranslator:
    def __init__(self, file_path):
        self.codes=[]
        self.assembly=[]
        self.segment_table={"constant":"SP","local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
        self.arithmetic_table={"add":"+","sub":"-","neg":"-","eq":"=","gt":">","lt":"<","and":"And","or":"Or","not":"Not"}
        self.file_name=os.path.basename(file_path)
        suffix=self.file_name[-2:]
        assert suffix=="vm","please choose an input named like xxx.vm"
        with open(file_path,'r') as file:
            for line in file:
                _line=line.strip()
                if len(_line)==0 or _line[0]=="/":
                    continue
                if _line.find('/')!=-1:
                    _line=_line[:_line.find('/')]
                self.codes.append(_line.strip())
    
    def parse(self):
        for line in self.codes:
            push_index=line.find("push")
            pop_index=line.find("pop")
            if push_index!=-1:
                self.push_command(line[push_index+5:])
            elif pop_index!=-1:
                self.pop_command(line[pop_index+4:])
            else:
                self.other_command(line)
    
    def find_pos(self,command):
        space_index=command.find(" ")
        if command.find("static")!=-1:
            pos=self.file_name[:-3]+"."+command[space_index+1:]
        elif command.find("temp")!=-1:
            pos=str(5+int(command[space_index+1:]))
        elif command.find("pointer")!=-1:
            if command[space_index+1:]=="0":
                pos="THIS"
            else:
                pos="THAT"
        else:
            pos=self.segment_table[command[:space_index]]
        return pos
        
                
    def push_command(self,command):
        pos=self.find_pos(command)
        space_index=command.find(" ")
        if command.find("temp")!=-1 or command.find("pointer")!=-1:
            code_temp="@"+pos+"\n"+"D=M"+"\n"+"@SP"+"\n"+"A=M"+"\n"+"M=D"+"\n"+"@SP"+"\n"+"M=M+1"+"\n"
        else:
            code_get_i="@"+command[space_index+1:]+"\n"+"D=A"+"\n"
            code_address="@"+pos+"\n"+"D=M+D"+"\n"+"A=D"+"\n"+"D=M"+"\n"
            code_change="@SP"+"\n"+"A=M"+"\n"+"M=D"+"\n"+"@SP"+"\n"+"M=M+1"+"\n"
            if command[:space_index]=="constant":
                self.assembly.append(code_get_i)
                self.assembly.append(code_change)
            else:
                self.assembly.append(code_get_i)
                self.assembly.append(code_address)
                self.assembly.append(code_change)
        
    def pop_command(self, command):
        pos=self.find_pos(command)
        if command.find("temp")!=-1 or command.find("pointer")!=-1:
            code_temp="@SP"+"\n"+"M=M-1"+"\n"+"A=M"+"\n"+"D=M"+"\n"+"@"+pos+"\n"+"M=D"+"\n"
            self.assembly.append(code_temp)
        else:
            space_index=command.find(" ")
            code_get_i="@"+command[space_index+1:]+"\n"+"D=A"+"\n"
            code_address="@"+pos+"\n"+"M=M+D"+"\n"
            code_change="@SP"+"\n"+"M=M-1"+"\n"+"A=M"+"\n"+"D=M"+"\n"+"@"+pos+"\n"+"A=M"+"\n"+"M=D"+"\n"
            code_recover="@"+pos+"\n"+"M=M-D"+"\n"
            self.assembly.append(code_get_i)
            self.assembly.append(code_address)
            self.assembly.append(code_change)
            self.assembly.append(code_get_i)
            self.assembly.append(code_recover)
        
    
    def other_command(self,command):
        code1="@SP"+"M=M-1"+"\n"+"A=M"+"\n"+"M="+self.arithmetic_table[command]+"M"+"\n"
        code2="@SP"+"\n"+"M=M-1"+"\n"+"A=M"+"\n"+"D=M"+"\n"+"A=A-1"+"\n"+"M=M"+self.arithmetic_table[command]+"D"+"\n"
        if command=="neg" or command=="not":
            self.assembly.append(code1)
        else:
            self.assembly.append(code2)
    
    def save(self):
        new_filename=self.file_name[:-3]+".asm"
        with open(new_filename,'w') as file:
            for line in self.assembly:
                file.write(line)
                
def main():
    file_path=sys.argv[1]
    vm=VMtranslator(file_path)
    vm.parse()
    vm.save()
    
if __name__=='__main__':
    main()

