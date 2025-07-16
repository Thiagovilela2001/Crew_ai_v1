"""
Sistema de validação de ferramentas para CrewAI
Garante que todas as chamadas de ferramentas tenham parâmetros válidos
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class ToolValidator:
    """Validador de parâmetros para ferramentas do CrewAI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging estruturado"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def validate_google_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e sanitiza parâmetros para Google Search Tool
        
        Args:
            params: Dicionário com parâmetros da ferramenta
            
        Returns:
            Dicionário com parâmetros validados e sanitizados
        """
        validated_params = {}
        
        # Log detalhado dos parâmetros recebidos para debug
        self.logger.info(f"Parâmetros recebidos para validação: {params}")
        self.logger.info(f"Tipo dos parâmetros: {type(params)}")
        
        # Query é obrigatório - tratamento mais robusto
        query_value = None
        
        # Verifica diferentes formas de receber a query
        if 'query' in params:
            query_value = params['query']
        elif 'q' in params:  # Algumas ferramentas podem usar 'q'
            query_value = params['q']
        elif len(params) == 1 and isinstance(list(params.values())[0], str):
            # Se há apenas um parâmetro string, assume que é a query
            query_value = list(params.values())[0]
            self.logger.info(f"Query inferida de parâmetro único: '{query_value}'")
        
        # Se ainda não encontrou query, verifica se params é uma string
        if query_value is None and isinstance(params, str):
            query_value = params
            self.logger.info(f"Parâmetros recebidos como string, usando como query: '{query_value}'")
        
        # Validação final da query
        if query_value is None or (isinstance(query_value, str) and query_value.strip() == ''):
            self.logger.error(f"Parâmetro 'query' ausente ou vazio. Parâmetros recebidos: {params}")
            # Fornece uma query padrão para evitar falha total
            default_query = "investimento expansão São Paulo 2025"
            self.logger.warning(f"Usando query padrão: '{default_query}'")
            validated_params['query'] = default_query
        else:
            validated_params['query'] = str(query_value).strip()
        
        # Log da query validada para debug
        self.logger.info(f"Query validada: '{validated_params['query']}'")
        
        # Quantidade (opcional, padrão 5)
        quantidade = params.get('quantidade', 5)
        if isinstance(quantidade, str):
            try:
                quantidade = int(quantidade)
            except ValueError:
                self.logger.warning(f"Quantidade inválida '{quantidade}', usando padrão 5")
                quantidade = 5
        
        validated_params['quantidade'] = max(1, min(quantidade, 50))  # Entre 1 e 50
        
        # Data limite (opcional)
        data_limite = params.get('data_limite')
        if data_limite:
            validated_params['data_limite'] = self._validate_date_format(data_limite)
        
        # Tentativas de query (opcional)
        tentativas_query = params.get('tentativas_query')
        if tentativas_query:
            if isinstance(tentativas_query, str):
                tentativas_query = [tentativas_query]
            elif not isinstance(tentativas_query, list):
                self.logger.warning("tentativas_query deve ser lista ou string, ignorando")
                tentativas_query = None
            
            if tentativas_query:
                validated_params['tentativas_query'] = [
                    str(q).strip() for q in tentativas_query if q and str(q).strip()
                ]
        
        self.logger.info(f"Parâmetros Google Search validados: {validated_params}")
        return validated_params
    
    def validate_scrape_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida parâmetros para ScrapeWebsiteTool
        
        Args:
            params: Dicionário com parâmetros da ferramenta
            
        Returns:
            Dicionário com parâmetros validados
        """
        validated_params = {}
        
        # URL é obrigatório
        if 'website_url' not in params or not params['website_url']:
            raise ValueError("Parâmetro 'website_url' é obrigatório")
        
        url = str(params['website_url']).strip()
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"URL inválida: {url}")
        
        validated_params['website_url'] = url
        
        self.logger.info(f"Parâmetros Scrape validados: {validated_params}")
        return validated_params
    
    def sanitize_tool_input(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza entrada de ferramenta baseado no nome da ferramenta
        
        Args:
            tool_name: Nome da ferramenta
            params: Parâmetros originais
            
        Returns:
            Parâmetros sanitizados
        """
        try:
            if tool_name.lower() in ['google search tool', 'googlesearchtool']:
                return self.validate_google_search_params(params)
            elif tool_name.lower() in ['scrapewebsitetool', 'read website content']:
                return self.validate_scrape_params(params)
            else:
                self.logger.warning(f"Ferramenta desconhecida: {tool_name}")
                return params
                
        except Exception as e:
            self.log_validation_error(str(e), {
                'tool_name': tool_name,
                'original_params': params
            })
            raise
    
    def log_validation_error(self, error: str, context: Dict[str, Any]) -> None:
        """
        Registra erro de validação com contexto estruturado
        
        Args:
            error: Mensagem de erro
            context: Contexto adicional do erro
        """
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'level': 'ERROR',
            'component': 'ToolValidator',
            'message': error,
            'context': context
        }
        
        self.logger.error(json.dumps(error_log, ensure_ascii=False, indent=2))
    
    def _validate_date_format(self, date_str: str) -> Optional[str]:
        """
        Valida formato de data DD/MM/YYYY
        
        Args:
            date_str: String de data para validar
            
        Returns:
            Data validada ou None se inválida
        """
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return date_str
        except ValueError:
            self.logger.warning(f"Formato de data inválido: {date_str}")
            return None


# Instância global do validador
tool_validator = ToolValidator()