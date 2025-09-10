#!/usr/bin/env python3
"""
Script para verificar conversas no banco de dados
"""
import sys
import os
from sqlalchemy import text
from datetime import datetime

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.database import engine, SessionLocal
from models.chat_models import Conversation, Message

def verificar_conversas():
    """Verifica conversas no banco de dados"""
    try:
        print("🔍 Verificando conversas no banco de dados...")
        print("=" * 50)
        
        with SessionLocal() as db:
            # Contar total de conversas
            total_conversations = db.query(Conversation).count()
            print(f"📊 Total de conversas: {total_conversations}")
            
            if total_conversations == 0:
                print("❌ Nenhuma conversa encontrada no banco de dados!")
                return
            
            # Listar conversas recentes
            print("\n📝 Últimas 10 conversas:")
            recent_conversations = (
                db.query(Conversation)
                .order_by(Conversation.created_at.desc())
                .limit(10)
                .all()
            )
            
            for i, conv in enumerate(recent_conversations, 1):
                # Contar mensagens da conversa
                message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
                
                print(f"\n{i}. Conversa ID: {conv.id}")
                print(f"   👤 User ID: {conv.user_id}")
                print(f"   🤖 Agent ID: {conv.agent_id}")
                print(f"   📝 Título: {conv.title or 'Sem título'}")
                print(f"   📊 Status: {conv.status}")
                print(f"   💬 Mensagens: {message_count}")
                print(f"   📅 Criada: {conv.created_at}")
                print(f"   📅 Última msg: {conv.last_message_at or 'N/A'}")
                
                # Mostrar algumas mensagens
                if message_count > 0:
                    messages = (
                        db.query(Message)
                        .filter(Message.conversation_id == conv.id)
                        .order_by(Message.created_at.desc())
                        .limit(3)
                        .all()
                    )
                    print("   📨 Últimas mensagens:")
                    for msg in messages:
                        content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                        print(f"      - [{msg.message_type}] {content_preview}")
            
            # Estatísticas por status
            print("\n📈 Estatísticas por status:")
            statuses = db.execute(
                text("SELECT status, COUNT(*) as count FROM empl.conversations GROUP BY status")
            ).fetchall()
            
            for status, count in statuses:
                print(f"   {status}: {count} conversas")
            
            # Mensagens por tipo
            print("\n💬 Mensagens por tipo:")
            message_types = db.execute(
                text("SELECT message_type, COUNT(*) as count FROM empl.messages GROUP BY message_type")
            ).fetchall()
            
            for msg_type, count in message_types:
                print(f"   {msg_type}: {count} mensagens")
                
            print("\n✅ Verificação concluída!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_conversas()
