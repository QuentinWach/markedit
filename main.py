from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                           QTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFileDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QColor
import sys
import markdown
import os

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragPos = None
        self.maximizeButton = None
        self.load_styles()
        self.initUI()
        self.current_file = None  # Track current file

    def load_styles(self):
        # Load Qt stylesheet
        qt_style_path = os.path.join('styles', 'qt_style.qss')
        with open(qt_style_path, 'r') as f:
            self.qt_style = f.read()

        # Load HTML stylesheet
        html_style_path = os.path.join('styles', 'html_style.css')
        with open(html_style_path, 'r') as f:
            self.html_style = f.read()

    def initUI(self):
        self.setWindowTitle('Markdown Editor with Preview')
        
        # Apply Qt stylesheet
        self.setStyleSheet(self.qt_style)
        
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
            <style>
{style}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        '''
        
        # Set initial size of the window
        self.resize(1200, 800)
        
        # Set some initial markdown content
        initial_markdown = r"""# Welcome to Markdown Editor

## Math Equations Example

The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$

### Display Math
Maxwell's Equations:

$$
\\begin{aligned}
\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0} \\\\\\
\\nabla \\cdot \\mathbf{B} &= 0 \\\\\\
\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\\\
\\nabla \\times \\mathbf{B} &= \\mu_0\\mathbf{J} + \\mu_0\\epsilon_0\\frac{\\partial \\mathbf{E}}{\\partial t}
\\end{aligned}
$$

## Regular Markdown

You can write:
- Lists
- *Italic text*
- **Bold text**
- [Links](https://example.com)

> This is a blockquote

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`
"""
        self.editor.setText(initial_markdown)

        # Create a custom title bar
        titleBar = QWidget(self)
        titleBar.setObjectName("titleBar")
        titleBarLayout = QHBoxLayout(titleBar)
        titleBarLayout.setContentsMargins(5, 2, 5, 2)
        titleBarLayout.setSpacing(4)
        
        # Add title label with smaller font
        titleLabel = QLabel("Markdown Editor", titleBar)
        titleLabel.setStyleSheet("color: #e0e0e0; font-size: 11px; padding-left: 3px;")
        
        # Add window control buttons with smaller size
        minimizeButton = QPushButton("−", titleBar)
        minimizeButton.setObjectName("minimizeButton")
        minimizeButton.setFixedSize(16, 16)
        minimizeButton.clicked.connect(self.showMinimized)
        
        # Initialize maximizeButton properly
        self.maximizeButton = QPushButton("□", titleBar)
        self.maximizeButton.setObjectName("maximizeButton")
        self.maximizeButton.setFixedSize(16, 16)
        self.maximizeButton.clicked.connect(self.toggleMaximized)
        
        closeButton = QPushButton("×", titleBar)
        closeButton.setObjectName("closeButton")
        closeButton.setFixedSize(16, 16)
        closeButton.clicked.connect(self.close)
        
        titleBarLayout.addWidget(titleLabel)
        titleBarLayout.addStretch()
        titleBarLayout.addWidget(minimizeButton)
        titleBarLayout.addWidget(self.maximizeButton)
        titleBarLayout.addWidget(closeButton)
        
        # Add the title bar to the main layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(titleBar)
        
        # Create toolbar
        toolBar = QWidget()
        toolBar.setObjectName("toolBar")
        toolBarLayout = QHBoxLayout(toolBar)
        toolBarLayout.setContentsMargins(5, 2, 5, 2)
        toolBarLayout.setSpacing(4)

        # Create toolbar buttons
        openButton = QPushButton("Open", toolBar)
        openButton.setObjectName("toolBarButton")
        openButton.clicked.connect(self.open_file)

        saveButton = QPushButton("Save", toolBar)
        saveButton.setObjectName("toolBarButton")
        saveButton.clicked.connect(self.save_file)

        #saveAsButton = QPushButton("Save As", toolBar)
        #saveAsButton.setObjectName("toolBarButton")
        #saveAsButton.clicked.connect(self.save_file_as)

        # Add buttons to toolbar
        toolBarLayout.addWidget(openButton)
        toolBarLayout.addWidget(saveButton)
        #toolBarLayout.addWidget(saveAsButton)
        toolBarLayout.addStretch()

        # Modify main layout to include toolbar
        mainLayout.addWidget(toolBar)  # Add toolbar below titleBar
        mainLayout.addWidget(splitter)
        
        # Set the main layout
        centralWidget = QWidget()
        centralWidget.setObjectName("centralWidget")
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def toggleMaximized(self):
        if self.isMaximized():
            self.showNormal()
            self.maximizeButton.setText("□")
        else:
            self.showMaximized()
            self.maximizeButton.setText("❐")

    def update_preview(self):
        # Convert markdown to HTML
        markdown_text = self.editor.toPlainText()
        html_content = markdown.markdown(markdown_text, extensions=['fenced_code', 'codehilite'])
        
        # Insert both the style and HTML content into the base template
        full_html = self.base_html.format(
            style=self.html_style,
            content=html_content
        )
        
        # Update the preview
        self.preview.setHtml(full_html)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "deck",  # Default to deck directory
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.current_file = file_path
            with open(file_path, 'r', encoding='utf-8') as file:
                self.editor.setText(file.read())

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "deck",  # Default to deck directory
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.current_file = file_path
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())