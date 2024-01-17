# cpp2llvm词法分析与语法分析

林敏芝 王皓雯 郭嘉伟

## 选题与工具

源语言：C++

目标语言：LLVM（LLVM 架构的中间代码，可以使用LLVM工具编译成机器代码

使用python-lex-yacc

## 开发环境

操作系统：ubuntu 20.04

安装库：

```
sudo apt-get install clang
sudo apt-get install llvm
pip install PLY
```

并安装与已安装llvm版本对应的llvmlite。

## 运行方式
+ 词法分析：对需要翻译的C++语言文件`test.cpp`，运行以下命令

``` bash
python src/lexer.py exe/test.cpp
```

程序将输出token流，可以用定向符把它存储到文本文件中：

``` bash
python src/lexer.py exe/test.cpp > token_test.txt
```

+ 语法分析
``` bash
python src/myYacc.py exe/test.cpp
```
会把生成的json格式的语法分析树保存在test.cpp源文件同目录下，以test为例，会命名为test_syntree.json

	

## 支持的功能
### 词法分析部分

+ 预处理`#include`和`#define`
+ 词法分析的错误处理：遇到错误（无法匹配识别的部分）时不会阻塞，会打印报错信息并继续进行编译

### 语法分析部分
+ 支持函数、变量、数组（高维）、结构体声明
+ 支持精确的类型定义（如unsigned int）
+ 支持表达式解析（包括一元、二元、三元和赋值表达式）
+ 支持参数列表、列表式声明（如int a=1, *b, c = 2+3）
+ 支持分支、循环、跳出语句
+ 支持（多重）指针的解析
+ 支持注释插入语法树中

### 语义分析部分
+ 支持将注释插入llvm中
+ 定义注释对应的TOKEN
+ 编写注释对应的语法规则
+ 定义注释对应的语法分析结点
+ 产生包含注释的语法分析树
+ 生成LLVM注释代码


## 难点与创新点

### 词法分析

#### 预处理

在进行匹配token前，需要预处理C++中由`#`开头的预处理命令，主要是对`#include`、`#define`进行预处理。

首先，逐行读入需要处理的文件，去除原文件中所有的空格、换行符等C++语言中无意义字符。

```python
line = line.strip(' ').strip('\t').strip('\r').strip('\n')
```

**通过搜索由`#include`开头的行来处理头文件**：对于头文件名被`""`修饰的自定义库，根据引号内的文件名构造绝对路径，并将其添加到需要读取的文件列表中；对于头文件名被`<>`修饰的标准库直接跳过，后续对库函数进行单独处理。处理后，将这些行从原始串中删去。

递归地预处理需要读取的文件列表，将所有函数和类的定义都粘贴进处理后的串。在递归时，通过**条件编译语句` #if、#ifdef、#ifndef`等判断是否重复处理**，防止进入死循环或进行冗余处理。

**搜索由`#define`开头的行来处理**：遍历所有定义宏语句，将其名称和定义的内容添加至定义列表中。在遍历匹配串中所有存在的宏名称，替换为定义的内容。

预处理后，将得到的串返回。

#### 词法分析中正则表达式

见`lex.py`代码中注释，解释其功能和正确性。

对于c++代码中的存在的注释，通过正则表达式识别`//`和`/**/`两种，对其进行识别，期望能最终转化为llvm中的注释，提高转化出的代码的可读性。

#### 错误处理

预处理中，对所有由`#`开头且不是`#include #define`或者条件编译语句` #if、#ifdef、#ifndef`等的行，打印错误提示并跳过，继续处理。

词法分析中，对所有无法与已存在token匹配的，打印错误提示并跳过，继续匹配token。

### 语法分析

#### PLY库
PLY库的语法分析需要在给定语法规则的同时，手动构造个对应语法规则的解析器，比较麻烦

#### 注释处理
在两个地方插入了注释操作：一是cpp文件所有函数定义之外，另一是函数体之中，实现方法是自定义了新的语法规则如
```declorcom   : comment | external_declaration```  这里declorcom表示要么是一个声明要么是一条注释。以及```block_item  : declaration | statement | comment```，表示函数体的一个项目要么是声明或者语句，要么是注释

#### 精确的类型标识符
支持int, unsigned, unsigned int（等同一系列的），同时对形如unsigned float的类型进行错误处理

#### 三元运算符
除了常规支持一元、二元运算符外，本项目的语法分析部分还可以支持c特有的三元运算符，由如下函数确定：
```
def p_conditional_expression(p):
    """ conditional_expression  : binary_expression 
                | ternary_expression
    """
    if len(p) == 2:
        p[0] = p[1]
        
def p_ternary_expression(p):
    """ternary_expression : expression '?' expression ':' expression
    """
    if len(p) == 6:
        args={'condition':p[1],'true':p[3],'false':p[5]}
        p[0] = myAST.Operation(OpType='TernaryOp',OpName=p[2],**args)
```

#### 区分左值右值
众所周知，右值（包括函数返回值、表达式计算值、或者常量右值）都不能进行赋值运算，我们考虑到了这一点。在语法规则中考虑到了
```
assignable_expression   : conditional_expression | variable assign_operator assignable_expression
```
这里表示我们的赋值运算只支持左值，varible就是一个左值量，而不能是任意表达式。

#### 对赋值运算符进行语法检查
c++（或者说c）中支持形如
```
    int a = 1;
    int b = a*=3 ;
```
的语法。其作用是先是a*=3，然后结果赋值给b。我们支持这个语法。

### 语义分析

#### 将注释插入llvm中

+ 在进行 C++ 到 LLVM 的转换过程中，将注释插入 LLVM 代码中是一项有用的操作，可以保留源代码中的重要信息，以便在后续调试和理解 LLVM 生成的代码时提供上下文。以下是如何实现这一步骤的概要：

+ 提取源代码注释信息： 在进行语法分析和生成 AST（抽象语法树）的过程中，将源代码中的注释信息保留下来。这可以通过词法分析器和语法分析器的协作来实现。确保注释信息与相应的代码段关联。
在生成 LLVM 代码时插入注释： 在生成 LLVM IR（中间表示）代码的过程中，根据之前提取的注释信息，将注释插入到合适的位置。通常，LLVM IR 中可以使用 ; 符号来添加单行注释，也可以使用 /* */ 来添加多行注释。

+ 确保注释不影响 LLVM 代码的正确性： 插入注释时要确保不会影响生成的 LLVM 代码的语法和语义正确性。注释应该被视为额外的信息而不是影响程序逻辑的部分。

#### 



## 分工

|        | 词法分析阶段                                               | 语法分析阶段             |语义分析阶段
| ------ | ---------------------------------------------------------- | ------------------------ | ------------------------ |
| 郭嘉伟 | 编写预处理`#include`、`#define`、`#ifndef`，查找C++标准    | 处理注释、语法规则整理编写,生成语法树代码编写 | 语法树处理调研、前阶段对接
| 林敏芝 | 搭建框架、工具调研、正则表达式设计、注释处理、测试代码编写 | 语法规则调研、调研语法解析器使用        | 语法树处理调研、结果调试
| 王皓雯 | 搭建框架、工具调研、完成token列表                          |  检查声明正确性、调研语法解析器使用    | 语义树处理代码编写、代码翻译代码编写


## 参考

C语言标准：https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf

https://blog.csdn.net/keke193991/article/details/17566937

https://blog.csdn.net/qq_41687938/article/details/119349135
