"""
Custom Navbar Component
"""
import streamlit as st

def render_navbar():
    """Render custom navbar dengan HTML/CSS"""
    
    st.markdown("""
    <style>
        .navbar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            color: white !important;
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .nav-link {
            color: white !important;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .nav-link:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .nav-link.active {
            background: rgba(255,255,255,0.3);
            font-weight: bold;
        }
    </style>
    
    <div class="navbar">
        <div class="navbar-brand">🧬 Genetic Scheduler</div>
        <div class="nav-links">
            <a href="/" class="nav-link" target="_self">🏠 Home</a>
            <a href="/Input_Data" class="nav-link" target="_self">📊 Input Data</a>
            <a href="/Run_Algorithm" class="nav-link" target="_self">🧬 Run Algorithm</a>
            <a href="/Results" class="nav-link" target="_self">📈 Results</a>
            <a href="/Settings" class="nav-link" target="_self">⚙️ Settings</a>
        </div>
    </div>
    """, unsafe_allow_html=True)