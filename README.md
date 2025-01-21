# PDF Chat Assistant

Um assistente interativo para conversas contextuais sobre documentos PDF. Ele combina processamento local eficiente e busca na web, garantindo respostas relevantes e contextualizadas.

## 🎥 Demonstração


## 🚀 Instalação e Uso

#### Requisitos

##### Software
 - Docker 24.0 ou superior.
 - Docker Compose v2.0 ou superior.
 - Git.

##### Hardware Recomendado

- 4GB de RAM (mínimo).
- 2 núcleos de CPU.
- 10GB de espaço em disco.

##### Chaves de API
 - OpenAI API Key.

## 🦅 Como Executar

#### Clone o Repositório:

```bash 
git clone https://github.com/jailsonmatz/pdf-chat-assistant.git 
cd pdf-chat-assistant 
```

#### Configure as Variáveis de Ambiente:
```bash
cp .env.example .env
```
Edite o arquivo .env e adicione sua OpenAI API Key.


#### Inicie os Containers:
```bash 
docker-compose up --build 
```

#### Acesse a Aplicação:
- Interface Web: http://localhost:8501.
- Documentação da API: http://localhost:8000/docs.

## Instalação Manual (Sem Docker)

1. **Prepare o Ambiente**
```bash
# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. **Instale as Dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as Variáveis de Ambiente**
```bash
cp .env.example .env
```
Edite o arquivo .env e adicione sua OpenAI API Key

4. **Inicie os Serviços**
```bash
# Terminal 1 - API
uvicorn api.main:app --reload --port 8000

# Terminal 2 - UI
streamlit run ui/ui.py
```

## 🏗️ Arquitetura

#### Componentes Principais

#### 1. Processamento de Documentos
- **PDFExtractor**: Responsável pela extração de texto de PDFs
- **TextAnalyzer**: Analisa e estrutura o conteúdo do documento
  - Identifica tópicos principais
  - Detecta estrutura do documento
  - Fornece métricas de linguagem

#### 2. Sistema de Agentes
- **BaseAgent**: Classe base abstrata para todos os agentes
- **DocumentAgent**: Processa queries usando o conteúdo do PDF
- **WebAgent**: Realiza e processa buscas na web
- **AgentOrchestrator**: Coordena os agentes e decide a melhor estratégia

#### 3. Gerenciamento de Estado e Memória
- **ConversationMemory**: Mantém histórico e contexto das conversas
- **StateManagement**: Gerencia estado global da aplicação
- **ConversationState**: Define estrutura de estado das conversas

### Fluxo de Processamento
##### 1. Upload e análise inicial do PDF
##### 2. Processamento de perguntas em três etapas:
   - Busca no documento
   - Busca na web (se necessário)
   - Combinação de informações

## 🛠️ Tecnologias Utilizadas

### Core
- **FastAPI**: Framework web assíncrono
- **Streamlit**: Interface do usuário
- **LangChain**: Framework para aplicações LLM
- **OpenAI API**: Modelo de linguagem principal

### Processamento
- **pdfplumber**: Extração de texto de PDFs
- **FAISS**: Busca semântica eficiente
- **HuggingFace Transformers**: Embeddings e análise de texto

### Integração e Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração de serviços
- **DuckDuckGo API**: Busca na web sem autenticação

## 🤖 Decisões de Design

### 1. Arquitetura de Agentes
- Sistema modular com agentes especializados
- Decisão dinâmica baseada em relevância
- Facilidade de adicionar novos agentes

### 2. Processamento de Documentos
- Análise em duas fases: extração e estruturação
- Identificação automática de seções e tópicos
- Cache eficiente de resultados

### 3. Gestão de Estado
- Estado centralizado para consistência
- Memória de conversação para contexto
- Limpeza automática para economia de recursos

### 4. Interface do Usuário
- Design minimalista e intuitivo
- Feedback em tempo real
- Suporte a documentos genéricos

## ⚡ Performance

- Processamento de PDFs até 10MB
- Respostas aproximadamete 5 segundos (podendo variar)
- Otimização de memória e cache

### Verificação da Instalação

Execute os seguintes testes para garantir que tudo está funcionando:

1. **Verifique os Serviços**
```bash
# Verifique a API
curl http://localhost:8000/health

# A UI deve estar acessível em
# http://localhost:8501
```

## 🎯 Estrutura do Projeto

```plaintext . 
    Project
    ├── api/
    │   ├── models/
    │   │   ├── state.py
    │   │   └── responses.py
    │   ├── services/
    │   │   ├── agents/
    │   │   ├── extractors/
    │   │   ├── llm/
    │   │   ├── memory/
    │   │   └── search/
    │   └── main.py
    ├── ui/
    │   ├── Dockerfile
    │   └── ui.py
    ├── Dockerfile
    ├── docker-compose.yml
    └── requirements.txt
```

## 📝 Desenvolvimento e Melhorias Futuras

### Implementadas
- [x] Sistema de agentes inteligente
- [x] Processamento de PDFs genéricos
- [x] Busca web integrada
- [x] Interface responsiva

### Planejadas
- [ ]  Suporte a mais formatos de documento
- [ ]  Cache distribuído
- [ ]  Análise de sentimento
- [ ]  Exportação de conversas

## 🔍 Pontos de Avaliação

### 1. Qualidade do Código
- Arquitetura modular e extensível
- Padrões SOLID aplicados
- Tipagem forte e validações
- Tratamento de erros robusto

### 2. Estrutura de Prompts
- Prompts dinâmicos baseados em contexto
- Sistema de memória para contexto
- Gestão eficiente de estado
- Encadeamento inteligente de chamadas

### 3. Comunicação
- Logs informativos
- Feedback em tempo real
- Mensagens de erro claras
- Interface intuitiva

## ⚠️ Limitações Conhecidas
- Tempo limite de 5 segundos para respostas
- Tamanho máximo de PDF: 10MB
- Número máximo de páginas recomendado: 50
- Limite de tokens por requisição
## 📄 Licença

MIT