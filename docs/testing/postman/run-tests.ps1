# EmployeeVirtual API Test Runner
# Executa testes da API usando Newman

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Development", "Production")]
    [string]$Environment = "Development",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "smoke", "auth", "agents", "chats", "flows", "files", "dashboard")]
    [string]$TestSuite = "full",
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$OpenReport = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$DelayBetweenRequests = 1000,
    
    [Parameter(Mandatory=$false)]
    [int]$RequestTimeout = 30000
)

# Configurações
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Collection = Join-Path $ScriptDir "EmployeeVirtual_Agents_API.postman_collection.json"
$EnvFile = Join-Path $ScriptDir "EmployeeVirtual-$Environment.postman_environment.json"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$ReportPrefix = "newman-report-$Environment-$TestSuite-$Timestamp"

# Verificar pré-requisitos
Write-Host "🔍 Verificando pré-requisitos..." -ForegroundColor Cyan

# Verificar Newman
try {
    $newmanVersion = newman --version 2>$null
    Write-Host "✅ Newman encontrado: v$newmanVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Newman não encontrado. Instale com: npm install -g newman"
    exit 1
}

# Verificar arquivos
if (!(Test-Path $Collection)) {
    Write-Error "❌ Coleção não encontrada: $Collection"
    exit 1
}

if (!(Test-Path $EnvFile)) {
    Write-Error "❌ Ambiente não encontrado: $EnvFile"
    exit 1
}

Write-Host "✅ Arquivos encontrados" -ForegroundColor Green

# Verificar servidor (se Development)
if ($Environment -eq "Development") {
    Write-Host "🔍 Verificando servidor local..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Servidor local respondendo: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Warning "⚠️  Servidor local não respondeu. Continuando mesmo assim..."
    }
}

# Configurar comandos baseados no tipo de teste
$NewmanArgs = @(
    "run", $Collection,
    "-e", $EnvFile,
    "--timeout-request", $RequestTimeout,
    "--delay-request", $DelayBetweenRequests,
    "--reporters", "cli"
)

# Adicionar relatórios se solicitado
if ($GenerateReport) {
    $NewmanArgs += @(
        "--reporters", "cli,html,json",
        "--reporter-html-export", "$ReportPrefix.html",
        "--reporter-json-export", "$ReportPrefix.json"
    )
}

# Configurar pasta/teste específico
switch ($TestSuite) {
    "smoke" {
        $NewmanArgs += @("--folder", "🔐 Autenticação", "--folder", "👤 Usuários")
        Write-Host "🧪 Executando testes de Smoke (Autenticação + Usuários)" -ForegroundColor Yellow
    }
    "auth" {
        $NewmanArgs += @("--folder", "🔐 Autenticação")
        Write-Host "🔐 Executando testes de Autenticação" -ForegroundColor Yellow
    }
    "agents" {
        $NewmanArgs += @("--folder", "🤖 Agentes")
        Write-Host "🤖 Executando testes de Agentes" -ForegroundColor Yellow
    }
    "chats" {
        $NewmanArgs += @("--folder", "💬 Chats")
        Write-Host "💬 Executando testes de Chats" -ForegroundColor Yellow
    }
    "flows" {
        $NewmanArgs += @("--folder", "🔄 Fluxos")
        Write-Host "🔄 Executando testes de Fluxos" -ForegroundColor Yellow
    }
    "files" {
        $NewmanArgs += @("--folder", "📁 Arquivos")
        Write-Host "📁 Executando testes de Arquivos" -ForegroundColor Yellow
    }
    "dashboard" {
        $NewmanArgs += @("--folder", "📊 Dashboard")
        Write-Host "📊 Executando testes de Dashboard" -ForegroundColor Yellow
    }
    "full" {
        Write-Host "🚀 Executando suite completa de testes" -ForegroundColor Yellow
    }
}

Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Test Suite: $TestSuite" -ForegroundColor Cyan
Write-Host "Generate Report: $GenerateReport" -ForegroundColor Cyan

# Executar Newman
Write-Host "`n🏃‍♂️ Executando testes..." -ForegroundColor Yellow
Write-Host "Comando: newman $($NewmanArgs -join ' ')" -ForegroundColor Gray

$StartTime = Get-Date
& newman @NewmanArgs
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

# Resultados
Write-Host "`n📊 Execução concluída!" -ForegroundColor Green
Write-Host "⏱️  Duração: $($Duration.ToString('mm\:ss'))" -ForegroundColor Cyan

if ($GenerateReport) {
    Write-Host "`n📄 Relatórios gerados:" -ForegroundColor Green
    if (Test-Path "$ReportPrefix.html") {
        Write-Host "  📄 HTML: $ReportPrefix.html" -ForegroundColor White
    }
    if (Test-Path "$ReportPrefix.json") {
        Write-Host "  📄 JSON: $ReportPrefix.json" -ForegroundColor White
    }
    
    if ($OpenReport -and (Test-Path "$ReportPrefix.html")) {
        Write-Host "`n🌐 Abrindo relatório HTML..." -ForegroundColor Cyan
        Start-Process "$ReportPrefix.html"
    }
}

Write-Host "`n✨ Concluído!" -ForegroundColor Green

# Exemplos de uso no final
Write-Host "`n💡 Exemplos de uso:" -ForegroundColor Yellow
Write-Host "  .\run-tests.ps1                              # Teste completo em Development" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 -TestSuite smoke              # Apenas smoke tests" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 -Environment Production       # Testes em produção" -ForegroundColor Gray
Write-Host "  .\run-tests.ps1 -TestSuite auth -OpenReport   # Só auth + abrir relatório" -ForegroundColor Gray
