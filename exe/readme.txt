环境配置：
ubuntu20.04

sudo apt-get install clang
sudo apt-get install llvm
pip install PLY

还需安装对应版本的llvmlite，具体方式见report.pdf

运行方式：
在根目录下运行： python src/lexer.py exe/helloworld.cpp

程序将输出token流，可以用定向符把它存储到文本文件中：

python src/lex.py exe/helloworld.cpp > token_test.txt