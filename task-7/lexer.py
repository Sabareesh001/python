"""
Lexer (Tokenizer) for mini language.
Converts source code into tokens.
"""

from enum import Enum, auto
from typing import List, Optional, NamedTuple
import re


class TokenType(Enum):
    """Token types for the mini language."""
    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    IDENT = auto()
    
    # Keywords
    FN = auto()
    LET = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    PRINT = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    
    # Comparison
    EQ = auto()        # ==
    NEQ = auto()       # !=
    LT = auto()        # <
    LTE = auto()       # <=
    GT = auto()        # >
    GTE = auto()       # >=
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    ARROW = auto()    # ->
    
    # Special
    EOF = auto()
    NEWLINE = auto()


class Token(NamedTuple):
    """Represents a single token."""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.type.name}({self.value!r})"
        return self.type.name


class Lexer:
    """Tokenizes source code."""
    
    KEYWORDS = {
        'fn': TokenType.FN,
        'let': TokenType.LET,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source."""
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self.pos >= len(self.source):
                break
            
            char = self.source[self.pos]
            
            if char.isdigit():
                self._read_number()
            elif char.isalpha() or char == '_':
                self._read_identifier()
            elif char == '"':
                self._read_string()
            elif char == "'":
                self._read_string("'")
            else:
                self._read_operator_or_delimiter()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def _skip_whitespace_and_comments(self) -> None:
        """Skip whitespace and comments."""
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if char == ' ' or char == '\t':
                self._advance()
            elif char == '\n':
                self._advance()
                self.line += 1
                self.column = 1
            elif char == '#':
                # Skip comment until end of line
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self._advance()
            else:
                break
    
    def _read_number(self) -> None:
        """Read integer or float literal."""
        start_pos = self.pos
        start_col = self.column
        
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self._advance()
        
        # Check for float
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            self._advance()
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self._advance()
            
            value = float(self.source[start_pos:self.pos])
            self.tokens.append(Token(TokenType.FLOAT, value, self.line, start_col))
        else:
            value = int(self.source[start_pos:self.pos])
            self.tokens.append(Token(TokenType.INT, value, self.line, start_col))
    
    def _read_identifier(self) -> None:
        """Read identifier or keyword."""
        start_pos = self.pos
        start_col = self.column
        
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()
        
        value = self.source[start_pos:self.pos]
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(value, TokenType.IDENT)
        self.tokens.append(Token(token_type, value, self.line, start_col))
    
    def _read_string(self, quote: str = '"') -> None:
        """Read string literal."""
        start_col = self.column
        self._advance()  # Skip opening quote
        
        value = ""
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == '\\':
                self._advance()
                if self.pos < len(self.source):
                    escape_char = self.source[self.pos]
                    if escape_char == 'n':
                        value += '\n'
                    elif escape_char == 't':
                        value += '\t'
                    elif escape_char == '\\':
                        value += '\\'
                    else:
                        value += escape_char
                    self._advance()
            else:
                value += self.source[self.pos]
                self._advance()
        
        if self.pos < len(self.source):
            self._advance()  # Skip closing quote
        
        self.tokens.append(Token(TokenType.STRING, value, self.line, start_col))
    
    def _read_operator_or_delimiter(self) -> None:
        """Read operators and delimiters."""
        start_col = self.column
        char = self.source[self.pos]
        
        # Two-character operators
        if self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos + 2]
            
            if two_char == '==':
                self.tokens.append(Token(TokenType.EQ, '==', self.line, start_col))
                self._advance()
                self._advance()
                return
            elif two_char == '!=':
                self.tokens.append(Token(TokenType.NEQ, '!=', self.line, start_col))
                self._advance()
                self._advance()
                return
            elif two_char == '<=':
                self.tokens.append(Token(TokenType.LTE, '<=', self.line, start_col))
                self._advance()
                self._advance()
                return
            elif two_char == '>=':
                self.tokens.append(Token(TokenType.GTE, '>=', self.line, start_col))
                self._advance()
                self._advance()
                return
            elif two_char == '->':
                self.tokens.append(Token(TokenType.ARROW, '->', self.line, start_col))
                self._advance()
                self._advance()
                return
        
        # Single-character operators and delimiters
        token_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '=': TokenType.ASSIGN,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
        }
        
        if char in token_map:
            self.tokens.append(Token(token_map[char], char, self.line, start_col))
            self._advance()
        else:
            raise SyntaxError(f"Unexpected character: {char} at line {self.line}, column {self.column}")
    
    def _advance(self) -> None:
        """Move to next character."""
        self.pos += 1
        self.column += 1
