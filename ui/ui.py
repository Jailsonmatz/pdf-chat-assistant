import streamlit as st
import requests
from io import BytesIO
import time

# Configuração da página
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📚",
    layout="wide"
)

# Inicialização do estado da sessão
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_info" not in st.session_state:
    st.session_state.pdf_info = None

def check_server_connection():
    """Verifica se o servidor está disponível"""
    try:
        response = requests.get("http://api:8000/health", timeout=2)
        return response.ok
    except:
        return False

def wait_for_server(timeout=30):
    """Espera o servidor iniciar"""
    with st.spinner('Aguardando o servidor iniciar...'):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_server_connection():
                return True
            time.sleep(2)
    return False

# Verifica a conexão com o servidor
if not check_server_connection():
    if not wait_for_server():
        st.error("O servidor está offline. Por favor, aguarde alguns instantes e recarregue a página.")
        st.stop()

# Interface principal
st.title("PDF Chat Assistant")

# Sidebar para upload e controles
with st.sidebar:
    st.header("📄 Upload de Documento")
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")
    
    # Upload de arquivo
    if uploaded_file and (not st.session_state.pdf_info or uploaded_file.name != st.session_state.pdf_info.get("name")):
        with st.spinner('Processando o documento...'):
            try:
                # Prepara o arquivo para envio
                pdf_contents = uploaded_file.read()
                files = {"file": (uploaded_file.name, pdf_contents, "application/pdf")}
                
                # Processa o PDF
                response = requests.post(
                    "http://api:8000/process-pdf",
                    files=files,
                    timeout=65  # 65 segundos para permitir o timeout de 60s do servidor
                )
                
                if response.ok:
                    data = response.json()
                    st.session_state.conversation_id = data["conversation_id"]
                    st.session_state.pdf_info = {
                        "name": uploaded_file.name,
                        "analysis": data["analysis"]
                    }
                    
                    # Limpa mensagens anteriores
                    st.session_state.messages = []
                    
                    # Adiciona mensagem de boas-vindas
                    welcome_msg = f"O arquivo '{uploaded_file.name}' foi carregado com sucesso! Como posso ajudar?"
                    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                    st.rerun()
                else:
                    st.error(f"Erro ao processar o PDF: {response.text}")
                    
            except requests.Timeout:
                st.error("O processamento do documento excedeu o tempo limite. Tente um arquivo menor.")
            except Exception as e:
                st.error(f"Erro ao processar o documento: {str(e)}")

    # Botão para nova conversa
    if st.button("🗑️ Nova Conversa"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.pdf_info = None
        st.rerun()

    # Mostra informações do documento atual
    if st.session_state.pdf_info:
        st.header("📊 Informações do Documento")
        with st.expander("Ver detalhes"):
            analysis = st.session_state.pdf_info["analysis"]
            
            st.subheader("Estrutura")
            st.write(f"Tipo: {analysis.get('structure_type', 'N/A')}")
            
            st.subheader("Tópicos Principais")
            for topic in analysis.get('main_topics', []):
                st.write(f"• {topic}")
            
            if 'language_metrics' in analysis:
                st.subheader("Métricas")
                metrics = analysis['language_metrics']
                st.write(f"Idioma: {metrics.get('language', 'N/A')}")
                st.write(f"Sentenças: {metrics.get('num_sentences', 0)}")
                st.write(f"Palavras: {metrics.get('num_words', 0)}")

# Área principal de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua pergunta sobre o documento..."):
    if not st.session_state.conversation_id:
        st.error("Por favor, carregue um documento primeiro.")
    else:
        # Adiciona a pergunta ao chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                with st.spinner('Processando sua pergunta...'):
                    # Verifica conexão
                    if not check_server_connection():
                        st.error("O servidor está temporariamente indisponível.")
                        st.stop()
                    
                    # Envia a pergunta
                    response = requests.post(
                        f"http://api:8000/chat/{st.session_state.conversation_id}",
                        params={
                            "question": prompt
                        },
                        timeout=30  # 30 segundos 
                    )
                    
                    if response.ok:
                        data = response.json()
                        answer = data["answer"]
                        
                        # Se tem resultados da web, formata a resposta
                        if data.get("web_results"):
                            web_result = data["web_results"][0]  # Pega apenas o primeiro resultado
                            answer = f"{answer}\n\nFonte: [{web_result['url']}]"
                        
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error("Erro ao processar sua pergunta. Por favor, tente novamente.")

        except requests.Timeout:
            st.error("A resposta demorou muito. Por favor, tente novamente.")
        except Exception as e:
            st.error(f"Erro ao processar sua pergunta: {str(e)}")

# CSS para melhor aparência
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatInput {
        padding: 0.5rem;
    }
    .st-emotion-cache-1h5k6m9 {
        max-width: 1200px;
    }
</style>
""", unsafe_allow_html=True)