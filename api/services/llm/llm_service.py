from typing import Dict, List
import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Erro: API key da OpenAI não está configurada")
            raise ValueError("API key não configurada")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=self.api_key,
            temperature=0.1,
            max_tokens=150
        )

    def _clean_response(self, text: str) -> str:
        """Limpa e formata a resposta do LLM"""
        # Remove espaços e quebras de linha extras
        text = re.sub(r'\s+', ' ', text)
        # Remove aspas e caracteres especiais
        text = text.replace('"', '').replace('`', '')
        # Remove prefixos comuns
        text = re.sub(r'^(Resposta:|R:|Assistant:|A:)', '', text)
        return text.strip()

    def generate_response(self, prompt: str) -> str:
        """Gera uma resposta usando o LLM"""
        try:
            messages = [
                SystemMessage(content=(
                    "Você é um assistente objetivo que analisa documentos "
                    "e responde perguntas usando apenas as informações fornecidas. "
                    "Mantenha as respostas curtas e diretas."
                )),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            cleaned_text = self._clean_response(response.content)
            
            # Limita o tamanho da resposta
            if len(cleaned_text.split()) > 50:
                cleaned_text = " ".join(cleaned_text.split()[:50]) + "..."
            
            return cleaned_text if cleaned_text else "Não foi possível gerar uma resposta adequada."
            
        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            return "Erro ao processar sua solicitação."

    def generate_section_summary(self, section_text: str) -> str:
        """Gera um resumo de uma seção do documento"""
        try:
            prompt = f"""
            Faça um resumo conciso desta seção do documento em até 2 linhas.
            Mantenha apenas as informações mais importantes.

            Seção:
            {section_text}
            """
            
            return self.generate_response(prompt)
        except Exception as e:
            print(f"Erro ao gerar resumo: {str(e)}")
            return ""