"""
Sistema de logging e monitoramento para CrewAI
Registra métricas de desempenho e qualidade dos dados
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import statistics

@dataclass
class SystemMetrics:
    """Métricas de sistema para uma iteração"""
    iteracao: int
    timestamp: str
    total_noticias_encontradas: int
    noticias_validadas: int
    duplicatas_removidas: int
    municipios_invalidos: int
    tempo_execucao: float
    taxa_sucesso_ferramentas: float
    consultas_alternativas_usadas: int
    erros_validacao: int
    qualidade_dados: float

@dataclass
class PerformanceAlert:
    """Alerta de performance do sistema"""
    tipo: str
    severidade: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    mensagem: str
    timestamp: str
    contexto: Dict[str, Any]

class SystemMonitor:
    """Monitor de sistema para CrewAI"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Métricas da sessão atual
        self.current_iteration = 0
        self.session_start_time = time.time()
        self.iteration_metrics: List[SystemMetrics] = []
        self.alerts: List[PerformanceAlert] = []
        
        # Contadores para métricas
        self.tool_calls_success = 0
        self.tool_calls_total = 0
        self.validation_errors = 0
        
        # Thresholds para alertas
        self.alert_thresholds = {
            'execution_time_minutes': 10,
            'data_quality_min': 0.7,
            'tool_success_rate_min': 0.8,
            'validation_error_max': 5
        }
    
    def _setup_logging(self):
        """Configura logging estruturado em JSON"""
        # Handler para arquivo de log
        log_file = self.log_dir / f"system_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # Handler para console
        console_handler = logging.StreamHandler()
        
        # Formatter JSON estruturado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_iteration_start(self, iteration: int) -> None:
        """
        Registra início de uma iteração
        
        Args:
            iteration: Número da iteração
        """
        self.current_iteration = iteration
        self.iteration_start_time = time.time()
        
        log_entry = {
            'event': 'iteration_start',
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'session_duration_minutes': (time.time() - self.session_start_time) / 60
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_iteration_end(self, metrics: SystemMetrics) -> None:
        """
        Registra fim de uma iteração com métricas
        
        Args:
            metrics: Métricas da iteração
        """
        self.iteration_metrics.append(metrics)
        
        log_entry = {
            'event': 'iteration_end',
            'metrics': asdict(metrics)
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        # Verifica alertas
        self._check_performance_alerts(metrics)
    
    def log_data_quality_metrics(self, data: List[Dict[str, Any]]) -> float:
        """
        Registra métricas de qualidade dos dados coletados
        
        Args:
            data: Lista de dados coletados
            
        Returns:
            Score de qualidade dos dados (0-1)
        """
        if not data:
            quality_score = 0.0
        else:
            # Calcula score baseado em campos preenchidos
            total_fields = 0
            filled_fields = 0
            
            required_fields = [
                'titulo', 'link', 'descricao_detalhada', 'data', 
                'municipio', 'tipo_investimento'
            ]
            
            for item in data:
                for field in required_fields:
                    total_fields += 1
                    if field in item and item[field] and str(item[field]).strip():
                        filled_fields += 1
            
            quality_score = filled_fields / total_fields if total_fields > 0 else 0.0
        
        log_entry = {
            'event': 'data_quality_check',
            'timestamp': datetime.now().isoformat(),
            'iteration': self.current_iteration,
            'total_records': len(data),
            'quality_score': quality_score,
            'quality_percentage': quality_score * 100
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        # Alerta se qualidade baixa
        if quality_score < self.alert_thresholds['data_quality_min']:
            self._create_alert(
                'DATA_QUALITY',
                'HIGH',
                f'Qualidade dos dados baixa: {quality_score:.2%}',
                {'quality_score': quality_score, 'records': len(data)}
            )
        
        return quality_score
    
    def log_duplicate_consolidation(self, before: int, after: int) -> None:
        """
        Registra consolidação de duplicatas
        
        Args:
            before: Número de registros antes da consolidação
            after: Número de registros após consolidação
        """
        duplicates_removed = before - after
        reduction_rate = duplicates_removed / before if before > 0 else 0
        
        log_entry = {
            'event': 'duplicate_consolidation',
            'timestamp': datetime.now().isoformat(),
            'iteration': self.current_iteration,
            'records_before': before,
            'records_after': after,
            'duplicates_removed': duplicates_removed,
            'reduction_rate': reduction_rate
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_tool_usage(self, tool_name: str, success: bool, execution_time: float, 
                      params: Dict[str, Any] = None) -> None:
        """
        Registra uso de ferramenta
        
        Args:
            tool_name: Nome da ferramenta
            success: Se a execução foi bem-sucedida
            execution_time: Tempo de execução em segundos
            params: Parâmetros usados na ferramenta
        """
        self.tool_calls_total += 1
        if success:
            self.tool_calls_success += 1
        
        log_entry = {
            'event': 'tool_usage',
            'timestamp': datetime.now().isoformat(),
            'iteration': self.current_iteration,
            'tool_name': tool_name,
            'success': success,
            'execution_time_seconds': execution_time,
            'params': params or {}
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def log_validation_error(self, error_type: str, error_message: str, 
                           context: Dict[str, Any] = None) -> None:
        """
        Registra erro de validação
        
        Args:
            error_type: Tipo do erro
            error_message: Mensagem de erro
            context: Contexto adicional
        """
        self.validation_errors += 1
        
        log_entry = {
            'event': 'validation_error',
            'timestamp': datetime.now().isoformat(),
            'iteration': self.current_iteration,
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))
        
        # Alerta se muitos erros de validação
        if self.validation_errors > self.alert_thresholds['validation_error_max']:
            self._create_alert(
                'VALIDATION_ERRORS',
                'HIGH',
                f'Muitos erros de validação: {self.validation_errors}',
                {'error_count': self.validation_errors}
            )
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Gera relatório de performance da sessão
        
        Returns:
            Relatório com estatísticas de performance
        """
        if not self.iteration_metrics:
            return {'error': 'Nenhuma métrica disponível'}
        
        # Calcula estatísticas
        execution_times = [m.tempo_execucao for m in self.iteration_metrics]
        quality_scores = [m.qualidade_dados for m in self.iteration_metrics]
        success_rates = [m.taxa_sucesso_ferramentas for m in self.iteration_metrics]
        
        report = {
            'session_summary': {
                'total_iterations': len(self.iteration_metrics),
                'session_duration_minutes': (time.time() - self.session_start_time) / 60,
                'total_alerts': len(self.alerts)
            },
            'performance_stats': {
                'avg_execution_time_minutes': statistics.mean(execution_times) / 60,
                'max_execution_time_minutes': max(execution_times) / 60,
                'min_execution_time_minutes': min(execution_times) / 60,
                'avg_data_quality': statistics.mean(quality_scores),
                'avg_tool_success_rate': statistics.mean(success_rates)
            },
            'data_collection': {
                'total_news_found': sum(m.total_noticias_encontradas for m in self.iteration_metrics),
                'total_news_validated': sum(m.noticias_validadas for m in self.iteration_metrics),
                'total_duplicates_removed': sum(m.duplicatas_removidas for m in self.iteration_metrics),
                'total_invalid_locations': sum(m.municipios_invalidos for m in self.iteration_metrics)
            },
            'alerts': [asdict(alert) for alert in self.alerts],
            'iteration_details': [asdict(m) for m in self.iteration_metrics]
        }
        
        # Salva relatório em arquivo
        report_file = self.log_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Relatório de performance salvo em: {report_file}")
        return report
    
    def _check_performance_alerts(self, metrics: SystemMetrics) -> None:
        """
        Verifica se métricas acionam alertas de performance
        
        Args:
            metrics: Métricas da iteração
        """
        # Alerta por tempo de execução alto
        if metrics.tempo_execucao > self.alert_thresholds['execution_time_minutes'] * 60:
            self._create_alert(
                'EXECUTION_TIME',
                'MEDIUM',
                f'Tempo de execução alto: {metrics.tempo_execucao/60:.1f} minutos',
                {'execution_time_minutes': metrics.tempo_execucao/60}
            )
        
        # Alerta por baixa taxa de sucesso de ferramentas
        if metrics.taxa_sucesso_ferramentas < self.alert_thresholds['tool_success_rate_min']:
            self._create_alert(
                'TOOL_SUCCESS_RATE',
                'HIGH',
                f'Taxa de sucesso de ferramentas baixa: {metrics.taxa_sucesso_ferramentas:.2%}',
                {'success_rate': metrics.taxa_sucesso_ferramentas}
            )
        
        # Alerta por qualidade de dados baixa
        if metrics.qualidade_dados < self.alert_thresholds['data_quality_min']:
            self._create_alert(
                'DATA_QUALITY',
                'HIGH',
                f'Qualidade de dados baixa: {metrics.qualidade_dados:.2%}',
                {'quality_score': metrics.qualidade_dados}
            )
    
    def _create_alert(self, alert_type: str, severity: str, message: str, 
                     context: Dict[str, Any]) -> None:
        """
        Cria um alerta de performance
        
        Args:
            alert_type: Tipo do alerta
            severity: Severidade do alerta
            message: Mensagem do alerta
            context: Contexto adicional
        """
        alert = PerformanceAlert(
            tipo=alert_type,
            severidade=severity,
            mensagem=message,
            timestamp=datetime.now().isoformat(),
            contexto=context
        )
        
        self.alerts.append(alert)
        
        log_entry = {
            'event': 'performance_alert',
            'alert': asdict(alert)
        }
        
        self.logger.warning(json.dumps(log_entry, ensure_ascii=False))


# Instância global do monitor
system_monitor = SystemMonitor()