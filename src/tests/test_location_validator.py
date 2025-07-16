"""
Testes unitários para o LocationValidator
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.location_validator import LocationValidator

class TestLocationValidator(unittest.TestCase):
    """Testes para a classe LocationValidator"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Mock do arquivo de municípios para testes
        self.test_municipalities = {
            'São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto',
            'São José dos Campos', 'Sorocaba', 'Osasco', 'Guarulhos'
        }
        
        with patch.object(LocationValidator, 'load_sp_municipalities') as mock_load:
            mock_load.return_value = self.test_municipalities
            self.validator = LocationValidator()
    
    def test_validate_municipality_valid(self):
        """Testa validação de municípios válidos"""
        valid_municipalities = ['São Paulo', 'Campinas', 'Santos']
        
        for municipality in valid_municipalities:
            with self.subTest(municipality=municipality):
                self.assertTrue(self.validator.validate_municipality(municipality))
    
    def test_validate_municipality_invalid(self):
        """Testa validação de municípios inválidos"""
        invalid_municipalities = ['Rio de Janeiro', 'Belo Horizonte', 'Curitiba']
        
        for municipality in invalid_municipalities:
            with self.subTest(municipality=municipality):
                self.assertFalse(self.validator.validate_municipality(municipality))
    
    def test_validate_municipality_empty(self):
        """Testa validação com entrada vazia"""
        self.assertFalse(self.validator.validate_municipality(""))
        self.assertFalse(self.validator.validate_municipality(None))
    
    def test_normalize_text(self):
        """Testa normalização de texto"""
        test_cases = [
            ("São Paulo", "sao paulo"),
            ("Ribeirão Preto", "ribeirao preto"),
            ("CAMPINAS", "campinas"),
            ("  Santos  ", "santos")
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.validator._normalize_text(original)
                self.assertEqual(result, expected)
    
    def test_extract_location_from_text_success(self):
        """Testa extração bem-sucedida de localização"""
        test_texts = [
            "Investimento anunciado em São Paulo",
            "Nova fábrica na cidade de Campinas",
            "Projeto no município de Santos",
            "Empresa em Ribeirão Preto - SP"
        ]
        
        expected_locations = ['São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto']
        
        for text, expected in zip(test_texts, expected_locations):
            with self.subTest(text=text):
                result = self.validator.extract_location_from_text(text)
                self.assertEqual(result, expected)
    
    def test_extract_location_from_text_not_found(self):
        """Testa extração quando localização não é encontrada"""
        test_texts = [
            "Investimento anunciado no Rio de Janeiro",
            "Nova fábrica em Belo Horizonte",
            "Projeto sem localização específica"
        ]
        
        for text in test_texts:
            with self.subTest(text=text):
                result = self.validator.extract_location_from_text(text)
                self.assertIsNone(result)
    
    def test_extract_location_from_text_empty(self):
        """Testa extração com texto vazio"""
        self.assertIsNone(self.validator.extract_location_from_text(""))
        self.assertIsNone(self.validator.extract_location_from_text(None))
    
    def test_resolve_ambiguous_location_success(self):
        """Testa resolução bem-sucedida de ambiguidade"""
        # Teste sem scraping real - apenas validação básica
        result = self.validator.resolve_ambiguous_location("São Paulo", "")
        # Se não conseguir fazer scraping, deve retornar None
        self.assertIsNone(result)
    
    @patch('crewai_tools.ScrapeWebsiteTool')
    def test_resolve_ambiguous_location_failure(self, mock_scraper_class):
        """Testa falha na resolução de ambiguidade"""
        # Mock do scraper que falha
        mock_scraper = MagicMock()
        mock_scraper.run.side_effect = Exception("Scraping failed")
        mock_scraper_class.return_value = mock_scraper
        
        # Recriar validator com mock
        with patch.object(LocationValidator, 'load_sp_municipalities') as mock_load:
            mock_load.return_value = self.test_municipalities
            validator = LocationValidator()
        
        result = validator.resolve_ambiguous_location("Ambígua", "http://example.com")
        self.assertIsNone(result)
    
    def test_get_validation_stats(self):
        """Testa obtenção de estatísticas"""
        stats = self.validator.get_validation_stats()
        
        self.assertIn('total_municipalities', stats)
        self.assertIn('patterns_count', stats)
        self.assertIn('municipalities_file', stats)
        self.assertEqual(stats['total_municipalities'], len(self.test_municipalities))
    
    def test_find_similar_municipalities(self):
        """Testa busca por municípios similares"""
        # Teste com busca que deve retornar resultados
        similar = self.validator.find_similar_municipalities("São", max_results=3)
        self.assertIn("São Paulo", similar)
        self.assertIn("São José dos Campos", similar)
        
        # Teste com busca que não deve retornar resultados
        similar = self.validator.find_similar_municipalities("Rio", max_results=3)
        self.assertEqual(len(similar), 0)
        
        # Teste com entrada vazia
        similar = self.validator.find_similar_municipalities("", max_results=3)
        self.assertEqual(len(similar), 0)

if __name__ == '__main__':
    unittest.main()