"""
Exemplo de uso do validador de URLs
Demonstra como verificar se notícias realmente existem
"""

from utils.url_validator import url_validator
from utils.data_processor import data_processor
import json

def example_url_validation():
    """Exemplo de validação de URLs"""
    
    # Exemplos de URLs para teste
    test_urls = [
        "https://valor.com.br/empresas",  # URL válida
        "https://estadao.com.br/economia",  # URL válida
        "https://exemplo-inexistente-404.com/noticia",  # URL que não existe
        "https://globo.com/economia/noticia-exemplo",  # URL que pode existir
        "invalid-url-format",  # URL com formato inválido
        "https://httpstat.us/500",  # URL que retorna erro 500
    ]
    
    print("=== EXEMPLO DE VALIDAÇÃO DE URLs ===\n")
    
    # Valida URLs individualmente
    print("1. VALIDAÇÃO INDIVIDUAL DE URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- URL {i} ---")
        print(f"URL: {url}")
        
        result = url_validator.validate_url(url, check_content=True)
        
        print(f"✅ Acessível: {'SIM' if result.is_accessible else 'NÃO'}")
        print(f"📊 Status Code: {result.status_code}")
        print(f"⏱️ Tempo de Resposta: {result.response_time:.2f}s")
        print(f"📄 Conteúdo Válido: {'SIM' if result.has_valid_content else 'NÃO'}")
        print(f"📏 Tamanho do Conteúdo: {result.content_length} chars")
        
        if result.error_message:
            print(f"❌ Erro: {result.error_message}")
        
        if result.content_indicators:
            print(f"🔍 Indicadores de Conteúdo:")
            for indicator, value in result.content_indicators.items():
                status = "✅" if value else "❌"
                print(f"   {status} {indicator}")
    
    # Valida lote de URLs
    print(f"\n\n2. VALIDAÇÃO EM LOTE:")
    batch_results = url_validator.batch_validate_urls(test_urls, check_content=True)
    
    accessible_count = sum(1 for r in batch_results if r.is_accessible)
    valid_content_count = sum(1 for r in batch_results if r.has_valid_content)
    
    print(f"Total de URLs: {len(test_urls)}")
    print(f"URLs acessíveis: {accessible_count}")
    print(f"URLs com conteúdo válido: {valid_content_count}")
    print(f"Taxa de acessibilidade: {accessible_count/len(test_urls):.1%}")
    print(f"Taxa de conteúdo válido: {valid_content_count/len(test_urls):.1%}")
    
    # Gera relatório detalhado
    print(f"\n\n3. RELATÓRIO DE VALIDAÇÃO:")
    report = url_validator.generate_validation_report(batch_results)
    
    print(f"Taxa de acessibilidade: {report['validation_summary']['accessibility_rate']:.1%}")
    print(f"Taxa de conteúdo válido: {report['validation_summary']['content_validity_rate']:.1%}")
    print(f"Tempo médio de resposta: {report['validation_summary']['average_response_time']:.2f}s")
    
    print(f"\nDistribuição de Status Codes:")
    for code, count in report['status_code_distribution'].items():
        print(f"  - {code}: {count} URLs")
    
    if report['error_types']:
        print(f"\nTipos de Erro:")
        for error_type, count in list(report['error_types'].items())[:5]:
            print(f"  - {error_type}: {count} ocorrências")
    
    return report

def example_news_filtering():
    """Exemplo de filtragem de notícias com URLs válidas"""
    
    print("\n\n=== EXEMPLO DE FILTRAGEM DE NOTÍCIAS ===\n")
    
    # Notícias de exemplo (algumas com URLs inválidas)
    sample_news = [
        {
            "categoria": "Investimentos",
            "titulo": "Empresa anuncia investimento em São Paulo",
            "link": "https://valor.com.br/empresas",  # URL válida
            "descricao_detalhada": "Empresa XYZ anuncia investimento de R$ 50 milhões em nova fábrica.",
            "data": "15/07/2025",
            "municipio": "São Paulo",
            "tipo_investimento": "Construção",
            "fonte_noticia": "Valor Econômico"
        },
        {
            "categoria": "Expansões",
            "titulo": "Nova unidade industrial em Campinas",
            "link": "https://exemplo-404-nao-existe.com/noticia",  # URL inválida
            "descricao_detalhada": "Indústria planeja nova unidade em Campinas.",
            "data": "10/07/2025",
            "municipio": "Campinas",
            "tipo_investimento": "Expansão",
            "fonte_noticia": "Jornal Local"
        },
        {
            "categoria": "Modernização",
            "titulo": "Modernização de fábrica em Santos",
            "link": "https://estadao.com.br/economia",  # URL válida
            "descricao_detalhada": "Fábrica em Santos recebe investimento para modernização.",
            "data": "12/07/2025",
            "municipio": "Santos",
            "tipo_investimento": "Modernização",
            "fonte_noticia": "Estadão"
        },
        {
            "categoria": "Investimentos",
            "titulo": "Investimento sem link válido",
            "link": "url-invalida-sem-protocolo",  # URL com formato inválido
            "descricao_detalhada": "Investimento sem URL válida.",
            "data": "08/07/2025",
            "municipio": "Sorocaba",
            "tipo_investimento": "Instalação",
            "fonte_noticia": "Fonte Desconhecida"
        }
    ]
    
    print(f"Notícias originais: {len(sample_news)}")
    for i, news in enumerate(sample_news, 1):
        print(f"  {i}. {news['titulo']} - {news['link']}")
    
    # Filtra notícias com URLs válidas
    print(f"\n🔍 Filtrando notícias com URLs válidas...")
    valid_news = url_validator.filter_valid_news(sample_news, check_content=True)
    
    print(f"\nNotícias após filtragem: {len(valid_news)}")
    for i, news in enumerate(valid_news, 1):
        print(f"  {i}. {news['titulo']} - {news['link']}")
        
        # Mostra informações de validação
        validation_info = news.get('url_validation', {})
        print(f"     ✅ Status: {validation_info.get('status_code', 'N/A')}")
        print(f"     ⏱️ Tempo: {validation_info.get('response_time', 0):.2f}s")
        print(f"     📄 Conteúdo: {'Válido' if validation_info.get('has_valid_content') else 'Inválido'}")
    
    return valid_news

def demonstrate_integration_with_processor():
    """Demonstra integração com o processador de dados"""
    
    print("\n\n=== INTEGRAÇÃO COM PROCESSADOR DE DADOS ===\n")
    
    # Notícias de exemplo
    sample_news = [
        {
            "categoria": "Investimentos",
            "titulo": "Investimento válido com URL acessível",
            "link": "https://valor.com.br/empresas",
            "descricao_detalhada": "Descrição detalhada do investimento.",
            "data": "15/07/2025",
            "municipio": "São Paulo",
            "tipo_investimento": "Construção",
            "valor_estimado": "50000000",
            "fonte_financiamento": "Recursos próprios",
            "fonte_noticia": "Valor Econômico"
        },
        {
            "categoria": "Investimentos", 
            "titulo": "Investimento com URL inválida",
            "link": "https://site-que-nao-existe-404.com/noticia",
            "descricao_detalhada": "Esta notícia será filtrada por URL inválida.",
            "data": "10/07/2025",
            "municipio": "Campinas",
            "tipo_investimento": "Expansão",
            "valor_estimado": "30000000",
            "fonte_financiamento": "Financiamento bancário",
            "fonte_noticia": "Fonte Inexistente"
        }
    ]
    
    print(f"Processando {len(sample_news)} notícias com validação de URL habilitada...")
    
    # Processa com validação de URL habilitada
    processed_news = data_processor.process_news_batch(
        sample_news, 
        verify_credibility=True, 
        validate_urls=True
    )
    
    print(f"\nNotícias processadas: {len(processed_news)}")
    
    for i, news in enumerate(processed_news, 1):
        print(f"\n--- Notícia {i} ---")
        print(f"Título: {news.titulo}")
        print(f"URL: {news.link}")
        print(f"Qualidade dos dados: {news.qualidade_dados:.2f}")
        print(f"Score de credibilidade: {news.credibility_score:.2f}")
        print(f"É confiável: {'✅ SIM' if news.is_credible else '❌ NÃO'}")
        
        if hasattr(news, 'url_validation_info'):
            print(f"Validação de URL: ✅ Aprovada")
        
        if news.warning_flags:
            print(f"Alertas: {', '.join(news.warning_flags)}")

def demonstrate_validation_criteria():
    """Demonstra os critérios de validação de URLs"""
    
    print("\n=== CRITÉRIOS DE VALIDAÇÃO DE URLs ===\n")
    
    print("1. VERIFICAÇÃO DE ACESSIBILIDADE:")
    print("   - Status HTTP 200-299: URL acessível")
    print("   - Status HTTP 404: Página não encontrada")
    print("   - Status HTTP 403: Acesso negado")
    print("   - Status HTTP 500: Erro do servidor")
    print("   - Timeout: URL inacessível")
    
    print("\n2. ANÁLISE DE CONTEÚDO:")
    print("   ✅ Indicadores de conteúdo válido:")
    print("      - Presença de tags HTML estruturais (<title>, <h1>, <article>)")
    print("      - Conteúdo com mais de 500 caracteres")
    print("      - Estrutura de página de notícia")
    
    print("\n   ❌ Indicadores de problema:")
    print("      - Mensagens de erro (404, página não encontrada)")
    print("      - Paywall ou bloqueio de conteúdo")
    print("      - Conteúdo insuficiente")
    
    print("\n3. CONFIGURAÇÕES DE SEGURANÇA:")
    print("   - User-Agent de navegador real")
    print("   - Headers HTTP apropriados")
    print("   - Timeout de 15 segundos")
    print("   - Máximo 3 tentativas com retry")
    print("   - Pausa de 1 segundo entre requisições")
    
    print("\n4. RELATÓRIOS GERADOS:")
    print("   - Taxa de acessibilidade")
    print("   - Taxa de conteúdo válido")
    print("   - Tempo médio de resposta")
    print("   - Distribuição de status codes")
    print("   - Tipos de erro mais comuns")

if __name__ == "__main__":
    # Executa exemplos
    print("🔍 SISTEMA DE VALIDAÇÃO DE URLs PARA NOTÍCIAS")
    print("=" * 50)
    
    # Exemplo 1: Validação básica de URLs
    url_report = example_url_validation()
    
    # Exemplo 2: Filtragem de notícias
    valid_news = example_news_filtering()
    
    # Exemplo 3: Integração com processador
    demonstrate_integration_with_processor()
    
    # Exemplo 4: Critérios de validação
    demonstrate_validation_criteria()
    
    # Salva relatório em arquivo
    with open('url_validation_report_example.json', 'w', encoding='utf-8') as f:
        json.dump(url_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ Relatório salvo em 'url_validation_report_example.json'")
    print("✅ Validador de URLs implementado com sucesso!")
    print("\n🚀 Para usar no sistema principal:")
    print("   python src/main.py")
    print("   (A validação de URLs roda automaticamente!)")