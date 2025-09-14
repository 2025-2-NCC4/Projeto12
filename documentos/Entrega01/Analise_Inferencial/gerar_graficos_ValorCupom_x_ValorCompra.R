cat("=== INÍCIO DA EXECUÇÃO ===\n")

# === 1. Ler arquivo CSV ===
cat("Lendo CSV...\n")
dados <- read.csv(
  "C:/Users/gabri/Downloads/PicMoney_Valor_compra_e_cupom.csv",
  sep = ",",
  dec = ".",
  header = TRUE,
  stringsAsFactors = FALSE
)

cat("Colunas disponíveis:\n")
print(names(dados))

# === 2. Converter colunas valor_compra e valor_cupom para numérico ===
convert_to_numeric <- function(x) {
  x <- gsub(" ", "", x)      # remove espaços
  x <- gsub(",", ".", x)     # substitui vírgula por ponto
  as.numeric(x)
}

dados$valor_compra <- convert_to_numeric(dados$valor_compra)
dados$valor_cupom  <- convert_to_numeric(dados$valor_cupom)

# Remove linhas inválidas
dados <- dados[!is.na(dados$valor_compra) & !is.na(dados$valor_cupom), ]

# === 3. Tipos de cupom ===
tipos_cupom <- c("Cashback", "Produto", "Desconto")

# === 4. Loop por cada tipo de cupom e salvar gráfico em PNG ===
for (tipo in tipos_cupom) {
  
  cat("\n--- Analisando cupom do tipo:", tipo, "---\n")
  
  # Filtra dados
  dados_tipo <- subset(dados, tipo_cupom == tipo)
  
  if (nrow(dados_tipo) == 0) {
    cat("Nenhum dado para este tipo de cupom.\n")
    next
  }
  
  # Seleciona colunas
  valor_compra <- dados_tipo$valor_compra
  valor_cupom  <- dados_tipo$valor_cupom
  
  # Correlação
  correlacao <- cor(valor_compra, valor_cupom, use = "complete.obs")
  cat("Correlação entre valor_compra e valor_cupom:", correlacao, "\n")
  
  # Regressão Linear
  modelo <- lm(valor_compra ~ valor_cupom)
  print(summary(modelo))
  
  # === Salvar gráfico em PNG ===
  arquivo_png <- paste0("grafico_", tipo, ".png")
  png(filename = arquivo_png, width = 800, height = 600)
  
  plot(valor_cupom, valor_compra,
       main = paste("Valor do Cupom x Valor da Compra -", tipo, "  (R$)"),
       xlab = "Valor do Cupom",
       ylab = "Valor da Compra",
       pch = 19, col = "blue",
       cex.main = 2,
       cex.lab  = 1.5,
       cex.axis = 1.2
  )
  abline(modelo, col = "red", lwd = 2)
  
  dev.off()  # Fecha o arquivo PNG
  cat("Gráfico salvo em:", arquivo_png, "\n")
}

cat("\n=== FIM DA EXECUÇÃO ===\n")

getwd()
