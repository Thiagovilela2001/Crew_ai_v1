# serp_tool_aprimorado.py

from crewai.tools import BaseTool
import requests
import json
import os
import time # Importar time para possíveis delays em retries
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import ClassVar, List, Dict, Any
from datetime import datetime

load_dotenv()

class GoogleSearchTool(BaseTool):
    name: str = "Google Search Tool"
    description: str = (
        "Busca na internet por notícias sobre um tópico específico, **reforçando a busca para o estado de São Paulo**, "
        "restrito a uma lista predefinida de sites, com número específico de resultados, intervalo de datas, "
        "e tentativas de busca alternativas opcionais."
    )

    ALLOWED_SITES: ClassVar[List[str]] = [
        # ... (lista de sites permitidos permanece a mesma)
        "abcr.org.br", "aberje.org.br", "abinee.org.br", "acidadevotuporanga.com.br", 
        "araraquara.com", "atribuna.com.br", "bndes.gov.br", "canalenergia.com.br", 
        "canalrioclaro.com.br", "canaonline.com.br", "cbic.org.br", "comerciodojahu.com.br", 
        "correiopopular.com.br", "correio.rac.com.br", "cultura.estadao.com.br", "dci.com.br", 
        "dcomercio.com.br", "dgabc.com.br", "diariodafranca.com.br", "diariodaregiao.com.br", 
        "diariodemarilia.com.br", "diariodesorocaba.com.br", "diariosp.com.br", "estadao.com.br", 
        "einvestidor.estadao.com.br", "flip.siteseguro.ws", "folhadaregiao.com.br", "gcn.net.br", 
        "globo.com", "guarulhosweb.com.br", "imparcial.com.br", "j1diario.com.br", 
        "jcnet.com.br", "jj.com.br", "jornalcana.com.br", "jornalcruzeiro.com.br", 
        "jornaldamanhamarilia.com.br", "jornaldebarretos.com.br", "jornaldecampinas.com.br", 
        "jornaldepiracicaba.com.br", "jornaldocarro.estadao.com.br", "jornalacidade.com.br", 
        "jpdigital.com.br", "noticiadamanha.com.br", "odiariodemogi.com.br", 
        "odiariodaregiao.com", "oimparcial.com.br", "pipelinevalor.globo.com", 
        "politica.estadao.com.br", "redebomdia.com.br", "ribeiraopretoonline.com.br", 
        "sampi.net.br", "saocarlosemrede.com.br", "tododia.uol.com.br", "uol.com.br", 
        "valor.com.br", "vp.virtualpaper.com.br", "webdiario.com.br"
    ]

    def _run(self, query: str, quantidade: int = 5, data_limite: str = None, tentativas_query: List[str] = None) -> List[Dict[str, Any]]:
        """
        Busca na internet com opções aprimoradas e filtro geografico direcionado para SP.

        Args:
            query (str): A consulta de busca principal (sem necessidade de incluir "São Paulo" explicitamente, será adicionado).
            quantidade (int): O número máximo de resultados a retornar.
            data_limite (str): A data de publicação dada no dia 04/06/2025 no formato DD/MM/YYYY.
            tentativas_query (List[str]): (Opcional) Lista de queries alternativas.
            
        Returns:
            List[Dict[str, Any]]: Lista de dicionários contendo titulo, link, descricao e data_publicacao_estimada.
        """
        if not os.getenv("SERPER_API_KEY"):
            return [{"error": "SERPER_API_KEY não configurada no ambiente."}]
        if not isinstance(quantidade, int) or quantidade < 1:
            return [{"error": "Quantidade deve ser um inteiro positivo."}]

        geo_filter = '"estado de São Paulo" OR "município de" SP'
        
        queries_a_tentar = [f"{query} {geo_filter}"]
        if tentativas_query:
            queries_a_tentar.extend([f"{alt_query} {geo_filter}" for alt_query in tentativas_query])

        results = []
        tentativa_atual = 0

        # Loop pelas queries alternativas
        while tentativa_atual < len(queries_a_tentar) and len(results) < quantidade:
            current_query = queries_a_tentar[tentativa_atual]
            print(f"--- Tentando busca com query: '{current_query}' ---") # Log interno

            # Lógica de busca (similar à anterior, mas dentro do loop de tentativas)
            tbs_param = "qdr:m" # Default: último mês
            if data_limite == '05/06/2025':
                # Se a data for a data fixa, não aplica filtro de data
                try:
                    date_obj = datetime.strptime(data_limite, "%d/%m/%Y")
                    api_date = date_obj.strftime("%m/%d/%Y")
                    tbs_param = f"cdr:1,cd_min:{api_date}"
                except ValueError:
                    # Se a data for inválida em uma tentativa, reporta e continua para a próxima query
                    print(f"Alerta: Formato de data_limite inválido ('{data_limite}') na tentativa {tentativa_atual + 1}. Pulando para próxima query se houver.")
                    tentativa_atual += 1
                    continue

            url = "https://google.serper.dev/search"
            start = 0
            max_pages_per_query = 5 # Limitar páginas por tentativa para agilizar
            paginas_tentadas = 0
            resultados_nesta_query = []

            while len(results) + len(resultados_nesta_query) < quantidade and paginas_tentadas < max_pages_per_query:
                site_restriction = " | ".join(f"site:{site}" for site in self.ALLOWED_SITES)
                full_query = f"{current_query} {site_restriction}"

                payload = json.dumps({
                    "q": full_query,
                    "gl": "br",
                    "hl": "pt-br",
                    "tbs": tbs_param,
                    "location": "São Paulo, Brazil",
                    "num": 10, # Busca 10 por página
                    "start": start
                })
                headers = {
                    "Content-Type": "application/json",
                    "X-API-KEY": os.getenv("SERPER_API_KEY")
                }

                try:
                    response = requests.post(url, headers=headers, data=payload, timeout=15) # Adiciona timeout
                    response.raise_for_status()
                    response_data = response.json()
                    organic_results = response_data.get("organic", [])

                    if not organic_results:
                        print(f"--- Nenhum resultado orgânico na página {paginas_tentadas + 1} para query '{current_query}' ---")
                        break # Sai do loop de páginas se não houver mais resultados

                    # Filtra por sites permitidos e formata
                    filtered_page_results = [
                        {
                            "titulo": result.get("title", "Sem título"),
                            "link": result.get("link", "Sem link"),
                            "descricao": result.get("snippet", "Sem descrição"),
                            "data_publicacao_estimada": result.get("date", None) # <-- EXTRAÇÃO DA DATA
                        }
                        for result in organic_results
                        if any(site in urlparse(result.get("link", "")).netloc.lower() for site in self.ALLOWED_SITES)
                    ]
                    
                    resultados_nesta_query.extend(filtered_page_results)
                    
                    start += 10
                    paginas_tentadas += 1
                    time.sleep(0.5) # Pequeno delay entre páginas

                except requests.RequestException as e:
                    print(f"Erro na busca da página {paginas_tentadas + 1} para query '{current_query}': {str(e)}")
                    # Considerar se deve parar a tentativa ou apenas pular a página
                    break # Para a busca desta query em caso de erro
            
            # Adiciona os resultados desta query aos resultados gerais
            results.extend(resultados_nesta_query)
            print(f"--- Fim da tentativa {tentativa_atual + 1}. Resultados até agora: {len(results)} ---")

            # Se já atingiu a quantidade, não precisa tentar outras queries
            if len(results) >= quantidade:
                break

            tentativa_atual += 1
            time.sleep(1) # Delay entre queries diferentes

        # Retorna a quantidade desejada ou o que foi encontrado
        final_results = results[:quantidade]
        if not final_results:
            return [{"error": "Nenhum resultado encontrado nos sites permitidos após todas as tentativas."}]
        
        return final_results

# Exemplo de como o Agente poderia chamar (NÃO EXECUTAR AQUI):
# google_tool = GoogleSearchToolAprimorada()
# resultados = google_tool._run(
#     query="investimento infraestrutura Campinas São Paulo", 
#     quantidade=10, 
#     data_limite="01/03/2025",
#     tentativas_query=["obra infraestrutura Campinas SP", "nova instalação logística Campinas"] # Agente forneceria alternativas
# )
# print(resultados)

