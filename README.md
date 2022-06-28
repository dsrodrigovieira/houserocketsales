# Venda de imóveis em King County, EUA

## Identificação de imóveis para compra e revenda
![](.reports/figures/readme/header.png)

# 1. Objetivo
- Gerar insight através da análise e manipulação dos dados para auxiliar a tomada de decisão do time de negócio

# 2. Questão de negócio
- Encontrar as melhores oportunidades de compra de imóveis em King County.
- A tomada de decisão depende da experiência dos colaboradores mais experientes, tomando muito tempo devido ao tamanho do portifólio da empresa.

# 3. Premissas de negócio
- Apenas casas com classificação 5 serão consideradas boas.
- O registro com 33 quartos é um erro de digitação, considerando que os valores de preço, sala de estar, terreno e numero de banheiros estão na média dos imóveis de 3 quartos.
- Imóveis com ano de construção anterior a 2000 são considerados antigos.

# 4. Planejamento da solução
## 4.1 Selecionar imóveis para compra
- Filtrar os imóveis que estejam em boas condições e tenham preço de compra abaixo da mediana da região.
## 4.2 Definir preço e momento ideal para venda
- Definir a mediana de cada região, filtrando pela estação do ano.
- Imóveis com custo acima da mediana terão uma margem de 10%, os demais, margem de 30%.
# 5. Principais insights
**Hipótese 1:** Imóveis com vista para água são mais caros que a média geral do portifolio.
![](.reports/figures/readme/h1.png)
**Verdadeiro.** O valor dos imóveis com vista para a água apresentam variação de 206,82% em relação à média geral.

**Hipótese 2:** Crescimento médio do preço dos imóveis Year over Year (YoY) é de 10%.
![](.reports/figures/readme/h2.png)
**Falso.** A variação percentual do valor médio dos imóveis YoY é de 0,18%.

**Hipótese 3:** Imóveis antigos que passaram por reforma são, em média, mais caros do que imóveis novos.
![](.reports/figures/readme/h3.png)
**Verdadeiro.** A diferença da média do valor dos imóveis antigos reformados em relação aos imóveis novos é de 23,20%.

**Hipótese 4:** Imóveis sem porão tem terrenos maiores do que os imóveis com porão (em média).
![](.reports/figures/readme/h4.png)
**Verdadeiro.** A diferença percentual da área total dos imóveis sem porão em relação aos imóveis com porão é de 22,79%.

# 6. Resultados financeiros
- A utilização desta ferramenta como auxílio na tomada de decisão para definição do preço de venda do portifólio trará um lucro líquido de aproximadamente **US$ 72mi** no próximo exercício.
# 7. Conclusão
- Após análise sobre o portifólio de imóveis em King County, a House Rocket identificou **698** imóveis em boas condições para aquisição pelo preço mais vantajoso possível.
- A venda destes imóveis com a margem sugerida proporciona um aumento de **12%** sobre o lucro do período anterior.
# 8. Melhorias
- Agendar a coleta dos dados atualizados e execução do script automaticamente.
- Criar arquivos de log.
#
### [Clique aqui para acessar a solução](https://dsr-houserocketsales.herokuapp.com/)







