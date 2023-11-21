import os
import sys

class JackAnalyzer:

    def __init__(self, file_path):
        self.jack_files=[]
        
        if os.path.isdir(file_path):
            for file in os.listdir(file_path):
                if file[-4:]=="jack":
                    self.jack_files.append(os.path.join(file_path,file))
            assert len(self.jack_files)>0,"please choose a dir with Xxx.jack files in it"
            self.xml_filename=file[:-5]+"3.xml"
            self.xml_T_filename=file[:-5]+"2.xml"
            self.output_path=file_path
        else:
            suffix=file_path[file_path.find(".")+1:]
            assert suffix=="jack","please choose an input file name Xxx.jack"
            self.jack_files=[file_path]
            self.xml_filename=file_path[:-5]+"3.xml"
            self.xml_T_filename=file_path[:-5]+"2.xml"
            if file_path.find('/')==-1:
                self.output_path=os.getcwd()
            else:
                self.output_path=file_path[:file_path.rfind('/')]
        
        for file in self.jack_files:
            single_analyzer=SingleJackAnalyzer(file,self.output_path,self.xml_T_filename,self.xml_filename)
            single_analyzer.tokenize()
            single_analyzer.parse()
            
class SingleJackAnalyzer:
    
    def __init__(self,file_path,out_path,xml_T_name,xml_name):
        self.output_path=out_path
        self.xml_T_filename=xml_T_name
        self.xml_filename=xml_name
        self.jack_filename=os.path.basename(file_path)
        self.xml_text=[]
        self.part=[]
        self.tokens=['<tokens>']
        self.codes=[]
        self.keywords=['class','constructor','function','method','field','static','var','int','char','boolean', 'void','true', 'false' ,'null','this','let','do','if','else','while','return']
        self.symbols=['{','}', '(' ,')', '[', ']' ,'.',',' ,';' , '+','-' ,'*' ,'/' , '&' , '|', '<' , '>','=' , '~']
        with open(file_path,'r') as file:
            for line in file:
                _line=line.strip()
                if len(_line)==0 or _line[0]=='/' or _line[0]=='*':
                    continue
                if _line.find('//')!=-1:
                    _line=_line[:_line.find('//')]
                self.codes.append(_line.strip())
    
    def token_type(self,token):
        if token in self.keywords:
            return 'KEYWORD'
        elif token in self.symbols:
            return 'SYMBOL'
        elif token.isdigit():
            return 'INT'
        elif token[0]=='"':
            return 'STR'
        else:
            return 'IDENTIFIER'
        
    def write_token(self,token):
        self.part+=[token]
        if self.token_type(token)=='KEYWORD':
            return '<keyword> '+token+' </keyword>'
        elif self.token_type(token)=='SYMBOL':
            if token=='<':
                token='&lt;'
            elif token=='>':
                token='&gt;'
            elif token=='"':
                token='&quot;'
            elif token=='&':
                token='&amp;'
            return '<symbol> '+token+' </symbol>'
        elif self.token_type(token)=='INT':
            return '<integerConstant> '+token+' </integerConstant>'
        elif self.token_type(token)=='STR':
            return '<stringConstant> '+token[1:]+' </stringConstant>'
        else:
            return '<identifier> '+token+' </identifier>'
    
    def tokenize(self):
        for code in self.codes:
            i=0
            while i<len(code):
                j=i
                if j<len(code) and code[i]=='"':
                    j=j+1
                    while code[j]!='"':
                        j=j+1
                    self.tokens+=[self.write_token(code[i:j])]
                    i=j+1
                    continue
                while j<len(code) and code[j]!=' ' and code[j] not in self.symbols:
                    j=j+1
                if j<len(code) and code[j]==' 'and i!=j:
                    self.tokens+=[self.write_token(code[i:j])]
                    i=j
                elif j<len(code) and code[j] in self.symbols:
                    if i!=j:
                        self.tokens+=[self.write_token(code[i:j])]
                    self.tokens+=[self.write_token(code[j])]
                    i=j
                i=i+1
        self.tokens+=['</tokens>']
        output=os.path.join(self.output_path,self.xml_T_filename)
        with open(output,'w') as file:
            for line in self.tokens:
                file.write(line+'\n')

    def compileClass(self):
        self.xml_text+=['<class>']
        #'class'
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #class name
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #{
        self.xml_text+=[self.write_token(self.part.pop(0))]
        while self.part[0]!='}':
            if self.part[0]=='static' or self.part[0]=='field':
                self.compileClassVarDec()
            elif self.part[0] in ['constructor', 'function', 'method']:
                self.compileSubroutineDec()
            else:
                break
        #print(self.xml_text)
        #}
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</class>']
        #print(self.xml_text)
    
    def compileClassVarDec(self):
        self.xml_text+=['<classVarDec>']
        #filed or static
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #type
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #name
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #more variables
        while self.part[0]==',':
            self.xml_text+=[self.write_token(self.part.pop(0))]
            self.xml_text+=[self.write_token(self.part.pop(0))]
        #;
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</classVarDec>']
        
    def compileSubroutineDec(self):
        self.xml_text+=['<subroutineDec>']
        #constructor...
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #return type
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #subroutine name
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #(
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #parameterList
        self.xml_text+=['<parameterList>']
        while self.part[0]!=')':
            self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</parameterList>']
        #)
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.compileSubroutineBody()
        self.xml_text+=['</subroutineDec>']
    
    def compileSubroutineBody(self):
        self.xml_text+=['<subroutineBody>']
        #{
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #varDec
        while self.part[0]=='var':
            self.compileVarDec()
        #statements
        self.compileStatements()
        #}
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</subroutineBody>']
    
    def compileStatements(self):
        self.xml_text+=['<statements>']
        while self.part[0]!='}':
            if self.part[0]=='let':
                self.compileLet()
            elif self.part[0]=='if':
                self.compileIf()
            elif self.part[0]=='while':
                self.compileWhile()
            elif self.part[0]=='do':
                self.compileDo()
            elif self.part[0]=='return':
                self.compileReturn()
        self.xml_text+=['</statements>']
    
    def compileLet(self):
        self.xml_text+=['<letStatement>']
        #let
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #varName
        self.xml_text+=[self.write_token(self.part.pop(0))]
        if self.part[0]=='[':
            #[
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #expression
            self.compileExpression()
            #]
            self.xml_text+=[self.write_token(self.part.pop(0))]
        #=
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #expression
        self.compileExpression()
        #;
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</letStatement>']
        #print(self.xml_text)
    
    def compileIf(self):
        self.xml_text+=['<ifStatement>']
        #if
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #(
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #expression
        self.compileExpression()
        #)
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #{
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #statements
        self.compileStatements()
        #}
        self.xml_text+=[self.write_token(self.part.pop(0))]
        if self.part[0]=='else':
            #else
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #{
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #statements
            self.compileStatements()
            #}
            self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</ifStatement>']
        print(self.xml_text)
    
    def compileWhile(self):
        self.xml_text+=['<whileStatement>']
        #while
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #(
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #expression
        self.compileExpression()
        #)
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #{
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #statements
        self.compileStatements()
        #}
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</whileStatement>']
        print(self.xml_text)
    
    def compileSubrourineCall(self):
        while self.part[0]!='(':
            self.xml_text+=[self.write_token(self.part.pop(0))]
        #(
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #expressionList
        self.compileExpressionList()
        #)
        self.xml_text+=[self.write_token(self.part.pop(0))]
    
    def compileDo(self):
        self.xml_text+=['<doStatement>']
        #do
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #subroutineCall
        self.compileSubrourineCall()
        #;
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</doStatement>']
        #print(self.xml_text)
    
    def compileExpressionList(self):
        self.xml_text+=['<expressionList>']
        while self.part[0]!=')':
            self.compileExpression()
            if self.part[0]==',':
                self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</expressionList>']
        
        
    def compileReturn(self):
        self.xml_text+=['<returnStatement>']
        #return
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #expression
        if self.part[0]!=';':
            self.compileExpression()
        #;
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</returnStatement>']
        
        
    def compileVarDec(self):
        self.xml_text+=['<varDec>']
        #var
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #type
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #varName
        self.xml_text+=[self.write_token(self.part.pop(0))]
        while self.part[0]==',':
            #,
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #varName
            self.xml_text+=[self.write_token(self.part.pop(0))]
        #;
        self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</varDec>']
        
    def compileTerm(self):
        self.xml_text+=['<term>']
        if self.part[1]=='.':
            self.compileSubrourineCall()
        elif self.part[0]=='(':
            #(
            self.xml_text+=[self.write_token(self.part.pop(0))]
            while self.part[0]!=')':
                self.compileExpression()
            #)
            self.xml_text+=[self.write_token(self.part.pop(0))]
        elif self.part[0] in ['~','-']:
            self.xml_text+=[self.write_token(self.part.pop(0))]
            self.compileTerm()
        elif self.part[1]=='[':
            #array name
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #[
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #expression
            self.compileExpression()
            #]
            self.xml_text+=[self.write_token(self.part.pop(0))]
        else:
            self.xml_text+=[self.write_token(self.part.pop(0))]
        self.xml_text+=['</term>']
        
    def compileExpression(self):
        #print(self.xml_text)
        self.xml_text+=['<expression>']
        self.compileTerm()
        if self.part[0] in ['+','-','*','/','&','|','<','>','=']:
            #+...
            self.xml_text+=[self.write_token(self.part.pop(0))]
            #term
            self.compileTerm()
        self.xml_text+=['</expression>']
        #print(self.xml_text)
        '''if self.part[0] in ['+','-','*','/','&','|','<','>','=']:
        #+...
        self.xml_text+=[self.write_token(self.part.pop(0))]
        #term
        self.compileTerm()'''
    
    def parse(self):
        self.compileClass()
        self.save_file()
            
    
    def save_file(self):
        output=os.path.join(self.output_path,self.xml_filename)
        with open(output,'w') as file:
            for line in self.xml_text:
                file.write(line+'\n')

def main():
    assert len(sys.argv)>=2,"please enter a filename of dir"
    file_path=sys.argv[1]
    jackanalyzer=JackAnalyzer(file_path)
    
if __name__=='__main__':
    main()
