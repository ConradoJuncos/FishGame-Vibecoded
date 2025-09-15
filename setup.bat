@echo off
echo 🎣 FISHING GAME - FIRST TIME SETUP 🎣
echo ===================================
echo.
echo This will install the required Python packages...
echo.
pause

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo You can now run:
echo - start_server.bat (to start server)
echo - start_client.bat (to start client) 
echo - start_floating_character.bat (for character window)
echo - run_tests.bat (to run tests)
echo.
pause
