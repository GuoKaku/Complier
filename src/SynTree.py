import sys
class Node(object):

    def children(self):
        pass

    def generate_syntree(self):

        tree={}
        tree['name'] = self.__class__.__name__
        tree['children'] = []
        for (child_name, child) in self.children():
             tree['children'].append(child.generate_syntree())

        return tree


class FirstNode(Node):
    def __init__(self, nodes):
        self.nodes = nodes

    def children(self):
        child_list = []
        for id, u in enumerate(self.nodes or []):
            child_list.append(("note[%d]" % id, u))
        return tuple(child_list)


class Constant(Node):
    def __init__(self, kind, content):
        self.kind = kind
        self.content = content

    def children(self):
        return tuple([])


class Identifier(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.spec = kwargs['spec']

    def children(self):
        return tuple([])

class Struct(Node):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

    def children(self):
        child_list = []
        for i, child in enumerate(self.decls or []):
            child_list.append(("declarations[%d]" % i, child))
        return tuple(child_list)

class Blocks(Node):
    def __init__(self, blocks):
        self.blocks = blocks

    def children(self):
        child_list = []
        for i, child in enumerate(self.blocks or []):
            child_list.append(("blocks[%d]" % i, child))
        return tuple(child_list)
    
class CommentNode(Node):
    def __init__(self, content):
        self.content = content
        
    def children(self):
        return tuple([])

class FuncDef(Node):
    def __init__(self, **kwargs):
        self.decl = kwargs['decl']
        self.param_decls = kwargs['param_decls']
        self.body = kwargs['body']

    def children(self):
        child_list = []
        if self.decl is not None: child_list.append(("decl", self.decl))
        if self.body is not None: child_list.append(("body", self.body))
        for i, child in enumerate(self.param_decls or []):
            child_list.append(("params[%d]" % i, child))
        return tuple(child_list)

class EmptyStatement(Node):
    def __init__(self):
        pass
    
    def children(self):
        return tuple([])
    
class FunctionCall(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.args = kwargs['args']

    def children(self):
        child_list = []
        if self.name is not None: child_list.append(("name", self.name))
        if self.args is not None: child_list.append(("args", self.args))
        return tuple(child_list)


class ControlLogic(Node):
    def __init__(self,logicType,**kwargs):
        r"""
        logicType: If,While,Continue,Break
        """
        self.logicType=logicType
        if logicType=='If':
            self.judge = kwargs['judge']
            self.action1 = kwargs['action1']
            self.action2 = kwargs['action2']
        elif logicType == 'While':
            self.judge = kwargs['judge']
            self.action = kwargs['action']
        elif logicType == 'For':
            self.first = kwargs['first']
            self.judge = kwargs['judge']
            self.action = kwargs['action']  
            self.statement = kwargs['statement']       
        elif logicType == 'Return':
            self.return_result = kwargs['return_result']
        elif logicType in ['Continue','Break','EmptyStatement']:
            pass

    def children(self):
        child_list = []
        if self.logicType == 'If':
            if self.judge is not None: child_list.append(("condition", self.judge))
            if self.action1 is not None: child_list.append(("true_do", self.action1))
            if self.action2 is not None: child_list.append(("false_do", self.action2))
        elif self.logicType == 'While':
            if self.judge is not None: child_list.append(("condition", self.judge))
            if self.action is not None: child_list.append(("statement", self.action))
        elif self.logicType == 'For':
            if self.first is not None: child_list.append(("first", self.first))         
            if self.judge is not None: child_list.append(("condition", self.judge))
            if self.action is not None: child_list.append(("statement", self.action))
        elif self.logicType in ['Continue','Break','EmptyStatement']:
            return ()
        elif self.logicType == 'Return':
            if self.return_result != None: child_list.append(("return_result", self.return_result))
        return tuple(child_list)

class ContentList(Node):
    def __init__(self,listType,elements):
        self.listType=listType # InitList,ParamList,ExprList
        self.elements=elements

    def children(self):
        child_list = []
        prefix_str='None'
        if self.listType == 'InitList':
            prefix_str='expressions'
        elif self.listType == 'ParamList':
            prefix_str='parameters'
        elif self.listType == 'ExprList':
            prefix_str='expressions'
        for i, son in enumerate(self.elements or []):
            child_list.append((prefix_str+"[%d]" % i, son))
        return tuple(child_list)

class InlineNode(Node):
    def __init__(self, **kwargs):
        self.content = kwargs['content']

    def children(self):
        child_list = []
        if self.content is not None: child_list.append(("content", self.content))
        return tuple([])
    
class Operation(Node):

    def __init__(self, OpType, OpName,**kwargs):
        self.OpType = OpType  # Binary,Unary,Ternary
        self.OpName = OpName
        if OpType == 'BinaryOp':
            self.left = kwargs['left']
            self.right = kwargs['right']
        elif OpType == 'UnaryOp':
            self.expression = kwargs['expression']
        elif OpType == 'Assignment':
            self.left = kwargs['left']
            self.right = kwargs['right']
        elif OpType == 'TernaryOp':
            self.condition = kwargs['condition']
            self.true = kwargs['true']
            self.false = kwargs['false']

    def children(self):
        child_list = []
        if self.OpType == 'BinaryOp':
            if self.left != None: child_list.append(("left", self.left))
            if self.right != None: child_list.append(("right", self.right))
        elif self.OpType == 'UnaryOp':
            if self.expression != None: child_list.append(("expression", self.expression))
        elif self.OpType == 'Assignment':
            if self.left != None: child_list.append(("left", self.left))
            if self.right != None: child_list.append(("right", self.right))
        elif self.OpType == 'TernaryOp':
            if self.condition != None:  child_list.append(('condition',self.condition))
            if self.true != None: child_list.append(('true',self.true))
            if self.false != None: child_list.append(('false',self.false))
            
        return tuple(child_list)
    
class InitListNode(Node):
    def __init__(self, **kwargs):
        self.exprs = kwargs['exprs']

    def children(self):
        child_list = []
        for i, child in enumerate(self.exprs or []):
            child_list.append(("exprs[%d]" % i, child))
        return tuple(child_list)
    

class Ref(Node):
    """
    ArrayRef,StructRef
    """
    def __init__(self, refType,name, **kwargs):
        self.name=name
        self.refType=refType
        if refType=='ArrayRef':
            self.sub = kwargs['subscript']
        elif refType == 'StructRef':
            self.type = kwargs['type']
            self.field = kwargs['field']
            self.attr_names = ('type',)

    def children(self):
        child_list = []
        if self.name is not None: child_list.append(("name", self.name))
        if self.refType == 'ArrayRef':
            if self.sub is not None: child_list.append(("subscript", self.sub))
        elif self.refType == 'StructRef':
            if self.field is not None: child_list.append(("field", self.field))
        return tuple(child_list)

class ArrayRef(Node):
    def __init__(self, name, subscript):
        self.name = name
        self.subscript = subscript

    def children(self):
        child_list = []
        if self.name is not None: child_list.append(("name", self.name))
        if self.subscript is not None: child_list.append(("subscript", self.subscript))
        return tuple(child_list)

class StructRef(Node):
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def children(self):
        child_list = []
        if self.name is not None: child_list.append(("name", self.name))
        if self.field is not None: child_list.append(("field", self.field))
        return tuple(child_list)
    
class DeclListNode(Node):
    def __init__(self, **kwargs):
        self.decls = kwargs['decls']

    def children(self):
        child_list = []
        for i, child in enumerate(self.decls or []):
            child_list.append(("decls[%d]" % i, child))
        return tuple(child_list)
    
class DeclInitListNode(Node):
    def __init__(self, **kwargs):
        self.decls = kwargs['decls']
        self.init = kwargs['init']

    def children(self):
        child_list = []
        for i, child in enumerate(self.decls or []):
            child_list.append(("decls[%d]" % i, child))
        if self.init is not None: child_list.append(("init", self.init))
        return tuple(child_list)



class This(Node):
    def __init__(self):
        pass

    def children(self):
        return tuple([])

class Template(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.params = kwargs['params']

    def children(self):
        child_list = []
        if self.name is not None: child_list.append(("name", self.name))
        if self.params is not None: child_list.append(("params", self.params))
        return tuple(child_list)

class Friend(Node):
    def __init__(self, **kwargs):
        self.decl = kwargs['decl']

    def children(self):
        child_list = []
        if self.decl is not None: child_list.append(("decl", self.decl))
        return tuple(child_list)

class Build_in_function(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.type = kwargs['type']

    def children(self):
        return tuple([])


class DeclPointer(Node):
    def __init__(self, **kwargs):
        self.quals = kwargs['quals']
        self.type=None

    def children(self):
        return tuple([])
    


class DeclFunction(Node):
    def __init__(self, **kwargs):
        self.args = kwargs['args']
        self.type = None

    def children(self):
        child_list = []
        if self.args is not None: child_list.append(("args", self.args))
        return tuple(child_list)

class DeclArray(Node):
    def __init__(self, **kwargs):
        self.dim = kwargs['dim']
        self.type = None

    def children(self):
        childrenList = []
        if self.dim is not None: childrenList.append(("dim", self.dim))
        return tuple(childrenList)



class Decl(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.quals = kwargs['quals']
        self.spec = kwargs['spec']
        self.type = kwargs['type']
        self.init = kwargs['init']

    def children(self):
        child_list = []
        if self.type is not None: child_list.append(("type", self.type))
        if self.init is not None: child_list.append(("init", self.init))
        return tuple(child_list)
    

    
class EmptyNode(Node):
    def __init__(self):
        pass
    
    def children(self):
        return tuple([])
    



class TypeNode(Node):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.quals = kwargs['quals']
        self.spec = kwargs['spec']
        self.type = kwargs['type']
        self.init = kwargs['init']

    def children(self):
        child_list = []
        if self.type is not None: child_list.append(("type", self.type))
        if self.init is not None: child_list.append(("init", self.init))
        return tuple(child_list)
    

