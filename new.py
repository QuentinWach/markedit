import customtkinter as ctk
import markdown2
import webbrowser
from tkinter import filedialog
from tkinterweb import HtmlFrame
import re
import os

def math_preprocessor(text):
    """Pre-process math expressions before markdown conversion"""
    # Handle display math ($$...$$)
    def replace_display_math(match):
        math_content = match.group(1).strip()
        # Ensure proper spacing around display math
        return f'\n\n$${math_content}$$\n\n'

    # Handle inline math ($...$)
    def replace_inline_math(match):
        math_content = match.group(1).strip()
        return f'${math_content}$'

    # Replace display math first ($$...$$)
    text = re.sub(r'\$\$(.*?)\$\$', replace_display_math, text, flags=re.DOTALL)
    # Then replace inline math ($...$)
    text = re.sub(r'\$(.+?)\$', replace_inline_math, text)
    return text

class MarkdownEditor:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Markdown Editor")
        self.app.geometry("1200x800")
        
        # Get the absolute path to the static directory first
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        
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
        
        # Create preview containers
        self.preview_frame = ctk.CTkFrame(self.app)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        
        # HTML Preview (WebView)
        self.html_preview = HtmlFrame(self.preview_frame, messages_enabled=False)
        self.html_preview.grid(row=0, column=0, sticky="nsew")
        
        # Raw HTML Preview (Text)
        self.raw_preview = ctk.CTkTextbox(self.preview_frame, wrap="none")
        self.raw_preview.grid(row=0, column=0, sticky="nsew")
        self.raw_preview.grid_remove()  # Initially hidden
        
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

    def toggle_preview_mode(self):
        self.show_raw_html = not self.show_raw_html
        if self.show_raw_html:
            self.toggle_button.configure(text="Show Rendered HTML")
            self.html_preview.grid_remove()
            self.raw_preview.grid()
        else:
            self.toggle_button.configure(text="Show Raw HTML")
            self.raw_preview.grid_remove()
            self.html_preview.grid()

    def update_preview(self):
        # Get text from editor
        markdown_text = self.editor.get("1.0", "end-1c")
        
        # Pre-process the markdown to protect math expressions
        processed_text = math_preprocessor(markdown_text)
        
        # Convert markdown to HTML, but protect our math delimiters
        extras = {
            'fenced-code-blocks': None,
            'tables': None,
            'code-friendly': None  # This prevents markdown2 from processing underscores in math
        }
        html = markdown2.markdown(processed_text, extras=extras)
        
        # Create absolute paths for KaTeX files
        katex_css = os.path.join(self.static_dir, 'katex', 'katex.min.css').replace('\\', '/')
        katex_js = os.path.join(self.static_dir, 'katex', 'katex.min.js').replace('\\', '/')
        auto_render_js = os.path.join(self.static_dir, 'katex', 'contrib', 'auto-render.min.js').replace('\\', '/')
        
        # Debug output to check file paths and existence
        print("\nChecking KaTeX files:")
        print(f"Static directory: {self.static_dir}")
        print(f"CSS path: {katex_css}")
        print(f"CSS exists: {os.path.exists(katex_css)}")
        print(f"JS path: {katex_js}")
        print(f"JS exists: {os.path.exists(katex_js)}")
        print(f"Auto-render path: {auto_render_js}")
        print(f"Auto-render exists: {os.path.exists(auto_render_js)}")
        
        # Create a complete HTML document with KaTeX support
        full_html = f"""
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="file:///{katex_css}">
                <script src="file:///{katex_js}"></script>
                <script src="file:///{auto_render_js}"></script>
                
                <script>
                    window.addEventListener('load', function() {{
                        renderMathInElement(document.body, {{
                            delimiters: [
                                {{left: '$$', right: '$$', display: true}},
                                {{left: '$', right: '$', display: false}}
                            ],
                            throwOnError: false,
                            output: 'html',
                            strict: false
                        }});
                    }});
                </script>
                
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        padding: 20px;
                        max-width: 100px;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #333;
                        margin-top: 24px;
                        margin-bottom: 16px;
                    }}
                    code {{
                        background-color: #f6f8fa;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f6f8fa;
                        padding: 16px;
                        border-radius: 6px;
                        overflow: auto;
                    }}
                    .katex {{
                        font-size: 1.1em;
                    }}
                    .katex-display {{
                        overflow-x: auto;
                        overflow-y: hidden;
                        padding: 8px 0;
                        margin: 0.5em 0;
                    }}
                    .katex-display > .katex {{
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                {html}
                <script>
                    // Force KaTeX to reprocess after load
                    setTimeout(function() {{
                        if (typeof renderMathInElement !== 'undefined') {{
                            renderMathInElement(document.body, {{
                                delimiters: [
                                    {{left: '$$', right: '$$', display: true}},
                                    {{left: '$', right: '$', display: false}}
                                ],
                                throwOnError: false,
                                output: 'html',
                                strict: false
                            }});
                        }}
                    }}, 100);
                </script>
            </body>
        </html>
        """
        
        # Update both previews
        self.html_preview.load_html(full_html)
        
        # Update raw preview
        self.raw_preview.configure(state="normal")
        self.raw_preview.delete("1.0", "end")
        self.raw_preview.insert("1.0", full_html)
        self.raw_preview.configure(state="disabled")

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