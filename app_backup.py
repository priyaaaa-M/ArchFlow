import streamlit as st
import requests
import time
import json
from datetime import datetime
import base64
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="System Design Generator | Quirkless Code",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- BACKEND CONFIG ----------------
BACKEND_URL = "http://127.0.0.1:8000"

# ---------------- CSS STYLING ----------------
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
.main { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

/* Header Styles */
.main-header {
    background: linear-gradient(135deg, #FF6B35, #F7931E);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
}

.main-title {
    color: white;
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-subtitle {
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-top: 0.5rem;
    font-weight: 400;
}

/* Sidebar Styles */
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #2C3E50, #34495E);
    border-radius: 15px;
    padding: 1.5rem;
}

/* Card Styles */
.status-card {
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border-left: 5px solid #FF6B35;
}

.preview-card {
    background: rgba(255,255,255,0.98);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    position: relative;
    margin: 2rem 0;
}

/* Button Styles */
.stButton > button {
    background: linear-gradient(135deg, #FF6B35, #F7931E) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6) !important;
}

/* Download Button Styles */
.stDownloadButton > button {
    background: linear-gradient(135deg, #28a745, #20c997) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 500 !important;
    margin: 0.25rem !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4) !important;
}

/* Progress Styles */
.progress-container {
    background: rgba(255,255,255,0.9);
    border-radius: 15px;
    padding: 2rem;
    margin: 1rem 0;
    text-align: center;
}

.progress-step {
    display: inline-block;
    margin: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(255, 107, 53, 0.1);
    border-radius: 20px;
    font-size: 0.9rem;
    color: #FF6B35;
    font-weight: 500;
}

.progress-step.active {
    background: #FF6B35;
    color: white;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

/* Image Styles */
.diagram-image {
    max-width: 100%;
    height: auto;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    margin: 1rem 0;
}

/* Stats Styles */
.stats-container {
    display: flex;
    justify-content: space-around;
    margin: 1rem 0;
}

.stat-item {
    text-align: center;
    padding: 1rem;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    color: white;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #FF6B35;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
}

/* Alert Styles */
.success-alert {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.error-alert {
    background: linear-gradient(135deg, #dc3545, #c82333);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

/* Loading Animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,107,53,0.3);
    border-radius: 50%;
    border-top-color: #FF6B35;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-title { font-size: 2rem; }
    .main-subtitle { font-size: 1rem; }
    .stats-container { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------
def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_job(title, design_type):
    """Create a new job in the backend"""
    try:
        # Convert design type
        job_type = "HLD" if "HLD" in design_type else "LLD"
        
        response = requests.post(
            f"{BACKEND_URL}/generate",
            json={"title": title, "type": job_type},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to create job: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error creating job: {e}")
        return None

def check_job_status(job_id):
    """Check job status"""
    try:
        response = requests.get(f"{BACKEND_URL}/status/{job_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_job_result(job_id):
    """Get job result"""
    try:
        response = requests.get(f"{BACKEND_URL}/result/{job_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_png_from_url(png_url):
    """Download PNG from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}{png_url}", timeout=10)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# ---------------- SESSION STATE ----------------
if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "job_status" not in st.session_state:
    st.session_state.job_status = None
if "result_data" not in st.session_state:
    st.session_state.result_data = None
if "png_data" not in st.session_state:
    st.session_state.png_data = None

# ---------------- MAIN HEADER ----------------
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛠️ System Design Generator</h1>
    <p class="main-subtitle">AI-Powered Architecture Diagrams | Team Quirkless Code</p>
</div>
""", unsafe_allow_html=True)

# ---------------- BACKEND STATUS CHECK ----------------
backend_status = check_backend_health()

if not backend_status:
    st.markdown("""
    <div class="error-alert">
        ⚠️ <strong>Backend Not Running</strong><br>
        Please start the FastAPI server:<br>
        <code>uv run uvicorn api:app --reload --host 127.0.0.1 --port 8000</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 🎯 Generate System Design")
    
    system_title = st.text_input(
        "System Title",
        placeholder="e.g., UBER Backend System",
        help="Enter the name of the system you want to design"
    )
    
    design_type = st.selectbox(
        "Design Type",
        ["HLD (High Level Design)", "LLD (Low Level Design)"],
        help="Choose the level of detail for your diagram"
    )
    
    # Custom URLs (optional)
    with st.expander("🔗 Custom URLs (Optional)"):
        st.info("Leave empty to auto-discover URLs")
        custom_urls = st.text_area(
            "URLs (one per line)",
            placeholder="https://example.com/article1\nhttps://example.com/article2",
            height=100
        )
    
    generate_btn = st.button("🚀 Generate Diagram", use_container_width=True)
    
    st.divider()
    
    # Backend Stats
    try:
        stats_response = requests.get(f"{BACKEND_URL}/jobs/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            st.markdown("### 📊 System Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Jobs", stats.get('total', 0))
                st.metric("Completed", stats.get('completed', 0))
            with col2:
                st.metric("Failed", stats.get('failed', 0))
                st.metric("Running", stats.get('running', 0))
    except:
        pass

# ---------------- GENERATE LOGIC ----------------
if generate_btn and system_title.strip():
    # Parse custom URLs
    urls = None
    if custom_urls.strip():
        urls = [url.strip() for url in custom_urls.strip().split('\n') if url.strip()]
    
    # Create job
    job_data = create_job(system_title, design_type)
    
    if job_data:
        st.session_state.job_id = job_data["job_id"]
        st.session_state.job_status = "queued"
        st.session_state.result_data = None
        st.session_state.png_data = None
        st.rerun()

# ---------------- JOB MONITORING ----------------
if st.session_state.job_id:
    job_status = check_job_status(st.session_state.job_id)
    
    if job_status:
        current_status = job_status.get("status", "unknown")
        
        # Progress indicator
        st.markdown("""
        <div class="progress-container">
            <h3>🔄 Processing Your System Design</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress steps
        steps = ["queued", "running", "completed"]
        step_labels = ["📝 Queued", "🔄 Processing", "✅ Completed"]
        
        cols = st.columns(3)
        for i, (step, label) in enumerate(zip(steps, step_labels)):
            with cols[i]:
                if current_status == step:
                    st.markdown(f'<div class="progress-step active">{label}</div>', unsafe_allow_html=True)
                elif steps.index(current_status) > i if current_status in steps else False:
                    st.markdown(f'<div class="progress-step" style="background: #28a745; color: white;">{label}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="progress-step">{label}</div>', unsafe_allow_html=True)
        
        # Status details
        st.markdown(f"""
        <div class="status-card">
            <strong>Job ID:</strong> {st.session_state.job_id[:8]}...<br>
            <strong>Title:</strong> {job_status.get('title', 'N/A')}<br>
            <strong>Type:</strong> {job_status.get('type', 'N/A')}<br>
            <strong>Status:</strong> {current_status.title()}<br>
            <strong>Created:</strong> {job_status.get('created_at', 'N/A')[:19].replace('T', ' ')}
        </div>
        """, unsafe_allow_html=True)
        
        # Handle different statuses
        if current_status == "completed":
            # Get results
            result_data = get_job_result(st.session_state.job_id)
            
            if result_data:
                st.session_state.result_data = result_data
                
                # Download PNG
                png_url = result_data.get('png_url')
                if png_url and not st.session_state.png_data:
                    png_data = get_png_from_url(png_url)
                    if png_data:
                        st.session_state.png_data = png_data
                
                # Success message
                st.markdown("""
                <div class="success-alert">
                    🎉 <strong>Diagram Generated Successfully!</strong><br>
                    Your system design is ready for download and viewing.
                </div>
                """, unsafe_allow_html=True)
                
        elif current_status == "failed":
            error_msg = job_status.get('error', 'Unknown error')
            st.markdown(f"""
            <div class="error-alert">
                ❌ <strong>Generation Failed</strong><br>
                {error_msg[:200]}{'...' if len(error_msg) > 200 else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Try Again"):
                st.session_state.job_id = None
                st.rerun()
                
        elif current_status in ["queued", "running"]:
            # Auto-refresh for active jobs
            time.sleep(2)
            st.rerun()

# ---------------- RESULTS DISPLAY ----------------
if st.session_state.result_data and st.session_state.png_data:
    result = st.session_state.result_data
    
    st.markdown("""
    <div class="preview-card">
        <h2>📊 Generated System Design</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Download buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.download_button(
            label="📥 Download PNG",
            data=st.session_state.png_data,
            file_name=f"{result.get('topic', 'diagram').replace(' ', '_')}.png",
            mime="image/png",
            use_container_width=True
        )
    
    with col2:
        if result.get('mermaid'):
            st.download_button(
                label="📄 Download Mermaid",
                data=result['mermaid'],
                file_name=f"{result.get('topic', 'diagram').replace(' ', '_')}.mmd",
                mime="text/plain",
                use_container_width=True
            )
    
    # Display image
    st.image(
        st.session_state.png_data,
        caption=f"System Design: {result.get('topic', 'Generated Diagram')}",
        use_column_width=True
    )
    
    # Results summary
    components = result.get('components', {}).get('components', [])
    relationships = result.get('components', {}).get('relationships', [])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Components", len(components))
    with col2:
        st.metric("🔗 Relationships", len(relationships))
    with col3:
        st.metric("🌐 URLs Processed", len(result.get('urls', [])))
    with col4:
        st.metric("📄 Files Created", len(result.get('raw_files', [])))
    
    # Component details
    if components:
        with st.expander("🧩 View Components"):
            for i, comp in enumerate(components[:10]):  # Show first 10
                st.write(f"**{comp.get('name', 'Unknown')}** - {comp.get('type', 'unknown').title()}")
            
            if len(components) > 10:
                st.write(f"... and {len(components) - 10} more components")
    
    # Clear results button
    if st.button("🗑️ Clear Results"):
        st.session_state.job_id = None
        st.session_state.result_data = None
        st.session_state.png_data = None
        st.rerun()

# ---------------- EMPTY STATE ----------------
if not st.session_state.job_id:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: rgba(255,255,255,0.8);">
        <h2>🚀 Ready to Generate Your System Design?</h2>
        <p style="font-size: 1.2rem; margin: 2rem 0;">
            Enter a system title in the sidebar and click <strong>Generate Diagram</strong> to create 
            beautiful, professional system architecture diagrams powered by AI.
        </p>
        <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 2rem; margin: 2rem 0;">
            <h3>✨ Features</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div>🤖 <strong>AI-Powered</strong><br>Intelligent component extraction</div>
                <div>🎨 <strong>Beautiful Diagrams</strong><br>Professional PNG outputs</div>
                <div>🔍 <strong>Auto Research</strong><br>Finds relevant articles automatically</div>
                <div>⚡ <strong>Fast Processing</strong><br>Results in 60-120 seconds</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); padding: 1rem;">
    <strong>System Design Generator</strong> • Hackathon Prototype • 
    Frontend by <strong>Quirkless Code</strong> • 
    Powered by FastAPI + Streamlit
</div>
""", unsafe_allow_html=True)
