# Documento de Design

## Visão Geral

Este documento descreve o design para otimizar o sistema CrewAI existente de coleta de notícias sobre investimentos em São Paulo. O foco principal é resolver problemas de validação de ferramentas, melhorar a estruturação de dados e adicionar recursos de monitoramento e retry automático.

## Arquitetura

### Arquitetura Atual
```
[Pesquisador] -> [Analista Relatórios] -> [Verificador Duplicatas]
     |                    |                        |
[Google Tool]        [Processar JSON]      [Read Website]
[Scrape Tool]
```

### Arquitetura Otimizada
```
[Pesquisador Aprimorado] -> [Analista Melhorado] -> [Verificador Otimizado]
         |                          |                        |
[Google Tool Validado]    [Processador JSON]      [Consolidador Inteligente]
[Scrape Tool]             [Validador Dados]       [Read Website]
[Query Expander]          [Logger Sistema]        [Detector Duplicatas]
```

## Componentes e Interfaces

### 1. Validador de Schema de Ferramentas
**Responsabilidade:** Garantir que todas as chamadas de ferramentas tenham parâmetros válidos

**Interface:**
```python
class ToolValidator:
    def validate_google_search_params(self, params: dict) -> dict
    def sanitize_tool_input(self, tool_name: str, params: dict) -> dict
    def log_validation_error(self, error: str, context: dict) -> None
```

### 2. Expansor de Consultas Automático
**Responsabilidade:** Gerar consultas alternativas quando os resultados são insuficientes

**Interface:**
```python
class QueryExpander:
    def generate_alternative_queries(self, original_query: str) -> List[str]
    def get_sector_specific_terms(self, sector: str) -> List[str]
    def combine_location_terms(self, base_query: str) -> List[str]
```

### 3. Validador Geográfico Aprimorado
**Responsabilidade:** Validar localizações contra lista oficial de municípios de SP

**Interface:**
```python
class LocationValidator:
    def load_sp_municipalities(self) -> Set[str]
    def validate_municipality(self, location: str) -> bool
    def extract_location_from_text(self, text: str) -> Optional[str]
    def resolve_ambiguous_location(self, location: str, url: str) -> Optional[str]
```

### 4. Sistema de Logging e Monitoramento
**Responsabilidade:** Registrar métricas de desempenho e qualidade dos dados

**Interface:**
```python
class SystemMonitor:
    def log_iteration_start(self, iteration: int) -> None
    def log_data_quality_metrics(self, data: List[dict]) -> None
    def log_duplicate_consolidation(self, before: int, after: int) -> None
    def generate_performance_report(self) -> dict
```

### 5. Processador de Dados Robusto
**Responsabilidade:** Processar e validar dados coletados com tratamento de erros

**Interface:**
```python
class DataProcessor:
    def validate_required_fields(self, data: dict) -> dict
    def apply_default_values(self, data: dict) -> dict
    def sanitize_data_types(self, data: dict) -> dict
    def export_to_json(self, data: List[dict], filename: str) -> bool
```

## Modelos de Dados

### Estrutura de Notícia Aprimorada
```python
@dataclass
class InvestmentNews:
    categoria: str
    titulo: str
    link: str
    descricao_detalhada: str
    data: str
    municipio: str
    tipo_investimento: str
    valor_estimado: Optional[Union[str, float]]
    fonte_financiamento: Optional[str]
    fonte_noticia: str
    piesp_setor: Optional[str]
    cnae_investimento: Optional[Union[str, float]]
    investimento_estrangeiro: str = "não identificado"
    esg: str = "não identificado"
    pme: str = "não identificado"
    
    # Novos campos para monitoramento
    data_coleta: str = field(default_factory=lambda: datetime.now().isoformat())
    tentativas_busca: List[str] = field(default_factory=list)
    validacao_municipio: bool = False
    qualidade_dados: float = 0.0
```

### Métricas de Sistema
```python
@dataclass
class SystemMetrics:
    iteracao: int
    total_noticias_encontradas: int
    noticias_validadas: int
    duplicatas_removidas: int
    municipios_invalidos: int
    tempo_execucao: float
    taxa_sucesso_ferramentas: float
    consultas_alternativas_usadas: int
```

## Tratamento de Erros

### Estratégia de Retry
1. **Falhas de Rede:** 3 tentativas com backoff exponencial
2. **Validação de Schema:** Log detalhado + valores padrão
3. **Scraping Falhou:** Tentar fonte alternativa se disponível
4. **API Rate Limit:** Delay automático baseado em headers de resposta

### Logs Estruturados
```python
{
    "timestamp": "2025-07-15T10:30:00Z",
    "level": "ERROR",
    "component": "GoogleSearchTool",
    "message": "Schema validation failed",
    "context": {
        "agent": "pesquisador_noticias",
        "iteration": 3,
        "query": "investimento São Paulo 2025",
        "error_details": "tentativas_query field missing"
    }
}
```

## Estratégia de Testes

### Testes Unitários
- Validação de schema de ferramentas
- Expansão de consultas
- Validação geográfica
- Processamento de dados

### Testes de Integração
- Fluxo completo de uma iteração
- Interação entre agentes
- Persistência de dados

### Testes de Performance
- Tempo de execução por iteração
- Uso de memória durante processamento
- Taxa de sucesso de APIs externas

## Considerações de Segurança

1. **Sanitização de Dados:** Todos os inputs de ferramentas são validados
2. **Rate Limiting:** Respeitar limites de APIs externas
3. **Logs Seguros:** Não registrar informações sensíveis como API keys
4. **Validação de URLs:** Verificar domínios permitidos antes de scraping

## Métricas de Qualidade

### Indicadores de Sucesso
- Taxa de conclusão de iterações: > 95%
- Precisão de validação geográfica: > 98%
- Redução de duplicatas: > 80%
- Tempo médio por iteração: < 5 minutos

### Alertas Automáticos
- Queda na qualidade dos dados abaixo de 70%
- Falhas consecutivas de ferramentas
- Tempo de execução acima de 10 minutos
- Zero notícias válidas encontradas em uma iteração