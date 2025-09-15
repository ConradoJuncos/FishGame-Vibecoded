@echo off
echo 🎣 UNIFIED FISHING GAME TEST SUITE 🎣
echo ====================================
echo.
echo This will run comprehensive tests for:
echo - Character images and switching system
echo - Offline fishing mechanics  
echo - Server connection and online fishing (optional)
echo.
echo Make sure the server is running if you want to test online features!
echo.
pause
echo.
python scripts/unified_test.py
echo.
echo Tests completed!
pause
