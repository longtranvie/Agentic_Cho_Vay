@echo off
REM ============================================================
REM  Demo Loan Agent - double-click de chay server cuc bo.
REM  Mo http://127.0.0.1:8000/demo de bam thu API (Swagger UI).
REM  Dong cua so nay de tat demo.
REM ============================================================
cd /d "%~dp0"
set PYTHONPATH=src
set LOAN_LLM_PROVIDER=mock
set LOAN_RAG_BACKEND=keyword

echo.
echo  ====================================================
echo   Demo Loan Agent dang khoi dong...
echo   Link demo:  http://127.0.0.1:8000/demo
echo   (Neu trang bao loi, doi vai giay roi nhan F5)
echo   Dong cua so nay de TAT demo.
echo  ====================================================
echo.

REM Mo trinh duyet sau 4 giay (cho server kip khoi dong - tranh ERR_CONNECTION_REFUSED)
start "" /min cmd /c "timeout /t 4 >nul & start http://127.0.0.1:8000/demo"
python -m uvicorn loan_agent.api.app:app --host 127.0.0.1 --port 8000
echo.
echo  Server da dung. Nhan phim bat ky de dong.
pause >nul
