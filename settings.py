# settings.py - Enhanced with performance options
import os
# Device configuration
DEVICE_IDS = [
  "127.0.0.1:16800",
  "127.0.0.1:16832",
  "127.0.0.1:16864",
  "127.0.0.1:16896",
  "127.0.0.1:16928",
  "127.0.0.1:16960",
  "127.0.0.1:16992",
  "127.0.0.1:17024",
  "127.0.0.1:17056",
  "127.0.0.1:17088"
]
# -------------------
# PERFORMANCE SETTINGS
# -------------------
# Screenshot caching duration (seconds) - reduces redundant captures
SCREENSHOT_CACHE_DURATION = 0.8  # Increased for better caching

# Batch processing size - how many tasks to check per screenshot
TASK_BATCH_SIZE = 8  # Increased batch size for efficiency

# Background check interval (seconds) - how often to cycle through tasks
BACKGROUND_CHECK_INTERVAL = 0.2  # Faster checking

# Parallel screenshot capture for all devices
PARALLEL_SCREENSHOT_CAPTURE = True

# Maximum concurrent screenshot operations
MAX_CONCURRENT_SCREENSHOTS = 16  # Half of device count for optimal performance

# Smart task prioritization - check high-priority tasks first
USE_TASK_PRIORITIZATION = True

# Skip checking stable devices as frequently
ADAPTIVE_CHECK_INTERVAL = True

# Use async processing instead of threads (recommended)
USE_ASYNC_PROCESSING = True

# Maximum concurrent ADB connections per device
MAX_ADB_CONNECTIONS = 2

# Enable GPU memory pooling for better performance
ENABLE_GPU_MEMORY_POOL = True

# Screenshot quality (1-100) - lower = faster but less accurate
SCREENSHOT_QUALITY = 85

# -------------------
# OPTIMIZATION FLAGS
# -------------------
# Skip bounds checking for known good coordinates (small performance gain)
SKIP_BOUNDS_CHECK = False

# Use persistent ADB connections (experimental)
USE_PERSISTENT_ADB = False

# Enable performance profiling
ENABLE_PROFILING = False

# -------------------
# GAME & APP SETTINGS
# -------------------
GAME_PACKAGE_NAME = 'com.bandainamcoent.dblegends_ww'
GAME_ACTIVITY_NAME = f'{GAME_PACKAGE_NAME}.UnityPlayerActivity'

# -------------------
# FILE & PATH SETTINGS
# -------------------
LOCAL_STOCKS_PATH_BASE = os.path.join(os.path.expanduser('~'), 'Desktop', 'STOCKS')
REMOTE_DATA_DIR = f'/storage/emulated/0/Android/data/{GAME_PACKAGE_NAME}/files'
ECD_FILES = {
    'PRIMARY': 'ecd1bb8b626d380e93748523485ef051',
    'SECONDARY': '2b7038f1a0d3b9c9e57f3954bfa7672a',
    'IMAGE': '89bb4eb5637df3cd96c463a795005065',
}

# -------------------
# AUTOMATION SETTINGS
# -------------------
EMULATOR_RESOLUTION = (960, 540)

# Number of concurrent threads (only used if USE_ASYNC_PROCESSING is False)
NUM_THREADS = 4

# Coordinates to check for a black screen after launch
BLACK_SCREEN_PIXELS = [
    (100, 200),
    (400, 200),
    (100, 800),
    (400, 800),
]

# How long to wait for a black screen before restarting the game (in seconds)
BLACK_SCREEN_TIMEOUT = 15

# -------------------
# GPU OPTIMIZATION
# -------------------
# GPU optimization disabled - using NumPy instead of CuPy
ENABLE_GPU_MEMORY_POOL = False