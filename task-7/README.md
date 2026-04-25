# Compiler/Interpreter for Mini Language

A complete compiler and tree-walking interpreter for a mini programming language. Implements lexical analysis, recursive descent parsing, and AST-based execution.

## Architecture Overview

### Three-Stage Pipeline

```
Source Code → Lexer → Tokens → Parser → AST → Interpreter → Output
```

### Core Components

1. **Lexer** (`lexer.py`)
   - Tokenization (source → tokens)
   - Keyword recognition
   - String/number/identifier parsing
   - Line/column tracking

2. **AST Nodes** (`ast_nodes.py`)
   - Expression nodes (literals, binary ops, calls)
   - Statement nodes (declarations, control flow)
   - Program root node

3. **Parser** (`parser.py`)
   - Recursive descent parsing
   - Operator precedence
   - Statement/expression distinction
   - Error reporting

4. **Interpreter** (`interpreter.py`)
   - Tree-walking execution
   - Environment (scoping)
   - Function calls and closures
   - Built-in functions

## Language Features

### Variables

```python
let x = 10
let y = x + 5
let name = "Alice"
```

### Functions (with recursion)

```python
fn fibonacci(n) {
    if n <= 1 { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

let result = fibonacci(10)  # 55
```

### Operators

**Arithmetic:**

```python
2 + 3       # 5
10 - 4      # 6
3 * 4       # 12
20 / 4      # 5.0
17 % 5      # 2
```

**Comparison:**

```python
5 == 5      # true
5 != 3      # true
10 > 5      # true
10 >= 10    # true
```

**Logical:**

```python
true and false   # false
true or false    # true
not true         # false
```

### Control Flow

**If/Else:**

```python
let age = 25

if age < 18 {
    print("Minor")
} else {
    print("Adult")
}
```

**While Loop:**

```python
let i = 1
while i <= 5 {
    print(i)
    let i = i + 1
}
```

**For Loop:**

```python
let numbers = [1, 2, 3, 4, 5]
for num in numbers {
    print(num)
}
```

### Lists & Indexing

```python
let items = [10, 20, 30, 40]
print(items[0])      # 10
print(items[2])      # 30
let first = items[0]
```

### Built-in Functions

```python
len([1, 2, 3])           # 3
range(5)                 # [0, 1, 2, 3, 4]
str(42)                  # "42"
int("10")                # 10
list(1, 2, 3)            # [1, 2, 3]
```

## Implementation Details

### Lexer (Tokenization)

```python
lexer = Lexer("let x = 10 + 5")
tokens = lexer.tokenize()

# Output:
# [LET, IDENT("x"), ASSIGN, INT(10), PLUS, INT(5), EOF]
```

**Token Stream:**

- Each token has type, value, line, column
- Tracks position for error reporting
- Skips whitespace and comments

**Example Flow:**

```
Input:  "let x = 10"
Output: [
    Token(LET, "let", 1, 1),
    Token(IDENT, "x", 1, 5),
    Token(ASSIGN, "=", 1, 7),
    Token(INT, 10, 1, 9),
    Token(EOF, None, 1, 11)
]
```

### Parser (AST Construction)

**Recursive Descent Parsing:**

```python
parser = Parser(tokens)
ast = parser.parse()

# Builds tree structure:
# Program
# ├── VarDecl("x", Literal(10))
# ├── FunctionDecl("fibonacci", ...)
# └── PrintStatement(...)
```

**Operator Precedence (highest to lowest):**

1. Primary (literals, identifiers, calls)
2. Postfix (calls `()`, indexing `[]`)
3. Unary (`-`, `not`)
4. Multiplication (`*`, `/`, `%`)
5. Addition (`+`, `-`)
6. Comparison (`==`, `!=`, `<`, `<=`, `>`, `>=`)
7. Logical AND (`and`)
8. Logical OR (`or`)
9. Assignment (`=`)

**Parse Tree Example (fibonacci):**

```
FunctionDecl("fibonacci", ["n"])
├── IfStatement
│   ├── condition: BinaryOp(<=, Ident("n"), Literal(1))
│   └── then_block:
│       └── ReturnStatement(Ident("n"))
└── ReturnStatement(BinaryOp(+, Call(...), Call(...)))
```

### AST Nodes

**Expressions:**

- `Literal`: Values (int, float, string, bool)
- `Identifier`: Variable references
- `BinaryOp`: `+`, `-`, `*`, `/`, `==`, `<`, etc.
- `UnaryOp`: `-`, `not`
- `Call`: Function calls
- `Index`: List/array access
- `ListLiteral`: `[1, 2, 3]`

**Statements:**

- `VarDecl`: Variable declaration
- `Assignment`: Variable assignment
- `FunctionDecl`: Function definition
- `IfStatement`: Conditional execution
- `WhileStatement`: Loop
- `ForStatement`: Iteration
- `ReturnStatement`: Return from function
- `PrintStatement`: Output
- `Block`: Group of statements

### Interpreter (Execution)

**Environment (Scoping):**

```python
class Environment:
    def __init__(self, parent=None):
        self.parent = parent  # Lexical scope chain
        self.variables = {}   # Local variables

    def get(name):    # Look up variable
    def set(name, value):  # Update variable
    def define(name, value):  # Create variable
```

**Scoping Example:**

```python
let x = 10          # Global x

fn outer() {
    let x = 20      # Local x in outer
    fn inner() {
        print(x)    # References outer's x (closures)
    }
    inner()
}
```

**Function Calls:**

```python
# User-defined function
class Function:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure  # Captured environment
```

**Closure Example:**

```python
fn make_adder(x) {
    fn add(y) {
        return x + y
    }
    return add
}

let add5 = make_adder(5)
print(add5(3))  # 8
```

## Example Program: Fibonacci

```python
fn fibonacci(n) {
    if n <= 1 { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

let result = fibonacci(10)
print("Fibonacci(10) =")
print(result)
```

**Execution Flow:**

1. **Lexer** tokenizes source:

   ```
   FN, IDENT("fibonacci"), LPAREN, IDENT("n"), RPAREN, LBRACE, ...
   ```

2. **Parser** builds AST:

   ```
   Program
   └── FunctionDecl("fibonacci", ["n"], Block(...))
   └── VarDecl("result", Call(Ident("fibonacci"), [Literal(10)]))
   └── PrintStatement(...)
   ```

3. **Interpreter** executes:
   - Registers `fibonacci` function
   - Calls `fibonacci(10)`
   - Recursively computes: fib(9) + fib(8)
   - Returns 55
   - Prints result

## Type System

**Supported Types:**

- `int`: 42
- `float`: 3.14
- `string`: "hello"
- `bool`: true, false
- `list`: [1, 2, 3]
- `function`: Function objects

**Type Coercion:**

```python
"3" + 4     # Error - type mismatch
str(42)     # "42" - explicit conversion
```

## Performance Characteristics

**Time Complexity:**

- Lexing: O(n) where n = source length
- Parsing: O(n) with good grammar
- Interpretation: O(ast_nodes) for execution

**Recursion Depth:**

- Limited by Python's recursion limit (~1000)
- Fibonacci(30) approaches limit
- Tail call optimization not implemented

## Error Handling

```python
# Syntax Error
fn test(  # Missing closing paren

# Name Error
print(undefined_variable)

# Type Error
5 + "hello"

# Division by Zero
10 / 0
```

## Code Statistics

- **lexer.py**: 280+ lines - Tokenization
- **ast_nodes.py**: 120+ lines - Node definitions
- **parser.py**: 380+ lines - Recursive descent parser
- **interpreter.py**: 200+ lines - Tree-walking interpreter
- **example.py**: 150+ lines - Examples
- **Total**: 1,130+ lines

## Advanced Features

### Closures

```python
fn outer(x) {
    fn inner(y) {
        return x + y
    }
    return inner
}

let add_ten = outer(10)
print(add_ten(5))  # 15
```

### Higher-Order Functions

```python
fn apply_twice(f, x) {
    return f(f(x))
}

fn double(x) { return x * 2 }

print(apply_twice(double, 5))  # 20
```

### List Comprehensions (simulated)

```python
fn map_list(f, items) {
    let result = []
    for item in items {
        # Append not yet implemented,
        # but can simulate with return
    }
    return result
}
```

## Extending the Language

### Add String Methods

```python
class StringValue:
    def __init__(self, value):
        self.value = value

    def upper(self):
        return self.value.upper()
```

### Add Classes/Objects

```python
class ClassDef:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
```

### Add Modules/Imports

```python
class Module:
    def __init__(self, name, exports):
        self.name = name
        self.exports = exports
```

## Learning Outcomes

✅ **Lexical analysis** and tokenization  
✅ **Recursive descent parsing** and operator precedence  
✅ **Abstract syntax trees** and visitor pattern  
✅ **Interpreters** and tree-walking execution  
✅ **Scoping** and environment chains  
✅ **Closures** and captured environments  
✅ **Error reporting** with line numbers  
✅ **Type systems** and coercion  
✅ **Compiler/interpreter pipeline**

## Design Patterns

- **Visitor**: AST node traversal and execution
- **Factory**: Token and node creation
- **Environment Chain**: Lexical scoping
- **Exception-based control flow**: Returns via exceptions
