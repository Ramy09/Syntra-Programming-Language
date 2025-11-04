import sys
import scanner

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def check_token(self, expected_token):
        if self.current_token and self.current_token == expected_token:
            self.advance()
        else:
            print(
                f"Expected {expected_token}, but got {self.current_token} at position {self.pos}"
            )
            sys.exit(0)

    def check_token_type(self, expected_token_type):
        if self.current_token and self.current_token[0] == expected_token_type:
            token_value = self.current_token[1]
            self.advance()
            return token_value
        else:
            print(
                f"Expected token type '{expected_token_type}', but got {self.current_token} at position {self.pos}"
            )
            sys.exit(0)    

    def peek(self, n=1):
        next_pos = self.pos + n
        if next_pos < len(self.tokens):
            return self.tokens[next_pos]
        return None

############################ Function for each rule 👇 ##############################################

    def parse(self):
        self.parse_Program()
        print("Parsing completed successfully")

    def parse_Program(self):
        # Program → UseDecl* Action*

        # Parse UseDecl*
        while self.current_token and self.current_token == ('KEYWORD', 'use'):
            self.parse_UseDecl()

        # Parse Action*
        while self.current_token and self.current_token == ('KEYWORD', 'action'):
            self.parse_Action()

        # Ensure no unexpected trailing tokens
        if self.current_token is not None:
            print(
                f"Unexpected token after program: {self.current_token} at position {self.pos}"
            )
            sys.exit(0)

    def parse_UseDecl(self):
        # UseDecl → "use" IDENTIFIER ";"
        self.check_token(('KEYWORD', 'use'))
        self.check_token_type('IDENT')
        self.check_token(('SYMBOL', ';'))

    def parse_Action(self):
        # Action → "action" Identifier "(" ParamList? ")" Block
        self.check_token(('KEYWORD', 'action'))
        self.check_token_type('IDENT')
        self.check_token(('SYMBOL', '('))
        
        # ParamList? - Only parse if it's not an immediate close paren
        if self.current_token and self.current_token != ('SYMBOL', ')'):
            self.parse_ParamList()
            
        self.check_token(('SYMBOL', ')'))
        self.parse_Block()

    def parse_Block(self):
        # Block → "{" Statement* "}"
        self.check_token(('SYMBOL', '{'))

        while self.current_token and self.current_token != ('SYMBOL', '}'):
            self.parse_Statement()

        self.check_token(('SYMBOL', '}'))

    def parse_Statement(self):
        # Statement → VarDecl | AssignStmt | ShowStmt | GetStmt
        # | IfStmt | WhileStmt | ForStmt | ReturnStmt | Expr ";"
        
        token = self.current_token
        if not token:
            print(f"Error: Expected statement, got end of file at position {self.pos}")
            sys.exit(0)

        # VarDecl → ("point" | "distance" | "name" | "flag") ...
        if token[0] == 'KEYWORD' and token[1] in ('point', 'distance', 'name', 'flag'):
            self.parse_VarDecl()

        # AssignStmt → Identifier "=" ...
        elif token[0] == 'IDENT' and self.peek() == ('OPERATOR', '='):
            self.parse_AssignStmt()

        # ShowStmt → "show" ...
        elif token == ('KEYWORD', 'show'):
            self.parse_ShowStmt()

        # GetStmt → "get" ...
        elif token == ('KEYWORD', 'get'):
            self.parse_GetStmt()

        # IfStmt → "when" ...
        elif token == ('KEYWORD', 'when'):
            self.parse_IfStmt() # Does not end in ';'

        # WhileStmt → "loop" ...
        elif token == ('KEYWORD', 'loop'):
            self.parse_WhileStmt() # Does not end in ';'

        # ForStmt → "repeat" ...
        elif token == ('KEYWORD', 'repeat'):
            self.parse_ForStmt() # Does not end in ';'

        # ReturnStmt → "give" ...
        elif token == ('KEYWORD', 'give'):
            self.parse_ReturnStmt()
        
        # Expr ";"
        # Check if it looks like the start of an Expression
        elif (token[0] in ('IDENT', 'NUMBER', 'STRING') or
              token in (('KEYWORD', 'true'), ('KEYWORD', 'false')) or
              token == ('SYMBOL', '(')):
            self.parse_Expr()
            self.check_token(('SYMBOL', ';')) # Semicolon for the Expr statement
            
        # Error
        else:
            print(
                f"Unexpected token used as a beginning of a statement: {token} at position {self.pos}"
            )
            sys.exit(0)

    def parse_ReturnStmt(self):
        # ReturnStmt → "give" Expr ";"
        self.check_token(('KEYWORD', 'give'))
        self.parse_Expr()
        self.check_token(('SYMBOL', ';'))

    def parse_ForStmt(self):
        # ForStmt → "repeat" "(" VarDecl Condition ";" Expr ")" Block
        self.check_token(('KEYWORD', 'repeat'))
        self.check_token(('SYMBOL', '('))
        self.parse_VarDecl()  # VarDecl includes its own semicolon
        self.parse_Condition()
        self.check_token(('SYMBOL', ';'))
        self.parse_Expr()
        self.check_token(('SYMBOL', ')'))
        self.parse_Block()

    def parse_WhileStmt(self):
        # WhileStmt → "loop" "(" Condition ")" Block
        self.check_token(('KEYWORD', 'loop'))
        self.check_token(('SYMBOL', '('))
        self.parse_Condition()
        self.check_token(('SYMBOL', ')'))
        self.parse_Block()

    def parse_ShowStmt(self):
        # ShowStmt → "show" Expr ";"
        self.check_token(('KEYWORD', 'show'))
        self.parse_Expr()
        self.check_token(('SYMBOL', ';'))

    def parse_GetStmt(self):
        # GetStmt → "get" Identifier ";"
        self.check_token(('KEYWORD', 'get'))
        self.check_token_type('IDENT')
        self.check_token(('SYMBOL', ';'))

    def parse_IfStmt(self):
        # IfStmt → "when" "(" Condition ")" Block ("otherwise" Block)?
        self.check_token(('KEYWORD', 'when'))
        self.check_token(('SYMBOL', '('))
        self.parse_Condition()
        self.check_token(('SYMBOL', ')'))
        self.parse_Block()
        
        if self.current_token and self.current_token == ('KEYWORD', 'otherwise'):
            self.advance() # Consume 'otherwise'
            self.parse_Block()

    def parse_AssignStmt(self):
        # AssignStmt → Identifier "=" Expr ";"
        self.check_token_type('IDENT')
        self.check_token(('OPERATOR', '='))
        self.parse_Expr()
        self.check_token(('SYMBOL', ';'))

    def parse_VarDecl(self):
        # VarDecl → ("point" | "distance" | "name" | "flag") Identifier "=" Expr ";"
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ('point', 'distance', 'name', 'flag'):
            self.advance() # Consume type keyword
        else:
            print(
                f"Error: Expected type (point, distance, name, flag), got {self.current_token} at position {self.pos}"
            )
            sys.exit(0)
            
        self.check_token_type('IDENT')
        self.check_token(('OPERATOR', '='))
        self.parse_Expr()
        self.check_token(('SYMBOL', ';'))

    def parse_Condition(self):
        # Condition → Expr ("==" | "!=" | "<" | "<=" | ">" | ">=") Expr
        self.parse_Expr()
        
        if (self.current_token and self.current_token[0] == 'OPERATOR' and 
            self.current_token[1] in ('==', '!=', '<', '>=', '>', '<=')):
            self.advance() # Consume operator
        else:
            print(
                f"Error: Expected comparison operator, got {self.current_token} at position {self.pos}"
            )
            sys.exit(0)
            
        self.parse_Expr()

    def parse_Expr(self):
        # Expr → Term (("+" | "-") Term)*
        self.parse_Term()
        while self.current_token and self.current_token in (('OPERATOR', '+'), ('OPERATOR', '-')):
            self.advance()
            self.parse_Term()

    def parse_Term(self):
        # Term → Factor (("*" | "/") Factor)*
        self.parse_Factor()
        while self.current_token and self.current_token in (('OPERATOR', '*'), ('OPERATOR', '/')):
            self.advance()
            self.parse_Factor()

    def parse_Factor(self):
        # Factor → INTEGER | FLOAT | STRING | "true" | "false"
        # | Identifier | "(" Expr ")" | Identifier "(" ExprList? ")"
        
        token = self.current_token
        if not token:
            print(f"Error: Expected factor, got end of file at position {self.pos}")
            sys.exit(0)

        # INTEGER | FLOAT | STRING
        if token[0] in ('NUMBER', 'STRING'): # Assuming scanner combines INT and FLOAT
            self.advance()
        
        # "true" | "false"
        elif token in (('KEYWORD', 'true'), ('KEYWORD', 'false')):
            self.advance()
            
        # "(" Expr ")"
        elif token == ('SYMBOL', '('):
            self.advance() # Consume '('
            self.parse_Expr()
            self.check_token(('SYMBOL', ')'))
            
        # Identifier or Identifier "(" ... ")"
        elif token[0] == 'IDENT':
            if self.peek() == ('SYMBOL', '('):
                # Identifier "(" ExprList? ")"
                self.advance() # Consume IDENT
                self.advance() # Consume '('
                
                if self.current_token and self.current_token != ('SYMBOL', ')'):
                    self.parse_ExprList()
                    
                self.check_token(('SYMBOL', ')'))
            else:
                # Just Identifier
                self.advance()
                
        # Error
        else:
            print(
                f"Error: Expected factor (literal, variable, function call, or expression), got {token} at position {self.pos}"
            )
            sys.exit(0)

    def parse_ExprList(self):
        # ExprList → Expr ("," Expr)*
        self.parse_Expr()
        while self.current_token and self.current_token == ('SYMBOL', ','):
            self.advance() # Consume ','
            self.parse_Expr()

    def parse_ParamList(self):
        # ParamList → Param ("," Param)*
        self.parse_Param()
        while self.current_token and self.current_token == ('SYMBOL', ','):
            self.advance() # Consume ','
            self.parse_Param()

    def parse_Param(self):
        # Param → ('point' | 'distance' | 'name' | 'flag') Identifier
        if not (self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ('point', 'distance', 'name', 'flag')):
            print(f"Expected type (point, distance, name, flag), got {self.current_token} at position {self.pos}")
            sys.exit(0)
        self.advance() # Consume type
        
        self.check_token_type('IDENT')

if __name__ == "__main__":

    # Opening and reading example code
    filename = 'example1.syntra'
    f = open(filename)
    syntra_code = f.read()        
    
    # Scanning
    tokens = scanner.syntra_scanner(syntra_code)
    
    # Parsing
    parser = Parser(tokens)
    parser.parse()