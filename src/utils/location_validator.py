"""
Validador Geográfico Aprimorado para o Sistema PIESP
Valida localizações contra lista oficial de municípios de São Paulo
"""

import re
import logging
from typing import Set, Optional, List
from pathlib import Path
import unicodedata
from crewai_tools import ScrapeWebsiteTool

class LocationValidator:
    """
    Classe responsável por validar localizações geográficas contra
    a lista oficial de municípios do estado de São Paulo
    """
    
    def __init__(self, municipalities_file: str = "knowledge/municipios_sp.txt"):
        """
        Inicializa o validador com a lista de municípios
        
        Args:
            municipalities_file: Caminho para arquivo com lista de municípios
        """
        self.municipalities_file = municipalities_file
        self.logger = logging.getLogger(__name__)
        self.scraper = ScrapeWebsiteTool()
        self.sp_municipalities = self.load_sp_municipalities()
        
        # Padrões regex para extração de localização
        self.location_patterns = [
            r'(?:em|na cidade de|no município de|em)\s+([A-ZÁÊÇÕ][a-záêçõ\s\-\']+)(?:\s*[-,]?\s*SP|São Paulo)',
            r'([A-ZÁÊÇÕ][a-záêçõ\s\-\']+)(?:\s*[-,]?\s*SP|São Paulo)',
            r'município de\s+([A-ZÁÊÇÕ][a-záêçõ\s\-\']+)',
            r'cidade de\s+([A-ZÁÊÇÕ][a-záêçõ\s\-\']+)',
        ]
    
    def load_sp_municipalities(self) -> Set[str]:
        """
        Carrega a lista de municípios de São Paulo do arquivo
        
        Returns:
            Set com nomes dos municípios normalizados
        """
        municipalities = set()
        
        try:
            file_path = Path(self.municipalities_file)
            if not file_path.exists():
                self.logger.error(f"Arquivo de municípios não encontrado: {self.municipalities_file}")
                return municipalities
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrair municípios das linhas que começam com "-"
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    municipality = line[2:].strip()
                    if municipality:
                        # Normalizar nome do município
                        normalized = self._normalize_text(municipality)
                        municipalities.add(normalized)
                        # Adicionar também versão original
                        municipalities.add(municipality)
                        
            self.logger.info(f"Carregados {len(municipalities)} municípios de São Paulo")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar municípios: {str(e)}")
            
        return municipalities
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto removendo acentos e convertendo para minúsculas
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
            
        # Remover acentos
        normalized = unicodedata.normalize('NFD', text)
        normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        
        # Converter para minúsculas e remover espaços extras
        normalized = normalized.lower().strip()
        
        return normalized
    
    def validate_municipality(self, location: str) -> bool:
        """
        Valida se uma localização é um município válido de SP
        
        Args:
            location: Nome da localização a ser validada
            
        Returns:
            True se for um município válido de SP, False caso contrário
        """
        if not location:
            return False
            
        location_clean = location.strip()
        location_normalized = self._normalize_text(location_clean)
        
        # Verificar correspondência exata
        if location_clean in self.sp_municipalities:
            return True
            
        if location_normalized in {self._normalize_text(m) for m in self.sp_municipalities}:
            return True
            
        # Verificar correspondência parcial (para casos como "São Paulo - SP")
        for municipality in self.sp_municipalities:
            if self._normalize_text(municipality) in location_normalized:
                return True
            if location_normalized in self._normalize_text(municipality):
                return True
                
        return False
    
    def extract_location_from_text(self, text: str) -> Optional[str]:
        """
        Extrai localização de um texto usando regex
        
        Args:
            text: Texto para extrair localização
            
        Returns:
            Nome da localização extraída ou None se não encontrada
        """
        if not text:
            return None
            
        # Tentar cada padrão regex
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                
                # Limpar localização extraída
                location = re.sub(r'\s+', ' ', location)  # Normalizar espaços
                location = location.title()  # Capitalizar
                
                # Validar se é município de SP
                if self.validate_municipality(location):
                    self.logger.debug(f"Localização extraída e validada: {location}")
                    return location
                    
        # Tentar busca mais ampla por nomes de municípios no texto
        text_normalized = self._normalize_text(text)
        for municipality in self.sp_municipalities:
            municipality_normalized = self._normalize_text(municipality)
            if municipality_normalized in text_normalized:
                self.logger.debug(f"Município encontrado no texto: {municipality}")
                return municipality
                
        return None
    
    def resolve_ambiguous_location(self, location: str, url: str) -> Optional[str]:
        """
        Resolve ambiguidades de localização usando scraping adicional
        
        Args:
            location: Localização ambígua
            url: URL da notícia para scraping adicional
            
        Returns:
            Localização resolvida ou None se não conseguir resolver
        """
        if not location or not url:
            return None
            
        try:
            # Fazer scraping da página para obter mais contexto
            scraped_content = self.scraper.run(url)
            
            if scraped_content and isinstance(scraped_content, str):
                # Buscar por padrões mais específicos no conteúdo completo
                enhanced_patterns = [
                    rf'{re.escape(location)}\s*[-,]?\s*(SP|São Paulo)',
                    rf'município de\s+{re.escape(location)}\s*[-,]?\s*(SP|São Paulo)',
                    rf'{re.escape(location)}\s*[-,]?\s*estado de São Paulo',
                ]
                
                for pattern in enhanced_patterns:
                    if re.search(pattern, scraped_content, re.IGNORECASE):
                        if self.validate_municipality(location):
                            self.logger.info(f"Ambiguidade resolvida via scraping: {location}")
                            return location
                            
                # Tentar extrair localização do conteúdo completo
                extracted = self.extract_location_from_text(scraped_content)
                if extracted:
                    self.logger.info(f"Nova localização extraída via scraping: {extracted}")
                    return extracted
                    
        except Exception as e:
            self.logger.warning(f"Erro ao resolver ambiguidade via scraping: {str(e)}")
            
        return None
    
    def get_validation_stats(self) -> dict:
        """
        Retorna estatísticas do validador
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_municipalities": len(self.sp_municipalities),
            "patterns_count": len(self.location_patterns),
            "municipalities_file": self.municipalities_file
        }
    
    def find_similar_municipalities(self, location: str, max_results: int = 5) -> List[str]:
        """
        Encontra municípios similares para sugestões
        
        Args:
            location: Localização para buscar similares
            max_results: Número máximo de resultados
            
        Returns:
            Lista de municípios similares
        """
        if not location:
            return []
            
        location_normalized = self._normalize_text(location)
        similar = []
        
        for municipality in self.sp_municipalities:
            municipality_normalized = self._normalize_text(municipality)
            
            # Verificar se contém a string buscada
            if location_normalized in municipality_normalized:
                similar.append(municipality)
                
            # Verificar se começa com a string buscada
            elif municipality_normalized.startswith(location_normalized):
                similar.append(municipality)
                
            if len(similar) >= max_results:
                break
                
        return similar[:max_results]