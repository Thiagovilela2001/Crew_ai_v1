"""
Validador de URLs para verificar se notícias realmente existem
Verifica acessibilidade, status HTTP e conteúdo válido
"""

import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
import re

@dataclass
class URLValidationResult:
    """Resultado da validação de uma URL"""
    url: str
    is_accessible: bool
    status_code: int
    response_time: float
    content_length: int
    content_type: str
    final_url: str  # URL após redirecionamentos
    error_message: str
    validation_timestamp: str
    has_valid_content: bool
    content_indicators: Dict[str, bool]

class URLValidator:
    """Validador de URLs para verificar existência de notícias"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_session()
        self._setup_validation_rules()
    
    def _setup_session(self):
        """Configura sessão HTTP com headers apropriados"""
        self.session = requests.Session()
        
        # Headers para parecer um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configurações de timeout e retry
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
    
    def _setup_validation_rules(self):
        """Define regras de validação de conteúdo"""
        self.content_indicators = {
            # Indicadores de conteúdo válido
            'valid_content': [
                r'<title>.*</title>',
                r'<h1.*?>.*</h1>',
                r'<article.*?>',
                r'<main.*?>',
                r'<div.*?class.*?content.*?>',
                r'<div.*?class.*?article.*?>',
                r'<p>.*</p>'
            ],
            
            # Indicadores de página de erro
            'error_indicators': [
                r'404.*not found',
                r'página não encontrada',
                r'page not found',
                r'erro 404',
                r'content not available',
                r'conteúdo não disponível',
                r'acesso negado',
                r'access denied'
            ],
            
            # Indicadores de paywall ou bloqueio
            'blocked_content': [
                r'paywall',
                r'assinante',
                r'subscriber',
                r'login required',
                r'cadastre-se',
                r'faça login'
            ],
            
            # Indicadores de conteúdo de notícia
            'news_indicators': [
                r'publicado.*em',
                r'published.*on',
                r'data.*publicação',
                r'por.*redação',
                r'by.*reporter',
                r'<time.*?>',
                r'datetime.*?='
            ]
        }
    
    def validate_url(self, url: str, check_content: bool = True) -> URLValidationResult:
        """
        Valida uma URL verificando acessibilidade e conteúdo
        
        Args:
            url: URL para validar
            check_content: Se deve verificar o conteúdo da página
            
        Returns:
            Resultado da validação
        """
        start_time = time.time()
        
        # Inicializa resultado
        result = URLValidationResult(
            url=url,
            is_accessible=False,
            status_code=0,
            response_time=0.0,
            content_length=0,
            content_type="",
            final_url=url,
            error_message="",
            validation_timestamp=datetime.now().isoformat(),
            has_valid_content=False,
            content_indicators={}
        )
        
        try:
            # Valida formato da URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                result.error_message = "URL inválida: formato incorreto"
                return result
            
            # Tenta acessar a URL com retry
            response = None
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Tentativa {attempt + 1} de acessar: {url}")
                    
                    response = self.session.get(
                        url,
                        timeout=self.timeout,
                        allow_redirects=True,
                        stream=True  # Para não baixar todo o conteúdo de uma vez
                    )
                    
                    break  # Sucesso, sai do loop
                    
                except requests.exceptions.RequestException as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"Erro na tentativa {attempt + 1}: {str(e)}. Tentando novamente em {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                    else:
                        self.logger.error(f"Falha após {self.max_retries} tentativas: {str(e)}")
            
            if response is None:
                result.error_message = f"Falha ao acessar URL após {self.max_retries} tentativas: {str(last_error)}"
                return result
            
            # Calcula tempo de resposta
            result.response_time = time.time() - start_time
            result.status_code = response.status_code
            result.final_url = response.url
            result.content_type = response.headers.get('content-type', '')
            
            # Verifica se o status code indica sucesso
            if 200 <= response.status_code < 300:
                result.is_accessible = True
                
                if check_content:
                    # Lê apenas os primeiros KB do conteúdo para análise
                    content_sample = ""
                    try:
                        # Lê até 50KB do conteúdo
                        content_bytes = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            content_bytes += chunk
                            if len(content_bytes) > 50000:  # 50KB
                                break
                        
                        content_sample = content_bytes.decode('utf-8', errors='ignore')
                        result.content_length = len(content_sample)
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao ler conteúdo de {url}: {str(e)}")
                        content_sample = ""
                    
                    # Analisa o conteúdo
                    if content_sample:
                        result.has_valid_content, result.content_indicators = self._analyze_content(content_sample)
                    
            elif 300 <= response.status_code < 400:
                result.error_message = f"Redirecionamento não resolvido: {response.status_code}"
            elif response.status_code == 404:
                result.error_message = "Página não encontrada (404)"
            elif response.status_code == 403:
                result.error_message = "Acesso negado (403)"
            elif response.status_code == 500:
                result.error_message = "Erro interno do servidor (500)"
            else:
                result.error_message = f"Status HTTP inválido: {response.status_code}"
            
        except Exception as e:
            result.error_message = f"Erro inesperado: {str(e)}"
            self.logger.error(f"Erro validando URL {url}: {str(e)}")
        
        finally:
            # Fecha a resposta se foi aberta
            if 'response' in locals() and response:
                response.close()
        
        self.logger.info(f"URL {url} validada: acessível={result.is_accessible}, status={result.status_code}")
        return result
    
    def _analyze_content(self, content: str) -> Tuple[bool, Dict[str, bool]]:
        """
        Analisa o conteúdo da página para determinar se é válido
        
        Args:
            content: Conteúdo HTML da página
            
        Returns:
            Tupla (tem_conteudo_valido, indicadores_detalhados)
        """
        content_lower = content.lower()
        indicators = {}
        
        # Verifica indicadores de conteúdo válido
        has_valid_structure = False
        for pattern in self.content_indicators['valid_content']:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                has_valid_structure = True
                break
        indicators['has_valid_structure'] = has_valid_structure
        
        # Verifica indicadores de erro
        has_error_indicators = False
        for pattern in self.content_indicators['error_indicators']:
            if re.search(pattern, content, re.IGNORECASE):
                has_error_indicators = True
                break
        indicators['has_error_indicators'] = has_error_indicators
        
        # Verifica se há paywall ou bloqueio
        is_blocked = False
        for pattern in self.content_indicators['blocked_content']:
            if re.search(pattern, content, re.IGNORECASE):
                is_blocked = True
                break
        indicators['is_blocked'] = is_blocked
        
        # Verifica indicadores de notícia
        has_news_indicators = False
        for pattern in self.content_indicators['news_indicators']:
            if re.search(pattern, content, re.IGNORECASE):
                has_news_indicators = True
                break
        indicators['has_news_indicators'] = has_news_indicators
        
        # Verifica tamanho mínimo do conteúdo
        has_sufficient_content = len(content.strip()) > 500
        indicators['has_sufficient_content'] = has_sufficient_content
        
        # Determina se o conteúdo é válido
        is_valid = (
            has_valid_structure and
            not has_error_indicators and
            has_sufficient_content and
            not is_blocked
        )
        
        return is_valid, indicators
    
    def batch_validate_urls(self, urls: List[str], check_content: bool = True) -> List[URLValidationResult]:
        """
        Valida uma lista de URLs
        
        Args:
            urls: Lista de URLs para validar
            check_content: Se deve verificar o conteúdo das páginas
            
        Returns:
            Lista de resultados de validação
        """
        results = []
        
        for i, url in enumerate(urls):
            try:
                self.logger.info(f"Validando URL {i+1}/{len(urls)}: {url}")
                
                result = self.validate_url(url, check_content)
                results.append(result)
                
                # Pequena pausa entre requisições para ser respeitoso
                if i < len(urls) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Erro validando URL {url}: {str(e)}")
                # Cria resultado de erro
                error_result = URLValidationResult(
                    url=url,
                    is_accessible=False,
                    status_code=0,
                    response_time=0.0,
                    content_length=0,
                    content_type="",
                    final_url=url,
                    error_message=f"Erro na validação: {str(e)}",
                    validation_timestamp=datetime.now().isoformat(),
                    has_valid_content=False,
                    content_indicators={}
                )
                results.append(error_result)
        
        return results
    
    def filter_valid_news(self, news_list: List[Dict[str, Any]], check_content: bool = True) -> List[Dict[str, Any]]:
        """
        Filtra notícias mantendo apenas aquelas com URLs válidas
        
        Args:
            news_list: Lista de notícias com campo 'link'
            check_content: Se deve verificar o conteúdo das páginas
            
        Returns:
            Lista de notícias com URLs válidas
        """
        if not news_list:
            return []
        
        # Extrai URLs das notícias
        urls = [news.get('link', '') for news in news_list if news.get('link')]
        
        if not urls:
            self.logger.warning("Nenhuma URL encontrada nas notícias")
            return []
        
        # Valida URLs
        self.logger.info(f"Validando {len(urls)} URLs de notícias...")
        validation_results = self.batch_validate_urls(urls, check_content)
        
        # Filtra notícias com URLs válidas
        valid_news = []
        validation_stats = {
            'total': len(news_list),
            'accessible': 0,
            'valid_content': 0,
            'blocked': 0,
            'not_found': 0,
            'error': 0
        }
        
        for news, validation in zip(news_list, validation_results):
            # Adiciona informações de validação à notícia
            news['url_validation'] = {
                'is_accessible': validation.is_accessible,
                'status_code': validation.status_code,
                'has_valid_content': validation.has_valid_content,
                'response_time': validation.response_time,
                'error_message': validation.error_message,
                'validation_timestamp': validation.validation_timestamp
            }
            
            # Atualiza estatísticas
            if validation.is_accessible:
                validation_stats['accessible'] += 1
                
                if validation.has_valid_content:
                    validation_stats['valid_content'] += 1
                    valid_news.append(news)
                elif validation.content_indicators.get('is_blocked', False):
                    validation_stats['blocked'] += 1
                    self.logger.warning(f"URL bloqueada/paywall: {validation.url}")
                else:
                    self.logger.warning(f"Conteúdo inválido: {validation.url}")
            elif validation.status_code == 404:
                validation_stats['not_found'] += 1
                self.logger.warning(f"URL não encontrada: {validation.url}")
            else:
                validation_stats['error'] += 1
                self.logger.error(f"Erro acessando URL: {validation.url} - {validation.error_message}")
        
        # Log das estatísticas
        self.logger.info(f"Validação de URLs concluída:")
        self.logger.info(f"  - Total: {validation_stats['total']}")
        self.logger.info(f"  - Acessíveis: {validation_stats['accessible']}")
        self.logger.info(f"  - Conteúdo válido: {validation_stats['valid_content']}")
        self.logger.info(f"  - Bloqueadas: {validation_stats['blocked']}")
        self.logger.info(f"  - Não encontradas: {validation_stats['not_found']}")
        self.logger.info(f"  - Erros: {validation_stats['error']}")
        
        return valid_news
    
    def generate_validation_report(self, validation_results: List[URLValidationResult]) -> Dict[str, Any]:
        """
        Gera relatório de validação de URLs
        
        Args:
            validation_results: Lista de resultados de validação
            
        Returns:
            Relatório com estatísticas
        """
        if not validation_results:
            return {"error": "Nenhum resultado de validação"}
        
        total_urls = len(validation_results)
        accessible_urls = len([r for r in validation_results if r.is_accessible])
        valid_content_urls = len([r for r in validation_results if r.has_valid_content])
        
        # Calcula tempo médio de resposta
        response_times = [r.response_time for r in validation_results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Conta status codes
        status_codes = {}
        for result in validation_results:
            code = result.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Conta tipos de erro
        error_types = {}
        for result in validation_results:
            if result.error_message:
                error_type = result.error_message.split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        report = {
            'validation_summary': {
                'total_urls': total_urls,
                'accessible_urls': accessible_urls,
                'valid_content_urls': valid_content_urls,
                'accessibility_rate': accessible_urls / total_urls if total_urls > 0 else 0,
                'content_validity_rate': valid_content_urls / total_urls if total_urls > 0 else 0,
                'average_response_time': avg_response_time,
                'validation_timestamp': datetime.now().isoformat()
            },
            'status_code_distribution': dict(sorted(status_codes.items())),
            'error_types': dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)),
            'detailed_results': [
                {
                    'url': r.url,
                    'is_accessible': r.is_accessible,
                    'status_code': r.status_code,
                    'has_valid_content': r.has_valid_content,
                    'response_time': r.response_time,
                    'error_message': r.error_message
                }
                for r in validation_results
            ]
        }
        
        return report


# Instância global do validador
url_validator = URLValidator()