from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
import re

class TextAnalyzer:
    """
    Analisa e estrutura o texto extraído dos documentos
    Complementa RF01 e RF02
    """
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def analyze_content(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Analisa o conteúdo do texto e suas seções"""
        try:
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            avg_sentence_length = len(words) / len(sentences) if sentences else 0

            analysis = {
                "structure_type": self._identify_structure_type(text),
                "main_topics": self._extract_main_topics(text),
                "language_metrics": {
                    "num_sentences": len(sentences),
                    "num_words": len(words),
                    "avg_sentence_length": round(avg_sentence_length, 2),
                    "language": self._detect_language(text)
                }
            }

            return analysis

        except Exception as e:
            print(f"Erro na análise de texto: {str(e)}")
            return {
                "structure_type": "unknown",
                "main_topics": [],
                "language_metrics": {
                    "num_sentences": 0,
                    "num_words": 0,
                    "avg_sentence_length": 0.0,
                    "language": "unknown"
                }
            }

    def _extract_main_topics(self, text: str) -> List[str]:
        """Extrai os principais tópicos do texto"""
        topics = []
        words = text.lower().split()
        word_freq = {}
        
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'e', 'que'}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word for word, _ in sorted_words[:5]]
        
        return topics

    def _identify_structure_type(self, text: str) -> str:
        """Identifica o tipo de estrutura do texto"""
        has_bullets = bool(re.search(r'[•\-\*]|\d+\.', text))
        has_tables = len(re.findall(r'\||\t|    ', text)) > len(text.split('\n')) / 2
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        has_paragraphs = len(paragraphs) > 1
        
        if has_tables:
            return "tabular"
        elif has_bullets:
            return "list"
        elif has_paragraphs:
            return "continuous_text"
        else:
            return "mixed"

    def _detect_language(self, text: str) -> str:
        """Detecta o idioma do texto (simplificado)"""
        pt_indicators = ['ção', 'são', 'ões', 'para', 'como', 'está']
        en_indicators = ['the', 'is', 'are', 'and', 'for', 'with']
        
        text_lower = text.lower()
        pt_count = sum(1 for word in pt_indicators if word in text_lower)
        en_count = sum(1 for word in en_indicators if word in text_lower)
        
        return "pt" if pt_count >= en_count else "en"