"""
Processador de dados robusto para notícias de investimentos
Valida, sanitiza e processa dados coletados com tratamento de erros
"""

import json
import logging
from typing import Dict, List, Any, Union, Optional
from datetime import datetime
from pathlib import Path
import re
from dataclasses import dataclass, field, asdict
from .news_verifier import news_verifier, VerificationResult
from .url_validator import url_validator
from .location_validator import LocationValidator

@dataclass
class InvestmentNews:
    """Estrutura de dados para notícias de investimento"""
    categoria: str = ""
    titulo: str = ""
    link: str = ""
    descricao_detalhada: str = ""
    data: str = ""
    municipio: str = ""
    tipo_investimento: str = ""
    valor_estimado: Optional[Union[str, float]] = None
    fonte_financiamento: Optional[str] = None
    fonte_noticia: str = ""
    piesp_setor: Optional[str] = None
    cnae_investimento: Optional[Union[str, float]] = None
    investimento_estrangeiro: str = "não identificado"
    esg: str = "não identificado"
    pme: str = "não identificado"
    
    # Campos de controle
    data_coleta: str = field(default_factory=lambda: datetime.now().isoformat())
    tentativas_busca: List[str] = field(default_factory=list)
    validacao_municipio: bool = False
    qualidade_dados: float = 0.0
    
    # Campos de verificação de credibilidade
    credibility_score: float = 0.0
    is_credible: bool = True
    warning_flags: List[str] = field(default_factory=list)
    verification_recommendation: str = ""

class DataProcessor:
    """Processador robusto de dados de investimentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.location_validator = LocationValidator()
        self._setup_validation_rules()
        self._setup_default_values()
    
    def _setup_validation_rules(self):
        """Define regras de validação para campos"""
        self.required_fields = [
            'titulo', 'link', 'descricao_detalhada', 'data', 
            'municipio', 'tipo_investimento'
        ]
        
        self.field_validators = {
            'link': self._validate_url,
            'data': self._validate_date,
            'valor_estimado': self._validate_value,
            'cnae_investimento': self._validate_cnae
        }
        
        self.field_sanitizers = {
            'titulo': self._sanitize_text,
            'descricao_detalhada': self._sanitize_text,
            'municipio': self._sanitize_location,
            'fonte_noticia': self._sanitize_text,
            'categoria': self._sanitize_category,
            'tipo_investimento': self._sanitize_investment_type
        }
    
    def _setup_default_values(self):
        """Define valores padrão para campos"""
        self.default_values = {
            'categoria': 'Investimentos',
            'investimento_estrangeiro': 'não identificado',
            'esg': 'não identificado',
            'pme': 'não identificado',
            'fonte_financiamento': 'não informado',
            'piesp_setor': 'não classificado'
        }
    
    def validate_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida se campos obrigatórios estão presentes e válidos
        
        Args:
            data: Dicionário com dados da notícia
            
        Returns:
            Dicionário com dados validados e relatório de validação
        """
        validation_report = {
            'valid': True,
            'missing_fields': [],
            'invalid_fields': [],
            'warnings': []
        }
        
        validated_data = data.copy()
        
        # Verifica campos obrigatórios
        for field in self.required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                validation_report['missing_fields'].append(field)
                validation_report['valid'] = False
                self.logger.warning(f"Campo obrigatório ausente: {field}")
        
        # Valida campos específicos
        for field, validator in self.field_validators.items():
            if field in data and data[field]:
                try:
                    is_valid, validated_value = validator(data[field])
                    if not is_valid:
                        validation_report['invalid_fields'].append(field)
                        validation_report['warnings'].append(f"Campo {field} inválido: {data[field]}")
                    else:
                        validated_data[field] = validated_value
                except Exception as e:
                    validation_report['invalid_fields'].append(field)
                    validation_report['warnings'].append(f"Erro validando {field}: {str(e)}")
        
        validated_data['_validation_report'] = validation_report
        return validated_data
    
    def apply_default_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica valores padrão para campos ausentes
        
        Args:
            data: Dicionário com dados da notícia
            
        Returns:
            Dicionário com valores padrão aplicados
        """
        processed_data = data.copy()
        
        for field, default_value in self.default_values.items():
            if field not in processed_data or not processed_data[field] or str(processed_data[field]).strip() == '':
                processed_data[field] = default_value
                self.logger.info(f"Valor padrão aplicado para {field}: {default_value}")
        
        return processed_data
    
    def validate_and_enhance_location(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e aprimora informações de localização usando o LocationValidator
        
        Args:
            data: Dicionário com dados da notícia
            
        Returns:
            Dicionário com localização validada e aprimorada
        """
        enhanced_data = data.copy()
        
        # Validar município se presente
        if 'municipio' in enhanced_data and enhanced_data['municipio']:
            municipio = enhanced_data['municipio']
            
            # Validar se é município de SP
            is_valid = self.location_validator.validate_municipality(municipio)
            enhanced_data['validacao_municipio'] = is_valid
            
            if not is_valid:
                # Tentar extrair localização do texto da notícia
                full_text = f"{enhanced_data.get('titulo', '')} {enhanced_data.get('descricao_detalhada', '')}"
                extracted_location = self.location_validator.extract_location_from_text(full_text)
                
                if extracted_location:
                    self.logger.info(f"Localização extraída do texto: '{extracted_location}' (original: '{municipio}')")
                    enhanced_data['municipio'] = extracted_location
                    enhanced_data['validacao_municipio'] = True
                else:
                    # Tentar resolver ambiguidade via scraping se tiver URL
                    if 'link' in enhanced_data and enhanced_data['link']:
                        resolved_location = self.location_validator.resolve_ambiguous_location(
                            municipio, enhanced_data['link']
                        )
                        if resolved_location:
                            self.logger.info(f"Localização resolvida via scraping: '{resolved_location}'")
                            enhanced_data['municipio'] = resolved_location
                            enhanced_data['validacao_municipio'] = True
                        else:
                            self.logger.warning(f"Não foi possível validar município: '{municipio}'")
                    else:
                        self.logger.warning(f"Município '{municipio}' não validado - sem URL para scraping")
            else:
                self.logger.debug(f"Município validado: '{municipio}'")
        
        return enhanced_data
    
    def sanitize_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza tipos de dados e formatos
        
        Args:
            data: Dicionário com dados da notícia
            
        Returns:
            Dicionário com dados sanitizados
        """
        sanitized_data = data.copy()
        
        # Aplica sanitizadores específicos
        for field, sanitizer in self.field_sanitizers.items():
            if field in sanitized_data and sanitized_data[field]:
                try:
                    sanitized_data[field] = sanitizer(sanitized_data[field])
                except Exception as e:
                    self.logger.warning(f"Erro sanitizando {field}: {str(e)}")
        
        # Converte tipos específicos
        if 'valor_estimado' in sanitized_data and sanitized_data['valor_estimado']:
            sanitized_data['valor_estimado'] = self._convert_value_to_number(sanitized_data['valor_estimado'])
        
        if 'cnae_investimento' in sanitized_data and sanitized_data['cnae_investimento']:
            sanitized_data['cnae_investimento'] = self._convert_cnae_to_number(sanitized_data['cnae_investimento'])
        
        return sanitized_data
    
    def calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calcula score de qualidade dos dados (0-1)
        
        Args:
            data: Dicionário com dados da notícia
            
        Returns:
            Score de qualidade entre 0 e 1
        """
        total_score = 0
        max_score = 0
        
        # Pontuação por campos obrigatórios preenchidos
        for field in self.required_fields:
            max_score += 2
            if field in data and data[field] and str(data[field]).strip():
                total_score += 2
        
        # Pontuação por campos opcionais preenchidos
        optional_fields = ['valor_estimado', 'fonte_financiamento', 'piesp_setor', 'cnae_investimento']
        for field in optional_fields:
            max_score += 1
            if field in data and data[field] and str(data[field]).strip() and data[field] != 'não identificado':
                total_score += 1
        
        # Pontuação por qualidade do conteúdo
        max_score += 3
        if 'descricao_detalhada' in data and len(str(data['descricao_detalhada'])) > 50:
            total_score += 1
        if 'titulo' in data and len(str(data['titulo'])) > 10:
            total_score += 1
        if 'link' in data and self._validate_url(data['link'])[0]:
            total_score += 1
        
        quality_score = total_score / max_score if max_score > 0 else 0
        return round(quality_score, 2)
    
    def process_news_batch(self, news_list: List[Dict[str, Any]], verify_credibility: bool = True, validate_urls: bool = True) -> List[InvestmentNews]:
        """
        Processa um lote de notícias aplicando todas as validações incluindo verificação de credibilidade e URLs
        
        Args:
            news_list: Lista de dicionários com dados das notícias
            verify_credibility: Se deve verificar credibilidade das notícias
            validate_urls: Se deve validar se as URLs das notícias existem
            
        Returns:
            Lista de objetos InvestmentNews processados
        """
        processed_news = []
        verification_results = []
        
        # Fase 0: Validação de URLs (se habilitada)
        if validate_urls and news_list:
            self.logger.info("Iniciando validação de URLs das notícias...")
            try:
                # Filtra notícias com URLs válidas
                valid_news_list = url_validator.filter_valid_news(news_list, check_content=True)
                
                if len(valid_news_list) < len(news_list):
                    removed_count = len(news_list) - len(valid_news_list)
                    self.logger.warning(f"{removed_count} notícias removidas por URLs inválidas ou inacessíveis")
                
                news_list = valid_news_list
                
            except Exception as e:
                self.logger.error(f"Erro na validação de URLs: {str(e)}")
                # Continua sem validação de URL se houver erro
        
        # Primeira fase: processamento básico
        for i, news_data in enumerate(news_list):
            try:
                # Aplica processamento completo
                validated_data = self.validate_required_fields(news_data)
                default_applied_data = self.apply_default_values(validated_data)
                sanitized_data = self.sanitize_data_types(default_applied_data)
                
                # Validação e aprimoramento de localização
                location_enhanced_data = self.validate_and_enhance_location(sanitized_data)
                
                # Calcula qualidade dos dados usando dados aprimorados
                quality_score = self.calculate_data_quality_score(location_enhanced_data)
                location_enhanced_data['qualidade_dados'] = quality_score
                
                # Cria objeto estruturado
                news_obj = InvestmentNews(**{k: v for k, v in location_enhanced_data.items() 
                                           if k in InvestmentNews.__dataclass_fields__})
                
                processed_news.append(news_obj)
                
                self.logger.info(f"Notícia {i+1} processada com qualidade {quality_score:.2f}")
                
            except Exception as e:
                self.logger.error(f"Erro processando notícia {i+1}: {str(e)}")
                # Cria entrada com dados mínimos para não perder a notícia
                fallback_news = InvestmentNews(
                    titulo=str(news_data.get('titulo', 'Título não disponível')),
                    link=str(news_data.get('link', '')),
                    descricao_detalhada=str(news_data.get('descricao_detalhada', 'Descrição não disponível')),
                    qualidade_dados=0.1
                )
                processed_news.append(fallback_news)
        
        # Segunda fase: verificação de credibilidade
        if verify_credibility and processed_news:
            self.logger.info("Iniciando verificação de credibilidade das notícias...")
            
            try:
                # Converte objetos para dicionários para verificação
                news_dicts = [asdict(news) for news in processed_news]
                verification_results = news_verifier.batch_verify_news(news_dicts)
                
                # Aplica resultados da verificação
                credible_news = []
                for i, (news, verification) in enumerate(zip(processed_news, verification_results)):
                    # Adiciona informações de verificação ao objeto
                    news.credibility_score = verification.credibility_score
                    news.is_credible = verification.is_credible
                    news.warning_flags = verification.warning_flags
                    news.verification_recommendation = verification.recommendation
                    
                    # Ajusta qualidade dos dados baseado na credibilidade
                    original_quality = news.qualidade_dados
                    credibility_weight = 0.3  # 30% do peso para credibilidade
                    news.qualidade_dados = (
                        original_quality * (1 - credibility_weight) + 
                        verification.credibility_score * credibility_weight
                    )
                    
                    # Filtra notícias com credibilidade muito baixa
                    if verification.credibility_score >= 0.3:  # Threshold mínimo
                        credible_news.append(news)
                        self.logger.info(f"Notícia {i+1} aprovada: credibilidade {verification.credibility_score:.2f}")
                    else:
                        self.logger.warning(f"Notícia {i+1} rejeitada por baixa credibilidade: {verification.credibility_score:.2f}")
                
                processed_news = credible_news
                
                # Gera relatório de verificação
                if verification_results:
                    verification_report = news_verifier.generate_verification_report(verification_results)
                    self.logger.info(f"Verificação concluída: {verification_report['verification_summary']['credible_news']}/{verification_report['verification_summary']['total_news_verified']} notícias aprovadas")
                
            except Exception as e:
                self.logger.error(f"Erro na verificação de credibilidade: {str(e)}")
                # Continua sem verificação se houver erro
        
        return processed_news
    
    def export_to_json(self, data: List[InvestmentNews], filename: str) -> bool:
        """
        Exporta dados para arquivo JSON com tratamento de erros
        
        Args:
            data: Lista de objetos InvestmentNews
            filename: Nome do arquivo de saída
            
        Returns:
            True se exportação foi bem-sucedida
        """
        try:
            # Garante que diretório existe
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Converte objetos para dicionários
            json_data = [asdict(news) for news in data]
            
            # Adiciona metadados
            export_metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'total_records': len(json_data),
                'avg_quality_score': sum(news.qualidade_dados for news in data) / len(data) if data else 0,
                'data': json_data
            }
            
            # Salva arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_metadata, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"Dados exportados com sucesso para: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro exportando dados para {filename}: {str(e)}")
            return False
    
    def generate_processing_report(self, processed_data: List[InvestmentNews]) -> Dict[str, Any]:
        """
        Gera relatório de processamento dos dados
        
        Args:
            processed_data: Lista de dados processados
            
        Returns:
            Relatório com estatísticas de processamento
        """
        if not processed_data:
            return {'error': 'Nenhum dado processado'}
        
        quality_scores = [news.qualidade_dados for news in processed_data]
        
        report = {
            'processing_summary': {
                'total_records': len(processed_data),
                'processing_timestamp': datetime.now().isoformat()
            },
            'quality_metrics': {
                'avg_quality_score': sum(quality_scores) / len(quality_scores),
                'min_quality_score': min(quality_scores),
                'max_quality_score': max(quality_scores),
                'high_quality_count': len([s for s in quality_scores if s >= 0.8]),
                'medium_quality_count': len([s for s in quality_scores if 0.5 <= s < 0.8]),
                'low_quality_count': len([s for s in quality_scores if s < 0.5])
            },
            'field_completion': self._calculate_field_completion(processed_data),
            'data_distribution': self._calculate_data_distribution(processed_data)
        }
        
        return report
    
    # Métodos de validação específicos
    def _validate_url(self, url: str) -> tuple[bool, str]:
        """Valida formato de URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        is_valid = bool(url_pattern.match(url))
        return is_valid, url.strip()
    
    def _validate_date(self, date_str: str) -> tuple[bool, str]:
        """Valida formato de data"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2} de \w+ de \d{4}'  # DD de mês de YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, date_str):
                return True, date_str.strip()
        
        return False, date_str.strip()
    
    def _validate_value(self, value: Union[str, float]) -> tuple[bool, Union[str, float]]:
        """Valida valor de investimento"""
        if isinstance(value, (int, float)):
            return True, value
        
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto vírgulas e pontos
            cleaned = re.sub(r'[^\d,.]', '', value)
            if cleaned:
                return True, value.strip()
        
        return True, value  # Aceita qualquer valor como string
    
    def _validate_cnae(self, cnae: Union[str, float]) -> tuple[bool, Union[str, float]]:
        """Valida código CNAE"""
        if isinstance(cnae, (int, float)):
            return True, cnae
        
        if isinstance(cnae, str):
            # CNAE deve ter formato XXXX-X/XX
            cnae_pattern = r'\d{4}-?\d{1}/?\d{2}'
            if re.match(cnae_pattern, cnae.replace('-', '').replace('/', '')):
                return True, cnae.strip()
        
        return True, cnae  # Aceita qualquer valor
    
    # Métodos de sanitização
    def _sanitize_text(self, text: str) -> str:
        """Sanitiza texto removendo caracteres especiais"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove quebras de linha excessivas
        text = re.sub(r'\n+', ' ', text)
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        # Remove caracteres de controle
        text = ''.join(char for char in text if ord(char) >= 32)
        
        return text.strip()
    
    def _sanitize_location(self, location: str) -> str:
        """Sanitiza nome de localização"""
        if not isinstance(location, str):
            location = str(location)
        
        # Remove prefixos comuns
        location = re.sub(r'^(município de|cidade de|região de)\s+', '', location, flags=re.IGNORECASE)
        # Remove sufixos comuns
        location = re.sub(r'\s*\(SP\)$', '', location, flags=re.IGNORECASE)
        
        return self._sanitize_text(location).title()
    
    def _sanitize_category(self, category: str) -> str:
        """Sanitiza categoria da notícia"""
        if not isinstance(category, str):
            category = str(category)
        
        category_mapping = {
            'investimento': 'Investimentos',
            'expansao': 'Expansões',
            'construcao': 'Construções',
            'inauguracao': 'Inaugurações',
            'modernizacao': 'Modernizações'
        }
        
        category_lower = category.lower()
        for key, value in category_mapping.items():
            if key in category_lower:
                return value
        
        return category.title()
    
    def _sanitize_investment_type(self, inv_type: str) -> str:
        """Sanitiza tipo de investimento"""
        if not isinstance(inv_type, str):
            inv_type = str(inv_type)
        
        type_mapping = {
            'inauguracao': 'Inauguração',
            'expansao': 'Expansão',
            'construcao': 'Construção',
            'instalacao': 'Instalação',
            'modernizacao': 'Modernização',
            'ampliacao': 'Ampliação'
        }
        
        inv_type_lower = inv_type.lower()
        for key, value in type_mapping.items():
            if key in inv_type_lower:
                return value
        
        return inv_type.title()
    
    # Métodos auxiliares
    def _convert_value_to_number(self, value: Union[str, float]) -> Union[str, float]:
        """Converte valor para número quando possível"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # Tenta extrair número do texto
            numbers = re.findall(r'[\d,]+\.?\d*', value)
            if numbers:
                try:
                    # Converte primeiro número encontrado
                    num_str = numbers[0].replace(',', '')
                    return float(num_str)
                except ValueError:
                    pass
        
        return value
    
    def _convert_cnae_to_number(self, cnae: Union[str, float]) -> Union[str, float]:
        """Converte CNAE para número quando possível"""
        if isinstance(cnae, (int, float)):
            return cnae
        
        if isinstance(cnae, str):
            # Extrai apenas números do CNAE
            numbers = re.findall(r'\d+', cnae)
            if numbers:
                try:
                    return int(''.join(numbers))
                except ValueError:
                    pass
        
        return cnae
    
    def _calculate_field_completion(self, data: List[InvestmentNews]) -> Dict[str, float]:
        """Calcula taxa de preenchimento por campo"""
        if not data:
            return {}
        
        field_completion = {}
        total_records = len(data)
        
        for field_name in InvestmentNews.__dataclass_fields__:
            filled_count = 0
            for news in data:
                field_value = getattr(news, field_name, None)
                if field_value and str(field_value).strip() and str(field_value) != 'não identificado':
                    filled_count += 1
            
            field_completion[field_name] = filled_count / total_records
        
        return field_completion
    
    def _calculate_data_distribution(self, data: List[InvestmentNews]) -> Dict[str, Any]:
        """Calcula distribuição dos dados"""
        if not data:
            return {}
        
        # Distribuição por município
        municipios = {}
        for news in data:
            municipio = news.municipio
            municipios[municipio] = municipios.get(municipio, 0) + 1
        
        # Distribuição por tipo de investimento
        tipos_investimento = {}
        for news in data:
            tipo = news.tipo_investimento
            tipos_investimento[tipo] = tipos_investimento.get(tipo, 0) + 1
        
        return {
            'municipios': dict(sorted(municipios.items(), key=lambda x: x[1], reverse=True)[:10]),
            'tipos_investimento': dict(sorted(tipos_investimento.items(), key=lambda x: x[1], reverse=True))
        }


# Instância global do processador
data_processor = DataProcessor()