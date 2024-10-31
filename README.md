# Markdown Editor with Local KaTeX Support

## Setup Instructions

1. Download KaTeX:
   - Go to https://github.com/KaTeX/KaTeX/releases/
   - Download the latest release zip file (e.g., katex.tar.gz)

2. Set up the static files:
   - Create a `static` folder in the project directory
   - Extract the KaTeX files into `static/katex/`
   - Ensure you have the following structure:
     ```
     static/
     └── katex/
         ├── katex.min.js
         ├── katex.min.css
         ├── contrib/
         │   └── auto-render.min.js
         └── fonts/
     ```

3. Install Python dependencies:
   ```bash
   pip install customtkinter markdown2 tkinterweb
   ```

4. Run the application:
   ```bash
   python new.py
   ```