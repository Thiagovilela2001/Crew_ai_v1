from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os
from datetime import datetime
from crewai_tools import MCPServerAdapter
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.knowledge import Knowledge
from tools.serp_tool import GoogleSearchTool
from tools.validated_tools import validated_google_tool, validated_scrape_tool
from crewai.memory import ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage

# Carregar variáveis de ambiente e criar diretório de saída
load_dotenv()
os.makedirs("output", exist_ok=True)

# API Keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Fontes de conhecimento
# csv_source = CSVKnowledgeSource(file_paths=["investimentos2025.csv"], encoding='utf-8')
pdf_source = PDFKnowledgeSource(file_paths=["piesp_metodologia.pdf"])
pdf_source2 = PDFKnowledgeSource(
    file_paths=["piesp-pesquisa-de-investimentos-anunciados.pdf"]
)
pdf_source3 = PDFKnowledgeSource(file_paths=["piesp_captados_2025.pdf"])
txt_source = TextFileKnowledgeSource(file_paths=["municipios_sp.txt"])

# Corrigir erro: adicionar collection_name
pesquisador_knowledge = Knowledge(
    collection_name="pesquisador_sp",
    sources=[pdf_source, pdf_source2, txt_source, pdf_source3],
)

analista_knowledge = Knowledge(
    collection_name="analista_sp", sources=[pdf_source, txt_source]
)

# Ferramentas
search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool()
google_tool = GoogleSearchTool()


def get_entity_memory(user_id: str):
    embedder_config = {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "dimensions": 512,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }
    entity = EntityMemory(
        storage=RAGStorage(
            embedder_config=embedder_config,
            type="entity",
            path=f".memnory/entity/{user_id}/",
        )
    )
    return {"entity": entity}


@CrewBase
class Teste:
    """Equipe unificada de pesquisa de notícias SP"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def pesquisador_noticias(self) -> Agent:
        return Agent(
            config=self.agents_config["pesquisador_noticias"],
            tools=[validated_google_tool, validated_scrape_tool],
            knowledge=pesquisador_knowledge,
            allow_delegation=False,
            verbose=True,
            memory=True,
            llm="gpt-4o-mini",
        )

    @agent
    def analista_relatorios(self) -> Agent:
        return Agent(
            config=self.agents_config["analista_relatorios"],
            tools=[validated_google_tool, validated_scrape_tool],
            knowledge=analista_knowledge,
            memory=True,
            llm="gpt-4o-mini",
        )

    @agent
    def analista_duplicatas(self) -> Agent:
        return Agent(
            config=self.agents_config["verificador_duplicatas"],
            tools=[validated_google_tool, validated_scrape_tool],
            knowledge=analista_knowledge,
            memory=True,
            llm="gpt-4o-mini",
        )

    # === Tarefas de pesquisa simplificadas ===

    @task
    def research_task_piesp_sp_2025(self):
        return Task(
            config=self.tasks_config["research_task_piesp_sp_2025"],
            agent=self.pesquisador_noticias(),
            tools=[validated_google_tool, validated_scrape_tool],
        )

    @task
    def research_task_piesp_sp_2025_relatorios(self):
        return Task(
            config=self.tasks_config["reporting_task_csv"],
            agent=self.analista_relatorios(),
            tools=[validated_google_tool, validated_scrape_tool],
            context=[self.research_task_piesp_sp_2025()],
            async_execution=False,
        )

    @task
    def research_task_piesp_sp_2025_duplicatas(self):
        return Task(
            config=self.tasks_config["identificar_noticias_repetidas"],
            agent=self.analista_duplicatas(),
            tools=[validated_google_tool, validated_scrape_tool],
            context=[self.research_task_piesp_sp_2025_relatorios()],
            async_execution=False,
        )

    # Task de consolidação
    @task
    def reporting_task_investimentos(self):
        return Task(
            config=self.tasks_config["identificar_noticias_repetidas"],
            agent=self.analista_duplicatas(),
            tools=[validated_google_tool, validated_scrape_tool],
            output_file=f"output/relatorio_final_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.json",
            context=[self.research_task_piesp_sp_2025()],
            async_execution=False,
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
