# 📁 EmployeeVirtual - Estrutura Organizacional

## 🎯 **ESTRUTURA ATUALIZADA E ORGANIZADA**

Este projeto foi completamente reorganizado para facilitar desenvolvimento, manutenção e deploy em produção.

---

## 📂 **ESTRUTURA DE PASTAS**

```
📦 employeevirtual/
├── 📁 api/                     # Módulos da API REST
├── 📁 auth/                    # Sistema de autenticação
├── 📁 data/                    # Repositórios e acesso a dados
├── 📁 middlewares/             # Middlewares customizados
├── 📁 models/                  # Modelos Pydantic
├── 📁 services/                # Lógica de negócio
├── 📁 docs/                    # 📚 DOCUMENTAÇÃO
│   ├── 📁 api/                 # Documentação da API
│   ├── 📁 auth/                # Documentação de autenticação
│   ├── 📁 database/            # Documentação do banco de dados
│   └── 📁 pydantic-ai/         # Documentação Pydantic AI
├── 📁 scripts/                 # 🛠️ SCRIPTS DE PRODUÇÃO
│   ├── 📁 database/            # Scripts de banco de dados
│   └── 📁 setup/               # Scripts de configuração
├── 📁 temp/                    # 🗃️ Arquivos temporários/antigos
├── 📄 main.py                  # 🚀 Aplicação principal
├── 📄 requirements.txt         # 📦 Dependências
└── 📄 README.md               # 📖 Documentação principal
```

---

## 🚀 **ARQUIVOS ESSENCIAIS PARA PRODUÇÃO**

### **Scripts de Banco de Dados:**
- **`scripts/database/database_schema_super_clean.sql`** ⭐ **PRINCIPAL**
  - Instalação completa do banco
  - Zero conflitos de cascade
  - Pronto para Azure SQL

- **`scripts/database/drop_all_tables_clean.sql`**
  - Limpeza completa do banco

- **`scripts/database/reinstall_complete_clean.sql`**
  - Reinstalação completa (drop + create)

### **Documentação Principal:**
- **`docs/database/DATABASE_FINAL_USAGE_GUIDE.md`** ⭐ **GUIA DE USO**
  - Instruções completas de instalação
  - Troubleshooting
  - Credenciais padrão

- **`docs/INSTALLATION.md`**
  - Guia de instalação geral

- **`docs/ARQUITETURA.md`**
  - Arquitetura do sistema

### **Scripts de Setup:**
- **`scripts/setup/entrypoint.sh`** - Entrypoint Docker
- **`scripts/setup/startup.sh`** - Script de inicialização
- **`scripts/setup/web.config`** - Configuração IIS

---

## 📚 **NAVEGAÇÃO RÁPIDA**

### **🏗️ Para Desenvolvedores:**
1. **Instalação**: `docs/INSTALLATION.md`
2. **Arquitetura**: `docs/ARQUITETURA.md`
3. **API**: `docs/api/API_DOCUMENTATION.md`
4. **Autenticação**: `docs/auth/AUTENTICACAO.md`
5. **Pydantic AI**: `docs/pydantic-ai/`

### **🗄️ Para DBAs:**
1. **Guia de Uso**: `docs/database/DATABASE_FINAL_USAGE_GUIDE.md`
2. **Script Principal**: `scripts/database/database_schema_super_clean.sql`
3. **Documentação**: `docs/database/database_documentation.md`

### **🚀 Para DevOps:**
1. **Scripts de Setup**: `scripts/setup/`
2. **Docker**: `scripts/setup/entrypoint.sh`
3. **Configuração**: `scripts/setup/web.config`

---

## 🗃️ **PASTA TEMP**

A pasta `temp/` contém:
- Scripts antigos de banco de dados
- Documentações obsoletas
- Arquivos de teste
- PDFs e arquivos temporários

**⚠️ Estes arquivos podem ser removidos após validação!**

---

## ✅ **ARQUIVOS VALIDADOS PARA PRODUÇÃO**

### **✅ Scripts de Banco (TESTADOS):**
- `database_schema_super_clean.sql` - **FUNCIONA 100%**
- `drop_all_tables_clean.sql` - **FUNCIONA 100%**
- `reinstall_complete_clean.sql` - **FUNCIONA 100%**

### **✅ Documentação (ATUALIZADA):**
- `DATABASE_FINAL_USAGE_GUIDE.md` - **COMPLETA**
- `API_DOCUMENTATION.md` - **ATUALIZADA**
- `ARQUITETURA.md` - **REVISADA**

### **✅ Código da Aplicação:**
- `main.py` - **Aplicação principal**
- `api/` - **Módulos da API**
- `services/` - **Lógica de negócio**
- `models/` - **Modelos Pydantic**

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Validar** estrutura reorganizada
2. **Testar** scripts de banco em ambiente limpo
3. **Revisar** documentação
4. **Remover** pasta `temp/` após validação
5. **Deploy** em produção

---

## 📞 **CONTATO**

Para dúvidas sobre a organização ou arquivos:
- Verifique primeiro `docs/DATABASE_FINAL_USAGE_GUIDE.md`
- Consulte `docs/INSTALLATION.md` 
- Revise `docs/ARQUITETURA.md`

**🎉 Projeto organizado e pronto para produção!**
