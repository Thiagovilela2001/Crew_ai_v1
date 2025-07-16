"""
Teste de integração para verificar se o sistema está funcionando corretamente
"""

import logging
from crew import Teste
from utils.system_monitor import system_monitor
from utils.data_processor import data_processor

def test_crew_integration():
    """Testa a integração completa do sistema"""
    
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=== TESTE DE INTEGRAÇÃO DO SISTEMA ===\n")
    
    try:
        # Inicia monitoramento
        system_monitor.log_iteration_start(1)
        
        # Executa a crew
        logger.info("Executando crew...")
        crew_result = Teste().crew().kickoff()
        
        # Analisa o resultado
        logger.info(f"Tipo do resultado: {type(crew_result)}")
        logger.info(f"Resultado: {str(crew_result)[:200]}...")
        
        # Verifica atributos disponíveis
        print(f"\nAtributos do resultado da crew:")
        for attr in dir(crew_result):
            if not attr.startswith('_'):
                try:
                    value = getattr(crew_result, attr)
                    print(f"  - {attr}: {type(value)} = {str(value)[:100]}...")
                except:
                    print(f"  - {attr}: (erro ao acessar)")
        
        # Tenta extrair dados
        raw_data = None
        if hasattr(crew_result, 'raw'):
            raw_data = crew_result.raw
            print(f"\nDados em crew_result.raw: {type(raw_data)}")
        elif hasattr(crew_result, 'output'):
            raw_data = crew_result.output
            print(f"\nDados em crew_result.output: {type(raw_data)}")
        else:
            raw_data = str(crew_result)
            print(f"\nUsando crew_result como string: {type(raw_data)}")
        
        print(f"Conteúdo dos dados: {str(raw_data)[:300]}...")
        
        # Verifica estatísticas do monitor
        print(f"\n=== ESTATÍSTICAS DO MONITOR ===")
        print(f"Tool calls total: {system_monitor.tool_calls_total}")
        print(f"Tool calls success: {system_monitor.tool_calls_success}")
        print(f"Validation errors: {system_monitor.validation_errors}")
        
        if system_monitor.tool_calls_total > 0:
            success_rate = system_monitor.tool_calls_success / system_monitor.tool_calls_total
            print(f"Taxa de sucesso: {success_rate:.2%}")
        else:
            print("Nenhuma ferramenta foi chamada!")
        
        return crew_result
        
    except Exception as e:
        logger.error(f"Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_crew_integration()
    
    if result:
        print("\n✅ Teste concluído - verifique os logs acima")
    else:
        print("\n❌ Teste falhou - verifique os erros acima")