import sys
import json
from tool import Tool
from Parser import parser
from pretreatment import Pretreatment
tool = Tool()



def main():
    if len(sys.argv) == 1:
        print("please specify the c++ file path")
        return
    
    pretreatmenter=Pretreatment()
    param = sys.argv[1]
    file_data, flag=pretreatmenter.Pretreatment(param)
    if not flag:
        print('pretreatment error')
        return
    result = tool.getcode(parser.parse(file_data))
    save_path = sys.argv[1][:-len('.cpp')] + '_llvm.ll' if len(sys.argv) <= 2 else sys.argv[2]
    print(result,file=open(save_path, 'w+'))
    with open(save_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[4:]
    with open(save_path, 'w', encoding='utf-8') as w:
        for l in lines:
            w.write(l)
    print("the llvm program is saved at {}.".format(save_path))


if __name__ == '__main__':
    main()
