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
    ("KEYWORD",   r"\b(?:use|action|begin|point|distance|name|flag|show|get|when|otherwise|loop|repeat|give|space|note)\b"),
    ("IDENT",     r"[A-Za-z_][A-Za-z0-9_]*"),    # Identifiers
    ("OP",        r"[+\-*/=<>!]+"),              # Operators
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

        if kind in {"SKIP", "NEWLINE"}:
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
    if len(sys.argv) != 2:
        print("Usage: python scanner.py filename")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            syntra_code = f.read()
    except FileNotFoundError:
        print(FileNotFoundError)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
            
    print(f"🔸 Scanning Syntra code from: {filename}\n")
    print("🔍 Scanning...\n")

    try:
        result = syntra_scanner(syntra_code)
        print("=== 🧾 Tokens ===")
        for token in result:
            print(token)
    except SyntaxError as e:
        print(f"Lexical Error: {e}")
        sys.exit(1)