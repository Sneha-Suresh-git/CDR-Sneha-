@echo off
echo Preparing for Streamlit Cloud deployment...
cd ..
git add app.py requirements.txt
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
echo.
echo ========================================
echo Files pushed to GitHub!
echo.
echo Now deploy on Streamlit Cloud:
echo 1. Go to: https://share.streamlit.io/
echo 2. Click "New app"
echo 3. Repository: Sneha-Suresh-git/CDR-Sneha-
echo 4. Branch: main
echo 5. Main file path: app.py
echo 6. Click "Deploy"
echo ========================================
pause
