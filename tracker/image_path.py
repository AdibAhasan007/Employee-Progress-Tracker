import sys
import os

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    When PyInstaller bundles an app, it extracts resources to a temporary folder
    stored in sys._MEIPASS. This function checks for that attribute to determine
    if the app is running as a bundled executable or as a script.
    
    Args:
        relative_path (str): The relative path to the resource file (e.g., "icon.png").
        
    Returns:
        str: The absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # During development, use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(base_path, relative_path)
    
    # If file doesn't exist in current location, try parent directory
    if not os.path.exists(full_path) and ".." not in relative_path:
        alt_path = os.path.join(base_path, "..", relative_path)
        if os.path.exists(alt_path):
            return alt_path
    
    return full_path

