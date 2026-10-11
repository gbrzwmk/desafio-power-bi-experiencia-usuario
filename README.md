# Desafio de Projeto DIO — Relatório Financeiro com Foco na Experiência do Usuário

Desafio da formação **Power BI Analyst** da [DIO](https://www.dio.me/) (Módulo 5 — *Atualizando Relatório Financeiro com Foco na Experiência do Usuário*). O ponto de partida é o **Relatório Criativo** da instrutora: três páginas (`Sales`, `Profit` e `Report`) em que só a primeira tinha sido reformulada em aula. O desafio pede:

- modificar a segunda página (e a terceira) de forma similar à primeira, pensando em **posicionamento, contraste, proporção áurea e segmentação dos dados**;
- inserir os **botões de navegabilidade** e criar o **menu de navegação em cada página**;
- destacar os estados **focalizar** (hover) e **selecionar / pressionar** dos botões (estilo livre);
- manter o relatório com **3 páginas**.

![Página Profit](prints/pagina-profit.png)

## Arquivos

| Pasta / arquivo | Conteúdo |
|---|---|
| `relatorio_criativo_experiencia_usuario.pbix` | Relatório final com as três páginas padronizadas, menus de navegação com estados e medidas |
| `prints/` | As três páginas, o menu nos estados *focalizar* e *pressionar* e as setas de navegação |
| `power-query/medidas.dax` | As 9 medidas criadas na tabela `financials` |
| `pbip/` | O modelo semântico em TMDL (`financials.tmdl` com as medidas) e o projeto completo em `relatorio_criativo_pbip.zip` (formato Power BI Project: TMDL + PBIR) |
| `scripts/aplicar_experiencia_usuario.py` | Script que reconstrói as páginas Profit e Report e os menus a partir do projeto PBIP (documenta exatamente o que foi alterado) |
| `src/` | O arquivo de partida (`relatorio_criativo_exp_usuario.pbix`), como veio da página do desafio |
| `enunciado/` | Texto do enunciado |

O arquivo original também está no repositório do curso: [julianazanelatto/power_bi_analyst — Módulo 5 / Desafio 1](https://github.com/julianazanelatto/power_bi_analyst/tree/main/M%C3%B3dulo%205).

## Antes e depois

As páginas `Profit` e `Report` vieram no estilo antigo do relatório (fundo cinza, cabeçalho largo com texto "Formação Power BI Analyst / Desafio de Projeto da DIO", botão *Home Page* solto no canto, visuais de tamanhos diferentes e um visual personalizado — *Radar Chart* — que nem vem instalado no Power BI Desktop). A página `Sales` já tinha o padrão novo: faixa lateral azul-marinho com logo, título sublinhado, cartões arredondados, painel cinza arredondado à direita com o filtro no topo e navegador de páginas na faixa.

| Página | Antes | Depois |
|---|---|---|
| Sales | já reformulada em aula | mantida; a seta "Next" ganhou os estados focalizar/pressionar |
| Profit | cabeçalho antigo, *chiclet slicer* de ano, árvore de decomposição, radar (não instalado), treemap e cascata soltos, botão *Home Page* e seta de voltar | mesma grade da Sales: cartões de lucro e margem, filtro de ano, árvore de decomposição, cascata, treemap e barras por produto dentro do painel |
| Report | cabeçalho antigo, área + matriz num quadro cinza e combo num segundo quadro, botão *Home Page* e seta de voltar | mesma grade da Sales: cartões de vendas brutas e descontos, filtro de ano, área + matriz à esquerda, combo e vendas por país no painel |

O arquivo de partida está em `src/` para comparação.

## As três páginas

### Sales

![Sales](prints/pagina-sales.png)

Página de referência (construída na aula). Cartões de vendas e unidades, botões de *bookmark* que alternam a visão por segmento ou por produto, vendas por período, matriz por ano/trimestre e o filtro de data. Única mudança: a seta **Next**, que levava à página Profit, agora tem os mesmos estados dos demais botões.

### Profit

A página foi refeita sobre a **mesma grade** da página Sales:

| Elemento da página Sales | Equivalente na página Profit |
|---|---|
| Título "Sales Report" + sublinhado | "Profit Report" + sublinhado |
| Cartões Total de Vendas / Unidades | **Lucro Total** (`Total Profit`) e **Margem de Lucro** |
| Filtro "Selecione a data" | **Selecione o ano** (segmentação em blocos: 2013 / 2014) |
| Bloco esquerdo (segmento × produto) | **Árvore de decomposição do lucro** (Ano → País), o mesmo visual da página original |
| Painel direito: vendas por período | **Cascata do lucro por trimestre** |
| Painel direito: matriz | **Lucro por segmento** (treemap) e **Lucro por produto** (barras, substitui o *Radar Chart* que não vinha instalado) |

### Report

![Report](prints/pagina-report.png)

| Elemento da página Sales | Equivalente na página Report |
|---|---|
| Título | "Detailed Report" + sublinhado |
| Cartões | **Vendas Brutas** e **Total de Descontos** |
| Filtro | **Selecione o ano** |
| Bloco esquerdo | **Vendas e Lucro por Período** (área, com marcadores) e a matriz **Lucro por ano e trimestre**, os dois visuais originais da página |
| Painel direito | **Vendas e Gross × Período** (combo colunas + linha, visual original) e **Vendas por país** |

## Navegação e estados dos botões

![Menu no estado focalizar](prints/menu-estado-focalizar.png)

- **Menu em todas as páginas.** O navegador de páginas (Sales / Profit / Report) fica na faixa lateral das três páginas, sempre na mesma posição, fora da área dos visuais. A página atual aparece em **negrito azul-marinho sobre branco** (estado *selecionado*).
- **Estados.** Cada botão do menu tem quatro estilos: *padrão* (texto escuro sobre o fundo claro), *focalizar* (ao passar o mouse: preenchimento azul claro e texto branco), *pressionar* (azul-marinho translúcido com texto branco em negrito) e *selecionado* (branco com texto azul-marinho em negrito).
- **Setas.** Além do menu, cada página tem setas na base da faixa: Sales → Profit, Profit ↔ Sales/Report e Report → Profit. As setas também têm os três estados (ícone branco; fundo azul claro ao focalizar; fundo branco com ícone azul-marinho ao pressionar).
- No Power BI Desktop os botões respondem a **Ctrl + clique**; no Power BI Service basta clicar.

![Setas e estado pressionar](prints/menu-estado-pressionar.png)

## Decisões de experiência do usuário

- **Posicionamento.** As três páginas usam a mesma grade: faixa de navegação à esquerda (96 px), título no canto superior esquerdo, cartões logo abaixo, bloco analítico à esquerda e painel de detalhes à direita com o filtro no topo. Quem aprende a ler a página Sales lê as outras duas sem reaprender nada.
- **Contraste.** Texto branco sobre azul-marinho na faixa e nos cartões; visuais com fundo transparente sobre o painel cinza claro; títulos dos visuais em azul escuro. As cores dos dados usam a mesma família de azuis da página Sales (tons do `ColorId 3` do tema), com laranja só para as variações negativas da cascata.
- **Proporção áurea.** A divisão da página segue aproximadamente 1 : 1,6 — bloco esquerdo de ~480 px para o painel direito de ~610 px, e o cartão (201 × 106 px) tem proporção próxima de 1,9 : 1, como no original. Os visuais internos do painel repetem a mesma proporção (cascata em cima, dois visuais menores embaixo).
- **Segmentação dos dados.** Cada página tem um filtro visível no topo do painel (data na Sales, ano na Profit e Report) e todos os visuais interagem entre si; a árvore de decomposição e a matriz permitem descer de ano para país/trimestre.

## Medidas DAX criadas

| Medida | Expressão |
|---|---|
| Total Sales | `SUM(financials[ Sales])` |
| Total Profit | `SUM(financials[Profit])` |
| Margem de Lucro | `DIVIDE([Total Profit], [Total Sales])` |
| Vendas Brutas | `SUM(financials[Gross Sales])` |
| Total de Descontos | `SUM(financials[Discounts])` |
| Unidades Vendidas | `SUM(financials[Units Sold])` |
| Ticket Médio | `DIVIDE([Total Sales], COUNTROWS(financials))` |
| Lucro Ano Anterior | `CALCULATE([Total Profit], SAMEPERIODLASTYEAR(financials[Date]))` |
| Variação Lucro vs Ano Anterior | `DIVIDE([Total Profit] - [Lucro Ano Anterior], [Lucro Ano Anterior])` |

O arquivo original não tinha medidas (os visuais usavam somas implícitas das colunas). As medidas alimentam os cartões e os novos visuais; as somas implícitas dos visuais reaproveitados foram mantidas.

## Como foi construído

1. O `relatrio criativo_exp_usuário.pbix` foi salvo como **projeto do Power BI (.pbip)**, que expõe o modelo em TMDL e o relatório em PBIR (arquivos de texto).
2. O script `scripts/aplicar_experiencia_usuario.py` adiciona as medidas em `financials.tmdl`, apaga os visuais antigos das páginas Profit e Report e recria as páginas copiando a formatação dos elementos da página Sales (faixa, logo, navegador de páginas, cartões, painéis, sublinhado) e reposicionando os visuais de dados originais.
3. O projeto foi reaberto no Power BI Desktop, conferido (navegação, estados dos botões, filtros, interação entre visuais) e salvo como `relatorio_criativo_experiencia_usuario.pbix`.

## Como abrir

Baixe `relatorio_criativo_experiencia_usuario.pbix` e abra no Power BI Desktop. Os dados já estão carregados (Financial Sample). Para navegar pelos botões dentro do Desktop use **Ctrl + clique**.
