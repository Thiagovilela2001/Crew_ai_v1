#!/usr/bin/env python
"""
Sistema CrewAI otimizado para coleta de investimentos em São Paulo
Versão aprimorada com monitoramento, validação e processamento robusto
"""

import sys
import os
import time
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path

# Imports do sistema otimizado
from crew import Teste
from utils.system_monitor import system_monitor, SystemMetrics
from utils.data_processor import data_processor
from utils.location_validator import LocationValidator


# Configuração de logging estruturado
def setup_logging():
    """Configura logging estruturado para toda a aplicação"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configuração do logger principal
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                log_dir / f"crewai_system_{datetime.now().strftime('%Y%m%d')}.log",
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado")
    return logger


# Inicializa AgentOps com segurança (caso esteja habilitado no .env)
def initialize_agentops():
    """Inicializa AgentOps se disponível"""
    try:
        import agentops

        AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
        if AGENTOPS_API_KEY:
            agentops.init(api_key=AGENTOPS_API_KEY)
            agentops.start_session()
            return True
    except ImportError:
        pass  # Segue normalmente se agentops não estiver instalado
    return False


def validate_environment():
    """Valida configuração do ambiente"""
    logger = logging.getLogger(__name__)

    required_env_vars = ["SERPER_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Variáveis de ambiente ausentes: {missing_vars}")
        return False

    # Verifica se arquivo de municípios existe
    if not Path("knowledge/municipios_sp.txt").exists():
        logger.error("Arquivo de municípios de SP não encontrado")
        return False

    logger.info("Ambiente validado com sucesso")
    return True


def run_single_iteration(
    iteration_number: int, logger: logging.Logger
) -> SystemMetrics:
    """
    Executa uma única iteração com monitoramento completo

    Args:
        iteration_number: Número da iteração
        logger: Logger para registrar eventos

    Returns:
        Métricas da iteração executada
    """
    # Inicia monitoramento da iteração
    system_monitor.log_iteration_start(iteration_number)
    iteration_start_time = time.time()

    logger.info(f"Iniciando iteração {iteration_number}")

    try:
        # Executa a crew
        crew_result = Teste().crew().kickoff()
        
        logger.info(f"Resultado da crew recebido: {type(crew_result)}")
        logger.info(f"Conteúdo do resultado: {str(crew_result)[:500]}...")

        # Processa resultados se disponíveis
        processed_data = []
        
        try:
            # Diferentes formas de extrair dados do resultado da crew
            raw_data = None
            
            # Tenta diferentes atributos do resultado
            if hasattr(crew_result, 'raw'):
                raw_data = crew_result.raw
                logger.info(f"Dados encontrados em crew_result.raw: {type(raw_data)}")
            elif hasattr(crew_result, 'output'):
                raw_data = crew_result.output
                logger.info(f"Dados encontrados em crew_result.output: {type(raw_data)}")
            elif hasattr(crew_result, 'result'):
                raw_data = crew_result.result
                logger.info(f"Dados encontrados em crew_result.result: {type(raw_data)}")
            else:
                # Se não tem atributos específicos, usa o próprio resultado
                raw_data = crew_result
                logger.info(f"Usando crew_result diretamente: {type(raw_data)}")
            
            # Tenta processar os dados
            if raw_data:
                logger.info(f"Tentando processar dados: {str(raw_data)[:200]}...")
                
                # Se é uma string, tenta converter para lista (pode ser JSON)
                if isinstance(raw_data, str):
                    try:
                        import json
                        parsed_data = json.loads(raw_data)
                        if isinstance(parsed_data, list):
                            raw_data = parsed_data
                            logger.info(f"JSON parseado com sucesso: {len(parsed_data)} itens")
                    except json.JSONDecodeError:
                        logger.warning("Resultado não é JSON válido")
                
                # Se é uma lista, processa diretamente
                if isinstance(raw_data, list):
                    processed_data = data_processor.process_news_batch(raw_data)
                    logger.info(f"Processados {len(processed_data)} registros")
                else:
                    logger.warning(f"Dados não estão em formato de lista: {type(raw_data)}")
                    
        except Exception as e:
            logger.error(f"Erro processando dados da crew: {str(e)}")
            logger.error(f"Detalhes do erro: {repr(e)}")

        # Calcula métricas da iteração
        execution_time = time.time() - iteration_start_time

        # Simula métricas (em implementação real, seria extraído dos resultados)
        total_found = len(processed_data) if processed_data else 0
        validated_count = (
            len([d for d in processed_data if d.qualidade_dados > 0.5])
            if processed_data
            else 0
        )

        # Calcula qualidade média dos dados
        avg_quality = 0.0
        if processed_data:
            avg_quality = sum(d.qualidade_dados for d in processed_data) / len(
                processed_data
            )
            system_monitor.log_data_quality_metrics(
                [
                    {
                        "titulo": d.titulo,
                        "municipio": d.municipio,
                        "qualidade": d.qualidade_dados,
                    }
                    for d in processed_data
                ]
            )

        # Cria métricas da iteração
        metrics = SystemMetrics(
            iteracao=iteration_number,
            timestamp=datetime.now().isoformat(),
            total_noticias_encontradas=total_found,
            noticias_validadas=validated_count,
            duplicatas_removidas=0,  # Será calculado pelo verificador de duplicatas
            municipios_invalidos=0,  # Será calculado pelo validador geográfico
            tempo_execucao=execution_time,
            taxa_sucesso_ferramentas=system_monitor.tool_calls_success
            / max(system_monitor.tool_calls_total, 1),
            consultas_alternativas_usadas=0,  # Será rastreado pelo expansor de consultas
            erros_validacao=system_monitor.validation_errors,
            qualidade_dados=avg_quality,
        )

        # Registra fim da iteração
        system_monitor.log_iteration_end(metrics)

        logger.info(f"Iteração {iteration_number} concluída em {execution_time:.1f}s")
        logger.info(f"Qualidade média dos dados: {avg_quality:.2%}")

        return metrics

    except Exception as e:
        logger.error(f"Erro na iteração {iteration_number}: {str(e)}")

        # Cria métricas de erro
        error_metrics = SystemMetrics(
            iteracao=iteration_number,
            timestamp=datetime.now().isoformat(),
            total_noticias_encontradas=0,
            noticias_validadas=0,
            duplicatas_removidas=0,
            municipios_invalidos=0,
            tempo_execucao=time.time() - iteration_start_time,
            taxa_sucesso_ferramentas=0.0,
            consultas_alternativas_usadas=0,
            erros_validacao=1,
            qualidade_dados=0.0,
        )

        system_monitor.log_iteration_end(error_metrics)
        return error_metrics


def run_optimized_system(num_iterations: int = 1):
    """
    Executa o sistema otimizado com monitoramento completo

    Args:
        num_iterations: Número de iterações para executar
    """
    # Configuração inicial
    logger = setup_logging()
    logger.info("=== INICIANDO SISTEMA CREWAI OTIMIZADO ===")

    # Valida ambiente
    if not validate_environment():
        logger.error("Falha na validação do ambiente. Encerrando.")
        sys.exit(1)

    # Inicializa AgentOps
    agentops_enabled = initialize_agentops()
    if agentops_enabled:
        logger.info("AgentOps inicializado")

    # Carrega validador geográfico
    location_validator = LocationValidator()
    logger.info(
        f"Carregados {len(location_validator.sp_municipalities)} municípios de SP"
    )

    # Executa iterações
    all_metrics = []

    for i in range(1, num_iterations + 1):
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"ITERAÇÃO {i}/{num_iterations}")
            logger.info(f"{'='*50}")

            metrics = run_single_iteration(i, logger)
            all_metrics.append(metrics)

            # Pausa entre iterações para evitar rate limiting
            if i < num_iterations:
                logger.info("Aguardando 30 segundos antes da próxima iteração...")
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Execução interrompida pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro crítico na iteração {i}: {str(e)}")
            continue

    # Gera relatório final
    logger.info(f"\n{'='*50}")
    logger.info("GERANDO RELATÓRIO FINAL")
    logger.info(f"{'='*50}")

    try:
        final_report = system_monitor.generate_performance_report()

        # Log do resumo do relatório
        if "session_summary" in final_report:
            summary = final_report["session_summary"]
            logger.info(f"Total de iterações: {summary['total_iterations']}")
            logger.info(
                f"Duração da sessão: {summary['session_duration_minutes']:.1f} minutos"
            )
            logger.info(f"Total de alertas: {summary['total_alerts']}")

        if "performance_stats" in final_report:
            perf = final_report["performance_stats"]
            logger.info(
                f"Tempo médio por iteração: {perf['avg_execution_time_minutes']:.1f} minutos"
            )
            logger.info(f"Qualidade média dos dados: {perf['avg_data_quality']:.2%}")
            logger.info(
                f"Taxa média de sucesso das ferramentas: {perf['avg_tool_success_rate']:.2%}"
            )

        if "data_collection" in final_report:
            data = final_report["data_collection"]
            logger.info(f"Total de notícias encontradas: {data['total_news_found']}")
            logger.info(f"Total de notícias validadas: {data['total_news_validated']}")
            logger.info(
                f"Total de duplicatas removidas: {data['total_duplicates_removed']}"
            )

        logger.info("Relatório completo salvo em logs/performance_report_*.json")

    except Exception as e:
        logger.error(f"Erro gerando relatório final: {str(e)}")

    logger.info("=== SISTEMA CREWAI OTIMIZADO FINALIZADO ===")


def main():
    """Função principal com opções de configuração"""
    # Configurações via variáveis de ambiente
    num_iterations = int(os.getenv("CREWAI_ITERATIONS", "1"))

    # Executa sistema otimizado
    run_optimized_system(num_iterations)


if __name__ == "__main__":
    main()
