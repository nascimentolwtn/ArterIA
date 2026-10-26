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
