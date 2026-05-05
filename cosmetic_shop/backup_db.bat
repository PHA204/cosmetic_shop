@echo off
setlocal enabledelayedexpansion

:: --- CẤU HÌNH ---
set PGUSER=postgres
set PGDATABASE=cosmetic_db
set PGPASSWORD=123456
set BACKUP_DIR=D:\Document\Python_Code\cosmetic_shop\cosmetic_shop\backups

:: Tạo thư mục backups nếu chưa có
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Lấy ngày giờ hiện tại làm tên file (YYYY-MM-DD_HHMM)
set DATETIME=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%%time:~3,2%
set DATETIME=%DATETIME: =0%

set FILENAME=%BACKUP_DIR%\backup_%PGDATABASE%_%DATETIME%.sql

echo Dang backup database %PGDATABASE%...
"D:\Programs\PostgreSQL\16\bin\pg_dump.exe" -U %PGUSER% -d %PGDATABASE% -f "%FILENAME%"

if %ERRORLEVEL% equ 0 (
    echo [THANH CONG] Da luu backup tai: %FILENAME%
) else (
    echo [LOI] Co loi xay ra trong qua trinh backup!
)

pause
