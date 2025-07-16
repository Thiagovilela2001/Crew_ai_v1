"""
Expansor automático de consultas para melhorar resultados de busca
Gera consultas alternativas baseadas em setores e termos relacionados
"""

from typing import List, Dict, Set
import logging
import random

class QueryExpander:
    """Expansor de consultas para busca de investimentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_sector_terms()
        self._setup_investment_terms()
        self._setup_location_terms()
    
    def _setup_sector_terms(self):
        """Define termos específicos por setor econômico"""
        self.sector_terms = {
            'industria': [
                'fábrica', 'indústria', 'manufatura', 'produção', 'planta industrial',
                'linha de produção', 'automação', 'metalúrgica', 'química', 'têxtil',
                'alimentícia', 'farmacêutica', 'automotiva', 'siderúrgica'
            ],
            'servicos': [
                'centro de distribuição', 'logística', 'armazém', 'hub', 'escritório',
                'call center', 'data center', 'tecnologia', 'software', 'consultoria',
                'financeiro', 'banco', 'seguradora', 'hospital', 'clínica'
            ],
            'agronegocio': [
                'agronegócio', 'agricultura', 'pecuária', 'frigorífico', 'usina',
                'processamento', 'grãos', 'açúcar', 'etanol', 'fertilizante',
                'defensivo', 'sementes', 'cooperativa', 'rural'
            ],
            'infraestrutura': [
                'rodovia', 'ferrovia', 'porto', 'aeroporto', 'energia', 'elétrica',
                'transmissão', 'distribuição', 'saneamento', 'água', 'esgoto',
                'telecomunicações', 'fibra ótica', 'antena', '5G'
            ],
            'comercio': [
                'shopping', 'varejo', 'loja', 'supermercado', 'hipermercado',
                'atacado', 'distribuidor', 'franquia', 'e-commerce', 'marketplace'
            ]
        }
    
    def _setup_investment_terms(self):
        """Define termos relacionados a investimentos"""
        self.investment_terms = {
            'acao': [
                'investimento', 'expansão', 'ampliação', 'construção', 'instalação',
                'inauguração', 'abertura', 'modernização', 'reforma', 'upgrade',
                'implantação', 'implementação', 'desenvolvimento', 'criação'
            ],
            'valor': [
                'milhões', 'bilhões', 'R$', 'reais', 'dólares', 'investir',
                'aportar', 'aplicar', 'destinar', 'orçamento', 'capital'
            ],
            'impacto': [
                'empregos', 'vagas', 'trabalhadores', 'funcionários', 'contratação',
                'capacidade', 'produção', 'volume', 'crescimento', 'desenvolvimento'
            ]
        }
    
    def _setup_location_terms(self):
        """Define termos geográficos para São Paulo"""
        self.location_terms = {
            'estado': ['São Paulo', 'SP', 'estado de São Paulo', 'paulista'],
            'regioes': [
                'Grande São Paulo', 'RMSP', 'interior paulista', 'Vale do Paraíba',
                'Campinas', 'Sorocaba', 'Ribeirão Preto', 'São José dos Campos',
                'Santos', 'ABC paulista', 'região metropolitana'
            ],
            'qualificadores': [
                'município de', 'cidade de', 'região de', 'polo de', 'hub de'
            ]
        }
    
    def generate_alternative_queries(self, original_query: str) -> List[str]:
        """
        Gera consultas alternativas baseadas na consulta original
        
        Args:
            original_query: Consulta original
            
        Returns:
            Lista de consultas alternativas
        """
        alternatives = []
        
        # Detecta setor provável da consulta
        detected_sector = self._detect_sector(original_query)
        
        # Gera variações por setor
        if detected_sector:
            sector_alternatives = self.get_sector_specific_terms(detected_sector)
            for term in sector_alternatives[:3]:  # Máximo 3 termos por setor
                alt_query = self._replace_sector_terms(original_query, term)
                if alt_query != original_query:
                    alternatives.append(alt_query)
        
        # Gera variações com termos de investimento
        investment_alternatives = self._generate_investment_variations(original_query)
        alternatives.extend(investment_alternatives[:2])
        
        # Gera variações geográficas
        location_alternatives = self.combine_location_terms(original_query)
        alternatives.extend(location_alternatives[:2])
        
        # Remove duplicatas e limita a 5 alternativas
        unique_alternatives = list(dict.fromkeys(alternatives))
        
        self.logger.info(f"Geradas {len(unique_alternatives)} consultas alternativas para: {original_query}")
        return unique_alternatives[:5]
    
    def get_sector_specific_terms(self, sector: str) -> List[str]:
        """
        Retorna termos específicos para um setor
        
        Args:
            sector: Nome do setor
            
        Returns:
            Lista de termos específicos do setor
        """
        sector_lower = sector.lower()
        if sector_lower in self.sector_terms:
            return self.sector_terms[sector_lower].copy()
        
        # Se não encontrar setor específico, retorna termos gerais
        all_terms = []
        for terms in self.sector_terms.values():
            all_terms.extend(terms)
        
        return random.sample(all_terms, min(5, len(all_terms)))
    
    def combine_location_terms(self, base_query: str) -> List[str]:
        """
        Combina consulta base com termos geográficos
        
        Args:
            base_query: Consulta base
            
        Returns:
            Lista de consultas com variações geográficas
        """
        location_variations = []
        
        # Adiciona qualificadores geográficos
        for qualifier in self.location_terms['qualificadores'][:2]:
            variation = f"{base_query} {qualifier}"
            location_variations.append(variation)
        
        # Adiciona regiões específicas
        for region in self.location_terms['regioes'][:2]:
            variation = f"{base_query} {region}"
            location_variations.append(variation)
        
        return location_variations
    
    def _detect_sector(self, query: str) -> str:
        """
        Detecta o setor provável baseado na consulta
        
        Args:
            query: Consulta para analisar
            
        Returns:
            Nome do setor detectado ou string vazia
        """
        query_lower = query.lower()
        
        sector_scores = {}
        for sector, terms in self.sector_terms.items():
            score = sum(1 for term in terms if term in query_lower)
            if score > 0:
                sector_scores[sector] = score
        
        if sector_scores:
            return max(sector_scores, key=sector_scores.get)
        
        return ''
    
    def _replace_sector_terms(self, query: str, new_term: str) -> str:
        """
        Substitui termos de setor na consulta
        
        Args:
            query: Consulta original
            new_term: Novo termo para incluir
            
        Returns:
            Consulta modificada
        """
        # Adiciona novo termo à consulta
        return f"{query} {new_term}"
    
    def _generate_investment_variations(self, query: str) -> List[str]:
        """
        Gera variações com termos de investimento
        
        Args:
            query: Consulta original
            
        Returns:
            Lista de variações com termos de investimento
        """
        variations = []
        
        # Adiciona termos de ação
        action_terms = random.sample(
            self.investment_terms['acao'], 
            min(2, len(self.investment_terms['acao']))
        )
        
        for term in action_terms:
            variation = f"{term} {query}"
            variations.append(variation)
        
        return variations


# Instância global do expansor
query_expander = QueryExpander()