# Insights

Documento vivo: será preenchido com os achados definitivos após a construção do dashboard Power BI. Esta versão inicial define a estrutura de registro e lista hipóteses observadas no profiling dos dados brutos, a validar (ou descartar) com a base tratada.

## Como registrar um insight

Cada achado deve ser documentado com:

1. **Achado** — o que os dados mostram.
2. **Evidência** — indicador/página do dashboard que sustenta o achado.
3. **Implicação de negócio** — por que isso importa.
4. **Ação sugerida** — o que a área de relacionamento/negócio poderia fazer a respeito.

## Páginas do dashboard e o que cada uma deve responder

| Página | Pergunta de negócio |
|---|---|
| 1. Visão Geral | Qual o tamanho e o perfil médio da carteira de associados? |
| 2. Relacionamento | Onde os associados estão concentrados (agência/cidade) e como se distribuem por renda e tempo de casa? |
| 3. Classificação | Como a carteira se divide entre Inicial, Em Desenvolvimento, Maduro e Engajado? |
| 4. Oportunidades | Quais associados representam risco de evasão ou potencial de expansão de relacionamento? |

## Hipóteses iniciais a validar (originadas do profiling em `qualidade_dados.md`)

- **Concentração geográfica em Pato Branco**: somando as três grafias da mesma cidade ("Pato Branco", "P. Branco", "PATO BRANCO"), ela responde por ~43% da base — antes da padronização de `CIDADE`, esse padrão ficaria mascarado como 3 cidades "menores" no dashboard. Validar se, após a limpeza, Pato Branco de fato se destaca como praça de maior concentração e se isso reflete a distribuição por agência.
- **Renda concentrada nas faixas superiores**: ~50% dos associados estão na faixa "Acima de R$ 15.000" e apenas ~4% na faixa "Até R$ 3.000" — perfil de carteira com renda elevada. Verificar se essa concentração é uniforme entre agências/cidades ou se há polarização.
- **Base madura em tempo de relacionamento**: mediana de ~4 anos de relacionamento, com uma cauda de associados acima de 8 anos — sugere carteira consolidada, não uma base recém-captada. A confirmar após excluir os registros com data de associação inválida (futura).
- **Diversificação de produtos mediana, mas com cauda relevante em ambas as pontas**: ~13% dos associados têm 0–1 produto (baixa penetração) e ~12% têm 5–6 produtos (alta diversificação) — potencial claro para as páginas de Classificação e Oportunidades.
- **Qualidade de dados como insight em si**: o fato de 3,7% dos registros terem data de associação futura e ~1,2% terem renda não informada deve ser reportado como limitação/observação metodológica no dashboard ou README, não apenas corrigido silenciosamente.

## Pendências para a versão final deste documento

- Substituir as hipóteses acima pelos números reais pós-tratamento (base Gold).
- Adicionar 3 a 5 insights definitivos por página, seguindo o formato da seção "Como registrar um insight".
- Priorizar os achados que sustentam diretamente as listas de oportunidade da página 4.
