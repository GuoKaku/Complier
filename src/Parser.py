import re
import ply.yacc as yacc
import SynTree as SynTree
from lexer import *
from utility import handle_decl_change

# 开始

#simply pass the argument from right to
def pass_arg(item):
    item[0]=item[1]


def p_starter(item):
    """ start   : part
                | empty
    """
    item[0] = SynTree.FirstNode(item[1]) if item[1]  else SynTree.FirstNode(list())


def p_part(item):
    """ part    : part declorcom
                | declorcom
    """
    if len(item) > 2 and item[2]:
        item[1].extend(item[2])
    pass_arg(item)
    
    
def p_decl_or_comment_1(item):
    """ declorcom   : comment
    """
    item[0] = [item[1]]
    
def p_decl_or_comment_2(item):
    """ declorcom   : external_declaration
    """
    pass_arg(item)
    

def p_initializer_ass(item):
    """ initializer : assignable_expression
    """
    pass_arg(item)

def p_initializer_in(item):
    """ initializer : '{' initializer_list_orempty '}'
                    | '{' initializer_list ',' '}'
    """
    if item[2] :
        item[0] = item[2]
    else:
        item[0] = SynTree.ContentList(listType='Init',elements=list())
        

def p_initializer_list(item):
    """ initializer_list    : initializer
                            | initializer_list ',' initializer
    """
    init = item[1] if len(item) == 2 else item[3]
    item[0] = SynTree.ContentList(listType='Init', elements=[init]) if len(item) == 2 else item[1]

    if len(item) != 2:
        item[1].elements+=[init]

def p_variable_initable(item):
    """ variable_initable : variable
                        | variable '=' initializer
    """
    init_ = item[3] if len(item) > 2 else None
    item[0] = dict(type=item[1], init=init_)

def p_variable_initable_list_idec(item):
    """ variable_initable_list    : variable_initable
                                | variable_initable_list ',' variable_initable
    """
    (new_var,e_list)=(item[1],[item[3]]) if len(item) == 4 else (list(),[item[1]])
    item[0]=new_var+e_list

    



def p_empty(item):
    """ empty :
    """
    item[0] = None


def p_type(item):
    """ type  : type_specifier_can_unsigned
                                | type_specifier_cannot_unsigned 
                                | uorus
                                | uorus type_specifier_can_unsigned
    """
    if len(item)<=2:
        item[0] = dict(qual=list(), spec=[item[1]])
    else:
        tmp = item[1] + item[2]
        item[0] = dict(qual=list(), spec=[tmp])

        


def p_type_specifier(item):
    '''type_specifier : type_specifier_cannot_unsigned
                        | type_specifier_can_unsigned
                        | uorus '''
    pass_arg(item)
                        

def p_type_specifier_cannot_unsigned(item):
    ''' type_specifier_cannot_unsigned : VOID
                       | FLOAT
                       | DOUBLE
                       | BOOL
                       | struct_specifier
    '''
    pass_arg(item)
    
def p_type_specifier_can_unsigned(item):
    ''' type_specifier_can_unsigned : INT
                       | SHORT
                       | LONG
                       | CHAR
    '''
    pass_arg(item)
    
def p_uorus(item):
    '''uorus   :          SIGNED
                       | UNSIGNED'''
    pass_arg(item)

def p_declaration_list_orempty(item):
    """declaration_list_orempty : empty
                            | declaration_list
    """
    pass_arg(item)

def p_declaration(item):
    """ declaration : type variable_initable_list_orempty ';'
    """
    decl_spec = item[1]
    struct = None
    if isinstance(decl_spec['spec'][0], SynTree.Struct):
        struct = decl_spec['spec'][0]
    init_decl_list = item[2]

    item[0] = list()

    for init_decl in init_decl_list:
        type = init_decl['type']
        if struct :
            if isinstance(type, SynTree.Id):
                args = dict()
                args['quals']=decl_spec['qual']
                args['name']=type.name
                args['spec']=decl_spec['spec']
                args['type']=struct
                args['init']=init_decl['init']

                declaration = SynTree.Decl(**args)

            else:
                while not isinstance(type.type, SynTree.Id):
                    type = type.type
                declname = type.type.name
                type.type = struct
                
                args = dict()
                args['quals']=decl_spec['qual']
                args['name']=declname
                args['spec']=decl_spec['spec']
                args['type']=init_decl['type']
                args['init']=None

                
                declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type, SynTree.Id):
                type = type.type
            type.spec = decl_spec['spec']
            args = dict()
            args['quals']=decl_spec['qual']
            args['name']=type.name
            args['spec']=decl_spec['spec']
            args['type']=init_decl['type']
            args['init']=init_decl['init']
           
            declaration = SynTree.Decl(**args)
        item[0]=[declaration]+item[0]

def p_declaration_list(item):
    """ declaration_list    : declaration
                            | declaration_list declaration
    """
    decl_var= item[2] if len(item) >= 3 else None
    item[0] = item[1] + decl_var


def p_identifier_list_orempty(item):
    """identifier_list_orempty  : empty
                            | identifier_list
    """
    pass_arg(item)

def p_identifier_list(item):
    """ identifier_list : identifier
                        | identifier_list ',' identifier
    """
    if len(item) >= 2:
        item[1].elements+=[item[3]]
        pass_arg(item)
    else:
        item[0] = SynTree.ContentList(listType='Param', elements=[item[1]])


def p_identifier(item):
    """ identifier  : ID 
                    | inlinefunc """
    args=dict()
    args['name']=item[1]
    args['spec']=None
    item[0] = SynTree.Id(**args)
    
def p_inclinefunc(item):
    """ inlinefunc  : SIZEOF"""
    item[0] =item[1]

# 跳转
def p_back_statement_break(item):
    """ back_statement  : BREAK ';' """
    item[0] = SynTree.ControlLogic(logicType='Break')

def p_back_statement_continue(item):
    """ back_statement  : CONTINUE ';' """
    item[0] = SynTree.ControlLogic(logicType='Continue')

def p_back_statement_return(item):
    """ back_statement  : RETURN ';'
                        | RETURN expression ';'
    """
    if len(item)==3:
        args = dict()
        args["return_result"]= None
        item[0] = SynTree.ControlLogic(logicType='Return',**args)
    else:
        args = dict()
        args["return_result"]= item[2]
        item[0] = SynTree.ControlLogic(logicType='Return',**args)


def p_assignable_expression_orempty(item):
    """assignable_expression_orempty    : empty
                                    | assignable_expression
    """
    pass_arg(item)
    
    
def p_variable_initable_list_orempty(item):
    """variable_initable_list_orempty  : empty
                            | variable_initable_list
    """
    pass_arg(item)




def p_assign_operator(item):
    ''' assign_operator : '='
                            | MUL_ASG
                            | DIV_ASG
                            | MOD_ASG
                            | ADD_ASG
                            | SUB_ASG
                            | LEFT_ASG
                            | RIGHT_ASG
                            | AND_ASG
                            | XOR_ASG
                            | OR_ASG '''
    pass_arg(item)

def p_arg_value_exp_list(item):
    """ arg_value_exp_list    : assignable_expression
                                    | arg_value_exp_list ',' assignable_expression
    """
    if len(item) > 2:
        item[1].elements+=[item[3]]
        pass_arg(item)
    else:
        item[0] = SynTree.ContentList(listType='Expression', elements=[item[1]])


def p_assignable_expression(item):
    """ assignable_expression   : conditional_expression
                                | unary_expression assign_operator assignable_expression
    """
    if len(item) == 2:
        pass_arg(item)
    else:
        args=dict()
        args['left']=item[1]
        args['right']=item[3]
        item[0] = SynTree.Operation(OperationType='Assignment',OperationName=item[2],**args)

def p_block_item_list_orempty(item):
    """block_item_list_orempty  : empty
                            | block_item_list
    """
    pass_arg(item)

def p_constant_expression_orempty(item):
    """constant_expression_orempty  : empty
                            | constant_expression
    """
    pass_arg(item)

def p_specifier_qualifier_list_orempty(item):
    """specifier_qualifier_list_orempty  : empty
                            | specifier_qualifier_list
    """
    pass_arg(item)

# block
def p_block_item(item):
    """ block_item  : declaration
                    | statement
                    | comment
    """
    item[0] = item[1] if isinstance(item[1], list) else [item[1]]


def p_block_item_list(item):
    """ block_item_list : block_item
                        | block_item_list block_item
    """
    if len(item) == 3:
        if not item[2][0]:
            pass_arg(item)
        else:
            item[0] = item[1] + item[2] 
    elif len(item) == 2:
        pass_arg(item)



def p_expression_orempty(item):
    """expression_orempty    : empty
                        | expression
    """
    pass_arg(item)

def p_funcbody_statement(item):
    """ funcbody_statement : '{' block_item_list_orempty '}' """
    item[0] = SynTree.Blocks(item[2])

def p_conditional_expression(item):
    """ conditional_expression  : binary_expression 
                | ternary_expression
    """
    if len(item) == 2:
        pass_arg(item)
        
def p_ternary_expression(item):
    """ternary_expression : expression '?' expression ':' expression
    """
    if len(item) == 6:
        args={'condition':item[1],'true':item[3],'false':item[5]}
        item[0] = SynTree.Operation(OperationType='TernaryOp',OperationName=item[2],**args)
    
        


def p_constant_int(item):
    """ constant    : INTEGER_CONST
    """
    item[0] = SynTree.Constant('int', item[1], )

def p_constant_char(item):
    """ constant    : CHAR_CONST
    """
    item[0] = SynTree.Constant('char', item[1], )

def p_constant_float(item):
    """ constant    : FLOAT_CONST
    """
    item[0] = SynTree.Constant('float', item[1], )

def p_bool_constant(item):
    """ constant    : BOOL_CONST
    """
    item[0] = SynTree.Constant('bool', item[1], )

def p_constant_expression(item):
    """ constant_expression : conditional_expression """
    pass_arg(item)

def p_variable_direct(item):
    """ variable  : direct_variable
    """
    pass_arg(item)

def p_variable_pd(item):
    """ variable  : pointer direct_variable
    """
    item[0] = handle_decl_change(item[2], item[1])

def p_specifier_qualifier_list_ts(item):
    """ specifier_qualifier_list    : type specifier_qualifier_list_orempty
    """
    if item[2]:
        item[2]['spec']=list(item[1])+item[2]['spec']
    item[0] = item[2] or dict(qual=list(), spec=[item[1]])



# 直接声明
def p_direct_variable_1(item):
    """ direct_variable   : identifier
    """
    pass_arg(item)

def p_direct_variable_3(item):
    """ direct_variable   : direct_variable '[' assignable_expression_orempty ']'
    """

    args=dict()
    args['dim']=item[3]

    item[0] = handle_decl_change(item[1], SynTree.DeclArray(**args))

def p_direct_variable_6(item):
    """ direct_variable   : direct_variable '(' parameter_list ')'
                            | direct_variable '(' identifier_list_orempty ')'
    """
    args=dict()
    args['args']=item[3]

    item[0] = handle_decl_change(item[1], SynTree.DeclFunction(**args))

def p_external_declaration_1(item):
    """ external_declaration    : function_definition
    """
    item[0] = [item[1]]

def p_external_declaration_2(item):
    """ external_declaration    : declaration
    """
    pass_arg(item)
    
    


# 表达式
def p_expression(item):
    """ expression  : assignable_expression
                    | expression ',' assignable_expression
    """
    num=len(item)
    if num != 2:
        if not isinstance(item[1], SynTree.ContentList):
            item[1] = SynTree.ContentList(listType='Expression', elements=[item[1]])
        item[1].elements+=[item[3]]
        pass_arg(item)
    else:
        pass_arg(item)


def p_expression_statement(item):
    """ expression_statement : expression_orempty ';' """
    item[0] = item[1] or SynTree.ControlLogic(logicType='EmptyStatement')

def p_function_definition(item):
    """ function_definition : type variable declaration_list_orempty funcbody_statement
    """
    #variale is func(int a, int b, ...)
    decl_spec = item[1]
    struct = None
    if isinstance(decl_spec['spec'][0], SynTree.Struct):
        struct = decl_spec['spec'][0]
    type = item[2]


    args = dict()
    args['quals']=decl_spec['qual']
    args['spec']=decl_spec['spec']
    args['init']=None
    if struct :
      
        if isinstance(type, SynTree.Id):
            args['name']=type.name
            args['type']=struct

            declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type.type, SynTree.Id):
                type = type.type
            declname = type.type.name
            type.type = struct
            args['name']=declname
            args['type']=item[2]
            declaration = SynTree.Decl(**args)


    else:
        while not isinstance(type, SynTree.Id):
            type = type.type
        type.spec = decl_spec['spec']
        args['name']=type.name
        args['type']=item[2]

        declaration = SynTree.Decl(**args)

    fun_args = {'decl': declaration, 'param_args': item[3], 'body': item[4]}
    item[0] = SynTree.FuncDef(**fun_args)



def p_parameter_list(item):
    """ parameter_list  : parameter_declaration
                        | parameter_list ',' parameter_declaration
    """
    item[0] = item[1] if len(item)>2 else SynTree.ContentList(listType='Param', elements=[item[1]])
    if len(item)!=2:
        item[1].elements+=[item[3]]

        
        

def p_parameter_declaration(item):
    """ parameter_declaration   : type variable
    """
    decl_spec = item[1]
    decl_poth=decl_spec['spec']
    struct = None
    if isinstance(decl_poth[0], SynTree.Struct):
        struct = decl_poth[0]
    type = item[2]

    args=dict()
    args['quals']=decl_spec['qual']
    args['spec']=decl_poth
    args['init']=None
    if struct :
        if isinstance(type, SynTree.Id):
            args['name']=type.name
            args['type']=struct

            declaration = SynTree.Decl(**args)
        else:
            while not isinstance(type.type, SynTree.Id):
                type = type.type
            declname = type.type.name
            type.type = struct
            args['name']=declname
            args['type']=item[2]

            declaration = SynTree.Decl(**args)
    else:
        while not isinstance(type, SynTree.Id):
            type = type.type
        type.spec = decl_poth
        args['name']=type.name
        args['type']=item[2]

        declaration = SynTree.Decl(**args)

    item[0] = declaration

#usdc: unit, subscript, func call, depoint
def p_uscd_expression_1(item):
    """ uscd_expression : unit_expression """
    pass_arg(item)

def p_uscd_expression_2(item):
    """ uscd_expression : uscd_expression '[' expression ']' """
    #item[0] = SynTree.ArrayRef(item[1], item[3])
    args = {'subscript': item[3]}
    item[0] = SynTree.Ref(refType='ArrayRef', name=item[1], **args)

def p_uscd_expression_3(item):
    """ uscd_expression : uscd_expression '(' arg_value_exp_list ')'
                            | uscd_expression '(' ')'
    """
    arg=item[3] if len(item) == 5 else None
    args = {'name': item[1], 'args': arg}

    item[0] = SynTree.FunctionCall(**args)

def p_uscd_expression_4(item):
    """ uscd_expression : uscd_expression PTR_OP identifier
    """
    args_tmp=dict()
    args=dict()
    args_tmp['name']=item[3]
    args_tmp['spec']=None

    reign = SynTree.Id(**args_tmp)
    args['type']=item[2]
    args['reign']=reign
    item[0] = SynTree.Ref(refType='StructRef',name=item[1], **args)

def p_unit_expression_id(item):
    """ unit_expression  : identifier """
    pass_arg(item)

def p_unit_expression_const(item):
    """ unit_expression  : constant """
    pass_arg(item)

def p_unit_expression_mstring(item):
    """ unit_expression  : multiple_string
    """
    pass_arg(item)

def p_unit_expression_bracket(item):
    """ unit_expression  : '(' expression ')' """
    item[0] = item[2]
    

    
    



def p_branch_statement_if(item):
    """ branch_statement : IF '(' expression ')' statement """
    args=dict()
    args['judge']=item[3]
    args['action1']=item[5]
    args['action2']=None
    args={'judge':item[3], 'action1':item[5], 'action2': None}
    item[0] = SynTree.ControlLogic('If',**args)

def p_branch_statement_ifelse(item):
    """ branch_statement : IF '(' expression ')' statement ELSE statement """
    args = dict()
    args['judge'] = item[3]
    args['action1'] = item[5]
    args['action2'] = item[7]
    item[0] = SynTree.ControlLogic('If', **args)


def p_loop_statement(item):
    """ loop_statement : WHILE '(' expression ')' statement """
    args = dict()
    args['judge'] = item[3]
    args['action'] = item[5]
    item[0] = SynTree.ControlLogic(logicType='While',**args)

def p_loop_statement_2(item):
    """ loop_statement : FOR '(' parameter_declaration ';' expression_orempty ';' expression_orempty ')'  statement
                        | FOR '(' expression ';' expression_orempty ';' expression_orempty ')'  statement
                        | FOR '(' empty ';' expression_orempty ';' expression_orempty ')'  statement
    """
    args = dict()
    args['first'] = item[3]
    args['judge'] = item[5]
    args['action'] = item[7]
    args['statement'] = item[9]

    item[0] = SynTree.ControlLogic(logicType='For',**args)
    
def p_loop_statement_3(item):
    """ loop_statement : FOR '(' parameter_declaration '=' expression ';' expression_orempty ';' expression_orempty ')'  statement
    """
    args = dict()
    args['first'] = item[3]
    args['judge'] = item[5]
    args['action'] = item[7]
    args['statement'] = item[9]

    item[0] = SynTree.ControlLogic(logicType='For',**args)


def p_statement(item):
    """ statement   : funcbody_statement
                    | branch_statement
                    | expression_statement
                    | loop_statement
                    | back_statement
    """
    pass_arg(item)

def p_struct_specifier_1(item):
    """ struct_specifier   : STRUCT identifier
    """
    item[0] = SynTree.Struct(
        name=item[2].name,
        args=None)

def p_struct_specifier_2(item):
    """ struct_specifier : STRUCT '{' struct_declaration_list '}'
    """
    item[0] = SynTree.Struct(
        name=None,
        args=item[3])

def p_initializer_list_orempty(item):
    """initializer_list_orempty : empty
                            | initializer_list
    """
    pass_arg(item)
    
def p_struct_specifier_3(item):
    """ struct_specifier   : STRUCT identifier '{' struct_declaration_list '}'
    """
    item[0] = SynTree.Struct(
        name=item[2].name,
        args=item[4])

# Combine all declarations into a single list
#
def p_struct_declaration_list(item):
    """ struct_declaration_list     : struct_declaration
                                    | struct_declaration_list struct_declaration
    """
    
    if len(item) > 2:
        item[0] = item[1] + (item[2] or list())
    else:
        item[0] = item[1] or list()
        

def p_struct_declaration(item):
    """ struct_declaration : type struct_variable_list ';'
    """
    item[0] = list()
    struct_decl_list = item[2]
    spec_qual = item[1]
    struct = None
    if isinstance(spec_qual['spec'][0], SynTree.Struct):
        struct = spec_qual['spec'][0]

    for decl in struct_decl_list:
        type = decl
        while not isinstance(type, SynTree.Id):
            type = type.type
        if struct :
            type.type = struct
            declname = type.type.name
        else:
            type.spec = spec_qual['spec']
            declname = type.name
        args = dict()
        args['name'] = declname
        args['quals'] = spec_qual['qual']
        args['spec'] = spec_qual['spec']
        args['type'] = decl
        args['init'] = None

        declaration = SynTree.Decl(**args)
        item[0]=[declaration]+item[0]


def p_struct_variable_list(item):
    """ struct_variable_list  : variable
                                | struct_variable_list ',' variable
    """
    
    item[0] = [item[1]]if len(item) != 4 else item[1] + [item[3]] 


def p_pointer(item):
    """ pointer : '*'
                | '*' pointer
    """
    args = dict()
    args['quals'] = item[1]
    type_ = SynTree.DeclPointer(**args or list())
    if len(item) == 2:
        item[0] = type_
    else:
        tail = item[2]
        while tail.type :
            tail = tail.type
        tail.type = type_
        item[0] = item[2]


# 一元运算
def p_unary_operator(item):
    ''' unary_operator : '&'
                       | '*'
                       | '+'
                       | '-'
                       | '~'
                       | '!' 
                       '''
                       
    pass_arg(item)
    
def p_self_incdec_op(item):
    ''' self_incdec :   INC_OP
                       | DEC_OP
    '''
    pass_arg(item)

def p_unary_expression_1(item):
    """ unary_expression    : uscd_expression"""
    pass_arg(item)

def p_unary_expression_2(item):
    """ unary_expression    : unary_operator cast_expression
                            | self_incdec cast_expression
    """
    args = dict()
    args['expression'] = item[2]
    item[0] = SynTree.Operation(OperationType='UnaryOp',OperationName=item[1],**args)
    
def p_unary_expression_3(item):
    """ unary_expression    : cast_expression self_incdec 
    """
    args = dict()
    args['expression'] = item[1]
    item[0] = SynTree.Operation(OperationType='UnaryOp',OperationName=item[2],**args)
    

def p_multiple_string(item):
    """ multiple_string  : STRING_CONST
                                | multiple_string STRING_CONST
    """
    if len(item) > 2:
        item[1].content += item[2][1:]
        pass_arg(item)
    else:
        item[0] = SynTree.Constant('string', item[1])


def p_binary_expression(item):
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
    if len(item) > 2:
        args = dict()
        args['left'] = item[1]
        args['right'] = item[3]
        item[0] = SynTree.Operation(OperationType='BinaryOp',OperationName=item[2],**args)
    else:
        pass_arg(item)
        
def p_cast_expression_1(item):
    """ cast_expression : unary_expression """
    pass_arg(item)

def p_comment(item):
    """  
        comment : COMMENT1
                | COMMENT2
    """
    item[0]=SynTree.CommentNode(item[1])
    



# C++相比C多出的特性，因为没有用到，暂时没有处理
def p_cpp_advanced(item):
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
    #item[0]=MidNode('cpp_advanced',item[1:])
    pass


    

def p_error(item):
    #print('Syntax error of %s type in line %d, lexpos - %d: %s' % (p.type, p.lineno, p.lexpos, p.value))
    if item:
        print('Syntax error of token %s in line %d' % (item.type, item.lineno))
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
        cooked_file, ok=pretreatmenter.Pretreatment(sys.argv[1])
        if ok:
            result = parser.parse(cooked_file, lexer=lexer)
            ast_dict = result.generate_syntree()
            syntax_tree = json.dumps(ast_dict, indent=4)
            tree_path = sys.argv[1][:-len('.cpp')]+'_syntree.json'
            if len(sys.argv) > 2:
                tree_path = sys.argv[2]
            with open(tree_path, 'w+',encoding='utf-8') as f:
                f.write(str(syntax_tree))
            print("tree generated at {}.".format(tree_path))
        else:
            print('pretreatment error')
    else:
        print("only c++ file is feasible")

