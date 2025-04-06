import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from .window_manager import WindowManager
from .keyboard_manager import KeyboardManager
from mcp.server.fastmcp import FastMCP

# Configure logging
logger = logging.getLogger(__name__)

# Initialize MCP Server
mcp = FastMCP(
    name="window-screenshot",
    description="MCP server for capturing window screenshots",
    version="1.0.0",
    initialize_timeout=5
)

# Create FastAPI app
app = FastAPI(
    title="MCP Window Server",
    description="MCP server for window management and screenshot capture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure paths
SCREENSHOTS_DIR = Path("data/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files handler for screenshots
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")

class WindowInfo(BaseModel):
    id: int
    name: str
    owner: str
    bounds: Dict

@mcp.tool()
async def capture_window_screenshot(
    window_identifier: str,
    format: str = "binary"
) -> Dict:
    """Capture a screenshot of a specific window by its title or ID.
    
    Args:
        window_identifier: Window title to search for or window ID
        format: Output format (binary or base64) (default: "binary")
    """
    try:
        logger.info(f"Attempting to capture screenshot for window identifier: {window_identifier}")
        
        # Try to parse as window ID first
        try:
            window_id = int(window_identifier)
        except ValueError:
            # If not a number, search by title
            window_id = WindowManager.find_window_by_title(window_identifier, search_in_owner=True)
            if window_id is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No window found with title or owner containing '{window_identifier}'"
                )
        
        # Capture the screenshot
        screenshot = WindowManager.capture_window_screenshot(window_id)
        if screenshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to capture screenshot for window {window_id}"
            )
        
        # Get window info for the response
        windows = WindowManager.get_window_list()
        window_info = next((w for w in windows if w['id'] == window_id), None)
        window_name = window_info['name'] if window_info else "Unknown Window"
        
        # Generate unique filename and save screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.png"
        filepath = SCREENSHOTS_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(screenshot)
        
        logger.info(f"Successfully captured screenshot for window {window_id} ({window_name}) at {filepath}")
        
        # Return URL to the saved screenshot
        return {
            "window_id": window_id,
            "window_name": window_name,
            "screenshot_url": f"/screenshots/{filename}"
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error capturing window screenshot: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@mcp.tool()
async def list_windows() -> List[Dict]:
    """List all visible windows."""
    try:
        windows = WindowManager.get_window_list()
        return windows
    except Exception as e:
        logger.error(f"Error listing windows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mcp.tool()
async def find_window(
    title: str,
    search_in_owner: bool = True
) -> Dict:
    """Find a window by title or owner name.
    
    Args:
        title: Window title or owner name to search for
        search_in_owner: Whether to search in window owner names (default: true)
    """
    try:
        window_id = WindowManager.find_window_by_title(title, search_in_owner)
        if window_id is None:
            search_type = "title or owner" if search_in_owner else "title"
            raise HTTPException(
                status_code=404,
                detail=f"No window found with {search_type} containing '{title}'"
            )
        return {"window_id": window_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching for window: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mcp.tool()
async def send_key(
    key: str,
    modifiers: Optional[List[str]] = None
) -> Dict:
    """Send a keyboard key press event to the active window.
    
    Args:
        key: The key to press (e.g., 'a', 'return', 'space')
        modifiers: List of modifier keys to hold (e.g., ['command', 'shift'])
    """
    try:
        success = KeyboardManager.send_key(key, modifiers)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send key '{key}' with modifiers {modifiers if modifiers else 'none'}"
            )
        return {
            "status": "success",
            "key": key,
            "modifiers": modifiers if modifiers else []
        }
    except Exception as e:
        logger.error(f"Error sending key: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@mcp.tool()
async def type_text(
    text: str,
    delay: float = 0.1
) -> Dict:
    """Type a sequence of text characters.
    
    Args:
        text: The text to type
        delay: Delay between keystrokes in seconds (default: 0.1)
    """
    try:
        success = KeyboardManager.type_text(text, delay)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to type text: {text}"
            )
        return {
            "status": "success",
            "text": text,
            "delay": delay
        }
    except Exception as e:
        logger.error(f"Error typing text: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize managers before starting server
async def initialize_managers():
    """Initialize all managers before starting the server."""
    logger.info("Initializing managers...")
    
    # Initialize window manager
    try:
        windows = WindowManager.get_window_list()
        logger.info(f"Window manager initialized, found {len(windows)} windows")
    except Exception as e:
        logger.error(f"Failed to initialize window manager: {e}")
        raise
        
    # Initialize keyboard manager
    try:
        if not KeyboardManager.initialize():
            raise RuntimeError("Failed to initialize keyboard manager")
        logger.info("Keyboard manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize keyboard manager: {e}")
        raise
    
    logger.info("All managers initialized successfully")

# Register startup event
@app.on_event("startup")
async def startup_event():
    """Initialize all components on server startup."""
    try:
        # Initialize our managers
        await initialize_managers()
        logger.info("Server initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        logger.exception("Full traceback:")
        raise

# Create MCP app instance
mcp_app = mcp.sse_app()

# Mount MCP server at /
# IT MUST BE MOUNTED AT / or else it will not work
app.mount("/", mcp_app)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        windows = WindowManager.get_window_list()
        return {
            "status": "healthy",
            "windows_found": len(windows),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MCP Window Server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    ) 