from typing import Dict, Any
from .base_agent import BaseAgent
from ...models.state import ConversationState
from api.services.llm.llm_service import LLMService
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentAgent(BaseAgent):
    def __init__(self):
        self.llm = LLMService()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def can_handle(self, state: ConversationState) -> float:
        """
        Determina se a pergunta está relacionada ao documento
        através de análise de similaridade semântica
        """
        try:
            # Calcula similaridade entre a pergunta e o conteúdo do documento
            similarity = self._calculate_similarity(
                state["current_question"],
                state["document"]["content"]
            )
            
            # Verifica histórico de conversa para manter contexto
            if state["conversation_history"]:
                last_messages = state["conversation_history"][-3:]  # últimas 3 mensagens
                context_similarity = max(
                    self._calculate_similarity(
                        state["current_question"],
                        str(msg.content)
                    )
                    for msg in last_messages
                )
                # Aumenta a pontuação se houver contexto relevante
                similarity = max(similarity, context_similarity)
            
            return similarity
        except Exception as e:
            print(f"Erro ao calcular capacidade do DocumentAgent: {e}")
            return 0.0

    async def execute(self, state: ConversationState) -> ConversationState:
        """Processa a pergunta usando o documento como contexto"""
        try:
            # Cria base de conhecimento vetorial
            texts = [
                state["document"]["content"]
            ] + list(state["document"]["sections"].values())
            
            db = FAISS.from_texts(texts, self.embeddings)
            relevant_docs = db.similarity_search(
                state["current_question"],
                k=2
            )
            context = " ".join(doc.page_content for doc in relevant_docs)
            
            # Gera resposta baseada no contexto
            prompt = f"""
            Com base no seguinte contexto do documento, responda à pergunta.
            Se a informação não estiver disponível no contexto, responda exatamente: NAO_ENCONTRADO

            Contexto:
            {context}

            Pergunta: {state["current_question"]}

            Lembre-se: 
            - Use apenas informações do contexto
            - Seja direto e objetivo
            - Responda em até 3 linhas
            """
            
            answer = self.llm.generate_response(prompt)
            state["answer"] = answer
            state["selected_strategy"] = "document"
            
            return state
            
        except Exception as e:
            state["error"] = f"Erro no DocumentAgent: {str(e)}"
            return state