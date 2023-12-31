from typing import Optional
from enum import Enum, auto

from .parser import (
    Program,
    ExpressionStatement,
    BlockStatement,
    LetStatement,
    ReturnStatement,
    ForStatement,
    PrefixExpression,
    InfixExpression,
    CallExpression,
    IndexExpression,
    IfExpression,
    IntegerLiteral,
    StringLiteral,
    FunctionLiteral,
    ListLiteral,
    Boolean,
    Identifier,
)


class Environment:
    def __init__(self, trace_eval=False):
        self.store = {}
        self.builtin = {
            "len": BuiltinObject(builtin_len),
            "first": BuiltinObject(builtin_first),
            "last": BuiltinObject(builtin_last),
            "rest": BuiltinObject(builtin_rest),
            "push": BuiltinObject(builtin_push),
            "puts": BuiltinObject(builtin_puts),
        }
        self.outer: Optional[Environment] = None
        self.trace_eval = trace_eval

    def get(self, identifier):
        value = self.store.get(identifier, None)
        if value is None and self.outer is not None:
            return self.outer.get(identifier)
        return value

    def set(self, identifier, value):
        self.store[identifier] = value

    def unset(self, identifier):
        if identifier in self.store:
            del self.store[identifier]

    def __str__(self):
        items = []
        for k, v in self.store.items():
            if v.otype == ObjectType.FUNCTION:
                v = v.compact_str()
            items.append(f"{k}: {v}")
        if self.outer is not None:
            outer_items = []
            for k, v in self.outer.store.items():
                if v.otype == ObjectType.FUNCTION:
                    v = v.compact_str()
                outer_items.append(f"{k}: {v}")
            return f"{{{', '.join(items)}}} outer: {{{', '.join(outer_items)}}}"
        return f"{{{', '.join(items)}}}"


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    RETURN_VALUE = auto()
    FUNCTION = auto()
    BUILTIN = auto()
    LIST = auto()
    STRING = auto()
    ERROR = auto()
    NULL = auto()


class Object:
    def __init__(self, type):
        self.otype: ObjectType = type
        self.value: Optional[int|bool]


class IntegerObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.INTEGER)
        self.value: int = value

    def __str__(self) -> str:
        return f'{self.value}'


class BooleanObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.BOOLEAN)
        self.value = value

    def __str__(self) -> str:
        return str(self.value).lower()


class StringObject(Object):
    def __init__(self, value: str):
        super().__init__(ObjectType.STRING)
        self.value: str = value

    def __str__(self) -> str:
        return str(self.value).lower()


class ReturnObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.RETURN_VALUE)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class FunctionObject(Object):
    def __init__(self, parameters, body, env):
        super().__init__(ObjectType.FUNCTION)
        self.parameters = parameters
        self.body = body
        self.env = env

    def __str__(self) -> str:
        params = ', '.join([str(p) for p in self.parameters])
        return f"func({params}) {{\n{self.body}\n}}"
    
    def compact_str(self):
        params = ', '.join([str(p) for p in self.parameters])
        return f"func({params})"


class BuiltinObject(Object):
    def __init__(self, fn):
        super().__init__(ObjectType.BUILTIN)
        self.fn = fn

    def __str__(self) -> str:
        return f"builtin function"


class ListObject(Object):
    def __init__(self, elements):
        super().__init__(ObjectType.LIST)
        self.elements = elements

    def get_index(self, idx):
        if idx.value < 0 or idx.value >= len(self.elements):
            return new_error("Index %d out of bounds for collection of len %d", idx.value, len(self.elements))
        return self.elements[idx.value]

    def __str__(self) -> str:
        elements = ', '.join([str(e) for e in self.elements])
        return f"[{elements}]"


class ErrorObject(Object):
    def __init__(self, msg):
        super().__init__(ObjectType.ERROR)
        self.msg = msg

    def __str__(self) -> str:
        return f"ERROR: {self.msg}"


class NullObject(Object):
    def __init__(self):
        super().__init__(ObjectType.NULL)

    def __str__(self) -> str:
        return "null"


NULL = NullObject()
TRUE = BooleanObject(True)
FALSE = BooleanObject(False)


def eval(node, env: Environment):
    if env.trace_eval:
        print("evaluating:", type(node), node.token, "env:", env)
    if isinstance(node, Program):
        return eval_program(node, env)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression, env)
    if isinstance(node, BlockStatement):
        return eval_block_statement(node, env)
    if isinstance(node, ReturnStatement):
        value = eval(node.return_value, env)
        if is_error(value):
            return value
        return ReturnObject(value)
    if isinstance(node, ForStatement):
        return eval_for_statement(node, env)
    if isinstance(node, LetStatement):
        value = eval(node.value, env)
        if is_error(value):
            return value
        env.set(node.name.value, value)
    if isinstance(node, PrefixExpression):
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left, env)
        if is_error(left):
            return left
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    if isinstance(node, IfExpression):
        return eval_if_expression(node, env)
    if isinstance(node, IntegerLiteral):
        return IntegerObject(node.value)
    if isinstance(node, StringLiteral):
        return StringObject(node.value)
    if isinstance(node, Boolean):
        return native_bool_to_boolean_object(node.value)
    if isinstance(node, Identifier):
        value = env.get(node.value)
        if value is not None:
            return value
        value = env.builtin.get(node.value, None)
        if value is not None:
            return value
        return new_error("identifier not found: %s", node.value)
    if isinstance(node, FunctionLiteral):
        params = node.parameters
        body = node.body
        return FunctionObject(params, body, env)
    if isinstance(node, ListLiteral):
        elements = eval_expressions(node.elements, env)
        if len(elements) == 1 and isinstance(elements[0], ErrorObject):
            return elements[0]
        return ListObject(elements)
    if isinstance(node, CallExpression):
        function = eval(node.function, env)
        if is_error(function):
            return function
        args = eval_expressions(node.arguments, env)
        if is_error(args):
            return args
        return apply_function(function, args)
    if isinstance(node, IndexExpression):
        collection = eval(node.collection, env)
        if is_error(collection):
            return collection
        idx = eval(node.idx, env)
        if is_error(idx):
            return idx
        return eval_index_expression(collection, idx)
    return None


def eval_program(program, env):
    result = None
    for stmt in program.statements:
        result = eval(stmt, env)
        if isinstance(result, ReturnObject):
            return result.value
        if isinstance(result, ErrorObject):
            return result
    return result


def eval_block_statement(block, env):
    result = None
    for stmt in block.statements:
        result = eval(stmt, env)
        if result is not None:
            if isinstance(result, ReturnObject) or isinstance(result, ErrorObject):
                return result
    return result


def eval_for_statement(stmt: ForStatement, env):
    initial_value = eval(stmt.initial_value, env)
    if is_error(initial_value):
        return initial_value
    env.set(stmt.counter.value, initial_value)
    condition = eval(stmt.condition, env)
    if is_error(condition):
        return condition
    while is_truthy(eval(stmt.condition, env)):
        evaluated = eval_block_statement(stmt.body, env)
        if is_error(evaluated):
            return evaluated
        eval(stmt.update_rule, env)


def eval_expressions(expressions, env):
    result = []
    for expr in expressions:
        evaluated = eval(expr, env)
        if is_error(evaluated):
            return evaluated
        result.append(evaluated)
    return result


def apply_function(function, args):
    if isinstance(function, BuiltinObject):
        return function.fn(*args)
    if isinstance(function, FunctionObject):
        if len(args) != len(function.parameters):
            return new_error("function requires %d parameters, got %d", len(function.parameters), len(args))
        extended_env = extend_function_env(function, args)
        evaluated = eval(function.body, extended_env)
        return unwrap_return_value(evaluated)
    return new_error("not a function: %s", get_type_name(function))


def extend_function_env(function, args):
    env = new_enclosed_environment(function.env)
    for i, param in enumerate(function.parameters):
        env.set(param.value, args[i])
    return env


def unwrap_return_value(obj):
    if isinstance(obj, ReturnObject):
        return obj.value
    return obj


def new_enclosed_environment(outer: Environment):
    env = Environment(outer.trace_eval)
    env.outer = outer
    return env


def eval_index_expression(collection, idx):
    if isinstance(collection, ListObject) and isinstance(idx, IntegerObject):
        return collection.get_index(idx)
    return new_error("Exprected collection for indexing, got ObjectType.INTEGER")


def eval_prefix_expression(operator, right):
    match operator:
        case '!':
            return eval_not_operator_expression(right)
        case '-':
            return eval_minus_prefix_operator_expression(right)
        case _:
            return new_error('unknown operator: %s%s', operator, get_type_name(right))


def eval_infix_expression(operator, left, right):
    if isinstance(left, IntegerObject) and isinstance(right, IntegerObject):
        return eval_integer_infix_expression(operator, left, right)
    if isinstance(left, StringObject) and isinstance(right, StringObject):
        if operator != '+':
            return new_error('unknown operator: STRING %s STRING', operator)
        return StringObject(left.value + right.value)
    match operator:
        case '<':
            return native_bool_to_boolean_object(left.value < right.value)
        case '>':
            return native_bool_to_boolean_object(left.value > right.value)
        case '<=':
            return native_bool_to_boolean_object(left.value <= right.value)
        case '>=':
            return native_bool_to_boolean_object(int(left.value >= right.value))
        case '==':
            return native_bool_to_boolean_object(left.value == right.value)
        case '!=':
            return native_bool_to_boolean_object(int(left.value != right.value))
    if type(left) != type(right):
        return new_error('type mismatch: %s %s %s', get_type_name(left), operator, get_type_name(right))
    return new_error('unknown operator: %s %s %s', get_type_name(left), operator, get_type_name(right))


def eval_integer_infix_expression(operator, left, right):
    match operator:
        case '+':
            return IntegerObject(left.value + right.value)
        case '-':
            return IntegerObject(left.value - right.value)
        case '*':
            return IntegerObject(left.value * right.value)
        case '/':
            return IntegerObject(int(left.value / right.value))
        case '<':
            return native_bool_to_boolean_object(left.value < right.value)
        case '>':
            return native_bool_to_boolean_object(left.value > right.value)
        case '<=':
            return native_bool_to_boolean_object(left.value <= right.value)
        case '>=':
            return native_bool_to_boolean_object(int(left.value >= right.value))
        case '==':
            return native_bool_to_boolean_object(left.value == right.value)
        case '!=':
            return native_bool_to_boolean_object(int(left.value != right.value))
    return new_error('unknown operator: %s %s %s', get_type_name(left), operator, get_type_name(right))


def native_bool_to_boolean_object(value):
    if value:
        return TRUE
    return FALSE


def eval_not_operator_expression(right):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE


def eval_minus_prefix_operator_expression(right):
    if not isinstance(right, IntegerObject):
        return new_error('unknown operator: -%s', get_type_name(right))
    if right.value is None:
        return new_error('integer value is null in: -%s', get_type_name(right))
    return IntegerObject(-right.value)


def eval_if_expression(node, env):
    condition = eval(node.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return eval(node.consequence, env)
    elif node.alternative is not None:
        return eval(node.alternative, env)
    else:
        return NULL


def is_truthy(node):
    if node == NULL:
        return False
    if node == TRUE:
        return True
    if node == FALSE:
        return False
    return True


def new_error(format_string, *params):
    return ErrorObject(format_string % params)


def is_error(obj):
    if obj is not None:
        return isinstance(obj, ErrorObject)
    return False


def get_type_name(expr):
    try:
        return expr.otype.name
    except AttributeError:
        return None


def builtin_len(*args):
    if len(args) != 1:
        return ErrorObject('Builtin function len expected one argument')
    if isinstance(args[0], StringObject):
        return IntegerObject(len(args[0].value))
    if isinstance(args[0], ListObject):
        return IntegerObject(len(args[0].elements))
    return ErrorObject('Builtin function len expected type String or List')


def builtin_first(*args):
    if len(args) != 1:
        return ErrorObject('Builtin function first expected one argument')
    if isinstance(args[0], ListObject):
        if len(args[0].elements) < 1:
            return ErrorObject('List is empty')
        return args[0].elements[0]
    return ErrorObject('Builtin function first expected type List')


def builtin_last(*args):
    if len(args) != 1:
        return ErrorObject('Builtin function last expected one argument')
    if isinstance(args[0], ListObject):
        if len(args[0].elements) < 1:
            return ErrorObject('List is empty')
        return args[0].elements[-1]
    return ErrorObject('Builtin function last expected type List')


def builtin_rest(*args):
    if len(args) != 1:
        return ErrorObject('Builtin function rest expected one argument')
    if isinstance(args[0], ListObject):
        if len(args[0].elements) <= 1:
            return ListObject([])
        return ListObject(args[0].elements[1:])
    return ErrorObject('Builtin function rest expected type List')


def builtin_push(*args):
    if len(args) != 2:
        return ErrorObject('Builtin function push expected two arguments')
    value, lst = args
    if isinstance(lst, ListObject):
        lst.elements.append(value)
        return lst
    return ErrorObject('Builtin function push expected first argument of type List')


def builtin_puts(*args):
    for arg in args:
        print(str(arg))

