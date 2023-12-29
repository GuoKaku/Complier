start   : part | empty
part    : part declorcom | declorcom
declorcom   : comment | external_declaration
external_declaration    : function_definition | declaration

declaration : type variable_initable_list_orempty ';' 
type  : type_specifier_can_unsigned | type_specifier_cannot_unsigned  | uorus | uorus type_specifier_can_unsigned 
type_specifier : type_specifier_cannot_unsigned | type_specifier_can_unsigned | uorus
type_specifier_can_unsigned: CHAR | SHORT | INT | LONG 
type_specifier_cannot_unsigned : VOID | FLOAT | DOUBLE | BOOL | struct_specifier
uorus:  SIGNED | UNSIGNED 

struct_specifier   : STRUCT identifier | STRUCT '{' struct_declaration_list '}' | STRUCT identifier '{' struct_declaration_list '}' 
struct_declaration_list     : struct_declaration | struct_declaration_list struct_declaration
struct_declaration : type struct_variable_list ';'
struct_variable_list  : variable | struct_variable_list ',' variable


variable_initable_list_orempty  : empty | variable_initable_list
variable_initable_list    : variable_initable | variable_initable_list ',' variable_initable
variable_initable : variable | variable '=' initializer
variable  : direct_variable | pointer direct_variable   /* int a, char* chp , ... */
direct_variable   : identifier | direct_variable '[' assignable_expression_orempty ']' | direct_variable '(' parameter_list ')' | direct_variable '(' identifier_list_orempty ')'
parameter_list  : parameter_declaration | parameter_list ',' parameter_declaration
parameter_declaration   : type variable 
identifier  : IDENTIFIER
pointer : '*' | '*' pointer
constant    : INTEGER_CONSTANT | CHAR_CONSTANT | FLOAT_CONSTANT | BOOL_CONSTANT 

initializer : assignable_expression |'{' initializer_list_orempty '}' | '{' initializer_list ',' '}'
initializer_list_orempty : empty | initializer_list
initializer_list    : initializer | initializer_list ',' initializer
assignable_expression   : conditional_expression | variable assign_operator assignable_expression
assign_operator : '=' | MUL_ASSIGN | DIV_ASSIGN | MOD_ASSIGN | ADD_ASSIGN | SUB_ASSIGN | LEFT_ASSIGN | RIGHT_ASSIGN | AND_ASSIGN | XOR_ASSIGN | OR_ASSIGN 

expression  : assignable_expression | expression ',' assignable_expression
conditional_expression  : binary_expression | ternary_expression
ternary_expression : expression '?' expression ':' expression
binary_expression   : cast_expression | binary_expression '*' binary_expression| binary_expression '/' binary_expression| binary_expression '%' binary_expression| binary_expression '+' binary_expression| binary_expression '-' binary_expression| binary_expression RIGHT_OP binary_expression| binary_expression LEFT_OP binary_expression| binary_expression '<' binary_expression| binary_expression LTE binary_expression| binary_expression GTE binary_expression| binary_expression '>' binary_expression| binary_expression EQ_OP binary_expression| binary_expression NEQ_OP binary_expression| binary_expression '&' binary_expression| binary_expression '|' binary_expression| binary_expression '^' binary_expression| binary_expression AND_OP binary_expression| binary_expression OR_OP binary_expression
cast_expression : unary_expression
unary_expression    : uscd_expression | unary_operator cast_expression
uscd_expression : unit_expression | uscd_expression '[' expression ']'  | uscd_expression '(' arg_value_exp_list ')' | uscd_expression '(' ')' | uscd_expression PTR_OP identifier
unit_expression  : identifier | constant | multiple_string | '(' expression ')' | inlinefunc
multiple_string  : STRING_CONSTANT | multiple_string STRING_CONSTANT
unary_operator : '&' | '*' | '+' | '-' | '~' | '!' 
inlinefunc : SIZEOF



arg_value_exp_list  : assignable_expression | arg_value_exp_list ',' assignable_expression


function_definition : type variable declaration_list_orempty funcbody_statement
declaration_list    : declaration | declaration_list declaration
funcbody_statement : '{' block_item_list_orempty '}'
block_item_list_orempty  : empty | block_item_list
block_item_list : block_item | block_item_list block_item
block_item  : declaration | statement | comment
statement   : funcbody_statement | branch_statement | expression_statement | loop_statement | back_statement
branch_statement : IF '(' expression ')' statement | IF '(' expression ')' statement ELSE statement  
expression_statement : expression_orempty
expression_orempty   : empty | expression
loop_statement : WHILE '(' expression ')' statement 

comment : COMMENT1 | COMMENT2