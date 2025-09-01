"""
High-Performance Screen Capture using ADB screenrecord streaming
No device binaries required - uses built-in Android screenrecord
"""
import asyncio
import subprocess
import threading
import time
import io
from typing import Optional, Dict
from dataclasses import dataclass
import numpy as np
import cv2

@dataclass
class StreamFrame:
    """Represents a decoded frame from screenrecord stream"""
    image: np.ndarray
    timestamp: float
    width: int
    height: int

class ScreenrecordManager:
    """High-performance streaming capture using adb screenrecord"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.process = None
        self.running = False
        self.last_frame: Optional[StreamFrame] = None
        self.frame_lock = threading.Lock()
        self.reader_thread = None
        self.cap = None
        
        # Stream settings
        self.bitrate = "8M"  # High quality
        self.size = "720x1280"  # Reduce for performance, scale up if needed
        self.time_limit = "3600"  # 1 hour max
        
    async def initialize(self):
        """Initialize screenrecord streaming"""
        try:
            print(f"[{self.device_id}] Basic screenrecord streaming disabled (requires FFmpeg for H264 decoding)")
            return False  # Disable basic streaming since it requires complex H264 decoding
            
        except Exception as e:
            print(f"[{self.device_id}] Failed to initialize screenrecord: {e}")
            return False
    
    async def _start_screenrecord_stream(self):
        """Start adb screenrecord streaming process"""
        # Kill any existing screenrecord
        kill_cmd = f"adb -s {self.device_id} shell pkill -f screenrecord"
        subprocess.run(kill_cmd, shell=True, capture_output=True)
        
        # Start streaming screenrecord
        cmd = [
            "adb", "-s", self.device_id, "exec-out",
            "screenrecord", 
            "--output-format=h264",
            f"--bit-rate={self.bitrate}",
            f"--size={self.size}",
            f"--time-limit={self.time_limit}",
            "--verbose",
            "-"  # Output to stdout
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0  # Unbuffered for real-time streaming
        )
        
        print(f"[{self.device_id}] Started screenrecord stream: {' '.join(cmd)}")
    
    def _frame_reader(self):
        """Read and decode H264 stream frames"""
        if not self.process or not self.process.stdout:
            return
            
        # Create OpenCV VideoCapture from pipe
        # Note: This approach reads raw H264 stream
        buffer = b''
        frame_buffer = bytearray()
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read chunk from stream
                chunk = self.process.stdout.read(8192)
                if not chunk:
                    time.sleep(0.001)
                    continue
                
                buffer += chunk
                
                # Try to decode frames from buffer
                # For H264, we need to find frame boundaries (NAL units)
                self._process_h264_buffer(buffer)
                
                # Keep only recent data to prevent memory buildup
                if len(buffer) > 1024 * 1024:  # 1MB max buffer
                    buffer = buffer[-512*1024:]  # Keep last 512KB
                    
            except Exception as e:
                if self.running:
                    print(f"[{self.device_id}] Frame reader error: {e}")
                    time.sleep(0.1)
    
    def _process_h264_buffer(self, buffer: bytes):
        """Process H264 buffer and extract frames"""
        try:
            # Create a temporary file-like object for OpenCV
            temp_buffer = io.BytesIO(buffer)
            
            # Try to create VideoCapture from buffer
            # This is a simplified approach - in production you'd want proper H264 parsing
            
            # For now, let's use a different approach: write to temp file and read
            # This is not the most efficient but works reliably
            temp_file = f"/tmp/stream_{self.device_id}.h264"
            
            # Write recent buffer to temp file
            with open(temp_file, 'wb') as f:
                f.write(buffer[-100000:])  # Last 100KB
            
            # Try to read with OpenCV
            cap = cv2.VideoCapture(temp_file)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    with self.frame_lock:
                        self.last_frame = StreamFrame(
                            image=frame_rgb,
                            timestamp=time.time(),
                            width=frame_rgb.shape[1],
                            height=frame_rgb.shape[0]
                        )
                
                cap.release()
            
        except Exception as e:
            # Silently ignore decode errors - they're common with streaming
            pass
    
    async def get_screenshot(self) -> Optional[np.ndarray]:
        """Get the latest frame as NumPy array"""
        with self.frame_lock:
            if self.last_frame is not None:
                # Check if frame is recent (within 1 second)
                if time.time() - self.last_frame.timestamp < 1.0:
                    return self.last_frame.image
        
        # Fallback to regular screencap if no recent frame
        return await self._fallback_screencap()
    
    async def _fallback_screencap(self) -> Optional[np.ndarray]:
        """Fallback to regular ADB screencap"""
        try:
            command = f"adb -s {self.device_id} exec-out screencap -p"
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if stdout:
                from PIL import Image
                pil_image = Image.open(io.BytesIO(stdout)).convert('RGB')
                return np.asarray(pil_image)
                
        except Exception as e:
            print(f"[{self.device_id}] Fallback screencap failed: {e}")
            
        return None
    
    def cleanup(self):
        """Clean up streaming resources"""
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        # Kill any remaining screenrecord processes on device
        try:
            kill_cmd = f"adb -s {self.device_id} shell pkill -f screenrecord"
            subprocess.run(kill_cmd, shell=True, capture_output=True, timeout=5)
        except:
            pass
        
        # Clean up temp files
        try:
            import os
            temp_file = f"/tmp/stream_{self.device_id}.h264"
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
        
        print(f"[{self.device_id}] Screenrecord cleaned up")

# Alternative implementation using FFmpeg for better H264 handling
class FFmpegScreenrecordManager:
    """Enhanced version using FFmpeg for H264 decoding"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.screenrecord_process = None
        self.ffmpeg_process = None
        self.running = False
        self.last_frame: Optional[StreamFrame] = None
        self.frame_lock = threading.Lock()
        self.reader_thread = None
        
    async def initialize(self):
        """Initialize with FFmpeg pipeline"""
        try:
            # Check if FFmpeg is available
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
            if result.returncode != 0:
                print(f"[{self.device_id}] FFmpeg not found, using basic implementation")
                return False
            
            await self._start_ffmpeg_pipeline()
            
            self.running = True
            self.reader_thread = threading.Thread(target=self._ffmpeg_frame_reader, daemon=True)
            self.reader_thread.start()
            
            print(f"[{self.device_id}] FFmpeg screenrecord streaming initialized")
            return True
            
        except Exception as e:
            print(f"[{self.device_id}] FFmpeg initialization failed: {e}")
            return False
    
    async def _start_ffmpeg_pipeline(self):
        """Start screenrecord -> FFmpeg pipeline"""
        # Kill existing processes
        kill_cmd = f"adb -s {self.device_id} shell pkill -f screenrecord"
        subprocess.run(kill_cmd, shell=True, capture_output=True)
        
        # Start screenrecord
        screenrecord_cmd = [
            "adb", "-s", self.device_id, "exec-out",
            "screenrecord", "--output-format=h264", "--bit-rate=8M",
            "--size=720x1280", "--time-limit=3600", "-"
        ]
        
        self.screenrecord_process = subprocess.Popen(
            screenrecord_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Start FFmpeg to decode H264 -> raw frames
        ffmpeg_cmd = [
            "ffmpeg", "-f", "h264", "-i", "pipe:0",
            "-f", "rawvideo", "-pix_fmt", "rgb24", 
            "-an", "-sn", "pipe:1"
        ]
        
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=self.screenrecord_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Close screenrecord stdout in parent
        self.screenrecord_process.stdout.close()
    
    def _ffmpeg_frame_reader(self):
        """Read decoded frames from FFmpeg"""
        if not self.ffmpeg_process:
            return
        
        frame_size = 720 * 1280 * 3  # Width * Height * RGB
        
        while self.running and self.ffmpeg_process.poll() is None:
            try:
                # Read one frame worth of data
                frame_data = self.ffmpeg_process.stdout.read(frame_size)
                
                if len(frame_data) == frame_size:
                    # Convert raw RGB data to numpy array
                    frame = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = frame.reshape((1280, 720, 3))
                    
                    with self.frame_lock:
                        self.last_frame = StreamFrame(
                            image=frame,
                            timestamp=time.time(),
                            width=720,
                            height=1280
                        )
                
            except Exception as e:
                if self.running:
                    print(f"[{self.device_id}] FFmpeg reader error: {e}")
                    time.sleep(0.1)
    
    async def get_screenshot(self) -> Optional[np.ndarray]:
        """Get latest frame"""
        with self.frame_lock:
            if self.last_frame and time.time() - self.last_frame.timestamp < 1.0:
                return self.last_frame.image
        return None
    
    def cleanup(self):
        """Cleanup FFmpeg processes"""
        self.running = False
        
        for process in [self.ffmpeg_process, self.screenrecord_process]:
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass

# Global managers
screenrecord_managers: Dict[str, ScreenrecordManager] = {}

async def get_screenrecord_manager(device_id: str) -> Optional[ScreenrecordManager]:
    """Get or create screenrecord manager for device"""
    if device_id not in screenrecord_managers:
        # Try FFmpeg version first, fallback to basic
        manager = FFmpegScreenrecordManager(device_id)
        if not await manager.initialize():
            manager = ScreenrecordManager(device_id)
            if not await manager.initialize():
                return None
        
        screenrecord_managers[device_id] = manager
    
    return screenrecord_managers.get(device_id)

def cleanup_all_screenrecord():
    """Clean up all screenrecord managers"""
    for manager in screenrecord_managers.values():
        manager.cleanup()
    screenrecord_managers.clear()
