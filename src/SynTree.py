

class BaseNode(object):

    def child(self):
        pass

    def generate_syntree(self):
        tree=dict()
        tree['name'] = self.__class__.__name__
        tree['child'] = list()
        for (_, child) in self.child():
             tree['child']+=[child.generate_syntree()]

        return tree


class FirstNode(BaseNode):
    def __init__(self, nodes):
        self.nodes = nodes

    def child(self):
        children = list()
        for id, u in enumerate(self.nodes or list()):
            children+=[("note[%d]" % id, u)]
        return tuple(children)





class Id(BaseNode):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'default_id')
        self.spec = kwargs.get('spec', 'default_specifivation')

    def child(self):
        return tuple(list())

class Struct(BaseNode):
    def __init__(self, name, args):
        self.args = args
        self.name = name


    def child(self):
        children = list()
        for i, child in enumerate(self.args or list()):
            children+=[("declarations[%d]" % i, child)]
        return tuple(children)
    
    
class Constant(BaseNode):
    def __init__(self, kind, content):
        self.kind = kind
        self.content = content

    def child(self):
        return tuple(list())
    
    
class EmptyNode(BaseNode):
    def __init__(self):
        pass
    
    def child(self):
        return tuple(list())

class Blocks(BaseNode):
    def __init__(self, blocks):
        self.blocks = blocks

    def child(self):
        children = list()
        for i, child in enumerate(self.blocks or list()):
            children+=[("blocks[%d]" % i, child)]
        return tuple(children)
    
class CommentNode(BaseNode):
    def __init__(self, content):
        self.content = content
        
    def child(self):
        return tuple(list())

class FuncDef(BaseNode):
    def __init__(self, **kwargs):
        self.decl = kwargs.get('decl', 'default_decler')
        self.param_args = kwargs.get('param_args')
        self.body = kwargs.get('body')

    def child(self):
        children = list()
        if self.decl  : children+=[("decl", self.decl)]
        if self.body  : children+=[("body", self.body)]
        for i, child in enumerate(self.param_args or list()):
            children+=[("params[%d]" % i, child)]
        return tuple(children)

class EmptyStatement(BaseNode):
    def __init__(self):
        pass
    
    def child(self):
        return tuple(list())
    
class FunctionCall(BaseNode):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'default_id')
        self.args = kwargs.get('args')

    def child(self):
        children = list()
        if self.name  : children+=[("name", self.name)]
        if self.args  : children+=[("args", self.args)]
        return tuple(children)


class ControlLogic(BaseNode):
    def __init__(self,logicType,**kwargs):

        self.logicType=logicType
        if logicType=='If':
            self.judge = kwargs.get('judge')
            self.action1 = kwargs.get('action1')
            self.action2 = kwargs.get('action2')
        elif logicType == 'Return':
            self.return_result = kwargs.get('return_result')
        elif logicType == 'While':
            self.judge = kwargs.get('judge')
            self.action = kwargs.get('action')
        elif logicType == 'For':
            self.first = kwargs.get('first')
            self.judge = kwargs.get('judge')
            self.action = kwargs.get('action')  
            self.statement = kwargs.get('statement')      
        else:
            pass

    def child(self):
        children = list()
        if self.logicType == 'If':
            if self.judge  : children+=[("condition", self.judge)]
            if self.action1  : children+=[("true_do", self.action1)]
            if self.action2  : children+=[("false_do", self.action2)]
        elif self.logicType == 'While':
            if self.judge  : children+=[("condition", self.judge)]
            if self.action  : children+=[("statement", self.action)]
        elif self.logicType == 'For':
            if self.first  : children+=[("first", self.first)]         
            if self.judge  : children+=[("condition", self.judge)]
            if self.action : children+=[("statement", self.action)]
        elif self.logicType == 'Return':
            if self.return_result : children+=[("return_result", self.return_result)]
        elif self.logicType in ['Continue','Break','EmptyStatement']:
            return ()

        return tuple(children)

class ContentList(BaseNode):
    def __init__(self,listType,elements):
        self.listType=listType # InitList,ParamList,ExprList
        self.elements=elements

    def child(self):
        children = list()
        prefix_str=''
        if self.listType == 'Init':
            prefix_str='expressions'
        elif self.listType == 'Param':
            prefix_str='parameters'
        elif self.listType == 'Expression':
            prefix_str='expressions'
        for i, son in enumerate(self.elements or list()):
            children+=[(prefix_str+"[%d]" % i, son)]
        return tuple(children)

class InlineNode(BaseNode):
    def __init__(self, **kwargs):
        self.content = kwargs.get('content')

    def child(self):
        children = list()
        if self.content  : children+=[("content", self.content)]
        return tuple(list())
    
class Operation(BaseNode):

    def __init__(self, OperationType, OperationName,**kwargs):
        self.OperationType = OperationType  # Binary,Unary,Ternary
        self.OperationName = OperationName
        if OperationType == 'BinaryOp':
            self.left = kwargs.get('left')
            self.right = kwargs.get('right')
        elif OperationType == 'UnaryOp':
            self.expression = kwargs.get('expression')
        elif OperationType == 'Assignment':
            self.left = kwargs.get('left')
            self.right = kwargs.get('right')
        elif OperationType == 'TernaryOp':
            self.condition = kwargs.get('condition')
            self.true = kwargs.get('true')
            self.false = kwargs.get('false')

    def child(self):
        children = list()
        if self.OperationType == 'BinaryOp':
            if self.left : children+=[("left", self.left)]
            if self.right : children+=[("right", self.right)]
        elif self.OperationType == 'UnaryOp':
            if self.expression : children+=[("expression", self.expression)]
        elif self.OperationType == 'Assignment':
            if self.left : children+=[("left", self.left)]
            if self.right : children+=[("right", self.right)]
        elif self.OperationType == 'TernaryOp':
            if self.condition :  children+=[('condition',self.condition)]
            if self.true : children+=[('true',self.true)]
            if self.false : children+=[('false',self.false)]
            
        return tuple(children)
    
class InitListNode(BaseNode):
    def __init__(self, **kwargs):
        self.exprs = kwargs.get('exprs')

    def child(self):
        children = list()
        for i, child in enumerate(self.exprs or list()):
            children+=[("exprs[%d]" % i, child)]
        return tuple(children)
    

class Ref(BaseNode):
    """
    ArrayRef,StructRef
    """
    def __init__(self, refType,name, **kwargs):
        self.name=name
        self.refType=refType
        if refType=='ArrayRef':
            self.sub = kwargs.get('subscript')
        elif refType == 'StructRef':
            self.type = kwargs.get('type')
            self.reign = kwargs.get('reign')
            self.attr_names = ('type',)

    def child(self):
        children = list()
        if self.name  : children+=[("name", self.name)]
        if self.refType == 'ArrayRef':
            if self.sub  : children+=[("subscript", self.sub)]
        elif self.refType == 'StructRef':
            if self.reign  : children+=[("reign", self.reign)]
        return tuple(children)

class ArrayRef(BaseNode):
    def __init__(self, name, subscript):
        self.name = name
        self.subscript = subscript

    def child(self):
        children = list()
        if self.name  : children+=[("name", self.name)]
        if self.subscript  : children+=[("subscript", self.subscript)]
        return tuple(children)

class StructRef(BaseNode):
    def __init__(self, name, reign):
        self.reign = reign
        self.name = name


    def child(self):
        children = list()
        if self.name  : children+=[("name", self.name)]
        if self.reign  : children+=[("reign", self.reign)]
        return tuple(children)
    
class DeclListNode(BaseNode):
    def __init__(self, **kwargs):
        self.args = kwargs.get('args')

    def child(self):
        children = list()
        for i, child in enumerate(self.args or list()):
            children+=[("args[%d]" % i, child)]
        return tuple(children)
    
class DeclInitListNode(BaseNode):
    def __init__(self, **kwargs):
        self.args = kwargs.get('args')
        self.init = kwargs.get('init')

    def child(self):
        children = list()
        for i, child in enumerate(self.args or list()):
            children+=[("args[%d]" % i, child)]
        if self.init  : children+=[("init", self.init)]
        return tuple(children)



class This(BaseNode):
    def __init__(self):
        pass

    def child(self):
        return tuple(list())

class Template(BaseNode):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'default_id')
        self.params = kwargs.get('params')

    def child(self):
        children = list()
        if self.name  : children+=[("name", self.name)]
        if self.params  : children+=[("params", self.params)]
        return tuple(children)

class DeclFunction(BaseNode):
    def __init__(self, **kwargs):
        self.args = kwargs.get('args')
        self.type = None

    def child(self):
        children = list()
        if self.args  : children+=[("args", self.args)]
        return tuple(children)



class Build_in_function(BaseNode):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'default_id')
        self.type = kwargs.get('type')

    def child(self):
        return tuple(list())


class DeclPointer(BaseNode):
    def __init__(self, **kwargs):
        self.quals = kwargs.get('quals')
        self.type=None

    def child(self):
        return tuple(list())
    




class DeclArray(BaseNode):
    def __init__(self, **kwargs):
        self.dim = kwargs.get('dim')
        self.type = None

    def child(self):
        childList = list()
        if self.dim  : childList+=[("dim", self.dim)]
        return tuple(childList)
    
class TypeNode(BaseNode):
    def __init__(self, **kwargs):
        self.spec = kwargs.get('spec', 'default_specifivation')
        self.type = kwargs.get('type')
        self.quals = kwargs.get('quals')
        self.init = kwargs.get('init')
        self.name = kwargs.get('name', 'default_id')


    def child(self):
        children = list()
        if self.type  : children+=[("type", self.type)]
        if self.init  : children+=[("init", self.init)]
        return tuple(children)



class Decl(BaseNode):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'default_id')
        self.quals = kwargs.get('quals')
        self.spec = kwargs.get('spec', 'default_specifivation')
        self.type = kwargs.get('type')
        self.init = kwargs.get('init')

    def child(self):
        children = list()
        if self.type  : children+=[("type", self.type)]
        if self.init  : children+=[("init", self.init)]
        return tuple(children)
    

    

    
class Friend(BaseNode):
    def __init__(self, **kwargs):
        self.decl = kwargs.get('decl', 'default_decler')

    def child(self):
        children = list()
        if self.decl  : children+=[("decl", self.decl)]
        return tuple(children)




    

