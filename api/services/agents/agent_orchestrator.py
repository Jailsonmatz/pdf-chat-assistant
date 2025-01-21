from typing import List, Dict, Any
from api.services.agents.base_agent import BaseAgent
from api.services.agents.document_agent import DocumentAgent
from api.services.agents.web_agent import WebAgent
from api.models.state import ConversationState
from api.services.memory.conversation_memory import ConversationMemory

class AgentOrchestrator:
    """
    Orquestrador dos agentes do sistema.
    Implementa RF04 e RF05
    """
    
    def __init__(self):
        self.agents: List[BaseAgent] = [
            DocumentAgent(),
            WebAgent()
        ]
        self.memory = ConversationMemory()
        
    async def process_question(self, state: ConversationState) -> ConversationState:
        """Processa uma pergunta usando os agentes disponíveis"""
        try:
            # Atualiza o histórico da conversa
            state = self.memory.update_history(state)
            
            # Verifica se a pergunta está totalmente fora do contexto
            max_similarity = max(
                agent.can_handle(state)
                for agent in self.agents
            )
            
            if max_similarity < 0.2:
                state["answer"] = "Esta pergunta parece não ter relação com o contexto fornecido. Por favor, reformule ou faça uma pergunta relacionada ao documento."
                state["selected_strategy"] = "out_of_context"
                return state

            # Primeira tentativa com DocumentAgent
            doc_agent = self.agents[0]  # DocumentAgent
            doc_confidence = doc_agent.can_handle(state)
            
            if doc_confidence > 0.3:
                state = await doc_agent.execute(state)
                
                # Se encontrou resposta satisfatória no documento
                if state["answer"] and "NAO_ENCONTRADO" not in state["answer"]:
                    return state

            # Se necessário, tenta com WebAgent
            web_agent = self.agents[1]  # WebAgent
            web_confidence = web_agent.can_handle(state)
            
            if web_confidence > 0.3:
                web_state = await web_agent.execute(state)
                
                # Se o DocumentAgent encontrou algo parcial, combina as respostas
                if state["answer"] and "NAO_ENCONTRADO" not in state["answer"]:
                    combined_answer = self._combine_responses(
                        state["answer"],
                        web_state["answer"]
                    )
                    state["answer"] = combined_answer
                    state["web_results"] = web_state["web_results"]
                    state["selected_strategy"] = "combined"
                else:
                    state = web_state

            return state
            
        except Exception as e:
            state["error"] = f"Erro no orchestrator: {str(e)}"
            return state

    def _combine_responses(self, doc_response: str, web_response: str) -> str:
        """Combina respostas do documento e da web de forma coerente"""
        try:
            # Remove mensagens de não encontrado
            if "NAO_ENCONTRADO" in doc_response:
                return web_response
            if "NAO_ENCONTRADO" in web_response:
                return doc_response
                
            # Formata a resposta combinada
            return f"""
            Do documento: {doc_response}
            
            Informações complementares: {web_response}
            """.strip()
            
        except Exception as e:
            print(f"Erro ao combinar respostas: {str(e)}")
            return doc_response  # Fallback para resposta do documento

    def _select_best_agent(self, state: ConversationState) -> BaseAgent:
        """Seleciona o melhor agente para a pergunta atual"""
        try:
            # Calcula confiança de cada agente
            agent_scores = [
                (agent, agent.can_handle(state))
                for agent in self.agents
            ]
            
            # Ordena por confiança
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Retorna o agente com maior confiança
            return agent_scores[0][0]
            
        except Exception as e:
            print(f"Erro ao selecionar agente: {str(e)}")
            return self.agents[0]  # Fallback para DocumentAgent

    async def _process_with_timeout(self, agent: BaseAgent, state: ConversationState) -> ConversationState:
        """Executa um agente com timeout"""
        try:
            # Define timeout de 4.5 segundos (para respeitar RNF02)
            return await agent.execute(state)
        except Exception as e:
            state["error"] = f"Timeout ou erro ao executar agente: {str(e)}"
            return state