"""
AST (Abstract Syntax Tree) node definitions.
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field


# Base AST Node
@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0


# Expressions
@dataclass
class Literal(ASTNode):
    """Literal value (int, float, string, bool)."""
    value: Any = None
    
    def __repr__(self) -> str:
        return f"Literal({self.value!r})"


@dataclass
class Identifier(ASTNode):
    """Variable or function name."""
    name: str = ""
    
    def __repr__(self) -> str:
        return f"Ident({self.name!r})"


@dataclass
class BinaryOp(ASTNode):
    """Binary operation (a + b, a < b, etc)."""
    left: 'ASTNode' = None
    op: str = ""
    right: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"BinOp({self.left!r} {self.op} {self.right!r})"


@dataclass
class UnaryOp(ASTNode):
    """Unary operation (-a, not a, etc)."""
    op: str = ""
    operand: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"UnaryOp({self.op} {self.operand!r})"


@dataclass
class Call(ASTNode):
    """Function call."""
    func: 'ASTNode' = None
    args: List['ASTNode'] = field(default_factory=list)
    
    def __repr__(self) -> str:
        args_str = ", ".join(repr(arg) for arg in self.args)
        return f"Call({self.func!r}({args_str}))"


@dataclass
class Index(ASTNode):
    """Array/list indexing."""
    expr: 'ASTNode' = None
    index: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"Index({self.expr!r}[{self.index!r}])"


@dataclass
class ListLiteral(ASTNode):
    """List literal [1, 2, 3]."""
    elements: List['ASTNode'] = field(default_factory=list)
    
    def __repr__(self) -> str:
        elements_str = ", ".join(repr(e) for e in self.elements)
        return f"List([{elements_str}])"


# Statements
@dataclass
class VarDecl(ASTNode):
    """Variable declaration."""
    name: str = ""
    expr: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"VarDecl({self.name!r} = {self.expr!r})"


@dataclass
class Assignment(ASTNode):
    """Variable assignment."""
    target: str = ""
    expr: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"Assign({self.target!r} = {self.expr!r})"


@dataclass
class Block(ASTNode):
    """Block of statements."""
    statements: List['ASTNode'] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"Block({len(self.statements)} stmts)"


@dataclass
class IfStatement(ASTNode):
    """If/else statement."""
    condition: 'ASTNode' = None
    then_block: Block = None
    else_block: Optional[Block] = None
    
    def __repr__(self) -> str:
        return f"If({self.condition!r})"


@dataclass
class WhileStatement(ASTNode):
    """While loop."""
    condition: 'ASTNode' = None
    body: Block = None
    
    def __repr__(self) -> str:
        return f"While({self.condition!r})"


@dataclass
class ForStatement(ASTNode):
    """For loop."""
    var: str = ""
    iterable: 'ASTNode' = None
    body: Block = None
    
    def __repr__(self) -> str:
        return f"For({self.var!r} in {self.iterable!r})"


@dataclass
class FunctionDecl(ASTNode):
    """Function declaration."""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: Block = None
    
    def __repr__(self) -> str:
        return f"Func({self.name!r}({', '.join(self.params)}))"


@dataclass
class ReturnStatement(ASTNode):
    """Return statement."""
    expr: Optional['ASTNode'] = None
    
    def __repr__(self) -> str:
        return f"Return({self.expr!r})" if self.expr else "Return"


@dataclass
class PrintStatement(ASTNode):
    """Print statement."""
    expr: 'ASTNode' = None
    
    def __repr__(self) -> str:
        return f"Print({self.expr!r})"


@dataclass
class Program(ASTNode):
    """Root node - entire program."""
    statements: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"Program({len(self.statements)} stmts)"
