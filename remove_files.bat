@echo off
echo Removing files from GitHub repository...
cd ..
git rm --cached .gitignore
git rm --cached README.md
git rm --cached push_to_github.bat
git rm --cached requirements.txt
git rm -r --cached .streamlit
git add app.py
git commit -m "Remove all files except app.py"
git push origin main
echo.
echo Done! Only app.py should remain in GitHub.
pause
