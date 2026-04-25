"""
Interpreter for mini language.
Walks the AST and executes the program.
"""

from typing import Any, Dict, Optional, List, Callable
from ast_nodes import *
import sys


class ReturnValue(Exception):
    """Exception used for return statements."""
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Exception used for break statements."""
    pass


class ContinueException(Exception):
    """Exception used for continue statements."""
    pass


class Function:
    """User-defined function."""
    def __init__(self, name: str, params: List[str], body: Block, closure: 'Environment'):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
    
    def __repr__(self) -> str:
        return f"<function {self.name}({', '.join(self.params)})>"


class Environment:
    """Scope for variables."""
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any) -> None:
        """Define variable in this scope."""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get variable value."""
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise NameError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: Any) -> None:
        """Set variable value."""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            # Define in current scope if not found
            self.variables[name] = value


class Interpreter:
    """Interpreter for mini language."""
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self._setup_builtins()
    
    def _setup_builtins(self) -> None:
        """Add built-in functions."""
        self.global_env.define('len', lambda x: len(x))
        self.global_env.define('range', lambda *args: list(range(*args)))
        self.global_env.define('str', lambda x: str(x))
        self.global_env.define('int', lambda x: int(x))
        self.global_env.define('float', lambda x: float(x))
        self.global_env.define('list', lambda *args: list(args))
    
    def interpret(self, program: Program) -> None:
        """Interpret an entire program."""
        for statement in program.statements:
            self._execute(statement)
    
    def _execute(self, node: ASTNode) -> Any:
        """Execute an AST node."""
        if isinstance(node, Program):
            for stmt in node.statements:
                self._execute(stmt)
        
        elif isinstance(node, Block):
            for stmt in node.statements:
                self._execute(stmt)
        
        elif isinstance(node, VarDecl):
            value = self._evaluate(node.expr)
            self.current_env.define(node.name, value)
        
        elif isinstance(node, Assignment):
            value = self._evaluate(node.expr)
            self.current_env.set(node.target, value)
        
        elif isinstance(node, FunctionDecl):
            func = Function(node.name, node.params, node.body, self.current_env)
            self.current_env.define(node.name, func)
        
        elif isinstance(node, IfStatement):
            condition = self._evaluate(node.condition)
            if self._is_truthy(condition):
                self._execute(node.then_block)
            elif node.else_block:
                self._execute(node.else_block)
        
        elif isinstance(node, WhileStatement):
            while self._is_truthy(self._evaluate(node.condition)):
                try:
                    self._execute(node.body)
                except ContinueException:
                    continue
                except BreakException:
                    break
        
        elif isinstance(node, ForStatement):
            iterable = self._evaluate(node.iterable)
            for value in iterable:
                self.current_env.set(node.var, value)
                try:
                    self._execute(node.body)
                except ContinueException:
                    continue
                except BreakException:
                    break
        
        elif isinstance(node, ReturnStatement):
            value = self._evaluate(node.expr) if node.expr else None
            raise ReturnValue(value)
        
        elif isinstance(node, PrintStatement):
            value = self._evaluate(node.expr)
            print(value)
        
        else:
            # Try to evaluate as expression
            self._evaluate(node)
    
    def _evaluate(self, node: ASTNode) -> Any:
        """Evaluate an expression."""
        if isinstance(node, Literal):
            return node.value
        
        elif isinstance(node, Identifier):
            return self.current_env.get(node.name)
        
        elif isinstance(node, ListLiteral):
            return [self._evaluate(e) for e in node.elements]
        
        elif isinstance(node, BinaryOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            elif node.op == '%':
                return left % right
            elif node.op == '==':
                return left == right
            elif node.op == '!=':
                return left != right
            elif node.op == '<':
                return left < right
            elif node.op == '<=':
                return left <= right
            elif node.op == '>':
                return left > right
            elif node.op == '>=':
                return left >= right
            elif node.op == 'and':
                return left and right
            elif node.op == 'or':
                return left or right
            else:
                raise RuntimeError(f"Unknown operator: {node.op}")
        
        elif isinstance(node, UnaryOp):
            operand = self._evaluate(node.operand)
            
            if node.op == '-':
                return -operand
            elif node.op == 'not':
                return not operand
            else:
                raise RuntimeError(f"Unknown unary operator: {node.op}")
        
        elif isinstance(node, Call):
            func = self._evaluate(node.func)
            args = [self._evaluate(arg) for arg in node.args]
            
            if isinstance(func, Function):
                return self._call_function(func, args)
            elif callable(func):
                return func(*args)
            else:
                raise TypeError(f"Not callable: {func}")
        
        elif isinstance(node, Index):
            obj = self._evaluate(node.expr)
            index = self._evaluate(node.index)
            return obj[index]
        
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def _call_function(self, func: Function, args: List[Any]) -> Any:
        """Call a user-defined function."""
        if len(args) != len(func.params):
            raise TypeError(
                f"{func.name}() takes {len(func.params)} arguments but {len(args)} were given"
            )
        
        # Create new environment for function
        func_env = Environment(func.closure)
        
        # Bind parameters
        for param, arg in zip(func.params, args):
            func_env.define(param, arg)
        
        # Execute function body
        previous_env = self.current_env
        self.current_env = func_env
        
        try:
            self._execute(func.body)
            result = None
        except ReturnValue as ret:
            result = ret.value
        finally:
            self.current_env = previous_env
        
        return result
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine truthiness of a value."""
        if value is None or value is False:
            return False
        if value == 0 or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return False
        return True
