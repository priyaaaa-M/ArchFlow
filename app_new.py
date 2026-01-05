import streamlit as st
import requests
import time
import json
from datetime import datetime
import base64
from pathlib import Path
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas

# Page config
st.set_page_config(
    page_title="System Design Generator",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend config
BACKEND_URL = "http://127.0.0.1:8000"

# CSS for clean layout
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.main { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }

/* Compact header */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    text-align: center;
}

.header h1 {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.header p {
    color: rgba(255,255,255,0.8);
    margin: 0.5rem 0 0 0;
    font-size: 0.9rem;
}

/* Layout containers */
.control-panel {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    height: fit-content;
}

.canvas-panel {
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    height: 600px;
}

/* Form elements */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
}

.stSelectbox > div > div > select {
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    width: 100%;
}

.download-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    margin: 0.5rem 0;
}

.edit-btn {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
}

/* Canvas tools */
.canvas-tools {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.5rem;
    background: #f1f5f9;
    border-radius: 8px;
}

.tool-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
}

.tool-btn.active {
    background: #667eea;
    color: white;
}

/* Status indicators */
.status-queued { color: #f59e0b; }
.status-running { color: #3b82f6; }
.status-completed { color: #10b981; }
.status-failed { color: #ef4444; }

</style>
""", unsafe_allow_html=True)

# Helper functions
def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_job(title, design_type, custom_urls=None):
    try:
        payload = {
            "title": title,
            "type": design_type,
            "custom_urls": custom_urls or []
        }
        response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_job_status(job_id):
    try:
        response = requests.get(f"{BACKEND_URL}/status/{job_id}", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_job_result(job_id):
    try:
        response = requests.get(f"{BACKEND_URL}/result/{job_id}", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def download_image(filename):
    try:
        response = requests.get(f"{BACKEND_URL}/files/{filename}", timeout=10)
        return response.content if response.status_code == 200 else None
    except:
        return None

# Initialize session state
if 'current_job_id' not in st.session_state:
    st.session_state.current_job_id = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = 0

# Header
st.markdown("""
<div class="header">
    <h1>🛠️ System Design Generator</h1>
    <p>AI-Powered Architecture Diagrams | Team Quirkless Code</p>
</div>
""", unsafe_allow_html=True)

# Main layout - two columns
col1, col2 = st.columns([1, 2])

# Left column - Controls
with col1:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    st.markdown("### Generate Diagram")
    
    # Check backend status
    if not check_backend():
        st.error("⚠️ Backend not running. Please start the backend server.")
        st.stop()
    
    # Input form
    with st.form("generate_form"):
        title = st.text_input("System Title", placeholder="e.g., Netflix Streaming Architecture")
        design_type = st.selectbox("Design Type", ["HLD", "LLD"])
        
        # Advanced options
        with st.expander("Advanced Options"):
            custom_urls = st.text_area(
                "Custom URLs (optional)", 
                placeholder="Enter URLs separated by newlines",
                height=100
            )
        
        submitted = st.form_submit_button("Generate Diagram")
    
    # Handle form submission
    if submitted and title:
        urls_list = [url.strip() for url in custom_urls.split('\n') if url.strip()] if custom_urls else None
        
        with st.spinner("Creating job..."):
            job_data = create_job(title, design_type, urls_list)
            
        if job_data:
            st.session_state.current_job_id = job_data['job_id']
            st.success(f"Job created: {job_data['job_id'][:8]}...")
        else:
            st.error("Failed to create job")
    
    # Job monitoring
    if st.session_state.current_job_id:
        st.markdown("### Job Status")
        
        # Auto-refresh for running jobs
        status_data = get_job_status(st.session_state.current_job_id)
        
        if status_data:
            status = status_data['status']
            
            # Status indicator
            status_colors = {
                'queued': '🟡',
                'running': '🔵', 
                'completed': '🟢',
                'failed': '🔴'
            }
            
            st.markdown(f"{status_colors.get(status, '⚪')} **Status:** {status.title()}")
            
            if status == 'running':
                st.info("Processing... This may take 60-120 seconds")
                time.sleep(2)
                st.rerun()
            
            elif status == 'completed':
                st.success("✅ Diagram generated successfully!")
                
                # Get results and load image
                result_data = get_job_result(st.session_state.current_job_id)
                if result_data and 'png_file' in result_data:
                    image_data = download_image(result_data['png_file'])
                    if image_data:
                        st.session_state.generated_image = Image.open(io.BytesIO(image_data))
                        
                        # Download original PNG
                        st.download_button(
                            "📥 Download Original PNG",
                            data=image_data,
                            file_name=f"{title.replace(' ', '_')}_diagram.png",
                            mime="image/png",
                            key="download_original"
                        )
            
            elif status == 'failed':
                st.error("❌ Job failed. Please try again.")
        
        # Clear job button
        if st.button("🔄 New Diagram"):
            st.session_state.current_job_id = None
            st.session_state.generated_image = None
            st.session_state.canvas_key += 1
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Right column - Canvas
with col2:
    st.markdown('<div class="canvas-panel">', unsafe_allow_html=True)
    
    st.markdown("### Interactive Canvas")
    
    # Canvas tools
    col_tool1, col_tool2, col_tool3, col_tool4 = st.columns(4)
    
    with col_tool1:
        drawing_mode = st.selectbox("Tool", ["freedraw", "line", "rect", "circle", "transform"])
    
    with col_tool2:
        stroke_width = st.slider("Brush Size", 1, 25, 3)
    
    with col_tool3:
        stroke_color = st.color_picker("Color", "#000000")
    
    with col_tool4:
        if st.button("🗑️ Clear"):
            st.session_state.canvas_key += 1
            st.rerun()
    
    # Background image (generated diagram)
    bg_image = st.session_state.generated_image if st.session_state.generated_image else None
    
    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#ffffff",
        background_image=bg_image,
        update_streamlit=True,
        height=400,
        width=700,
        drawing_mode=drawing_mode,
        point_display_radius=0,
        key=f"canvas_{st.session_state.canvas_key}",
    )
    
    # Canvas download options
    if canvas_result.image_data is not None:
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # Convert canvas to PNG
            canvas_img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            canvas_buffer = io.BytesIO()
            canvas_img.save(canvas_buffer, format='PNG')
            canvas_bytes = canvas_buffer.getvalue()
            
            st.download_button(
                "🎨 Download Edited Canvas",
                data=canvas_bytes,
                file_name="edited_diagram.png",
                mime="image/png",
                key="download_canvas"
            )
        
        with col_dl2:
            if st.button("💾 Save to Gallery"):
                st.success("Saved to gallery! (Feature coming soon)")
    
    # Instructions
    if not st.session_state.generated_image:
        st.info("""
        📝 **How to use:**
        1. Enter a system title on the left
        2. Click 'Generate Diagram' 
        3. Wait for AI to create your diagram
        4. Edit the diagram here with drawing tools
        5. Download your customized version
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ by Team Quirkless Code*")