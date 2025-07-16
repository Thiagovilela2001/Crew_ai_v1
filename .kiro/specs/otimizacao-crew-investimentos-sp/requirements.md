# Documento de Requisitos

## Introdução

Este documento define os requisitos para otimizar e aprimorar o sistema CrewAI existente de coleta e análise de notícias sobre investimentos produtivos no estado de São Paulo. O sistema atual possui três agentes (pesquisador, analista de relatórios e verificador de duplicatas) que trabalham em sequência para coletar, processar e consolidar informações sobre investimentos em 2025.

## Requisitos

### Requisito 1

**História do Usuário:** Como um analista de investimentos, eu quero que o sistema colete dados de forma mais eficiente e confiável, para que eu possa obter informações precisas sobre investimentos em São Paulo sem erros de execução.

#### Critérios de Aceitação

1. QUANDO o sistema executar a coleta de dados ENTÃO ele deve processar as ferramentas sem erros de "None" input
2. QUANDO um agente chamar a ferramenta Google Search Tool ENTÃO todos os parâmetros devem ser validados corretamente
3. SE houver erro de validação de schema ENTÃO o sistema deve fornecer mensagens de erro claras e específicas

### Requisito 2

**História do Usuário:** Como um usuário do sistema, eu quero que os dados coletados sejam estruturados de forma consistente, para que eu possa analisar facilmente os investimentos por município, setor e valor.

#### Critérios de Aceitação

1. QUANDO o pesquisador coletar notícias ENTÃO cada entrada deve conter todos os campos obrigatórios definidos no schema
2. QUANDO o analista processar os dados ENTÃO o arquivo de saída deve estar no formato JSON correto
3. SE algum campo obrigatório estiver ausente ENTÃO o sistema deve registrar um aviso e preencher com valor padrão

### Requisito 3

**História do Usuário:** Como um administrador do sistema, eu quero monitorar o desempenho e a qualidade dos dados coletados, para que eu possa identificar problemas e melhorar a eficiência do processo.

#### Critérios de Aceitação

1. QUANDO o sistema executar uma iteração ENTÃO deve gerar logs detalhados de cada etapa
2. QUANDO houver duplicatas identificadas ENTÃO o sistema deve reportar quantas foram encontradas e consolidadas
3. SE a qualidade dos dados estiver abaixo do esperado ENTÃO o sistema deve alertar sobre possíveis problemas nas fontes

### Requisito 4

**História do Usuário:** Como um pesquisador, eu quero que o sistema seja capaz de expandir automaticamente as consultas de busca, para que eu possa encontrar mais investimentos relevantes sem intervenção manual.

#### Critérios de Aceitação

1. QUANDO uma busca retornar poucos resultados ENTÃO o sistema deve tentar consultas alternativas automaticamente
2. QUANDO usar consultas alternativas ENTÃO deve priorizar termos relacionados ao setor de investimentos
3. SE todas as tentativas falharem ENTÃO o sistema deve documentar as consultas tentadas para análise posterior

### Requisito 5

**História do Usuário:** Como um analista de dados, eu quero que o sistema valide a localização geográfica das notícias, para que eu tenha certeza de que todos os investimentos são realmente em municípios de São Paulo.

#### Critérios de Aceitação

1. QUANDO uma notícia mencionar um município ENTÃO o sistema deve validar contra a lista oficial de municípios de SP
2. QUANDO a validação falhar ENTÃO a notícia deve ser descartada com log explicativo
3. SE houver ambiguidade na localização ENTÃO o sistema deve usar scraping adicional para confirmar

### Requisito 6

**História do Usuário:** Como um usuário final, eu quero que o sistema execute múltiplas iterações de forma estável, para que eu possa coletar grandes volumes de dados sem interrupções.

#### Critérios de Aceitação

1. QUANDO o sistema executar 5 iterações ENTÃO cada uma deve completar sem erros críticos
2. QUANDO houver falhas de rede temporárias ENTÃO o sistema deve implementar retry automático
3. SE uma iteração falhar completamente ENTÃO as iterações seguintes devem continuar normalmente