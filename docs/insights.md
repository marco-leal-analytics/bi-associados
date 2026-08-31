# Insights

Principais achados e oportunidades identificados sobre a base Gold tratada (`data/2_gold/features.parquet`, 1000 associados). Números medidos diretamente sobre o parquet — o dashboard Power BI (README, item 03.04) ainda não foi construído; quando existir, os valores abaixo devem ser conferidos visualmente e as hipóteses de cruzamento aprofundadas com os filtros interativos das páginas correspondentes.

## Como registrar um insight

Cada achado é documentado com:

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

## Página 1 — Visão Geral

**Achado**: carteira de 1000 associados, renda média de R$ 15.791, saldo médio de R$ 123.365 e 2,99 produtos por associado (mediana 3) — perfil de relacionamento já consolidado, não uma base de captação recente.
**Evidência**: médias gerais sobre `RENDA_MENSAL`, `SALDO_MEDIO`, `QTD_PRODUTOS` na Gold.
**Implicação de negócio**: os KPIs de topo do dashboard devem comunicar uma carteira madura e de renda elevada, não uma base "early stage" — isso molda a expectativa de quem for interpretar as demais páginas.
**Ação sugerida**: usar esses números como baseline nas metas trimestrais de produtos por associado e saldo médio.

## Página 2 — Relacionamento

**Achado**: após a padronização de `CIDADE` (`qualidade_dados.md`), Pato Branco responde por **43,3%** da base — mais que o triplo da segunda maior praça (Cascavel, 15,0%) — e essa concentração se repete de forma equilibrada nas 5 agências (76 a 100 associados de Pato Branco por agência), ou seja, não é efeito de uma agência específica.
**Evidência**: `CIDADE` (Página 2, distribuição por cidade) cruzado com `AGENCIA`.
**Implicação de negócio**: qualquer decisão de expansão, campanha local ou dimensionamento de equipe pautada por cidade tem Pato Branco como praça dominante estrutural da cooperativa, não uma anomalia de uma agência.
**Ação sugerida**: priorizar Pato Branco em ações de relacionamento presencial e tratar as demais 4 cidades (15% cada, aprox.) como praças secundárias de tamanho comparável entre si.

**Achado**: renda concentrada nas faixas superiores — **50,3%** dos associados na faixa "Acima de R$ 15.000" e apenas **3,7%** em "Até R$ 3.000" (mais 1,2% sem renda informada).
**Evidência**: `FAIXA_RENDA` (Página 2, distribuição por faixa de renda).
**Implicação de negócio**: a carteira tem poder aquisitivo alto — produtos e ofertas de maior valor agregado (investimento, crédito consignado, seguros premium) têm público potencial relevante.
**Ação sugerida**: usar a faixa "Acima de R$ 15.000" como base para o cruzamento de oportunidade da Página 4 (ver abaixo).

**Achado**: tempo de relacionamento com mediana de **4,23 anos** (média 4,33, desvio padrão 2,57) sobre os 963 registros válidos — carteira consolidada, mas com dispersão ampla (25% dos associados têm até 2,15 anos; 25% têm mais de 6,61 anos).
**Evidência**: `TEMPO_RELACIONAMENTO_ANOS` (Página 2), excluindo os 37 registros com `DATA_ASSOCIACAO_INVALIDA` (ver `qualidade_dados.md`).
**Implicação de negócio**: a base combina um núcleo fiel de longo prazo com uma cauda relevante de associados mais recentes — estratégias de retenção e de onboarding precisam coexistir, não é uma carteira homogênea.
**Ação sugerida**: segmentar campanhas de fidelização para o quartil de tempo mais alto (> 6,6 anos) separadamente de campanhas de aprofundamento de relacionamento para o quartil mais recente (< 2,2 anos).

## Página 3 — Classificação

**Achado**: por construção do índice em quartis (`regras_negocio.md`, seção 5), a base se divide exatamente em 250/250/250/250 entre Inicial, Em Desenvolvimento, Maduro e Engajado — 25% da carteira ("Inicial") está no quartil mais baixo de engajamento combinado (produtos, tempo, saldo, utilização).
**Evidência**: `CLASSIFICACAO` (Página 3, distribuição percentual e quantitativa).
**Implicação de negócio**: por ser um corte relativo (quartil), "Inicial" não significa necessariamente associado novo ou de baixo valor absoluto — é o quarto mais fraco *em relação ao restante da própria carteira* em cada rodada.
**Ação sugerida**: ao comunicar a Página 3 a stakeholders, deixar explícito que os grupos são relativos entre si (25% cada, por definição), não faixas fixas de mérito — evita a leitura equivocada de que 1/4 da base está "em risco" em termos absolutos.

## Página 4 — Oportunidades

**Achado**: **538 associados (53,8%)** aparecem em pelo menos uma das três listas de oportunidade — mais da metade da carteira tem uma ação comercial objetivamente identificável.
**Evidência**: `FLAG_OPORTUNIDADE_*` (Página 4), união das três flags.
**Implicação de negócio**: o volume de oportunidades acionáveis é grande o suficiente para justificar uma rotina periódica de acompanhamento comercial dedicada a esta página, não um relatório eventual.
**Ação sugerida**: definir um dono (área de relacionamento) e uma cadência (ex.: mensal) para trabalhar as três listas, priorizando pelo cruzamento abaixo.

**Achado**: "Baixa utilização dos serviços" é a maior das três oportunidades — **285 associados (28,5%)** já têm 2+ produtos, mas nível de movimentação Baixa.
**Evidência**: `FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO`.
**Implicação de negócio**: é a maior massa de risco de evasão silenciosa — o associado já contratou produtos, mas não está usando ativamente a cooperativa no dia a dia (saldo, PIX, cartão).
**Ação sugerida**: priorizar esta lista para ações de reativação (ex.: contato consultivo, revisão de produtos contratados vs. uso real) antes das outras duas, dado o volume.

**Achado**: "Alta renda e poucos produtos" soma **177 associados (17,7%)** — e é composta inteiramente por associados da faixa "Acima de R$ 15.000" (35,2% de toda essa faixa de renda tem 2 produtos ou menos, por definição do critério).
**Evidência**: `FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS` cruzada com `FAIXA_RENDA`.
**Implicação de negócio**: mais de 1 em cada 3 associados de alta renda está subutilizado em produtos — é o segmento de maior potencial de receita incremental por associado (ticket médio mais alto), mesmo sendo o menor dos três grupos em volume.
**Ação sugerida**: tratar como prioridade de valor (não de volume) — ofertas consultivas individualizadas de crédito/investimento, e não campanhas de massa.

**Achado**: "Potencial de crescimento" soma **163 associados (16,3%)** — associados "Em Desenvolvimento" (2º quartil de engajamento) que já têm nível de movimentação Média ou Alta, ou seja, já são financeiramente ativos apesar de ainda terem poucos produtos.
**Evidência**: `FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO`.
**Implicação de negócio**: é o segmento com melhor relação esforço/retorno para cross-sell — o associado já demonstrou engajamento financeiro, falta apenas diversificar produtos.
**Ação sugerida**: usar como lista prioritária para ofertas de segundo produto (ex.: cartão para quem só tem conta corrente), medindo taxa de conversão como indicador de sucesso da própria metodologia de classificação.

## Qualidade de dados como insight

**Achado**: 3,7% dos registros (37) têm data de associação futura e 1,2% (12) têm renda não informada — inconsistências da fonte, não do tratamento.
**Evidência**: `DATA_ASSOCIACAO_INVALIDA` e `FAIXA_RENDA = "Não informado"` (ver `qualidade_dados.md`, seção 5.1, para os números completos de qualidade pós-tratamento).
**Implicação de negócio**: qualquer leitura de tempo de relacionamento ou renda média no dashboard já exclui esses registros do cálculo — reportar isso evita que um stakeholder estranhe uma contagem de linhas menor que 1000 em determinados cartões/gráficos.
**Ação sugerida**: manter uma nota de rodapé/tooltip no dashboard citando essas exclusões, em vez de deixá-las implícitas.
