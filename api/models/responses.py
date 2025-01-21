from pydantic import BaseModel
from typing import Optional, List, Dict, Union

class HealthResponse(BaseModel):
    status: str

class WebResult(BaseModel):
    text: str
    url: str

class ChatResponse(BaseModel):
    answer: str
    source: Optional[str] = None
    web_results: Optional[List[WebResult]] = None

class LanguageMetrics(BaseModel):
    num_sentences: int
    num_words: int
    avg_sentence_length: float
    language: str

class DocumentAnalysis(BaseModel):
    structure_type: str
    main_topics: List[str]
    language_metrics: LanguageMetrics

class ProcessPDFResponse(BaseModel):
    conversation_id: str
    message: str
    analysis: DocumentAnalysis

class ConversationHistoryResponse(BaseModel):
    history: List[Dict[str, str]]