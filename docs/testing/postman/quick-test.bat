@echo off
REM EmployeeVirtual API - Quick Test Runner
REM Executa testes básicos usando Newman

echo.
echo ==========================================
echo  EmployeeVirtual API - Quick Test Runner
echo ==========================================
echo.

REM Verificar se Newman está instalado
newman --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Newman nao encontrado!
    echo.
    echo Para instalar Newman:
    echo   npm install -g newman
    echo.
    pause
    exit /b 1
)

echo ✅ Newman encontrado

REM Verificar se o servidor está rodando
echo.
echo 🔍 Verificando servidor local...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Servidor local nao responde na porta 8000
    echo    Certifique-se de que o servidor esta rodando:
    echo    python main.py
    echo.
) else (
    echo ✅ Servidor local respondendo
)

REM Executar testes básicos
echo.
echo 🧪 Executando testes básicos...
echo.

newman run EmployeeVirtual_Agents_API.postman_collection.json ^
  -e EmployeeVirtual-Development.postman_environment.json ^
  --folder "🔐 Autenticação" ^
  --folder "👤 Usuários" ^
  --reporters cli ^
  --timeout-request 30000 ^
  --delay-request 1000

echo.
if %errorlevel% equ 0 (
    echo ✅ Testes básicos concluídos com sucesso!
) else (
    echo ❌ Alguns testes falharam
)

echo.
echo 💡 Para testes mais avançados, use:
echo    .\run-tests.ps1
echo.
pause
