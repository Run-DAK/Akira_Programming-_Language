import sys
import re

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = code[self.position]
    
    def advance(self):
        self.position += 1
        if self.position < len(self.code):
            self.current_char = self.code[self.position]
        else:
            self.current_char = None
    
    def peek(self):
        if self.position + 1 < len(self.code):
            return self.code[self.position + 1]
        else:
            return None
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def identifier(self):
        identifier = ''
        while self.current_char is not None and self.current_char.isalnum():
            identifier += self.current_char
            self.advance()
        return identifier
    
    def number(self):
        number = ''
        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self.advance()
        return int(number)
    
    def get_next_token(self):
        self.skip_whitespace()
        
        if self.current_char is None:
            return None
        
        if self.current_char.isdigit():
            return ('NUMBER', self.number())
        
        if self.current_char.isalpha():
            identifier = self.identifier()
            if identifier in ['print', 'for', 'in', 'range', 'end']:
                return (identifier.upper(), identifier)
            else:
                return ('IDENTIFIER', identifier)
        
        if self.current_char in ['+', '-', '*', '/']:
            token = self.current_char
            self.advance()
            return (token, token)
        
        if self.current_char == '(':
            self.advance()
            return ('LPAREN', '(')
        
        if self.current_char == ')':
            self.advance()
            return ('RPAREN', ')')
        
        if self.current_char == ':':
            self.advance()
            return ('COLON', ':')
        
        raise Exception(f'character not present...: {self.current_char}')

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        if self.current_token is not None and self.current_token[0] == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f'syntax error: expected {token_type}, got {self.current_token}...')
    
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            value = self.current_token[1]
            self.eat('NUMBER')
            return ('NUMBER', value)
        elif self.current_token[0] == 'IDENTIFIER':
            identifier = self.current_token[1]
            self.eat('IDENTIFIER')
            return ('IDENTIFIER', identifier)
        elif self.current_token[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            raise Exception('syntax error: expected factor...')
    
    def term(self):
        node = self.factor()
        while self.current_token is not None and self.current_token[0] in ['*', '/']:
            op = self.current_token[1]
            self.eat(self.current_token[0])
            node = ('BINOP', node, op, self.factor())
        return node
    
    def expr(self):
        node = self.term()
        while self.current_token is not None and self.current_token[0] in ['+', '-']:
            op = self.current_token[1]
            self.eat(self.current_token[0])
            node = ('BINOP', node, op, self.term())
        return node
    
    def statement(self):
        if self.current_token[0] == 'PRINT':
            self.eat('PRINT')
            expr_node = self.expr()
            return ('PRINT', expr_node)
        elif self.current_token[0] == 'FOR':
            self.eat('FOR')
            var_name = self.current_token[1]
            self.eat('IDENTIFIER')
            self.eat('IN')
            self.eat('RANGE')
            self.eat('LPAREN')
            start = self.expr()
            self.eat('COLON')
            end = self.expr()
            self.eat('RPAREN')
            block = self.block()
            return ('FOR', var_name, start, end, block)
        else:
            raise Exception('syntax error: expected statement...')
    
    def block(self):
        statements = []
        while self.current_token is not None and self.current_token[0] != 'END':
            statements.append(self.statement())
        self.eat('END')
        return statements
    
    #recursive descent parser method pairing statements till the end of the code
    def program(self):
        statements = []
        while self.current_token is not None:
            statements.append(self.statement())
        return statements

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.env = {}
    
    def visit(self, node):
        if node[0] == 'NUMBER':
            return node[1]
        elif node[0] == 'IDENTIFIER':
            return self.env.get(node[1], 0)
        elif node[0] == 'BINOP':
            left = self.visit(node[1])
            op = node[2]
            right = self.visit(node[3])
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
        elif node[0] == 'PRINT':
            value = self.visit(node[1])
            print(value)
        elif node[0] == 'FOR':
            var_name = node[1]
            start = self.visit(node[2])
            end = self.visit(node[3])
            block = node[4]
            
            for i in range(start, end):
                self.env[var_name] = i
                for statement in block:
                    self.visit(statement)
        else:
            raise Exception(f'node type not specified: {node[0]}')
    
    def interpret(self):
        program = self.parser.program()
        for statement in program:
            self.visit(statement)

def main():
    
    if len(sys.argv) < 2:
        print(".ak file must be provided")
        sys.exit(1)
    ak_file_path = sys.argv[1]
    with open(ak_file_path, 'r') as file:
        code = file.read()
    lexer = Lexer(code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()

if __name__ == '__main__':
    main()


"""for i in range(0 : 5)
    print i
end """

"""print 10
print 20 + 30"""