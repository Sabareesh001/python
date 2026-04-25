"""
Compiler/Interpreter example for mini language.
Demonstrates lexer, parser, and interpreter.
"""

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


# Example programs in mini language
EXAMPLES = {
    'fibonacci': '''
fn fibonacci(n) {
    if n <= 1 { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

let result = fibonacci(10)
print("Fibonacci(10) =")
print(result)
''',
    
    'factorial': '''
fn factorial(n) {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}

print("Factorials:")
let i = 1
while i <= 5 {
    print(factorial(i))
    let i = i + 1
}
''',
    
    'sum_list': '''
fn sum_list(nums) {
    let total = 0
    for item in nums {
        let total = total + item
    }
    return total
}

let numbers = [1, 2, 3, 4, 5]
print("Sum of list:")
print(sum_list(numbers))
''',
    
    'conditionals': '''
let age = 25

if age < 13 {
    print("Child")
} else {
    if age < 18 {
        print("Teenager")
    } else {
        if age < 65 {
            print("Adult")
        } else {
            print("Senior")
        }
    }
}
''',
    
    'loops': '''
print("Counting from 1 to 5:")
let i = 1
while i <= 5 {
    print(i)
    let i = i + 1
}

print("Iterating through list:")
for x in [10, 20, 30, 40] {
    print(x)
}
''',
    
    'arithmetic': '''
print("Arithmetic operations:")
print(2 + 3)
print(10 - 4)
print(3 * 4)
print(20 / 4)
print(17 % 5)

let x = 5
let y = 3
print((x + y) * 2)
''',
}


def print_header(title: str) -> None:
    """Print section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def run_example(name: str, source: str) -> None:
    """Run an example program."""
    print_header(f"Example: {name.upper()}")
    
    print("--- Source Code ---")
    print(source.strip())
    print("\n--- Lexer Output (first 20 tokens) ---")
    
    try:
        # Lexing
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Show first 20 tokens
        for token in tokens[:20]:
            print(f"  {token}")
        
        if len(tokens) > 20:
            print(f"  ... and {len(tokens) - 20} more tokens")
        
        print("\n--- Parser Output (AST) ---")
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        print(f"  {ast}")
        if ast.statements:
            for i, stmt in enumerate(ast.statements[:3], 1):
                print(f"    {i}. {stmt}")
            if len(ast.statements) > 3:
                print(f"    ... and {len(ast.statements) - 3} more statements")
        
        print("\n--- Interpreter Output (Runtime) ---")
        
        # Interpretation
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MINI LANGUAGE COMPILER/INTERPRETER")
    print("=" * 70)
    
    print("\nSupported Features:")
    print("  - Variables (let)")
    print("  - Functions (fn)")
    print("  - Conditionals (if/else)")
    print("  - Loops (while, for)")
    print("  - Arithmetic & Logical operators")
    print("  - Lists and indexing")
    print("  - Print statements")
    print("  - Recursion")
    
    # Run examples
    for name, source in EXAMPLES.items():
        run_example(name, source)
    
    print("\n" + "=" * 70)
    print("PIPELINE DEMONSTRATION")
    print("=" * 70)
    print("\nPipeline Stages:")
    print("  1. Lexer:      Source Code → Tokens")
    print("  2. Parser:     Tokens → AST")
    print("  3. Interpreter: AST → Execution")
    
    print("\n" + "=" * 70)
    print("All examples complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
