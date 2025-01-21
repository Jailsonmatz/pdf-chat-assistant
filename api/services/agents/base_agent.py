from abc import ABC, abstractmethod
from typing import Dict, Any
from api.models.state import ConversationState
from langchain_community.embeddings import HuggingFaceEmbeddings

class BaseAgent(ABC):
    """Classe base abstrata para todos os agentes"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
    @abstractmethod
    def can_handle(self, state: ConversationState) -> float:
        """
        Determina se o agente pode lidar com o estado atual
        Retorna: Pontuação de 0 a 1 indicando a confiança do agente
        """
        pass

    @abstractmethod
    async def execute(self, state: ConversationState) -> ConversationState:
        """
        Executa a ação do agente
        Retorna: Estado atualizado após a execução
        """
        pass

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula a similaridade semântica entre dois textos"""
        try:
            # Gera embeddings para os textos
            embedding1 = self.embeddings.embed_query(text1)
            embedding2 = self.embeddings.embed_query(text2)

            # Calcula similaridade de cosseno
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 * magnitude2 == 0:
                return 0.0
                
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            print(f"Erro ao calcular similaridade: {str(e)}")
            # Fallback para cálculo mais simples em caso de erro
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            return intersection / union if union > 0 else 0.0

    def _should_use_web_search(self, state: ConversationState) -> bool:
        """Determina se deve usar busca na web"""
        # Verifica se é solicitação explícita
        question_lower = state["current_question"].lower()
        if "busque na web" in question_lower or "pesquise na internet" in question_lower:
            return True
            
        # Se não encontrou resposta no documento
        if state.get("answer") == "NAO_ENCONTRADO":
            return True
            
        # Se a similaridade com o documento é baixa
        similarity = self._calculate_similarity(
            state["current_question"],
            state["document"]["content"]
        )
        if similarity < 0.2:
            return True
            
        return False

    def _format_response(self, text: str) -> str:
        """Formata a resposta para o usuário"""
        # Remove quebras de linha extras
        text = ' '.join(text.split())
        
        # Remove prefixos comuns
        prefixes = ["Resposta:", "R:", "A:", "Assistant:"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                
        # Limita tamanho
        if len(text) > 500:
            text = text[:497] + "..."
            
        return text.strip()

    def _get_relevant_context(self, state: ConversationState) -> str:
        """Obtém contexto relevante do documento"""
        try:
            question = state["current_question"]
            sections = state["document"]["sections"]
            
            # Calcula similaridade com cada seção
            section_scores = []
            for section_name, content in sections.items():
                score = self._calculate_similarity(question, content)
                section_scores.append((score, content))
                
            # Ordena por similaridade e pega as 2 seções mais relevantes
            section_scores.sort(reverse=True)
            relevant_sections = [content for _, content in section_scores[:2]]
            
            return "\n\n".join(relevant_sections)
            
        except Exception as e:
            print(f"Erro ao obter contexto: {str(e)}")
            return state["document"]["content"]