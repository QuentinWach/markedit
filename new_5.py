import customtkinter as ctk
import markdown
from tkinter import filedialog
from tkinter import messagebox
from mdx_math import MathExtension
from tkhtmlview import HTMLLabel

class MarkdownEditor:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Markdown Editor")
        self.app.geometry("1200x800")
        
        # Fix HTML template by escaping curly braces in the MathJax config
        self.html_template = """
        <html>
        <head>
            <!--
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            -->
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/mathtex-script-type.min.js" defer></script>

            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    tex2jax: {{
                        inlineMath: [['$','$'], ['\\\\(','\\\\)']],
                        displayMath: [['$$','$$'], ['\\\\[','\\\\]']],
                        processEscapes: true
                    }}
                }});
            </script>
            <style>
                body {{ 
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: white;
                }}
                pre {{ 
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 4px;
                }}
                code {{ 
                    font-family: Courier, monospace;
                }}
                blockquote {{
                    border-left: 4px solid #ccc;
                    margin: 0;
                    padding-left: 16px;
                    font-style: italic;
                }}
            </style>
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
        
        # Create HTML preview widget
        self.preview_html = HTMLLabel(self.preview_frame, html="")
        self.preview_html.pack(fill="both", expand=True)
        
        # Sample text
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

    def insert_html_content(self, html_content):
        """Insert HTML content with MathJax support"""
        full_html = self.html_template.format(html_content)
        self.preview_html.set_html(full_html)

    def update_preview(self):
        # Get text from editor
        markdown_text = self.editor.get("1.0", "end-1c")

        # Create markdown instance with math extension
        md = markdown.Markdown(extensions=[MathExtension(enable_dollar_delimiter=True)])

        # Convert markdown to HTML
        html = md.convert(markdown_text)
        
        if self.show_raw_html:
            # Show raw HTML by escaping < and > characters
            escaped_html = html.replace('<', '&lt;').replace('>', '&gt;')
            self.preview_html.set_html(f"<pre style='background-color: #f0f0f0; padding: 10px; font-family: monospace;'>{escaped_html}</pre>")
        else:
            # Show rendered HTML with MathJax support
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