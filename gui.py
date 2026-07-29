import tkinter as tk
from tkinter import filedialog, ttk
import sys
import io
import contextlib

import scanner
import parser

class SyntraIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Syntra Language IDE")
        self.root.geometry("900x700")

        # --- Top Frame: Buttons ---
        self.top_frame = tk.Frame(root, pady=5)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_open = tk.Button(self.top_frame, text="📂 Open Source File", command=self.open_file, bg="#e1e1e1")
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_run = tk.Button(self.top_frame, text="▶ Run Parser", command=self.run_parser, bg="#90ee90", font=("Arial", 10, "bold"))
        self.btn_run.pack(side=tk.LEFT, padx=10)

        # --- Middle Frame: Code Editor ---
        self.editor_frame = tk.LabelFrame(root, text="Source Code Editor", padx=5, pady=5)
        self.editor_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.txt_editor = tk.Text(self.editor_frame, height=15, font=("Consolas", 11), undo=True)
        self.scroll_editor = tk.Scrollbar(self.editor_frame, command=self.txt_editor.yview)
        self.txt_editor.configure(yscrollcommand=self.scroll_editor.set)
        
        self.txt_editor.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scroll_editor.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Bottom Frame: Output Tabs ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Tab 1: Console / Output (Errors & Success messages)
        self.tab_console = tk.Frame(self.notebook)
        self.notebook.add(self.tab_console, text="Console Output")
        self.txt_console = tk.Text(self.tab_console, state='disabled', font=("Consolas", 10), bg="#f0f0f0")
        self.txt_console.pack(expand=True, fill=tk.BOTH)

        # Tab 2: Token List
        self.tab_tokens = tk.Frame(self.notebook)
        self.notebook.add(self.tab_tokens, text="Token List")
        self.txt_tokens = tk.Text(self.tab_tokens, state='disabled', font=("Consolas", 10))
        self.txt_tokens.pack(expand=True, fill=tk.BOTH)

        # Tab 3: Parse Tree
        self.tab_tree = tk.Frame(self.notebook)
        self.notebook.add(self.tab_tree, text="Parse Tree")
        self.txt_tree = tk.Text(self.tab_tree, state='disabled', font=("Consolas", 10))
        self.txt_tree.pack(expand=True, fill=tk.BOTH)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Syntra Files", "*.syntra"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                code = file.read()
                self.txt_editor.delete("1.0", tk.END)
                self.txt_editor.insert(tk.END, code)
            self.write_console(f"Loaded: {file_path}\n")

    def run_parser(self):
        # 1. Get Code from Editor
        code = self.txt_editor.get("1.0", tk.END).strip()
        if not code:
            self.write_console("Error: Editor is empty!\n")
            return

        # Clear previous outputs
        self.clear_outputs()

        # 2. Scanning Phase
        try:
            tokens = scanner.syntra_scanner(code)
            
            # Display Tokens nicely
            token_str = ""
            for t in tokens:
                token_str += f"{t}\n"
            self.write_to_widget(self.txt_tokens, token_str)

        except Exception as e:
            self.write_console(f"Scanner Error: {e}\n")
            return

        # 3. Parsing Phase
        # We need to capture stdout because your parser uses 'print'
        capture_output = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(capture_output):
                # Initialize your Parser with the tokens
                parser_instance = parser.Parser(tokens)
                
                # Run the parse logic
                # We expect SystemExit(0) if there's a parser error, so we catch it.
                root_node = parser_instance.parse()
                
                # If successful, print the tree
                parser.print_tree(root_node)

            # If we get here, parsing was successful
            self.write_console("Parsing Completed Successfully!\n")
            self.write_to_widget(self.txt_tree, capture_output.getvalue())
            self.notebook.select(self.tab_tree) # Switch to tree view

        except SystemExit:
            # The parser calls sys.exit(0) on error. 
            # The error message was printed to stdout before exit, so we capture it.
            error_msg = capture_output.getvalue()
            self.write_console("Parsing Failed:\n")
            self.write_console(error_msg)
            self.notebook.select(self.tab_console) # Switch to console view

        except Exception as e:
            self.write_console(f"Unexpected Error: {e}\n")

    def write_console(self, message):
        self.txt_console.config(state='normal')
        self.txt_console.insert(tk.END, message)
        self.txt_console.see(tk.END)
        self.txt_console.config(state='disabled')

    def write_to_widget(self, widget, content):
        widget.config(state='normal')
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.config(state='disabled')

    def clear_outputs(self):
        self.txt_console.config(state='normal')
        self.txt_console.delete("1.0", tk.END)
        self.txt_console.config(state='disabled')
        
        self.txt_tokens.config(state='normal')
        self.txt_tokens.delete("1.0", tk.END)
        self.txt_tokens.config(state='disabled')

        self.txt_tree.config(state='normal')
        self.txt_tree.delete("1.0", tk.END)
        self.txt_tree.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = SyntraIDE(root)
    root.mainloop()