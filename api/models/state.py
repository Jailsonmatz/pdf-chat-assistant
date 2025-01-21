from typing import TypedDict, List, Optional, Dict
from langchain_core.messages import BaseMessage

class DocumentInfo(TypedDict):
    content: str
    sections: Dict[str, str]
    metadata: Dict[str, any]

class WebResult(TypedDict):
    text: str
    url: str
    relevance: float

class ConversationState(TypedDict):
    document: DocumentInfo
    conversation_history: List[BaseMessage]
    current_question: str
    web_results: List[WebResult]
    selected_strategy: str
    answer: Optional[str]
    error: Optional[str]