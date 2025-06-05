library(jsonlite)
library(tidyverse)

# Definir diretório onde estão os arquivos
setwd("C:/Users/lucasmingardo/Documents/Projetos/testes_crewai/versao_20250205/crewai")

# Listar todos os arquivos de texto na pasta "output"
arquivos <- list.files("output", pattern = "\\.txt$", full.names = TRUE)

# Função para processar um único arquivo
processar_json <- function(file_path) {
  # Ler todas as linhas do arquivo
  linhas <- readLines(file_path, warn = FALSE)
  
  # Remover cabeçalho e rodapé ("```json" e "```")
  linhas <- linhas[!(linhas == "```json" | linhas == "```")]
  
  # Unir as linhas em uma única string
  texto_completo <- paste(linhas, collapse = " ")
  
  # Extrair JSON entre colchetes [ ... ]
  json_bruto <- regmatches(texto_completo, regexpr("\\[.*\\]", texto_completo))
  
  # Se JSON foi encontrado, tentar converter para dataframe
  if (length(json_bruto) > 0 && json_bruto != "") {
    df <- tryCatch(fromJSON(json_bruto), error = function(e) NULL)
    
    # Adicionar o nome do arquivo para rastrear a origem dos dados
    if (!is.null(df)) {
      df <- df %>%
        mutate(arquivo_origem = basename(file_path))
    }
    
    return(df)
  } else {
    return(NULL)  # Retorna NULL se nenhum JSON for encontrado
  }
}

# Processar todos os arquivos e combiná-los em um único dataframe
df_final <- arquivos %>%
  map_dfr(~ processar_json(.x))  # map_dfr() une automaticamente os dataframes

# Exibir resultado
print(df_final)


# Salvar resultado
write.csv2(df_final, "output/relatorio_investimentos.csv",
           fileEncoding = "latin1",
           row.names = F
           )


# Fim do Arquivo