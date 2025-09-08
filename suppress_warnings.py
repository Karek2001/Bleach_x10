# suppress_warnings.py - Suppress libpng and other warnings
import warnings
import os
import sys
import ctypes
import io
from contextlib import contextmanager

# Global variable to track if stderr has been redirected
_stderr_redirected = False

def suppress_libpng_warning():
    """Suppress libpng warnings that clutter the console"""
    global _stderr_redirected
    
    # Set environment variables FIRST before any imports
    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
    os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
    os.environ['OPENCV_IO_MAX_IMAGE_PIXELS'] = '1073741824'  # 1GB limit instead of 0
    os.environ['PYTHONWARNINGS'] = 'ignore'
    
    # Suppress Python warnings
    warnings.filterwarnings("ignore")
    
    # Aggressive C-level stderr redirection
    if not _stderr_redirected:
        try:
            if sys.platform == "win32":
                # Windows: Redirect stderr file descriptor to NUL
                import msvcrt
                # Open NUL device
                nul_fd = os.open('NUL', os.O_WRONLY)
                # Duplicate stderr (fd 2) to NUL
                os.dup2(nul_fd, 2)
                os.close(nul_fd)
                _stderr_redirected = True
            else:
                # Unix/Linux: Redirect stderr to /dev/null
                devnull_fd = os.open('/dev/null', os.O_WRONLY)
                os.dup2(devnull_fd, 2)
                os.close(devnull_fd)
                _stderr_redirected = True
        except (OSError, AttributeError):
            # Fallback: Try ctypes approach
            try:
                if sys.platform == "win32":
                    # Windows ctypes approach
                    kernel32 = ctypes.windll.kernel32
                    # Get stderr handle
                    stderr_handle = kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE
                    # Open NUL device
                    nul_handle = kernel32.CreateFileW(
                        "NUL", 0x40000000, 0, None, 3, 0, None
                    )
                    # Set stderr to NUL
                    kernel32.SetStdHandle(-12, nul_handle)
                    _stderr_redirected = True
                else:
                    # Unix ctypes approach
                    libc = ctypes.CDLL("libc.so.6")
                    # Redirect stderr (fd 2) to /dev/null
                    devnull = libc.open(b"/dev/null", 1)  # O_WRONLY
                    libc.dup2(devnull, 2)
                    libc.close(devnull)
                    _stderr_redirected = True
            except:
                pass
    
    # Suppress libpng warnings at OpenCV level
    try:
        import cv2
        cv2.setLogLevel(0)  # Completely silent
    except ImportError:
        pass
    
    # PIL/Pillow suppression
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
    except ImportError:
        pass

@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout and stderr temporarily"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

# Initialize suppression when module is imported
suppress_libpng_warning()