"""
Verificador de notícias inventadas/falsas para o sistema CrewAI
Analisa a veracidade e credibilidade das notícias coletadas
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """Resultado da verificação de uma notícia"""

    is_credible: bool
    credibility_score: float  # 0.0 a 1.0
    warning_flags: List[str]
    verification_details: Dict[str, Any]
    recommendation: str


class NewsVerifier:
    """Verificador de credibilidade de notícias"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_verification_rules()
        self._setup_credible_sources()
        self._setup_suspicious_patterns()

    def _setup_verification_rules(self):
        """Define regras de verificação de credibilidade"""
        self.verification_rules = {
            "source_credibility": 0.3,  # 30% do score
            "content_quality": 0.25,  # 25% do score
            "date_consistency": 0.15,  # 15% do score
            "factual_coherence": 0.15,  # 15% do score
            "technical_details": 0.15,  # 15% do score
        }

        # Thresholds para classificação
        self.credibility_thresholds = {
            "high": 0.8,  # Altamente confiável
            "medium": 0.6,  # Moderadamente confiável
            "low": 0.4,  # Baixa confiabilidade
            "very_low": 0.2,  # Muito baixa confiabilidade
        }

    def _setup_credible_sources(self):
        """Define fontes conhecidamente confiáveis"""
        self.credible_sources = {
            # Fontes de alta credibilidade (score 1.0)
            "tier_1": [
                "estadao.com.br",
                "valor.com.br",
                "folha.uol.com.br",
                "globo.com",
                "uol.com.br",
                "bndes.gov.br",
                "gov.br",
                "seade.gov.br",
                "fiesp.com.br",
            ],
            # Fontes de boa credibilidade (score 0.8)
            "tier_2": [
                "dci.com.br",
                "correiopopular.com.br",
                "dgabc.com.br",
                "jornaldecampinas.com.br",
                "diariodaregiao.com.br",
                "atribuna.com.br",
                "jornaldepiracicaba.com.br",
            ],
            # Fontes de credibilidade moderada (score 0.6)
            "tier_3": [
                "diariodesorocaba.com.br",
                "jornalcruzeiro.com.br",
                "odiariodemogi.com.br",
                "ribeiraopretoonline.com.br",
                "saocarlosemrede.com.br",
                "webdiario.com.br",
            ],
        }

    def _setup_suspicious_patterns(self):
        """Define padrões suspeitos que indicam possível notícia falsa"""
        self.suspicious_patterns = {
            # Padrões no título
            "clickbait_titles": [
                r"URGENTE[!]*",
                r"BREAKING[!]*",
                r"EXCLUSIVO[!]*",
                r"BOMBA[!]*",
                r"CHOCANTE[!]*",
                r"NÃO VAI ACREDITAR",
                r"VOCÊ PRECISA VER",
            ],
            # Padrões no conteúdo
            "suspicious_content": [
                r"fonte não revelada",
                r"segundo rumores",
                r"informações extraoficiais",
                r"bastidores revelam",
                r"fonte próxima ao governo",
                r"não confirmado oficialmente",
            ],
            # Padrões de valores irreais
            "unrealistic_values": [
                r"trilhões de reais",
                r"bilhões de dólares.*pequena empresa",
                r"investimento de.*100% de lucro",
                r"retorno garantido de.*%",
            ],
            # Padrões temporais suspeitos
            "temporal_inconsistencies": [
                r"ontem.*próximo ano",
                r"semana passada.*2030",
                r"mês que vem.*já inaugurado",
            ],
        }

    def verify_news(self, news_data: Dict[str, Any]) -> VerificationResult:
        """
        Verifica a credibilidade de uma notícia

        Args:
            news_data: Dicionário com dados da notícia

        Returns:
            Resultado da verificação com score e detalhes
        """
        verification_details = {}
        warning_flags = []

        # 1. Verifica credibilidade da fonte
        source_score = self._verify_source_credibility(
            news_data.get("link", ""), news_data.get("fonte_noticia", "")
        )
        verification_details["source_score"] = source_score

        # 2. Verifica qualidade do conteúdo
        content_score = self._verify_content_quality(
            news_data.get("titulo", ""), news_data.get("descricao_detalhada", "")
        )
        verification_details["content_score"] = content_score

        # 3. Verifica consistência de data
        date_score = self._verify_date_consistency(news_data.get("data", ""))
        verification_details["date_score"] = date_score

        # 4. Verifica coerência factual
        factual_score = self._verify_factual_coherence(news_data)
        verification_details["factual_score"] = factual_score

        # 5. Verifica detalhes técnicos
        technical_score = self._verify_technical_details(news_data)
        verification_details["technical_score"] = technical_score

        # Calcula score final ponderado
        final_score = (
            source_score * self.verification_rules["source_credibility"]
            + content_score * self.verification_rules["content_quality"]
            + date_score * self.verification_rules["date_consistency"]
            + factual_score * self.verification_rules["factual_coherence"]
            + technical_score * self.verification_rules["technical_details"]
        )

        # Identifica flags de aviso
        warning_flags = self._identify_warning_flags(news_data, verification_details)

        # Determina credibilidade e recomendação
        is_credible = final_score >= self.credibility_thresholds["medium"]
        recommendation = self._generate_recommendation(final_score, warning_flags)

        self.logger.info(
            f"Notícia verificada: score {final_score:.2f}, credível: {is_credible}"
        )

        return VerificationResult(
            is_credible=is_credible,
            credibility_score=final_score,
            warning_flags=warning_flags,
            verification_details=verification_details,
            recommendation=recommendation,
        )

    def _verify_source_credibility(self, url: str, source_name: str) -> float:
        """Verifica credibilidade da fonte"""
        if not url:
            return 0.3

        domain = urlparse(url).netloc.lower()

        # Remove www. se presente
        domain = domain.replace("www.", "")

        # Verifica tiers de credibilidade
        for tier, sources in self.credible_sources.items():
            for source in sources:
                if source in domain:
                    if tier == "tier_1":
                        return 1.0
                    elif tier == "tier_2":
                        return 0.8
                    elif tier == "tier_3":
                        return 0.6

        # Verifica padrões suspeitos no domínio
        suspicious_domains = [
            "blogspot",
            "wordpress",
            "wix",
            "weebly",
            "fake",
            "news",
            "click",
            "viral",
        ]

        for suspicious in suspicious_domains:
            if suspicious in domain:
                return 0.2

        # Fonte desconhecida mas não suspeita
        return 0.5

    def _verify_content_quality(self, title: str, description: str) -> float:
        """Verifica qualidade do conteúdo"""
        score = 1.0

        # Verifica padrões clickbait no título
        for pattern in self.suspicious_patterns["clickbait_titles"]:
            if re.search(pattern, title.upper()):
                score -= 0.3
                break

        # Verifica padrões suspeitos no conteúdo
        full_text = f"{title} {description}".lower()

        for pattern in self.suspicious_patterns["suspicious_content"]:
            if re.search(pattern, full_text):
                score -= 0.2

        # Verifica valores irreais
        for pattern in self.suspicious_patterns["unrealistic_values"]:
            if re.search(pattern, full_text):
                score -= 0.4

        # Verifica qualidade da escrita
        if len(description) < 50:
            score -= 0.2  # Descrição muito curta

        # Verifica excesso de maiúsculas (indicativo de sensacionalismo)
        if title and sum(1 for c in title if c.isupper()) / len(title) > 0.5:
            score -= 0.2

        return max(0.0, score)

    def _verify_date_consistency(self, date_str: str) -> float:
        """Verifica consistência da data"""
        if not date_str:
            return 0.5

        try:
            # Tenta parsear diferentes formatos de data
            date_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d de %B de %Y"]
            news_date = None

            for fmt in date_formats:
                try:
                    news_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            if not news_date:
                return 0.3  # Formato de data inválido

            current_date = datetime.now()

            # Verifica se a data está no futuro (suspeito)
            if news_date > current_date + timedelta(days=1):
                return 0.2

            # Verifica se a data é muito antiga para ser relevante
            if news_date < datetime(2024, 1, 1):
                return 0.4

            # Data dentro do período esperado (2025)
            if news_date.year == 2025:
                return 1.0

            return 0.7

        except Exception:
            return 0.3

    def _verify_factual_coherence(self, news_data: Dict[str, Any]) -> float:
        """Verifica coerência factual da notícia"""
        score = 1.0

        # Verifica se município é válido
        municipio = news_data.get("municipio", "")
        if not municipio or municipio.lower() in ["não identificado", "desconhecido"]:
            score -= 0.3

        # Verifica se tipo de investimento é específico
        tipo_investimento = news_data.get("tipo_investimento", "")
        if not tipo_investimento or tipo_investimento.lower() in [
            "não especificado",
            "geral",
        ]:
            score -= 0.2

        # Verifica se há valor estimado
        valor_estimado = news_data.get("valor_estimado")
        if not valor_estimado or str(valor_estimado).lower() in ["não informado", "0"]:
            score -= 0.1

        # Verifica coerência entre título e descrição
        titulo = news_data.get("titulo", "").lower()
        descricao = news_data.get("descricao_detalhada", "").lower()

        # Palavras-chave que devem aparecer em ambos
        investment_keywords = [
            "investimento",
            "expansão",
            "construção",
            "inauguração",
            "instalação",
        ]

        title_has_keywords = any(keyword in titulo for keyword in investment_keywords)
        desc_has_keywords = any(keyword in descricao for keyword in investment_keywords)

        if not (title_has_keywords and desc_has_keywords):
            score -= 0.2

        return max(0.0, score)

    def _verify_technical_details(self, news_data: Dict[str, Any]) -> float:
        """Verifica detalhes técnicos da notícia"""
        score = 1.0

        # Verifica se há detalhes técnicos suficientes
        required_fields = [
            "categoria",
            "tipo_investimento",
            "municipio",
            "fonte_noticia",
        ]
        missing_fields = 0

        for field in required_fields:
            if not news_data.get(field) or str(news_data.get(field)).strip() == "":
                missing_fields += 1

        # Penaliza por campos ausentes
        score -= (missing_fields / len(required_fields)) * 0.5

        # Verifica se há informações específicas sobre o setor
        if (
            news_data.get("piesp_setor")
            and news_data["piesp_setor"] != "não classificado"
        ):
            score += 0.1

        # Verifica se há código CNAE
        if (
            news_data.get("cnae_investimento")
            and str(news_data["cnae_investimento"]) != "não informado"
        ):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _identify_warning_flags(
        self, news_data: Dict[str, Any], verification_details: Dict[str, Any]
    ) -> List[str]:
        """Identifica flags de aviso baseados na verificação"""
        flags = []

        # Flags baseados em scores baixos
        if verification_details["source_score"] < 0.5:
            flags.append("FONTE_SUSPEITA")

        if verification_details["content_score"] < 0.5:
            flags.append("CONTEUDO_SUSPEITO")

        if verification_details["date_score"] < 0.5:
            flags.append("DATA_INCONSISTENTE")

        if verification_details["factual_score"] < 0.5:
            flags.append("FATOS_INCOERENTES")

        # Flags específicos
        titulo = news_data.get("titulo", "").upper()
        if any(pattern in titulo for pattern in ["URGENTE", "BREAKING", "BOMBA"]):
            flags.append("CLICKBAIT")

        if (
            not news_data.get("valor_estimado")
            or str(news_data.get("valor_estimado")) == "não informado"
        ):
            flags.append("SEM_VALOR_INVESTIMENTO")

        if (
            not news_data.get("municipio")
            or news_data.get("municipio") == "não identificado"
        ):
            flags.append("LOCALIZACAO_VAGA")

        return flags

    def _generate_recommendation(self, score: float, warning_flags: List[str]) -> str:
        """Gera recomendação baseada no score e flags"""
        if score >= self.credibility_thresholds["high"]:
            return "ACEITAR - Notícia altamente confiável"
        elif score >= self.credibility_thresholds["medium"]:
            if len(warning_flags) <= 1:
                return (
                    "ACEITAR_COM_RESSALVAS - Notícia confiável com pequenas ressalvas"
                )
            else:
                return "REVISAR - Notícia confiável mas com múltiplos alertas"
        elif score >= self.credibility_thresholds["low"]:
            return "REVISAR_CUIDADOSAMENTE - Credibilidade questionável"
        else:
            return "REJEITAR - Credibilidade muito baixa, possível notícia falsa"

    def batch_verify_news(
        self, news_list: List[Dict[str, Any]]
    ) -> List[VerificationResult]:
        """
        Verifica um lote de notícias

        Args:
            news_list: Lista de notícias para verificar

        Returns:
            Lista de resultados de verificação
        """
        results = []

        for i, news in enumerate(news_list):
            try:
                result = self.verify_news(news)
                results.append(result)

                self.logger.info(
                    f"Notícia {i+1}/{len(news_list)} verificada: {result.recommendation}"
                )

            except Exception as e:
                self.logger.error(f"Erro verificando notícia {i+1}: {str(e)}")
                # Cria resultado de erro
                error_result = VerificationResult(
                    is_credible=False,
                    credibility_score=0.0,
                    warning_flags=["ERRO_VERIFICACAO"],
                    verification_details={"error": str(e)},
                    recommendation="ERRO - Falha na verificação",
                )
                results.append(error_result)

        return results

    def generate_verification_report(
        self, results: List[VerificationResult]
    ) -> Dict[str, Any]:
        """
        Gera relatório de verificação

        Args:
            results: Lista de resultados de verificação

        Returns:
            Relatório com estatísticas de verificação
        """
        if not results:
            return {"error": "Nenhum resultado de verificação"}

        total_news = len(results)
        credible_news = len([r for r in results if r.is_credible])
        avg_score = sum(r.credibility_score for r in results) / total_news

        # Conta flags mais comuns
        all_flags = []
        for result in results:
            all_flags.extend(result.warning_flags)

        flag_counts = {}
        for flag in all_flags:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

        # Distribui por recomendação
        recommendations = {}
        for result in results:
            rec = result.recommendation.split(" - ")[0]  # Pega só a primeira parte
            recommendations[rec] = recommendations.get(rec, 0) + 1

        report = {
            "verification_summary": {
                "total_news_verified": total_news,
                "credible_news": credible_news,
                "credibility_rate": credible_news / total_news,
                "average_credibility_score": avg_score,
                "verification_timestamp": datetime.now().isoformat(),
            },
            "quality_distribution": {
                "high_quality": len([r for r in results if r.credibility_score >= 0.8]),
                "medium_quality": len(
                    [r for r in results if 0.6 <= r.credibility_score < 0.8]
                ),
                "low_quality": len(
                    [r for r in results if 0.4 <= r.credibility_score < 0.6]
                ),
                "very_low_quality": len(
                    [r for r in results if r.credibility_score < 0.4]
                ),
            },
            "common_warning_flags": dict(
                sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "recommendations_distribution": recommendations,
            "detailed_results": [
                {
                    "credibility_score": r.credibility_score,
                    "is_credible": r.is_credible,
                    "warning_flags": r.warning_flags,
                    "recommendation": r.recommendation,
                }
                for r in results
            ],
        }

        return report


# Instância global do verificador
news_verifier = NewsVerifier()
