#!/usr/bin/env python
import sys
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from crew import Teste

# Inicializa AgentOps com segurança (caso esteja habilitado no .env)
try:
    import agentops
    AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
    if AGENTOPS_API_KEY:
        agentops.init(api_key=AGENTOPS_API_KEY)
        agentops.start_session()
except ImportError:
    pass  # Segue normalmente se agentops não estiver instalado

def run():
    """
    Executa a Crew com parâmetros de data.
    """
    data_atual = datetime.today().strftime('%d/%m/%Y')
    data_limite = (datetime.now() - relativedelta(months=2)).strftime('%d/%m/%Y')

    Teste().crew().kickoff()

run()
