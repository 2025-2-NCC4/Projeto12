cat("=== INÍCIO DA EXECUÇÃO ===\n")

# 1. Ler CSV
dados <- read.csv(
  "C:/Users/gabri/Downloads/PicMoney_Valor_compra_e_cupom.csv",
  sep = ",", dec = ".", header = TRUE, stringsAsFactors = FALSE
)

# 2. Converter colunas numéricas
convert_to_numeric <- function(x) {
  x <- gsub(" ", "", x)
  x <- gsub(",", ".", x)
  as.numeric(x)
}
dados$valor_compra <- convert_to_numeric(dados$valor_compra)
dados$valor_cupom  <- convert_to_numeric(dados$valor_cupom)
dados <- dados[!is.na(dados$valor_compra) & !is.na(dados$valor_cupom), ]

# 3. Tipos de cupom
tipos_cupom <- c("Cashback", "Produto", "Desconto")

# 4. Função para intervalo de confiança da média (Z)
intervalo_confianca_media <- function(x, nivel = 0.95) {
  n <- length(x)
  media <- mean(x)
  s <- sd(x)
  erro_padrao <- s / sqrt(n)
  z_crit <- qnorm(1 - (1 - nivel)/2)
  li <- media - z_crit * erro_padrao
  ls <- media + z_crit * erro_padrao
  return(c(media = media, li = li, ls = ls, n = n))
}

# 5. Cálculo por tipo de cupom
resultados <- data.frame()
for (tipo in tipos_cupom) {
  dados_tipo <- subset(dados, tipo_cupom == tipo)
  if (nrow(dados_tipo) == 0) next
  
  ic <- intervalo_confianca_media(dados_tipo$valor_compra)
  
  cat("\n---", tipo, "---\n")
  cat("n =", ic["n"], "\n")
  cat("Média amostral =", round(ic["media"], 2), "\n")
  cat("IC 95% para média populacional: [", round(ic["li"], 2), ",", round(ic["ls"], 2), "]\n")
  
  resultados <- rbind(resultados, data.frame(
    tipo = tipo,
    media = ic["media"],
    li = ic["li"],
    ls = ic["ls"],
    n = ic["n"]
  ))
}

cat("\n=== RESULTADOS FINAIS ===\n")
print(resultados)

cat("\n=== FIM ===\n")