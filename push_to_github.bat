@echo off
echo Pushing to GitHub...
git add .
git commit -m "Clean up: Keep only app.py and essential files"
git push origin main
echo.
echo Done! Changes pushed to GitHub.
echo Repository: https://github.com/Sneha-Suresh-git/CDR-Sneha-
pause
