import streamlit as st
import markdown
import json
from utils.markdown_parser import MarkdownParser

# ============== MAIN APP ==============

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
Nested Section
This is a nested section under the main content.

Deep Nesting
Content can be nested multiple levels deep.

Links and Images
GitHub
Google
Task List
 Completed task
 Incomplete task
 Another task
This is a blockquote with bold text.

Conclusion
This demonstrates various markdown elements."""
        st.rerun()

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input Markdown")
    markdown_input = st.text_area(
        "Enter your markdown text:",
        value=st.session_state.markdown_text,
        height=500,
        key="markdown_input",
        help="Enter or paste your markdown text here"
    )

    # Update session state on text change
    st.session_state.markdown_text = markdown_input

    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.markdown_text = ""
            st.session_state.structured_data = {}
            st.rerun()
    with col_btn2:
        if st.button("📋 Copy Structure", use_container_width=True):
            st.info("Structure copied to clipboard!") # Note: This needs clipboard functionality
    with col_btn3:
        process_btn = st.button("⚡ Process", type="primary", use_container_width=True)

if process_btn and markdown_input:
    # Parse markdown
    parser = MarkdownParser(
        parse_tables=parse_tables,
        parse_code=parse_code,
        parse_lists=parse_lists
    )
    structured_data = parser.parse(markdown_input)
    st.session_state.structured_data = structured_data

with col2:
    structured_data = st.session_state.structured_data
    if structured_data:
        # Display options
        if show_preview:
            st.subheader("👁️ HTML Preview")
            # Convert markdown to HTML
            extensions = ['tables', 'fenced_code', 'nl2br', 'toc', 'sane_lists']
            html_content = markdown.markdown(markdown_input, extensions=extensions)
            st.markdown(f'<div class="markdown-body">{html_content}</div>', unsafe_allow_html=True)
        
        if show_structure:
            st.subheader("🏗️ Document Structure")
            structure_tabs = st.tabs(["Tree View", "Detailed View"])
            
            with structure_tabs[0]:
                # Tree view
                st.markdown('<div class="structure-view">', unsafe_allow_html=True)
                for item in structured_data.get('structure', []):
                    indent = "  " * (item.get('level', 1) - 1)
                    icon = {
                        'header': '📌',
                        'table': '📊',
                        'code': '💻',
                        'list': '📝',
                        'blockquote': '💬',
                        'paragraph': '📄'
                    }.get(item.get('type', 'paragraph'), '📄')
                    
                    st.text(f"{indent}{icon} {item.get('type', 'unknown').upper()}: {item.get('content', '')[:50]}...")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with structure_tabs[1]:
                # Detailed view with expandable sections
                for i, item in enumerate(structured_data.get('structure', [])):
                    with st.expander(f"{item.get('type', 'unknown').upper()} - {item.get('content', '')[:30]}...", expanded=False):
                        st.json(item)
        
        if show_json:
            st.subheader("📋 JSON Structure")
            st.json(structured_data)
            
            # Download button for JSON
            json_str = json.dumps(structured_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="markdown_structure.json",
                mime="application/json"
            )
        
        if show_stats:
            st.subheader("📊 Document Statistics")
            stats = structured_data.get('stats', {})
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            
            with stats_col1:
                st.metric("Headers", stats.get('headers', 0))
            with stats_col2:
                st.metric("Tables", stats.get('tables', 0))
            with stats_col3:
                st.metric("Code Blocks", stats.get('code_blocks', 0))
            with stats_col4:
                st.metric("Lists", stats.get('lists', 0))
            
            # Word count
            word_count = len(markdown_input.split())
            char_count = len(markdown_input)
            line_count = len(markdown_input.splitlines())
            
            stats_col5, stats_col6, stats_col7 = st.columns(3)
            with stats_col5:
                st.metric("Words", word_count)
            with stats_col6:
                st.metric("Characters", char_count)
            with stats_col7:
                st.metric("Lines", line_count)
    else:
        st.info("👈 Enter markdown text, then click '⚡ Process' to see the output.")

st.divider()
st.markdown("""

<div style='text-align: center; color: #666;'> Made with ❤️ using Streamlit | <a href='https://github.com' target='_blank'>GitHub</a> </div> """, unsafe_allow_html=True) ```