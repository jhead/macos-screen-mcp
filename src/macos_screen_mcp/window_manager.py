import logging
from typing import List, Dict, Optional, Tuple
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    CGWindowListCreateImage,
    CGRectNull,
    kCGWindowImageDefault,
    CGWindowListCreateDescriptionFromArray,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetDataProvider,
    CGDataProviderCopyData,
    CGRectMake,
    kCGWindowImageBoundsIgnoreFraming,
    kCGWindowListOptionIncludingWindow,
    CGImageGetBitsPerComponent,
    CGImageGetBytesPerRow,
    CGImageGetBitsPerPixel,
)
from Foundation import NSArray, NSDictionary
from PIL import Image
import io
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowManager:
    @staticmethod
    def get_window_list() -> List[Dict]:
        """Get a list of all visible windows."""
        try:
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            )
            windows = []
            
            for window in window_list:
                window_dict = dict(window)
                if window_dict.get('kCGWindowName'):  # Only include windows with names
                    windows.append({
                        'id': window_dict.get('kCGWindowNumber'),
                        'name': window_dict.get('kCGWindowName'),
                        'owner': window_dict.get('kCGWindowOwnerName'),
                        'bounds': window_dict.get('kCGWindowBounds'),
                    })
            
            logger.info(f"Found {len(windows)} visible windows")
            return windows
        except Exception as e:
            logger.error(f"Error getting window list: {e}")
            return []

    @staticmethod
    def capture_window_screenshot(window_id: int) -> Optional[bytes]:
        """Capture a screenshot of a specific window by its ID."""
        try:
            logger.info(f"Attempting to capture screenshot for window {window_id}")
            
            # Get window info to get bounds
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            )
            target_window = None
            for window in window_list:
                window_dict = dict(window)
                if window_dict.get('kCGWindowNumber') == window_id:
                    target_window = window_dict
                    break
            
            if not target_window:
                logger.error(f"Window {window_id} not found")
                return None
            
            # Get window bounds
            bounds = target_window.get('kCGWindowBounds')
            if not bounds:
                logger.error(f"No bounds found for window {window_id}")
                return None
            
            # Create CGRect from bounds using original dimensions
            window_bounds = CGRectMake(
                bounds['X'],
                bounds['Y'],
                bounds['Width'],
                bounds['Height']
            )
            logger.info(f"Window bounds: X={bounds['X']}, Y={bounds['Y']}, Width={bounds['Width']}, Height={bounds['Height']}")
            
            # Get the window image using only the target window
            logger.info("Creating window image...")
            image = CGWindowListCreateImage(
                window_bounds,
                kCGWindowListOptionIncludingWindow,  # Only include the target window
                window_id,
                kCGWindowImageDefault
            )
            logger.info(f"Window image created: {image is not None}")
            
            if image is None:
                logger.error(f"Failed to capture screenshot for window {window_id}")
                return None
            
            # Get image properties
            width = int(CGImageGetWidth(image))
            height = int(CGImageGetHeight(image))
            bits_per_component = CGImageGetBitsPerComponent(image)
            bytes_per_row = CGImageGetBytesPerRow(image)
            bits_per_pixel = CGImageGetBitsPerPixel(image)
            
            logger.info(f"Image properties: {width}x{height}, {bits_per_component} bits/component, {bits_per_pixel} bits/pixel, {bytes_per_row} bytes/row")
            
            # Create a new PIL Image from the CGImage
            logger.info("Converting to PIL Image...")
            data_provider = CGImageGetDataProvider(image)
            if data_provider is None:
                logger.error("Failed to get data provider from image")
                return None
                
            image_data = CGDataProviderCopyData(data_provider)
            if image_data is None:
                logger.error("Failed to copy image data from provider")
                return None

            # Convert image data to numpy array and handle BGRA to RGBA conversion
            buffer = np.frombuffer(image_data, dtype=np.uint8)
            array = buffer.reshape(height, bytes_per_row // 4, 4)
            # Convert BGRA to RGBA by swapping the R and B channels
            array = array[..., [2, 1, 0, 3]]
            
            pil_image = Image.fromarray(array, mode='RGBA')
            logger.info("Successfully converted to PIL Image")
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            logger.info(f"Successfully captured screenshot for window {window_id}")
            return img_byte_arr
            
        except Exception as e:
            logger.error(f"Error capturing window screenshot: {e}")
            logger.exception("Full traceback:")
            return None

    @staticmethod
    def find_window_by_title(title: str, search_in_owner: bool = True) -> Optional[int]:
        """
        Find a window ID by its title or owner name (partial match).
        
        Args:
            title: The search term to look for
            search_in_owner: Whether to also search in the owner field (default: True)
            
        Returns:
            The window ID if found, None otherwise
        """
        windows = WindowManager.get_window_list()
        search_term = title.lower()
        
        # First try exact match in owner field if search_in_owner is True
        if search_in_owner:
            for window in windows:
                owner_name = window['owner'].lower()
                if owner_name == search_term:
                    logger.info(f"Found exact match in owner: '{window['owner']}'")
                    return window['id']
        
        # Then try partial match in either field
        for window in windows:
            window_name = window['name'].lower()
            owner_name = window['owner'].lower()
            
            # Check if the search term matches either the window name or owner
            if search_term in window_name or (search_in_owner and search_term in owner_name):
                logger.info(f"Found window with title '{title}' in name '{window['name']}' or owner '{window['owner']}'")
                return window['id']
                
        logger.warning(f"No window found with title or owner containing '{title}'")
        return None
