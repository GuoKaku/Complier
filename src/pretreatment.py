import re
import os

class Pretreatment:
    def __init__(self) -> None:
        self.macros={}
        self.cooked_lines=[]
        self.includes={}
        
    def __FindEndifPos(self,lines,start_pos):
        for i in range(start_pos,len(lines)):
            line=lines[i].strip(' ').strip('t').strip('\r').strip('\n')
            if len(line)>0 and line[0]=='#':
                cmd=line[1:].strip(' ').strip('t').strip('\r').strip('\n').split()
                if cmd[0]=="endif":
                    return i
        return None
    
    def Pretreatment(self,filename):
        filedir=os.path.dirname(filename)
        nameoffile = filename.split('/')[-1]
        filename=os.path.join(filedir,nameoffile)
        self.includes[filename]="not_yet_processed"
        done=False
        while not done:
            done=True
            now_length=len(self.includes)
            for i in range(now_length):
                file=list(self.includes.keys())[i]
                if self.includes[file]=="not_yet_processed":
                    msg,ok=self.pretreatment_single(file)
                    if not ok:
                        return f"{file} failed: \nerror detail: {msg}",False
                    self.includes[file]="processed"
                    
            for value in self.includes.values():
                if value=="not_yet_processed":
                    done=False
                    break
        data='\n'.join(self.cooked_lines)
        
        
        for key,value in self.macros.items():
            if value is not None:
                data= re.sub(key, value, data)
        
        return data,True

                
    
    def pretreatment_single(self,filename):
    
        try:
            f = open(filename, "r")
            data = f.read()
            f.close()
        except FileNotFoundError as e:
            return str(e), False

        lines=data.split('\n')
        filedir=os.path.dirname(filename)
        includes=[]
        i=0

        while i < len(lines):
            line=lines[i]
            line=line.strip(' ').strip('t').strip('\r').strip('\n')
            if(len(line)==0): pass
            elif(line[0]=='#'):
                cmd=line[1:].split() #除去多余的空白字符，严格保持#后的内容是#A B C的形式，不然#A  B    C多空格会报错
                if cmd[0]=='include':
                    try: 
                        file_to_include=cmd[1]
                        if file_to_include[0]=='"' and file_to_include[-1]=='"':
                            includes.append(os.path.join(filedir,file_to_include[1:-1]))
                        elif file_to_include[0]=='<' and file_to_include[-1]=='>':
                            pass
                        else:
                            return "invalid include format", False
                    except IndexError:
                        return "include file not specified",False
                    except FileNotFoundError as e:
                        return f"Header file not found: {e.filename}",False
                elif cmd[0]=='define':
                    
                    if len(cmd)>=3:
                        if cmd[1] in self.macros.keys() and self.macros[cmd[1]]!=cmd[2]:
                            return f"Macro redefination {cmd[1]}",False
                        else:
                            self.macros[cmd[1]]=cmd[2]
                    elif len(cmd)==2:  #仅定义了一个宏
                        self.macros[cmd[1]]=None
                    else:
                        return "improper define",False
                elif cmd[0]=="ifndef":
                    now_macro=cmd[1]
                    endif_pos=self.__FindEndifPos(lines,i+1)
                    if endif_pos==None:
                        return f"lack #endif for #ifnedf {now_macro}",False
                    else:  #正常编译
                        if now_macro in self.macros.keys(): #已经define了，不需要在做
                            i=endif_pos+1
                        else:
                            pass
                elif cmd[0]=="ifdef":
                    now_macro=cmd[1]
                    endif_pos=self.__FindEndifPos(lines,i+1)
                    if endif_pos==None:
                        return f"lack #endif for #ifedf {now_macro}",False
                    else:
                        if now_macro not in self.macros.keys(): #已经define了，不需要在做
                            i=endif_pos+1
                        else: #正常编译
                            pass
                elif cmd[0]=="endif":
                    pass 
                else:
                    return f"symbol{cmd[0]} cannot be recognized",False
            else: #正常的一行
                self.cooked_lines.append(line)
            i+=1;    #处理下一行
            
        self.cooked_lines.append('\n')
        
        for inc_file in includes:
            if inc_file not in self.includes.keys():
                self.includes[inc_file]="not_yet_processed"
        
            
        return f"File {filename} pretreatment complete",True
    
        
        