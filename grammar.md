# Terminals (T)

T = {
  "begin", "action", "use", "show", "get", "when", "otherwise", "loop",
  "repeat", "give", "space", "note", "point", "distance", "name", "flag",
  "true", "false",
  "=", "==", "!=", "+", "-", "*", "/", "<", "<=", ">", ">=",
  "(", ")", "{", "}", ";",
  IDENTIFIER,
  INTEGER,
  FLOAT,
  STRING
}

# Non-terminals (N)

N = {
  Program,
  UseDecl,
  Action,
  ParamList,
  Param,
  Block,
  Statement,
  VarDecl,
  AssignStmt,
  ShowStmt,
  GetStmt,
  IfStmt,
  WhileStmt,
  ForStmt,
  ReturnStmt,
  Condition,
  Expr,
  Term,
  Factor,
  ExprList
}

# Production Rules (P)

Program      → UseDecl* Action*

UseDecl      → "use" IDENTIFIER ";"

Action       → "action" IDENTIFIER "(" ParamList? ")" Block

ParamList    → Param ("," Param)*
Param        → Type IDENTIFIER

Block        → "{" Statement* "}"

Statement    → VarDecl
             | AssignStmt
             | ShowStmt
             | GetStmt
             | IfStmt
             | WhileStmt
             | ForStmt
             | ReturnStmt
             | Expr ";"

VarDecl      → ("point" | "distance" | "name" | "flag") IDENTIFIER "=" Expr ";"

AssignStmt   → IDENTIFIER "=" Expr ";"

ShowStmt     → "show" Expr ";"

GetStmt      → "get" IDENTIFIER ";"

IfStmt       → "when" "(" Condition ")" Block ("otherwise" Block)?

WhileStmt    → "loop" "(" Condition ")" Block

ForStmt      → "repeat" "(" VarDecl Condition ";" Expr ")" Block

ReturnStmt   → "give" Expr ";"

Expr         → Term (("+" | "-") Term)*
Term         → Factor (("*" | "/") Factor)*

Factor       → INTEGER
             | FLOAT
             | STRING
             | "true"
             | "false"
             | IDENTIFIER
             | "(" Expr ")"
             | IDENTIFIER "(" ExprList? ")"

Condition    → Expr ("==" | "!=" | "<" | "<=" | ">" | ">=") Expr

ExprList     → Expr ("," Expr)*