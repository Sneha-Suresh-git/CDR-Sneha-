@echo off
echo Deploying fixed app to GitHub...
git add app.py
git commit -m "Fix: Move st.set_page_config inside main() for Streamlit Cloud"
git push origin main
echo.
echo ========================================
echo SUCCESS! Code pushed to GitHub.
echo.
echo Streamlit Cloud will auto-redeploy in 2-3 minutes.
echo Your app: https://cdr-sneha.streamlit.app
echo ========================================
pause
