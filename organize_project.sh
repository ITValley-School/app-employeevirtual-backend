#!/bin/bash
# ================================================================
# SCRIPT DE ORGANIZAÇÃO - EMPLOYEEVIRTUAL
# ================================================================
# Purpose: Organize all project files into proper folder structure
# Version: 1.0
# Date: September 2025
# ================================================================

echo "🗂️  Starting EmployeeVirtual project organization..."
echo "📁 Creating organized folder structure..."

# ================================================================
# MOVE DATABASE SCRIPTS
# ================================================================
echo "📊 Moving database scripts..."

# Current database scripts (KEEP - PRODUCTION READY)
mv database_schema_super_clean.sql scripts/database/
mv drop_all_tables_clean.sql scripts/database/
mv reinstall_complete_clean.sql scripts/database/
mv DATABASE_FINAL_USAGE_GUIDE.md docs/database/

# Old database scripts (MOVE TO TEMP)
mv database_final_supercorrigido.sql temp/
mv drop_all_tables.sql temp/
mv reinstall_complete.sql temp/
mv create_admin_user.sql temp/
mv insert_test_data.sql temp/

# ================================================================
# MOVE DOCUMENTATION
# ================================================================
echo "📚 Moving documentation..."

# API Documentation
mv API_DOCUMENTATION.md docs/api/
mv EmployeeVirtual_Agents_API.postman_collection.json docs/api/

# Authentication Documentation
mv AUTENTICACAO.md docs/auth/
mv auth_md_technical.md docs/auth/
mv JWT_Auth_Documentation.md docs/auth/ 2>/dev/null || echo "File not found: JWT_Auth_Documentation.md"

# Pydantic AI Documentation
mv ANALISE_PYDANTIC_AI.md docs/pydantic-ai/
mv ANALISE_FINAL_PYDANTIC_AI.md docs/pydantic-ai/
mv IMPLEMENTACAO_PYDANTIC_AI.md docs/pydantic-ai/
mv COMO_EXECUTAR_AGENTES_PYDANTIC_AI.md docs/pydantic-ai/

# General Documentation
mv ARQUITETURA.md docs/
mv INSTALLATION.md docs/
mv database_documentation.md docs/database/

# ================================================================
# MOVE OLD/TEMPORARY DOCUMENTATION
# ================================================================
echo "🗃️  Moving old documentation to temp..."

mv MELHORIAS_SCHEMA_SQL.md temp/
mv OTIMIZACOES_INDICES.md temp/
mv FINALIZACAO_IMPLEMENTACAO.md temp/

# ================================================================
# MOVE SETUP SCRIPTS
# ================================================================
echo "⚙️  Moving setup scripts..."

mv entrypoint.sh scripts/setup/
mv startup.sh scripts/setup/
mv web.config scripts/setup/

# ================================================================
# MOVE TEST FILES
# ================================================================
echo "🧪 Moving test files..."

mv test_agent_implementation.py temp/

# ================================================================
# MOVE PDF FILES TO TEMP
# ================================================================
echo "📄 Moving PDF files to temp..."

mv *.pdf temp/ 2>/dev/null || echo "No PDF files found"

# ================================================================
# CLEAN UP REQUIREMENTS
# ================================================================
echo "📦 Organizing requirements..."

# Keep main requirements.txt in root
# Move minimal version to temp
mv requirements.minimal.txt temp/

echo "✅ Organization completed!"
echo ""
echo "📁 NEW FOLDER STRUCTURE:"
echo "  📊 scripts/database/     - Production database scripts"
echo "  📊 scripts/setup/        - Server setup scripts"
echo "  📚 docs/                 - All documentation"
echo "  📚 docs/api/             - API documentation"
echo "  📚 docs/auth/            - Authentication docs"
echo "  📚 docs/database/        - Database documentation"
echo "  📚 docs/pydantic-ai/     - Pydantic AI documentation"
echo "  🗃️  temp/                - Old/temporary files"
echo ""
echo "🎯 READY FOR PRODUCTION!"
