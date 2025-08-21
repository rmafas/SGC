import streamlit as st
import re
from textblob import TextBlob
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Spell & Grammar Checker",
    page_icon="📝",
    layout="wide"
)

# Initialize tools
@st.cache_resource
def load_grammar_tool():
    """Load LanguageTool for grammar checking"""
    return language_tool_python.LanguageTool('en-US')

@st.cache_resource
def load_spell_checker():
    """Load PySpellChecker"""
    return SpellChecker()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .error-box {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .suggestion-box {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .stats-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>📝 Spell & Grammar Checker</h1><p>Enter your text below to check for spelling and grammar errors</p></div>', unsafe_allow_html=True)

# Sidebar for settings
st.sidebar.title("⚙️ Settings")
check_spelling = st.sidebar.checkbox("Check Spelling", value=True)
check_grammar = st.sidebar.checkbox("Check Grammar", value=True)
show_suggestions = st.sidebar.checkbox("Show Suggestions", value=True)
highlight_errors = st.sidebar.checkbox("Highlight Errors", value=True)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Text")
    user_text = st.text_area(
        "Enter your text here:",
        height=300,
        placeholder="Type or paste your text here to check for spelling and grammar errors..."
    )
    
    check_button = st.button("🔍 Check Text", type="primary", use_container_width=True)

with col2:
    st.subheader("✨ Results")
    
    if user_text and check_button:
        # Initialize results
        spelling_errors = []
        grammar_errors = []
        corrected_text = user_text
        
        # Text statistics
        word_count = len(user_text.split())
        char_count = len(user_text)
        sentence_count = len(re.findall(r'[.!?]+', user_text))
        
        # Display statistics
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Words", word_count)
        with stat_cols[1]:
            st.metric("Characters", char_count)
        with stat_cols[2]:
            st.metric("Sentences", sentence_count)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Spell checking
        if check_spelling and user_text.strip():
            try:
                spell_checker = load_spell_checker()
                words = re.findall(r'\b[a-zA-Z]+\b', user_text.lower())
                misspelled = spell_checker.unknown(words)
                
                for word in misspelled:
                    suggestions = list(spell_checker.candidates(word))[:3]
                    spelling_errors.append({
                        'word': word,
                        'type': 'Spelling',
                        'suggestions': suggestions
                    })
            except Exception as e:
                st.error(f"Spelling check error: {str(e)}")
        
        # Grammar checking
        if check_grammar and user_text.strip():
            try:
                # Use TextBlob for basic grammar correction
                blob = TextBlob(user_text)
                corrected_blob = blob.correct()
                
                # Find differences
                original_words = str(blob).split()
                corrected_words = str(corrected_blob).split()
                
                if len(original_words) == len(corrected_words):
                    for i, (orig, corr) in enumerate(zip(original_words, corrected_words)):
                        if orig.lower() != corr.lower():
                            grammar_errors.append({
                                'word': orig,
                                'type': 'Grammar',
                                'suggestions': [corr]
                            })
                
                corrected_text = str(corrected_blob)
                
            except Exception as e:
                st.error(f"Grammar check error: {str(e)}")
        
        # Display results
        total_errors = len(spelling_errors) + len(grammar_errors)
        
        if total_errors == 0:
            st.success("✅ No errors found! Your text looks good.")
        else:
            st.warning(f"⚠️ Found {total_errors} potential error(s)")
            
            # Display errors
            if spelling_errors:
                st.subheader("🔤 Spelling Errors")
                for error in spelling_errors:
                    st.markdown(f'<div class="error-box">', unsafe_allow_html=True)
                    st.write(f"**Word:** {error['word']}")
                    if show_suggestions and error['suggestions']:
                        st.write(f"**Suggestions:** {', '.join(error['suggestions'])}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if grammar_errors:
                st.subheader("📖 Grammar Corrections")
                for error in grammar_errors:
                    st.markdown(f'<div class="error-box">', unsafe_allow_html=True)
                    st.write(f"**Original:** {error['word']}")
                    if show_suggestions and error['suggestions']:
                        st.write(f"**Suggestion:** {', '.join(error['suggestions'])}")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Show corrected text
        if corrected_text != user_text:
            st.subheader("✏️ Suggested Correction")
            st.markdown(f'<div class="suggestion-box">', unsafe_allow_html=True)
            st.write(corrected_text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy button simulation
            st.text_area("Corrected text (copy this):", corrected_text, height=100)

# Instructions
st.markdown("---")
st.subheader("📖 How to Use")
st.markdown("""
1. **Enter your text** in the input area on the left
2. **Adjust settings** in the sidebar if needed
3. **Click 'Check Text'** to analyze your content
4. **Review results** on the right side showing:
   - Text statistics (word count, characters, sentences)
   - Spelling errors with suggestions
   - Grammar corrections
   - Suggested corrected text

**Features:**
- ✅ Real-time spell checking
- ✅ Grammar correction suggestions  
- ✅ Text statistics
- ✅ Customizable checking options
- ✅ Clean, user-friendly interface
""")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit • Powered by TextBlob and PySpellChecker")

# Required installations note
with st.expander("📦 Required Packages"):
    st.code("""
pip install streamlit
pip install textblob
pip install pyspellchecker
pip install language-tool-python
pip install pandas
    """, language="bash")
