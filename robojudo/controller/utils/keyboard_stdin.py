"""
Keyboard input handler using stdin (works over SSH)
No dependencies required, works in any terminal
"""
import sys
import termios
import tty
import time
import atexit
from queue import Queue
from threading import Thread
import logging

logger = logging.getLogger(__name__)


class KeyboardStdinThread(Thread):
    """Keyboard thread using stdin (works over SSH)"""
    
    def __init__(self, event_queue: Queue):
        super().__init__(name="KeyboardStdinThread", daemon=True)
        self.event_queue = event_queue
        self.running = True
        
        # Save terminal settings
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            # Register cleanup on exit
            atexit.register(self._restore_terminal)
        except:
            logger.error("Failed to get terminal settings. Make sure you're running in a terminal.")
            raise
    
    def run(self):
        """Main loop to read keyboard events"""
        logger.info("Keyboard thread started (stdin mode)")
        logger.info("Press keys to control. Press ESC or Ctrl+C to exit.")
        
        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            
            while self.running:
                # Read one character
                char = sys.stdin.read(1)
                
                if not char:
                    continue
                
                # Convert to key name
                key_name = self._char_to_key_name(char)
                
                if key_name:
                    # Send press event
                    event_press = {
                        "type": "keyboard",
                        "name": key_name,
                        "pressed": True,
                        "timestamp": time.time(),
                    }
                    self.event_queue.put(event_press)
                    
                    # Immediately send release event
                    time.sleep(0.01)
                    event_release = {
                        "type": "keyboard",
                        "name": key_name,
                        "pressed": False,
                        "timestamp": time.time(),
                    }
                    self.event_queue.put(event_release)
                    
        except Exception as e:
            logger.error(f"Keyboard thread error: {e}")
        finally:
            # Restore terminal settings
            self._restore_terminal()
    
    def _char_to_key_name(self, char):
        """Convert character to key name"""
        # Handle special keys
        if char == '\x1b':  # ESC
            return 'Key.esc'
        elif char == '\x03':  # Ctrl+C
            logger.info("Ctrl+C detected, exiting...")
            self.running = False
            return 'Key.esc'  # Treat as ESC
        elif char == '`':
            return '`'
        elif char == '<':
            return '<'
        elif char == '>':
            return '>'
        elif char == '|':
            return '|'
        elif char == '[':
            return '['
        elif char == ']':
            return ']'
        elif char == '{':
            return '{'
        elif char == '}':
            return '}'
        elif char == ';':
            return ';'
        elif char == "'":
            return "'"
        elif char in '0123456789':
            # Number keys for policy switching
            logger.debug(f"Number key pressed: {char}")
            return char
        elif char in 'wasdqeior':
            # Log for debugging
            logger.debug(f"Key pressed: {char}")
            return char
        else:
            # Log ignored keys for debugging
            logger.debug(f"Ignored key: {repr(char)}")
            return None
    
    def _restore_terminal(self):
        """Restore terminal settings"""
        try:
            if hasattr(self, 'old_settings'):
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
                logger.info("Terminal settings restored")
        except Exception as e:
            logger.warning(f"Failed to restore terminal: {e}")
    
    def stop(self):
        """Stop the thread"""
        self.running = False
        self._restore_terminal()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self._restore_terminal()


if __name__ == "__main__":
    event_queue = Queue()
    
    try:
        kb_thread = KeyboardStdinThread(event_queue)
        kb_thread.start()
        
        print("Press keys (ESC or Ctrl+C to exit)...")
        print("Supported keys: w, a, s, d, q, e, i, o, r, ESC, `, <, >, |, [, ], {, }, ;, '")
        
        while True:
            if not event_queue.empty():
                event = event_queue.get()
                if not event["pressed"]:  # Only show release events
                    print(f"Key: {event['name']}")
                    if event['name'] == 'Key.esc':
                        print("ESC pressed, exiting...")
                        break
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'kb_thread' in locals():
            kb_thread.stop()
