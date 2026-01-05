import streamlit as st
import requests
import io
import time
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas

# Compatibility shim for streamlit_drawable_canvas with newer Streamlit versions
try:
    from streamlit.elements import image as st_image
    if not hasattr(st_image, "image_to_url"):
        from streamlit.runtime.media_file_manager import media_file_manager

        def _image_to_url(image, width, clamp=False, channels="RGB", output_format="PNG", image_id=None):
            buf = io.BytesIO()
            fmt = output_format or "PNG"
            image.save(buf, format=fmt)
            file_id = media_file_manager.add(buf.getvalue(), mime_type=f"image/{fmt.lower()}", file_id=image_id)
            return media_file_manager.get_url(file_id)

        st_image.image_to_url = _image_to_url
except Exception:
    # If the shim fails, canvas will render without a background instead of crashing
    pass

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="System Design Generator",
    page_icon="🛠️",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"


def render_components_overlay(image: Image.Image, components: list[dict]) -> Image.Image:
    """Overlay component labels onto the generated diagram."""
    if not components:
        return image

    try:
        img = image.convert("RGBA")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        lines = [
            f"{idx + 1}. {c.get('name', 'component')} ({c.get('type', '')})"
            for idx, c in enumerate(components)
        ]

        padding = 12
        x = 16
        y = 16
        text_heights = font.size + 6
        box_width = int(max(font.getlength(line) for line in lines) + padding * 2)
        box_height = int(len(lines) * text_heights + padding * 2)

        draw.rectangle([x, y, x + box_width, y + box_height], fill=(255, 255, 255, 200))

        for i, line in enumerate(lines):
            draw.text((x + padding, y + padding + i * text_heights), line, fill=(0, 0, 0), font=font)

        return img
    except Exception:
        return image

# ================== GLOBAL CSS ==================
st.markdown("""
<style>

/* RESET STREAMLIT LAYOUT */
header, footer {visibility: hidden; height: 0;}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stToolbar"] {display: none !important;}
.main {
    padding-top: 0 !important;
    padding-left: 0 !important;
}
.main .block-container {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* SIDEBAR STYLING */
section[data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    min-width: 250px !important;
    max-width: 600px !important;
    width: 280px !important;
    transition: width 0.3s ease;
}

section[data-testid="stSidebar"] > div {
    background-color: #0f0f0f !important;
    padding-top: 2rem;
}

/* RESIZE HANDLE */
.sidebar-resize-handle {
    position: absolute;
    right: -2px;
    top: 0;
    width: 4px;
    height: 100%;
    background: #1f1f1f;
    cursor: col-resize;
    z-index: 1000;
    transition: background 0.2s;
}

.sidebar-resize-handle:hover {
    background: #6c63ff;
}

/* MINIMIZE BUTTON */
.sidebar-minimize-btn {
    position: absolute;
    top: 15px;
    right: 15px;
    background: #2b2b2b;
    color: #eaeaea;
    border: 1px solid #3f3f3f;
    border-radius: 6px;
    width: 32px;
    height: 32px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    z-index: 1001;
    transition: all 0.2s;
}

.sidebar-minimize-btn:hover {
    background: #3f3f3f;
    border-color: #6c63ff;
}

/* MINIMIZED SIDEBAR */
section[data-testid="stSidebar"].sidebar-minimized {
    min-width: 60px !important;
    max-width: 60px !important;
    width: 60px !important;
}

section[data-testid="stSidebar"].sidebar-minimized .sidebar-resize-handle {
    display: none;
}

section[data-testid="stSidebar"].sidebar-minimized > div {
    overflow: hidden;
}

section[data-testid="stSidebar"].sidebar-minimized > div > div {
    opacity: 0 !important;
    pointer-events: none !important;
}

section[data-testid="stSidebar"].sidebar-minimized .sidebar-minimize-btn {
    opacity: 1 !important;
    pointer-events: all !important;
}

/* CANVAS AREA */
.canvas-bg {
    background-color: #ffffff;
    background-image: radial-gradient(#d6d6d6 1px, transparent 1px);
    background-size: 20px 20px;
    padding: 0;
    overflow: auto;
    position: relative;
    width: 100%;
    height: calc(100vh - 0px);
    box-sizing: border-box;
}

/* DOWNLOAD BUTTON OVERLAY */
.download-overlay {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    z-index: 1000;
}

.stDownloadButton > button {
    background-color: #FF6B35 !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-size: 16px !important;
    width: 200px !important;
    border: none !important;
    box-shadow: 0 6px 15px rgba(255,107,53,0.4) !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
    background-color: #e55a2b !important;
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(255,107,53,0.6) !important;
}

/* CANVAS CONTAINER */
.canvas-container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
    position: relative;
    overflow: auto;
    max-height: calc(100vh - 40px);
}

/* Make canvas responsive - fit to container */
.canvas-container > div {
    max-width: calc(100vw - 320px) !important;
    max-height: calc(100vh - 100px) !important;
}

.canvas-container canvas {
    max-width: 100% !important;
    max-height: calc(100vh - 100px) !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain;
}

/* MAIN CONTENT AREA ADJUSTMENT */
.main .block-container {
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}

</style>

<script>
(function() {
    function initResizableSidebar() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (!sidebar) {
            setTimeout(initResizableSidebar, 100);
            return;
        }
        
        // Don't reinitialize
        if (sidebar.dataset.resizableInitialized === 'true') {
            return;
        }
        sidebar.dataset.resizableInitialized = 'true';
        
        // Make sidebar position relative
        sidebar.style.position = 'relative';
        
        // Create resize handle
        let resizeHandle = sidebar.querySelector('.sidebar-resize-handle');
        if (!resizeHandle) {
            resizeHandle = document.createElement('div');
            resizeHandle.className = 'sidebar-resize-handle';
            sidebar.appendChild(resizeHandle);
        }
        
        // Create minimize button
        let minimizeBtn = sidebar.querySelector('.sidebar-minimize-btn');
        if (!minimizeBtn) {
            minimizeBtn = document.createElement('button');
            minimizeBtn.className = 'sidebar-minimize-btn';
            minimizeBtn.innerHTML = '◀';
            minimizeBtn.title = 'Minimize sidebar';
            sidebar.appendChild(minimizeBtn);
        }
        
        // Load saved width from localStorage
        const savedWidth = localStorage.getItem('sidebarWidth');
        const isMinimized = localStorage.getItem('sidebarMinimized') === 'true';
        
        if (isMinimized) {
            sidebar.classList.add('sidebar-minimized');
            minimizeBtn.innerHTML = '▶';
            minimizeBtn.title = 'Expand sidebar';
        } else if (savedWidth) {
            sidebar.style.width = savedWidth + 'px';
        }
        
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;
        
        function startResize(e) {
            if (sidebar.classList.contains('sidebar-minimized')) return;
            isResizing = true;
            startX = e.clientX || (e.touches && e.touches[0].clientX);
            startWidth = parseInt(window.getComputedStyle(sidebar).width, 10);
            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
            if (e.touches) {
                document.addEventListener('touchmove', resize);
                document.addEventListener('touchend', stopResize);
            }
            e.preventDefault();
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        }
        
        function resize(e) {
            if (!isResizing || !sidebar) return;
            const clientX = e.clientX || (e.touches && e.touches[0].clientX);
            const diff = clientX - startX;
            const newWidth = Math.max(250, Math.min(600, startWidth + diff));
            sidebar.style.width = newWidth + 'px';
            localStorage.setItem('sidebarWidth', newWidth);
            localStorage.setItem('sidebarMinimized', 'false');
            e.preventDefault();
        }
        
        function stopResize() {
            isResizing = false;
            document.removeEventListener('mousemove', resize);
            document.removeEventListener('mouseup', stopResize);
            document.removeEventListener('touchmove', resize);
            document.removeEventListener('touchend', stopResize);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
        
        // Minimize/Expand functionality
        minimizeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar.classList.contains('sidebar-minimized')) {
                sidebar.classList.remove('sidebar-minimized');
                minimizeBtn.innerHTML = '◀';
                minimizeBtn.title = 'Minimize sidebar';
                const savedWidth = localStorage.getItem('sidebarWidth') || '280';
                sidebar.style.width = savedWidth + 'px';
                localStorage.setItem('sidebarMinimized', 'false');
            } else {
                // Save current width before minimizing
                const currentWidth = parseInt(window.getComputedStyle(sidebar).width, 10);
                if (currentWidth > 60) {
                    localStorage.setItem('sidebarWidth', currentWidth);
                }
                sidebar.classList.add('sidebar-minimized');
                minimizeBtn.innerHTML = '▶';
                minimizeBtn.title = 'Expand sidebar';
                localStorage.setItem('sidebarMinimized', 'true');
            }
        });
        
        resizeHandle.addEventListener('mousedown', startResize);
        resizeHandle.addEventListener('touchstart', startResize);
        
        // Update canvas container max-width when sidebar changes
        function updateCanvasWidth() {
            const sidebar = document.querySelector('section[data-testid="stSidebar"]');
            const canvasContainer = document.querySelector('.canvas-container');
            if (sidebar && canvasContainer) {
                const sidebarWidth = sidebar.classList.contains('sidebar-minimized') ? 60 : parseInt(window.getComputedStyle(sidebar).width, 10);
                const availableWidth = window.innerWidth - sidebarWidth - 40;
                const canvasDiv = canvasContainer.querySelector('div');
                if (canvasDiv) {
                    canvasDiv.style.maxWidth = availableWidth + 'px';
                }
            }
        }
        
        // Update on sidebar resize/minimize
        const observer = new MutationObserver(updateCanvasWidth);
        observer.observe(sidebar, {
            attributes: true,
            attributeFilter: ['class', 'style']
        });
        window.addEventListener('resize', updateCanvasWidth);
        updateCanvasWidth();
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initResizableSidebar);
    } else {
        initResizableSidebar();
    }
    
    // Also try after delays to ensure Streamlit has rendered
    setTimeout(initResizableSidebar, 100);
    setTimeout(initResizableSidebar, 500);
    setTimeout(initResizableSidebar, 1000);
})();
</script>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
if "diagram_img" not in st.session_state:
    st.session_state.diagram_img = None
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0
if "components" not in st.session_state:
    st.session_state.components = []

# ================== SIDEBAR ==================
st.sidebar.title("🛠️ System Design Generator")
st.sidebar.subheader("Team: Quirkless Code")
st.sidebar.divider()

system_title = st.sidebar.text_input("System Title", placeholder="Example: Uber backend system")
design_type = st.sidebar.selectbox("Design Type", ["HLD (High Level Design)", "LLD (Low Level Design)"])
generate_btn = st.sidebar.button("⚡ Generate Diagram")

st.sidebar.divider()
st.sidebar.markdown("**Drawing Tools**")
drawing_mode = st.sidebar.selectbox(
    "Tool",
    ["freedraw", "line", "rect", "circle", "transform"]
)
stroke_width = st.sidebar.slider("Stroke Width", 1, 20, 3)
stroke_color = st.sidebar.color_picker("Stroke Color", "#000000")

if st.sidebar.button("🧹 Clear Canvas"):
    st.session_state.canvas_key += 1
    st.session_state.diagram_img = None

# Map design_type for API
design_type_api = "HLD" if "High Level" in design_type else "LLD"
generate = generate_btn
title = system_title

# ================== BACKEND GENERATION ==================
if generate and title.strip():
    with st.spinner("Submitting job to backend and waiting for completion..."):
        try:
            create_resp = requests.post(
                f"{BACKEND_URL}/generate",
                json={"title": title, "type": design_type_api},
                timeout=30,
            )
            create_resp.raise_for_status()
            job_info = create_resp.json()
            job_id = job_info.get("job_id")

            if not job_id:
                raise RuntimeError("Backend did not return a job_id")

            status = job_info.get("status", "queued")
            for _ in range(400):  # ~90 seconds max wait
                if status in {"completed", "failed"}:
                    break

                status_resp = requests.get(
                    f"{BACKEND_URL}/status/{job_id}", timeout=10
                )
                status_resp.raise_for_status()
                status = status_resp.json().get("status", "unknown")

                if status == "completed":
                    break
                if status == "failed":
                    raise RuntimeError("Job failed during processing")

                time.sleep(2)

            if status != "completed":
                raise TimeoutError("Job did not complete in time")

            result_resp = requests.get(
                f"{BACKEND_URL}/result/{job_id}", timeout=30
            )
            result_resp.raise_for_status()
            result = result_resp.json()

            st.session_state.components = result.get("components", {}).get("components", [])
            png_url = result.get("png_url") or ""

            if png_url:
                image_resp = requests.get(f"{BACKEND_URL}{png_url}", timeout=30)
                image_resp.raise_for_status()
                fetched_img = Image.open(io.BytesIO(image_resp.content)).convert("RGBA")
                st.session_state.diagram_img = render_components_overlay(
                    fetched_img, st.session_state.components
                )
                st.session_state.canvas_key += 1
            else:
                st.warning("Diagram URL missing from backend result.")

        except Exception as e:
            st.error(f"Backend error: {e}")

# ================== MAIN CANVAS ==================
st.markdown('<div class="canvas-bg">', unsafe_allow_html=True)

# Calculate responsive canvas dimensions
# Use reasonable default sizes that fit most screens
CANVAS_WIDTH = 1200  # Base width - will fit screen with CSS
CANVAS_HEIGHT = 700  # Base height - will fit screen with CSS

if st.session_state.diagram_img:
    bg_image = st.session_state.diagram_img.resize(
        (CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS
    )
else:
    bg_image = Image.new(
        "RGBA",
        (CANVAS_WIDTH, CANVAS_HEIGHT),
        (255, 255, 255, 255)
    )

st.markdown('<div class="canvas-container">', unsafe_allow_html=True)

canvas_result = st_canvas(
    background_image=bg_image,
    drawing_mode=drawing_mode,
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    update_streamlit=True,
    key=f"canvas_{st.session_state.canvas_key}",
)

st.markdown('</div>', unsafe_allow_html=True)  # Close canvas-container

# Download overlay container - positioned absolutely in top right
st.markdown('<div class="download-overlay">', unsafe_allow_html=True)

# ================== DOWNLOAD ==================
if canvas_result.image_data is not None:
    merged = Image.alpha_composite(
        bg_image,
        Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
    )

    buf = io.BytesIO()
    merged.save(buf, format="PNG")

    st.download_button(
        "⬇ Download PNG",
        buf.getvalue(),
        file_name="system_design.png",
        mime="image/png"
    )

st.markdown('</div>', unsafe_allow_html=True)  # Close download-overlay
st.markdown('</div>', unsafe_allow_html=True)  # Close canvas-bg
