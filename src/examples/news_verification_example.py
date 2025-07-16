"""
Exemplo de uso do verificador de notícias falsas
Demonstra como usar o sistema de verificação de credibilidade
"""

from utils.news_verifier import news_verifier
from utils.data_processor import data_processor
import json

def example_news_verification():
    """Exemplo de verificação de notícias"""
    
    # Exemplos de notícias para teste
    sample_news = [
        {
            # Notícia confiável
            "categoria": "Investimentos",
            "titulo": "Empresa anuncia investimento de R$ 50 milhões em nova fábrica em Campinas",
            "link": "https://valor.com.br/empresas/exemplo-investimento-campinas",
            "descricao_detalhada": "A empresa XYZ anunciou oficialmente um investimento de R$ 50 milhões para construção de nova unidade fabril em Campinas, com previsão de gerar 200 empregos diretos.",
            "data": "15/07/2025",
            "municipio": "Campinas",
            "tipo_investimento": "Construção",
            "valor_estimado": "50000000",
            "fonte_financiamento": "Recursos próprios",
            "fonte_noticia": "Valor Econômico"
        },
        {
            # Notícia suspeita
            "categoria": "Investimentos",
            "titulo": "URGENTE! BOMBA: Investimento trilionário vai revolucionar São Paulo!!!",
            "link": "https://noticias-fake.blogspot.com/investimento-trilionario",
            "descricao_detalhada": "Segundo rumores, uma fonte não revelada confirmou que um investimento de trilhões de reais vai transformar São Paulo. Informações extraoficiais indicam retorno garantido de 1000%.",
            "data": "30/12/2025",
            "municipio": "não identificado",
            "tipo_investimento": "não especificado",
            "valor_estimado": "não informado",
            "fonte_financiamento": "não informado",
            "fonte_noticia": "Blog Notícias"
        },
        {
            # Notícia moderadamente confiável
            "categoria": "Expansões",
            "titulo": "Indústria planeja ampliação em Sorocaba",
            "link": "https://diariodesorocaba.com.br/industria-ampliacao",
            "descricao_detalhada": "Indústria do setor alimentício planeja ampliar suas operações em Sorocaba, com investimento estimado em R$ 10 milhões.",
            "data": "10/07/2025",
            "municipio": "Sorocaba",
            "tipo_investimento": "Ampliação",
            "valor_estimado": "10000000",
            "fonte_financiamento": "não informado",
            "fonte_noticia": "Diário de Sorocaba"
        }
    ]
    
    print("=== EXEMPLO DE VERIFICAÇÃO DE NOTÍCIAS FALSAS ===\n")
    
    # Verifica cada notícia individualmente
    print("1. VERIFICAÇÃO INDIVIDUAL:")
    for i, news in enumerate(sample_news, 1):
        print(f"\n--- Notícia {i} ---")
        print(f"Título: {news['titulo']}")
        
        result = news_verifier.verify_news(news)
        
        print(f"Score de Credibilidade: {result.credibility_score:.2f}")
        print(f"É Confiável: {'✅ SIM' if result.is_credible else '❌ NÃO'}")
        print(f"Recomendação: {result.recommendation}")
        
        if result.warning_flags:
            print(f"Alertas: {', '.join(result.warning_flags)}")
        
        print(f"Detalhes da Verificação:")
        for key, value in result.verification_details.items():
            print(f"  - {key}: {value:.2f}")
    
    # Verifica lote de notícias
    print(f"\n\n2. VERIFICAÇÃO EM LOTE:")
    batch_results = news_verifier.batch_verify_news(sample_news)
    
    credible_count = sum(1 for r in batch_results if r.is_credible)
    print(f"Total de notícias: {len(sample_news)}")
    print(f"Notícias confiáveis: {credible_count}")
    print(f"Taxa de credibilidade: {credible_count/len(sample_news):.1%}")
    
    # Gera relatório detalhado
    print(f"\n\n3. RELATÓRIO DE VERIFICAÇÃO:")
    report = news_verifier.generate_verification_report(batch_results)
    
    print(f"Score médio de credibilidade: {report['verification_summary']['average_credibility_score']:.2f}")
    print(f"Taxa de credibilidade: {report['verification_summary']['credibility_rate']:.1%}")
    
    print(f"\nDistribuição de qualidade:")
    for quality, count in report['quality_distribution'].items():
        print(f"  - {quality}: {count} notícias")
    
    print(f"\nAlertas mais comuns:")
    for flag, count in list(report['common_warning_flags'].items())[:5]:
        print(f"  - {flag}: {count} ocorrências")
    
    print(f"\nDistribuição de recomendações:")
    for rec, count in report['recommendations_distribution'].items():
        print(f"  - {rec}: {count} notícias")
    
    # Demonstra integração com processador de dados
    print(f"\n\n4. INTEGRAÇÃO COM PROCESSADOR DE DADOS:")
    processed_news = data_processor.process_news_batch(sample_news, verify_credibility=True)
    
    print(f"Notícias processadas: {len(processed_news)}")
    for i, news in enumerate(processed_news, 1):
        print(f"\nNotícia {i}:")
        print(f"  - Título: {news.titulo[:50]}...")
        print(f"  - Qualidade dos dados: {news.qualidade_dados:.2f}")
        print(f"  - Score de credibilidade: {news.credibility_score:.2f}")
        print(f"  - É confiável: {'✅ SIM' if news.is_credible else '❌ NÃO'}")
        print(f"  - Recomendação: {news.verification_recommendation}")
        if news.warning_flags:
            print(f"  - Alertas: {', '.join(news.warning_flags)}")
    
    return report

def demonstrate_verification_criteria():
    """Demonstra os critérios de verificação"""
    
    print("\n=== CRITÉRIOS DE VERIFICAÇÃO DE CREDIBILIDADE ===\n")
    
    print("1. CREDIBILIDADE DA FONTE (30% do score):")
    print("   - Tier 1 (Score 1.0): Estadão, Valor, Folha, Globo, UOL, BNDES, Gov.br")
    print("   - Tier 2 (Score 0.8): DCI, Correio Popular, DGABC, Jornal de Campinas")
    print("   - Tier 3 (Score 0.6): Diários regionais, jornais locais")
    print("   - Suspeitas (Score 0.2): Blogspot, WordPress, domínios com 'fake', 'viral'")
    
    print("\n2. QUALIDADE DO CONTEÚDO (25% do score):")
    print("   - Penaliza títulos clickbait: 'URGENTE', 'BOMBA', 'CHOCANTE'")
    print("   - Penaliza conteúdo suspeito: 'fonte não revelada', 'segundo rumores'")
    print("   - Penaliza valores irreais: 'trilhões de reais', 'retorno garantido'")
    print("   - Penaliza descrições muito curtas ou excesso de maiúsculas")
    
    print("\n3. CONSISTÊNCIA DE DATA (15% do score):")
    print("   - Verifica se data está no futuro (suspeito)")
    print("   - Verifica se data é muito antiga")
    print("   - Prioriza notícias de 2025")
    
    print("\n4. COERÊNCIA FACTUAL (15% do score):")
    print("   - Verifica se município é válido")
    print("   - Verifica se tipo de investimento é específico")
    print("   - Verifica coerência entre título e descrição")
    
    print("\n5. DETALHES TÉCNICOS (15% do score):")
    print("   - Verifica presença de campos obrigatórios")
    print("   - Bonifica informações sobre setor e CNAE")
    
    print("\n=== THRESHOLDS DE CREDIBILIDADE ===")
    print("   - Alta (≥0.8): ACEITAR")
    print("   - Média (≥0.6): ACEITAR_COM_RESSALVAS ou REVISAR")
    print("   - Baixa (≥0.4): REVISAR_CUIDADOSAMENTE")
    print("   - Muito Baixa (<0.4): REJEITAR")

if __name__ == "__main__":
    # Executa exemplos
    report = example_news_verification()
    demonstrate_verification_criteria()
    
    # Salva relatório em arquivo
    with open('verification_report_example.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ Relatório salvo em 'verification_report_example.json'")
    print("✅ Verificador de notícias falsas implementado com sucesso!")