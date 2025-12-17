# 📄 Guia de Gerenciamento de Documentos RAG - Frontend

## 📋 Visão Geral

Este guia explica como usar as novas funcionalidades de gerenciamento de documentos RAG no frontend. Permite listar, visualizar, editar metadados e remover documentos associados aos agentes.

## 🎯 Endpoints Disponíveis

### 1. Listar Documentos
- **Endpoint**: `GET /api/agents/{agent_id}/documents`
- **Descrição**: Lista todos os documentos associados a um agente
- **Autenticação**: Requerida (Bearer Token)

### 2. Deletar Documento
- **Endpoint**: `DELETE /api/agents/{agent_id}/documents/{document_id}`
- **Descrição**: Remove um documento do agente (MongoDB + Pinecone)
- **Autenticação**: Requerida (Bearer Token)

### 3. Atualizar Metadados
- **Endpoint**: `PATCH /api/agents/{agent_id}/documents/{document_id}/metadata`
- **Descrição**: Atualiza metadados de um documento
- **Autenticação**: Requerida (Bearer Token)

### 4. Upload de Documento (já existente)
- **Endpoint**: `POST /api/agents/{agent_id}/documents`
- **Descrição**: Faz upload de um PDF para o agente
- **Autenticação**: Requerida (Bearer Token)

---

## 💻 Implementação no Frontend

### 1. Serviço de API (Service Layer)

Crie um serviço para centralizar as chamadas à API:

```typescript
// services/agentDocumentsService.ts

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface AgentDocument {
  id: string;
  agent_id: string;
  user_id: string;
  file_name: string;
  metadata: Record<string, any>;
  vector_response?: Record<string, any>;
  created_at: string;
  updated_at?: string;
  mongo_error?: boolean;
}

interface AgentDocumentListResponse {
  documents: AgentDocument[];
  total: number;
  agent_id: string;
}

interface AgentDocumentDeleteResponse {
  success: boolean;
  document_id: string;
  file_name?: string;
  vector_db_response?: Record<string, any>;
  mongo_deleted: boolean;
  message?: string;
}

class AgentDocumentsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Lista todos os documentos de um agente
   */
  async listDocuments(agentId: string): Promise<AgentDocumentListResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/agents/${agentId}/documents`,
      {
        method: 'GET',
        headers: this.getAuthHeaders(),
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Token inválido ou expirado');
      }
      if (response.status === 404) {
        throw new Error('Agente não encontrado');
      }
      throw new Error(`Erro ao listar documentos: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Deleta um documento do agente
   */
  async deleteDocument(
    agentId: string,
    documentId: string
  ): Promise<AgentDocumentDeleteResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/agents/${agentId}/documents/${documentId}`,
      {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Token inválido ou expirado');
      }
      if (response.status === 404) {
        throw new Error('Documento não encontrado');
      }
      throw new Error(`Erro ao deletar documento: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Atualiza metadados de um documento
   */
  async updateDocumentMetadata(
    agentId: string,
    documentId: string,
    metadata: Record<string, any>
  ): Promise<AgentDocument> {
    const response = await fetch(
      `${API_BASE_URL}/api/agents/${agentId}/documents/${documentId}/metadata`,
      {
        method: 'PATCH',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ metadata }),
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Token inválido ou expirado');
      }
      if (response.status === 404) {
        throw new Error('Documento não encontrado');
      }
      throw new Error(`Erro ao atualizar metadados: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Faz upload de um documento PDF
   */
  async uploadDocument(
    agentId: string,
    file: File,
    metadata?: Record<string, any>
  ): Promise<any> {
    const formData = new FormData();
    formData.append('filepdf', file);
    
    if (metadata) {
      formData.append('metadone', JSON.stringify(metadata));
    }

    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `${API_BASE_URL}/api/agents/${agentId}/documents`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Não definir Content-Type - o browser define automaticamente com boundary
        },
        body: formData,
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Token inválido ou expirado');
      }
      if (response.status === 400) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao fazer upload do documento');
      }
      throw new Error(`Erro ao fazer upload: ${response.statusText}`);
    }

    return await response.json();
  }
}

export const agentDocumentsService = new AgentDocumentsService();
export type { AgentDocument, AgentDocumentListResponse, AgentDocumentDeleteResponse };
```

---

### 2. Hook React para Gerenciar Documentos

```typescript
// hooks/useAgentDocuments.ts

import { useState, useEffect, useCallback } from 'react';
import { agentDocumentsService, AgentDocument } from '../services/agentDocumentsService';

interface UseAgentDocumentsReturn {
  documents: AgentDocument[];
  loading: boolean;
  error: string | null;
  total: number;
  refreshDocuments: () => Promise<void>;
  deleteDocument: (documentId: string) => Promise<void>;
  updateMetadata: (documentId: string, metadata: Record<string, any>) => Promise<void>;
  uploadDocument: (file: File, metadata?: Record<string, any>) => Promise<void>;
}

export function useAgentDocuments(agentId: string | null): UseAgentDocumentsReturn {
  const [documents, setDocuments] = useState<AgentDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadDocuments = useCallback(async () => {
    if (!agentId) {
      setDocuments([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await agentDocumentsService.listDocuments(agentId);
      setDocuments(response.documents);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar documentos');
      setDocuments([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const deleteDocument = useCallback(async (documentId: string) => {
    if (!agentId) return;

    setLoading(true);
    setError(null);

    try {
      await agentDocumentsService.deleteDocument(agentId, documentId);
      // Recarrega a lista após deletar
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao deletar documento');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [agentId, loadDocuments]);

  const updateMetadata = useCallback(async (
    documentId: string,
    metadata: Record<string, any>
  ) => {
    if (!agentId) return;

    setLoading(true);
    setError(null);

    try {
      const updated = await agentDocumentsService.updateDocumentMetadata(
        agentId,
        documentId,
        metadata
      );
      // Atualiza o documento na lista
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId ? updated : doc
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar metadados');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  const uploadDocument = useCallback(async (
    file: File,
    metadata?: Record<string, any>
  ) => {
    if (!agentId) return;

    setLoading(true);
    setError(null);

    try {
      await agentDocumentsService.uploadDocument(agentId, file, metadata);
      // Recarrega a lista após upload
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao fazer upload');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [agentId, loadDocuments]);

  return {
    documents,
    loading,
    error,
    total,
    refreshDocuments: loadDocuments,
    deleteDocument,
    updateMetadata,
    uploadDocument,
  };
}
```

---

### 3. Componente React para Listar Documentos

```typescript
// components/AgentDocumentsList.tsx

import React, { useState } from 'react';
import { useAgentDocuments } from '../hooks/useAgentDocuments';
import { AgentDocument } from '../services/agentDocumentsService';

interface AgentDocumentsListProps {
  agentId: string;
}

export function AgentDocumentsList({ agentId }: AgentDocumentsListProps) {
  const {
    documents,
    loading,
    error,
    total,
    deleteDocument,
    updateMetadata,
  } = useAgentDocuments(agentId);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editMetadata, setEditMetadata] = useState<Record<string, any>>({});

  const handleDelete = async (documentId: string, fileName: string) => {
    if (!window.confirm(`Tem certeza que deseja remover o documento "${fileName}"?`)) {
      return;
    }

    try {
      await deleteDocument(documentId);
      alert('Documento removido com sucesso!');
    } catch (err) {
      alert(`Erro ao remover documento: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const handleEditStart = (document: AgentDocument) => {
    setEditingId(document.id);
    setEditMetadata({ ...document.metadata });
  };

  const handleEditSave = async (documentId: string) => {
    try {
      await updateMetadata(documentId, editMetadata);
      setEditingId(null);
      alert('Metadados atualizados com sucesso!');
    } catch (err) {
      alert(`Erro ao atualizar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const handleEditCancel = () => {
    setEditingId(null);
    setEditMetadata({});
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (loading && documents.length === 0) {
    return (
      <div className="documents-loading">
        <p>Carregando documentos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="documents-error">
        <p>Erro: {error}</p>
        <button onClick={() => window.location.reload()}>Tentar novamente</button>
      </div>
    );
  }

  return (
    <div className="agent-documents-list">
      <div className="documents-header">
        <h3>Documentos do Agente</h3>
        <span className="documents-count">Total: {total}</span>
      </div>

      {documents.length === 0 ? (
        <div className="documents-empty">
          <p>Nenhum documento encontrado. Faça upload de um PDF para começar.</p>
        </div>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <div className="document-header">
                <h4>{doc.file_name}</h4>
                {doc.mongo_error && (
                  <span className="warning-badge">⚠️ Aviso MongoDB</span>
                )}
              </div>

              <div className="document-info">
                <p><strong>ID:</strong> {doc.id}</p>
                <p><strong>Criado em:</strong> {formatDate(doc.created_at)}</p>
                {doc.updated_at && (
                  <p><strong>Atualizado em:</strong> {formatDate(doc.updated_at)}</p>
                )}
              </div>

              {editingId === doc.id ? (
                <div className="document-edit">
                  <h5>Editar Metadados:</h5>
                  <textarea
                    value={JSON.stringify(editMetadata, null, 2)}
                    onChange={(e) => {
                      try {
                        setEditMetadata(JSON.parse(e.target.value));
                      } catch {
                        // Ignora JSON inválido temporariamente
                      }
                    }}
                    rows={6}
                    style={{ width: '100%', fontFamily: 'monospace' }}
                  />
                  <div className="edit-actions">
                    <button onClick={() => handleEditSave(doc.id)}>Salvar</button>
                    <button onClick={handleEditCancel}>Cancelar</button>
                  </div>
                </div>
              ) : (
                <div className="document-metadata">
                  <h5>Metadados:</h5>
                  <pre>{JSON.stringify(doc.metadata, null, 2)}</pre>
                </div>
              )}

              <div className="document-actions">
                <button
                  onClick={() => handleEditStart(doc)}
                  disabled={editingId === doc.id}
                >
                  ✏️ Editar Metadados
                </button>
                <button
                  onClick={() => handleDelete(doc.id, doc.file_name)}
                  className="delete-button"
                >
                  🗑️ Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### 4. Componente para Upload de Documentos

```typescript
// components/AgentDocumentUpload.tsx

import React, { useState } from 'react';
import { useAgentDocuments } from '../hooks/useAgentDocuments';

interface AgentDocumentUploadProps {
  agentId: string;
}

export function AgentDocumentUpload({ agentId }: AgentDocumentUploadProps) {
  const { uploadDocument, loading, error } = useAgentDocuments(agentId);
  const [file, setFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState<string>('{}');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        alert('Apenas arquivos PDF são permitidos!');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      alert('Selecione um arquivo PDF');
      return;
    }

    let parsedMetadata = {};
    try {
      parsedMetadata = JSON.parse(metadata);
    } catch {
      alert('Metadados devem ser um JSON válido');
      return;
    }

    setUploading(true);
    try {
      await uploadDocument(file, parsedMetadata);
      alert('Documento enviado com sucesso!');
      setFile(null);
      setMetadata('{}');
      // Limpa o input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      alert(`Erro ao fazer upload: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <h3>Enviar Novo Documento</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="file-input">Arquivo PDF:</label>
          <input
            id="file-input"
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            disabled={uploading}
            required
          />
          {file && (
            <p className="file-info">
              Arquivo selecionado: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="metadata-input">Metadados (JSON opcional):</label>
          <textarea
            id="metadata-input"
            value={metadata}
            onChange={(e) => setMetadata(e.target.value)}
            rows={4}
            placeholder='{"categoria": "manual", "versao": "1.0"}'
            disabled={uploading}
            style={{ fontFamily: 'monospace', width: '100%' }}
          />
        </div>

        <button type="submit" disabled={!file || uploading}>
          {uploading ? 'Enviando...' : 'Enviar Documento'}
        </button>

        {error && <p className="error-message">Erro: {error}</p>}
      </form>
    </div>
  );
}
```

---

### 5. Componente Completo de Gerenciamento

```typescript
// components/AgentDocumentsManager.tsx

import React, { useState } from 'react';
import { AgentDocumentsList } from './AgentDocumentsList';
import { AgentDocumentUpload } from './AgentDocumentUpload';

interface AgentDocumentsManagerProps {
  agentId: string;
}

export function AgentDocumentsManager({ agentId }: AgentDocumentsManagerProps) {
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="agent-documents-manager">
      <div className="manager-header">
        <h2>Gerenciamento de Documentos RAG</h2>
        <button onClick={() => setShowUpload(!showUpload)}>
          {showUpload ? 'Ocultar Upload' : 'Mostrar Upload'}
        </button>
      </div>

      {showUpload && <AgentDocumentUpload agentId={agentId} />}

      <AgentDocumentsList agentId={agentId} />
    </div>
  );
}
```

---

## 🎨 Exemplo de CSS (Opcional)

```css
/* styles/agentDocuments.css */

.agent-documents-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.documents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.documents-count {
  color: #666;
  font-size: 14px;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.document-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.document-header h4 {
  margin: 0;
  color: #333;
}

.warning-badge {
  background: #fff3cd;
  color: #856404;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.document-info {
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.document-info p {
  margin: 4px 0;
}

.document-metadata {
  margin-bottom: 12px;
}

.document-metadata h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.document-metadata pre {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.document-edit {
  margin-bottom: 12px;
}

.document-edit h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.edit-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.document-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.document-actions button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.document-actions button:not(.delete-button) {
  background: #007bff;
  color: white;
}

.document-actions button.delete-button {
  background: #dc3545;
  color: white;
}

.document-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.document-upload {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.document-upload h3 {
  margin-top: 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input[type="file"] {
  width: 100%;
  padding: 8px;
}

.file-info {
  margin-top: 8px;
  font-size: 14px;
  color: #666;
}

.error-message {
  color: #dc3545;
  margin-top: 8px;
}

.documents-loading,
.documents-error,
.documents-empty {
  text-align: center;
  padding: 40px;
  color: #666;
}
```

---

## 📱 Exemplo de Uso em uma Página

```typescript
// pages/AgentDetailsPage.tsx

import React from 'react';
import { useParams } from 'react-router-dom';
import { AgentDocumentsManager } from '../components/AgentDocumentsManager';

export function AgentDetailsPage() {
  const { agentId } = useParams<{ agentId: string }>();

  if (!agentId) {
    return <div>Agente não encontrado</div>;
  }

  return (
    <div>
      <h1>Detalhes do Agente</h1>
      <AgentDocumentsManager agentId={agentId} />
    </div>
  );
}
```

---

## 🔄 Fluxo Completo de Uso

### 1. Upload de Documento
```typescript
// Usuário seleciona arquivo PDF
// Opcionalmente adiciona metadados em JSON
// Clica em "Enviar Documento"
// Sistema faz upload para Pinecone e salva metadados no MongoDB
```

### 2. Listar Documentos
```typescript
// Ao abrir a página de documentos do agente
// Sistema carrega automaticamente todos os documentos
// Exibe lista com nome, data, metadados
```

### 3. Editar Metadados
```typescript
// Usuário clica em "Editar Metadados"
// Edita JSON dos metadados
// Clica em "Salvar"
// Sistema atualiza apenas no MongoDB (Pinecone não é afetado)
```

### 4. Deletar Documento
```typescript
// Usuário clica em "Remover"
// Sistema confirma ação
// Remove do MongoDB e do Pinecone
// Atualiza lista automaticamente
```

---

## ⚠️ Tratamento de Erros

### Erros Comuns e Como Tratar

1. **401 Unauthorized**
   - Token expirado ou inválido
   - **Ação**: Redirecionar para login ou renovar token

2. **404 Not Found**
   - Agente ou documento não encontrado
   - **Ação**: Mostrar mensagem amigável ao usuário

3. **400 Bad Request**
   - Dados inválidos (ex: JSON malformado)
   - **Ação**: Validar dados antes de enviar

4. **500 Internal Server Error**
   - Erro no servidor
   - **Ação**: Tentar novamente ou mostrar mensagem de erro

---

## 🚀 Melhorias Futuras (Opcional)

1. **Paginação**: Para listas grandes de documentos
2. **Filtros**: Por nome, data, tipo de arquivo
3. **Busca**: Pesquisar documentos por nome ou metadados
4. **Preview**: Visualizar conteúdo do PDF antes de deletar
5. **Download**: Baixar arquivo original (se armazenado)
6. **Validação**: Validar JSON de metadados antes de enviar
7. **Drag & Drop**: Upload arrastando arquivo
8. **Progress Bar**: Mostrar progresso do upload

---

## 📚 Recursos Adicionais

- **Swagger UI**: `/docs` - Documentação interativa da API
- **Postman**: Coleção de testes disponível
- **Logs**: Verificar logs do backend para debug

---

## ✅ Checklist de Implementação

- [ ] Criar serviço de API (`agentDocumentsService.ts`)
- [ ] Criar hook React (`useAgentDocuments.ts`)
- [ ] Criar componente de lista (`AgentDocumentsList.tsx`)
- [ ] Criar componente de upload (`AgentDocumentUpload.tsx`)
- [ ] Criar componente gerenciador (`AgentDocumentsManager.tsx`)
- [ ] Adicionar estilos CSS
- [ ] Testar upload de documento
- [ ] Testar listagem de documentos
- [ ] Testar edição de metadados
- [ ] Testar deleção de documentos
- [ ] Tratar erros de autenticação
- [ ] Adicionar loading states
- [ ] Adicionar confirmações para ações destrutivas

---

**Pronto para usar!** 🎉

