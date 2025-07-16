"""
Ferramentas validadas que usam o sistema de validação
"""

from crewai.tools import BaseTool
from crewai_tools import ScrapeWebsiteTool
from tools.serp_tool import GoogleSearchTool, GoogleSearchToolSchema
from utils.tool_validator import tool_validator
from utils.query_expander import query_expander
from utils.location_validator import LocationValidator
from typing import Dict, Any, List, Optional
from pydantic import Field
import logging
import time


class ValidatedGoogleSearchTool(BaseTool):
    """Google Search Tool com validação automática de parâmetros"""

    name: str = "Validated Google Search Tool"
    description: str = (
        "Busca na internet por notícias sobre um tópico específico, com validação automática "
        "de parâmetros para evitar erros de execução. Focado no estado de São Paulo."
    )

    # Definindo o schema dos argumentos da ferramenta
    args_schema: type = GoogleSearchToolSchema

    def __init__(self):
        super().__init__()

    def _run(self, query: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Executa busca com validação automática de parâmetros e expansão de consultas

        Args:
            query: Query de busca (pode ser passada como parâmetro posicional)
            **kwargs: Parâmetros adicionais da busca

        Returns:
            Lista de resultados da busca
        """
        # Cria instâncias das ferramentas localmente
        google_tool = GoogleSearchTool()
        logger = logging.getLogger(__name__)

        try:
            # Registra início do uso da ferramenta
            tool_start_time = time.time()

            # Se query foi passada como parâmetro posicional, adiciona aos kwargs
            if query is not None:
                kwargs["query"] = query
                logger.info(f"Query recebida como parâmetro posicional: '{query}'")

            # Log detalhado para debug
            logger.info(f"Parâmetros recebidos na ValidatedGoogleSearchTool: {kwargs}")

            # Verifica se não há parâmetros e adiciona contexto útil
            if not kwargs and query is None:
                logger.warning(
                    "Ferramenta chamada sem parâmetros. Isso pode indicar um problema na configuração do agente."
                )
                logger.info(
                    "Sugestão: Verifique se o agente está passando a query corretamente para a ferramenta."
                )

            # Valida parâmetros antes de executar
            validated_params = tool_validator.validate_google_search_params(kwargs)

            # Se não há tentativas_query definidas, gera automaticamente
            if not validated_params.get("tentativas_query"):
                alternative_queries = query_expander.generate_alternative_queries(
                    validated_params["query"]
                )
                if alternative_queries:
                    validated_params["tentativas_query"] = alternative_queries
                    logger.info(
                        f"Consultas alternativas geradas: {alternative_queries}"
                    )

            # Executa busca com parâmetros validados e expandidos
            results = google_tool._run(**validated_params)

            # Se poucos resultados, tenta com mais consultas alternativas
            if len(results) < validated_params.get("quantidade", 5) // 2:
                logger.info("Poucos resultados encontrados, expandindo consultas...")
                additional_queries = query_expander.generate_alternative_queries(
                    validated_params["query"]
                )

                # Adiciona novas consultas se não estavam nas originais
                current_queries = validated_params.get("tentativas_query", [])
                new_queries = [
                    q for q in additional_queries if q not in current_queries
                ]

                if new_queries:
                    validated_params["tentativas_query"] = (
                        current_queries + new_queries[:2]
                    )
                    additional_results = google_tool._run(**validated_params)

                    # Combina resultados evitando duplicatas por URL
                    seen_urls = {r.get("link") for r in results if r.get("link")}
                    for result in additional_results:
                        if result.get("link") and result["link"] not in seen_urls:
                            results.append(result)
                            seen_urls.add(result["link"])

            # Registra uso da ferramenta no monitor
            execution_time = time.time() - tool_start_time
            success = len(results) > 0 and not any(
                "error" in r for r in results if isinstance(r, dict)
            )

            # Importa o monitor aqui para evitar import circular
            try:
                from utils.system_monitor import system_monitor

                system_monitor.log_tool_usage(
                    tool_name="Google Search Tool",
                    success=success,
                    execution_time=execution_time,
                    params=validated_params,
                )
            except ImportError:
                pass  # Continua sem monitoramento se houver problema

            logger.info(f"Busca executada com sucesso: {len(results)} resultados")
            return results

        except Exception as e:
            error_msg = f"Erro na busca validada: {str(e)}"
            logger.error(error_msg)
            tool_validator.log_validation_error(
                error_msg,
                {"original_params": kwargs, "tool": "ValidatedGoogleSearchTool"},
            )
            return [{"error": error_msg}]


class ValidatedScrapeWebsiteTool(BaseTool):
    """Scrape Website Tool com validação automática de parâmetros"""

    name: str = "Validated Scrape Website Tool"
    description: str = (
        "Extrai conteúdo de websites com validação automática de URLs "
        "para evitar erros de execução."
    )

    def __init__(self):
        super().__init__()

    def _run(self, website_url: str) -> str:
        """
        Executa scraping com validação automática de URL e extração de localização

        Args:
            website_url: URL do website para extrair conteúdo

        Returns:
            Conteúdo extraído do website com informações de localização validadas
        """
        # Cria instâncias das ferramentas localmente
        scrape_tool = ScrapeWebsiteTool()
        logger = logging.getLogger(__name__)

        try:
            # Registra início do uso da ferramenta
            tool_start_time = time.time()

            # Valida parâmetros antes de executar
            validated_params = tool_validator.validate_scrape_params(
                {"website_url": website_url}
            )

            # Executa scraping com parâmetros validados
            content = scrape_tool._run(**validated_params)

            # Cria instância do validador de localização
            location_validator = LocationValidator()
            
            # Extrai e valida localização do conteúdo
            extracted_location = location_validator.extract_location_from_text(content)

            if extracted_location:
                if location_validator.validate_municipality(extracted_location):
                    logger.info(f"Localização válida encontrada: {extracted_location}")
                    # Adiciona informação de localização validada ao conteúdo
                    location_info = f"\n\n[LOCALIZAÇÃO VALIDADA: {extracted_location} - Município de São Paulo confirmado]"
                    content += location_info
                else:
                    # Tenta resolver ambiguidade
                    resolved_location = location_validator.resolve_ambiguous_location(
                        extracted_location, website_url
                    )
                    if resolved_location:
                        logger.info(
                            f"Localização resolvida: {extracted_location} -> {resolved_location}"
                        )
                        location_info = f"\n\n[LOCALIZAÇÃO RESOLVIDA: {resolved_location} - Município de São Paulo confirmado]"
                        content += location_info
                    else:
                        logger.warning(
                            f"Localização inválida descartada: {extracted_location}"
                        )
                        location_info = f"\n\n[LOCALIZAÇÃO INVÁLIDA: {extracted_location} - Não é município de São Paulo]"
                        content += location_info
            else:
                logger.warning("Nenhuma localização encontrada no conteúdo")
                content += "\n\n[LOCALIZAÇÃO: Não identificada no conteúdo]"

            # Registra uso da ferramenta no monitor
            execution_time = time.time() - tool_start_time
            success = (
                len(content.strip()) > 0 and "Erro ao extrair conteúdo" not in content
            )

            # Importa o monitor aqui para evitar import circular
            try:
                from utils.system_monitor import system_monitor

                system_monitor.log_tool_usage(
                    tool_name="Scrape Website Tool",
                    success=success,
                    execution_time=execution_time,
                    params=validated_params,
                )
            except ImportError:
                pass  # Continua sem monitoramento se houver problema

            logger.info(f"Scraping executado com sucesso para: {website_url}")
            return content

        except Exception as e:
            error_msg = f"Erro no scraping validado: {str(e)}"
            logger.error(error_msg)
            tool_validator.log_validation_error(
                error_msg,
                {"website_url": website_url, "tool": "ValidatedScrapeWebsiteTool"},
            )
            return f"Erro ao extrair conteúdo: {error_msg}"


# Instâncias das ferramentas validadas
validated_google_tool = ValidatedGoogleSearchTool()
validated_scrape_tool = ValidatedScrapeWebsiteTool()
