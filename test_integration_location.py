"""
Teste de integração do validador geográfico com o processador de dados
"""

import sys
import os
sys.path.insert(0, 'src')

from utils.data_processor import DataProcessor

def test_location_validation_integration():
    """Testa a integração da validação geográfica no processamento de dados"""
    
    # Criar instância do processador
    processor = DataProcessor()
    
    # Dados de teste com diferentes cenários de localização
    test_news = [
        {
            'titulo': 'Nova fábrica em São Paulo',
            'link': 'http://example.com/news1',
            'descricao_detalhada': 'Empresa anuncia investimento de R$ 100 milhões em nova fábrica na cidade de São Paulo',
            'data': '15/07/2025',
            'municipio': 'São Paulo',
            'tipo_investimento': 'Inauguração',
            'fonte_noticia': 'Portal de Notícias'
        },
        {
            'titulo': 'Investimento em Campinas',
            'link': 'http://example.com/news2',
            'descricao_detalhada': 'Nova unidade industrial será construída em Campinas com investimento de R$ 50 milhões',
            'data': '16/07/2025',
            'municipio': 'Campinas',
            'tipo_investimento': 'Construção',
            'fonte_noticia': 'Jornal Local'
        },
        {
            'titulo': 'Projeto em cidade inexistente',
            'link': 'http://example.com/news3',
            'descricao_detalhada': 'Investimento anunciado em cidade que não existe em SP',
            'data': '16/07/2025',
            'municipio': 'Cidade Inexistente',
            'tipo_investimento': 'Expansão',
            'fonte_noticia': 'Site de Notícias'
        }
    ]
    
    # Processar notícias (sem verificação de credibilidade e URL para teste rápido)
    processed_news = processor.process_news_batch(
        test_news, 
        verify_credibility=False, 
        validate_urls=False
    )
    
    print(f"Processadas {len(processed_news)} notícias")
    
    # Verificar resultados
    for i, news in enumerate(processed_news):
        print(f"\nNotícia {i+1}:")
        print(f"  Título: {news.titulo}")
        print(f"  Município: {news.municipio}")
        print(f"  Validação Município: {news.validacao_municipio}")
        print(f"  Qualidade: {news.qualidade_dados}")
    
    # Verificar se pelo menos as duas primeiras notícias foram validadas
    assert processed_news[0].validacao_municipio == True, "São Paulo deveria ser validado"
    assert processed_news[1].validacao_municipio == True, "Campinas deveria ser validado"
    
    print("\n✅ Teste de integração passou com sucesso!")

if __name__ == "__main__":
    test_location_validation_integration()