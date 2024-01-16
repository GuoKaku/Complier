from __future__ import print_function
from llvmlite import ir
import SynTree as SynTree
from utility import *

# int32 = ir.IntType(32)
# int8 = ir.IntType(8)
# int1 = ir.IntType(1)
# unsigned_int32 = ir.IntType(32)
# ir_void = ir.VoidType()
# ir_float = ir.FloatType()
# ir_double = ir.DoubleType()
# ir_func = ir.FunctionType


# def c2i(s):
#     if s == "'\\n'" or s == "'\\r\\n'":
#         return 10
#     return ord(s[1:-1])


class Tool(object):
    def __init__(self):
        # llvm module
        self.tool_module = ir.Module('my compiler')
        # llvm builder for every function
        self.tool_builders = None

        # global information
        self.tool_type_defined = dict()
        self.tool_used_memory = dict()
        self.tool_functions = dict()
        self.tool_global_variables = dict()
        self.tool_global_comments = list()

        # function information
        self.tool_arguments = dict()
        self.tool_start_stack = list()
        self.tool_end_stack = list()
        self.builtin_func = self.tool_module.declare_intrinsic
        self.tool_current_function = None


    def getcode(self, head):
        self.visit_FirstNode(head)
        return self.tool_module


    def visit_FirstNode(self, ast_node, flag=0):
        for child in ast_node.nodes:
            if isinstance(child, SynTree.FuncDef):
                # self.visit(unit, flag=0)
                self.visit_FuncDef(child, flag=0)
            elif isinstance(child, SynTree.Decl):
                # self.visit(unit, flag=1)
                self.visit_Decl(child, flag=1)
            elif isinstance(child, SynTree.CommentNode):
                # print(f'content:{child.content}')
                self.tool_global_comments+=[child.content]
                self.visit_CommentNode(child, flag=0)
                # # print(f'visit_FirstNode child:{child}')

    def visit_Decl(self, ast_node, flag=0):
        """
            declorcom   : external_declaration

        """
        # print(f'visit_Decl ast_node.name:{ast_node.name}, next type:{ast_node.type}, quals:{ast_node.quals}, spec:{ast_node.spec}, init:{ast_node.init}')
        # print(f'self.tool_builders:{self.tool_builders}')
        if ast_node.name in self.tool_used_memory.keys() or ast_node.name in self.tool_arguments.keys() or ast_node.name in self.tool_global_variables.keys():
            raise RuntimeError("Duplicate declaration: " + ast_node.name)
        # dec = self.allocate_variable(ast_node, flag, list())

        temp_node = ast_node
        modifier_list = list()
        while (type(temp_node) == SynTree.DeclArray) or (type(temp_node) == SynTree.DeclFunction) or (
                type(temp_node) == SynTree.DeclPointer) or (type(temp_node) == SynTree.Decl):
            modifier_list+=[temp_node]
            # print(f'modifier_list:{modifier_list}')
            temp_node = temp_node.type
        if type(temp_node) == SynTree.Id:
            # print(f'temp_node_spec:{temp_node.spec[0]}')
            if temp_node.spec[0] in ['int', 'char', 'void', 'float', 'double', 'unsignedint']:
                iden_type = self.get_regular_type(temp_node.spec[0])
            elif temp_node.spec[0] in self.tool_type_defined:
                iden_type = self.tool_module.context.get_identified_type(temp_node.spec[0].name)
            # iden_type = self.get_element_type(temp_node.spec[0])
            # print(f'iden_type:{iden_type}')
            iden_name = modifier_list.pop(0).name
            # print(f'modifier_list:{modifier_list}, iden_name:{iden_name}')
            for modifier in modifier_list:
                iden_type = self.return_content(modifier, iden_type)
                # print(f'iden_type:{iden_type}, modifier:{modifier}')
            dec = self.handle_allocate_indenti_by_flag(temp_node, iden_type, iden_name, flag, modifier_list)
        elif type(temp_node) == SynTree.Struct:
            dec = self.allocate_struct(temp_node, flag, modifier_list)

        # print(f'dec:{dec}')
        # self.handle_decl_args(ast_node, flag)
        # print(f'self.tool_builders:{self.tool_builders}')

        if flag == 0:
            if ast_node.init:
                # print(f'ast_node.init:{ast_node.init}')
                self.tool_builders.store(self.visit(ast_node.init, 1), self.tool_used_memory[ast_node.name])
        elif flag == 1:
            if ast_node.init:
                if not self.tool_global_variables[ast_node.name].initializer:
                    self.tool_global_variables[ast_node.name].initializer = self.visit(ast_node.init, ast_node.name)
                    # print(f'flag=1 ast_node.name:{ast_node.name}, self.tool_global_variables:{self.tool_global_variables}, self.tool_global_variables[ast_node.name]:{self.tool_global_variables[ast_node.name]}')
            else:
                # print(f'self.tool_used_memory:{self.tool_used_memory}')
                self.tool_global_variables[ast_node.name].align = 4
                self.tool_global_variables[ast_node.name].linkage = "common"
        
                # ast_node.init:<cAST.Constant object at 0x1054b3cd0>
                # ast_node.init:<cAST.Operation object at 0x1054d4250>
                # ast_node.init:<cAST.ContentList object at 0x1054d4a50>
        elif flag == 2:
            return dec

    def visit_FuncDef(self, ast_node, flag=0):
        self.tool_arguments.clear()
        # print(f'visit_FuncDef ast_node.decl:{ast_node.decl}, ast_node.body:{ast_node.body}, param_args:{ast_node.param_args}, flag:{flag}')
        # ast_node.decl:<cAST.Decl object at 0x10566bb50>, ast_node.body:<cAST.Blocks object at 0x10566bdd0>, param_args:None
        # func_ = self.visit(ast_node.decl, flag=2)
        f_ = self.visit_Decl(ast_node.decl, flag=2)
        self.tool_current_function = f_

        if ast_node.body:
            # print(f'func_的类型是{type(f_)}')
            # func_的类型是<class 'llvmlite.ir.values.Function'>
            entry_block = f_.append_basic_block(name="entry")
            self.tool_builders = ir.IRBuilder(entry_block)
            # 通过self.tool_builders对象，可以使用IRBuilder类的方法来生成LLVM IR代码，例如创建指令基本块函数等，并将其添加到相应的函数中。
            # 通过append_basic_block方法，可以在函数中添加一个基本块，该方法的参数name是可选的，用于指定基本块的名称。
            # print(f'func_args:{f_.args}')
            for a in f_.args:
                self.tool_used_memory[a.name] = self.tool_builders.alloca(a.type, name=a.name)
                self.tool_builders.store(a, self.tool_used_memory[a.name])

            # self.visit(ast_node.body)
            # self.visit_Blocks(ast_node.body)
            if ast_node.body.blocks:
                for item in ast_node.body.blocks:
                    # print(f'item:{item}')
                    self.visit(item, flag=0)

        # else:
        #     self.tool_current_function = None
        #     func_.is_declaration = True

        
        self.tool_used_memory.clear()
        self.tool_arguments.clear()
        del self.tool_start_stack[:]
        del self.tool_end_stack[:]
        self.tool_current_function = None

    def visit_Blocks(self, ast_node, flag=0):
        # print(f'visit_Blocks ast_node:{ast_node}, ast_node.blocks:{ast_node.blocks}')
        if ast_node.blocks:
            for block in ast_node.blocks:
                # print(f'item:{block}')
                self.visit(block, flag=0)
            

    def visit_Constant(self, ast_node, flag=0):
        # print(f'visit_Constant ast_node.kind:{ast_node.kind}, ast_node.content:{ast_node.content}')
        if ast_node.kind == 'int':
            return ir.Constant(int32, ast_node.content)
        elif ast_node.kind == 'char':
            if ast_node.content == "'\\n'" or ast_node.content == "'\\r\\n'":
                return ir.Constant(int8, 10)
            return ir.Constant(int8, ord(ast_node.content[1:-1]))
            # return ir.Constant(int8, c2i(ast_node.content))
        elif ast_node.kind == 'float':
            return ir.Constant(ir_float, ast_node.content)
        elif ast_node.kind == 'double':
            return ir.Constant(ir_double, ast_node.content)

        elif ast_node.kind == 'unsignedint':
            return ir.Constant(unsigned_int32, ast_node.content)
        elif ast_node.kind == 'string':
            # mid_str = ast_node.content[1:-1].replace('\\n', '\n') + '\0'
            # arr_str = ir.ArrayType(int8, len(mid_str))
            # str_name = '.str' + str(len(self.tool_global_variables))
            # glb_str = ir.GlobalVariable(self.tool_module, arr_str, name=str_name)
            # glb_str.initializer = ir.Constant(arr_str, bytearray(mid_str, 'utf-8'))
            # glb_str.global_constant = True
            # self.tool_global_variables[str_name] = glb_str
            # zero = ir.Constant(int32, 0)
            # return self.tool_builders.gep(glb_str, [zero, zero], inbounds=True)
            return self.visit_Constant_String(ast_node, flag=0)
        
        else:
            raise RuntimeError("The type is not recognized: " + ast_node.kind)
        return res
    
    def visit_Constant_String(self, ast_node, flag=0):
        # print(f'visit_Constant_String ast_node:{ast_node}, ast_node.content:{ast_node.content}')
        mid_str = ast_node.content[1:-1] + '\0'
        if '\\n' in ast_node.content:
            mid_str = ast_node.content[1:-1].replace('\\n', '\n') + '\0'
        len_mid= len(mid_str)
        arr_str = ir.ArrayType(int8, len_mid)
        len_global_variables = len(self.tool_global_variables)
        str_name = '.str' + str(len_global_variables)
        # glb_str = ir.GlobalVariable(self.tool_module, arr_str, name=str_name)
        # glb_str.initializer = ir.Constant(arr_str, bytearray(mid_str, 'utf-8'))
        # glb_str.global_constant = True
        self.tool_global_variables[str_name] = ir.GlobalVariable(self.tool_module, arr_str, name=str_name)
        self.tool_global_variables[str_name].initializer = ir.Constant(arr_str, bytearray(mid_str, 'utf-8'))
        self.tool_global_variables[str_name].global_constant = True
        # zero = ir.Constant(int32, 0)
        return self.tool_builders.gep(self.tool_global_variables[str_name], [ir.Constant(int32, 0), ir.Constant(int32, 0)], inbounds=True)


    def visit_Id(self, ast_node, flag=0):
        # print(f'visit_Identifier ast_node:{ast_node}, ast_node.name:{ast_node.name}, ast_node.spec:{ast_node.spec}')
        if ast_node.spec:
            kind = ast_node.spec
            if kind == 'int':
                return int32
            if kind == 'char':
                return int8
            if kind == 'void':
                return ir.VoidType()
            elif ast_node == 'float':
                return ir_float
            elif ast_node == 'double':
                return ir_double
            elif ast_node == 'unsignedint':
                # print(f'unsigned_int32:{unsigned_int32}')
                return unsigned_int32
            if kind in self.tool_type_defined:
                return self.tool_module.context.get_identified_type(ast_node.name)
            else:
                raise RuntimeError("Not implemented type: " + kind)
        else:
            if ast_node.name in self.tool_used_memory:
                if flag == 0:
                    return self.tool_used_memory[ast_node.name]
                elif flag == 1:
                    return self.tool_builders.load(self.tool_used_memory[ast_node.name])

            elif ast_node.name in self.tool_global_variables:
                if flag == 0:
                    return self.tool_global_variables[ast_node.name]
                elif flag == 1:
                    return self.tool_builders.load(self.tool_global_variables[ast_node.name])
            else:
                raise RuntimeError("Undefined variable: " + ast_node.name)


    def visit_BinaryOp(self, ast_node, flag=0):
        left = self.visit(ast_node.left, flag)
        right = self.visit(ast_node.right, 1)
        if right == 'NULL':
            right = ir.Constant(int32, 0).bitcast(left.type)
        if left == 'NULL':
            left = ir.Constant(int32, 0).bitcast(right.type)
        if ast_node.OperationName == '+':
            if not isinstance(left.type, ir.PointerType):
                return self.tool_builders.add(left, right)
            elif isinstance(left.type.pointee, ir.ArrayType):
                zero = ir.Constant(int32, 0)
                first_addr = self.tool_builders.gep(left, [zero, zero], inbounds=True)
                return self.tool_builders.gep(first_addr, [right], inbounds=True)
            # if isinstance(left.type, ir.PointerType):
            #     if isinstance(left.type.pointee, ir.ArrayType):
            #         zero = ir.Constant(int32, 0)
            #         first_addr = self.tool_builders.gep(left, [zero, zero], inbounds=True)
            #         return self.tool_builders.gep(first_addr, [right], inbounds=True)
            #     elif isinstance(left.type.pointee, ir.IntType):
            #         pass

            # return self.tool_builders.add(left, right)
        elif ast_node.OperationName == '-':
            return self.tool_builders.sub(left, right)
        elif ast_node.OperationName == '*':
            return self.tool_builders.mul(left, right)
        elif ast_node.OperationName == '/':
            return self.tool_builders.sdiv(left, right)
        elif ast_node.OperationName in {'<', '<=', '==', '!=', '>=', '>'}:
            return self.tool_builders.icmp_signed(ast_node.OperationName, left, right)
        # elif ast_node.OperationName == '===':
        #     return self.tool_builders.icmp_signed('==', left, right)
        left_constant = ir.Constant(left.type, 0)
        right_constant = ir.Constant(right.type, 0)
        left = self.tool_builders.icmp_signed('!=', left, left_constant)
        right = self.tool_builders.icmp_signed('!=', right, right_constant)

        if ast_node.OperationName == '&&':
            # left = self.tool_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
            # right = self.tool_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
            return self.tool_builders.and_(left, right)
        elif ast_node.OperationName == '||':
            # left = self.tool_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
            # right = self.tool_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
            return self.tool_builders.or_(left, right)
        else:
            raise RuntimeError("not implement binary operator!")

    def visit_UnaryOp(self, ast_node, flag=0):
        result = None
        if (ast_node.OperationName == '&'):
            result =  self.visit(ast_node.expression, 0)
        elif (ast_node.OperationName == '-'):
            result =  self.tool_builders.neg(self.visit(ast_node.expression, 1))
        elif (ast_node.OperationName == '!'):
            obj = self.visit(ast_node.expression, 1)
            result =  self.tool_builders.icmp_signed('==', obj, ir.Constant(obj.type, 0))
        # elif (ast_node.OperationName == '*'):
        #     result =  self.visit(ast_node.expression, 1)
        elif (ast_node.OperationName == '++'):
            obj = self.visit(ast_node.expression, 1)
            result =  self.tool_builders.add(obj, ir.Constant(obj.type, 1))
            self.tool_builders.store(result, self.visit(ast_node.expression, 0))
        return result
        
    def visit_Assignment(self, ast_node, flag=0):
        # print(f'visit_Assignment ast_node:{ast_node}, ast_node.left:{ast_node.left}, ast_node.right:{ast_node.right}')
        if ast_node.OperationName == '=':
            res = self.visit(ast_node.left, 0)
            assigner = self.visit(ast_node.right, 1)
            if assigner == 'NULL':
                assigner = ir.Constant(int32, 0).bitcast(res.type)
            self.tool_builders.store(assigner, res)

    def visit_Operation(self, ast_node: SynTree.Operation, flag=0):
        if ast_node.OperationType == 'BinaryOp':
            # print(f'visit_Operation ast_node.OperationType:{ast_node.OperationType}, ast_node.OperationName:{ast_node.OperationName}, ast_node.left:{ast_node.left}, ast_node.right:{ast_node.right}')
            return self.visit_BinaryOp(ast_node, flag)
            # left = self.visit(ast_node.left, flag)
            # right = self.visit(ast_node.right, 1)
            # if right == 'NULL':
            #     right = ir.Constant(int32, 0).bitcast(left.type)
            # if left == 'NULL':
            #     left = ir.Constant(int32, 0).bitcast(right.type)
            # if ast_node.OperationName == '+':
            #     if isinstance(left.type, ir.PointerType):
            #         if isinstance(left.type.pointee, ir.ArrayType):
            #             zero = ir.Constant(int32, 0)
            #             first_addr = self.tool_builders.gep(left, [zero, zero], inbounds=True)
            #             return self.tool_builders.gep(first_addr, [right], inbounds=True)
            #         elif isinstance(left.type.pointee, ir.IntType):
            #             pass

            #     return self.tool_builders.add(left, right)
            # elif ast_node.OperationName == '-':
            #     return self.tool_builders.sub(left, right)
            # elif ast_node.OperationName == '*':
            #     return self.tool_builders.mul(left, right)
            # elif ast_node.OperationName == '/':
            #     return self.tool_builders.sdiv(left, right)
            # elif ast_node.OperationName in {'<', '<=', '==', '!=', '>=', '>'}:
            #     return self.tool_builders.icmp_signed(ast_node.OperationName, left, right)
            # elif ast_node.OperationName == '===':
            #     return self.tool_builders.icmp_signed('==', left, right)
            # elif ast_node.OperationName == '&&':
            #     left = self.tool_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
            #     right = self.tool_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
            #     return self.tool_builders.and_(left, right)
            # elif ast_node.OperationName == '||':
            #     left = self.tool_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
            #     right = self.tool_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
            #     return self.tool_builders.or_(left, right)
            # else:
            #     raise RuntimeError("not implement binary operator!")
        elif ast_node.OperationType == 'UnaryOp':
            # print(f'visit_Operation ast_node.OperationType:{ast_node.OperationType}, ast_node.OperationName:{ast_node.OperationName}, ast_node.expression:{ast_node.expression}')
            return self.visit_UnaryOp(ast_node, flag)
            # if (ast_node.OperationName == '&'):
            #     return self.visit(ast_node.expression, 0)
            # elif (ast_node.OperationName == '!'):
            #     obj = self.visit(ast_node.expression, 1)
            #     return self.tool_builders.icmp_signed('==', obj, ir.Constant(obj.type, 0))
            # elif (ast_node.OperationName == '*'):
            #     return self.visit(ast_node.expression, 1)
            # elif (ast_node.OperationName == '-'):
            #     return self.tool_builders.neg(self.visit(ast_node.expression, 1))
        elif ast_node.OperationType == 'Assignment':
            # print(f'visit_Operation ast_node.OperationType:{ast_node.OperationType}, ast_node.OperationName:{ast_node.OperationName}, ast_node.left:{ast_node.left}, ast_node.right:{ast_node.right}')
            return self.visit_Assignment(ast_node, flag)
        
            # if ast_node.OperationName == '=':
            #     # print(f'left:{ast_node.left}, right:{ast_node.right}')
            #     res = self.visit(ast_node.left, 0)
            #     assigner = self.visit(ast_node.right, 1)
            #     # print(f'visit_Operation ast_node.OperationType:{ast_node.OperationType}, ast_node.OperationName:{ast_node.OperationName}, res:{res}, assigner:{assigner}')
            #     if assigner == 'NULL':
            #         assigner = ir.Constant(int32, 0).bitcast(res.type)
            #     self.tool_builders.store(assigner, res)

    def visit_FunctionCall(self, ast_node, flag=0):
        fname = ast_node.name.name
        if fname not in self.tool_functions:
            fun_, arglist = self.extern_function(ast_node)
        else:
            fun_ = self.tool_functions[fname]
            arglist = list()
            if ast_node.args:
                arglist=self.visit(ast_node.args, 1)
            # else:
            #     arglist = list()
            for id, farg in enumerate(zip(arglist, fun_.args)):
                f_param,f_arg=farg
                if isinstance(f_arg.type, ir.IntType) and isinstance(f_param.type, ir.IntType) and f_arg.type.width != f_param.type.width:
                    # if isinstance(f_param.type, ir.IntType):
                        arglist[id] =  self.tool_builders.sext(f_param, f_arg.type) if (f_arg.type.width > f_param.type.width) else self.tool_builders.trunc(f_param, f_arg.type)
                        # if f_arg.type.width > f_param.type.width:
                        #     arglist[id] = self.tool_builders.sext(f_param, f_arg.type)
                        # elif f_arg.type.width < f_param.type.width:
                        #     arglist[id] = self.tool_builders.trunc(f_param, f_arg.type)
        return self.tool_builders.call(fun_, arglist)

    def visit_ControlLogic(self, ast_node, flag=0):
        # print(f'visit_ControlLogic ast_node:{ast_node}, ast_node.logicType:{ast_node.logicType}')
        if ast_node.logicType == 'If':
            judge = self.visit(ast_node.judge, 1)
            if type(judge) is not ir.IntType(1):
                judge = self.tool_builders.icmp_signed('!=', judge, ir.Constant(judge.type, 0))
            if ast_node.action2:  # false
                with self.tool_builders.if_else(judge) as (then, otherwise):
                    with then:
                        self.visit(ast_node.action1)
                    with otherwise:
                        self.visit(ast_node.action2)
            else:
                with self.tool_builders.if_then(judge):
                    self.visit(ast_node.action1)
            # judge = self.visit(ast_node.judge, 1)
            # if type(judge) is not ir.IntType(1):
            #     judge = self.tool_builders.icmp_signed('!=', judge, ir.Constant(judge.type, 0))
            # loop_s = self.tool_current_function.append_basic_block()
            # loop_e = self.tool_current_function.append_basic_block()
            # loop_then = self.tool_current_function.append_basic_block()
            # loop_otherwise = self.tool_current_function.append_basic_block()
            # self.tool_builders.branch(loop_s)
            # self.tool_builders.position_at_end(loop_s)
            # self.tool_builders.cbranch(judge, loop_then, loop_otherwise)
            # self.tool_builders.position_at_end(loop_then)
            # self.visit(ast_node.action1)
            # self.tool_builders.branch(loop_e)
            # self.tool_builders.position_at_end(loop_otherwise)

            # if ast_node.action2:  # false
            #     # with self.tool_builders.if_else(judge) as (then, otherwise):
            #     #     with then:
            #     #         self.visit(ast_node.action1)
            #     #     with otherwise:
            #     #         self.visit(ast_node.action2)
                
            #     self.visit(ast_node.action2)
            #     self.tool_builders.branch(loop_e)
            #     self.tool_builders.position_at_end(loop_e)

            # else:
            #     with self.tool_builders.if_then(judge):
            #         self.visit(ast_node.action1)
            # self.visit_ControlLogic_If(ast_node, flag=0)
        elif ast_node.logicType == 'For':
            self.visit_ControlLogic_For(ast_node, flag=0)

        elif ast_node.logicType == 'While':
            
            self.visit_ControlLogic_While(ast_node, flag=0)

        elif ast_node.logicType == 'Continue':
            self.visit_ControlLogic_Continue(ast_node, flag=0)

        elif ast_node.logicType == 'Break':
            self.visit_ControlLogic_Break(ast_node, flag=0)

        elif ast_node.logicType == 'Return':
            self.visit_ControlLogic_Return(ast_node, flag=0)


    def visit_ControlLogic_If(self, ast_node, flag=0):
        judge = self.visit(ast_node.judge, 1)
        if type(judge) is not ir.IntType(1):
            judge = self.tool_builders.icmp_signed('!=', judge, ir.Constant(judge.type, 0))
        loop_s = self.tool_current_function.append_basic_block()
        loop_e = self.tool_current_function.append_basic_block()
        loop_then = self.tool_current_function.append_basic_block()
        self.tool_start_stack+=[loop_s]
        self.tool_end_stack+=[loop_e]


        self.tool_builders.branch(loop_s)
        self.tool_builders.position_at_end(loop_s)
        if ast_node.action2:
            loop_otherwise = self.tool_current_function.append_basic_block()
            self.tool_builders.cbranch(judge, loop_then, loop_otherwise)
            self.tool_builders.position_at_end(loop_then)
            self.visit(ast_node.action1)
            try:
                self.tool_builders.branch(loop_e)

        # if ast_node.action2:  # false
        #     # with self.tool_builders.if_else(judge) as (then, otherwise):
        #     #     with then:
        #     #         self.visit(ast_node.action1)
        #     #     with otherwise:
        #     #         self.visit(ast_node.action2)
                self.tool_builders.position_at_end(loop_otherwise)
                self.visit(ast_node.action2)
                self.tool_builders.branch(loop_e)
                self.tool_builders.position_at_end(loop_e)
            except:
                pass
        else:
            self.tool_builders.cbranch(judge, loop_then, loop_e)
            self.tool_builders.position_at_end(loop_then)
            self.visit(ast_node.action1)
            try:
                self.tool_builders.branch(loop_e)
                self.tool_builders.position_at_end(loop_e)
            except:
                pass

        
        self.tool_end_stack.pop()
        self.tool_start_stack.pop()
        self.tool_builders.position_at_end(loop_e)

    def visit_ControlLogic_For(self, ast_node, flag=0):
        # print(f'ast_node.first:{ast_node.first}, ast_node.judge:{ast_node.judge}, ast_node.action:{ast_node.action}, ast_node.statement:{ast_node.statement}')
        self.visit(ast_node.first)
        loop_e = self.tool_current_function.append_basic_block()
        loop_s = self.tool_current_function.append_basic_block()
        loop_body = self.tool_current_function.append_basic_block()
        self.tool_start_stack+=[loop_s]
        self.tool_end_stack+=[loop_e]
        self.tool_builders.branch(loop_s)
        self.tool_builders.position_at_end(loop_s)
        condition = self.visit(ast_node.judge, 1)
        if type(condition) is not ir.IntType(1):
            condition = self.tool_builders.icmp_signed('!=', condition, ir.Constant(condition.type, 0))
        self.tool_builders.cbranch(condition, loop_body, loop_e)
        self.tool_builders.position_at_end(loop_body)
        self.visit(ast_node.statement)
        # print(f'ast_node.action:{ast_node.action}')
        self.visit(ast_node.action)
        self.tool_builders.branch(loop_s)
        self.tool_start_stack.pop()
        self.tool_end_stack.pop()
        self.tool_builders.position_at_end(loop_e)


    def visit_ControlLogic_While(self, ast_node, flag=0):
        # print(f'visit_ControlLogic_While ast_node:{ast_node}, ast_node.judge:{ast_node.judge}, ast_node.action:{ast_node.action}')
        loop_s = self.tool_current_function.append_basic_block()
        loop_body = self.tool_current_function.append_basic_block()
        loop_e = self.tool_current_function.append_basic_block()
        self.tool_start_stack+=[loop_s]
        self.tool_end_stack+=[loop_e]

        self.tool_builders.branch(loop_s)
        self.tool_builders.position_at_end(loop_s)
        condition = self.visit(ast_node.judge, 1)
        # print(f'condition:{condition}')
        if type(condition) is not ir.IntType(1):
            condition = self.tool_builders.icmp_signed('!=', condition, ir.Constant(condition.type, 0))
        self.tool_builders.cbranch(condition, loop_body, loop_e)

        self.tool_builders.position_at_end(loop_body)
        self.visit(ast_node.action)
        self.tool_builders.branch(loop_s)

        self.tool_start_stack.pop()
        self.tool_end_stack.pop()
        self.tool_builders.position_at_end(loop_e)

    def visit_ControlLogic_Continue(self, ast_node, flag=0):
        self.tool_builders.branch(self.tool_start_stack[-1])

    def visit_ControlLogic_Break(self, ast_node, flag=0):
        self.tool_builders.branch(self.tool_end_stack[-1])

    def visit_ControlLogic_Return(self, ast_node, flag=0):
        if ast_node.return_result:
                # print(f'ast_node.return_result:{ast_node.return_result}')
                return_value = self.visit(ast_node.return_result, 1)
                self.tool_builders.ret(return_value)
        else:
            self.tool_builders.ret_void()

    def visit_Ref(self, ast_node: SynTree.Ref, flag=0):
        # # print(f'visit_Ref ast_node:{ast_node}, ast_node.refType:{ast_node.refType}, ast_node.name:{ast_node.name}, ast_node.sub:{ast_node.sub}')
        """
        ArrayRef,按照下标获取数组某个元素
        StructRef，按照域名获取结构体成员变量
        """
        # zero = ir.Constant(int32, 0)
        ele_addr = None
        if ast_node.refType == 'ArrayRef':
            ele_addr = self.tool_builders.gep(self.visit(ast_node.name),
                                                        [ir.Constant(int32, 0), self.visit(ast_node.sub, 1)], inbounds=True)
            if flag == 0:
                return ele_addr
            elif flag == 1:
                return self.tool_builders.load(ele_addr)
        elif ast_node.refType == 'StructRef':
            if ast_node.type == '->':
                name_of_struct = self.visit(ast_node.name, 1)
                index = ir.Constant(int32,
                                    self.tool_type_defined[name_of_struct.type.pointee.name].index(ast_node.reign.name.name))
                ele_addr = self.tool_builders.gep(name_of_struct, [ir.Constant(int32, 0), index], inbounds=True)
            if flag == 0:
                # return address
                return ele_addr
            elif flag == 1:
                # return value
                return self.tool_builders.load(ele_addr)

    def visit_ArrayRef(self, ast_node, flag=0):
        """
            Return variable in an array.
            flag == 0 -> get pointer
            flag == 1 -> get value
        """
        arr = self.visit(ast_node.name)
        index = self.visit(ast_node.subscript, 1)
        zero = ir.Constant(int32, 0)
        ele = self.tool_builders.gep(arr, [zero, index], inbounds=True)
        if flag == 0:
            return ele
        elif flag == 1:
            return self.tool_builders.load(ele)

    def visit_ContentList(self, ast_node, flag=0):
        arr = list()
        if ast_node.listType == 'Expression':
            for e in ast_node.elements:
                arr+=[self.visit(e, flag)]
            return arr
        elif ast_node.listType == 'Init':
            for e in ast_node.elements:
                arr+=[self.visit(e)]
            return ir.Constant.literal_array(arr)
        # elif ast_node.listType == 'Expression':
        #     for e in ast_node.elements:
        #         arr+=[self.visit(e, flag))
        #     return arr


    def visit_CommentNode(self, ast_node, flag=0):
        # print(f'visit_CommentNode ast_node:{ast_node}, ast_node.content:{ast_node.content}')
        content = ast_node.content
        if '\n' in ast_node.content:
            content = content[0:-1]
        if '//' in ast_node.content:
            content = content[2:]
        if '/*' in ast_node.content:
            content = content[2:-2]
        if self.tool_builders:
            self.tool_builders.comment(content)
            

    def extern_function(self, ast_node):
        # zero = ir.Constant(int32, 0)

        # def _from_arg_get_address(arg):
        #     return self.tool_builders.gep(self.visit(arg, flag=0), [ir.Constant(int32, 0), ir.Constant(int32, 0)], inbounds=True)

        arguList = list()

        if ast_node.args is  None:
            arg_eles = list()
        else:
            arg_eles = ast_node.args.elements
        
        if ast_node.name.name in ['printf', 'scanf']:
            if ast_node.name.name == 'printf':
                fType = ir_func(int32, [int8.as_pointer()], var_arg=True)
            else:
                fType = ir_func(int32, [ir.PointerType(int8)], var_arg=True)
            for i, a in enumerate(arg_eles):
                if i == 0:
                    arguList+=[self.visit(a)]
                else:
                    arguList+=[self.visit(a, flag=1)]
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'gets':
            fType = ir_func(int32, list(), var_arg=True)
            for a in arg_eles:
                # ptr = _from_arg_get_address(a)
                ptr = self.tool_builders.gep(self.visit(a, flag=0), [ir.Constant(int32, 0), ir.Constant(int32, 0)], inbounds=True)
                arguList+=[ptr]
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'isdigit':
            fType = ir_func(int32, [int32], var_arg=False)
            for a in arg_eles:
                ext = self.tool_builders.sext(self.visit(a, flag=1), int32)
                arguList+=[ext]
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'strlen':
            fType = ir_func(int32, [int8.as_pointer()], var_arg=False)
            for a in arg_eles:
                # ptr = _from_arg_get_address(a)
                ptr = self.tool_builders.gep(self.visit(a, flag=0), [ir.Constant(int32, 0), ir.Constant(int32, 0)], inbounds=True)
                arguList+=[ptr]
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'atoi':
            fType = ir_func(int32, list(), var_arg=True)
            for a in arg_eles:
                # p = _from_arg_get_address(a)
                p = self.tool_builders.gep(self.visit(a, flag=0), [ir.Constant(int32, 0), ir.Constant(int32, 0)], inbounds=True)
                arguList+=[p]

            return self.builtin_func(ast_node.name.name, (), fType), arguList
        
        else:
            raise RuntimeError('Undefined function: ' + ast_node.name.name)

    def return_content(self, ast_node, arg=None):
        # print(f'return_content, ast_node:{ast_node}, arg:{arg}')
        if arg is None:
            return self.get_element_type(ast_node)
        
        if type(ast_node) == SynTree.DeclPointer and arg is not None:
            return ir.PointerType(arg)
        elif type(ast_node) == SynTree.DeclArray and arg is not None:
            return ir.ArrayType(arg, int(ast_node.dim.content))
        elif type(ast_node) == SynTree.DeclFunction and arg is not None:
            param_list = list()
            if ast_node.args:
                # print(f'ast_node.args:{ast_node.args}')
                for p in ast_node.args.elements:
                    # param_list+=[self.allocate_variable(p, flag=2))
                    tmp_node = p
                    modi_list = list()
                    while (type(tmp_node) == SynTree.DeclArray) or (type(tmp_node) == SynTree.DeclFunction) or (
            type(tmp_node) == SynTree.DeclPointer) or (type(tmp_node) == SynTree.Decl):
                        tmp_node = tmp_node.type
                        modi_list+=[tmp_node]
                    if type(tmp_node) == SynTree.Id:
                        param_list+=[self.allocate_indenti(tmp_node, flag=2, modifier_list=modi_list)]
                    elif type(tmp_node) == SynTree.Struct:
                        param_list+=[self.allocate_struct(tmp_node, flag=2, modifier_list=modi_list)]
                    # print(f'param_list:{param_list}')
            return ir_func(arg, param_list)
        elif arg is not None:
            return None
        # else:
        #     self.get_element_type(ast_node)
    def get_regular_type(self, ast_node):
        if ast_node == 'int':
            return int32
        elif ast_node == 'char':
            return int8
        elif ast_node == 'void':
            return ir.VoidType()
        elif ast_node == 'float':
            return ir_float
        elif ast_node == 'double':
            return ir_double
        elif ast_node == 'unsignedint':
            # print(f'unsigned_int32:{unsigned_int32}')
            return unsigned_int32
    
    # def get_defined_type(self, ast_node):


    def get_element_type(self, ast_node):
        if ast_node in ['int', 'char', 'void', 'float', 'double', 'unsignedint']:
            # if ast_node == 'int':
            #     return int32
            # elif ast_node == 'char':
            #     return int8
            # elif ast_node == 'void':
            #     return ir.VoidType()
            # elif ast_node == 'float':
            #     return ir_float
            # elif ast_node == 'double':
            #     return ir_double
            # elif ast_node == 'unsignedint':
            #     # print(f'unsigned_int32:{unsigned_int32}')
            #     return unsigned_int32
            return self.get_regular_type(ast_node)
        elif ast_node in self.tool_type_defined:
            return self.tool_module.context.get_identified_type(ast_node.name)
        return None

    def allocate_variable(self, ast_node, flag=0, modifier_list=list()):
        # print(f'allocate_variable, ast_node:{ast_node}, flag:{flag}, modifier_list:{modifier_list}')
        if type(ast_node) == SynTree.Id:
            # print(f'ast_node.name:{ast_node.name}')
            return self.allocate_indenti(ast_node, flag, modifier_list)
        elif type(ast_node) == SynTree.Struct:
            return self.allocate_struct(ast_node, flag, modifier_list)
        elif (type(ast_node) == SynTree.DeclArray) or (type(ast_node) == SynTree.DeclFunction) or (
                type(ast_node) == SynTree.DeclPointer) or (type(ast_node) == SynTree.Decl):
            return self.allocate_variable(ast_node.type, flag, modifier_list + [ast_node])

    def allocate_indenti(self, ast_node, flag=0, modifier_list=list()):
        if ast_node.spec[0] in ['int', 'char', 'void', 'float', 'double', 'unsignedint']:
            iden_type = self.get_regular_type(ast_node.spec[0])
        elif ast_node.spec[0] in self.tool_type_defined:
            iden_type = self.tool_module.context.get_identified_type(ast_node.spec[0].name)
        iden_name = modifier_list.pop(0).name
        # print(f'allocate_indenti, iden_type:{iden_type}, iden_name:{iden_name}, flag:{flag}, modifier_list:{modifier_list}')
        # allocate_indenti, iden_type:i32, iden_name:main, flag:2, modifier_list:[<SynTree.DeclFunction object at 0x100af2150>]
        for modifier in modifier_list:
            iden_type = self.return_content(modifier, iden_type)
            # print(f'iden_type:{iden_type}, modifier:{modifier}')

        return self.handle_allocate_indenti_by_flag(ast_node, iden_type, iden_name, flag, modifier_list)

    def handle_allocate_indenti_by_flag(self, ast_node, iden_type, iden_name, flag=0, modifier_list=list()):
        # print(f'handle_allocate_indenti_by_flag, ast_node:{ast_node}, iden_type:{iden_type}, iden_name:{iden_name}, flag:{flag}, modifier_list:{modifier_list}')
        # print(f'self.tool_used_memory:{self.tool_used_memory}')
        if flag == 0:  # local
            self.tool_used_memory[ast_node.name] = self.tool_builders.alloca(iden_type, name=iden_name)
            return iden_type
        elif flag == 1:  # global
            self.tool_global_variables[iden_name] = ir.GlobalVariable(self.tool_module, iden_type, name=iden_name)
            self.tool_global_variables[iden_name].initializer = ir.Constant(iden_type, None)
            return iden_type
        elif flag == 2: # function
            if len(modifier_list) > 0:
                if type(modifier_list[0]) == SynTree.DeclFunction:
                    new_func = ir.Function(self.tool_module, iden_type, name=iden_name)
                    # new_func:declare i32 @"main"()
                    # print(f'new_func:{new_func}')
                    if modifier_list[0].args:
                        # print(f'modifier_list[0].args:{modifier_list[0].args}')
                        params = list()
                        for p in modifier_list[0].args.elements:
                            params+=[p.name]
                        arg_name_list = zip(new_func.args, params)
                        for a, name_ in arg_name_list:
                            a.name = name_
                            self.tool_arguments[name_] = a
                            if isinstance(a.type, ir.IntType):
                                if a.type.width == 8:
                                    a.add_attribute('signext')
                    self.tool_functions[iden_name] = new_func
                    return new_func
                else:
                    return iden_type
            else:
                return iden_type

    def handle_decl_args(self, ast_node, flag):
        # print(f'handle_decl_args, ast_node:{ast_node}, flag:{flag}, init:{ast_node.init}')
        # if ast_node.init:
        if flag == 0 and ast_node.init:
            # print(f'flag=0 ast_node.name:{ast_node.name}, self.tool_used_memory:{self.tool_used_memory}, self.tool_used_memory[ast_node.name]:{self.tool_used_memory[ast_node.name]}')
            self.tool_builders.store(self.visit(ast_node.init, 1), self.tool_used_memory[ast_node.name])
            # 
            # ast_node.name:a, self.tool_used_memory:{'a': <ir.AllocaInstr 'a' of type 'i32*', OperationName 'alloca', operands ()>}, self.tool_used_memory[ast_node.name]:%"a" = alloca i32
            # self.tool_used_memory: {'a': <ir.AllocaInstr 'a' of type 'i32*', OperationName 'alloca', operands ()>}：这是一个字典（Dictionary），其中键（Key）是变量名，值（Value）是某个 LLVM IR 中的 alloca 指令对象。alloca 指令用于在函数的栈帧中分配变量的内存空间。
            # 在这里，'a' 是变量名，<ir.AllocaInstr 'a' of type 'i32*', OperationName 'alloca', operands ()> 是相应的 alloca 指令对象。
            # self.tool_used_memory[ast_node.name]:%"a" = alloca i32：这是 LLVM IR 代码的一部分，表示在变量 a 的内存分配指令。%"a" 是 LLVM IR 中的变量标识符，alloca i32 是分配 i32 类型（32位整数）的内存空间的指令。
            # 
            # 
            # ast_node.name:c, self.tool_used_memory:{'a': <ir.AllocaInstr 'a' of type 'i32*', OperationName 'alloca', operands ()>, 'b': <ir.AllocaInstr 'b' of type 'i32*', OperationName 'alloca', operands ()>, 'c': <ir.AllocaInstr 'c' of type 'i32*', OperationName 'alloca', operands ()>}, self.tool_used_memory[ast_node.name]:%"c" = alloca i32
            # 
            # 
            # 
        elif flag == 1 and ast_node.init and not self.tool_global_variables[ast_node.name].initializer:
            # print(f'flag=1 ast_node.name:{ast_node.name}, self.tool_global_variables:{self.tool_global_variables}, self.tool_global_variables[ast_node.name]:{self.tool_global_variables[ast_node.name]}')
            # if not self.tool_global_variables[ast_node.name].initializer:
            self.tool_global_variables[ast_node.name].initializer = self.visit(ast_node.init, ast_node.name)
            # print(f'flag=1 ast_node.name:{ast_node.name}, self.tool_global_variables:{self.tool_global_variables}, self.tool_global_variables[ast_node.name]:{self.tool_global_variables[ast_node.name]}')
        elif flag == 1:
            self.tool_global_variables[ast_node.name].align = 4
            self.tool_global_variables[ast_node.name].linkage = "common"
        else:
            pass

    def allocate_struct(self, ast_node, flag=0, modifier_list=list()):
        identified_type = self.tool_module.context.get_identified_type(ast_node.name)
        if ast_node.name not in self.tool_type_defined:
            self.tool_type_defined[ast_node.name] = [e.name for e in ast_node.args]
            tool_type_defined = [self.allocate_variable(e, flag=2) for e in ast_node.args]
            identified_type.set_body(*tool_type_defined)

        mod_name = modifier_list.pop(0).name
        for m in modifier_list:
            identified_type = self.return_content(m, identified_type)

        if flag == 0:
            return identified_type
        elif flag == 1:
            self.tool_global_variables[mod_name] = ir.GlobalVariable(self.tool_module, identified_type, name=mod_name)
            self.tool_global_variables[mod_name].initializer = ir.Constant(identified_type, None)
        elif len(modifier_list) > 0:
            if type(modifier_list[0]) == SynTree.DeclFunction:
                new_func = ir.Function(self.tool_module, identified_type, name=mod_name)
                params = list()
                for p in modifier_list[0].args:
                    params+=[p.name]
                arg_name_list = zip(new_func.args, params)
                for a, name_ in arg_name_list:
                    a.name = name_
                    self.tool_arguments[name_] = a
                self.tool_functions[mod_name] = new_func
                return new_func
            else:
                return identified_type
        else:
            return identified_type

    def define_struct(self, ast_node, identified_type):
        if ast_node.name not in self.tool_type_defined:
            tmp=list()
            tool_type_defined_list=list()
            for e in ast_node.args:
                tmp+=[e]
                modi_list = list()
                temp_node = e
                while (type(ast_node) == SynTree.DeclArray) or (type(ast_node) == SynTree.DeclFunction) or (
                type(ast_node) == SynTree.DeclPointer) or (type(ast_node) == SynTree.Decl):
                    temp_node = temp_node.type
                    modi_list+=[temp_node]
                if type(temp_node) == SynTree.Id:
                    tool_type_defined_list+=[self.allocate_indenti(temp_node, flag=2, modifier_list=modi_list)]
                elif type(temp_node) == SynTree.Struct:
                    tool_type_defined_list+=[self.allocate_struct(temp_node, flag=2, modifier_list=modi_list)]
                    
                # tool_type_defined_list+=[self.allocate_variable(e, flag=2))
            self.tool_type_defined[ast_node.name] = tmp
            identified_type.set_body(*tool_type_defined_list)
        return identified_type
    
    def visit(self, node, flag=0):
        fun_name = 'visit_' + node.__class__.__name__
        # print(f'fun_name:{fun_name}, node:{node}, flag:{flag}')
        return getattr(self, fun_name)(node, flag)
