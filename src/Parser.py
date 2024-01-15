import re
import ply.yacc as yacc
import SynTree as SynTree
from lexer import *
from utility import handle_decl_change

# 开始


def p_starter(p):
    """ start   : part
                | empty
    """
    p[0] = SynTree.FirstNode(p[1]) if p[1] is not None else SynTree.FirstNode([])


def p_part(p):
    """ part    : part declorcom
                | declorcom
    """
    if len(p) > 2:
        if p[2] is not None:
            p[1].extend(p[2])
    p[0] = p[1]
    
    
def p_decl_or_comment_1(p):
    """ declorcom   : comment
    """
    p[0] = [p[1]]
    
def p_decl_or_comment_2(p):
    """ declorcom   : external_declaration
    """
    p[0] = p[1]
    

def p_initializer_ass(p):
    """ initializer : assignable_expression
    """
    p[0] = p[1]

def p_initializer_in(p):
    """ initializer : '{' initializer_list_orempty '}'
                    | '{' initializer_list ',' '}'
    """
    if p[2] is None:
        p[0] = SynTree.ContentList(listType='InitList',elements=[])
    else:
        p[0] = p[2]

def p_initializer_list(p):
    """ initializer_list    : initializer
                            | initializer_list ',' initializer
    """
    if len(p) == 2:
        init = p[1]
        p[0] = SynTree.ContentList(listType='InitList', elements=[init])
    else:
        init = p[3]
        p[1].elements.append(init)
        p[0] = p[1]

def p_variable_initable(p):
    """ variable_initable : variable
                        | variable '=' initializer
    """
    init_ = None
    if len(p) > 2:
        init_ = p[3]
    p[0] = dict(type=p[1], init=init_)

def p_variable_initable_list_idec(p):
    """ variable_initable_list    : variable_initable
                                | variable_initable_list ',' variable_initable
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

    



def p_empty(p):
    """ empty :
    """
    p[0] = None


def p_type(p):
    """ type  : type_specifier_can_unsigned
                                | type_specifier_cannot_unsigned 
                                | uorus
                                | uorus type_specifier_can_unsigned
    """
    if len(p)>2:
        print(type(p[1]))
        tmp = p[1] + p[2]
        print(type(tmp))
        p[0] = dict(qual=[], spec=[tmp])
    else:
        p[0] = dict(qual=[], spec=[p[1]])
        


def p_type_specifier(p):
    '''type_specifier : type_specifier_cannot_unsigned
                        | type_specifier_can_unsigned
                        | uorus '''

def p_type_specifier_cannot_unsigned(p):
    ''' type_specifier_cannot_unsigned : VOID
                       | FLOAT
                       | DOUBLE
                       | BOOL
                       | struct_specifier
    '''
    p[0] = p[1]
    
def p_type_specifier_can_unsigned(p):
    ''' type_specifier_can_unsigned : INT
                       | SHORT
                       | LONG
                       | CHAR
    '''
    p[0] = p[1]
    
def p_uorus(p):
    '''uorus   :          SIGNED
                       | UNSIGNED'''
    p[0]=p[1]

def p_declaration_list_orempty(p):
    """declaration_list_orempty : empty
                            | declaration_list
    """
    p[0] = p[1]

def p_declaration(p):
    """ declaration : type variable_initable_list_orempty ';'
    """
    decl_spec = p[1]
    struct = None
    if isinstance(decl_spec['spec'][0], SynTree.Struct):
        struct = decl_spec['spec'][0]
    init_decl_list = p[2]

    p[0] = []

    for init_decl in init_decl_list:
        type = init_decl['type']
        if struct is not None:
            if isinstance(type, SynTree.Identifier):
                args = {'name': type.name, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'], 'type': struct,
                       'init': init_decl['init']}
                declaration = SynTree.Decl(**args)

            else:
                while not isinstance(type.type, SynTree.Identifier):
                    type = type.type
                declname = type.type.name
                type.type = struct
                args = {'name': declname, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'], 'type': init_decl['type'],
                       'init': None}
                declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type, SynTree.Identifier):
                type = type.type
            type.spec = decl_spec['spec']
            args = {'name': type.name, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'], 'type': init_decl['type'],
                   'init': init_decl['init']}
            declaration = SynTree.Decl(**args)
        p[0].insert(0, declaration)

def p_declaration_list(p):
    """ declaration_list    : declaration
                            | declaration_list declaration
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_identifier_list_orempty(p):
    """identifier_list_orempty  : empty
                            | identifier_list
    """
    p[0] = p[1]

def p_identifier_list(p):
    """ identifier_list : identifier
                        | identifier_list ',' identifier
    """
    if len(p) == 2:
        p[0] = SynTree.ContentList(listType='ParamList', elements=[p[1]])
    else:
        p[1].elements.append(p[3])
        p[0] = p[1]

def p_identifier(p):
    """ identifier  : IDENTIFIER 
                    | inlinefunc """
    args = {'name': p[1], 'spec': None}
    p[0] = SynTree.Identifier(**args)
    
def p_inclinefunc(p):
    """ inlinefunc  : SIZEOF"""
    p[0] =p[1]

# 跳转
def p_back_statement_break(p):
    """ back_statement  : BREAK ';' """
    p[0] = SynTree.ControlLogic(logicType='Break')

def p_back_statement_continue(p):
    """ back_statement  : CONTINUE ';' """
    p[0] = SynTree.ControlLogic(logicType='Continue')

def p_back_statement_return(p):
    """ back_statement  : RETURN ';'
                        | RETURN expression ';'
    """
    if len(p)==3:
        args = {"return_result": None}
        p[0] = SynTree.ControlLogic(logicType='Return',**args)
    else:
        args={"return_result":p[2]}
        p[0] = SynTree.ControlLogic(logicType='Return',**args)


def p_variable_initable_list_orempty(p):
    """variable_initable_list_orempty  : empty
                            | variable_initable_list
    """
    p[0] = p[1]

def p_assignable_expression_orempty(p):
    """assignable_expression_orempty    : empty
                                    | assignable_expression
    """
    p[0] = p[1]


def p_assign_operator(p):
    ''' assign_operator : '='
                            | MUL_ASSIGN
                            | DIV_ASSIGN
                            | MOD_ASSIGN
                            | ADD_ASSIGN
                            | SUB_ASSIGN
                            | LEFT_ASSIGN
                            | RIGHT_ASSIGN
                            | AND_ASSIGN
                            | XOR_ASSIGN
                            | OR_ASSIGN '''
    p[0] = p[1]

def p_arg_value_exp_list(p):
    """ arg_value_exp_list    : assignable_expression
                                    | arg_value_exp_list ',' assignable_expression
    """
    if len(p) == 2:
        p[0] = SynTree.ContentList(listType='ExprList', elements=[p[1]])
    else:
        p[1].elements.append(p[3])
        p[0] = p[1]

def p_assignable_expression(p):
    """ assignable_expression   : conditional_expression
                                | unary_expression assign_operator assignable_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        args={'left':p[1],'right':p[3]}
        p[0] = SynTree.Operation(OpType='Assignment',OpName=p[2],**args)

def p_block_item_list_orempty(p):
    """block_item_list_orempty  : empty
                            | block_item_list
    """
    p[0] = p[1]

def p_constant_expression_orempty(p):
    """constant_expression_orempty  : empty
                            | constant_expression
    """
    p[0] = p[1]

def p_specifier_qualifier_list_orempty(p):
    """specifier_qualifier_list_orempty  : empty
                            | specifier_qualifier_list
    """
    p[0] = p[1]

# block
def p_block_item(p):
    """ block_item  : declaration
                    | statement
                    | comment
    """
    p[0] = p[1] if isinstance(p[1], list) else [p[1]]


def p_block_item_list(p):
    """ block_item_list : block_item
                        | block_item_list block_item
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        if p[2] == [None]:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]


def p_expression_orempty(p):
    """expression_orempty    : empty
                        | expression
    """
    p[0] = p[1]

def p_funcbody_statement(p):
    """ funcbody_statement : '{' block_item_list_orempty '}' """
    p[0] = SynTree.Blocks(
        blocks=p[2])

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
        p[0] = SynTree.Operation(OpType='TernaryOp',OpName=p[2],**args)
    
        


def p_constant_int(p):
    """ constant    : INTEGER_CONSTANT
    """
    p[0] = SynTree.Constant(
        'int', p[1], )

def p_constant_char(p):
    """ constant    : CHAR_CONSTANT
    """
    p[0] = SynTree.Constant(
        'char', p[1], )

def p_constant_float(p):
    """ constant    : FLOAT_CONSTANT
    """
    p[0] = SynTree.Constant(
        'float', p[1], )

def p_bool_constant(p):
    """ constant    : BOOL_CONSTANT
    """
    p[0] = SynTree.Constant(
        'bool', p[1], )

def p_constant_expression(p):
    """ constant_expression : conditional_expression """
    p[0] = p[1]

def p_variable_direct(p):
    """ variable  : direct_variable
    """
    p[0] = p[1]

def p_variable_pd(p):
    """ variable  : pointer direct_variable
    """
    p[0] = handle_decl_change(p[2], p[1])

def p_specifier_qualifier_list_ts(p):
    """ specifier_qualifier_list    : type specifier_qualifier_list_orempty
    """
    if p[2]:
        p[2]['spec'].insert(0, p[1])
        p[0] = p[2]
    else:
        p[0] = dict(qual=[], spec=[p[1]])


# 直接声明
def p_direct_variable_1(p):
    """ direct_variable   : identifier
    """
    p[0] = p[1]

def p_direct_variable_3(p):
    """ direct_variable   : direct_variable '[' assignable_expression_orempty ']'
    """
    print(3,p[3])
    args={'dim':p[3]}
    arr = SynTree.DeclArray(**args)

    p[0] = handle_decl_change(p[1], arr)

def p_direct_variable_6(p):
    """ direct_variable   : direct_variable '(' parameter_list ')'
                            | direct_variable '(' identifier_list_orempty ')'
    """
    args={'args':p[3]}
    func = SynTree.DeclFunction(**args)

    p[0] = handle_decl_change(p[1], func)

def p_external_declaration_1(p):
    """ external_declaration    : function_definition
    """
    p[0] = [p[1]]

def p_external_declaration_2(p):
    """ external_declaration    : declaration
    """
    p[0] = p[1]
    
    


# 表达式
def p_expression(p):
    """ expression  : assignable_expression
                    | expression ',' assignable_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if not isinstance(p[1], SynTree.ContentList):
            p[1] = SynTree.ContentList(listType='ExprList', elements=[p[1]])

        p[1].elements.append(p[3])
        p[0] = p[1]

def p_expression_statement(p):
    """ expression_statement : expression_orempty ';' """
    if p[1] is None:
        p[0] = SynTree.ControlLogic(logicType='EmptyStatement')
    else:
        p[0] = p[1]

def p_function_definition(p):
    """ function_definition : type variable declaration_list_orempty funcbody_statement
    """
    #variale is func(int a, int b, ...)
    decl_spec = p[1]
    struct = None
    if isinstance(decl_spec['spec'][0], SynTree.Struct):
        struct = decl_spec['spec'][0]
    type = p[2]

    if struct is not None:
        if isinstance(type, SynTree.Identifier):
            args={'name':type.name,'quals':decl_spec['qual'],'spec':decl_spec['spec'],'type':struct,'init':None}
            declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type.type, SynTree.Identifier):
                type = type.type
            declname = type.type.name
            type.type = struct
            args = {'name': declname, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'], 'type': p[2],
                   'init': None}
            declaration = SynTree.Decl(**args)

    else:
        while not isinstance(type, SynTree.Identifier):
            type = type.type
        type.spec = decl_spec['spec']
        args = {'name': type.name, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'], 'type': p[2],
               'init': None}
        declaration = SynTree.Decl(**args)

    fun_args = {'decl': declaration, 'param_decls': p[3], 'body': p[4]}
    p[0] = SynTree.FuncDef(**fun_args)



def p_parameter_list(p):
    """ parameter_list  : parameter_declaration
                        | parameter_list ',' parameter_declaration
    """
    if len(p) == 2:
        p[0] = SynTree.ContentList(listType='ParamList', elements=[p[1]])
    else:
        p[1].elements.append(p[3])
        p[0] = p[1]

def p_parameter_declaration(p):
    """ parameter_declaration   : type variable
    """
    decl_spec = p[1]
    struct = None
    if isinstance(decl_spec['spec'][0], SynTree.Struct):
        struct = decl_spec['spec'][0]
    type = p[2]

    if struct is not None:
        if isinstance(type, SynTree.Identifier):
            args = {'name': type.name, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'],
                   'type': struct,
                   'init': None}
            declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type.type, SynTree.Identifier):
                type = type.type
            declname = type.type.name
            type.type = struct
            args = {'name': declname, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'],
                   'type': p[2],
                   'init': None}
            declaration = SynTree.Decl(**args)
    else:
        while not isinstance(type, SynTree.Identifier):
            type = type.type
        type.spec = decl_spec['spec']
        args = {'name': type.name, 'quals': decl_spec['qual'], 'spec': decl_spec['spec'],
               'type': p[2],
               'init': None}
        declaration = SynTree.Decl(**args)

    p[0] = declaration

#usdc: unit, subscript, func call, depoint
def p_uscd_expression_1(p):
    """ uscd_expression : unit_expression """
    p[0] = p[1]

def p_uscd_expression_2(p):
    """ uscd_expression : uscd_expression '[' expression ']' """
    #p[0] = SynTree.ArrayRef(p[1], p[3])
    args = {'subscript': p[3]}
    p[0] = SynTree.Ref(refType='ArrayRef', name=p[1], **args)

def p_uscd_expression_3(p):
    """ uscd_expression : uscd_expression '(' arg_value_exp_list ')'
                            | uscd_expression '(' ')'
    """
    if len(p) == 5:
        args = {'name': p[1], 'args': p[3]}
    else:
        args = {'name': p[1], 'args': None}
    p[0] = SynTree.FunctionCall(**args)

def p_uscd_expression_4(p):
    """ uscd_expression : uscd_expression PTR_OP identifier
    """
    args1 = {'name': p[3], 'spec': None}
    field = SynTree.Identifier(**args1)
    args={'type':p[2],'field':field}
    p[0] = SynTree.Ref(refType='StructRef',name=p[1], **args)

def p_unit_expression_id(p):
    """ unit_expression  : identifier """
    p[0] = p[1]

def p_unit_expression_const(p):
    """ unit_expression  : constant """
    p[0] = p[1]

def p_unit_expression_mstring(p):
    """ unit_expression  : multiple_string
    """
    p[0] = p[1]

def p_unit_expression_bracket(p):
    """ unit_expression  : '(' expression ')' """
    p[0] = p[2]
    

    
    



def p_branch_statement_if(p):
    """ branch_statement : IF '(' expression ')' statement """
    args={'judge':p[3], 'action1':p[5], 'action2': None}
    p[0] = SynTree.ControlLogic('If',**args)

def p_branch_statement_ifelse(p):
    """ branch_statement : IF '(' expression ')' statement ELSE statement """
    args = {'judge': p[3], 'action1': p[5], 'action2': p[7]}
    p[0] = SynTree.ControlLogic('If', **args)


def p_loop_statement(p):
    """ loop_statement : WHILE '(' expression ')' statement """
    args={'judge':p[3],'action':p[5]}
    p[0] = SynTree.ControlLogic(logicType='While',**args)

def p_loop_statement_2(p):
    """ loop_statement : FOR '(' parameter_declaration ';' expression_orempty ';' expression_orempty ')'  statement
                        | FOR '(' expression ';' expression_orempty ';' expression_orempty ')'  statement
                        | FOR '(' empty ';' expression_orempty ';' expression_orempty ')'  statement
    """
    args={'first':p[3],'judge':p[5],'action':p[7], 'statement':p[9]}
    p[0] = SynTree.ControlLogic(logicType='For',**args)
    
def p_loop_statement_3(p):
    """ loop_statement : FOR '(' parameter_declaration '=' expression ';' expression_orempty ';' expression_orempty ')'  statement
    """
    args={'first':p[3],'judge':p[7],'action':p[9], 'statement':p[11]}
    p[0] = SynTree.ControlLogic(logicType='For',**args)


def p_statement(p):
    """ statement   : funcbody_statement
                    | branch_statement
                    | expression_statement
                    | loop_statement
                    | back_statement
    """
    p[0] = p[1]

def p_struct_specifier_1(p):
    """ struct_specifier   : STRUCT identifier
    """
    p[0] = SynTree.Struct(
        name=p[2].name,
        decls=None)

def p_struct_specifier_2(p):
    """ struct_specifier : STRUCT '{' struct_declaration_list '}'
    """
    p[0] = SynTree.Struct(
        name=None,
        decls=p[3])

def p_initializer_list_orempty(p):
    """initializer_list_orempty : empty
                            | initializer_list
    """
    p[0] = p[1]
def p_struct_specifier_3(p):
    """ struct_specifier   : STRUCT identifier '{' struct_declaration_list '}'
    """
    p[0] = SynTree.Struct(
        name=p[2].name,
        decls=p[4])

# Combine all declarations into a single list
#
def p_struct_declaration_list(p):
    """ struct_declaration_list     : struct_declaration
                                    | struct_declaration_list struct_declaration
    """
    if len(p) == 2:
        p[0] = p[1] or []
    else:
        p[0] = p[1] + (p[2] or [])

def p_struct_declaration(p):
    """ struct_declaration : type struct_variable_list ';'
    """
    p[0] = []
    struct_decl_list = p[2]
    spec_qual = p[1]
    struct = None
    if isinstance(spec_qual['spec'][0], SynTree.Struct):
        struct = spec_qual['spec'][0]

    for decl in struct_decl_list:
        type = decl
        while not isinstance(type, SynTree.Identifier):
            type = type.type
        if struct is not None:
            type.type = struct
            declname = type.type.name
        else:
            type.spec = spec_qual['spec']
            declname = type.name
        args = {'name': declname, 'quals': spec_qual['qual'], 'spec': spec_qual['spec'],
               'type': decl,
               'init': None}
        declaration = SynTree.Decl(**args)
        p[0].insert(0, declaration)


def p_struct_variable_list(p):
    """ struct_variable_list  : variable
                                | struct_variable_list ',' variable
    """
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_pointer(p):
    """ pointer : '*'
                | '*' pointer
    """
    args={'quals':p[1]}
    type_ = SynTree.DeclPointer(**args or [])
    if len(p) > 2:
        tail = p[2]
        while tail.type is not None:
            tail = tail.type
        tail.type = type_
        p[0] = p[2]
    else:
        p[0] = type_

# 一元运算
def p_unary_operator(p):
    ''' unary_operator : '&'
                       | '*'
                       | '+'
                       | '-'
                       | '~'
                       | '!' 
                       '''
                       
    p[0] = p[1]
    
def p_self_incdec_op(p):
    ''' self_incdec :   INC_OP
                       | DEC_OP
    '''
    p[0] = p[1]

def p_unary_expression_1(p):
    """ unary_expression    : uscd_expression"""
    p[0] = p[1]

def p_unary_expression_2(p):
    """ unary_expression    : unary_operator cast_expression
                            | self_incdec cast_expression
    """
    args={'expression':p[2]}
    p[0] = SynTree.Operation(OpType='UnaryOp',OpName=p[1],**args)
    
def p_unary_expression_3(p):
    """ unary_expression    : cast_expression self_incdec 
    """
    args={'expression':p[1]}
    p[0] = SynTree.Operation(OpType='UnaryOp',OpName=p[2],**args)
    

def p_multiple_string(p):
    """ multiple_string  : STRING_CONSTANT
                                | multiple_string STRING_CONSTANT
    """
    if len(p) == 2:
        p[0] = SynTree.Constant(
            'string', p[1])
    else:
        p[1].content = p[1].content[:-1] + p[2][1:]
        p[0] = p[1]

def p_binary_expression(p):
    """ binary_expression   : cast_expression
                            | binary_expression '*' binary_expression
                            | binary_expression '/' binary_expression
                            | binary_expression '%' binary_expression
                            | binary_expression '+' binary_expression
                            | binary_expression '-' binary_expression
                            | binary_expression RIGHT_OP binary_expression
                            | binary_expression LEFT_OP binary_expression
                            | binary_expression '<' binary_expression
                            | binary_expression LTE binary_expression
                            | binary_expression GTE binary_expression
                            | binary_expression '>' binary_expression
                            | binary_expression EQ_OP binary_expression
                            | binary_expression NEQ_OP binary_expression
                            | binary_expression '&' binary_expression
                            | binary_expression '|' binary_expression
                            | binary_expression '^' binary_expression
                            | binary_expression AND_OP binary_expression
                            | binary_expression OR_OP binary_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        args={'left':p[1],'right':p[3]}
        p[0] = SynTree.Operation(OpType='BinaryOp',OpName=p[2],**args)

def p_cast_expression_1(p):
    """ cast_expression : unary_expression """
    p[0] = p[1]

def p_comment(p):
    """  
        comment : COMMENT1
                | COMMENT2
    """
    p[0]=SynTree.CommentNode(p[1])
    



# C++相比C多出的特性，因为没有用到，暂时没有处理
def p_cpp_advanced(p):
    """ cpp_advanced : ASM
    | BUILT_IN_FUNCTION
    | CATCH
    | CLASS
    | COMMENT2
    | CONST_CAST
    | DELETE
    | DYNAMIC_CAST
    | EXPLICIT
    | EXPORT
    | FRIEND
    | MUTABLE
    | NAMESPACE
    | NEW
    | OPERATOR
    | PRIVATE
    | PROTECTED
    | PUBLIC
    | REINTERPRET_CAST
    | STATIC_CAST
    | TEMPLATE
    | THIS
    | THROW
    | TRY
    | TYPEID
    | TYPENAME
    | USING
    | VIRTUAL
    | AUTO
    | CONST
    | DO
    | ENUM
    | EXTERN
    | FOR
    | STATIC
    | UNION
    | VOLATILE
    | RESTRICT
    | REGISTER
    | INLINE
    | GOTO
    | TYPEDEF
    | SWITCH
    | CASE
    | INC_OP
    | DEC_OP
    | DEFAULT
    """
    #p[0]=MidNode('cpp_advanced',p[1:])
    pass


    

def p_error(p):
    #print('Syntax error of %s type in line %d, lexpos - %d: %s' % (p.type, p.lineno, p.lexpos, p.value))
    if p:
        print('Syntax error of token %s in line %d' % (p.type, p.lineno))
        # Just discard the token and tell the parser it's okay.
        parser.errok()
    else:
        print("Syntax error at EOF")

lexer = lex.lex()
parser = yacc.yacc()

if __name__ == '__main__':
    import sys
    from pretreatment import Pretreatment
    import json

    if len(sys.argv) > 1:  # specify file
        pretreatmenter=Pretreatment()
        file_data, ok=pretreatmenter.Pretreatment(sys.argv[1])
        if not ok:
            print('pretreatment error')
        else:
            result = parser.parse(file_data, lexer=lexer)
            print(result.__str__())
            ast_dict = result.generate_syntree()
            tree = json.dumps(ast_dict, indent=4)
            save_path = sys.argv[1][:-len('.cpp')]+'_syntree.json'
            if len(sys.argv) > 2:
                save_path = sys.argv[2]
            with open(save_path, 'w+',encoding='utf-8') as f:
                #f.write(buf)
                f.write(str(tree))
            # print(tree)
            print("results is saved at {}.".format(save_path))

    else:
        print("please input c++ file path")

