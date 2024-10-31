import tkinter as tk
from tkinter import scrolledtext
from tkhtmlview import HTMLLabel
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from mdx_math import MathExtension

class MarkdownEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Markdown Editor with LaTeX")
        
        # Create and pack the text input area
        self.text_input = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.text_input.pack(expand=True, fill='both', side='left')
        
        # Create and pack the preview area
        self.preview = HTMLLabel(self.master, html="<h1>Preview</h1>")
        self.preview.pack(expand=True, fill='both', side='right')
        
        # Bind the key release event to update preview
        self.text_input.bind('<KeyRelease>', self.update_preview)

    def update_preview(self, event=None):
        # Get the markdown text
        markdown_text = self.text_input.get('1.0', tk.END)
        
        # Convert markdown to HTML with LaTeX support
        html = markdown.markdown(markdown_text, extensions=[
            'markdown.extensions.extra',
            CodeHiliteExtension(),
            FencedCodeExtension(),
            MathExtension(enable_dollar_delimiter=True)
        ])
        
        # Add KaTeX resources and rendering script
        html_template = f"""
        <html>
        <head>
            <link rel="stylesheet" href="static/katex/katex.min.css">
            <script src="static/katex/katex.min.js"></script>
        </head>
        <body>
            {html}
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    var mathElements = document.getElementsByClassName("math");
                    for (var i = 0; i < mathElements.length; i++) {{
                        var texText = mathElements[i].firstChild.textContent;
                        if (mathElements[i].tagName == "SPAN") {{
                            katex.render(texText, mathElements[i]);
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.set_html(html_template)

if __name__ == "__main__":
    root = tk.Tk()
    editor = MarkdownEditor(root)
    root.geometry("800x600")
    root.mainloop()