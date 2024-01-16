import ply.lex as lex
from ply.lex import TOKEN
import sys
from pretreatment import Pretreatment,verbose


tokens = (
    'ID',
    
    'RIGHT_ASG',
    'LEFT_ASG',
    'MOD_ASG',
    'ADD_ASG',
    'AND_ASG',
    'XOR_ASG',
    'OR_ASG',
    'SUB_ASG',
    'MUL_ASG',
    'DIV_ASG',

    'COMMENT1',
    'COMMENT2',
    
    'EQ_OP',
    'NEQ_OP',

    'INC_OP',
    'DEC_OP',
    'PTR_OP',
    'AND_OP',
    'OR_OP',

    'RIGHT_OP',
    'LEFT_OP',

    
    'GTE',
    'LTE',

    'BUILT_IN_FUNCTION',
    
    'CHAR_CONST',
    'BOOL_CONST', 
    'FLOAT_CONST',
    'INTEGER_CONST',
    'STRING_CONST',

)




t_RIGHT_OP = r'>>'
t_LEFT_OP = r'<<'
t_INC_OP = r'\+\+'
t_DEC_OP = r'--'
t_PTR_OP = r'->'
t_AND_OP = r'&&'
t_OR_OP = r'\|\|'
t_EQ_OP = r"=="
t_NEQ_OP = r"!="

t_RIGHT_ASG = r'>>='
t_LEFT_ASG = r'<<='
t_XOR_ASG = r'\^='
t_OR_ASG = r'\|='

t_ADD_ASG = r'\+='
t_SUB_ASG = r'-='
t_MUL_ASG = r'\*='


t_LTE = r"\<\="
t_GTE = r"\>\="

t_DIV_ASG = r'/='
t_MOD_ASG = r'%='
t_AND_ASG = r'&='

t_ignore  = ' \t\v\f'


literals = "+-*/%|&~^<>=!?()[]{}.,;:\\\'\""


# C++ ID
def t_ID(t):
    r"[_a-zA-Z][_a-zA-Z0-9]*"
    if t.value.lower() in reserved_keywords:
        t.type = reserved_keywords[t.value.lower()]
    return t

# 匹配以单引号包围的字符常量
def t_CHAR_CONST(t):
    r'(L)?\'([^\\\n]|(\\(.|\n)))*?\''
    return t


# 匹配不同形式的整数常量，包括十进制、十六进制
# 前一部分匹配数字，后一部分匹配代表四种可能的后缀组合，包括 ul、lu、u 或 l
def t_INTEGER_CONST(t):
    r'(((((0x)|(0X))[0-9a-fA-F]+)|(\d+))([uU][lL]|[lL][uU]|[uU]|[lL])?)'
    return t

# 匹配小数点表示的浮点数和匹配科学计数法表示的浮点数
# 小数点表示中支持指数表示
def t_FLOAT_CONST(t):
    r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
    return t


# bool类型
def t_BOOL_CONST(t):
    r'(true|false)'
    return t

# 被“”修饰的字符串
def t_STRING_CONST(t):
    r'"(\\.|[^\\"])*"'
    return t



def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 错误处理
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# \\类型的注释
def t_COMMENT1(t):
    r'(//.*?(\n|$))'
    return t

# /**/类型的注释
def t_COMMENT2(t):
    r'(/\*(.|\n)*?\*/)'
    t.value = t.value.replace(' ','')
    t.value = t.value.replace('\n',' ')
    return t





reserved_keywords = {
    'asm': 'ASM',
    'auto': 'AUTO',
    'bool': 'BOOL',
    'break': 'BREAK',
    'case': 'CASE',
    'catch': 'CATCH',
    'char': 'CHAR',
    'class': 'CLASS',
    'const': 'CONST',
    'const_cast': 'CONST_CAST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'delete': 'DELETE',
    'do': 'DO',
    'double': 'DOUBLE',
    'dynamic_cast': 'DYNAMIC_CAST',
    'else': 'ELSE',
    'enum': 'ENUM',
    'explicit': 'EXPLICIT',
    'export': 'EXPORT',
    'extern': 'EXTERN',
    'float': 'FLOAT',
    'for': 'FOR',
    'friend': 'FRIEND',
    'goto': 'GOTO',
    'if': 'IF',
    'inline': 'INLINE',
    'int': 'INT',
    'long': 'LONG',
    'mutable': 'MUTABLE',
    'namespace': 'NAMESPACE',
    'new': 'NEW',
    'operator': 'OPERATOR',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
    'register': 'REGISTER',
    'reinterpret_cast': 'REINTERPRET_CAST',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'static_cast': 'STATIC_CAST',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'template': 'TEMPLATE',
    'this': 'THIS',
    'throw': 'THROW',
    'try': 'TRY',
    'typedef': 'TYPEDEF',
    'typeid': 'TYPEID',
    'typename': 'TYPENAME',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'using': 'USING',
    'virtual': 'VIRTUAL',
    'void': 'VOID',
    'volatile': 'VOLATILE',
    'restrict':'RESTRICT',
    'while': 'WHILE',
}

# 将预定义的关键字列表中的所有值添加到 tokens 列表中
# reserved_keywords.values() 返回一个包含所有值的可迭代对象
# 使用 tuple() 函数将其转换为元组，然后通过 + 运算符将其与 tokens 列表连接起来
# 这样做是为了确保词法分析器能够识别并处理这些关键字。
tokens = tokens + tuple(reserved_keywords.values())


lexer = lex.lex()

if __name__ == '__main__':
    if len(sys.argv) > 1:  # specify file
        try:
            pretreatmenter=Pretreatment()
            cooked_file, ok=pretreatmenter.Pretreatment(sys.argv[1])
            if verbose:
                print(f'cooked_file: {cooked_file}')
            if ok is not True:
                print('Pretreatment error with file:', cooked_file)
            else:
                lexer.input(cooked_file)
                while True:
                    token = lexer.token()
                    if not token:
                        break  # not input
                    print(token)
        except Exception as e:
            print(e)
    else:
        print("please specify the c++ file path")

