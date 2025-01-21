from typing import List, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from api.models.state import ConversationState
from langchain_community.embeddings import HuggingFaceEmbeddings

class ConversationMemory:
    """
    Gerencia o histórico da conversa e mantém o contexto
    """
    
    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def update_history(self, state: ConversationState) -> ConversationState:
        """Atualiza o histórico da conversa no estado"""
        try:
            # Adiciona a nova pergunta ao histórico
            state["conversation_history"].append(
                HumanMessage(content=state["current_question"])
            )
            
            # Se houver uma resposta anterior, adiciona também
            if state.get("answer"):
                state["conversation_history"].append(
                    AIMessage(content=state["answer"])
                )
            
            # Mantém apenas as últimas mensagens
            if len(state["conversation_history"]) > self.max_history * 2:
                state["conversation_history"] = state["conversation_history"][-self.max_history*2:]
            
            return state
            
        except Exception as e:
            print(f"Erro ao atualizar histórico: {str(e)}")
            return state

    def get_relevant_history(self, state: ConversationState, question: str) -> List[BaseMessage]:
        """Retorna as mensagens do histórico relevantes para a pergunta atual"""
        try:
            # Gera embedding para a pergunta atual
            question_embedding = self.embeddings.embed_query(question)
            
            # Calcula similaridade com cada mensagem do histórico
            message_scores = []
            for msg in state["conversation_history"]:
                msg_embedding = self.embeddings.embed_query(msg.content)
                similarity = self._calculate_similarity(
                    question_embedding,
                    msg_embedding
                )
                message_scores.append((similarity, msg))
            
            # Ordena por similaridade
            message_scores.sort(reverse=True)
            
            # Retorna as mensagens mais relevantes
            return [msg for _, msg in message_scores[:4]]
            
        except Exception as e:
            print(f"Erro ao obter histórico relevante: {str(e)}")
            return state["conversation_history"][-4:]

    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calcula similaridade de cosseno entre embeddings"""
        try:
            # Calcula produto escalar
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Calcula magnitudes
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 * magnitude2 == 0:
                return 0.0
                
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            print(f"Erro ao calcular similaridade: {str(e)}")
            return 0.0

    def get_conversation_summary(self, state: ConversationState) -> str:
        """Gera um resumo da conversa atual"""
        try:
            if not state["conversation_history"]:
                return ""
                
            # Pega as últimas mensagens
            recent_messages = state["conversation_history"][-6:]  # últimas 3 interações
            
            # Formata o resumo
            summary = []
            for i in range(0, len(recent_messages), 2):
                if i + 1 < len(recent_messages):
                    q = recent_messages[i].content
                    a = recent_messages[i + 1].content
                    summary.append(f"Q: {q}\nA: {a}")
            
            return "\n\n".join(summary)
            
        except Exception as e:
            print(f"Erro ao gerar resumo: {str(e)}")
            return ""

    def clear_history(self, state: ConversationState) -> ConversationState:
        """Limpa o histórico da conversa"""
        state["conversation_history"] = []
        return state