import os
import sys
from JackCompiler import JackCompiler
    

def compile_file(input_file,output_file):
    jack_codes=[]
    with open(input_file,'r') as file:
        for line in file:
            _line=line.strip()
            if len(_line)==0 or _line[0]=='/' or _line[0]=='*':
                continue
            if _line.find('//')!=-1:
                _line=_line[:_line.find('//')]
            jack_codes.append(_line.strip())
    compiler=JackCompiler(jack_codes)
    compiler.tokenize()
    compiler.compileClass()
    with open(output_file,'w') as file:
        for line in compiler.codes:
            file.write(line+'\n')
    

def main():
    assert len(sys.argv)>=2,"please enter a filename of dir"
    argument_path=os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        jack_files=[os.path.join(argument_path,filename) for filename in os.listdir(argument_path)]
    else:
        jack_files=[argument_path]
    for input_path in jack_files:
        filename,extension=os.path.splitext(input_path)
        if extension.lower()!=".jack":
            continue
        output_path=filename+".vm"
        compile_file(input_path,output_path)
            
    
if __name__=='__main__':
    main()
