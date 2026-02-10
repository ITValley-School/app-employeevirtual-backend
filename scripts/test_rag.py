#!/usr/bin/env python3
"""
Script de teste para o sistema RAG
Uso: python scripts/test_rag.py
"""
import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TOKEN = os.getenv("JWT_TOKEN", "")


def print_section(title: str):
    """Imprime seção formatada"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_create_agent() -> Optional[str]:
    """Teste 1: Criar agente"""
    print_section("TESTE 1: Criar Agente")
    
    url = f"{BASE_URL}/api/agents/"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Agente RAG Teste",
        "description": "Agente para testar sistema RAG",
        "type": "chatbot",
        "instructions": "Você é um assistente especializado em responder perguntas baseado em documentos enviados.",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        agent_id = data.get("id")
        print(f"✅ Agente criado com sucesso!")
        print(f"   ID: {agent_id}")
        print(f"   Nome: {data.get('name')}")
        return agent_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar agente: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Resposta: {e.response.text}")
        return None


def test_upload_document(agent_id: str, pdf_path: str) -> bool:
    """Teste 2: Upload de PDF"""
    print_section("TESTE 2: Upload de PDF")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return False
    
    url = f"{BASE_URL}/api/agents/{agent_id}/documents"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    metadata = {
        "curso": "IA",
        "modulo": "1",
        "topico": "RAG"
    }
    
    files = {"filepdf": open(pdf_path, "rb")}
    data = {"metadone": json.dumps(metadata)}
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        print(f"✅ PDF enviado com sucesso!")
        print(f"   Documento: {result.get('document', {}).get('file_name', 'N/A')}")
        print(f"   Vector DB: {result.get('vector_db_response', {}).get('message', 'N/A')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar PDF: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Resposta: {e.response.text}")
        return False
    finally:
        files["filepdf"].close()


def test_execute_agent(agent_id: str, message: str = None) -> bool:
    """Teste 3: Executar agente com RAG"""
    print_section("TESTE 3: Executar Agente (RAG)")
    
    if message is None:
        message = "O que você sabe sobre o conteúdo do documento que enviei?"
    
    url = f"{BASE_URL}/api/agents/{agent_id}/execute"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message,
        "context": {},
        "session_id": None
    }
    
    try:
        print(f"📤 Enviando pergunta: {message}")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Resposta recebida!")
        print(f"   Tempo de execução: {result.get('execution_time', 0):.2f}s")
        print(f"   Tokens usados: {result.get('tokens_used', 0)}")
        print(f"\n📝 Resposta do agente:")
        print(f"   {result.get('response', 'N/A')[:500]}...")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao executar agente: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Resposta: {e.response.text}")
        return False


def test_execute_without_docs(agent_id: str) -> bool:
    """Teste 4: Executar agente sem documentos (fallback)"""
    print_section("TESTE 4: Executar Agente SEM Documentos (Fallback)")
    
    url = f"{BASE_URL}/api/agents/{agent_id}/execute"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": "Olá, como você está?",
        "context": {},
        "session_id": None
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Resposta recebida (fallback)!")
        print(f"   Resposta: {result.get('response', 'N/A')[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("  TESTES DO SISTEMA RAG - EmployeeVirtual")
    print("="*60)
    
    if not TOKEN:
        print("\n⚠️  ATENÇÃO: Configure JWT_TOKEN no ambiente")
        print("   export JWT_TOKEN='seu_token_aqui'")
        print("\n   Ou defina no .env:")
        print("   JWT_TOKEN=seu_token_aqui")
        return
    
    # Teste 1: Criar agente
    agent_id = test_create_agent()
    if not agent_id:
        print("\n❌ Não foi possível continuar sem criar o agente")
        return
    
    # Teste 2: Upload PDF (opcional - precisa de arquivo)
    pdf_path = os.getenv("TEST_PDF_PATH", "")
    if pdf_path and os.path.exists(pdf_path):
        test_upload_document(agent_id, pdf_path)
    else:
        print("\n⚠️  Pulando upload de PDF (configure TEST_PDF_PATH ou envie manualmente)")
    
    # Teste 3: Executar com RAG
    if pdf_path and os.path.exists(pdf_path):
        test_execute_agent(agent_id)
    
    # Teste 4: Fallback
    # Criar outro agente sem documentos para testar fallback
    agent_id_2 = test_create_agent()
    if agent_id_2:
        test_execute_without_docs(agent_id_2)
    
    print_section("TESTES CONCLUÍDOS")
    print(f"✅ Agente criado: {agent_id}")
    print(f"📝 Próximos passos:")
    print(f"   1. Envie um PDF: POST /api/agents/{agent_id}/documents")
    print(f"   2. Execute: POST /api/agents/{agent_id}/execute")
    print(f"   3. Verifique logs do backend para ver fluxo RAG")


if __name__ == "__main__":
    main()


