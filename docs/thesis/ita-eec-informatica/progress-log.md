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
