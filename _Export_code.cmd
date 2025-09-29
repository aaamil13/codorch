@echo off
setlocal enabledelayedexpansion

REM Абсолютен път до изходния файл
set "OUTPUT_FILE=.\code_export.txt"

REM Изтриване на стария файл, ако съществува
if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"

REM Директории за сканиране, относителни спрямо местоположението на скрипта
set "SCAN_DIRS=codorch\config codorch\src codorch\tests "
REM Разширения на файлове за включване
set "EXTENSIONS=py toml env yaml yml json"

echo Starting code export...

REM Обхождане на всяка от зададените директории
for %%D in (%SCAN_DIRS%) do (
    REM Временно преминаване в целевата директория
    pushd "%~dp0%%D"
    if !errorlevel! equ 0 (
        echo Scanning directory: %%D
        REM Обхождане на всеки тип файл
        for %%E in (%EXTENSIONS%) do (
            REM Рекурсивно търсене на файлове от текущата директория
            for /r %%F in (*.%%E) do (
                echo Writing file: %%~fF
                echo =============================================================================== >> "%OUTPUT_FILE%"
                echo File: %%~fF >> "%OUTPUT_FILE%"
                echo =============================================================================== >> "%OUTPUT_FILE%"
                type "%%F" >> "%OUTPUT_FILE%"
                echo. >> "%OUTPUT_FILE%"
                echo. >> "%OUTPUT_FILE%"
            )
        )
        REM Връщане към предишната директория
        popd
    ) else (
        echo Failed to change to directory: %%D
    )
)

echo Code export finished.
endlocal
