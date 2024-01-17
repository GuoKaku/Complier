环境配置：
ubuntu20.04

sudo apt-get install clang
sudo apt-get install llvm
pip install PLY

还需安装对应版本的llvmlite，具体方式见report.pdf

运行方式：
要得到helloworld.cpp的token流，则在根目录下运行： python src/lexer.py exe/helloworld.cpp

程序将输出token流，可以用定向符把它存储到文本文件中：

python src/lex.py exe/helloworld.cpp > token_test.txt

要得到helloworld.cpp的语法分析树，则在根目录下运行：python src/Parser.py exe/helloworld.cpp

程序将生成语法分析树文件，在源程序同目录下，文件名为helloworld_syntree.json

要把helloworld.cpp翻译成等价的llvm代码，则在根目录下运行：python src/cpp2llvm.py exe/helloworld.cpp

程序将生成llvm代码文件，在源程序同目录下，文件名为helloworld_llvm.ll。

输入lli exe/helloworld_llvm.ll即可运行llvm代码程序。r