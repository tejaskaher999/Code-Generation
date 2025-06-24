from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import time
import sys
import logging
import webbrowser
import os
import tempfile
import html
import threading
from flask import Flask, render_template_string, request

# Initialize Flask app
app = Flask(__name__)
generated_code = ""
function_description = ""

# Global variables for model
tokenizer = None
model = None

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevGenius: Code Generation Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Favicon links -->
        <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
        <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
        <link rel="manifest" href="/static/site.webmanifest">
        <!-- Syntax highlighting -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/atom-one-dark.min.css" id="dark-highlight-theme">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css" id="light-highlight-theme" disabled>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            /* Light Theme Variables */
            :root.light-theme {
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --bg-color: #f5f5f5;
                --card-bg: #ffffff;
                --text-color: #333333;
                --border-color: #dddddd;
                --highlight-bg: #f0f7fb;
                --code-bg: #f8f8f8;
            }
            
            /* Dark Theme Variables */
            :root.dark-theme {
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-color: #e2e8f0;
                --border-color: #334155;
                --highlight-bg: #1a2234;
                --code-bg: #282c34;
            }
            
            /* Default to light theme */
            :root {
                --primary-color: #3498db;
                --secondary-color: #2ecc71;
                --bg-color: #f5f5f5;
                --card-bg: #ffffff;
                --text-color: #333333;
                --border-color: #dddddd;
                --highlight-bg: #f0f7fb;
                --code-bg: #f8f8f8;
            }
            
            body { 
                font-family: 'Segoe UI', 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                background-color: var(--bg-color);
                color: var(--text-color);
                min-height: 100vh;
                transition: all 0.3s ease;
            }
            
            h1 { 
                color: var(--text-color);
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 15px;
                margin-top: 0;
                font-weight: 600;
            }
            
            form {
                margin: 25px 0;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
                width: 100%;
            }
            
            input[type="text"] {
                flex: 1;
                padding: 12px 15px;
                border: 1px solid var(--border-color);
                border-radius: 6px;
                background-color: var(--card-bg);
                color: var(--text-color);
                font-size: 16px;
                transition: all 0.3s ease;
                outline: none;
            }
            
            input[type="text"]:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
            }
            
            button {
                padding: 12px 20px;
                background-color: var(--primary-color);
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
                font-size: 16px;
            }
            
            button:hover {
                background-color: #2980b9;
                transform: translateY(-2px);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            pre { 
                background-color: var(--code-bg);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                color: var(--text-color); 
                margin-bottom: 1.6em; 
                overflow: auto; 
                padding: 0;
                position: relative;
                transition: all 0.3s ease;
            }
            
            code {
                padding: 1.5em !important;
                display: block;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 14px;
                line-height: 1.6;
            }
            
            .container { 
                max-width: 900px;
                margin: 0 auto;
                background-color: var(--card-bg);
                padding: 30px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                margin-top: 40px;
                margin-bottom: 40px;
                transition: all 0.3s ease;
            }
            
            .examples {
                margin: 25px 0;
                padding: 15px;
                background-color: rgba(52, 152, 219, 0.1);
                border-left: 4px solid var(--primary-color);
                border-radius: 4px;
                transition: all 0.3s ease;
            }
            
            .examples ul {
                margin: 10px 0 0 0;
                padding-left: 20px;
            }
            
            .examples li {
                margin-bottom: 8px;
                cursor: pointer;
                transition: color 0.2s;
            }
            
            .examples li:hover {
                color: var(--primary-color);
            }
            
            .code-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                background-color: var(--highlight-bg);
                border-bottom: 1px solid var(--border-color);
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                transition: all 0.3s ease;
            }
            
            .code-header h2 {
                margin: 0;
                font-size: 16px;
                font-weight: 500;
            }
            
            .copy-button {
                background-color: transparent;
                border: 1px solid var(--border-color);
                color: var(--text-color);
                padding: 6px 12px;
                font-size: 13px;
                cursor: pointer;
                border-radius: 4px;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .copy-button:hover {
                background-color: rgba(127, 127, 127, 0.1);
                transform: none;
            }
            
            .save-info {
                font-size: 13px;
                color: var(--text-color);
                opacity: 0.7;
                margin-top: 10px;
                display: flex;
                align-items: center;
                gap: 5px;
                transition: all 0.3s ease;
            }
            
            .loader {
                display: none;
                border: 2px solid rgba(127, 127, 127, 0.1);
                border-top: 2px solid var(--secondary-color);
                border-radius: 50%;
                width: 16px;
                height: 16px;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            #generateBtn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            #generateBtn .loader {
                display: none;
            }
            
            #generateBtn.loading .loader {
                display: block;
            }
            
            .tag {
                display: inline-block;
                background-color: rgba(52, 152, 219, 0.2);
                color: var(--primary-color);
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-right: 5px;
                transition: all 0.3s ease;
            }
            
            .footer {
                text-align: center;
                margin-top: 20px;
                font-size: 13px;
                color: var(--text-color);
                opacity: 0.7;
                transition: all 0.3s ease;
            }
            
            /* Theme toggle */
            .theme-toggle {
                position: absolute;
                top: 20px;
                right: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 14px;
            }
            
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 50px;
                height: 24px;
            }
            
            .toggle-switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            
            .toggle-slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 24px;
            }
            
            .toggle-slider:before {
                position: absolute;
                content: "";
                height: 16px;
                width: 16px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }
            
            input:checked + .toggle-slider {
                background-color: var(--primary-color);
            }
            
            input:checked + .toggle-slider:before {
                transform: translateX(26px);
            }
            
            .theme-icon {
                font-size: 16px;
            }
            
            @media (max-width: 768px) {
                .container {
                    margin: 0;
                    padding: 20px;
                    border-radius: 0;
                    min-height: 100vh;
                }
                
                .input-group {
                    flex-direction: column;
                }
                
                input[type="text"], button {
                    width: 100%;
                }
                
                .theme-toggle {
                    position: relative;
                    top: auto;
                    right: auto;
                    justify-content: flex-end;
                    margin-bottom: 10px;
                }
            }

            /* Icons */
            .icon {
                display: inline-block;
                width: 16px;
                height: 16px;
                stroke-width: 0;
                stroke: currentColor;
                fill: currentColor;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="theme-toggle">
                <span class="theme-icon">☀️</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="themeToggle">
                    <span class="toggle-slider"></span>
                </label>
                <span class="theme-icon">🌙</span>
            </div>
            
            <h1>DevGenius: Code Generation Assistant</h1>
            
            <div class="examples">
                <p><strong>Example inputs:</strong></p>
                <ul>
                    <li onclick="fillExample(this)">create a function for sum of two numbers</li>
                    <li onclick="fillExample(this)">generate factorial function</li>
                    <li onclick="fillExample(this)">make a function to sort an array</li>
                    <li onclick="fillExample(this)">write a function to check if a string is a palindrome</li>
                </ul>
            </div>
            
            <form id="generateForm" action="/generate" method="post">
                <div class="input-group">
                    <input type="text" id="promptInput" name="prompt" placeholder="Enter function description..." required>
                    <button type="submit" id="generateBtn">
                        <span class="loader"></span>
                        Generate Code
                    </button>
                </div>
            </form>
            
            {% if code %}
                <div class="result-container">
                    <div class="code-header">
                        <h2>
                            <span class="tag">Python</span>
                            {{ description }}
                        </h2>
                        <div class="button-group">
                            <button id="copyButton" class="copy-button" onclick="copyCode()">
                                <svg class="icon" viewBox="0 0 24 24">
                                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                                </svg>
                                Copy
                            </button>
                        </div>
                    </div>
                    <pre><code class="language-python">{{ code }}</code></pre>
                    <div class="save-info">
                        <svg class="icon" viewBox="0 0 24 24">
                            <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>
                        </svg>
                        Code saved to results folder
                    </div>
                </div>
            {% endif %}
            
            <div class="footer">
                &copy; 2025 DevGenius: Code Generation Assistant | Powered by AI
            </div>
        </div>
        
        <script>
            // Theme switching
            const themeToggle = document.getElementById('themeToggle');
            const root = document.documentElement;
            const darkHighlightTheme = document.getElementById('dark-highlight-theme');
            const lightHighlightTheme = document.getElementById('light-highlight-theme');
            
            // Check for saved theme preference or use system preference
            const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            
            // Apply the saved theme
            if (savedTheme === 'dark') {
                root.classList.add('dark-theme');
                themeToggle.checked = true;
                darkHighlightTheme.disabled = false;
                lightHighlightTheme.disabled = true;
            } else {
                root.classList.add('light-theme');
                themeToggle.checked = false;
                darkHighlightTheme.disabled = true;
                lightHighlightTheme.disabled = false;
            }
            
            // Theme toggle event
            themeToggle.addEventListener('change', function() {
                if (this.checked) {
                    root.classList.remove('light-theme');
                    root.classList.add('dark-theme');
                    localStorage.setItem('theme', 'dark');
                    darkHighlightTheme.disabled = false;
                    lightHighlightTheme.disabled = true;
                } else {
                    root.classList.remove('dark-theme');
                    root.classList.add('light-theme');
                    localStorage.setItem('theme', 'light');
                    darkHighlightTheme.disabled = true;
                    lightHighlightTheme.disabled = false;
                }
                
                // Re-highlight the code when theme changes
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            });
            
            // Copy code function
            function copyCode() {
                const codeElement = document.querySelector('pre code');
                const textArea = document.createElement('textarea');
                textArea.value = codeElement.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const copyBtn = document.getElementById('copyButton');
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg> Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            }
            
            // Fill example
            function fillExample(element) {
                document.getElementById('promptInput').value = element.textContent;
            }
            
            // Show loading state
            document.getElementById('generateForm').addEventListener('submit', function() {
                document.getElementById('generateBtn').classList.add('loading');
            });
            
            // Highlight code on load
            document.addEventListener('DOMContentLoaded', (event) => {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            });
            
            // Handle keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter to submit form
                if (e.ctrlKey && e.key === 'Enter') {
                    document.getElementById('generateForm').submit();
                }
            });
        </script>
    </body>
    </html>
    ''', code=generated_code, description=function_description)

@app.route('/generate', methods=['POST'])
def generate():
    global generated_code, function_description
    
    user_input = request.form['prompt']
    function_description = user_input
    generated_code = generate_code(user_input)
    
    # Save the generated code to file
    save_path = save_generated_code(function_description, generated_code)
    
    return home()

def save_generated_code(description, code):
    """Save the generated code to a text file in the results folder"""
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create a sanitized filename based on the description
    # Remove special characters and spaces
    sanitized_name = ''.join(c if c.isalnum() else '_' for c in description.lower())
    sanitized_name = sanitized_name[:50]  # Limit length
    
    # Add timestamp to ensure unique filenames
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{sanitized_name}_{timestamp}.txt"
    
    # Full path to the file
    file_path = os.path.join(results_dir, filename)
    
    # Save the code to the file
    with open(file_path, 'w') as f:
        f.write(f"# Function: {description}\n")
        f.write(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(code)
    
    print(f"Generated code saved to: {file_path}")
    return file_path

def load_model_with_progress():
    global tokenizer, model
    
    # Disable logging
    logging.getLogger("transformers").setLevel(logging.ERROR)
    
    print("Loading AI model...")
    progress_bar = tqdm(total=100, desc="Loading", unit="%", ncols=75)
    
    try:
        # Load tokenizer (approximately 30% of progress)
        tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
        progress_bar.update(30)
        time.sleep(0.5) # Small delay for visual feedback
        
        # Load model (approximately 70% of progress)
        model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
        progress_bar.update(70)
        
        # Set pad token
        tokenizer.pad_token = tokenizer.eos_token
        
        progress_bar.close()
        print("\nModel loaded successfully!\n")
        
    except Exception as e:
        progress_bar.close()
        print(f"\nError loading model: {str(e)}")
        sys.exit(1)

def parse_description(description):
    """Convert natural language description to function signature"""
    description = description.lower()
    
    # Remove common words and convert to snake_case
    words = description.replace('create', '').replace('function', '').replace('for', '').strip()
    words = words.replace(' ', '_')
    
    # Default parameter 'x' if no specific parameters mentioned
    return f"{words}(x)"

# Define a function to generate code
def generate_code(prompt, max_length=150):
    # Convert natural language to function signature
    if not prompt.strip().startswith('def'):
        function_signature = parse_description(prompt)
        prompt = f"def {function_signature}:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        inputs['input_ids'], 
        max_length=max_length,
        pad_token_id=tokenizer.eos_token_id,
        num_return_sequences=1,
        temperature=0.7,
        do_sample=True,  # Enable sampling for more creative outputs
        top_p=0.95,      # Nucleus sampling
        top_k=50         # Top-k sampling
    )
    generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the function definition
    lines = generated_code.split('\n')
    result = []
    in_function = False
    
    for line in lines:
        if line.strip().startswith('def '):
            in_function = True
        if in_function and line.strip():
            result.append(line)
        if in_function and not line.strip():
            break
            
    # Check if we have a valid function
    if not result:
        return "# Could not generate valid function. Please try again with more specific description."
    
    return '\n'.join(result)

def start_flask_server():
    # Start Flask server on port 5000
    app.run(debug=False, port=5000)

def main():
    # Load the model first
    load_model_with_progress()
    
    # Start Flask server in a separate thread
    thread = threading.Thread(target=start_flask_server)
    thread.daemon = True
    thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Open browser to localhost
    print("Opening web interface at http://localhost:5000")
    webbrowser.open("http://localhost:5000")
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
