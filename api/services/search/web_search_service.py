import requests
from typing import List, Dict
import time

class WebSearchService:
    """
    Serviço de busca na web usando DuckDuckGo
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.max_results = 2  # Limitado a 2 resultados conforme RF07

    def search(self, query: str) -> List[Dict[str, str]]:
        """Realiza busca na web e retorna resultados formatados"""
        try:
            # Adiciona timestamp para evitar cache
            params = {
                "q": query,
                "format": "json",
                "t": int(time.time())
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            # Processa AbstractText e AbstractURL primeiro (geralmente mais relevantes)
            if data.get("AbstractText") and data.get("AbstractURL"):
                results.append({
                    "text": data["AbstractText"],
                    "url": data["AbstractURL"]
                })
                
            # Adiciona resultados relacionados se necessário
            for topic in data.get("RelatedTopics", []):
                if len(results) >= self.max_results:
                    break
                    
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "text": topic["Text"],
                        "url": topic["FirstURL"]
                    })
            
            # Filtra e limpa resultados
            cleaned_results = []
            for result in results:
                # Remove URLs muito longas
                if len(result["url"]) > 100:
                    result["url"] = result["url"][:97] + "..."
                # Remove textos muito longos
                if len(result["text"]) > 300:
                    result["text"] = result["text"][:297] + "..."
                cleaned_results.append(result)
            
            return cleaned_results[:self.max_results]
            
        except Exception as e:
            print(f"Erro na busca web: {str(e)}")
            return []

    def _is_result_relevant(self, query: str, result_text: str) -> bool:
        """
        Verifica se o resultado é relevante para a query
        Implementa parte do RF08
        """
        # Converte para minúsculas
        query = query.lower()
        text = result_text.lower()
        
        # Extrai palavras-chave da query (removendo stop words comuns)
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'é', 'são', 'com', 'em', 'no', 'na'}
        query_words = [w for w in query.split() if w not in stop_words]
        
        # Conta quantas palavras-chave aparecem no resultado
        matches = sum(1 for word in query_words if word in text)
        
        # Calcula porcentagem de palavras encontradas
        relevance = matches / len(query_words) if query_words else 0
        
        return relevance > 0.3  # threshold de 30%