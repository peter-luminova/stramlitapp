import streamlit as st
import markdown
from markdown.extensions import tables, fenced_code, toc
import pandas as pd
from utils.markdown_parser import MarkdownParser
import json

# Page configuration
st.set_page_config(
    page_title="Markdown Structure Converter",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .markdown-body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        line-height: 1.6;
        padding: 20px;
        background-color: #f6f8fa;
        border-radius: 10px;
    }
    .structure-view {
        background-color: #2b2b2b;
        color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    h1 { color: #0366d6; }
    h2 { color: #28a745; }
    h3 { color: #6f42c1; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
    }
    th, td {
        border: 1px solid #dfe2e5;
        padding: 6px 13px;
        text-align: left;
    }
    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }
    code {
        background-color: #f6f8fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 85%;
    }
    pre {
        background-color: #f6f8fa;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'markdown_text' not in st.session_state:
    st.session_state.markdown_text = ""
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = {}

# Header
st.title("📝 Markdown Structure Converter")
st.markdown("Convert Markdown text into structured format with live preview")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("Display Options")
    show_preview = st.checkbox("Show HTML Preview", value=True)
    show_structure = st.checkbox("Show Document Structure", value=True)
    show_json = st.checkbox("Show JSON Structure", value=False)
    show_stats = st.checkbox("Show Statistics", value=True)
    
    st.subheader("Parser Options")
    parse_tables = st.checkbox("Parse Tables", value=True)
    parse_code = st.checkbox("Parse Code Blocks", value=True)
    parse_lists = st.checkbox("Parse Lists", value=True)
    
    st.divider()
    
    # Sample markdown
    if st.button("Load Sample Markdown"):
        st.session_state.markdown_text = """# Main Title

## Introduction
This is a **sample** markdown document with various elements.

### Features
- First item
- Second item with *italic* text
- Third item with `inline code`

## Table Example

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
    ```
"""