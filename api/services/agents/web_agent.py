from typing import Dict, Any
from .base_agent import BaseAgent
from ...models.state import ConversationState, WebResult
from ..llm.llm_service import LLMService
from ..search.web_search_service import WebSearchService

class WebAgent(BaseAgent):
    def __init__(self):
        self.llm = LLMService()
        self.web_search = WebSearchService()

    def can_handle(self, state: ConversationState) -> float:
        """
        Determina se deve usar busca na web baseado em:
        1. Se o DocumentAgent não encontrou resposta
        2. Se o usuário solicitou explicitamente busca na web
        3. Se a pergunta tem baixa similaridade com o documento
        """
        # Verifica se é solicitação explícita de busca web
        if "busque na web" in state["current_question"].lower():
            return 1.0

        # Se já tem uma resposta do documento que não é NAO_ENCONTRADO
        if state.get("answer") and "NAO_ENCONTRADO" not in state["answer"]:
            return 0.0

        # Calcula similaridade com o documento
        doc_similarity = self._calculate_similarity(
            state["current_question"],
            state["document"]["content"]
        )

        # Se a similaridade for muito baixa, indica que devemos buscar na web
        if doc_similarity < 0.2:
            return 0.8

        return 0.3  # valor default baixo

    async def execute(self, state: ConversationState) -> ConversationState:
        """Realiza busca na web e processa os resultados"""
        try:
            # Realiza a busca
            results = self.web_search.search(state["current_question"])
            
            # Seleciona até 2 resultados mais relevantes
            relevant_results: List[WebResult] = []
            for result in results[:2]:
                relevance = self._calculate_similarity(
                    state["current_question"],
                    result["text"]
                )
                if relevance > 0.3:  # threshold de relevância
                    relevant_results.append({
                        "text": result["text"],
                        "url": result["url"],
                        "relevance": relevance
                    })
            
            if not relevant_results:
                state["answer"] = "Não encontrei informações relevantes sobre isso."
                state["selected_strategy"] = "web_no_results"
                return state

            # Se temos resultados relevantes
            web_context = "\n".join(r["text"] for r in relevant_results)
            
            prompt = f"""
            Com base nas informações encontradas na web, responda à pergunta de forma clara e direta.
            Use no máximo 3 linhas.

            Informações:
            {web_context}

            Pergunta: {state["current_question"]}
            """
            
            answer = self.llm.generate_response(prompt)
            
            # Adiciona os links no final da resposta
            links = [f"[{r['url']}]" for r in relevant_results[:1]]  # limita a 1 link
            if links:
                answer = f"{answer}\n\nFonte: {links[0]}"
            
            state["answer"] = answer
            state["web_results"] = relevant_results
            state["selected_strategy"] = "web"
            
            return state
            
        except Exception as e:
            state["error"] = f"Erro no WebAgent: {str(e)}"
            return state