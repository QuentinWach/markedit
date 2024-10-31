from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QTextEdit, QVBoxLayout, QHBoxLayout, QSplitter)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
import markdown
import sys

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Editor with LaTeX")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Create editor pane
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Enter Markdown text here...")
        self.editor.textChanged.connect(self.update_preview)
        splitter.addWidget(self.editor)

        # Create preview pane
        self.preview = QWebEngineView()
        splitter.addWidget(self.preview)

        # Set up initial HTML template with MathJax
        self.html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <script type="text/x-mathjax-config">
                MathJax.Hub.Config({{
                    tex2jax: {{
                        inlineMath: [['$','$'], ['\\(','\\)']],
                        processEscapes: true
                    }}
                }});
            </script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 100%;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                }
                code {
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        '''

        # Set initial preview
        self.update_preview()

    def update_preview(self):
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])
        content = md.convert(self.editor.toPlainText())
        
        # Insert content into HTML template
        html = self.html_template.format(content=content)
        
        # Update preview
        self.preview.setHtml(html)

def main():
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
