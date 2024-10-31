from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys

# Define HTML content as a string
html_content = r"""
<html>
<head>
    <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
                inlineMath: [['$','$'], ['\\(','\\)']],
                displayMath: [['$$','$$'], ['\\[','\\]']],
                processEscapes: true
            }
        });
    </script>
</head>
<body>
    <h1 style="color: blue;">Math Equations Example</h1>
    
    <h2>Inline Math</h2>
    <p>The quadratic formula is \(x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\)</p>
    
    <h2>Display Math</h2>
    <p>Maxwell's Equations:</p>
    \[
    \begin{aligned}
    \nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\
    \nabla \cdot \mathbf{B} &= 0 \\
    \nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
    \nabla \times \mathbf{B} &= \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}
    \end{aligned}
    \]
    
    <h2>More Examples</h2>
    <p>The Euler's identity: \(e^{i\pi} + 1 = 0\)</p>
    
    <p>The integral of \(x^2\):</p>
    \[\int x^2 dx = \frac{x^3}{3} + C\]
</body>
</html>
"""

app = QApplication(sys.argv)
web = QWebEngineView()
web.setHtml(html_content)
web.show()
web.resize(800, 600)
sys.exit(app.exec_())