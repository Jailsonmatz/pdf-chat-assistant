from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import asyncio

from api.services.extractors.pdf_extractor import PDFExtractor
from api.services.extractors.text_analyzer import TextAnalyzer
from api.services.agents.agent_orchestrator import AgentOrchestrator
from api.models.state import ConversationState, DocumentInfo
from api.models.responses import (
    HealthResponse,
    ChatResponse,
    ProcessPDFResponse,
    ConversationHistoryResponse
)

app = FastAPI(title="PDF Chat API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serviços
pdf_extractor = PDFExtractor()
text_analyzer = TextAnalyzer()
agent_orchestrator = AgentOrchestrator()

# Estado global (em produção, usar banco de dados)
CONVERSATION_STATES: Dict[str, ConversationState] = {}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check"""
    return HealthResponse(status="ok")

@app.post("/process-pdf", response_model=ProcessPDFResponse)
async def process_pdf(file: UploadFile = File(...)):
    """
    Processa um arquivo PDF
    Implementa RF01, RF02, RF12
    """
    try:
        # RNF01: Limite de tamanho do arquivo
        file_size = 0
        chunk_size = 1024
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(400, "Arquivo excede 10MB")
        await file.seek(0)
        
        # Processa o PDF
        start_time = asyncio.get_event_loop().time()
        doc_info: DocumentInfo = await pdf_extractor.process_pdf(file.file)
        
        # Analisa o conteúdo
        analysis = text_analyzer.analyze_content(
            doc_info["content"],
            doc_info["sections"]
        )
        
        # Verifica tempo de processamento (RNF01)
        process_time = asyncio.get_event_loop().time() - start_time
        if process_time > 60:  # 1 minuto
            print(f"Alerta: Processamento demorou {process_time:.2f} segundos")
        
        # Inicializa estado da conversa
        conversation_id = f"conv_{len(CONVERSATION_STATES) + 1}"
        CONVERSATION_STATES[conversation_id] = {
            "document": doc_info,
            "conversation_history": [],
            "current_question": "",
            "web_results": [],
            "selected_strategy": "",
            "answer": None,
            "error": None
        }
        
        return ProcessPDFResponse(
            conversation_id=conversation_id,
            message="PDF processado com sucesso",
            analysis=analysis
        )
        
    except Exception as e:
        raise HTTPException(500, f"Erro ao processar PDF: {str(e)}")

@app.post("/chat/{conversation_id}", response_model=ChatResponse)
async def chat(
    conversation_id: str,
    question: str = Query(..., description="Pergunta sobre o documento"),
    force_web_search: bool = Query(False, description="Força busca na web")
):
    """
    Processa uma pergunta sobre o documento
    Implementa RF03, RF04, RF05, RF09, RF10
    """
    try:
        # Verifica se a conversa existe
        if conversation_id not in CONVERSATION_STATES:
            raise HTTPException(404, "Conversa não encontrada")
            
        state = CONVERSATION_STATES[conversation_id]
        state["current_question"] = question
        
        # RNF02: Timeout de 5 segundos
        start_time = asyncio.get_event_loop().time()
        
        # Processa a pergunta
        state = await agent_orchestrator.process_question(state)
        
        # Verifica tempo de resposta
        process_time = asyncio.get_event_loop().time() - start_time
        if process_time > 5:
            print(f"Alerta: Resposta demorou {process_time:.2f} segundos")
        
        # Atualiza estado
        CONVERSATION_STATES[conversation_id] = state
        
        return ChatResponse(
            answer=state["answer"],
            source=state["selected_strategy"],
            web_results=state["web_results"] if state["web_results"] else None
        )
        
    except Exception as e:
        raise HTTPException(500, f"Erro ao processar pergunta: {str(e)}")

@app.get("/conversations/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """Retorna o histórico da conversa"""
    if conversation_id not in CONVERSATION_STATES:
        raise HTTPException(404, "Conversa não encontrada")
        
    state = CONVERSATION_STATES[conversation_id]
    history = [
        {
            "role": msg.type,
            "content": msg.content
        }
        for msg in state["conversation_history"]
    ]
    
    return ConversationHistoryResponse(history=history)