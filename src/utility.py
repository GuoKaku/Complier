from llvmlite import ir
import SynTree as SynTree

# LLVM tool_type_defined
int64 = ir.IntType(64)
int32 = ir.IntType(32)
int8 = ir.IntType(8)
int1 = ir.IntType(1)
unsigned_int32 = ir.IntType(32)
ir_void = ir.VoidType()
ir_float = ir.FloatType()
ir_double = ir.DoubleType()
ir_func = ir.FunctionType

# 
# def c2i(s):
#     if s == "'\\n'" or s == "'\\r\\n'":
#         return 10
#     return ord(s[1:-1])

def handle_decl_change(to_be_changed, changer):
    changer_head = changer
    changer_tail = changer

    while changer_tail.type:
        changer_tail = changer_tail.type

    if isinstance(to_be_changed, SynTree.Identifier):
        changer_tail.type = to_be_changed
        return changer
    else:
        res = to_be_changed

        while not isinstance(res.type, SynTree.Identifier):
            res = res.type

        changer_tail.type = res.type
        res.type = changer_head
        return to_be_changed

