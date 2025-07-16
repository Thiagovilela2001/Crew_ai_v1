# Sistema CrewAI Otimizado - Coleta de Investimentos SP

Sistema aprimorado para coleta e análise de notícias sobre investimentos produtivos no estado de São Paulo, com validação automática, monitoramento de performance e processamento robusto de dados.

## 🚀 Principais Melhorias

### ✅ Problemas Resolvidos
- **Erro "None" tool input**: Sistema de validação automática de parâmetros
- **Falhas de execução**: Tratamento robusto de erros com retry automático
- **Dados inconsistentes**: Validação e sanitização automática de dados
- **Falta de monitoramento**: Sistema completo de logging e métricas

### 🔧 Novos Recursos
- **Validação de Ferramentas**: Parâmetros validados automaticamente
- **Expansão de Consultas**: Geração automática de consultas alternativas
- **Validação Geográfica**: Verificação automática de municípios de SP
- **Verificador de Notícias Falsas**: Sistema avançado de detecção de credibilidade
- **Validador de URLs**: Verifica se notícias realmente existem e são acessíveis
- **Monitoramento Completo**: Métricas de performance e qualidade
- **Processamento Robusto**: Sanitização e estruturação de dados

## 📁 Estrutura do Projeto

```
src/
├── utils/                      # Utilitários do sistema otimizado
│   ├── tool_validator.py       # Validação de parâmetros de ferramentas
│   ├── query_expander.py       # Expansão automática de consultas
│   ├── location_validator.py   # Validação geográfica de municípios
│   ├── system_monitor.py       # Monitoramento e métricas
│   └── data_processor.py       # Processamento robusto de dados
├── tools/
│   ├── validated_tools.py      # Ferramentas com validação automática
│   └── serp_tool.py           # Ferramenta Google Search original
├── config/
│   ├── agents.yaml            # Configuração dos agentes
│   └── tasks.yaml             # Configuração das tarefas
├── main.py                    # Sistema principal otimizado
└── crew.py                    # Definição da crew
```

## 🛠️ Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas chaves de API:

```bash
cp src/.env.example src/.env
```

Configure as seguintes variáveis obrigatórias:
```env
SERPER_API_KEY=sua_chave_serper_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

### 2. Configurações Opcionais

```env
# Número de iterações (padrão: 5)
CREWAI_ITERATIONS=5

# AgentOps para monitoramento (opcional)
AGENTOPS_API_KEY=sua_chave_agentops_aqui
```

## 🚀 Execução

### Execução Padrão
```bash
python src/main.py
```

### Execução com Configurações Personalizadas
```bash
# Definir número de iterações
CREWAI_ITERATIONS=3 python src/main.py

# Com logging detalhado
LOG_LEVEL=DEBUG python src/main.py
```

## 📊 Monitoramento e Relatórios

### Logs Estruturados
O sistema gera logs estruturados em JSON em:
- `logs/crewai_system_YYYYMMDD.log` - Log principal
- `logs/system_monitor_YYYYMMDD.log` - Log do monitor

### Relatórios de Performance
Relatórios automáticos são gerados em:
- `logs/performance_report_YYYYMMDD_HHMMSS.json`

### Métricas Monitoradas
- **Tempo de execução** por iteração
- **Qualidade dos dados** coletados
- **Taxa de sucesso** das ferramentas
- **Duplicatas removidas**
- **Localizações validadas**
- **Erros de validação**

## 🔍 Funcionalidades Detalhadas

### 1. Validação Automática de Ferramentas
- Valida parâmetros antes da execução
- Aplica valores padrão quando necessário
- Log detalhado de erros de validação

### 2. Expansão Inteligente de Consultas
- Gera consultas alternativas por setor
- Combina termos geográficos automaticamente
- Retry automático com consultas expandidas

### 3. Validação Geográfica Rigorosa
- Verifica municípios contra lista oficial de SP
- Extrai localizações usando regex e NLP
- Resolve ambiguidades automaticamente

### 4. Processamento Robusto de Dados
- Sanitização automática de campos
- Aplicação de valores padrão
- Cálculo de score de qualidade
- Exportação estruturada em JSON

### 5. Verificador de Notícias Falsas
- Análise automática de credibilidade das notícias
- Score de confiabilidade de 0.0 a 1.0
- Detecção de padrões suspeitos (clickbait, fontes duvidosas)
- Validação de fontes contra lista de veículos confiáveis
- Filtragem automática de notícias com baixa credibilidade

### 6. Sistema de Alertas
- Alertas automáticos para problemas de performance
- Thresholds configuráveis
- Severidade classificada (LOW, MEDIUM, HIGH, CRITICAL)

## 📈 Métricas de Qualidade

### Indicadores de Sucesso
- **Taxa de conclusão**: > 95%
- **Precisão geográfica**: > 98%
- **Redução de duplicatas**: > 80%
- **Tempo médio por iteração**: < 5 minutos

### Campos de Qualidade dos Dados
Cada notícia coletada inclui:
```json
{
  "categoria": "Investimentos",
  "titulo": "Título da notícia",
  "link": "URL da fonte",
  "descricao_detalhada": "Resumo do investimento",
  "data": "DD/MM/YYYY",
  "municipio": "Nome do município (validado)",
  "tipo_investimento": "Tipo da ação",
  "valor_estimado": "Valor ou 'não informado'",
  "fonte_financiamento": "Fonte ou 'não informado'",
  "fonte_noticia": "Nome da fonte",
  "piesp_setor": "Setor econômico",
  "cnae_investimento": "Código CNAE",
  "investimento_estrangeiro": "sim/não/não identificado",
  "esg": "sim/não/não identificado",
  "pme": "sim/não/não identificado",
  "qualidade_dados": 0.85,
  "credibility_score": 0.92,
  "is_credible": true,
  "warning_flags": [],
  "verification_recommendation": "ACEITAR - Notícia altamente confiável"
}
```

## 🐛 Troubleshooting

### Erro "None" tool input
✅ **Resolvido**: Sistema de validação automática implementado

### Falhas de conexão
- O sistema implementa retry automático
- Delays entre iterações para evitar rate limiting
- Logs detalhados para diagnóstico

### Dados de baixa qualidade
- Alertas automáticos quando qualidade < 70%
- Relatórios detalhados de completude de campos
- Sugestões de melhoria nos logs

### Problemas de localização
- Validação automática contra lista oficial de municípios
- Resolução de ambiguidades
- Logs de localizações descartadas

## 📝 Logs de Exemplo

### Log de Iteração
```json
{
  "event": "iteration_end",
  "metrics": {
    "iteracao": 1,
    "total_noticias_encontradas": 15,
    "noticias_validadas": 12,
    "qualidade_dados": 0.78,
    "tempo_execucao": 245.6
  }
}
```

### Log de Alerta
```json
{
  "event": "performance_alert",
  "alert": {
    "tipo": "DATA_QUALITY",
    "severidade": "HIGH",
    "mensagem": "Qualidade dos dados baixa: 65%",
    "timestamp": "2025-07-15T10:30:00Z"
  }
}
```

## 🛡️ Verificador de Notícias Falsas

### Como Funciona
O sistema analisa automaticamente a credibilidade de cada notícia coletada usando múltiplos critérios:

#### 📊 Critérios de Verificação (Score 0.0 - 1.0)

1. **Credibilidade da Fonte (30%)**
   - **Tier 1 (1.0)**: Estadão, Valor, Folha, Globo, UOL, BNDES, Gov.br
   - **Tier 2 (0.8)**: DCI, Correio Popular, DGABC, Jornal de Campinas
   - **Tier 3 (0.6)**: Diários regionais, jornais locais confiáveis
   - **Suspeitas (0.2)**: Blogspot, WordPress, domínios com 'fake', 'viral'

2. **Qualidade do Conteúdo (25%)**
   - Detecta títulos clickbait: "URGENTE", "BOMBA", "CHOCANTE"
   - Identifica conteúdo suspeito: "fonte não revelada", "segundo rumores"
   - Flagra valores irreais: "trilhões de reais", "retorno garantido de X%"
   - Analisa qualidade da escrita e coerência

3. **Consistência Temporal (15%)**
   - Verifica datas no futuro (suspeito)
   - Valida período de publicação (prioriza 2025)
   - Detecta inconsistências temporais

4. **Coerência Factual (15%)**
   - Valida municípios mencionados
   - Verifica especificidade do tipo de investimento
   - Analisa coerência entre título e descrição

5. **Detalhes Técnicos (15%)**
   - Verifica completude de campos obrigatórios
   - Bonifica informações sobre setor e CNAE
   - Avalia especificidade técnica

#### 🚦 Classificação de Credibilidade

- **🟢 Alta (≥0.8)**: ACEITAR - Notícia altamente confiável
- **🟡 Média (≥0.6)**: ACEITAR_COM_RESSALVAS - Revisar se muitos alertas
- **🟠 Baixa (≥0.4)**: REVISAR_CUIDADOSAMENTE - Credibilidade questionável  
- **🔴 Muito Baixa (<0.4)**: REJEITAR - Possível notícia falsa

#### ⚠️ Flags de Alerta Automáticos

- `FONTE_SUSPEITA`: Domínio não confiável
- `CONTEUDO_SUSPEITO`: Padrões de desinformação
- `CLICKBAIT`: Título sensacionalista
- `DATA_INCONSISTENTE`: Problemas temporais
- `FATOS_INCOERENTES`: Informações contraditórias
- `SEM_VALOR_INVESTIMENTO`: Falta dados financeiros
- `LOCALIZACAO_VAGA`: Município não especificado

### 📋 Exemplo de Uso

```python
from utils.news_verifier import news_verifier

# Verifica uma notícia
result = news_verifier.verify_news(news_data)
print(f"Credibilidade: {result.credibility_score:.2f}")
print(f"Recomendação: {result.recommendation}")

# Verifica lote de notícias
results = news_verifier.batch_verify_news(news_list)
report = news_verifier.generate_verification_report(results)
```

### 📈 Integração Automática

O verificador está integrado ao processador de dados:
- **Filtragem automática**: Notícias com score < 0.3 são rejeitadas
- **Ajuste de qualidade**: Score de credibilidade influencia qualidade final
- **Relatórios detalhados**: Estatísticas de verificação por iteração

## 🔗 Validador de URLs

### Como Funciona
O sistema verifica automaticamente se as URLs das notícias realmente existem e são acessíveis antes de processá-las.

#### 🔍 Verificações Realizadas

1. **Acessibilidade da URL**
   - ✅ Status HTTP 200-299: URL acessível
   - ❌ Status HTTP 404: Página não encontrada
   - ❌ Status HTTP 403: Acesso negado
   - ❌ Status HTTP 500: Erro do servidor
   - ❌ Timeout: URL inacessível

2. **Análise de Conteúdo**
   - **Indicadores Positivos**: Tags HTML estruturais, conteúdo > 500 chars
   - **Indicadores Negativos**: Mensagens de erro, paywall, conteúdo insuficiente
   - **Indicadores de Notícia**: Data de publicação, autor, estrutura jornalística

3. **Configurações de Segurança**
   - User-Agent de navegador real
   - Headers HTTP apropriados
   - Timeout de 15 segundos
   - Máximo 3 tentativas com retry
   - Pausa respeitosa entre requisições

#### 📊 Métricas Geradas

- **Taxa de Acessibilidade**: % de URLs que respondem corretamente
- **Taxa de Conteúdo Válido**: % de URLs com conteúdo jornalístico válido
- **Tempo Médio de Resposta**: Performance das fontes de notícias
- **Distribuição de Status Codes**: Análise de problemas comuns
- **Tipos de Erro**: Categorização de falhas

#### 🚀 Exemplo de Uso

```python
from utils.url_validator import url_validator

# Valida uma URL
result = url_validator.validate_url("https://exemplo.com/noticia")
print(f"Acessível: {result.is_accessible}")
print(f"Conteúdo válido: {result.has_valid_content}")

# Filtra notícias com URLs válidas
valid_news = url_validator.filter_valid_news(news_list)
```

#### 🔧 Integração Automática

O validador está integrado ao processador de dados:
- **Filtragem prévia**: URLs inacessíveis são removidas antes do processamento
- **Informações adicionais**: Cada notícia recebe dados de validação de URL
- **Relatórios detalhados**: Estatísticas de acessibilidade por iteração
- **Otimização de performance**: Evita processamento de conteúdo inexistente

## 🔄 Próximos Passos

Para continuar melhorando o sistema:

1. **Implementar testes automatizados** (Tarefas 9-10)
2. **Adicionar retry com backoff exponencial** (Tarefa 6)
3. **Criar modelos de dados com Pydantic** (Tarefa 8)
4. **Expandir configurações dos agentes** (Tarefa 7)

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Consulte o relatório de performance mais recente
3. Verifique as configurações no arquivo `.env`

---

**Status**: ✅ Sistema otimizado e funcional
**Última atualização**: 15/07/2025