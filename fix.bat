@echo off
powershell -File "%~dp0code-quality.ps1" -Fix %*
