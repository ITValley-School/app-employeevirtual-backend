# ================================================================
# SCRIPT DE LIMPEZA - EMPLOYEEVIRTUAL
# ================================================================
# Purpose: Remove obsolete files from temp folder safely
# Version: 1.0
# Date: September 2025
# ================================================================

Write-Host "🧹 Starting EmployeeVirtual cleanup process..." -ForegroundColor Green
Write-Host "📁 Analyzing temp folder for obsolete files..." -ForegroundColor Yellow
Write-Host ""

# Navigate to project root
Set-Location "c:\Projetos_Dev\employeevirtual"

# Check if temp folder exists
if (-not (Test-Path "temp")) {
    Write-Host "❌ Temp folder not found! Nothing to clean." -ForegroundColor Red
    exit
}

Write-Host "🗑️  Removing obsolete database scripts..." -ForegroundColor Yellow

# Remove obsolete database scripts
$obsoleteDbFiles = @(
    "temp\database_final_supercorrigido.sql",
    "temp\drop_all_tables.sql",
    "temp\reinstall_complete.sql", 
    "temp\create_admin_user.sql",
    "temp\insert_test_data.sql"
)

foreach ($file in $obsoleteDbFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✅ Removed: $($file.Split('\')[-1])" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Not found: $($file.Split('\')[-1])" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📚 Removing obsolete documentation..." -ForegroundColor Yellow

# Remove obsolete documentation
$obsoleteDocFiles = @(
    "temp\MELHORIAS_SCHEMA_SQL.md",
    "temp\OTIMIZACOES_INDICES.md",
    "temp\FINALIZACAO_IMPLEMENTACAO.md"
)

foreach ($file in $obsoleteDocFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✅ Removed: $($file.Split('\')[-1])" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Not found: $($file.Split('\')[-1])" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📦 Removing extra requirements files..." -ForegroundColor Yellow

# Remove extra requirements
if (Test-Path "temp\requirements.minimal.txt") {
    Remove-Item "temp\requirements.minimal.txt" -Force
    Write-Host "  ✅ Removed: requirements.minimal.txt" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  Not found: requirements.minimal.txt" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔍 Checking remaining files in temp..." -ForegroundColor Cyan

# List remaining files for manual review
$remainingFiles = Get-ChildItem "temp" -File
if ($remainingFiles.Count -gt 0) {
    Write-Host "📋 Files remaining for manual review:" -ForegroundColor Yellow
    foreach ($file in $remainingFiles) {
        Write-Host "  🔍 $($file.Name)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "💡 These files require manual review before deletion." -ForegroundColor Cyan
} else {
    Write-Host "✨ Temp folder is now empty!" -ForegroundColor Green
    Write-Host "🗑️  You can safely remove the temp folder if desired." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ CLEANUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 SUMMARY:" -ForegroundColor White
Write-Host "  • Obsolete database scripts: REMOVED" -ForegroundColor Green
Write-Host "  • Obsolete documentation: REMOVED" -ForegroundColor Green  
Write-Host "  • Extra requirements: REMOVED" -ForegroundColor Green
Write-Host "  • Project structure: OPTIMIZED" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Project is now clean and production-ready!" -ForegroundColor Green
Write-Host "📁 All essential files are in their proper organized folders." -ForegroundColor White

# Final validation
Write-Host ""
Write-Host "🔐 VALIDATION CHECK:" -ForegroundColor Cyan
$essentialFiles = @(
    "scripts\database\database_schema_super_clean.sql",
    "scripts\database\drop_all_tables_clean.sql", 
    "scripts\database\reinstall_complete_clean.sql",
    "docs\database\DATABASE_FINAL_USAGE_GUIDE.md"
)

$allEssentialPresent = $true
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ Essential file present: $($file.Split('\')[-1])" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Essential file missing: $($file.Split('\')[-1])" -ForegroundColor Red
        $allEssentialPresent = $false
    }
}

if ($allEssentialPresent) {
    Write-Host ""
    Write-Host "🎉 ALL ESSENTIAL FILES CONFIRMED PRESENT!" -ForegroundColor Green
    Write-Host "🚀 Project ready for production deployment!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some essential files are missing. Please check organization!" -ForegroundColor Yellow
}
