# Log de Progresso — Trilha ITA PG/EEC (Informática) — append-only

Status: ativo
Profundidade: completo

> Formato: entradas em ordem cronológica, **mais recente ao final**. Histórico anterior a 2026-10-26 (modo `leve`, mais recente no topo) permanece em `progress.md`, congelado como arquivo histórico.

---

## 2026-10-26 — Marco v1.0: primeira rede real do corredor B; validador expõe a distância entre fixtures e rede real

**Commits:** `72ef5cb` (ADR 0014, WSL2), `25eb78f`/`1d2c6ad`/`ca6b153` (docs de setup), mais alterações ainda não commitadas na data (`arteria/network/build.py`, `cities/sjc/study-areas.yaml`/`.geojson`, `docs/visualization-plan.md`, `CHANGELOG.md` [1.0]). TODO(rastreio): substituir por hash quando o commit existir.

**O que foi feito.** Primeira execução real ponta a ponta no desktop WSL2: `arteria studyarea build` (Nominatim) → `arteria osm fetch --candidate b` → `arteria network build` (`osmium cat` PBF→XML, depois `netconvert`) → `sumo-gui` com 1.800 veículos aleatórios (415 viagens inviáveis descartadas). Apenas o corredor B foi renderizado. Correções: `netconvert` não lê PBF; três consultas Nominatim erradas (uma resolvia ~30 km ao norte); `ARTERIA_DATA` passou a ser `data/` ignorado pelo git. O validador (`arteria network validate`) acusou 729 erros e 7.562 avisos na rede real, em grande parte falsos positivos ou efeito de recorte; 2 erros de `traffic_light_logic` são reais (2 de 18 junções semafóricas), de impacto não verificado.

**Por que importa.** Pela primeira vez a trilha tem um grafo viário real (ainda não medido) e evidência de que a qualidade desse grafo condiciona tudo o que vem depois: observação dos agentes, escolha de nós/arestas da GNN, definição de métricas de acessibilidade. Também mostra que validadores desenvolvidos sobre fixtures não transferem para redes reais, argumento metodológico próprio da dissertação.

**Impacto na tese.**
- Cap. 3 (`chapters/03-arquitetura-do-sistema.md`): novas Seções 3.2 a 3.5 em `rascunho` (construção da rede, validação estrutural real vs. fixtures, rede como grafo e implicações para RL/GNN, proveniência). Status do capítulo: `rascunho` parcial.
- Cap. 4 (`chapters/04-experimentos.md`): Seção 4.2 "Estudo de caso: corredor B" em `rascunho`, explicitamente sem valor probatório.
- Caps. 1, 2, 5, 6, 7: criados como `stub`. `references.bib` iniciado com 5 entradas (SUMO, OSM x2, OSMnx, Tarjan) a conferir.
- `pre-projeto.md`: Seção 9 corrigida (calibração de demanda não mais "a partir da Pesquisa OD", conforme ADR 0013) e riscos de qualidade do grafo adicionados à Seção 12.

**Perguntas abertas/riscos.**
1. Escolha de corredor da dissertação ainda não é decisão acadêmica; B é prioridade de produto. Risco de coincidência por conveniência de engenharia.
2. Rede unificada vs. por corredor altera tamanho do grafo e número de agentes; decisão futura do responsável (talvez ADR).
3. Nenhum número de tamanho da rede foi reportado; nada além das contagens acima foi usado.
4. Risco de a dissertação deslocar-se para "engenharia de dados geoespaciais"; contrapeso: manter RL/GNN como núcleo e tratar a qualidade do grafo como fator experimental (ablações), não como fim.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-26 (2) — Rede única de SJC (ADR 0016), validador adaptado a redes reais, benchmark de hardware

**Commits:** `a55c9d7` (ADR 0016), `72ab33e` (validador), `814f4c9` (benchmark), `ffcbd8e` (smoke real com SUMO); merges `8948351`, `736af5d`, `467ba96`, `e9b9d64`.

**O que foi feito (no repositório).** (i) Redes OSM->SUMO construídas para D, C e A; decisão (ADR 0016, `Accepted`) de usar uma única rede de SJC no envelope de todos os candidatos: 11.035 arestas, 94,0% no maior componente fortemente conexo (individuais: B 2.074/85,1%; D 1.203/69,9%; C 919/86,9%; A 2.256/88,3%), B/D/C/A como áreas de avaliação. (ii) `arteria network validate` reescrito para SCC, pares de arestas opostas e becos de borda; na rede real de B, 729 erros -> 0. (iii) Benchmark do PC: 6c/12t, 9,7 GiB RAM; NSGA-II de 10k execuções estimado em 35-45 h (inviável como planejado); lotes de sementes com 4 trabalhadores. (iv) `nox -s smoke` real passa com SUMO (wheel `eclipse-sumo`); infraestrutura, sem conteúdo de pesquisa, não registrada em capítulo.

**Por que importa.** A rede única fixa o grafo sobre o qual agentes e GNN operarão (ordem de 10^4 arestas) e evita cortar fluxos de passagem via Anel Viário, mas aumenta custo por simulação. O fechamento dos 729 erros mostra que o validador, e não a rede, era a principal fonte de ruído, reforçando o argumento de 3.3 (validação em fixtures não transfere). O benchmark delimita o orçamento de episódios de treinamento e fortalece a motivação do surrogate em GNN.

**Impacto na tese.** Cap. 3: 3.2 reescrita parcial (rede única, tamanhos da ADR) e atualização em 3.3 (`rascunho`). Cap. 4: TODO de 4.2 atualizado e nova 4.2.1 de orçamento computacional (`rascunho`). `outline.md`: duas notas. Demais capítulos inalterados.

**Perguntas abertas/riscos.**
1. Com rede única e quatro áreas, como definir agentes e recompensa (por área, junção ou aresta)? Risco de explosão do espaço de ação em 11 mil arestas.
2. Escolha acadêmica do corredor segue pendente e distinta da prioridade de produto; a rede única pode induzir um escopo de quatro corredores incompatível com um mestrado.
3. Detalhe do `72ab33e` (destino dos 2 erros `traffic_light_logic`; distribuição de componentes) não verificado nesta entrada, apenas a mensagem do commit.
4. Orçamento computacional: MARL com SUMO em 9,7 GiB de RAM é restritivo; decisão de nuvem/nó universitário pendente. Estimativas não medidas.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-27 — Corredores como sequências de arestas na rede unificada; áreas B e C estendidas; desk check de tags OSM (trabalho NÃO commitado; base `b24377a`)

**Commits:** nenhum. Registro do working tree: `cities/sjc/corridors/` (README, `corridors.geojson`, `summary.json`, KML, `build_corridors.py`), `cities/sjc/study-areas.{yaml,geojson}`, `candidate-corridors.md`, `data-manifest.yaml`, ADR 0016, `CHANGELOG.md` [Unreleased]. Itens sujeitos a mudança antes do commit.

**O que foi feito (no repositório, segundo README/CHANGELOG; não reexecutado aqui).**
1. Corredores A, B (derivado), C, D e ligação A-B desenhados como sequências ordenadas de arestas SUMO sobre a rede unificada (ADR 0016), por caminho de menor custo dirigido entre pontos de referência do OSM, roteando cada trecho nos dois sentidos. Exemplo: ligação A-B com 14 arestas/883 m (A para B) e 18 arestas/1.286 m (B para A); nenhum trecho inroteável. A assimetria é atribuída pelo README a rampas de mão única, a partir da geometria OSM.
2. Áreas de estudo estendidas: B de 5,31 para 7,67 km2 (ao sul, Av. Cassiopeia/Av. Perseu) e C de 1,54 para 4,17 km2 (Parque Vicentina Aranha, Av. Rio Branco etc.). Rede unificada reconstruída: 14.225 arestas, 6.655 junções, 93,1% das junções no componente principal, 0 erros de validação (eram 11.035 arestas na ADR 0016 inicial). Ids de arestas mudaram com a reconstrução.
3. Desk check de dados de SJC: completude de tags OSM medida no candidato B: vias principais bem etiquetadas; ruas residenciais com `lanes` em ~4% e `maxspeed` em ~5%. GeoSanja e IBGE NÃO confirmados como fontes disponíveis.
4. SUMO 1.28 carrega a rede real sem avisos; os 2 clusters `traffic_light` sem programa carregam como não semaforizados (inofensivos).
5. Reconciliação do roteiro com a ADR 0014 (WSL2): dev-process, sem conteúdo para a trilha; não registrado em capítulo.

**Ressalvas obrigatórias.** Toda a geometria dos corredores deriva do OSM e AINDA NÃO foi verificada por imagem aérea pelo responsável. O corredor B por arestas é novo (antes só existia o polígono, checado por imagem aérea); não herda aquela verificação. A direção da extensão de C (oeste/sudoeste, não norte) aguarda confirmação do responsável. Nada disso é validação nem escolha acadêmica de corredor; nenhum agente, GNN ou recompensa foi conectado a estes artefatos.

**Por que importa.** (i) Sequências de arestas dão a primeira definição concreta de "corredor" como subgrafo orientado, útil para delimitar observação, ação e recompensa por área (pergunta aberta 1 da entrada anterior) sem tratar 14 mil arestas como espaço de ação. (ii) O desk check (lanes ~4%, maxspeed ~5% em ruas residenciais) indica que atributos de faixa/velocidade serão em grande parte imputados fora das vias principais, afetando as características de aresta da GNN e sendo candidato a fator de ablação (reforça o risco de qualidade do grafo já registrado). (iii) Assimetrias direcionais (883 m vs 1.286 m) são exemplos reais do que a representação em grafo orientado deve preservar.

**Impacto na tese.** `outline.md`: nota no Cap. 3. Prosa de capítulos NÃO alterada: o número 11.035 em `chapters/03` (3.2) e `chapters/04` (TODO de 4.2) está defasado frente a 14.225 e deve ser atualizado após o commit e a resolução das ressalvas, para não consolidar números provisórios.

**Perguntas abertas/riscos.**
1. Agente/recompensa por corredor (subgrafo) versus por junção: decisão de modelagem pendente; risco de quatro corredores excederem o escopo de um mestrado.
2. Os percentuais de 4% e 5% vêm do relato do CHANGELOG, não verificados aqui; metodologia (denominador, escopo) precisa ser citada antes de entrarem no Cap. 3.
3. Sem GeoSanja/IBGE confirmados, atributos de ruas locais serão imputados ou omitidos.
4. Verificação aérea dos corredores e da direção de C pelo responsável pendente; até lá, rascunho. [Resolvida na entrada seguinte, 2026-10-27 (2).]
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-27 (2) — Checagem aérea aprovada; reprodutibilidade da construção da rede (Fase 2; trabalho NÃO commitado; base `0125f01`)

**Commits:** nenhum. Fontes: `CHANGELOG.md` [Unreleased] e `docs/roadmap.md` (Fase 2), lidos; código novo (`arteria/network/{snapshot,rebuild,diff,patches}.py`, `cities/sjc/network/osm-snapshot.yaml`) NÃO lido nem reexecutado; números abaixo são relatos do CHANGELOG.

**O que foi feito.**
1. Checagem aérea do responsável (2026-10-27, Google Earth): corredores A, B, C, D, ligação A-B e áreas estendidas de B e C aprovados, incluindo a extensão de C a oeste/sudoeste. Supera duas ressalvas da entrada anterior (geometria sem imagem aérea; direção de C não confirmada). Números vigentes da rede unificada: 14.225 arestas, 6.655 junções, 93,1% das junções no componente principal (substituem 11.035 arestas/94,0% da ADR 0016 inicial).
2. Reprodutibilidade (Fase 2): snapshot OSM fixado (Geofabrik Sudeste, PBF de 2026-10-25, sha256), `arteria network rebuild` reproduz o hash de conteúdo da rede (cabeçalho de timestamp do `netconvert` ignorado), duas execuções idênticas, 0 erros/127 avisos, ~16 s; patches como segunda passada do `netconvert` (nenhum necessário ainda); `arteria network diff` (demonstração: B isolada vs. unificada, 12.175 arestas adicionadas/24 removidas/137 alteradas). Teste de desktop confirma que todas as arestas dos corredores existem na rede. Nenhum GTFS público de SJC encontrado: P2.6 adiada.

**Por que importa.** Ids de aresta estáveis e reconstruíveis são pré-condição de qualquer ambiente de RL/GNN sobre o grafo (baseline, demanda e calibração dependem deles; ADR 0016). A falta de GTFS implica que a rede não terá ônibus por ora, restringindo intervenções de faixa de ônibus/prioridade semafórica, correlatas e não centrais ao escopo; o objeto estrutural (faixas/sentidos) não é afetado de imediato.

**Impacto na tese.** Cap. 3: 3.2 (atualização de tamanhos, corredores, aprovação aérea) e 3.5 (mecanismo de reprodutibilidade) em `rascunho`, via anexos; texto antigo preservado como histórico. Cap. 4: dois trechos de 4.2 sinalizados como defasados/atualizados. `outline.md`: notas no Cap. 3. Demais capítulos inalterados.

**Perguntas abertas/riscos.**
1. As frações 94,0% (arestas, ADR 0016) e 93,1% (junções, relato atual) usam unidades distintas; não comparar sem verificar o validador.
2. Formato do registro de proveniência do `rebuild` e relação com `RunManifest` não verificados; reprodutibilidade cobre só a construção da rede, não treinamento/simulação.
3. Sem GTFS, nenhuma demanda/rota de transporte público; decisão de fonte alternativa (rotas manuais) pendente do responsável.
4. Todo o material está no working tree; se mudar antes do commit, os anexos precisam de revisão.
5. Agente/recompensa por corredor versus junção segue sem decisão; escopo de quatro corredores pode exceder um mestrado. Orientador(a) não contatado(a).

---

## 2026-10-28 — Cross-check da rede OSM contra IBGE e GeoSanja (P2.1, P2.7); resolve lacuna de fontes de atributo de rua

**Commits:** `1c4a7b4` ("feat: cross-check SJC network against IBGE and GeoSanja (P2.1, P2.7)"). Números abaixo são relato repassado pelo responsável do ArterIA, não reexecutados nem lidos em código nesta sessão; caminhos confirmados por existirem no repositório (`arteria/network/crosscheck.py`, `arteria/network/render.py`, `cities/sjc/data-manifest.yaml`). TODO(evidência): ler `crosscheck.py` e reexecutar o comando antes de citar os números como fato assentado no capítulo.

**O que foi feito.** Dois novos comandos (`arteria network crosscheck --city sjc`, `arteria network render --city sjc`) comparam a rede SUMO/OSM construída (14.225 arestas, ver entrada 2026-10-27 (2)) contra duas fontes públicas de referência registradas em `cities/sjc/data-manifest.yaml`: Base de Faces de Logradouros do IBGE (2022, shapefile estadual) e as camadas `arruamentos`/Hierarquia Viária do GeoSanja (portal da prefeitura de SJC). O cross-check é restrito aos quatro corredores do estudo (buffer de 50 m em torno da união dos polígonos) e compara por nome de rua normalizado (contra IBGE) e por geometria/cobertura de centro de linha amostrado a cada 5 m (contra IBGE e GeoSanja, limiar de 15 m). Relato de resultados (não commitados; saídas gitignored em `data/crosscheck/` e `data/renders/`): 543 nomes de rua coincidentes dentro dos corredores (167 só-OSM, 201 só-IBGE); distância mediana amostra-referência ~3,0 m; 6,4% das amostras acima de 15 m; 81,5% do comprimento OSM dentro de 15 m do GeoSanja e 97,2% do GeoSanja dentro de 15 m do OSM. Parte dos descasamentos de distância alta é atribuída a nomes de rua genéricos/reutilizados (ex. "Rua Dois", "Viela Três") que casam por nome entre ruas distintas, não a erro de geometria. Renders de mapa (rede colorida por prioridade de aresta do SUMO, com os quatro contornos de área de estudo) também foram gerados, não commitados. Questão nova e ainda não corrigida: nomes de rua OSM na rede construída carregam um artefato de escape duplo de `&apos;` (afetando algumas dezenas de nomes com apóstrofo, ex. "D'Ávila"), origem suspeita no `netconvert` ou depois, não diagnosticada.

**Por que importa.** Resolve, com dados concretos, a lacuna registrada em duas entradas anteriores deste log ("GeoSanja e IBGE NÃO confirmados como fontes disponíveis", 2026-10-27) e no `outline.md` (Cap. 4: "apenas a topologia da malha viária tem fonte de autoatendimento confirmada [OSM/Geosanja/IBGE]" — agora com número de fato, não apenas fonte listada em manifesto). É o primeiro cross-check quantitativo da completude/precisão geométrica do grafo derivado de OSM contra fontes públicas independentes, pré-condição direta do Objetivo específico 1 (representação em grafo) e do argumento central de 3.3/3.4 (qualidade do grafo OSM condiciona observação, ação e GNN). Os números (81,5-97,2% de cobertura geométrica dentro de 15 m; ~37% dos nomes só-OSM ou só-IBGE) dão, por ora, a primeira medida substituta de completude referida como `TODO(citação)` em 3.3 (`haklay2010osm`/`barrington2017osm`), embora não substituam a literatura de qualidade do OSM, apenas a complementem com um dado local. O próprio commit e o relato o classificam como cross-check de triagem (casamento de nome não ajustado fino), não etapa de calibração — distinção que a dissertação deve preservar: não é validação de atributos de faixa/sentido (lanes/maxspeed, ainda ~4%/~5% em ruas residenciais segundo a entrada de 2026-10-27), apenas de nome e geometria de via.

**Impacto na tese.** Cap. 3 (`chapters/03-arquitetura-do-sistema.md`): nova atualização a registrar em 3.3 (cross-check como segunda camada de verificação, além do validador estrutural) e em 3.4 (completude do OSM, ponto 5, agora com número local além da citação genérica) — texto do capítulo ainda não editado nesta sessão, TODO para a próxima revisão de prosa. `outline.md`: notas do Cap. 3 e do Cap. 4 (linha sobre fonte confirmada de topologia) a atualizar para refletir que a confirmação de disponibilidade já ocorreu, com número associado.

**Perguntas abertas/riscos.**
1. Cross-check não cobre atributos estruturais (faixas, sentido, restrições de giro) — apenas nome e geometria do eixo da via; o risco de qualidade de `lanes`/`maxspeed` registrado em 2026-10-27 permanece integralmente aberto.
2. ~~Artefato de escape duplo (`&apos;`) em nomes de rua com apóstrofo~~ — **resolvido em `1895aeb`, ver addendum abaixo (2026-10-28 (2)).**
3. Os descasamentos de mediana alta por nomes genéricos reutilizados ("Rua Dois") sugerem que casamento por nome tem limite estrutural nesta malha; qualquer uso futuro desse cross-check como insumo de qualidade de dado (não apenas triagem) precisaria de casamento por nome+geometria conjunto, não nome isolado.
4. Números não verificados em código nesta sessão (apenas repassados); antes de citar no capítulo como fato, reexecutar `arteria network crosscheck --city sjc` e ler `crosscheck.py`.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada; escolha acadêmica de corredor segue pendente.

---

## 2026-10-28 (2) — Addendum: artefato de escape duplo diagnosticado e corrigido (risco 2 acima resolvido)

**Commit:** `1895aeb` ("fix: undo netconvert's double-escaping of names"), CHANGELOG [1.3].

**O que foi feito.** Causa raiz confirmada por fixture OSM mínima de duas vias contra o binário real do `netconvert` 1.28.0: o `netconvert` escapa duplamente qualquer caractere especial de XML literal (`'`, `&`, `"`, `<`, `>`) presente numa tag `name` do OSM — primeiro substitui o caractere pela entidade XML nomeada internamente, depois seu próprio escritor de saída escapa o `&` dessa entidade de novo (ex. apóstrofo vira `&amp;apos;`). Bug do próprio `netconvert`/SUMO, não erro de lógica do ArterIA. `arteria.network.build.fix_double_escaped_names()` agora roda automaticamente após toda chamada de `netconvert` em `build_network`, corrigindo os atributos `name`/`origId` no `.net.xml` escrito; testes novos cobrem a função isolada, um caso no-op e um teste de ponta a ponta com fixture reproduzindo o padrão. A rede real de SJC foi reconstruída com a correção e o snapshot OSM fixado (`cities/sjc/network/osm-snapshot.yaml`) foi repontado para o hash de conteúdo da rede corrigida: 58 caracteres corrigidos em exatamente 3 nomes de rua (ex. "Rua Armando D'Oliveira Cobra", antes "Rua Armando D&amp;apos;Oliveira Cobra"); estrutura da rede inalterada (0 arestas/faixas/junções adicionadas, removidas ou alteradas; validação ainda 0 erros, 127 avisos). O cross-check de `1c4a7b4` foi reexecutado contra a rede corrigida: nomes coincidentes com IBGE 543→544 (um dos três nomes corrigidos agora casa corretamente), só-OSM 167→166, só-IBGE 201→200; números de geometria (mediana ~3,0 m, 6,4% acima de 15 m, 81,5%/97,2% de cobertura GeoSanja) essencialmente inalterados.

**Por que importa.** Fecha, com causa raiz identificada e correção automática aplicada (não apenas contorno manual), o risco 2 registrado na entrada anterior (2026-10-28) e já citado em `chapters/03-arquitetura-do-sistema.md` (3.3) como "achado colateral ainda não corrigido". Nomes de rua em `sjc.net.xml` podem agora ser citados diretamente em figuras/tabelas/texto sem o artefato de apóstrofo — relevante porque a nota de 3.3 havia marcado explicitamente esse artefato como impeditivo para qualquer uso futuro de nome de rua como chave de junção com dados de calibração/contagem municipal.

**Impacto na tese.** `chapters/03-arquitetura-do-sistema.md`, 3.3 (nota de `1c4a7b4`, trecho final): acrescentada uma frase registrando a correção e os novos totais (544/166/200), sem reescrever o restante da nota. `outline.md`: nota do Cap. 3 (2026-10-28, `1c4a7b4`) marcada como superada neste ponto específico.

**Perguntas abertas/riscos.**
1. Os três nomes afetados e o novo total 544/166/200 não foram verificados em código nesta sessão (apenas repassados do CHANGELOG); mesma ressalva já registrada para os números de `1c4a7b4` — reexecutar `crosscheck.py` antes de consolidar na prosa.
2. `fix_double_escaped_names()` cobre `'`, `&`, `"`, `<`, `>`; não verificado se há outros caracteres de nome de rua (acentos/Unicode fora do conjunto de escape XML) sujeitos a problema semelhante — lacuna de verificação desta trilha, não hipótese levantada pelo commit.
3. Orientador(a) não contatado(a); arquitetura de agentes não validada; escolha acadêmica de corredor segue pendente.
