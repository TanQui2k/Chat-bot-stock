@echo off
chcp 65001 >nul
echo ==========================================================
echo          SCRIPT TỰ ĐỘNG THIẾT LẬP DỰ ÁN 
echo ==========================================================

echo.
echo [1/3] Khoi tao moi truong Frontend...
if not exist "frontend\.env.local" (
    echo - Dang sao chep frontend\.env.example sang frontend\.env.local ...
    copy "frontend\.env.example" "frontend\.env.local" >nul
) else (
    echo - frontend\.env.local da ton tai. Bo qua.
)

echo.
echo [2/3] Cai dat thu vien Backend...
echo (Luu y: Nen dam bao ban da vao moi truong ao Virtual Environment (neu co) truoc do).
cd backend
pip install -r requirements.txt

echo.
echo [3/3] Khoi tao Database va Migrations...
python setup_db.py

cd ..
echo.
echo ==========================================================
echo Hoan tat! 
echo ==========================================================
pause
