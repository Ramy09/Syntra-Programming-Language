import re
import sys

# ----------------------------------
# 🔹 Syntra Scanner (Lexer)
# ----------------------------------

KEYWORDS = {
    "use", "action", "begin", "point", "distance", "name", "flag",
    "show", "get", "when", "otherwise", "loop", "repeat",
    "give", "space", "note"
}

TOKEN_SPEC = [
    ("COMMENT",   r"note[^\n]*"),                # Comments
    ("STRING",    r'"[^"\n]*"'),                 # "text"
    ("NUMBER",    r"\d+\.\d+|\d+"),              # Numbers
    ("KEYWORD",   r"\b(?:use|action|point|distance|name|flag|show|get|when|otherwise|loop|repeat|give|space|note)\b"),
    ("IDENT",     r"[A-Za-z_][A-Za-z0-9_]*"),    # Identifiers
    ("OPERATOR",        r"[+\-*/=<>!]+"),              # Operators
    ("SYMBOL",    r"[{}();,]"),                  # Symbols
    ("NEWLINE",   r"\n"),                        # Line breaks
    ("SKIP",      r"[ \t]+"),                    # Spaces/tabs
    ("MISMATCH",  r"."),                         # Unknown chars
]


MASTER_PATTERN = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

def syntra_scanner(code):
    tokens = []
    for match in MASTER_PATTERN.finditer(code):
        kind = match.lastgroup
        value = match.group()

        if kind in {"SKIP", "NEWLINE", "COMMENT"}:
            continue
        elif kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        elif kind == "STRING":
            value = value.strip('"')
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character: {value}")

        tokens.append((kind, value))
    return tokens


# ----------------------------------
# 🔹 Main Program
# ----------------------------------
if __name__ == "__main__":

    # Opening and reading example code
    filename = 'example1.syntra'
    f = open(filename)
    syntra_code = f.read()        
    
    # Scanning and printing    
    tokens = syntra_scanner(syntra_code)
    print("=== Tokens ===")
    for token in tokens:
    	print(token)
