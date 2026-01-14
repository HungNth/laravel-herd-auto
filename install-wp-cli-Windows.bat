@echo off
setlocal

rem Run as administrator, AveYo: ps\vbs version
1>nul 2>nul fltmc || (
	set "_=call "%~dpfx0" %*" & powershell -nop -c start cmd -args '/d/x/r',$env:_ -verb runas || (
	>"%temp%\Elevate.vbs" echo CreateObject^("Shell.Application"^).ShellExecute "%~dpfx0", "%*" , "", "runas", 1
	>nul "%temp%\Elevate.vbs" & del /q "%temp%\Elevate.vbs" )
	exit)

set "herd_bin_dir=%USERPROFILE%\.config\herd\bin"

if not exist "%herd_bin_dir%" (
    echo You need to install Herd first.
    echo Download it from https://herd.laravel.com/
    exit /b 1
)

cd /d "%herd_bin_dir%" || exit /b 1

curl -L -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar

echo @ECHO OFF > wp.bat
echo php "%%~dp0wp-cli.phar" %%* >> wp.bat

echo.
echo ✅ WP-CLI installed successfully for Herd
echo 👉 Try: wp --info
endlocal
