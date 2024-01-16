from __future__ import print_function
from llvmlite import ir
import SynTree as SynTree

int32 = ir.IntType(32)
int8 = ir.IntType(8)
int1 = ir.IntType(1)
ir_float = ir.FloatType()
ir_double = ir.DoubleType()
ir_func = ir.FunctionType


def c2i(s):
    if s == "'\\n'" or s == "'\\r\\n'":
        return 10
    return ord(s[1:-1])


class Coder(object):
    def __init__(self):
        self.code_module = ir.Module('my compiler')

        self.code_builders = None
        self.now_fun = None
        self.stack_start_blocks = []
        self.stack_end_blocks = []
        self.code_arguments = {}
        self.allocated_mem = {}
        self.funs = {}
        self.glb_variables = {}
        self.types = {}
        self.builtin_func = self.code_module.declare_intrinsic

    def transform_ast2code(self, tree):
        print(f'tree:{tree}')
        self.translate(tree)
        return self.code_module

    def translate(self, node, level=0):
        fun_name = 'translate_' + node.__class__.__name__
        print(f'fun_name:{fun_name}, node:{node}, level:{level}')
        return getattr(self, fun_name)(node, level)

    def translate_TopAST(self, ast_node, level=0):
        for unit in ast_node.unitList:
            if isinstance(unit, SynTree.FuncDef):
                self.translate(unit, level=0)
            elif isinstance(unit, SynTree.DeclarationNode):
                self.translate(unit, level=1)

    def translate_DeclarationNode(self, ast_node, level=0):
        """
            声明并分配内存
        """
        print(f'translate_DeclarationNode ast_node.name:{ast_node.name}, next type:{ast_node.type}, quals:{ast_node.quals}, spec:{ast_node.spec}, init:{ast_node.init}')
        # ast_node.name:main, type:<cAST.DeclFunction object at 0x10566b910>, quals:[], spec:['int'], init:None

        # ast_node.name:a, type:<cAST.Identifier object at 0x100fdf390>, quals:[], spec:['int'], init:<cAST.Constant object at 0x100fdf290>

        # ast_node.name:b, next type:<cAST.Identifier object at 0x1054b3a10>, quals:[], spec:['int'], init:<cAST.Constant object at 0x1054b3cd0>

        # ast_node.name:c, next type:<cAST.Identifier object at 0x1054b3fd0>, quals:[], spec:['int'], init:<cAST.Operation object at 0x1054d4250>

        if ast_node.name in self.allocated_mem.keys() or ast_node.name in self.code_arguments.keys() or ast_node.name in self.glb_variables.keys():
            raise RuntimeError("Duplicate variable declaration: " + ast_node.name)
        dec = self.allocate_variable(ast_node, level, [])
        self.handle_decl_args(ast_node, level)
        if level == 2:
            return dec

    def translate_FuncDef(self, ast_node, level=0):
        self.code_arguments.clear()
        print(f'translate_FuncDef ast_node.decl:{ast_node.decl}, ast_node.body:{ast_node.body}, param_decls:{ast_node.param_decls}')
        # ast_node.decl:<cAST.DeclarationNode object at 0x10566bb50>, ast_node.body:<cAST.BlockStatement object at 0x10566bdd0>, param_decls:None
        func_ = self.translate(ast_node.decl, level=2)
        self.now_fun = func_

        if ast_node.body:
            print(f'func_的类型是{type(func_)}')
            # func_的类型是<class 'llvmlite.ir.values.Function'>
            ent = func_.append_basic_block(name="entry")
            self.code_builders = ir.IRBuilder(ent)
            # 通过self.code_builders对象，可以使用IRBuilder类的方法来生成LLVM IR代码，例如创建指令、基本块、函数等，并将其添加到相应的函数中。
            # 通过append_basic_block方法，可以在函数中添加一个基本块，该方法的参数name是可选的，用于指定基本块的名称。
            print(f'func_args:{func_.args}')
            for a in func_.args:
                self.allocated_mem[a.name] = self.code_builders.alloca(a.type, name=a.name)
                self.code_builders.store(a, self.allocated_mem[a.name])

            self.translate(ast_node.body)
        else:
            self.now_fun = None
            func_.is_declaration = True

        del self.stack_start_blocks[:]
        del self.stack_end_blocks[:]
        self.allocated_mem.clear()
        self.code_arguments.clear()
        self.now_fun = None

    def translate_BlockStatement(self, ast_node, level=0):
        if ast_node.block_items:
            for item in ast_node.block_items:
                print(f'item:{item}')
                self.translate(item, level=0)

    def translate_Constant(self, ast_node, level=0):
        print(f'translate_Constant ast_node.kind:{ast_node.kind}, ast_node.content:{ast_node.content}')
        if ast_node.kind == 'int':
            res = ir.Constant(int32, ast_node.content)
        elif ast_node.kind == 'float':
            res = ir.Constant(ir_float, ast_node.content)
        elif ast_node.kind == 'double':
            res = ir.Constant(ir_double, ast_node.content)
        elif ast_node.kind == 'char':
            res = ir.Constant(int8, c2i(ast_node.content))
        elif ast_node.kind == 'string':
            mid_str = ast_node.content[1:-1].replace('\\n', '\n') + '\0'
            arr_str = ir.ArrayType(int8, len(mid_str))
            str_name = '.str' + str(len(self.glb_variables))
            glb_str = ir.GlobalVariable(self.code_module, arr_str, name=str_name)
            glb_str.initializer = ir.Constant(arr_str, bytearray(mid_str, 'utf-8'))
            glb_str.global_constant = True
            self.glb_variables[str_name] = glb_str
            zero = ir.Constant(int32, 0)
            return self.code_builders.gep(glb_str, [zero, zero], inbounds=True)
        else:
            raise RuntimeError("The type is not recognized: " + ast_node.kind)
        return res


    def translate_Identifier(self, ast_node, level=0):
        print(f'translate_Identifier ast_node:{ast_node}, ast_node.name:{ast_node.name}, ast_node.spec:{ast_node.spec}')
        if ast_node.spec:
            kind = ast_node.spec
            if kind == 'int':
                return int32
            if kind == 'char':
                return int8
            if kind == 'void':
                return ir.VoidType()
            if kind in self.types:
                return self.code_module.context.get_identified_type(ast_node.name)
            else:
                raise RuntimeError("Not implemented type: " + kind)
        else:
            if ast_node.name in self.allocated_mem:
                if level == 0:
                    return self.allocated_mem[ast_node.name]
                elif level == 1:
                    return self.code_builders.load(self.allocated_mem[ast_node.name])

            elif ast_node.name in self.glb_variables:
                if level == 0:
                    return self.glb_variables[ast_node.name]
                elif level == 1:
                    return self.code_builders.load(self.glb_variables[ast_node.name])
            else:
                raise RuntimeError("Undefined variable: " + ast_node.name)


    def translate_Operation(self, ast_node: SynTree.Operation, level=0):
        if ast_node.OpType == 'BinaryOp':
            print(f'translate_Operation ast_node.OpType:{ast_node.OpType}, ast_node.OpName:{ast_node.OpName}, ast_node.left:{ast_node.left}, ast_node.right:{ast_node.right}')

            left = self.translate(ast_node.left, level)
            right = self.translate(ast_node.right, 1)
            if right == 'NULL':
                right = ir.Constant(int32, 0).bitcast(left.type)
            if left == 'NULL':
                left = ir.Constant(int32, 0).bitcast(right.type)
            if ast_node.OpName == '+':
                if isinstance(left.type, ir.PointerType):
                    if isinstance(left.type.pointee, ir.ArrayType):
                        zero = ir.Constant(int32, 0)
                        first_addr = self.code_builders.gep(left, [zero, zero], inbounds=True)
                        return self.code_builders.gep(first_addr, [right], inbounds=True)
                    elif isinstance(left.type.pointee, ir.IntType):
                        pass

                return self.code_builders.add(left, right)
            elif ast_node.OpName == '-':
                return self.code_builders.sub(left, right)
            elif ast_node.OpName == '*':
                return self.code_builders.mul(left, right)
            elif ast_node.OpName == '/':
                return self.code_builders.sdiv(left, right)
            elif ast_node.OpName in {'<', '<=', '==', '!=', '>=', '>'}:
                return self.code_builders.icmp_signed(ast_node.OpName, left, right)
            elif ast_node.OpName == '===':
                return self.code_builders.icmp_signed('==', left, right)
            elif ast_node.OpName == '&&':
                left = self.code_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
                right = self.code_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
                return self.code_builders.and_(left, right)
            elif ast_node.OpName == '||':
                left = self.code_builders.icmp_signed('!=', left, ir.Constant(left.type, 0))
                right = self.code_builders.icmp_signed('!=', right, ir.Constant(right.type, 0))
                return self.code_builders.or_(left, right)
            else:
                raise RuntimeError("not implement binary operator!")
        elif ast_node.OpType == 'UnaryOp':
            if (ast_node.OpName == '&'):
                return self.translate(ast_node.expression, 0)
            elif (ast_node.OpName == '!'):
                obj = self.translate(ast_node.expression, 1)
                return self.code_builders.icmp_signed('==', obj, ir.Constant(obj.type, 0))
            elif (ast_node.OpName == '*'):
                return self.translate(ast_node.expression, 1)
            elif (ast_node.OpName == '-'):
                return self.code_builders.neg(self.translate(ast_node.expression, 1))
        elif ast_node.OpType == 'Assignment':
            if ast_node.OpName == '=':
                res = self.translate(ast_node.left, 0)
                assigner = self.translate(ast_node.right, 1)
                if assigner == 'NULL':
                    assigner = ir.Constant(int32, 0).bitcast(res.type)
                self.code_builders.store(assigner, res)

    def translate_FuncCall(self, ast_node, level=0):
        fname = ast_node.name.name
        if fname not in self.funs:
            fun_, arglist = self.extern_function(ast_node)
        else:
            fun_ = self.funs[fname]
            if ast_node.args:
                arglist=self.translate(ast_node.args, 1)
            else:
                arglist = []
            for id, farg in enumerate(zip(arglist, fun_.args)):
                f_param,f_arg=farg
                if isinstance(f_arg.type, ir.IntType):
                    if isinstance(f_param.type, ir.IntType):
                        if f_arg.type.width > f_param.type.width:
                            arglist[id] = self.code_builders.sext(f_param, f_arg.type)
                        elif f_arg.type.width < f_param.type.width:
                            arglist[id] = self.code_builders.trunc(f_param, f_arg.type)
        return self.code_builders.call(fun_, arglist)

    def translate_ControlLogic(self, ast_node, level=0):
        if ast_node.logicType == 'If':
            judge = self.translate(ast_node.judge, 1)
            if type(judge) is not ir.IntType(1):
                judge = self.code_builders.icmp_signed('!=', judge, ir.Constant(judge.type, 0))
            if ast_node.action2:  # false
                with self.code_builders.if_else(judge) as (then, otherwise):
                    with then:
                        self.translate(ast_node.action1)
                    with otherwise:
                        self.translate(ast_node.action2)
            else:
                with self.code_builders.if_then(judge):
                    self.translate(ast_node.action1)
        elif ast_node.logicType == 'While':
            loop_s = self.now_fun.append_basic_block()
            loop_body = self.now_fun.append_basic_block()
            loop_e = self.now_fun.append_basic_block()
            self.stack_start_blocks.append(loop_s)
            self.stack_end_blocks.append(loop_e)

            self.code_builders.branch(loop_s)
            self.code_builders.position_at_end(loop_s)
            condition = self.translate(ast_node.judge, 1)
            if type(condition) is not ir.IntType(1):
                condition = self.code_builders.icmp_signed('!=', condition, ir.Constant(condition.type, 0))
            self.code_builders.cbranch(condition, loop_body, loop_e)

            self.code_builders.position_at_end(loop_body)
            self.translate(ast_node.action)
            self.code_builders.branch(loop_s)

            self.stack_start_blocks.pop()
            self.stack_end_blocks.pop()
            self.code_builders.position_at_end(loop_e)

        elif ast_node.logicType == 'Continue':
            self.code_builders.branch(self.stack_start_blocks[-1])

        elif ast_node.logicType == 'Break':
            self.code_builders.branch(self.stack_end_blocks[-1])

        elif ast_node.logicType == 'Return':
            if ast_node.return_result:
                value_to_return = self.translate(ast_node.return_result, 1)
                self.code_builders.ret(value_to_return)
            else:
                self.code_builders.ret_void()

    def translate_Ref(self, ast_node: SynTree.Ref, level=0):
        """
        ArrayRef,按照下标获取数组某个元素
        StructRef，按照域名获取结构体成员变量
        """
        zero = ir.Constant(int32, 0)
        address_of_element = None
        if ast_node.refType == 'ArrayRef':
            address_of_element = self.code_builders.gep(self.translate(ast_node.name),
                                                        [zero, self.translate(ast_node.sub, 1)], inbounds=True)
        elif ast_node.refType == 'StructRef':
            if ast_node.type == '->':
                name_of_struct = self.translate(ast_node.name, 1)
                index = ir.Constant(int32,
                                    self.types[name_of_struct.type.pointee.name].index(ast_node.field.name.name))
                address_of_element = self.code_builders.gep(name_of_struct, [zero, index], inbounds=True)
        if level == 0:
            # return address
            return address_of_element
        elif level == 1:
            # return value
            return self.code_builders.load(address_of_element)

    def translate_ArrayRef(self, ast_node, level=0):
        """
            Return variable in an array.
            level == 0 -> get pointer
            level == 1 -> get value
        """
        arr = self.translate(ast_node.name)
        index = self.translate(ast_node.subscript, 1)
        zero = ir.Constant(int32, 0)
        ele = self.code_builders.gep(arr, [zero, index], inbounds=True)
        if level == 0:
            return ele
        elif level == 1:
            return self.code_builders.load(ele)

    def translate_ContentList(self, ast_node, level=0):
        arr = []

        if ast_node.listType == 'InitList':
            for e in ast_node.elements:
                arr.append(self.translate(e))
            return ir.Constant.literal_array(arr)
        elif ast_node.listType == 'ExprList':
            for e in ast_node.elements:
                arr.append(self.translate(e, level))
            return arr

    def extern_function(self, ast_node):
        zero = ir.Constant(int32, 0)

        def _from_arg_get_address(arg):
            return self.code_builders.gep(self.translate(arg, level=0), [zero, zero], inbounds=True)

        arguList = []

        if ast_node.args is not None:
            arg_eles = ast_node.args.elements
        else:
            arg_eles = []
        
        if ast_node.name.name in ['printf', 'scanf']:
            if ast_node.name.name == 'printf':
                fType = ir_func(int32, [int8.as_pointer()], var_arg=True)
            else:
                fType = ir_func(int32, [ir.PointerType(int8)], var_arg=True)
            for i, a in enumerate(arg_eles):
                if i == 0:
                    arguList.append(self.translate(a))
                else:
                    arguList.append(self.translate(a, level=1))
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'gets':
            fType = ir_func(int32, [], var_arg=True)
            for a in arg_eles:
                ptr = _from_arg_get_address(a)
                arguList.append(ptr)
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'isdigit':
            fType = ir_func(int32, [int32], var_arg=False)
            for a in arg_eles:
                ext = self.code_builders.sext(self.translate(a, level=1), int32)
                arguList.append(ext)
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'strlen':
            fType = ir_func(int32, [int8.as_pointer()], var_arg=False)
            for a in arg_eles:
                ptr = _from_arg_get_address(a)
                arguList.append(ptr)
            return self.builtin_func(ast_node.name.name, (), fType), arguList

        elif ast_node.name.name == 'atoi':
            fType = ir_func(int32, [], var_arg=True)
            for a in arg_eles:
                p = _from_arg_get_address(a)
                arguList.append(p)

            return self.builtin_func(ast_node.name.name, (), fType), arguList
        
        else:
            raise RuntimeError('Undefined function: ' + ast_node.name.name)

    def return_content(self, ast_node, arg=None):
        if arg is not None:
            if type(ast_node) == SynTree.DeclPointer:
                return ir.PointerType(arg)
            elif type(ast_node) == SynTree.DeclArray:
                return ir.ArrayType(arg, int(ast_node.dim.content))
            elif type(ast_node) == SynTree.DeclFunction:
                param_list = []
                if ast_node.args:
                    for p in ast_node.args.elements:
                        param_list.append(self.allocate_variable(p, level=2))
                return ir_func(arg, param_list)
            else:
                return None
        else:
            self.return_element_type(ast_node)

    def return_element_type(self, ast_node):
        if ast_node in ['int', 'char', 'void']:
            if ast_node == 'int':
                return int32
            elif ast_node == 'char':
                return int8
            elif ast_node == 'void':
                return ir.VoidType()
        elif ast_node in self.types:
            return self.code_module.context.get_identified_type(ast_node.name)
        return None

    def allocate_variable(self, ast_node, level=0, modifier_list=[]):
        print(f'allocate_variable, ast_node:{ast_node}, level:{level}, modifier_list:{modifier_list}')
        if type(ast_node) == SynTree.Identifier:
            print(f'ast_node.name:{ast_node.name}')
            return self.allocate_indenti(ast_node, level, modifier_list)
        elif type(ast_node) == SynTree.Struct:
            return self.allocate_struct(ast_node, level, modifier_list)
        elif (type(ast_node) == SynTree.DeclArray) or (type(ast_node) == SynTree.DeclFunction) or (
                type(ast_node) == SynTree.DeclPointer) or (type(ast_node) == SynTree.DeclarationNode):
            return self.allocate_variable(ast_node.type, level, modifier_list + [ast_node])

    def allocate_indenti(self, ast_node, level=0, modifier_list=[]):
        iden_type = self.return_element_type(ast_node.spec[0])
        iden_name = modifier_list.pop(0).name
        print(f'allocate_indenti, iden_type:{iden_type}, iden_name:{iden_name}, level:{level}, modifier_list:{modifier_list}')
        for modifier in modifier_list:
            iden_type = self.return_content(modifier, iden_type)

        return self.handle_allocate_indenti_by_level(ast_node, iden_type, iden_name, level, modifier_list)

    def handle_allocate_indenti_by_level(self, ast_node, iden_type, iden_name, level=0, modifier_list=[]):
        if level == 0:  # local
            self.allocated_mem[ast_node.name] = self.code_builders.alloca(iden_type, name=iden_name)
            return iden_type
        elif level == 1:  # global
            self.glb_variables[iden_name] = ir.GlobalVariable(self.code_module, iden_type, name=iden_name)
            self.glb_variables[iden_name].initializer = ir.Constant(iden_type, None)
            return iden_type
        elif level == 2:
            if len(modifier_list) > 0:
                if type(modifier_list[0]) == SynTree.DeclFunction:
                    new_func = ir.Function(self.code_module, iden_type, name=iden_name)
                    if modifier_list[0].args:
                        params = []
                        for p in modifier_list[0].args.elements:
                            params.append(p.name)
                        arg_name_list = zip(new_func.args, params)
                        for a, name_ in arg_name_list:
                            a.name = name_
                            self.code_arguments[name_] = a
                            if isinstance(a.type, ir.IntType):
                                if a.type.width == 8:
                                    a.add_attribute('signext')
                    self.funs[iden_name] = new_func
                    return new_func
                else:
                    return iden_type
            else:
                return iden_type

    def handle_decl_args(self, ast_node, level):
        print(f'handle_decl_args, ast_node:{ast_node}, level:{level}, init:{ast_node.init}')
        if ast_node.init:
            if level == 0:
                print(f'level=0 ast_node.name:{ast_node.name}, self.allocated_mem:{self.allocated_mem}, self.allocated_mem[ast_node.name]:{self.allocated_mem[ast_node.name]}')
                self.code_builders.store(self.translate(ast_node.init, 1), self.allocated_mem[ast_node.name])
                # 
                # ast_node.name:a, self.allocated_mem:{'a': <ir.AllocaInstr 'a' of type 'i32*', opname 'alloca', operands ()>}, self.allocated_mem[ast_node.name]:%"a" = alloca i32
                # self.allocated_mem: {'a': <ir.AllocaInstr 'a' of type 'i32*', opname 'alloca', operands ()>}：这是一个字典（Dictionary），其中键（Key）是变量名，值（Value）是某个 LLVM IR 中的 alloca 指令对象。alloca 指令用于在函数的栈帧中分配变量的内存空间。
                # 在这里，'a' 是变量名，<ir.AllocaInstr 'a' of type 'i32*', opname 'alloca', operands ()> 是相应的 alloca 指令对象。
                # self.allocated_mem[ast_node.name]:%"a" = alloca i32：这是 LLVM IR 代码的一部分，表示在变量 a 的内存分配指令。%"a" 是 LLVM IR 中的变量标识符，alloca i32 是分配 i32 类型（32位整数）的内存空间的指令。
                # 
                # 
                # ast_node.name:c, self.allocated_mem:{'a': <ir.AllocaInstr 'a' of type 'i32*', opname 'alloca', operands ()>, 'b': <ir.AllocaInstr 'b' of type 'i32*', opname 'alloca', operands ()>, 'c': <ir.AllocaInstr 'c' of type 'i32*', opname 'alloca', operands ()>}, self.allocated_mem[ast_node.name]:%"c" = alloca i32
                # 
                # 
                # 
            elif level == 1:
                self.glb_variables[ast_node.name].initializer = self.translate(ast_node.init, ast_node.name)
        elif level == 1:
            self.glb_variables[ast_node.name].align = 4
            self.glb_variables[ast_node.name].linkage = "common"
        else:
            pass

    def allocate_struct(self, ast_node, level=0, modifier_list=[]):
        identified_type = self.code_module.context.get_identified_type(ast_node.name)
        if ast_node.name not in self.types:
            self.types[ast_node.name] = [e.name for e in ast_node.decls]
            types = [self.allocate_variable(e, level=2) for e in ast_node.decls]
            identified_type.set_body(*types)

        mod_name = modifier_list.pop(0).name
        for m in modifier_list:
            identified_type = self.return_content(m, identified_type)

        if level == 0:
            return identified_type
        elif level == 1:
            self.glb_variables[mod_name] = ir.GlobalVariable(self.code_module, identified_type, name=mod_name)
            self.glb_variables[mod_name].initializer = ir.Constant(identified_type, None)
        elif len(modifier_list) > 0:
            if type(modifier_list[0]) == SynTree.DeclFunction:
                new_func = ir.Function(self.code_module, identified_type, name=mod_name)
                params = []
                for p in modifier_list[0].args:
                    params.append(p.name)
                arg_name_list = zip(new_func.args, params)
                for a, name_ in arg_name_list:
                    a.name = name_
                    self.code_arguments[name_] = a
                self.funs[mod_name] = new_func
                return new_func
            else:
                return identified_type
        else:
            return identified_type

    def define_struct(self, ast_node, identified_type):
        if ast_node.name not in self.types:
            tmp=[]
            types_list=[]
            for e in ast_node.decls:
                tmp.append(e)
                types_list.append(self.allocate_variable(e, level=2))
            self.types[ast_node.name] = tmp
            identified_type.set_body(*types_list)
        return identified_type
