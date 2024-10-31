import customtkinter as ctk
import markdown2
import markdown
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sympy
from io import BytesIO
import re
import os
from tkinter import messagebox
import html
import matplotlib.pyplot as plt
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from mdx_math import MathExtension
# Remove these imports
from PIL import Image, ImageTk
import sympy

class MarkdownEditor:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Markdown Editor")
        self.app.geometry("1200x800")
        
        # Fix HTML template by escaping curly braces in the MathJax config
        self.html_template = """
        <html>
        <head>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    tex2jax: {{
                        inlineMath: [['$','$'], ['\\\\(','\\\\)']],
                        displayMath: [['$$','$$'], ['\\\\[','\\\\]']],
                        processEscapes: true
                    }}
                }});
            </script>
        </head>
        <body>
            {}
        </body>
        </html>
        """
        
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
        
        # Add toggle button
        self.show_raw_html = False
        self.current_html = ""
        
        self.toggle_button = ctk.CTkButton(
            self.menu_frame, 
            text="Show Raw HTML", 
            command=self.toggle_preview_mode, 
            width=120
        )
        self.toggle_button.pack(side="left", padx=5)
        
        # Create editor
        self.editor = ctk.CTkTextbox(self.app, wrap="word")
        self.editor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.editor.bind("<<Modified>>", self.on_edit)
        
        # Create preview frame
        self.preview_frame = ctk.CTkFrame(self.app)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Create text widget for preview
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap="word",
            padx=10,
            pady=10,
            bg='white',
            font=('Arial', 11)
        )
        self.preview_text.pack(side="left", fill="both", expand=True)
        
        # Make preview text read-only
        self.preview_text.config(state='disabled')
        
        # Add scrollbar for preview
        self.scrollbar = ttk.Scrollbar(
            self.preview_frame,
            orient="vertical",
            command=self.preview_text.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.preview_text.configure(yscrollcommand=self.scrollbar.set)
        
        # Initialize tags for HTML rendering
        self.setup_text_tags()
        
        # Store rendered LaTeX images
        self.latex_images = {}
        
        # Sample text at the end
        sample_text = """
# Math Examples

*Inline math with dollars:* $x^2 + y^2 = z^2$ in a sentence.

*Inline math with escaped delimiters:* \\(E = mc^2\\) in a sentence.

*Display math with dollars:*
$$
\\begin{aligned}
\\frac{\\partial f}{\\partial x} &= 2x \\\\
\\frac{\\partial f}{\\partial y} &= 2y
\\end{aligned}
$$

*Display math with escaped delimiters:*
\\[
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
\\]
        """
        self.editor.insert("1.0", sample_text)
        self.update_preview()

    def setup_text_tags(self):
        """Set up text tags for HTML rendering"""
        self.preview_text.tag_configure("h1", font=("Arial", 24, "bold"))
        self.preview_text.tag_configure("h2", font=("Arial", 20, "bold"))
        self.preview_text.tag_configure("h3", font=("Arial", 16, "bold"))
        self.preview_text.tag_configure("h4", font=("Arial", 14, "bold"))
        self.preview_text.tag_configure("h5", font=("Arial", 12, "bold"))
        self.preview_text.tag_configure("h6", font=("Arial", 11, "bold"))
        self.preview_text.tag_configure("p", font=("Arial", 11))
        self.preview_text.tag_configure("code", font=("Courier", 10))
        self.preview_text.tag_configure("pre", font=("Courier", 10), background="#f0f0f0")
        self.preview_text.tag_configure("em", font=("Arial", 11, "italic"))
        self.preview_text.tag_configure("strong", font=("Arial", 11, "bold"))
        self.preview_text.tag_configure("ul", lmargin1=20, lmargin2=40)
        self.preview_text.tag_configure("ol", lmargin1=20, lmargin2=40)
        self.preview_text.tag_configure("blockquote", lmargin1=40, lmargin2=40, 
                                      background="#f0f0f0", font=("Arial", 11, "italic"))
        self.preview_text.tag_configure("center", justify='center')
        
        # Add new tags for the extensions
        self.preview_text.tag_configure("mark", background="yellow")  # for highlighting
        self.preview_text.tag_configure("del", overstrike=True)  # for strikethrough
        self.preview_text.tag_configure("sub", offset=-4)  # for subscript
        self.preview_text.tag_configure("sup", offset=4)  # for superscript
        self.preview_text.tag_configure("mathjax", foreground="blue")  # for math

    def insert_html_content(self, html_content):
        """Insert HTML content with proper formatting"""
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', 'end')
        
        # Create full HTML document with MathJax support
        full_html = self.html_template.format(html_content)
        
        # Remove script tags but keep their content for LaTeX
        cleaned_html = re.sub(r'<script type="math/tex(?:;[^"]*)?">([^<]+)</script>', r'\1', html_content)
        
        # Remove other HTML tags while keeping the content
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_html)
        cleaned_text = html.unescape(cleaned_text)
        
        # Insert the cleaned text
        self.preview_text.insert('end', cleaned_text)
        
        # Apply formatting based on HTML tags
        current_pos = '1.0'
        for tag_pattern, tag_name in [
            (r'<h1[^>]*>(.*?)</h1>', 'h1'),
            (r'<h2[^>]*>(.*?)</h2>', 'h2'),
            (r'<h3[^>]*>(.*?)</h3>', 'h3'),
            (r'<h4[^>]*>(.*?)</h4>', 'h4'),
            (r'<h5[^>]*>(.*?)</h5>', 'h5'),
            (r'<h6[^>]*>(.*?)</h6>', 'h6'),
            (r'<p[^>]*>(.*?)</p>', 'p'),
            (r'<code[^>]*>(.*?)</code>', 'code'),
            (r'<pre[^>]*>(.*?)</pre>', 'pre'),
            (r'<em[^>]*>(.*?)</em>', 'em'),
            (r'<strong[^>]*>(.*?)</strong>', 'strong'),
            (r'<blockquote[^>]*>(.*?)</blockquote>', 'blockquote')
        ]:
            for match in re.finditer(tag_pattern, html_content, re.DOTALL):
                content = match.group(1)
                start_idx = self.preview_text.search(
                    content, current_pos, 'end', regexp=False
                )
                if start_idx:
                    end_idx = f"{start_idx}+{len(content)}c"
                    self.preview_text.tag_add(tag_name, start_idx, end_idx)
        
        # Handle lists
        for list_match in re.finditer(r'<([ou]l)[^>]*>(.*?)</\1>', html_content, re.DOTALL):
            list_content = list_match.group(2)
            list_type = list_match.group(1)
            items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL)
            for i, item in enumerate(items, 1):
                bullet = '•' if list_type == 'ul' else f"{i}."
                self.preview_text.insert('end', f"{bullet} {item}\n")
        
        self.preview_text.config(state='disabled')

    def update_preview(self):
        # Get text from editor
        markdown_text = self.editor.get("1.0", "end-1c")

        # Create markdown instance with math extension
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'codehilite',
            'md_in_html',
            'sane_lists',
            MathExtension(enable_dollar_delimiter=True)
        ])

        if self.show_raw_html:
            # Show raw HTML with LaTeX
            html = md.convert(markdown_text)
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', html)
            self.preview_text.config(state='disabled')
        else:
            # Convert markdown to HTML and render
            html = md.convert(markdown_text)
            self.insert_html_content(html)

    def toggle_preview_mode(self):
        self.show_raw_html = not self.show_raw_html
        self.toggle_button.configure(text="Show Rendered HTML" if self.show_raw_html else "Show Raw HTML")
        self.update_preview()

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
                messagebox.showerror("Error", f"Error opening file: {e}")

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
                messagebox.showerror("Error", f"Error saving file: {e}")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    editor = MarkdownEditor()
    editor.run()