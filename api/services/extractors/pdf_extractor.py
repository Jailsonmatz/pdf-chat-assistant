import pdfplumber
from typing import Dict, List, Any
import re
from api.models.state import DocumentInfo

class PDFExtractor:
    """
    Responsável por processar e extrair informações de PDFs
    """
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB (RNF01)

    async def process_pdf(self, file) -> DocumentInfo:
        """Processa o PDF e extrai informações estruturadas"""
        try:
            # Verifica tamanho do arquivo
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            if size > self.max_file_size:
                raise ValueError("Arquivo excede o tamanho máximo de 10MB")

            text_content = ""
            sections: Dict[str, str] = {}
            metadata: Dict[str, Any] = {}
            
            with pdfplumber.open(file) as pdf:
                metadata = {
                    "total_pages": len(pdf.pages),
                    "pdf_info": pdf.metadata
                }
                
                # Extrai texto de cada página
                current_section = "main"
                section_text = []
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Identifica possíveis títulos de seção
                        lines = text.split('\n')
                        for line in lines:
                            # Heurística para identificar títulos de seção
                            if len(line.strip()) < 100 and (
                                line.isupper() or 
                                re.match(r'^[\d.]+ [A-Z]', line) or
                                re.match(r'^[A-Z][a-z]+ \d+', line)
                            ):
                                if section_text:
                                    sections[current_section] = '\n'.join(section_text)
                                    section_text = []
                                current_section = line.strip()
                            else:
                                section_text.append(line)
                            
                        text_content += text + "\n"
                
                # Adiciona última seção
                if section_text:
                    sections[current_section] = '\n'.join(section_text)
                
                # Se não encontrou seções, usa o texto completo
                if not sections:
                    sections["main"] = text_content
                
                return {
                    "content": text_content,
                    "sections": sections,
                    "metadata": metadata
                }
                
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")

    def _detect_section_titles(self, text: str) -> List[str]:
        """Detecta possíveis títulos de seção no texto"""
        potential_titles = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Heurísticas para identificar títulos
            if (len(line) < 100 and  # Títulos geralmente são curtos
                (line.isupper() or  # Todo em maiúsculas
                 re.match(r'^\d+[\.\s]+[A-Z]', line) or  # Começa com número
                 re.match(r'^[A-Z][a-z]+\s+\d+', line) or  # Palavra capitalizada + número
                 line.endswith(':'))):  # Termina com dois pontos
                potential_titles.append(line)
        
        return potential_titles