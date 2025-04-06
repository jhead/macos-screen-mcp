from typing import List, Dict, Optional
import logging
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventKeyDown,
    kCGEventKeyUp,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskShift,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskAlternate,
)
import time

logger = logging.getLogger(__name__)

class KeyboardManager:
    _initialized = False
    
    @classmethod
    def initialize(cls) -> bool:
        """Initialize the keyboard manager.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if cls._initialized:
            return True
            
        try:
            # Test keyboard event creation
            test_event = CGEventCreateKeyboardEvent(None, 0x00, True)
            if test_event is None:
                logger.error("Failed to create test keyboard event")
                return False
                
            logger.info("Successfully initialized KeyboardManager")
            cls._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing KeyboardManager: {e}")
            logger.exception("Full traceback:")
            return False

    @classmethod
    def ensure_initialized(cls) -> bool:
        """Ensure the keyboard manager is initialized.
        
        Returns:
            bool: True if initialized or initialization successful, False otherwise
        """
        if not cls._initialized:
            return cls.initialize()
        return True

    # Key code mapping for common keys
    KEY_CODES = {
        'a': 0x00, 'b': 0x0B, 'c': 0x08, 'd': 0x02, 'e': 0x0E,
        'f': 0x03, 'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26,
        'k': 0x28, 'l': 0x25, 'm': 0x2E, 'n': 0x2D, 'o': 0x1F,
        'p': 0x23, 'q': 0x0C, 'r': 0x0F, 's': 0x01, 't': 0x11,
        'u': 0x20, 'v': 0x09, 'w': 0x0D, 'x': 0x07, 'y': 0x10,
        'z': 0x06, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
        '5': 0x17, '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19,
        '0': 0x1D, 'return': 0x24, 'tab': 0x30, 'space': 0x31,
        'delete': 0x33, 'escape': 0x35, 'command': 0x37,
        'shift': 0x38, 'capslock': 0x39, 'option': 0x3A,
        'control': 0x3B, 'right_shift': 0x3C, 'right_option': 0x3D,
        'right_control': 0x3E, 'left_arrow': 0x7B, 'right_arrow': 0x7C,
        'down_arrow': 0x7D, 'up_arrow': 0x7E,
    }

    # Modifier key mapping
    MODIFIERS = {
        'command': kCGEventFlagMaskCommand,
        'shift': kCGEventFlagMaskShift,
        'control': kCGEventFlagMaskControl,
        'option': kCGEventFlagMaskAlternate,
    }

    @classmethod
    def send_key(cls, key: str, modifiers: Optional[List[str]] = None) -> bool:
        """Send a keyboard key press event.
        
        Args:
            key: The key to press (e.g., 'a', 'return', 'space')
            modifiers: List of modifier keys to hold (e.g., ['command', 'shift'])
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not cls.ensure_initialized():
            return False
            
        try:
            # Convert key to lowercase for consistency
            key = key.lower()
            
            # Get key code
            if key not in cls.KEY_CODES:
                logger.error(f"Unknown key: {key}")
                return False
                
            key_code = cls.KEY_CODES[key]
            
            # Calculate modifier flags
            flags = 0
            if modifiers:
                for mod in modifiers:
                    mod = mod.lower()
                    if mod in cls.MODIFIERS:
                        flags |= cls.MODIFIERS[mod]
            
            # Create key down event
            event_down = CGEventCreateKeyboardEvent(None, key_code, True)
            if event_down is None:
                logger.error("Failed to create key down event")
                return False
                
            if flags:
                CGEventSetFlags(event_down, flags)
            
            # Create key up event
            event_up = CGEventCreateKeyboardEvent(None, key_code, False)
            if event_up is None:
                logger.error("Failed to create key up event")
                return False
                
            if flags:
                CGEventSetFlags(event_up, flags)
            
            # Post events
            CGEventPost(kCGHIDEventTap, event_down)
            time.sleep(0.01)  # Small delay between down and up events
            CGEventPost(kCGHIDEventTap, event_up)
            
            logger.info(f"Successfully sent key '{key}' with modifiers {modifiers if modifiers else 'none'}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending keyboard input: {e}")
            logger.exception("Full traceback:")
            return False

    @classmethod
    def type_text(cls, text: str, delay: float = 0.1) -> bool:
        """Type a sequence of text characters.
        
        Args:
            text: The text to type
            delay: Delay between keystrokes in seconds (default: 0.1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not cls.ensure_initialized():
            return False
            
        try:
            for char in text:
                # Handle uppercase letters
                if char.isupper():
                    if not cls.send_key(char.lower(), ['shift']):
                        return False
                else:
                    if not cls.send_key(char.lower()):
                        return False
                time.sleep(delay)
            
            logger.info(f"Successfully typed text: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            logger.exception("Full traceback:")
            return False 