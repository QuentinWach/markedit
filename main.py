import customtkinter
import markdown2
from tkinter import font, Label
from tkhtmlview import HTMLLabel

def format_text_with_html(text):
    # Convert markdown to HTML first
    html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
    
    # Wrap the HTML with MathJax support
    full_html = f"""
    <html>
    <head>
        <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['$', '$']],
                    displayMath: [['$$', '$$']]
                }},
                svg: {{
                    fontCache: 'global',
                    scale: 1,
                    color: 'white'
                }}
            }};
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        <style>
            :root {{
                color-scheme: dark;
            }}
            body {{
                font-family: Helvetica;
                font-size: 14px;
                margin: 10px;
                padding: 0;
                background-color: {app._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"])};
                color: white;
            }}
            * {{
                color: white !important;
            }}
            p {{
                margin: 0;
                padding: 0;
                color: white !important;
            }}
            .mjx-svg-display {{
                filter: invert(1) !important;
            }}
            .mjx-math svg {{
                filter: invert(1) !important;
            }}
            strong {{
                font-weight: bold;
                color: white !important;
            }}
            em {{
                font-style: italic;
                color: white !important;
            }}
            li {{
                color: white !important;
            }}
            ul {{
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: white !important;
                margin: 10px 0;
            }}
            code {{
                background-color: #2d2d2d;
                padding: 2px 4px;
                border-radius: 3px;
                color: #e6e6e6 !important;
            }}
            pre {{
                background-color: #2d2d2d;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                margin: 10px 0;
            }}
            th, td {{
                border: 1px solid white;
                padding: 5px;
                color: white !important;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return full_html

def create_preview_label(parent, html_content):
    preview = HTMLLabel(
        parent,
        html=html_content,
        width=450,
        height=280,
        padx=10,
        pady=10,
        background=app._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkTextbox"]["fg_color"]),
        fg="white"
    )
    preview.configure(
        borderwidth=0,
        highlightthickness=0
    )
    return preview

def button_callback():
    print("Adding card to deck...")
    print(f"Front text: {front_entry.get('1.0', 'end-1c')}")
    print(f"Back text: {back_entry.get('1.0', 'end-1c')}")

def toggle_preview():
    global preview_mode, front_preview_label, back_preview_label
    preview_mode = not preview_mode
    
    if preview_mode:
        # Switch to preview mode
        preview_button.configure(text="Edit")
        front_entry.pack_forget()
        back_entry.pack_forget()
        
        # Create new preview labels with rendered content
        front_html = format_text_with_html(front_entry.get("1.0", "end-1c"))
        back_html = format_text_with_html(back_entry.get("1.0", "end-1c"))
        
        front_preview_label = create_preview_label(app, front_html)
        back_preview_label = create_preview_label(app, back_html)
        
        front_preview_label.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        back_preview_label.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
    else:
        # Switch back to edit mode
        preview_button.configure(text="Preview")
        
        # Remove preview labels
        if 'front_preview_label' in globals():
            front_preview_label.destroy()
        if 'back_preview_label' in globals():
            back_preview_label.destroy()
        
        # Show text entry boxes
        front_entry.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        back_entry.pack(padx=20, pady=(0, 20), fill="both", expand=True)

app = customtkinter.CTk()
app.geometry("500x800")

# Create a custom font for the textboxes
text_font = customtkinter.CTkFont(family="Helvetica", size=14)

preview_mode = False

front_label = customtkinter.CTkLabel(app, text="Front of card")
front_label.pack(padx=20, pady=(20, 0))

# Text entry for front
front_entry = customtkinter.CTkTextbox(app, width=450, height=280)
front_entry.pack(padx=20, pady=(0, 20), fill="both", expand=True)
front_entry.configure(font=text_font)
front_entry.insert("1.0", "Enter markdown and LaTeX here...\nExample: **bold** and _italic_\nMath: $x^2$ or $$\\sum_{i=1}^n i$$")

back_label = customtkinter.CTkLabel(app, text="Back of card")
back_label.pack(padx=20, pady=(20, 0))

# Text entry for back
back_entry = customtkinter.CTkTextbox(app, width=450, height=280)
back_entry.pack(padx=20, pady=(0, 20), fill="both", expand=True)
back_entry.configure(font=text_font)
back_entry.insert("1.0", "More examples:\n**Bold text** and _italic text_\nMath: $\\alpha = \\beta$ or $$E = mc^2$$\n\n- List item 1\n- List item 2")

# Create a frame for buttons
button_frame = customtkinter.CTkFrame(app)
button_frame.pack(padx=20, pady=20)

# Add both buttons side by side
button = customtkinter.CTkButton(button_frame, text="Add card", command=button_callback)
button.pack(side="left", padx=10)

preview_button = customtkinter.CTkButton(button_frame, text="Preview", command=toggle_preview)
preview_button.pack(side="left", padx=10)

app.mainloop()