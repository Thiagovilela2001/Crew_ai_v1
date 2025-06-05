from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os
from datetime import datetime
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.knowledge import Knowledge
from tools.serp_tool import GoogleSearchTool

# Carregar variáveis de ambiente e criar diretório de saída
load_dotenv()
os.makedirs("output", exist_ok=True)

# API Keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
# Fontes de conhecimento
pdf_source = PDFKnowledgeSource(file_paths=["piesp_metodologia.pdf"])
pdf_source2 = PDFKnowledgeSource(file_paths=["piesp-pesquisa-de-investimentos-anunciados.pdf"])
txt_source = TextFileKnowledgeSource(file_paths=["municipios_sp.txt"])

# Corrigir erro: adicionar collection_name
pesquisador_knowledge = Knowledge(
    collection_name="pesquisador_sp",
    sources=[pdf_source, pdf_source2, txt_source]
)

analista_knowledge = Knowledge(
    collection_name="analista_sp",
    sources=[pdf_source]
)

# Ferramentas
search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool()
google_tool = GoogleSearchTool(api_key=SERPER_API_KEY)

@CrewBase
class Teste:
    """Equipe unificada de pesquisa de notícias SP"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def pesquisador_noticias(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisador_noticias'],
            tools=[google_tool, scrape_tool],
            knowledge=pesquisador_knowledge,
            allow_delegation=False,
            verbose=True,
            memory=False,
            llm='gpt-4o-mini'
        )

    @agent
    def analista_relatorios(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_relatorios'],
            tools=[google_tool],
            knowledge=analista_knowledge,
            memory=False,
            llm='gpt-4o-mini'
        )

    # === Tarefas de pesquisa simplificadas ===

    @task
    def research_task_piesp_sp_2025(self): 
        return Task(
            config=self.tasks_config['research_task_piesp_sp_2025'], 
            agent=self.pesquisador_noticias()
        )

    # Task de consolidação
    @task
    def reporting_task_investimentos(self): 
        return Task(
            config=self.tasks_config['reporting_task_investimentos'],
            agent=self.analista_relatorios(),
            output_file=f"output/relatorio_final_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json",
            context=[
                self.research_task_piesp_sp_2025()
            ],
            async_execution=False
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )