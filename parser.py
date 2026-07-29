import sys
import scanner

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.current_scope = self.scopes[0]

    def __del__(self):
        None

    def enter_scope(self):
        new_scope = {}
        self.scopes.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope = self.scopes[-1]

    def add_variable(self, name, datatype):
        if name in self.current_scope:
            print(f"Error: Variable '{name}' already declared in this scope.")
            sys.exit(0)
        self.current_scope[name] = datatype

    def get_variable_type(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class TreeNode:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def add_child(self, node):
        if node:
            self.children.append(node)

    def __repr__(self):
        return f"{self.name}" + (f": {self.value}" if self.value else "")

def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node}")
    for child in node.children:
        print_tree(child, level + 1)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None        
        self.st = SymbolTable()

    def infer_type(self, node):
        if node.name == "Terminal":
            val = node.value   

            if '.' in val and val.replace('.', '', 1).isdigit():
                return 'point'
                
            if val.isdigit(): return 'distance'
            if val.startswith('"'): return 'name'
            if val in ('true', 'false'): return 'flag'
                        
            var_type = self.st.get_variable_type(val)
            if var_type:
                return var_type
                
            return None

        child_types = []
        has_operator = False
        
        for child in node.children:
            if child.name == "Terminal" and child.value in ('+', '-', '*', '/'):
                has_operator = True
                continue
            
            if child.value in ('(', ')', ','):
                continue
            
            t = self.infer_type(child)
            if t:
                child_types.append(t)

        if 'point' in child_types:
            return 'point'
            
        if has_operator or 'distance' in child_types:
            return 'distance'
            
        if len(child_types) > 0:
            return child_types[0]

        return None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def check_token(self, expected_token):
        if self.current_token and self.current_token == expected_token:
            node = TreeNode("Terminal", str(self.current_token[1])) 
            self.advance()
            return node
        else:
            print(f"Expected {expected_token}, but got {self.current_token} at position {self.pos}")
            sys.exit(0)

    def check_token_type(self, expected_token_type):
        if self.current_token and self.current_token[0] == expected_token_type:
            token_value = self.current_token[1]
            node = TreeNode("Terminal", str(token_value))
            self.advance()
            return node
        else:
            print(f"Expected token type '{expected_token_type}', but got {self.current_token} at position {self.pos}")
            sys.exit(0)    

    def peek(self, n=1):
        next_pos = self.pos + n
        if next_pos < len(self.tokens):
            return self.tokens[next_pos]
        return None

    ############################# Function for each rule  #############################

    def parse(self):
        root = self.parse_Program()
        print("Parsing completed successfully. Generating Tree...\n")
        return root

    def parse_Program(self):
        # Program → UseDecl* VarDecl* Action*
        node = TreeNode("Program")

        # Parse UseDecl*
        while self.current_token and self.current_token == ('KEYWORD', 'use'):
            node.add_child(self.parse_UseDecl())

        # Parse VarDecl* (Global variables)
        while self.current_token and self.current_token[1] in ('point', 'distance', 'name', 'flag'):
            node.add_child(self.parse_VarDecl())

        # Parse Action*
        while self.current_token and self.current_token == ('KEYWORD', 'action'):
            node.add_child(self.parse_Action())

        if self.current_token is not None:
            print(f"Unexpected token after program: {self.current_token} at position {self.pos}")
            sys.exit(0)
            
        return node

    def parse_UseDecl(self):
        # UseDecl → "use" IDENTIFIER ";"
        node = TreeNode("UseDecl")
        node.add_child(self.check_token(('KEYWORD', 'use')))
        node.add_child(self.check_token_type('IDENT'))
        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_Action(self):
        # Action → "action" Identifier "(" ParamList? ")" Block
        node = TreeNode("Action")
        node.add_child(self.check_token(('KEYWORD', 'action')))
        node.add_child(self.check_token_type('IDENT'))
                
        self.st.enter_scope() 

        node.add_child(self.check_token(('SYMBOL', '(')))

        # ParamList?
        if self.current_token and self.current_token != ('SYMBOL', ')'):
            node.add_child(self.parse_ParamList())

        node.add_child(self.check_token(('SYMBOL', ')')))
        node.add_child(self.parse_Block())
        
        self.st.exit_scope()
        return node

    def parse_Block(self):
        # Block → "{" Statement* "}"
        node = TreeNode("Block")
        node.add_child(self.check_token(('SYMBOL', '{')))
        
        self.st.enter_scope()

        while self.current_token and self.current_token != ('SYMBOL', '}'):
            node.add_child(self.parse_Statement())

        self.st.exit_scope()

        node.add_child(self.check_token(('SYMBOL', '}')))
        return node

    def parse_Statement(self):
        # Statement → VarDecl | AssignStmt | ShowStmt | GetStmt
        # | IfStmt | WhileStmt | ForStmt | ReturnStmt | Expr ";"
        node = TreeNode("Statement")    
        token = self.current_token
        
        if not token:
            print(f"Error: Expected statement, got end of file at position {self.pos}")
            sys.exit(0)

        # VarDecl → ("point" | "distance" | "name" | "flag") ...
        if token[0] == 'KEYWORD' and token[1] in ('point', 'distance', 'name', 'flag'):
            node.add_child(self.parse_VarDecl())

        # AssignStmt → Identifier "=" ...
        elif token[0] == 'IDENT' and self.peek() == ('OPERATOR', '='):
            node.add_child(self.parse_AssignStmt())

        # ShowStmt → "show" ...    
        elif token == ('KEYWORD', 'show'):
            node.add_child(self.parse_ShowStmt())

        # GetStmt → "get" ...
        elif token == ('KEYWORD', 'get'):
            node.add_child(self.parse_GetStmt())

        # IfStmt → "when" ...
        elif token == ('KEYWORD', 'when'):
            node.add_child(self.parse_IfStmt())

        # WhileStmt → "loop" ...
        elif token == ('KEYWORD', 'loop'):
            node.add_child(self.parse_WhileStmt())

        # ForStmt → "repeat" ...
        elif token == ('KEYWORD', 'repeat'):
            node.add_child(self.parse_ForStmt())

        # ReturnStmt → "give" ...
        elif token == ('KEYWORD', 'give'):
            node.add_child(self.parse_ReturnStmt())

        # Expr ";"
        elif (token[0] in ('IDENT', 'NUMBER', 'STRING') or
              token in (('KEYWORD', 'true'), ('KEYWORD', 'false')) or
              token == ('SYMBOL', '(')):
            node.add_child(self.parse_Expr())
            node.add_child(self.check_token(('SYMBOL', ';')))

        # Error
        else:
            print(f"Unexpected token used as a beginning of a statement: {token} at position {self.pos}")
            sys.exit(0)
            
        return node

    def parse_ReturnStmt(self):
        # ReturnStmt → "give" Expr ";"
        node = TreeNode("ReturnStmt")
        node.add_child(self.check_token(('KEYWORD', 'give')))
        node.add_child(self.parse_Expr())
        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_ForStmt(self):
        # ForStmt → "repeat" "(" VarDecl Condition ";" Expr ")" Block
        node = TreeNode("ForStmt")
        node.add_child(self.check_token(('KEYWORD', 'repeat')))
        node.add_child(self.check_token(('SYMBOL', '(')))
        node.add_child(self.parse_VarDecl())
        node.add_child(self.parse_Condition())
        node.add_child(self.check_token(('SYMBOL', ';')))
        node.add_child(self.parse_Expr())
        node.add_child(self.check_token(('SYMBOL', ')')))
        node.add_child(self.parse_Block())
        return node

    def parse_WhileStmt(self):
        # WhileStmt → "loop" "(" Condition ")" Block
        node = TreeNode("WhileStmt")
        node.add_child(self.check_token(('KEYWORD', 'loop')))
        node.add_child(self.check_token(('SYMBOL', '(')))
        node.add_child(self.parse_Condition())
        node.add_child(self.check_token(('SYMBOL', ')')))
        node.add_child(self.parse_Block())
        return node

    def parse_ShowStmt(self):
        # ShowStmt → "show" Expr ";"
        node = TreeNode("ShowStmt")
        node.add_child(self.check_token(('KEYWORD', 'show')))
        node.add_child(self.parse_Expr())
        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_GetStmt(self):
        # GetStmt → "get" Identifier ";"
        node = TreeNode("GetStmt")
        node.add_child(self.check_token(('KEYWORD', 'get')))
        #📌
        node.add_child(self.check_token_type('IDENT'))
        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_IfStmt(self):
        # IfStmt → "when" "(" Condition ")" Block ("otherwise" Block)?
        node = TreeNode("IfStmt")
        node.add_child(self.check_token(('KEYWORD', 'when')))
        node.add_child(self.check_token(('SYMBOL', '(')))
        node.add_child(self.parse_Condition())
        node.add_child(self.check_token(('SYMBOL', ')')))
        node.add_child(self.parse_Block())
        
        # ("otherwise" Block)?
        if self.current_token and self.current_token == ('KEYWORD', 'otherwise'):
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
            node.add_child(self.parse_Block())
        return node

    def parse_AssignStmt(self):
        # AssignStmt → Identifier "=" Expr ";"
        node = TreeNode("AssignStmt")
        
        # Check if variable exists
        var_name = self.current_token[1]
        var_type = self.st.get_variable_type(var_name)
        
        if not var_type:
            print(f"Error: Variable '{var_name}' is not declared.")
            sys.exit(0)

        node.add_child(self.check_token_type('IDENT'))
        node.add_child(self.check_token(('OPERATOR', '=')))
        
        # Parse expression
        expr_node = self.parse_Expr()
        node.add_child(expr_node)
        
        # --- TYPE CHECK ---
        inferred = self.infer_type(expr_node)
        if inferred and inferred != var_type:
            print(f"Type Error: Cannot assign '{inferred}' to variable '{var_name}' of type '{var_type}'")
            sys.exit(0)
        # ------------------

        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_VarDecl(self):
        # VarDecl → ("point" | "distance" | "name" | "flag") Identifier "=" Expr ";"
        node = TreeNode("VarDecl")
        if self.current_token and self.current_token[0] == 'KEYWORD':
            var_type = self.current_token[1]
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
        else:
            print(f"Error: Expected type, got {self.current_token}")
            sys.exit(0)
            
        var_name = self.current_token[1]
        self.st.add_variable(var_name, var_type)
        
        node.add_child(self.check_token_type('IDENT'))
        node.add_child(self.check_token(('OPERATOR', '=')))
        
        # Parse the expression
        expr_node = self.parse_Expr()
        node.add_child(expr_node)
        
        # --- TYPE CHECK ---
        inferred = self.infer_type(expr_node)
        if inferred and inferred != var_type:
            print(f"Type Error: Cannot assign '{inferred}' to variable '{var_name}' of type '{var_type}'")
            sys.exit(0)
        # ------------------

        node.add_child(self.check_token(('SYMBOL', ';')))
        return node

    def parse_Condition(self):
        # Condition → Expr ("==" | "!=" | "<" | "<=" | ">" | ">=") Expr
        node = TreeNode("Condition")
        node.add_child(self.parse_Expr())
        
        if (self.current_token and self.current_token[0] == 'OPERATOR'):
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
        else:
            print(f"Error: Expected comparison operator")
            sys.exit(0)
            
        node.add_child(self.parse_Expr())
        return node

    def parse_Expr(self):
        # Expr → Term (("+" | "-") Term)*
        node = TreeNode("Expr")
        node.add_child(self.parse_Term())
        while self.current_token and self.current_token in (('OPERATOR', '+'), ('OPERATOR', '-')):
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
            node.add_child(self.parse_Term())
        return node

    def parse_Term(self):
        # Term → Factor (("*" | "/") Factor)*
        node = TreeNode("Term")
        node.add_child(self.parse_Factor())
        while self.current_token and self.current_token in (('OPERATOR', '*'), ('OPERATOR', '/')):
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
            node.add_child(self.parse_Factor())
        return node

    def parse_Factor(self):
        # Factor → INTEGER | FLOAT | STRING | "true" | "false"
        # | Identifier | "(" Expr ")" | Identifier "(" ExprList? ")"
        node = TreeNode("Factor")
        token = self.current_token
        
        if not token:
            print("Error: Expected factor")
            sys.exit(0)

        # INTEGER | FLOAT | STRING
        if token[0] in ('NUMBER', 'STRING'): 
            node.add_child(TreeNode("Terminal", str(token[1])))
            self.advance()

        # "true" | "false"
        elif token in (('KEYWORD', 'true'), ('KEYWORD', 'false')):
            node.add_child(TreeNode("Terminal", str(token[1])))
            self.advance()

        # "(" Expr ")"
        elif token == ('SYMBOL', '('):
            node.add_child(self.check_token(('SYMBOL', '(')))
            node.add_child(self.parse_Expr())
            node.add_child(self.check_token(('SYMBOL', ')')))

        # Identifier or Identifier "(" ... ")"
        elif token[0] == 'IDENT':
            # Identifier "(" ExprList? ")"
            if self.peek() == ('SYMBOL', '('):                
                node.add_child(self.check_token_type('IDENT'))
                node.add_child(self.check_token(('SYMBOL', '(')))

                if self.current_token and self.current_token != ('SYMBOL', ')'):
                    node.add_child(self.parse_ExprList())

                node.add_child(self.check_token(('SYMBOL', ')')))

            else:
                # Just Identifier
                node.add_child(self.check_token_type('IDENT'))

        else:
            print(f"Error: Expected factor, got {token}")
            sys.exit(0)

        return node

    def parse_ExprList(self):
        # ExprList → Expr ("," Expr)*
        node = TreeNode("ExprList")
        node.add_child(self.parse_Expr())
        while self.current_token and self.current_token == ('SYMBOL', ','):
            node.add_child(self.check_token(('SYMBOL', ',')))
            node.add_child(self.parse_Expr())
        return node

    def parse_ParamList(self):
        # ParamList → Param ("," Param)*
        node = TreeNode("ParamList")
        node.add_child(self.parse_Param())
        while self.current_token and self.current_token == ('SYMBOL', ','):
            node.add_child(self.check_token(('SYMBOL', ',')))
            node.add_child(self.parse_Param())
        return node

    def parse_Param(self):
        # Param → ('point' | 'distance' | 'name' | 'flag') Identifier
        node = TreeNode("Param")
        if self.current_token and self.current_token[0] == 'KEYWORD':
            # 1. Capture param type
            param_type = self.current_token[1]
            
            t_val = self.current_token[1]
            self.advance()
            node.add_child(TreeNode("Terminal", t_val))
        else:
            print(f"Expected type")
            sys.exit(0)
        
        # 2. Capture param name
        param_name = self.current_token[1]
        
        # 3. Add to Symbol Table
        self.st.add_variable(param_name, param_type)
        
        node.add_child(self.check_token_type('IDENT'))
        return node

if __name__ == "__main__":
    # Opening and reading example code
    filename = 'example.syntra'
    f = open(filename)
    syntra_code = f.read()        
    
    # Scanning
    tokens = scanner.syntra_scanner(syntra_code)
    print(tokens)
    
    # Parsing
    parser = Parser(tokens)
    parse_tree = parser.parse()
    print_tree(parse_tree)