@echo off
echo Killing ADB and FFmpeg processes...

taskkill /f /im ffmpeg.exe 2>nul  
if %errorlevel%==0 echo ✅ FFmpeg processes killed

taskkill /f /im cmd.exe /fi "WindowTitle ne Administrator*" 2>nul
if %errorlevel%==0 echo ✅ Orphaned CMD processes killed

echo.
echo ✅ Cleanup complete. All processes should be terminated.
pause
