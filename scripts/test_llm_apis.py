#!/usr/bin/env python3
"""
Script para testar as APIs de gerenciamento de chaves LLM
"""
import requests
import json
import time
from typing import Dict, Any

# Configuração
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class LLMKeyAPITester:
    """Classe para testar as APIs de chaves LLM"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        
    def print_separator(self, title: str):
        """Imprime um separador visual"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Imprime mensagem informativa"""
        print(f"ℹ️ {message}")
    
    def test_connection(self) -> bool:
        """Testa conexão com a API"""
        try:
            response = requests.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.print_success("Conexão com a API estabelecida")
                return True
            else:
                self.print_error(f"Falha na conexão: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Erro de conexão: {e}")
            return False
    
    def register_test_user(self) -> bool:
        """Registra usuário de teste"""
        try:
            self.print_info("Registrando usuário de teste...")
            
            data = {
                "name": "Usuário Teste",
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "plan": "pro"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=data
            )
            
            if response.status_code in [200, 201, 422]:  # 422 = usuário já existe
                self.print_success("Usuário de teste configurado")
                return True
            else:
                self.print_error(f"Falha no registro: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro no registro: {e}")
            return False
    
    def authenticate_user(self) -> bool:
        """Autentica o usuário de teste"""
        try:
            self.print_info("Autenticando usuário...")
            
            data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("access_token")
                self.user_id = result.get("user", {}).get("id")
                
                if self.auth_token and self.user_id:
                    self.print_success("Usuário autenticado com sucesso")
                    return True
                else:
                    self.print_error("Token ou ID do usuário não encontrado")
                    return False
            else:
                self.print_error(f"Falha na autenticação: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro na autenticação: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers com token de autenticação"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_providers_endpoint(self) -> bool:
        """Testa endpoint de provedores disponíveis"""
        try:
            self.print_info("Testando endpoint de provedores...")
            
            response = requests.get(
                f"{self.base_url}/api/llm/providers",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                providers = result.get("providers", [])
                self.print_success(f"Provedores encontrados: {len(providers)}")
                
                for provider in providers[:3]:  # Mostrar apenas os primeiros 3
                    print(f"   - {provider['name']} ({provider['value']})")
                
                return True
            else:
                self.print_error(f"Falha ao obter provedores: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao testar provedores: {e}")
            return False
    
    def test_create_user_key(self) -> str:
        """Testa criação de chave do usuário"""
        try:
            self.print_info("Testando criação de chave do usuário...")
            
            data = {
                "provider": "openai",
                "api_key": "sk-test-key-123456789",
                "usage_limit": 100.00,
                "is_active": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/llm/user/keys",
                json=data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                key_id = result.get("id")
                self.print_success(f"Chave criada com sucesso: {key_id}")
                return key_id
            else:
                self.print_error(f"Falha ao criar chave: {response.status_code}")
                if response.text:
                    print(f"   Resposta: {response.text}")
                return None
                
        except Exception as e:
            self.print_error(f"Erro ao criar chave: {e}")
            return None
    
    def test_get_user_keys(self) -> bool:
        """Testa listagem de chaves do usuário"""
        try:
            self.print_info("Testando listagem de chaves do usuário...")
            
            response = requests.get(
                f"{self.base_url}/api/llm/user/keys",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                keys = result if isinstance(result, list) else []
                self.print_success(f"Chaves encontradas: {len(keys)}")
                
                for key in keys:
                    print(f"   - {key['provider']} (ID: {key['id'][:8]}...)")
                
                return True
            else:
                self.print_error(f"Falha ao listar chaves: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao listar chaves: {e}")
            return False
    
    def test_validate_api_key(self) -> bool:
        """Testa validação de chave API"""
        try:
            self.print_info("Testando validação de chave API...")
            
            data = {
                "provider": "openai",
                "api_key": "sk-test-key-123456789"
            }
            
            response = requests.post(
                f"{self.base_url}/api/llm/validate",
                json=data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                is_valid = result.get("is_valid", False)
                message = result.get("message", "")
                
                if is_valid:
                    self.print_success(f"Chave válida: {message}")
                else:
                    self.print_info(f"Chave inválida (esperado): {message}")
                
                return True
            else:
                self.print_error(f"Falha na validação: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro na validação: {e}")
            return False
    
    def test_usage_stats(self) -> bool:
        """Testa endpoint de estatísticas de uso"""
        try:
            self.print_info("Testando estatísticas de uso...")
            
            response = requests.get(
                f"{self.base_url}/api/llm/usage/stats",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                user_keys = result.get("user_keys", [])
                system_keys = result.get("system_keys", [])
                total_usage = result.get("total_usage", 0)
                
                self.print_success("Estatísticas obtidas com sucesso")
                print(f"   - Chaves do usuário: {len(user_keys)}")
                print(f"   - Chaves do sistema: {len(system_keys)}")
                print(f"   - Uso total: {total_usage}")
                
                return True
            else:
                self.print_error(f"Falha ao obter estatísticas: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao obter estatísticas: {e}")
            return False
    
    def test_update_user_key(self, key_id: str) -> bool:
        """Testa atualização de chave do usuário"""
        try:
            self.print_info("Testando atualização de chave...")
            
            data = {
                "usage_limit": 200.00,
                "is_active": True
            }
            
            response = requests.put(
                f"{self.base_url}/api/llm/user/keys/{key_id}",
                json=data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                new_limit = result.get("usage_limit")
                self.print_success(f"Chave atualizada: novo limite = {new_limit}")
                return True
            else:
                self.print_error(f"Falha ao atualizar chave: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao atualizar chave: {e}")
            return False
    
    def test_delete_user_key(self, key_id: str) -> bool:
        """Testa remoção de chave do usuário"""
        try:
            self.print_info("Testando remoção de chave...")
            
            response = requests.delete(
                f"{self.base_url}/api/llm/user/keys/{key_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("message", "")
                self.print_success(f"Chave removida: {message}")
                return True
            else:
                self.print_error(f"Falha ao remover chave: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao remover chave: {e}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        self.print_separator("INICIANDO TESTES DAS APIS DE CHAVES LLM")
        
        # Teste de conexão
        if not self.test_connection():
            return False
        
        # Configuração do usuário
        if not self.register_test_user():
            return False
        
        if not self.authenticate_user():
            return False
        
        # Testes das APIs
        tests = [
            ("Provedores disponíveis", self.test_providers_endpoint),
            ("Criação de chave", lambda: self.test_create_user_key()),
            ("Listagem de chaves", self.test_get_user_keys),
            ("Validação de chave", self.test_validate_api_key),
            ("Estatísticas de uso", self.test_usage_stats),
        ]
        
        results = []
        created_key_id = None
        
        for test_name, test_func in tests:
            self.print_separator(f"TESTE: {test_name}")
            
            if test_name == "Criação de chave":
                created_key_id = test_func()
                results.append((test_name, created_key_id is not None))
            else:
                success = test_func()
                results.append((test_name, success))
            
            time.sleep(1)  # Pausa entre testes
        
        # Testes que dependem de chave criada
        if created_key_id:
            self.print_separator("TESTE: Atualização de chave")
            update_success = self.test_update_user_key(created_key_id)
            results.append(("Atualização de chave", update_success))
            
            self.print_separator("TESTE: Remoção de chave")
            delete_success = self.test_delete_user_key(created_key_id)
            results.append(("Remoção de chave", delete_success))
        
        # Resumo dos resultados
        self.print_separator("RESUMO DOS TESTES")
        
        total_tests = len(results)
        passed_tests = sum(1 for _, success in results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total de testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Reprovados: {failed_tests}")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detalhes dos testes:")
        for test_name, success in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"   {status} - {test_name}")
        
        if failed_tests == 0:
            self.print_success("🎉 TODOS OS TESTES PASSARAM!")
        else:
            self.print_error(f"⚠️ {failed_tests} teste(s) falharam")
        
        return failed_tests == 0

def main():
    """Função principal"""
    print("🚀 EmployeeVirtual - Testador de APIs de Chaves LLM")
    print("=" * 60)
    
    tester = LLMKeyAPITester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        exit(1)

if __name__ == "__main__":
    main()
