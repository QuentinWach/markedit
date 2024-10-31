import customtkinter as ctk
import markdown2
from tkinter import filedialog
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import sympy
from io import BytesIO
import re
import os



class MarkdownEditor:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Markdown Editor")
        self.app.geometry("1200x800")
        
        # Configure grid layout
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)
        self.app.grid_rowconfigure(1, weight=1)
        
        # Create menu frame
        self.menu_frame = ctk.CTkFrame(self.app, height=40)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Add buttons
        self.new_button = ctk.CTkButton(self.menu_frame, text="New", command=self.new_file, width=80)
        self.new_button.pack(side="left", padx=5)
        
        self.open_button = ctk.CTkButton(self.menu_frame, text="Open", command=self.open_file, width=80)
        self.open_button.pack(side="left", padx=5)
        
        self.save_button = ctk.CTkButton(self.menu_frame, text="Save", command=self.save_file, width=80)
        self.save_button.pack(side="left", padx=5)
        
        # Create editor
        self.editor = ctk.CTkTextbox(self.app, wrap="word")
        self.editor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.editor.bind("<<Modified>>", self.on_edit)
        
        # Create preview
        self.preview = tk.Canvas(self.app, bg='white')
        self.preview.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar for preview
        self.preview_scrollbar = ttk.Scrollbar(self.app, orient="vertical", command=self.preview.yview)
        self.preview_scrollbar.grid(row=1, column=2, sticky="ns")
        self.preview.configure(yscrollcommand=self.preview_scrollbar.set)
        
        # Create preview frame inside canvas
        self.preview_frame = tk.Frame(self.preview, bg='white')
        self.preview.create_window((0, 0), window=self.preview_frame, anchor="nw")
        
        # Sample text
        sample_text = """# Math Examples

Inline math: $x^2 + y^2 = z^2$ in a sentence.

Display math:

$$
\\begin{aligned}
\\frac{\\partial f}{\\partial x} &= 2x \\\\
\\frac{\\partial f}{\\partial y} &= 2y
\\end{aligned}
$$

More complex example:

$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
"""
        
        self.editor.insert("1.0", sample_text)
        self.update_preview()

    def render_latex(self, latex_str, is_display=False):
        """Render LaTeX string to PIL Image using sympy"""
        try:
            expr = sympy.latex(sympy.sympify(latex_str))
            if is_display:
                expr = fr"\displaystyle {expr}"
            
            # Use sympy to render the LaTeX
            png_data = sympy.preview(expr, output='png', viewer='BytesIO',
                                   euler=False, packages=('amsmath', 'amssymb'))
            
            # Convert to PIL Image
            image = Image.open(BytesIO(png_data))
            return ImageTk.PhotoImage(image)
        except:
            return None

    def extract_math(self, text):
        """Extract math expressions and replace with placeholders"""
        display_math = []
        inline_math = []
        
        # Extract display math
        for match in re.finditer(r'\$\$(.*?)\$\$', text, re.DOTALL):
            display_math.append(match.group(1).strip())
            text = text.replace(match.group(0), f'DISPLAY_MATH_{len(display_math)-1}')
            
        # Extract inline math
        for match in re.finditer(r'\$(.*?)\$', text):
            inline_math.append(match.group(1).strip())
            text = text.replace(match.group(0), f'INLINE_MATH_{len(inline_math)-1}')
            
        return text, display_math, inline_math

    def update_preview(self):
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        # Get text from editor
        text = self.editor.get("1.0", "end-1c")
        
        # Extract math expressions
        processed_text, display_math, inline_math = self.extract_math(text)
        
        # Convert markdown to HTML
        html = markdown2.markdown(processed_text)
        
        # Create a label for the HTML content
        content_label = tk.Label(self.preview_frame, text=html, justify=tk.LEFT,
                               wraplength=500, bg='white')
        content_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Render math expressions
        for i, math_expr in enumerate(display_math):
            img = self.render_latex(math_expr, is_display=True)
            if img:
                label = tk.Label(self.preview_frame, image=img, bg='white')
                label.image = img  # Keep a reference
                label.pack(pady=10)
                
        for i, math_expr in enumerate(inline_math):
            img = self.render_latex(math_expr, is_display=False)
            if img:
                label = tk.Label(self.preview_frame, image=img, bg='white')
                label.image = img  # Keep a reference
                label.pack(pady=5)
        
        # Update scroll region
        self.preview_frame.update_idletasks()
        self.preview.configure(scrollregion=self.preview.bbox("all"))

    def on_edit(self, event=None):
        self.editor.edit_modified(False)
        self.update_preview()


    def new_file(self):
        self.editor.delete("1.0", "end")
        self.update_preview()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.editor.delete("1.0", "end")
                    self.editor.insert("1.0", content)
                    self.update_preview()
            except Exception as e:
                print(f"Error opening file: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.editor.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
            except Exception as e:
                print(f"Error saving file: {e}")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    editor = MarkdownEditor()
    editor.run()