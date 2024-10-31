from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                           QTextEdit, QWidget, QVBoxLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
import sys
import markdown

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Markdown Editor with Preview')
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create splitter for side-by-side layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Create text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Enter Markdown text here...")
        self.editor.textChanged.connect(self.update_preview)
        
        # Create web view for preview
        self.preview = QWebEngineView()
        
        # Add widgets to splitter
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        
        # Set initial sizes for splitter
        splitter.setSizes([400, 400])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Set initial HTML content with MathJax configuration
        self.base_html = '''
        <html>
        <head>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    tex2jax: {{
                        inlineMath: [['$','$'], ['\\(','\\)']],
                        displayMath: [['$$','$$'], ['\\[','\\]']],
                        processEscapes: true
                    }}
                }});
            </script>
        </head>
        <body>
            {content}
        </body>
        </html>
        '''
        
        # Set initial size of the window
        self.resize(1200, 800)
        
        # Set some initial markdown content
        initial_markdown = """# Welcome to Markdown Editor

## Math Equations Example

The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$

### Display Math
Maxwell's Equations:

$$
\\begin{aligned}
\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0} \\\\
\\nabla \\cdot \\mathbf{B} &= 0 \\\\
\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\
\\nabla \\times \\mathbf{B} &= \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}
\\end{aligned}
$$

## Regular Markdown

You can write:
- Lists
- *Italic text*
- **Bold text**
- [Links](https://example.com)
"""
        self.editor.setText(initial_markdown)

    def update_preview(self):
        # Convert markdown to HTML
        markdown_text = self.editor.toPlainText()
        html_content = markdown.markdown(markdown_text)
        
        # Insert the HTML content into the base template
        full_html = self.base_html.format(content=html_content)
        
        # Update the preview
        self.preview.setHtml(full_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())