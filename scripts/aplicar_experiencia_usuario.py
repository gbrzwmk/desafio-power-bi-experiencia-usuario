"""Desafio 7 (Experiência do usuário) — parte do projeto PBIP exportado do 'relatório criativo' e:
 - adiciona medidas DAX ao modelo (financials.tmdl)
 - reconstrói as páginas Profit e Report no mesmo padrão visual da página Sales
   (faixa lateral, logo, título com sublinhado, cartões, painéis arredondados, filtro no topo)
 - coloca o menu de navegação (navegador de páginas com estados padrão / focalizar / pressionar / selecionado)
   e as setas de avançar/voltar em todas as páginas
Uso: python3 build7.py <pbip_orig> <pbip_out>"""
import copy, json, os, sys, shutil, random

_rng = random.Random(7)
hex10 = lambda: "%020x" % _rng.getrandbits(80)
src, out = sys.argv[1], sys.argv[2]
if os.path.exists(out):
    shutil.rmtree(out)
shutil.copytree(src, out, ignore=shutil.ignore_patterns(".pbi"))
J = lambda o: json.dumps(o, ensure_ascii=False, indent=2)
rep = os.path.join(out, "relatorio_criativo.Report", "definition")
sm = os.path.join(out, "relatorio_criativo.SemanticModel", "definition")

SALES, PROFIT, REPORT = "ReportSection", "ReportSection97cbc83821537e2e2f6e", "ReportSectionb1b39f30add9200534cd"

# ------------------------------------------------------------------ 1. medidas DAX
MEASURES = [
    ("Total Sales", "SUM(financials[ Sales])", "#,0.00"),
    ("Total Profit", "SUM(financials[Profit])", "#,0.00"),
    ("Margem de Lucro", "DIVIDE([Total Profit], [Total Sales])", "0.0%"),
    ("Vendas Brutas", "SUM(financials[Gross Sales])", "#,0.00"),
    ("Total de Descontos", "SUM(financials[Discounts])", "#,0.00"),
    ("Unidades Vendidas", "SUM(financials[Units Sold])", "#,0"),
    ("Ticket Médio", "DIVIDE([Total Sales], COUNTROWS(financials))", "#,0.00"),
    ("Lucro Ano Anterior", "CALCULATE([Total Profit], SAMEPERIODLASTYEAR(financials[Date]))", "#,0.00"),
    ("Variação Lucro vs Ano Anterior", "DIVIDE([Total Profit] - [Lucro Ano Anterior], [Lucro Ano Anterior])", "0.0%"),
]
tmdl_path = os.path.join(sm, "tables", "financials.tmdl")
tmdl = open(tmdl_path, encoding="utf-8").read()
block = ""
for name, expr, fmt in MEASURES:
    block += f"\tmeasure '{name}' = {expr}\n\t\tformatString: {fmt}\n\t\tlineageTag: {hex10()[:8]}-{hex10()[:4]}-4{hex10()[:3]}-a{hex10()[:3]}-{hex10()[:12]}\n\n"
tmdl = tmdl.replace("\tcolumn Segment\n", block + "\tcolumn Segment\n", 1)
open(tmdl_path, "w", encoding="utf-8", newline="\n").write(tmdl)

# ------------------------------------------------------------------ helpers PBIR
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json"
lit = lambda v: {"expr": {"Literal": {"Value": v}}}
theme = lambda cid, pct=0: {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": cid, "Percent": pct}}}}}
WHITE, NAVY = theme(0, 0), theme(3, -0.5)
F = "financials"

def col(prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": F}}, "Property": prop}}
def agg(prop, fn=0):
    return {"Aggregation": {"Expression": col(prop), "Function": fn}}
def mea(prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": F}}, "Property": prop}}
def hier(level):
    return {"HierarchyLevel": {"Expression": {"Hierarchy": {"Expression": {"PropertyVariationSource": {
        "Expression": {"SourceRef": {"Entity": F}}, "Name": "Variation", "Property": "Date"}}, "Hierarchy": "Hierarquia de datas"}}, "Level": level}}

def field(f, active=True):
    """(prop, kind, displayName) -> projection. kind: None=coluna, 'Sum', 'M'=medida, 'H'=nível da hierarquia de datas"""
    prop, kind, disp = f
    if kind == "M":
        p = {"field": mea(prop), "queryRef": f"{F}.{prop}"}
    elif kind == "Sum":
        p = {"field": agg(prop, 0), "queryRef": f"Sum({F}.{prop})"}
    elif kind == "H":
        p = {"field": hier(prop), "queryRef": f"{F}.Date.Variation.Hierarquia de datas.{prop}"}
    else:
        p = {"field": col(prop), "queryRef": f"{F}.{prop}"}
    if kind != "Sum" and kind != "M":
        p["active"] = active
    if disp:
        p["displayName"] = disp
    return p

def container(x, y, w, h, z, visual, name=None, parent=None):
    j = {"$schema": VC_SCHEMA, "name": name or hex10(),
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}, "visual": visual}
    if parent:
        j["parentGroupName"] = parent
    return j

def group(x, y, w, h, z, display, name=None):
    return {"$schema": VC_SCHEMA, "name": name or hex10(),
            "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
            "visualGroup": {"displayName": display, "groupMode": "ScaleMode"}}

def template(page, name):
    """copia um visual existente da página Sales para reaproveitar exatamente a mesma formatação"""
    return copy.deepcopy(json.load(open(os.path.join(src, "relatorio_criativo.Report", "definition", "pages", page, "visuals", name, "visual.json"), encoding="utf-8")))

def place(j, x, y, w, h, z, parent=None, name=None):
    j["name"] = name or hex10()
    j["position"] = {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}
    j.pop("parentGroupName", None)
    if parent:
        j["parentGroupName"] = parent
    return j

TITLE = lambda text, size=19: {"title": [{"properties": {"show": lit("true"), "text": lit("'" + text + "'"), "alignment": lit("'center'"),
                                                          "fontSize": lit(f"{size}D"), "fontColor": theme(2, -0.5)}}],
                               "background": [{"properties": {"show": lit("false")}}]}

def visual(vt, roles, objects=None, ttl=None, sort=None, extra=None):
    qs = {role: {"projections": [field(f) if not isinstance(f, dict) else f for f in fields]} for role, fields in roles.items()}
    v = {"visualType": vt, "query": {"queryState": qs}, "drillFilterOtherVisuals": True}
    if sort:
        f, direction = sort
        v["query"]["sortDefinition"] = {"sort": [{"field": field(f)["field"], "direction": direction}], "isDefaultSort": True}
    if objects:
        v["objects"] = objects
    v["visualContainerObjects"] = ttl if ttl else {"background": [{"properties": {"show": lit("false")}}]}
    if extra:
        v.update(extra)
    return v

def textbox(x, y, w, h, z, text, size, parent=None, bold=True):
    st = {"fontSize": f"{size}pt"}
    if bold:
        st["fontWeight"] = "bold"
    return container(x, y, w, h, z, {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": st}]}]}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": lit("false")}}]},
        "drillFilterOtherVisuals": True}, parent=parent)

def card(x, y, w, h, z, f, parent):
    v = visual("card", {"Values": [f]},
               objects={"labels": [{"properties": {"fontSize": lit("30D"), "color": WHITE}}],
                        "categoryLabels": [{"properties": {"color": WHITE}}]})
    return container(x, y, w, h, z, v, parent=parent)

def arrow(x, y, w, h, z, shape_type, target, tooltip, name=None):
    """seta de navegação com estados: padrão (ícone branco), focalizar (fundo azul claro), pressionar (fundo branco, ícone azul-marinho)"""
    v = {"visualType": "actionButton",
         "objects": {
             "icon": [{"properties": {"shapeType": lit(f"'{shape_type}'"), "lineColor": WHITE}, "selector": {"id": "default"}},
                      {"properties": {"lineColor": WHITE}, "selector": {"id": "hover"}},
                      {"properties": {"lineColor": NAVY}, "selector": {"id": "press"}}],
             "fill": [{"properties": {"show": lit("true")}},
                      {"properties": {"fillColor": NAVY, "transparency": lit("0D")}, "selector": {"id": "default"}},
                      {"properties": {"fillColor": theme(3, 0.6), "transparency": lit("0D")}, "selector": {"id": "hover"}},
                      {"properties": {"fillColor": WHITE, "transparency": lit("0D")}, "selector": {"id": "press"}}],
             "outline": [{"properties": {"show": lit("false")}}],
             "shape": [{"properties": {"roundEdge": lit("10L")}, "selector": {"id": "default"}}]},
         "visualContainerObjects": {
             "visualLink": [{"properties": {"show": lit("true"), "type": lit("'PageNavigation'"),
                                            "navigationSection": lit("'" + target + "'"), "tooltip": lit("'" + tooltip + "'")}}],
             "title": [{"properties": {"text": lit("'Botão - " + tooltip + "'")}}]},
         "drillFilterOtherVisuals": True}
    return container(x, y, w, h, z, v, name=name)

def write_visual(page_id, vc):
    d = os.path.join(rep, "pages", page_id, "visuals", vc["name"])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "visual.json"), "w", encoding="utf-8", newline="\n").write(J(vc))

# ------------------------------------------------------------------ 2. página Sales: a seta 'Next' ganha os estados focalizar/pressionar
write_visual(SALES, arrow(25, 668, 49, 40, 1000, "rightArrow", PROFIT, "Ir para Profit", name="08267e9539ad8f50f5c5"))

# ------------------------------------------------------------------ 3. esqueleto comum das páginas Profit e Report (igual à página Sales)
def skeleton(page_id, title_text, cards, filter_label, prev_page, next_page):
    V = []
    # faixa lateral + logo + ilustração (grupo Layout)
    g = group(0, 0, 511, 720, 0, "Layout"); V.append(g)
    V.append(place(template(SALES, "01b7ce94cde287aa2be1"), 0, 13, 96, 706, 0, parent=g["name"]))       # faixa azul-marinho
    V.append(place(template(SALES, "460066522faed2afc978"), 0, 36, 98, 63, 1000, parent=g["name"]))      # logo DIO
    V.append(place(template(SALES, "5a663c95b41165a98280"), 380, 0, 188, 141, 1000, parent=g["name"]))   # ilustração (à direita do título)
    # navegador de páginas com estados (mesma formatação da página Sales)
    V.append(place(template(SALES, "742d72c14bd8736a2e87"), 13, 211, 69, 306, 10000))
    # setas voltar / avançar na base da faixa
    if prev_page and next_page:
        V.append(arrow(6, 668, 40, 40, 11000, "leftArrow", prev_page, "Página anterior"))
        V.append(arrow(50, 668, 40, 40, 11000, "rightArrow", next_page, "Próxima página"))
    elif prev_page:
        V.append(arrow(25, 668, 49, 40, 11000, "leftArrow", prev_page, "Página anterior"))
    # título com sublinhado
    g = group(120, 43, 300, 74, 5000, "Title report"); V.append(g)
    V.append(textbox(0, 0, 300, 48, 1000, title_text, 24, parent=g["name"]))
    V.append(place(template(SALES, "f3924bba811944330ea8"), 3, 41, 296, 33, 0, parent=g["name"]))
    # cartões em caixas azul-marinho arredondadas
    g = group(147, 141, 410, 107, 2000, "Cartões"); V.append(g)
    for i, f in enumerate(cards):
        V.append(place(template(SALES, "da5393f03ea79871375e"), i * 208, 1, 201, 106, 0, parent=g["name"]))
        V.append(card(14 + i * 208, 0, 162, 107, 2000, f, parent=g["name"]))
    # painéis cinza arredondados à direita
    V.append(place(template(SALES, "4710efc327da5c16daad"), 584, 117, 640, 590, 3000))
    V.append(place(template(SALES, "72acccaba181720e003d"), 640, 108, 609, 612, 4000))
    # filtro no topo direito: texto + segmentação de ano em blocos
    g = group(661, 38, 551, 55, 6000, "Filtro por ano"); V.append(g)
    V.append(textbox(0, 6, 200, 46, 1000, filter_label, 18, parent=g["name"]))
    slicer = visual("slicer", {"Values": [("Year", None, None)]},
                    objects={"data": [{"properties": {"mode": lit("'Basic'")}}],
                             "general": [{"properties": {"orientation": lit("1D")}}],
                             "header": [{"properties": {"show": lit("false")}}],
                             "items": [{"properties": {"fontSize": lit("14D"), "background": theme(0, 0), "fontColor": theme(1, 0)}}],
                             "selection": [{"properties": {"singleSelect": lit("false"), "selectAllCheckboxEnabled": lit("false")}}]},
                    ttl={"background": [{"properties": {"show": lit("true")}}]},
                    sort=(("Year", None, None), "Ascending"))
    V.append(container(205, 0, 272, 55, 0, slicer, parent=g["name"]))
    return V

def clear_page(page_id):
    d = os.path.join(rep, "pages", page_id, "visuals")
    shutil.rmtree(d)
    os.makedirs(d)

# ------------------------------------------------------------------ 4. página Profit
clear_page(PROFIT)
V = skeleton(PROFIT, "Profit Report", [("Total Profit", "M", "Lucro Total"), ("Margem de Lucro", "M", "Margem de Lucro")],
             "Selecione o ano", SALES, REPORT)
# árvore de decomposição do lucro (visual original da página, reposicionado e com título)
g = group(120, 261, 478, 445, 7000, "Análise do lucro"); V.append(g)
tree = template(PROFIT, "2f0ab885269666fab4e1")
tree["visual"]["visualContainerObjects"] = TITLE("Decomposição do lucro")
tree["visual"]["objects"].pop("insights", None)   # referenciava uma tabela de datas que não existe mais
V.append(place(tree, 0, 0, 478, 445, 0, parent=g["name"]))
# cascata por trimestre
wf = visual("waterfallChart", {"Category": [("Trimestre", "H", None)], "Y": [("Total Profit", "M", None)]},
            objects={"categoryAxis": [{"properties": {"fontSize": lit("10D"), "showAxisTitle": lit("false")}}],
                     "valueAxis": [{"properties": {"fontSize": lit("10D"), "labelDisplayUnits": lit("1000000D"), "showAxisTitle": lit("false")}}],
                     "labels": [{"properties": {"show": lit("true"), "fontSize": lit("10D")}}],
                     "legend": [{"properties": {"position": lit("'Top'"), "fontSize": lit("10D")}}],
                     "sentimentColors": [{"properties": {"increaseFill": theme(2, 0), "decreaseFill": theme(4, 0), "totalFill": NAVY}}]},
            ttl=TITLE("Lucro por trimestre"))
V.append(container(661, 150, 539, 250, 8000, wf))
# treemap por segmento
tm = visual("treemap", {"Group": [("Segment", None, None)], "Values": [("Total Profit", "M", None)]},
            objects={"dataPoint": [{"properties": {}}] + [
                {"properties": {"fill": theme(3, p)}, "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col("Segment"), "Right": {"Literal": {"Value": f"'{s}'"}}}}}]}}
                for s, p in [("Government", -0.5), ("Small Business", -0.25), ("Enterprise", 0.2), ("Midmarket", 0.4), ("Channel Partners", 0.6)]],
                     "labels": [{"properties": {"show": lit("true"), "fontSize": lit("10D"), "color": WHITE}}],
                     "categoryLabels": [{"properties": {"show": lit("true"), "fontSize": lit("10D"), "color": WHITE}}],
                     "legend": [{"properties": {"show": lit("false")}}]},
            ttl=TITLE("Lucro por segmento"))
V.append(container(661, 415, 262, 285, 9000, tm))
# barras: lucro por produto (substitui o RadarChart, visual personalizado que não vem instalado)
pb = visual("clusteredBarChart", {"Category": [("Product", None, None)], "Y": [("Total Profit", "M", None)]},
            objects={"dataPoint": [{"properties": {"fill": theme(3, -0.25)}}],
                     "categoryAxis": [{"properties": {"fontSize": lit("10D"), "innerPadding": lit("17L"), "showAxisTitle": lit("false")}}],
                     "valueAxis": [{"properties": {"show": lit("false"), "showAxisTitle": lit("false")}}],
                     "labels": [{"properties": {"show": lit("true"), "fontSize": lit("10D")}}]},
            ttl=TITLE("Lucro por produto"), sort=(("Total Profit", "M", None), "Descending"))
V.append(container(938, 415, 262, 285, 9000, pb))
for vc in V:
    write_visual(PROFIT, vc)

# ------------------------------------------------------------------ 5. página Report
clear_page(REPORT)
V = skeleton(REPORT, "Detailed Report", [("Vendas Brutas", "M", "Vendas Brutas"), ("Total de Descontos", "M", "Total de Descontos")],
             "Selecione o ano", PROFIT, None)
# vendas e lucro por período + matriz ano x trimestre (visuais originais da página, reposicionados)
g = group(120, 261, 478, 445, 7000, "Detalhes venda x profit"); V.append(g)
area = template(REPORT, "984e7540c84039085716")
area["visual"]["visualContainerObjects"] = TITLE("Vendas e Lucro por Período")
area["visual"]["objects"]["categoryAxis"] = [{"properties": {"fontSize": lit("10D"), "showAxisTitle": lit("false")}}]
area["visual"]["objects"]["valueAxis"] = [{"properties": {"fontSize": lit("10D"), "labelDisplayUnits": lit("1000000D"), "showAxisTitle": lit("false")}}]
area["visual"]["objects"]["legend"] = [{"properties": {"position": lit("'Top'"), "fontSize": lit("10D")}}]
V.append(place(area, 0, 0, 478, 255, 0, parent=g["name"]))
pivot = template(REPORT, "6df5afb05182580ccb34")
po = pivot["visual"]["objects"]
po["columnHeaders"][0]["properties"].update({"fontSize": lit("12D"), "backColor": theme(3, -0.25)})
po["rowHeaders"][0]["properties"].update({"fontSize": lit("12D"), "backColor": theme(3, 0.2)})
po["values"][0]["properties"]["fontSize"] = lit("12D")
po["subTotals"] = [{"properties": {"fontSize": lit("12D")}, "selector": {"id": "Column"}}, {"properties": {"fontSize": lit("12D")}, "selector": {"id": "Row"}}]
pivot["visual"]["visualContainerObjects"] = {"background": [{"properties": {"show": lit("false")}}], "stylePreset": [{"properties": {"name": lit("'None'")}}],
                                              "title": [{"properties": {"show": lit("true"), "text": lit("'Lucro por ano e trimestre'"), "alignment": lit("'center'"), "fontSize": lit("14D"), "fontColor": theme(2, -0.5)}}]}
V.append(place(pivot, 0, 265, 478, 180, 0, parent=g["name"]))
# combo vendas e gross x período (visual original, fontes reduzidas)
combo = template(REPORT, "b5dfc92b5504175ea6d0")
co = combo["visual"]["objects"]
co["labels"][1]["properties"]["fontSize"] = lit("10D")
co["categoryAxis"] = [{"properties": {"fontSize": lit("10D"), "showAxisTitle": lit("false")}}]
co["valueAxis"] = [{"properties": {"fontSize": lit("10D"), "labelDisplayUnits": lit("1000000D"), "secShow": lit("false"), "showAxisTitle": lit("false")}}]
co["legend"] = [{"properties": {"position": lit("'Top'"), "fontSize": lit("10D")}}]
combo["visual"]["visualContainerObjects"] = TITLE("Vendas e Gross x Período")
V.append(place(combo, 661, 150, 539, 300, 8000))
# barras: vendas por país
cb = visual("clusteredBarChart", {"Category": [("Country", None, None)], "Y": [("Total Sales", "M", None)]},
            objects={"dataPoint": [{"properties": {"fill": theme(3, -0.25)}}],
                     "categoryAxis": [{"properties": {"fontSize": lit("10D"), "innerPadding": lit("17L"), "showAxisTitle": lit("false")}}],
                     "valueAxis": [{"properties": {"show": lit("false"), "showAxisTitle": lit("false")}}],
                     "labels": [{"properties": {"show": lit("true"), "fontSize": lit("10D"), "labelDisplayUnits": lit("1000000D")}}]},
            ttl=TITLE("Vendas por país"), sort=(("Total Sales", "M", None), "Descending"))
V.append(container(661, 465, 539, 235, 9000, cb))
for vc in V:
    write_visual(REPORT, vc)

# ------------------------------------------------------------------ 6. página ativa ao abrir = Sales
pj = os.path.join(rep, "pages", "pages.json")
pages = json.load(open(pj, encoding="utf-8"))
pages["activePageName"] = SALES
open(pj, "w", encoding="utf-8", newline="\n").write(J(pages))
print("ok")
