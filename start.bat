@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM   顶会四支柱文献看板 - 一键启动
REM   用法：双击运行，或在命令行执行 start.bat [端口]（默认 8765）
REM ============================================================

set "PORT=%~1"
if "%PORT%"=="" set "PORT=8765"

cd /d "%~dp0"

REM --- 1. 定位 Python（优先 py 启动器，其次 python / python3） ---
set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
    where python >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    where python3 >nul 2>nul
    if not errorlevel 1 set "PY=python3"
)
if not defined PY (
    echo [错误] 未检测到 Python，请先安装 Python 3 并勾选 "Add to PATH"。
    echo       官网：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- 2. 校验入口脚本 ---
if not exist "scripts\serve.py" (
    echo [错误] 未找到 scripts\serve.py，请确认在完整的项目目录下运行。
    pause
    exit /b 1
)

REM --- 3. 端口已被占用则直接打开浏览器，不再重复启动 ---
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo 端口 %PORT% 已在监听，直接打开浏览器...
    start "" "http://127.0.0.1:%PORT%/"
    exit /b 0
)

echo.
echo   顶会四支柱文献看板正在启动...
echo   地址：http://127.0.0.1:%PORT%/
echo   停止：在本窗口按 Ctrl+C
echo.

REM --- 4. 延时打开默认浏览器（等服务端就绪） ---
start "" /min powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:%PORT%/'"

%PY% scripts\serve.py --port %PORT%
set "RC=%errorlevel%"

echo.
if not "%RC%"=="0" (
    echo [提示] 服务已退出，退出码 %RC%。常见原因：端口 %PORT% 被占用（可用 start.bat 8790 换端口）。
) else (
    echo [提示] 服务已停止。
)
pause
exit /b %RC%
