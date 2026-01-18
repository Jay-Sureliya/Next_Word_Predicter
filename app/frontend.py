import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Ghost Text Writer", page_icon="👻", layout="wide")

# API Address (Change if deployed remotely)
API_URL = "http://127.0.0.1:8000/autocomplete"

st.title("👻 Ghost Text Autocomplete")
st.markdown("Type below. When you see a **gray suggestion**, press **`Tab`** to accept it.")

# --- THE CUSTOM COMPONENT ---
# This HTML/JS block handles the real-time typing and ghost text overlay
editor_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    :root {{
        --bg-color: #1e1e1e;
        --text-color: #d4d4d4;
        --ghost-color: #6a6a6a;
        --font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        --font-size: 18px;
        --line-height: 1.5;
    }}
    
    body {{
        margin: 0;
        background-color: #0e1117; /* Matches Streamlit Dark Mode */
        font-family: sans-serif;
    }}

    .editor-container {{
        position: relative;
        width: 100%;
        height: 300px;
        background-color: var(--bg-color);
        border-radius: 8px;
        border: 1px solid #333;
        overflow: hidden;
    }}

    /* Common styles for both layers to ensure perfect alignment */
    .layer {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        padding: 15px;
        box-sizing: border-box;
        font-family: var(--font-family);
        font-size: var(--font-size);
        line-height: var(--line-height);
        white-space: pre-wrap;
        word-wrap: break-word;
        border: none;
        outline: none;
        resize: none;
        background: transparent;
        margin: 0;
    }}

    /* The Ghost Layer (Behind) - Shows text + gray suggestion */
    #ghost-layer {{
        z-index: 1;
        color: transparent; /* Main text invisible, only suggestion span visible */
    }}

    /* The Input Layer (Front) - User types here */
    #input-layer {{
        z-index: 2;
        color: var(--text-color);
        caret-color: white;
        background: transparent; /* See through to ghost layer */
    }}

    /* The style for the suggested word */
    .suggestion {{
        color: var(--ghost-color);
        opacity: 0.8;
    }}
</style>
</head>
<body>

<div class="editor-container">
    <div id="ghost-layer" class="layer"></div>
    <textarea id="input-layer" class="layer" placeholder="Start typing... (e.g., 'artificial')"></textarea>
</div>

<script>
    const inputLayer = document.getElementById('input-layer');
    const ghostLayer = document.getElementById('ghost-layer');
    let currentSuggestion = "";

    // 1. Listen for typing
    inputLayer.addEventListener('input', async (e) => {{
        const text = inputLayer.value;
        syncScroll();
        
        // Update ghost text base immediately (hide old suggestion)
        renderGhost(text, ""); 

        // Only fetch suggestion if ending with space and not empty
        if (text.length > 0 && (text.endsWith(" ") || text.length < 5)) {{
            const suggestion = await fetchSuggestion(text);
            if (suggestion) {{
                currentSuggestion = suggestion;
                renderGhost(text, suggestion);
            }}
        }} else {{
            currentSuggestion = "";
        }}
    }});

    // 2. Handle Tab Key
    inputLayer.addEventListener('keydown', (e) => {{
        if (e.key === 'Tab') {{
            e.preventDefault(); // Stop focus change
            if (currentSuggestion) {{
                // Accept suggestion
                inputLayer.value += currentSuggestion + " ";
                // Clear suggestion
                currentSuggestion = "";
                renderGhost(inputLayer.value, "");
                // Trigger input event manually
                inputLayer.dispatchEvent(new Event('input'));
            }}
        }}
    }});

    // 3. Sync Scrolling
    inputLayer.addEventListener('scroll', syncScroll);
    function syncScroll() {{
        ghostLayer.scrollTop = inputLayer.scrollTop;
        ghostLayer.scrollLeft = inputLayer.scrollLeft;
    }}

    // 4. Render Ghost Text
    function renderGhost(text, suggestion) {{
        // We make the main text transparent in CSS, but we need it here for spacing.
        // The span contains the suggestion in gray.
        const safeText = escapeHtml(text);
        ghostLayer.innerHTML = `<span style="color:transparent">${{safeText}}</span><span class="suggestion">${{suggestion}}</span>`;
    }}

    // 5. Fetch from API
    async function fetchSuggestion(text) {{
        try {{
            const response = await fetch('{API_URL}', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ text: text }})
            }});
            const data = await response.json();
            return data.suggestion;
        }} catch (err) {{
            console.error("API Error", err);
            return "";
        }}
    }}

    function escapeHtml(text) {{
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;")
            .replace(/\\n/g, "<br>");
    }}
</script>

</body>
</html>
"""

# Render the HTML component
components.html(editor_html, height=350)

# Note to user
st.info("💡 **Pro Tip:** This editor runs entirely in your browser! It connects directly to your local API for zero-latency predictions.")