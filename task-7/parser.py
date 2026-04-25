"""
Parser for mini language.
Converts tokens to Abstract Syntax Tree using recursive descent parsing.
"""

from typing import List, Optional
from lexer import Token, TokenType, Lexer
from ast_nodes import *


class Parser:
    """Recursive descent parser for mini language."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        """Parse entire program."""
        statements = []
        
        while not self._is_at_end():
            if self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a statement."""
        # Function declaration
        if self._match(TokenType.FN):
            return self._parse_function_decl()
        
        # Variable declaration
        if self._match(TokenType.LET):
            return self._parse_var_decl()
        
        # If statement
        if self._match(TokenType.IF):
            return self._parse_if_statement()
        
        # While loop
        if self._match(TokenType.WHILE):
            return self._parse_while_statement()
        
        # For loop
        if self._match(TokenType.FOR):
            return self._parse_for_statement()
        
        # Return statement
        if self._match(TokenType.RETURN):
            return self._parse_return_statement()
        
        # Print statement
        if self._match(TokenType.PRINT):
            return self._parse_print_statement()
        
        # Expression or assignment
        return self._parse_expression_statement()
    
    def _parse_function_decl(self) -> FunctionDecl:
        """Parse function declaration."""
        name = self._consume(TokenType.IDENT, "Expected function name").value
        
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._consume(TokenType.IDENT, "Expected parameter name").value)
            while self._match(TokenType.COMMA):
                params.append(self._consume(TokenType.IDENT, "Expected parameter name").value)
        
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        body = self._parse_block()
        
        return FunctionDecl(name, params, body)
    
    def _parse_var_decl(self) -> VarDecl:
        """Parse variable declaration."""
        name = self._consume(TokenType.IDENT, "Expected variable name").value
        self._consume(TokenType.ASSIGN, "Expected '=' in variable declaration")
        expr = self._parse_expression()
        self._skip_terminators()
        
        return VarDecl(name, expr)
    
    def _parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        condition = self._parse_expression()
        
        then_block = self._parse_block()
        
        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self._parse_block()
        
        return IfStatement(condition, then_block, else_block)
    
    def _parse_while_statement(self) -> WhileStatement:
        """Parse while loop."""
        condition = self._parse_expression()
        body = self._parse_block()
        
        return WhileStatement(condition, body)
    
    def _parse_for_statement(self) -> ForStatement:
        """Parse for loop."""
        var = self._consume(TokenType.IDENT, "Expected variable name").value
        self._consume(TokenType.IN, "Expected 'in' in for loop")
        iterable = self._parse_expression()
        body = self._parse_block()
        
        return ForStatement(var, iterable, body)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        expr = None
        
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.NEWLINE) and not self._check(TokenType.RBRACE):
            expr = self._parse_expression()
        
        self._skip_terminators()
        return ReturnStatement(expr)
    
    def _parse_print_statement(self) -> PrintStatement:
        """Parse print statement."""
        self._consume(TokenType.LPAREN, "Expected '(' after 'print'")
        expr = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after print expression")
        self._skip_terminators()
        
        return PrintStatement(expr)
    
    def _parse_expression_statement(self) -> Optional[ASTNode]:
        """Parse expression as statement or assignment."""
        expr = self._parse_assignment()
        self._skip_terminators()
        return expr
    
    def _parse_assignment(self) -> ASTNode:
        """Parse assignment or expression."""
        expr = self._parse_logical_or()
        
        if self._check(TokenType.IDENT) and self._peek().type == TokenType.ASSIGN:
            # This was actually an assignment
            # Backtrack
            self.pos -= 1
            target = self._consume(TokenType.IDENT, "Expected identifier").value
            self._consume(TokenType.ASSIGN, "Expected '='")
            value = self._parse_assignment()
            return Assignment(target, value)
        
        return expr
    
    def _parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression."""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.OR):
            op = 'or'
            right = self._parse_logical_and()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def _parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression."""
        expr = self._parse_logical_not()
        
        while self._match(TokenType.AND):
            op = 'and'
            right = self._parse_logical_not()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def _parse_logical_not(self) -> ASTNode:
        """Parse logical NOT expression."""
        if self._match(TokenType.NOT):
            expr = self._parse_logical_not()
            return UnaryOp('not', expr)
        
        return self._parse_comparison()
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison expressions."""
        expr = self._parse_addition()
        
        while self._match(TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op = self._previous().value
            right = self._parse_addition()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def _parse_addition(self) -> ASTNode:
        """Parse addition and subtraction."""
        expr = self._parse_multiplication()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._parse_multiplication()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def _parse_multiplication(self) -> ASTNode:
        """Parse multiplication, division, and modulo."""
        expr = self._parse_unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous().value
            right = self._parse_unary()
            expr = BinaryOp(expr, op, right)
        
        return expr
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary expressions."""
        if self._match(TokenType.MINUS):
            expr = self._parse_unary()
            return UnaryOp('-', expr)
        
        return self._parse_postfix()
    
    def _parse_postfix(self) -> ASTNode:
        """Parse postfix expressions (function calls, indexing)."""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LPAREN):
                # Function call
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                expr = Call(expr, args)
            
            elif self._match(TokenType.LBRACKET):
                # Indexing
                index = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = Index(expr, index)
            
            else:
                break
        
        return expr
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expressions."""
        # Literals
        if self._match(TokenType.INT):
            return Literal(self._previous().value)
        
        if self._match(TokenType.FLOAT):
            return Literal(self._previous().value)
        
        if self._match(TokenType.STRING):
            return Literal(self._previous().value)
        
        if self._match(TokenType.TRUE):
            return Literal(True)
        
        if self._match(TokenType.FALSE):
            return Literal(False)
        
        # Identifier
        if self._match(TokenType.IDENT):
            return Identifier(self._previous().value)
        
        # List literal
        if self._match(TokenType.LBRACKET):
            elements = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    elements.append(self._parse_expression())
            
            self._consume(TokenType.RBRACKET, "Expected ']' after list elements")
            return ListLiteral(elements)
        
        # Grouped expression
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise SyntaxError(f"Unexpected token: {self._peek()}")
    
    def _parse_expression(self) -> ASTNode:
        """Parse any expression."""
        return self._parse_assignment()
    
    def _parse_block(self) -> Block:
        """Parse a block of statements."""
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RBRACE, "Expected '}'")
        
        return Block(statements)
    
    def _skip_terminators(self) -> None:
        """Skip statement terminators."""
        while self._match(TokenType.SEMICOLON, TokenType.NEWLINE):
            pass
    
    # Utility methods
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any type."""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of type."""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume and return current token."""
        if not self._is_at_end():
            self.pos += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if at end of tokens."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Get current token without consuming."""
        return self.tokens[self.pos]
    
    def _previous(self) -> Token:
        """Get previous token."""
        return self.tokens[self.pos - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of type or raise error."""
        if self._check(token_type):
            return self._advance()
        
        raise SyntaxError(f"{message} at {self._peek()}")
