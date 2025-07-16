# 🚀 Sistema CrewAI - Coleta Inteligente de Investimentos SP

Sistema avançado de coleta e análise de notícias sobre investimentos produtivos no estado de São Paulo, utilizando inteligência artificial multi-agente com validação automática, monitoramento de performance e processamento robusto de dados.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Principais Recursos](#-principais-recursos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Funcionalidades Avançadas](#-funcionalidades-avançadas)
- [Monitoramento e Relatórios](#-monitoramento-e-relatórios)
- [Troubleshooting](#-troubleshooting)
- [Contribuição](#-contribuição)

## 🎯 Visão Geral

Este sistema utiliza **CrewAI** para orquestrar agentes de IA especializados na coleta, validação e análise de notícias sobre investimentos no estado de São Paulo. O projeto foi otimizado para resolver problemas comuns de sistemas de coleta automatizada, oferecendo alta confiabilidade e qualidade de dados.

### 🔧 Problemas Resolvidos

- ✅ **Erro "None" tool input**: Sistema de validação automática de parâmetros
- ✅ **Falhas de execução**: Tratamento robusto de erros com retry automático
- ✅ **Dados inconsistentes**: Validação e sanitização automática de dados
- ✅ **Falta de monitoramento**: Sistema completo de logging e métricas
- ✅ **URLs inacessíveis**: Validação automática de links antes do processamento
- ✅ **Notícias falsas**: Sistema avançado de verificação de credibilidade

## 🌟 Principais Recursos

### 🛡️ Validação e Segurança
- **Validação de Ferramentas**: Parâmetros validados automaticamente antes da execução
- **Verificador de Notícias Falsas**: Sistema de scoring de credibilidade (0.0-1.0)
- **Validador de URLs**: Verifica acessibilidade e conteúdo válido das fontes
- **Validação Geográfica**: Verificação automática de municípios de SP

### 🧠 Inteligência Artificial
- **Expansão de Consultas**: Geração automática de consultas alternativas
- **Processamento Robusto**: Sanitização e estruturação inteligente de dados
- **Agentes Especializados**: Crew multi-agente com papéis específicos

### 📊 Monitoramento e Qualidade
- **Monitoramento Completo**: Métricas de performance e qualidade em tempo real
- **Sistema de Alertas**: Notificações automáticas para problemas de performance
- **Relatórios Detalhados**: Análises completas de cada execução
- **Logs Estruturados**: Logging em JSON para análise avançada

## 🚀 Instalação

### Pré-requisitos

- **Python**: 3.10 ou superior (< 3.13)
- **UV**: Gerenciador de dependências (recomendado)

### Instalação com UV (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Thiagovilela2001/Crew_ai_v1.git
cd Crew_ai_v1

# Instale UV se não tiver
pip install uv

# Instale as dependências
uv sync
```

### Instalação com PIP

```bash
# Clone o repositório
git clone https://github.com/Thiagovilela2001/Crew_ai_v1.git
cd Crew_ai_v1

# Instale as dependências
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas chaves de API:

```bash
cp src/.env.example src/.env
```

Configure as seguintes variáveis **obrigatórias**:

```env
# APIs obrigatórias
SERPER_API_KEY=sua_chave_serper_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Configurações opcionais
CREWAI_ITERATIONS=5                    # Número de iterações (padrão: 1)
AGENTOPS_API_KEY=sua_chave_agentops    # Monitoramento avançado (opcional)
LOG_LEVEL=INFO                         # Nível de logging (DEBUG, INFO, WARNING, ERROR)
```

### 2. Obter Chaves de API

#### SERPER API (Google Search)
1. Acesse [serper.dev](https://serper.dev)
2. Crie uma conta gratuita
3. Copie sua API key

#### OpenAI API
1. Acesse [platform.openai.com](https://platform.openai.com)
2. Crie uma conta e configure billing
3. Gere uma API key

#### AgentOps (Opcional)
1. Acesse [agentops.ai](https://agentops.ai)
2. Crie uma conta gratuita
3. Copie sua API key

## 🎮 Como Usar

### Execução Básica

```bash
# Execução padrão (1 iteração)
python src/main.py

# Com UV
uv run python src/main.py
```

### Execução Avançada

```bash
# Múltiplas iterações
CREWAI_ITERATIONS=5 python src/main.py

# Com logging detalhado
LOG_LEVEL=DEBUG python src/main.py

# Combinando configurações
CREWAI_ITERATIONS=3 LOG_LEVEL=DEBUG python src/main.py
```

### Usando CrewAI CLI

```bash
# Instalar dependências
crewai install

# Executar o projeto
crewai run
```

## 📁 Estrutura do Projeto

```
📦 Crew_ai_v1/
├── 📂 src/                           # Código fonte principal
│   ├── 📂 config/                    # Configurações dos agentes
│   │   ├── agents.yaml               # Definição dos agentes IA
│   │   └── tasks.yaml                # Definição das tarefas
│   ├── 📂 tools/                     # Ferramentas especializadas
│   │   ├── validated_tools.py        # Ferramentas com validação
│   │   └── serp_tool.py             # Ferramenta Google Search
│   ├── 📂 utils/                     # Utilitários do sistema
│   │   ├── tool_validator.py         # Validação de parâmetros
│   │   ├── query_expander.py         # Expansão de consultas
│   │   ├── location_validator.py     # Validação geográfica
│   │   ├── news_verifier.py          # Verificador de notícias falsas
│   │   ├── url_validator.py          # Validador de URLs
│   │   ├── system_monitor.py         # Monitoramento do sistema
│   │   └── data_processor.py         # Processamento de dados
│   ├── 📂 tests/                     # Testes automatizados
│   ├── 📂 examples/                  # Exemplos de uso
│   ├── main.py                       # Sistema principal otimizado
│   ├── crew.py                       # Definição da crew
│   └── .env.example                  # Exemplo de configuração
├── 📂 knowledge/                     # Base de conhecimento
│   ├── municipios_sp.txt             # Lista oficial de municípios SP
│   ├── investimentos2025.csv         # Dados de investimentos
│   └── user_preference.txt           # Preferências do usuário
├── 📂 output/                        # Relatórios gerados
├── 📂 logs/                          # Logs do sistema
├── 📂 .kiro/                         # Configurações Kiro (opcional)
├── README.md                         # Este arquivo
├── pyproject.toml                    # Configuração do projeto
└── uv.lock                          # Lock de dependências
```

## 🔍 Funcionalidades Avançadas

### 🛡️ Verificador de Notícias Falsas

Sistema avançado que analisa a credibilidade de cada notícia usando múltiplos critérios:

#### Critérios de Verificação (Score 0.0 - 1.0)

1. **Credibilidade da Fonte (30%)**
   - **Tier 1 (1.0)**: Estadão, Valor, Folha, Globo, UOL, BNDES, Gov.br
   - **Tier 2 (0.8)**: DCI, Correio Popular, DGABC, Jornal de Campinas
   - **Tier 3 (0.6)**: Diários regionais, jornais locais confiáveis
   - **Suspeitas (0.2)**: Blogspot, WordPress, domínios duvidosos

2. **Qualidade do Conteúdo (25%)**
   - Detecta títulos clickbait
   - Identifica conteúdo suspeito
   - Analisa coerência e qualidade da escrita

3. **Consistência Temporal (15%)**
   - Verifica datas no futuro
   - Valida período de publicação

4. **Coerência Factual (15%)**
   - Valida municípios mencionados
   - Verifica especificidade do investimento

5. **Detalhes Técnicos (15%)**
   - Completude de campos obrigatórios
   - Especificidade técnica

#### Classificação de Credibilidade

- 🟢 **Alta (≥0.8)**: ACEITAR - Notícia altamente confiável
- 🟡 **Média (≥0.6)**: ACEITAR_COM_RESSALVAS - Revisar se muitos alertas
- 🟠 **Baixa (≥0.4)**: REVISAR_CUIDADOSAMENTE - Credibilidade questionável
- 🔴 **Muito Baixa (<0.4)**: REJEITAR - Possível notícia falsa

### 🔗 Validador de URLs

Verifica automaticamente se as URLs das notícias são acessíveis:

- ✅ **Acessibilidade**: Status HTTP, timeout, retry automático
- 📄 **Conteúdo Válido**: Estrutura jornalística, tamanho adequado
- 📊 **Métricas**: Taxa de acessibilidade, tempo de resposta
- 🔧 **Integração**: Filtragem automática de URLs inválidas

### 🗺️ Validação Geográfica

Sistema rigoroso de validação de municípios:

- 📋 **Lista Oficial**: Base com todos os municípios de SP
- 🔍 **Extração Inteligente**: Regex e NLP para identificar localizações
- ✅ **Resolução de Ambiguidades**: Correção automática de nomes
- 📊 **Relatórios**: Estatísticas de validação geográfica

### 🔄 Expansão de Consultas

Geração inteligente de consultas alternativas:

- 🎯 **Por Setor**: Consultas específicas por área econômica
- 🗺️ **Geográficas**: Combinação com termos regionais
- 🔄 **Retry Automático**: Tentativas com consultas expandidas
- 📈 **Otimização**: Melhora taxa de sucesso da coleta

## 📊 Monitoramento e Relatórios

### 📈 Métricas Coletadas

- **Performance**: Tempo de execução, taxa de sucesso
- **Qualidade**: Score de qualidade dos dados, completude
- **Validação**: URLs válidas, municípios corretos, credibilidade
- **Erros**: Tipos de falhas, frequência, padrões

### 📋 Relatórios Gerados

#### Logs Estruturados
```
logs/
├── crewai_system_YYYYMMDD.log        # Log principal
├── system_monitor_YYYYMMDD.log       # Log do monitor
└── performance_report_YYYYMMDD_HHMMSS.json  # Relatório de performance
```

#### Exemplo de Relatório
```json
{
  "session_summary": {
    "total_iterations": 5,
    "session_duration_minutes": 25.3,
    "total_alerts": 2
  },
  "performance_stats": {
    "avg_execution_time_minutes": 4.8,
    "avg_data_quality": 0.82,
    "avg_tool_success_rate": 0.95
  },
  "data_collection": {
    "total_news_found": 67,
    "total_news_validated": 58,
    "total_duplicates_removed": 12
  }
}
```

### 🚨 Sistema de Alertas

Alertas automáticos para:
- **Qualidade baixa** dos dados (< 70%)
- **Taxa de falhas** alta das ferramentas (> 20%)
- **Tempo de execução** excessivo (> 10 min)
- **URLs inacessíveis** (> 30%)

## 🔧 Troubleshooting

### Problemas Comuns

#### ❌ Erro "None" tool input
**Solução**: ✅ Resolvido automaticamente pelo sistema de validação

#### ❌ Falhas de conexão
**Soluções**:
- Verifique suas chaves de API no arquivo `.env`
- Sistema implementa retry automático
- Delays entre iterações evitam rate limiting

#### ❌ Dados de baixa qualidade
**Soluções**:
- Alertas automáticos quando qualidade < 70%
- Relatórios detalhados de completude
- Ajuste os critérios de validação se necessário

#### ❌ Problemas de localização
**Soluções**:
- Validação automática contra lista oficial
- Logs de localizações descartadas
- Resolução automática de ambiguidades

### 📋 Checklist de Diagnóstico

1. ✅ Variáveis de ambiente configuradas?
2. ✅ Arquivo `knowledge/municipios_sp.txt` existe?
3. ✅ Chaves de API válidas?
4. ✅ Conexão com internet estável?
5. ✅ Logs em `logs/` para análise detalhada

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature
4. **Implemente** suas mudanças
5. **Teste** thoroughly
6. **Commit** com mensagens descritivas
7. **Push** para sua branch
8. **Abra** um Pull Request

### 🧪 Executando Testes

```bash
# Testes unitários
python -m pytest src/tests/

# Teste de integração
python test_integration_location.py

# Teste específico
python src/examples/news_verification_example.py
```

### 📝 Padrões de Código

- **PEP 8**: Seguir padrões Python
- **Type Hints**: Usar anotações de tipo
- **Docstrings**: Documentar funções e classes
- **Logging**: Usar logging estruturado
- **Testes**: Cobrir funcionalidades críticas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

### Canais de Suporte

- **Issues**: [GitHub Issues](https://github.com/Thiagovilela2001/Crew_ai_v1/issues)
- **Documentação**: Este README e comentários no código
- **Logs**: Sempre verifique `logs/` para diagnóstico

### 📞 Contato

Para dúvidas específicas sobre implementação ou problemas técnicos, abra uma issue no GitHub com:

1. **Descrição** do problema
2. **Logs** relevantes
3. **Configuração** do ambiente
4. **Passos** para reproduzir

---

## 🎯 Status do Projeto

- ✅ **Sistema Core**: Funcional e otimizado
- ✅ **Validação**: Implementada e testada
- ✅ **Monitoramento**: Completo e detalhado
- ✅ **Documentação**: Atualizada e completa
- 🔄 **Melhorias Contínuas**: Em desenvolvimento

**Última atualização**: 16/07/2025
**Versão**: 2.0.0 (Otimizada)

---

<div align="center">

**🚀 Desenvolvido com CrewAI e muito ☕**

[⭐ Star no GitHub](https://github.com/Thiagovilela2001/Crew_ai_v1) • [🐛 Reportar Bug](https://github.com/Thiagovilela2001/Crew_ai_v1/issues) • [💡 Sugerir Feature](https://github.com/Thiagovilela2001/Crew_ai_v1/issues)

</div>
