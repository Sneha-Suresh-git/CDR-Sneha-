@echo off
echo Removing all files from Git except app.py...
cd ..
git rm -r --cached .streamlit
git add app.py
git commit -m "Keep only app.py in repository"
git push origin main
echo.
echo Done! Only app.py remains in GitHub repository.
pause
