# Script para Gerar PDF do Roteiro de Testes
# EmployeeVirtual - Gerador de PDF

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputName = "ROTEIRO_TESTES_EMPLOYEEVIRTUAL",
    
    [Parameter(Mandatory=$false)]
    [switch]$OpenAfterGeneration = $true
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HtmlFile = Join-Path $ScriptDir "ROTEIRO_TESTES_PARA_PDF.html"
$PdfFile = Join-Path $ScriptDir "$OutputName.pdf"

Write-Host "📄 Gerador de PDF - Roteiro de Testes EmployeeVirtual" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se arquivo HTML existe
if (!(Test-Path $HtmlFile)) {
    Write-Error "❌ Arquivo HTML não encontrado: $HtmlFile"
    exit 1
}

Write-Host "✅ Arquivo HTML encontrado: $HtmlFile" -ForegroundColor Green

# Métodos de conversão disponíveis
Write-Host ""
Write-Host "🔍 Verificando métodos de conversão disponíveis..." -ForegroundColor Yellow

$methods = @()

# Método 1: wkhtmltopdf (recomendado)
try {
    $wkVersion = wkhtmltopdf --version 2>$null
    if ($?) {
        $methods += "wkhtmltopdf"
        Write-Host "✅ wkhtmltopdf encontrado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  wkhtmltopdf não encontrado" -ForegroundColor Yellow
}

# Método 2: Chrome/Chromium headless
try {
    $chromeExe = Get-Command "chrome.exe" -ErrorAction SilentlyContinue
    if ($chromeExe) {
        $methods += "chrome"
        Write-Host "✅ Google Chrome encontrado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Google Chrome não encontrado" -ForegroundColor Yellow
}

# Método 3: Edge headless (Windows)
try {
    $edgeExe = Get-Command "msedge.exe" -ErrorAction SilentlyContinue
    if ($edgeExe) {
        $methods += "edge"
        Write-Host "✅ Microsoft Edge encontrado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Microsoft Edge não encontrado" -ForegroundColor Yellow
}

# Método 4: Firefox headless
try {
    $firefoxExe = Get-Command "firefox.exe" -ErrorAction SilentlyContinue
    if ($firefoxExe) {
        $methods += "firefox"
        Write-Host "✅ Firefox encontrado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Firefox não encontrado" -ForegroundColor Yellow
}

if ($methods.Count -eq 0) {
    Write-Host ""
    Write-Host "❌ Nenhum método de conversão disponível!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Opções para instalar:" -ForegroundColor Yellow
    Write-Host "  1. wkhtmltopdf (recomendado):"
    Write-Host "     - Download: https://wkhtmltopdf.org/downloads.html"
    Write-Host "     - Instalar e adicionar ao PATH"
    Write-Host ""
    Write-Host "  2. Google Chrome:"
    Write-Host "     - Download: https://www.google.com/chrome/"
    Write-Host "     - Instalar normalmente"
    Write-Host ""
    Write-Host "  3. Microsoft Edge (já instalado no Windows 10+)"
    Write-Host ""
    Write-Host "🌐 Alternativa: Abra o arquivo HTML no navegador e use Ctrl+P para imprimir em PDF"
    Write-Host "   Arquivo: $HtmlFile"
    
    if ($OpenAfterGeneration) {
        Write-Host ""
        Write-Host "🌐 Abrindo arquivo HTML no navegador padrão..." -ForegroundColor Cyan
        Start-Process $HtmlFile
    }
    
    exit 1
}

Write-Host ""
Write-Host "🚀 Gerando PDF usando: $($methods[0])" -ForegroundColor Green

$success = $false

switch ($methods[0]) {
    "wkhtmltopdf" {
        Write-Host "📄 Convertendo com wkhtmltopdf..." -ForegroundColor Cyan
        try {
            & wkhtmltopdf --page-size A4 --margin-top 1cm --margin-bottom 1cm --margin-left 1cm --margin-right 1cm --print-media-type --enable-local-file-access $HtmlFile $PdfFile
            if ($?) {
                $success = $true
            }
        } catch {
            Write-Host "❌ Erro ao converter com wkhtmltopdf: $_" -ForegroundColor Red
        }
    }
    
    "chrome" {
        Write-Host "📄 Convertendo com Google Chrome..." -ForegroundColor Cyan
        try {
            & chrome.exe --headless --disable-gpu --print-to-pdf=$PdfFile --virtual-time-budget=5000 $HtmlFile
            Start-Sleep -Seconds 3
            if (Test-Path $PdfFile) {
                $success = $true
            }
        } catch {
            Write-Host "❌ Erro ao converter com Chrome: $_" -ForegroundColor Red
        }
    }
    
    "edge" {
        Write-Host "📄 Convertendo com Microsoft Edge..." -ForegroundColor Cyan
        try {
            & msedge.exe --headless --disable-gpu --print-to-pdf=$PdfFile --virtual-time-budget=5000 $HtmlFile
            Start-Sleep -Seconds 3
            if (Test-Path $PdfFile) {
                $success = $true
            }
        } catch {
            Write-Host "❌ Erro ao converter com Edge: $_" -ForegroundColor Red
        }
    }
    
    "firefox" {
        Write-Host "📄 Convertendo com Firefox..." -ForegroundColor Cyan
        Write-Host "⚠️  Firefox requer configuração manual para PDF headless" -ForegroundColor Yellow
        Write-Host "🌐 Abrindo arquivo no Firefox para conversão manual..." -ForegroundColor Cyan
        & firefox.exe $HtmlFile
        Write-Host "💡 Use Ctrl+P no Firefox e selecione 'Salvar como PDF'" -ForegroundColor Yellow
        $success = $false
    }
}

Write-Host ""
if ($success -and (Test-Path $PdfFile)) {
    Write-Host "✅ PDF gerado com sucesso!" -ForegroundColor Green
    Write-Host "📁 Arquivo salvo: $PdfFile" -ForegroundColor White
    
    $fileSize = (Get-Item $PdfFile).Length
    $fileSizeKB = [math]::Round($fileSize / 1KB, 2)
    Write-Host "📊 Tamanho: $fileSizeKB KB" -ForegroundColor Gray
    
    if ($OpenAfterGeneration) {
        Write-Host ""
        Write-Host "🔍 Abrindo PDF..." -ForegroundColor Cyan
        Start-Process $PdfFile
    }
    
    Write-Host ""
    Write-Host "📧 Arquivo pronto para compartilhar com a equipe!" -ForegroundColor Green
    
} else {
    Write-Host "❌ Falha na geração do PDF" -ForegroundColor Red
    Write-Host ""
    Write-Host "🌐 Alternativa: Abrindo arquivo HTML no navegador..." -ForegroundColor Yellow
    Write-Host "💡 Use Ctrl+P no navegador e selecione 'Salvar como PDF'" -ForegroundColor Yellow
    
    if ($OpenAfterGeneration) {
        Start-Process $HtmlFile
    }
}

Write-Host ""
Write-Host "📚 Arquivos disponíveis:" -ForegroundColor Cyan
Write-Host "  📄 HTML: $HtmlFile" -ForegroundColor White
if (Test-Path $PdfFile) {
    Write-Host "  📄 PDF:  $PdfFile" -ForegroundColor White
}
Write-Host "  📝 MD:   ROTEIRO_TESTES_COMPLETO.md" -ForegroundColor White

Write-Host ""
Write-Host "✨ Concluído!" -ForegroundColor Green
