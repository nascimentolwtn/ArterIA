# Log de Progresso — Trilha ITA PG/EEC (Informática) — append-only

Status: ativo
Profundidade: completo

> Formato: entradas em ordem cronológica, **mais recente ao final**. Histórico anterior a 2026-10-26 (modo `leve`, mais recente no topo) permanece em `progress.md`, congelado como arquivo histórico.

---

## 2026-10-26 — Marco v1.0: primeira rede real do corredor B; validador expõe a distância entre fixtures e rede real

**Commits:** `72ef5cb` (ADR 0014, WSL2), `25eb78f`/`1d2c6ad`/`ca6b153` (docs de setup), mais alterações ainda não commitadas na data (`arteria/network/build.py`, `cities/sjc/study-areas.yaml`/`.geojson`, `docs/visualization-plan.md`, `CHANGELOG.md` [1.0]). TODO(rastreio): substituir por hash quando o commit existir.

**O que foi feito.** A equipe fez a primeira execução real de ponta a ponta no desktop WSL2. A sequência foi: `arteria studyarea build` (Nominatim) → `arteria osm fetch --candidate b` → `arteria network build` (`osmium cat` converte PBF para XML, depois roda o `netconvert`) → `sumo-gui` com 1.800 veículos aleatórios. O sistema descartou 415 viagens inviáveis. Apenas o corredor B foi renderizado.

A execução precisou de três correções. O `netconvert` não lê arquivos PBF. Três consultas ao Nominatim estavam erradas (uma delas resolvia um ponto ~30 km ao norte do correto). A variável `ARTERIA_DATA` passou a apontar para `data/`, pasta ignorada pelo git.

O validador (`arteria network validate`) acusou 729 erros e 7.562 avisos na rede real. A maioria é falso positivo ou efeito de recorte. Mas 2 erros de `traffic_light_logic` são reais (2 de 18 junções semafóricas). O impacto desses 2 erros ainda não foi verificado.

**Por que importa.** Pela primeira vez, a trilha tem um grafo viário real. Esse grafo ainda não foi medido. Já há evidência de que a qualidade do grafo condiciona tudo o que vem depois: a observação dos agentes, a escolha de nós e arestas da GNN, e a definição de métricas de acessibilidade.

Além disso, o caso mostra que um validador feito sobre fixtures não funciona do mesmo jeito numa rede real. Esse é um argumento metodológico próprio da dissertação.

**Impacto na tese.** No Cap. 3 (`chapters/03-arquitetura-do-sistema.md`), a equipe criou as novas Seções 3.2 a 3.5. Elas ficaram em `rascunho` (construção da rede, validação estrutural real vs. fixtures, rede como grafo e implicações para RL/GNN, proveniência). O capítulo ficou com status `rascunho` parcial.

No Cap. 4 (`chapters/04-experimentos.md`), a Seção 4.2 ("Estudo de caso: corredor B") entrou em `rascunho`. Essa seção ainda não tem valor probatório.

Os Caps. 1, 2, 5, 6 e 7 foram criados como `stub`. O `references.bib` começou com 5 entradas (SUMO, OSM x2, OSMnx, Tarjan), ainda a conferir.

No `pre-projeto.md`, a Seção 9 foi corrigida: a calibração de demanda não vem mais "a partir da Pesquisa OD", conforme a ADR 0013. Os riscos de qualidade do grafo foram adicionados à Seção 12.

**Perguntas abertas/riscos.**
1. A escolha do corredor da dissertação ainda não é decisão acadêmica. B é prioridade de produto, não escolha acadêmica. Há risco de a escolha acadêmica coincidir com B só por conveniência de engenharia.
2. Rede unificada ou rede por corredor: a escolha muda o tamanho do grafo e o número de agentes. Essa decisão ainda é futura, do responsável (talvez vire ADR).
3. Ninguém reportou o tamanho da rede. Só as contagens já citadas acima foram usadas.
4. Há risco de a dissertação deslizar para "engenharia de dados geoespaciais". Como contrapeso, o núcleo continua sendo RL/GNN. A qualidade do grafo é tratada como fator experimental (ablações), não como objetivo final.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes ainda não foi validada.

---

## 2026-10-26 (2) — Rede única de SJC (ADR 0016), validador adaptado a redes reais, benchmark de hardware

**Commits:** `a55c9d7` (ADR 0016), `72ab33e` (validador), `814f4c9` (benchmark), `ffcbd8e` (smoke real com SUMO); merges `8948351`, `736af5d`, `467ba96`, `e9b9d64`.

**O que foi feito (no repositório).** A equipe construiu redes OSM→SUMO para D, C e A. Em seguida, decidiu (ADR 0016, `Accepted`) usar uma única rede de SJC, que cobre o envelope de todos os candidatos. Essa rede única tem 11.035 arestas, com 94,0% no maior componente fortemente conexo. Os números individuais por candidato são: B 2.074 arestas/85,1%; D 1.203 arestas/69,9%; C 919 arestas/86,9%; A 2.256 arestas/88,3%. B, D, C e A passam a ser as áreas de avaliação.

Depois, a equipe reescreveu o `arteria network validate`. O validador novo checa componente fortemente conexo (SCC), pares de arestas opostas e becos de borda. Na rede real de B, os erros caíram de 729 para 0.

O benchmark do PC (6 núcleos/12 threads, 9,7 GiB de RAM) estimou um NSGA-II de 10 mil execuções em 35 a 45 horas. Esse tempo é inviável como planejado. Por isso, a equipe adotou lotes de sementes com 4 trabalhadores.

Por fim, o `nox -s smoke` real passa com SUMO (wheel `eclipse-sumo`). Isso é infraestrutura, sem conteúdo de pesquisa, e não foi registrado em nenhum capítulo.

**Por que importa.** A rede única fixa o grafo sobre o qual agentes e GNN vão operar (ordem de 10^4 arestas). Ela evita cortar fluxos de passagem pelo Anel Viário. Em troca, aumenta o custo de cada simulação.

O fechamento dos 729 erros mostra algo importante: o validador, não a rede, era a principal fonte de ruído. Isso reforça o argumento da Seção 3.3 (um validador feito sobre fixtures não se transfere para uma rede real).

O benchmark, por fim, delimita o orçamento de episódios de treinamento. Ele também fortalece a motivação de usar um substituto (surrogate) em GNN.

**Impacto na tese.** No Cap. 3, a Seção 3.2 foi parcialmente reescrita, com a rede única e os tamanhos da ADR. A Seção 3.3 recebeu atualização, em `rascunho`.

No Cap. 4, o TODO da Seção 4.2 foi atualizado. A equipe criou a nova Seção 4.2.1, sobre orçamento computacional, também em `rascunho`.

O `outline.md` recebeu duas notas. Os demais capítulos ficaram sem mudança.

---

## 2026-11-06 — Checagens de validade passam a ser anotadas, não vetadas, no despachante de catálogo; ADR 0008 formaliza a arquitetura do otimizador de nível superior; primeiros baselines (aleatório e guloso) comparam a busca evolutiva

**Commits:** `fc282cf`.

**O que foi feito.** Primeiro, `apply_intervention()` (`arteria/interventions/apply.py`) passou a rodar `check_validity()` (`arteria/interventions/validity.py`) depois de toda transformação de rede. O resultado é anexado como `ApplyResult.validity`.

A decisão de desenho registrada no commit é explícita. Uma validade rompida (junção desconectada, rota nomeada quebrada) é só *anotada*, não é motivo de erro. `apply_intervention()` nunca levanta exceção por isso. A razão: julgar se uma ruptura de validade é aceitável é tarefa de quem decide o pacote (planejador ou otimizador), não do despachante.

Os novos parâmetros `emergency_routes`/`transit_routes`/`pedestrian_routes` deixam o chamador escolher quais rotas checar. Ainda não existe lista de rotas fixada por cidade.

Segundo, a equipe escreveu a ADR 0008 (`docs/adr/0008-optimization-architecture.md`). Ela documenta a arquitetura do otimizador de nível superior.

A ADR define `PackageProblem` como o espaço de busca: um pacote é um vetor booleano, uma entrada por item do catálogo. Esse vetor é restrito por `mutual_exclusions` e por um orçamento opcional. O espaço de busca fica estritamente separado do mecanismo de busca em si. O mecanismo de busca recebe um `Evaluator` injetável e um `PackageCache`.

A ADR escolheu NSGA-II (via `pymoo`) como primeiro mecanismo de busca, em vez de otimização bayesiana. A justificativa: NSGA-II não exige modelo substituto e devolve uma fronteira de Pareto completa. O custo é mais avaliações por candidato encontrado. Esse custo não importa ainda, porque o avaliador em uso é um stub sintético gratuito. Mas vai importar quando um avaliador real for conectado (P6.1, trabalho futuro de desktop).

Hoje, "retomar" uma busca significa só a memoização do `PackageCache` (chave: conjunto ordenado de ids de entrada incluídos, persistida em JSON). Não existe checkpoint da população/geração do próprio `pymoo`. Também não existe backend de avaliação paralela por pool de processos ou distribuído, nem modelo substituto. A ideia de substituto em GNN desta trilha (P7.4) continua não construída.

Terceiro, a equipe adicionou dois baselines de busca: aleatória e gulosa (`arteria/optimize/baselines.py`). `random_search_baseline()` amostra pacotes viáveis e mantém o subconjunto não dominado. `greedy_baseline()` percorre o catálogo da entrada mais barata à mais cara, mantendo o que continua viável, e guarda todo pacote não dominado encontrado nesse único caminho.

Os dois baselines existem para comparar a fronteira de Pareto do NSGA-II contra algo mais simples. Os dois ainda operam só contra o avaliador sintético.

**Por que importa.** A anotação de validade, em vez da rejeição, já é um argumento de desenho reutilizável por esta trilha. Ela decide que o limite entre ação válida e ação inválida não deve vir da camada de infraestrutura. Esse limite fica, em vez disso, com a política ou o otimizador que escolhe o pacote.

Essa é exatamente o tipo de margem de exploração que uma política de aprendizado por reforço multiagente precisaria. Com essa margem, a política aprende por conta própria se deve evitar ou aceitar uma ruptura de conectividade localizada, em troca de ganho de tráfego em outro ponto da rede.

Trata-se de um precedente de arquitetura concreto no próprio ArterIA. Não é, porém, uma decisão desta trilha.

A ADR 0008 nomeia e justifica, pela primeira vez, as costuras do sistema: `Evaluator`, `PackageCache`, `PackageProblem`. São exatamente os pontos onde uma política aprendida por reforço multiagente, ou um avaliador substituto baseado em rede neural em grafos, poderiam entrar sem mudar a representação do espaço de busca. Os dois estão no horizonte desta dissertação (Objetivo específico 3).

A ADR já discute um trade-off: o NSGA-II paga em número de avaliações o que economiza em não precisar de substituto. Esse mesmo argumento de custo vai, no futuro, favorecer um substituto em GNN com muito mais força do que favorece o NSGA-II hoje. Mas esse argumento de custo ainda não foi medido, porque nenhum avaliador real existe ainda.

Os baselines aleatório e guloso dão ao NSGA-II uma referência de comparação mais simples do que não ter baseline nenhum. Por extensão, também servem a qualquer comparação futura com RL multiagente.

**Impacto na tese.** No Cap. 3 (`chapters/03-arquitetura-do-sistema.md`), a Seção 3.6 (antes `stub`) recebeu prosa nova. A prosa cobre a semântica de anotação de validade e a arquitetura do otimizador de nível superior: separação espaço de busca/mecanismo de busca, trade-off NSGA-II vs. bayesiana, baselines. A seção passou a `rascunho`.

O cabeçalho do capítulo mudou de "3.2 a 3.5 em rascunho, 3.1 e 3.6 em stub" para "3.2 a 3.6 em rascunho, 3.1 em stub". A prosa evita citar a ADR 0008 pelo número, e evita qualquer nome de arquivo ou função. Ela trata a decisão em nível conceitual, conforme o guia de estilo.

O `outline.md` recebeu uma nota de rastreio complementar no Capítulo 3. Essa nota fecha parte dos TODOs já abertos na nota de 2026-11-06 anterior: a checagem de validade isolada passa a estar ligada ao despachante; o NSGA-II ganha ADR própria e baselines.

**Perguntas abertas/riscos.**
1. A anotação de validade sem rejeição é escolha de produto do ArterIA, não desta trilha. Falta decidir, quando o ambiente de RL/GNN for de fato desenhado, se a política aprendida herda essa mesma permissividade (pode explorar pacotes com ruptura de validade) ou se a função de recompensa penaliza essa ruptura. Essa decisão ainda não foi tomada.
2. O argumento de custo da ADR 0008 (o NSGA-II paga em avaliações o que economiza em substituto) ainda é hipotético. Só deixa de ser hipotético quando existir um avaliador real de tráfego. Nenhuma medição comparando os dois lados existe ainda.
3. Nenhum agente de RL, política ou substituto em GNN foi implementado. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada.

**Perguntas abertas/riscos.**
1. Com rede única e quatro áreas, como definir agentes e recompensa: por área, por junção ou por aresta? Há risco de explosão do espaço de ação em 11 mil arestas.
2. A escolha acadêmica do corredor segue pendente, e é distinta da prioridade de produto. A rede única pode, ainda, empurrar a dissertação para um escopo de quatro corredores. Esse escopo pode ser incompatível com um mestrado.
3. O detalhe do commit `72ab33e` (o que houve com os 2 erros `traffic_light_logic`; distribuição de componentes) não foi verificado nesta entrada. Só a mensagem do commit foi usada.
4. Orçamento computacional: rodar MARL com SUMO em 9,7 GiB de RAM é restritivo. A decisão entre nuvem e nó universitário está pendente. As estimativas acima não foram medidas.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada.

---

## 2026-10-27 — Corredores como sequências de arestas na rede unificada; áreas B e C estendidas; desk check de tags OSM (trabalho NÃO commitado; base `b24377a`)

**Commits:** nenhum. Não há commit: o registro é do working tree: `cities/sjc/corridors/` (README, `corridors.geojson`, `summary.json`, KML, `build_corridors.py`), `cities/sjc/study-areas.{yaml,geojson}`, `candidate-corridors.md`, `data-manifest.yaml`, ADR 0016, `CHANGELOG.md` [Unreleased]. Esses itens podem mudar antes do commit.

**O que foi feito (no repositório, segundo README/CHANGELOG; não reexecutado aqui).**
1. Os corredores A, B (derivado), C, D e a ligação A-B foram desenhados como sequências ordenadas de arestas SUMO sobre a rede unificada (ADR 0016). O método usou o caminho de menor custo dirigido entre pontos de referência do OSM, roteando cada trecho nos dois sentidos. A ligação A-B, por exemplo, tem 14 arestas/883 m no sentido A para B, e 18 arestas/1.286 m no sentido B para A. Nenhum trecho ficou inroteável. O README atribui essa assimetria a rampas de mão única, a partir da geometria do OSM.
2. As áreas de estudo foram estendidas. B passou de 5,31 para 7,67 km² (ao sul, Av. Cassiopeia/Av. Perseu). C passou de 1,54 para 4,17 km² (Parque Vicentina Aranha, Av. Rio Branco etc.). A rede unificada foi reconstruída: agora tem 14.225 arestas e 6.655 junções, com 93,1% das junções no componente principal, e 0 erros de validação. (A ADR 0016 inicial tinha 11.035 arestas.) Os ids de aresta mudaram com essa reconstrução.
3. No desk check de dados de SJC, a equipe mediu a completude de tags OSM no candidato B. As vias principais estão bem etiquetadas. Nas ruas residenciais, a tag `lanes` aparece em ~4% dos casos, e `maxspeed` em ~5%. GeoSanja e IBGE ainda não foram confirmados como fontes disponíveis.
4. O SUMO 1.28 carrega a rede real sem avisos. Os 2 clusters `traffic_light` sem programa carregam como não semaforizados. Isso é inofensivo.
5. A reconciliação do roteiro com a ADR 0014 (WSL2) é dev-process. Ela não tem conteúdo para a trilha, e não foi registrada em nenhum capítulo.

**Ressalvas obrigatórias.** Toda a geometria dos corredores vem do OSM. Ela AINDA NÃO foi verificada por imagem aérea pelo responsável. O corredor B por arestas é novo: antes só existia o polígono, que já tinha sido checado por imagem aérea. O corredor B por arestas não herda essa verificação anterior. A direção da extensão de C (oeste/sudoeste, não norte) também aguarda confirmação do responsável. Nada disso é validação nem é escolha acadêmica de corredor. Nenhum agente, GNN ou recompensa foi conectado a estes artefatos.

**Por que importa.** Primeiro, as sequências de arestas dão a primeira definição concreta de "corredor" como subgrafo orientado. Essa definição é útil para delimitar observação, ação e recompensa por área (pergunta aberta 1 da entrada anterior), sem tratar 14 mil arestas como espaço de ação.

Segundo, o desk check (lanes ~4%, maxspeed ~5% em ruas residenciais) indica que, fora das vias principais, os atributos de faixa e velocidade vão ser em grande parte imputados. Isso afeta as características de aresta da GNN, e torna esses atributos candidatos a fator de ablação. Isso reforça o risco de qualidade do grafo já registrado.

Por fim, as assimetrias direcionais (883 m contra 1.286 m) são exemplos reais do que a representação em grafo orientado precisa preservar.

**Impacto na tese.** O `outline.md` recebeu uma nota no Cap. 3. A prosa dos capítulos NÃO foi alterada. O número 11.035, citado em `chapters/03` (Seção 3.2) e em `chapters/04` (TODO da Seção 4.2), está defasado frente ao número atual, 14.225. Esse número deve ser atualizado só depois do commit e da resolução das ressalvas, para não consolidar números provisórios.

**Perguntas abertas/riscos.**
1. Agente e recompensa por corredor (subgrafo) ou por junção: essa decisão de modelagem segue pendente. Há risco de os quatro corredores juntos excederem o escopo de um mestrado.
2. Os percentuais de 4% e 5% vêm do relato do CHANGELOG. Eles não foram verificados aqui. Por isso, a metodologia (denominador, escopo) precisa ser citada antes de esses números entrarem no Cap. 3.
3. Sem GeoSanja e IBGE confirmados, os atributos de ruas locais vão ser imputados ou omitidos.
4. A verificação aérea dos corredores, e da direção de C, pelo responsável, está pendente. Até lá, tudo fica como rascunho. [Resolvida na entrada seguinte, 2026-10-27 (2).]
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada.

---

## 2026-10-27 (2) — Checagem aérea aprovada; reprodutibilidade da construção da rede (Fase 2; trabalho NÃO commitado; base `0125f01`)

**Commits:** nenhum. Não há commit. Fontes: `CHANGELOG.md` [Unreleased] e `docs/roadmap.md` (Fase 2), ambos lidos. O código novo (`arteria/network/{snapshot,rebuild,diff,patches}.py`, `cities/sjc/network/osm-snapshot.yaml`) NÃO foi lido nem reexecutado. Os números abaixo vêm do relato do CHANGELOG.

**O que foi feito.**
1. Na checagem aérea do responsável (2026-10-27, Google Earth), os corredores A, B, C, D, a ligação A-B e as áreas estendidas de B e C foram todos aprovados. Isso inclui a extensão de C a oeste/sudoeste. Essa checagem resolve duas ressalvas da entrada anterior: geometria sem imagem aérea, e direção de C não confirmada. Os números vigentes da rede unificada são 14.225 arestas, 6.655 junções e 93,1% das junções no componente principal. Esses números substituem os da ADR 0016 inicial (11.035 arestas/94,0%).
2. Quanto à reprodutibilidade (Fase 2), a equipe fixou um snapshot OSM: Geofabrik Sudeste, PBF de 2026-10-25, com sha256. O comando `arteria network rebuild` reproduz o hash de conteúdo da rede (o cabeçalho de timestamp do `netconvert` é ignorado no cálculo). Duas execuções deram resultado idêntico: 0 erros, 127 avisos, ~16 segundos.

   A equipe também introduziu patches como segunda passada do `netconvert` (nenhum patch é necessário até agora) e o comando `arteria network diff`. Numa demonstração (B isolada contra rede unificada), o diff mostrou 12.175 arestas adicionadas, 24 removidas e 137 alteradas. Um teste de desktop confirma que todas as arestas dos corredores existem na rede.

   Nenhum GTFS público de SJC foi encontrado. Por isso, a etapa P2.6 do roteiro foi adiada.

**Por que importa.** Ids de aresta estáveis e reconstruíveis são pré-condição para qualquer ambiente de RL/GNN sobre o grafo. Baseline, demanda e calibração dependem deles (ADR 0016).

A falta de GTFS significa que a rede não vai ter ônibus por ora. Isso restringe intervenções de faixa de ônibus e de prioridade semafórica — intervenções correlatas, não centrais ao escopo. O objeto estrutural (faixas e sentidos) não é afetado de imediato.

**Impacto na tese.** No Cap. 3, a Seção 3.2 (atualização de tamanhos, corredores, aprovação aérea) e a Seção 3.5 (mecanismo de reprodutibilidade) ficaram em `rascunho`, via anexos. O texto antigo foi preservado como histórico.

No Cap. 4, dois trechos da Seção 4.2 foram sinalizados como defasados/atualizados. O `outline.md` recebeu notas no Cap. 3. Os demais capítulos ficaram sem mudança.

**Perguntas abertas/riscos.**
1. As frações 94,0% (arestas, ADR 0016) e 93,1% (junções, relato atual) usam unidades distintas. Elas não devem ser comparadas direto, sem antes verificar o validador.
2. O formato do registro de proveniência do `rebuild`, e sua relação com `RunManifest`, não foram verificados. Além disso, essa reprodutibilidade cobre só a construção da rede, não o treinamento nem a simulação.
3. Sem GTFS, não há demanda nem rota de transporte público. A decisão sobre fonte alternativa (rotas manuais) está pendente do responsável.
4. Todo o material está no working tree. Se ele mudar antes do commit, os anexos precisam de revisão.
5. Agente e recompensa por corredor, ou por junção: essa decisão continua pendente. O escopo de quatro corredores pode exceder um mestrado. O(A) orientador(a) ainda não foi contatado(a).

---

## 2026-10-28 — Cross-check da rede OSM contra IBGE e GeoSanja (P2.1, P2.7); resolve lacuna de fontes de atributo de rua

**Commits:** `1c4a7b4` ("feat: cross-check SJC network against IBGE and GeoSanja (P2.1, P2.7)"). Os números abaixo vêm do relato repassado pelo responsável do ArterIA. Eles não foram reexecutados nem lidos em código nesta sessão. Os caminhos de arquivo foram confirmados: eles existem no repositório (`arteria/network/crosscheck.py`, `arteria/network/render.py`, `cities/sjc/data-manifest.yaml`). TODO(evidência): ler `crosscheck.py` e reexecutar o comando antes de citar os números como fato assentado no capítulo.

**O que foi feito.** Dois comandos novos — `arteria network crosscheck --city sjc` e `arteria network render --city sjc` — comparam a rede SUMO/OSM construída (14.225 arestas, ver entrada 2026-10-27 (2)) contra duas fontes públicas de referência. As duas fontes estão registradas em `cities/sjc/data-manifest.yaml`: a Base de Faces de Logradouros do IBGE (2022, shapefile estadual) e as camadas `arruamentos`/Hierarquia Viária do GeoSanja (portal da prefeitura de SJC).

O cross-check cobre só os quatro corredores do estudo, dentro de um buffer de 50 m em torno da união dos polígonos. Ele compara por dois critérios: nome de rua normalizado (contra o IBGE) e geometria/cobertura de centro de linha, amostrada a cada 5 m (contra IBGE e GeoSanja, com limiar de 15 m).

Os resultados relatados (não commitados; saídas gitignored em `data/crosscheck/` e `data/renders/`) mostram 543 nomes de rua coincidentes dentro dos corredores (167 só no OSM, 201 só no IBGE). A distância mediana entre amostra e referência é ~3,0 m. Em 6,4% das amostras, essa distância passa de 15 m. 81,5% do comprimento OSM fica dentro de 15 m do GeoSanja, e 97,2% do GeoSanja fica dentro de 15 m do OSM.

Parte dos descasamentos de distância alta vem de nomes de rua genéricos ou reutilizados (ex. "Rua Dois", "Viela Três"). Esses nomes casam entre ruas distintas, e isso não é erro de geometria.

A equipe também gerou renders de mapa: a rede colorida por prioridade de aresta do SUMO, com os quatro contornos de área de estudo. Esses renders não foram commitados.

Surgiu, ainda, uma questão nova, ainda não corrigida: os nomes de rua OSM na rede construída carregam um artefato de escape duplo de `&apos;`. Esse artefato afeta algumas dezenas de nomes com apóstrofo (ex. "D'Ávila"). A origem suspeita é o `netconvert`, ou uma etapa depois dele, mas ainda não foi diagnosticada.

**Por que importa.** Essa entrega resolve, com dados concretos, a lacuna já registrada em duas entradas anteriores deste log ("GeoSanja e IBGE NÃO confirmados como fontes disponíveis", 2026-10-27) e no `outline.md` (Cap. 4: "apenas a topologia da malha viária tem fonte de autoatendimento confirmada [OSM/Geosanja/IBGE]"). Agora há número de fato, não só fonte listada em manifesto.

Trata-se do primeiro cross-check quantitativo da completude e da precisão geométrica do grafo derivado de OSM contra fontes públicas independentes. É pré-condição direta do Objetivo específico 1 (representação em grafo) e do argumento central das Seções 3.3/3.4 (a qualidade do grafo OSM condiciona observação, ação e GNN).

Esses números (81,5-97,2% de cobertura geométrica dentro de 15 m; ~37% dos nomes só no OSM ou só no IBGE) dão, por ora, a primeira medida substituta de completude. Essa medida já estava referida como `TODO(citação)` na Seção 3.3 (`haklay2010osm`/`barrington2017osm`). Ela não substitui a literatura de qualidade do OSM — só a complementa com um dado local.

O próprio commit e o relato classificam essa entrega como cross-check de triagem (casamento de nome ainda não ajustado fino), não como etapa de calibração. A dissertação deve preservar essa distinção. Não se trata de validação de atributos de faixa/sentido (lanes/maxspeed, ainda ~4%/~5% em ruas residenciais, segundo a entrada de 2026-10-27). Trata-se só de nome e geometria de via.

**Impacto na tese.** No Cap. 3 (`chapters/03-arquitetura-do-sistema.md`), há uma atualização nova a registrar: na Seção 3.3 (cross-check como segunda camada de verificação, além do validador estrutural) e na Seção 3.4 (completude do OSM, ponto 5, agora com número local além da citação genérica). O texto do capítulo ainda não foi editado nesta sessão — fica como TODO para a próxima revisão de prosa.

No `outline.md`, as notas do Cap. 3 e do Cap. 4 (linha sobre fonte confirmada de topologia) devem ser atualizadas. Elas precisam refletir que a confirmação de disponibilidade já ocorreu, com número associado.

**Perguntas abertas/riscos.**
1. O cross-check não cobre atributos estruturais: faixas, sentido, restrições de giro. Ele cobre só nome e geometria do eixo da via. O risco de qualidade de `lanes`/`maxspeed`, já registrado em 2026-10-27, continua inteiramente aberto.
2. ~~Artefato de escape duplo (`&apos;`) em nomes de rua com apóstrofo~~ — **resolvido em `1895aeb`, ver addendum abaixo (2026-10-28 (2)).**
3. Os descasamentos de distância alta, por nomes genéricos reutilizados ("Rua Dois"), sugerem que o casamento por nome tem um limite estrutural nesta malha. Qualquer uso futuro desse cross-check como insumo de qualidade de dado (não só triagem) vai precisar de casamento por nome e geometria juntos, não por nome isolado.
4. Os números desta entrada não foram verificados em código nesta sessão, só repassados. Antes de citá-los no capítulo como fato, é preciso reexecutar `arteria network crosscheck --city sjc` e ler `crosscheck.py`.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-28 (2) — Addendum: artefato de escape duplo diagnosticado e corrigido (risco 2 acima resolvido)

**Commit:** `1895aeb` ("fix: undo netconvert's double-escaping of names"), CHANGELOG [1.3].

**O que foi feito.** A equipe confirmou a causa raiz com uma fixture OSM mínima de duas vias, testada contra o binário real do `netconvert` 1.28.0. O `netconvert` escapa duas vezes qualquer caractere especial de XML literal (`'`, `&`, `"`, `<`, `>`) presente numa tag `name` do OSM. Primeiro, ele troca o caractere pela entidade XML nomeada internamente. Depois, seu próprio escritor de saída escapa de novo o `&` dessa entidade (por exemplo, o apóstrofo vira `&amp;apos;`). Trata-se, portanto, de um bug do próprio `netconvert`/SUMO, não de um erro de lógica do ArterIA.

Com isso, a nova função `arteria.network.build.fix_double_escaped_names()` passou a rodar automaticamente depois de toda chamada de `netconvert`, dentro de `build_network`. Ela corrige os atributos `name`/`origId` no `.net.xml` escrito. Testes novos cobrem a função isolada, um caso no-op, e um teste de ponta a ponta com fixture reproduzindo o padrão.

A rede real de SJC foi reconstruída com a correção. O snapshot OSM fixado (`cities/sjc/network/osm-snapshot.yaml`) foi repontado para o hash de conteúdo da rede corrigida. No total, 58 caracteres foram corrigidos em exatamente 3 nomes de rua (exemplo: "Rua Armando D'Oliveira Cobra", antes escrito como "Rua Armando D&amp;apos;Oliveira Cobra"). A estrutura da rede não mudou: 0 arestas, faixas ou junções foram adicionadas, removidas ou alteradas, e a validação continua com 0 erros e 127 avisos.

Por fim, a equipe reexecutou o cross-check do commit `1c4a7b4` contra a rede corrigida. Os nomes coincidentes com o IBGE passaram de 543 para 544 (um dos três nomes corrigidos agora casa corretamente). Os nomes só-OSM caíram de 167 para 166, e os só-IBGE de 201 para 200. Os números de geometria (mediana ~3,0 m, 6,4% acima de 15 m, cobertura GeoSanja 81,5%/97,2%) ficaram essencialmente inalterados.

**Por que importa.** Essa correção fecha o risco 2 já registrado na entrada anterior (2026-10-28), e já citado em `chapters/03-arquitetura-do-sistema.md` (Seção 3.3) como "achado colateral ainda não corrigido". A causa raiz foi identificada, e a correção é automática — não é um contorno manual.

Os nomes de rua em `sjc.net.xml` podem, agora, ser citados direto em figuras, tabelas e texto, sem o artefato de apóstrofo. Esse ponto é relevante porque a nota da Seção 3.3 já tinha marcado esse artefato como impeditivo para qualquer uso futuro de nome de rua como chave de junção com dados de calibração ou contagem municipal.

**Impacto na tese.** Em `chapters/03-arquitetura-do-sistema.md`, na Seção 3.3 (nota do commit `1c4a7b4`, trecho final), a equipe acrescentou uma frase registrando a correção e os novos totais (544/166/200). O restante da nota não foi reescrito.

No `outline.md`, a nota do Cap. 3 (2026-10-28, `1c4a7b4`) foi marcada como superada, só neste ponto específico.

**Perguntas abertas/riscos.**
1. Os três nomes afetados, e o novo total 544/166/200, não foram verificados em código nesta sessão — só repassados do CHANGELOG. Vale a mesma ressalva já registrada para os números do commit `1c4a7b4`: é preciso reexecutar `crosscheck.py` antes de consolidar esses números na prosa.
2. A função `fix_double_escaped_names()` cobre `'`, `&`, `"`, `<`, `>`. Ainda não foi verificado se outros caracteres de nome de rua — acentos ou Unicode fora do conjunto de escape XML — têm um problema parecido. Essa é uma lacuna de verificação desta trilha, não uma hipótese levantada pelo commit.
3. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-28 (3) — Reenquadramento de registro de voz/estrutura em `pre-projeto.md` e `chapters/*.md` conforme o guia de estilo (entrada retroativa à edição)

**Commit:** `377056b` ("docs(thesis): adopt author's academic writing register across thesis tracks").

**O que foi feito.** O commit reescreveu `pre-projeto.md` e os capítulos já existentes em `chapters/` desta trilha. O objetivo foi seguir o registro acadêmico descrito em `docs/thesis/real-previous-tccs/writting-style.md`, conforme a regra "Registro de escrita por tipo de arquivo" deste agente.

Essa foi uma mudança de voz e de estrutura de prosa: impessoalização, tese-argumento-conclusão, remoção de marcadores do corpo argumentativo, citação integrada. Não incluiu fato novo, número novo, citação nova ou decisão nova.

Esta entrada registra o commit a posteriori. A rodada que produziu o commit não deixou o registro de progresso correspondente — lacuna já apontada pelo responsável do projeto.

**Por que importa.** O registro de rastreabilidade desta trilha exige que toda reescrita de capítulo ou de pré-projeto deixe rastro no log, mesmo quando a reescrita é puramente de forma. Isso mantém auditável todo trecho promovido de registro técnico a prosa de capítulo.

Sem esta entrada, o commit `377056b` ficaria sem nenhuma âncora de progresso. Isso quebraria essa convenção.

**Impacto na tese.** Não houve mudança de conteúdo de pesquisa, de arquitetura ou de literatura. A reescrita é de registro — voz impessoal, estrutura argumentativa —, não de tese.

Três pontos, porém, merecem checagem do responsável antes de virarem fato assentado. Eles não foram corrigidos nesta entrada, só sinalizados, por instrução explícita de não reescrever agora:

1. Em `pre-projeto.md` §9, a reescrita mudou "quatro componentes" para "cinco componentes" de metodologia. A mudança casa o número com a lista de componentes de fato enumerada no parágrafo. O responsável precisa confirmar que cinco é, de fato, a contagem correta pretendida — e não um ajuste mecânico de concordância que esconda um componente faltante ou duplicado na lista.
2. Em `pre-projeto.md`, o trecho sobre a ADR 0013 foi parafraseado como tratando de privacidade/reidentificação de microdados de Pesquisa OD. Essa paráfrase é consistente com o que o `progress.md` já registrava sobre a ADR (entrada do commit `975fec7`, 2026-10-25). Mas o responsável precisa confirmar que a formulação em prosa do pré-projeto não introduziu nenhuma nuance ausente do texto original da ADR.
3. Foram adicionados parágrafos de fechamento em `pre-projeto.md` §3 e §11, e em `chapters/03-arquitetura-do-sistema.md` §3.7 e `chapters/04-experimentos.md` §4.4. Esses parágrafos são síntese do agente, não do autor, e não transcrição literal de nenhuma fonte. Luiz Wagner precisa revisar pessoalmente esses quatro fechamentos antes de tratá-los como texto definitivo do autor.

**Perguntas abertas/riscos.**
1. Confirmar a contagem de "cinco componentes" em `pre-projeto.md` §9 contra a lista real de componentes pretendida.
2. Confirmar que a paráfrase da ADR 0013 (privacidade/reidentificação) em `pre-projeto.md` reflete com exatidão o texto da ADR.
3. Revisar pessoalmente os quatro parágrafos de fechamento escritos pelo agente (`pre-projeto.md` §3 e §11; `chapters/03-arquitetura-do-sistema.md` §3.7; `chapters/04-experimentos.md` §4.4) antes de considerá-los prosa definitiva.
4. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-29 — Zoneamento em zonas de análise de tráfego (P3.1) particiona a rede unificada; ADR 0017 (Proposta) decide os dados de população/empregos-proxy para o modelo gravitacional de demanda

**Commits:** `7633693` ("feat: start Phase 3 with TAZ zoning (P3.1)"); `e4daf87` ("feat: add run-sjc-sim.sh desk helper for quick SUMO visual runs", tratado separadamente ao final desta entrada).

**O que foi feito.** A Fase 3 do roteiro (Demanda e cenário-base) começou com a primeira etapa de zoneamento (P3.1). O módulo novo `arteria/demand/zoning.py`, exposto pelo comando `arteria demand taz --city sjc`, atribui cada aresta da rede unificada de SJC a uma zona de análise de tráfego (*traffic analysis zone*, TAZ). Há quatro dessas zonas, correspondentes às áreas de estudo já verificadas por imagem aérea (candidatos a, b, c, d — `cities/sjc/study-areas.geojson`). Tudo o que fica fora dessas quatro áreas vai para uma zona residual chamada `external`.

A atribuição usa um teste de ponto-em-polígono no ponto médio de cada aresta. O resultado é gravado num arquivo `.taz.xml`, no formato nativo do SUMO. Nenhuma geometria nova foi desenhada: a partição reaproveita integralmente os polígonos de área de estudo já aceitos e verificados. Nenhuma camada nova precisa ser validada.

Rodado contra a rede unificada real (14.225 arestas, ADR 0016, ver entrada de 2026-10-27 (2) deste log), o resultado foi: a=1.146, b=3.020, c=1.786, d=1.103, external=7.170. A soma bate exatamente com o total conhecido da rede, e nenhuma zona ficou vazia.

A zona `external`, por si só, concentra pouco mais da metade das arestas (7.170 de 14.225) — mais do que a soma das quatro áreas de avaliação juntas (7.055). Isso mostra que a rede unificada é, na maior parte, composta por tráfego fora do escopo das quatro áreas de interesse acadêmico.

Em paralelo, a equipe escreveu a ADR 0017 ("Zoning and trip-generation data for the gravity-model baseline"). O status dela é "Proposed" — ainda não foi aceita pelo responsável do projeto. Essa ADR decide, mas ainda não implementa, de onde virão os pesos de produção e atração de viagens do modelo gravitacional da etapa P3.2. Essa etapa já estava comprometida pela ADR 0013, que fixa a metodologia de demanda sintética calibrada por contagem, sem Pesquisa OD real. A ADR 0017 nomeia o dado a usar, não a metodologia.

O lado de produção (população) vai usar o Censo IBGE 2022 por setor censitário — dado público de autoatendimento, no mesmo precedente já usado para a base de faces de logradouros do IBGE (entrada de 2026-10-28 deste log).

O lado de atração (empregos) não tem fonte pública de autoatendimento alcançável. Dados no estilo RAIS/CAGED exigiriam contato com órgão. Por isso, a ADR propõe usar a camada de zoneamento do Plano Diretor do GeoSanja (já baixada) como proxy de densidade de uso do solo comercial/institucional. A própria ADR rotula essa camada explicitamente como proxy, não como contagem real de emprego — mesmo padrão de ressalva de limite de escopo já usado na ADR 0013.

A ADR também explicita um risco não resolvido: se o arquivo de população por setor do Censo 2022 não for baixável para SJC com a mesma facilidade da base de faces de logradouros, a etapa P3.2 ficaria sem fonte imediata de população. Nesse caso, seria preciso um substituto mais grosseiro: a população do município dividida pela área da TAZ. Esse item ficou registrado como pendência aberta no backlog do projeto — ele não foi resolvido por esta ADR.

**Por que importa.** O zoneamento é a primeira partição espacial real e concreta de toda a rede unificada em unidades mais grosseiras do que a aresta. Também é mais grosseira do que a sequência de arestas por corredor, já registrada na entrada de 2026-10-27 deste log.

Por isso, é uma terceira candidata concreta — ao lado de "aresta individual" e de "corredor como subgrafo orientado" — para a pergunta de modelagem repetidamente registrada como aberta neste log desde 2026-10-26: qual é a unidade de observação/ação/recompensa de um agente sobre um grafo de ordem 10^4 arestas?

Essa candidata, porém, tem motivação primária distinta: a partição foi desenhada para alimentar o modelo gravitacional de demanda (P3.2), não a arquitetura de agentes. O fato de mais da metade da rede cair na zona residual `external` sugere que, se essa partição for usada como unidade de agente, ela vai precisar de tratamento específico para esse tráfego de passagem majoritário. Esse ponto se relaciona à terceira hipótese já registrada em `chapters/03-arquitetura-do-sistema.md` (Seção 3.3, "efeito de borda").

A ADR 0017 é relevante porque fecha, no nível de decisão (ainda não no de execução), a lacuna de fonte de dado que bloqueava a etapa P3.2 desde a aceitação da ADR 0013. (A ADR 0013 nomeava "qual metodologia"; a ADR 0017 nomeia "qual dado".)

Ao mesmo tempo, a ADR 0017 reafirma — agora para o lado da demanda, não só para a topologia da rede — o mesmo padrão de honestidade metodológica já visto nos dados de rede. Um proxy de uso do solo substitui um dado real de emprego que não existe sem contato com órgão público. A ADR marca essa substituição explicitamente como limite de validade, não como dado real.

Isso reforça direto o risco de "cenário sintético calibrado a fluxos observados" (nunca "tráfego real de SJC"), já registrado na Seção 4.1 do capítulo de experimentos. A própria origem-destino sintética da demanda carrega, agora também no lado da atração, uma camada de proxy — não é só a ausência de Pesquisa OD já conhecida.

**Impacto na tese.** Em `chapters/03-arquitetura-do-sistema.md`, a Seção 3.4 ("A qualidade da rede condiciona observação, ação e GNN") recebeu uma sexta consideração. Ela registra a partição real da rede em zonas de análise de tráfego como candidata, ainda hipotética, de unidade espacial de agregação para agente e recompensa. O texto esclarece que essa partição já existe como artefato implementado para fins de estimativa de demanda — ainda não como escolha de arquitetura de aprendizado. O parágrafo de fechamento da seção foi ajustado para refletir essa distinção. As cinco considerações anteriores não foram reescritas.

Em `chapters/04-experimentos.md`, a Seção 4.1 (stub) recebeu uma frase nova, atualizando a nota sobre o cenário de demanda sintética. Ela registra que a fonte de dado proposta para o modelo gravitacional (ADR 0017) ainda não foi aceita, e que o lado de atração é, por decisão explícita da própria ADR, um proxy de uso do solo — não uma contagem real de emprego.

No `outline.md`, notas de rastreio foram adicionadas aos Capítulos 3 e 4. O commit `e4daf87` (script de desktop para rodar SUMO visualmente) não gerou nenhuma edição de capítulo. Ele é infraestrutura de execução de desktop, sem conteúdo de pesquisa. Fica registrado aqui só como infraestrutura disponível para rodar, no futuro, episódios de inspeção visual rápida e não calibrados — no mesmo status probatório já atribuído a qualquer execução de `sumo-gui` neste log: camada de comunicação/inspeção, nunca evidência.

**Perguntas abertas/riscos.**
1. A ADR 0017 está Proposta, ainda não aceita. Os dados de população (Censo IBGE 2022) ainda não foram baixados nem associados às zonas. Por isso, a matriz OD do modelo gravitacional (P3.2) está bloqueada até essa aceitação e essa busca de dado real — conforme o próprio backlog do projeto.
2. O lado de atração (empregos) vai continuar sendo um proxy de uso do solo, mesmo depois de uma eventual aceitação da ADR — não é uma contagem real de emprego. Qualquer leitura de recompensa ou de política que vier a depender dessa atração vai precisar herdar essa ressalva de forma explícita, no mesmo padrão já exigido para o conector novo do Candidato B (ADR 0013, nota do commit `975fec7` no Capítulo 3).
3. A zona residual `external` concentrar pouco mais da metade das arestas levanta uma questão ainda não decidida: como, ou se, o tráfego de passagem externo às quatro áreas de avaliação deve ser representado na observação de um agente, caso a partição em zonas venha a ser adotada como unidade de agregação espacial.
4. Os números desta entrada vêm do relato do README do projeto, e do próprio texto da ADR 0017. Eles não foram reexecutados nem lidos em código (`zoning.py`) nesta sessão. Vale a mesma ressalva de verificação já aplicada a outras entregas deste log.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-29 (2) — Censo IBGE 2022 fecha o lado de produção do modelo gravitacional (P3.2); lado de atração permanece bloqueado, e o desequilíbrio populacional entre zonas supera o já registrado por aresta

**Commit:** `264e8fc` ("feat: add IBGE census population join for TAZ production weights (P3.2)"). Nesta entrada, a equipe leu diretamente, nesta sessão, o módulo `arteria/demand/population.py` e a entrada correspondente de `cities/sjc/data-manifest.yaml` — não apenas repassou a mensagem do commit. O comando `arteria demand population --city sjc` em si não foi reexecutado.

**O que foi feito.** A equipe implementou a metade de "peso de produção" da etapa P3.2 do roteiro — a preparação da matriz origem-destino sintética. O módulo novo lê o GeoPackage estadual de setores censitários do Censo IBGE 2022. Esse arquivo é publicado pelo próprio IBGE num servidor de download direto. É o mesmo contorno já usado para a base de faces de logradouros (entrada de 2026-10-28 deste log), que evita o bloqueio de acesso automatizado do portal principal do IBGE.

O módulo soma, por teste de centroide em polígono, a população de cada setor na zona de análise de tráfego (TAZ) que o contém. São as quatro zonas de área de avaliação já verificadas por imagem aérea (a/b/c/d), mais a zona residual `external`. O módulo reaproveita integralmente o zoneamento já implementado na entrada anterior (2026-10-29, commit `7633693`).

A leitura do formato geoespacial é feita direto contra o módulo padrão de banco de dados embutido da linguagem. Não há dependência de nenhuma biblioteca geoespacial pesada adicional — mesma linha de engenharia frugal já seguida pelo restante do pipeline de dados desta trilha.

Rodado contra a rede real de SJC, o módulo processou 1.554 setores censitários do município. A população somada, por zona, foi: a=13.499, b=36.391, c=24.516, d=22.702 e external=599.946, com total de 697.054 habitantes. Esse total é compatível, em ordem de grandeza, com a população do município. Isso funciona como verificação de sanidade indireta da cobertura do filtro por código municipal.

A zona residual concentra, isoladamente, 86,1% de toda a população somada (599.946 de 697.054). Essa proporção é bem mais acentuada do que a já registrada para a mesma partição medida por aresta, na entrada anterior (50,4% das arestas, 7.170 de 14.225). Ou seja: a mesma zona `external`, que já tinha pouco mais da metade do grafo, concentra, do ponto de vista residencial, a grande maioria da população do município.

Em paralelo, o lado de atração continua bloqueado. Esse lado usaria, como proxy de uso do solo, a camada de "Macrozoneamento Urbano" do GeoSanja — nomeada, mas ainda não obtida, pela ADR 0017. Até aqui, só as camadas de hierarquia viária do GeoSanja foram de fato baixadas (ver entrada de 2026-10-28). A camada de zoneamento de uso do solo em si ainda não foi baixada: o portal correspondente não se mostrou acessível por automação nesta sessão.

O backlog do próprio projeto já registra esse bloqueio, como pendência de busca manual — sessão de navegador de mesa, ou obtenção manual pelo responsável. Este commit não resolveu essa pendência.

O modelo gravitacional de demanda em si precisa dos dois lados, produção e atração, para gerar a matriz origem-destino sintética. Por isso, ele continua não implementado. A ADR 0017 continua com status "Proposta", não aceita.

**Por que importa.** Primeiro, esta entrega resolve, com dado real em vez de só decisão de fonte, a primeira pergunta aberta registrada na entrada imediatamente anterior deste log (2026-10-29): "os dados de população do Censo IBGE 2022 ainda não foram baixados nem associados às zonas". O próprio risco que a ADR 0017 tinha levantado — de que o arquivo de população por setor do Censo 2022 talvez não fosse baixável para SJC com a mesma facilidade da base de faces de logradouros — não se confirmou. O mesmo contorno de servidor de download direto do IBGE funcionou de novo. Isso reduz um risco técnico que, até aqui, era só hipotético.

Segundo — e mais relevante para o núcleo de RL/GNN desta trilha — o desequilíbrio de 86,1% da população na zona residual `external` é evidência adicional. Agora é evidência de natureza demográfica, não só topológica, para a sexta consideração já registrada no Capítulo 3 (Seção 3.4), sobre a partição em zonas de análise de tráfego como candidata, ainda hipotética, de unidade espacial de agregação para agente e recompensa.

Se essa partição vier a ser adotada como unidade de agente, o fato de a cidade concentrar a grande maioria de sua população fora das quatro áreas de interesse acadêmico reforça algo importante — agora com um segundo indicador, independente do primeiro (arestas): o tráfego de passagem/externo não pode ser tratado como resíduo desprezível na observação de um agente. Pelo menos sob a ótica populacional, esse tráfego representa a maior parte da cidade real por trás da rede simulada.

Terceiro, este episódio reafirma, do lado da demanda, o mesmo padrão de honestidade metodológica já exigido do lado da rede. A terminologia é "cenário sintético calibrado a fluxos observados", nunca "tráfego real de SJC" — fixada pela ADR 0013.

Mesmo com o lado de produção agora lastreado em dado censitário real, o modelo gravitacional completo vai continuar dependendo, do lado de atração, de um proxy de uso do solo. E esse proxy, por sua vez, ainda não foi obtido. Por isso, a dissertação deve continuar tratando qualquer cenário de demanda futuro como parcialmente proxy, mesmo depois de uma eventual aceitação da ADR 0017 — não só até essa aceitação.

**Impacto na tese.** Em `chapters/03-arquitetura-do-sistema.md`, a sexta consideração da Seção 3.4 foi atualizada com o novo indicador populacional (86,1% na zona residual). A redação das cinco considerações anteriores, e do restante da seção, não mudou.

Em `chapters/04-experimentos.md`, a Seção 4.1 recebeu o ajuste de uma frase. Ela registra que o lado de produção do modelo gravitacional já tem dado real associado às zonas, mas que o lado de atração continua como proxy ainda não obtido. Por isso, o cenário de demanda continua apenas desenhado, não calculado.

No `outline.md`, a nota de rastreio do Capítulo 3 sobre o zoneamento foi estendida com o número populacional.

**Perguntas abertas/riscos.**
1. A ADR 0017 continua Proposta, não aceita. O modelo gravitacional em si — a combinação de produção e atração, e a construção da matriz origem-destino — ainda não foi implementado. A etapa P3.2 continua bloqueada no lado de atração; não mais no lado de produção.
2. O lado de atração depende de uma camada do portal GeoSanja, ainda não obtida. Até aqui, só as camadas de hierarquia viária foram baixadas — não a de zoneamento de uso do solo. O próprio backlog do projeto registra que o portal não se mostrou acessível por automação nesta sessão. Isso exige sessão de navegador de mesa, ou obtenção manual pelo responsável. É uma pendência de infraestrutura de dados, não de arquitetura de RL/GNN — mas ela continua bloqueando qualquer execução real do modelo gravitacional.
3. O indicador de 86,1% de concentração populacional na zona residual reforça, mas não resolve, a pergunta de modelagem já aberta desde 2026-10-26: qual é a unidade de observação/ação/recompensa de um agente sobre o grafo único? Nenhuma decisão de arquitetura de agente foi tomada nesta entrega. Ela é motivada inteiramente pela estimativa de demanda, não pelo desenho de RL.
4. O comando real (`arteria demand population --city sjc`) não foi reexecutado nesta sessão. Os números acima foram conferidos contra o texto do módulo de código, e contra a entrada correspondente do inventário de dados da cidade — os dois lidos por completo nesta sessão, não só contra a mensagem do commit. Mas a soma aritmética, e a cobertura do filtro municipal, não foram recalculadas a partir do arquivo bruto do IBGE.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-29 (3) — Mecânica de geração de rotas (od2trips/duarouter/routeSampler) fecha a tubulação do pipeline de demanda do roteiro P3, ainda sem execução real contra dados de SJC

**Commit:** `f78b73f` ("feat: wire od2trips/duarouter/routeSampler mechanics (P3.3)"). Nesta rodada, a equipe só leu o resumo repassado. O módulo `arteria/demand/trips.py`, e os testes correspondentes, não foram lidos diretamente nesta sessão.

**O que foi feito.** O módulo novo encapsula três ferramentas de linha de comando do SUMO. O pipeline de demanda do ArterIA (ADR 0013, já tratada nesta trilha nas entradas de 2026-10-25 e 2026-10-29) precisa dessas três ferramentas entre uma matriz origem-destino (OD) e uma linha de base calibrada por contagem. `od2trips` converte a matriz OD em viagens. `duarouter` roteia essas viagens em veículos. `routeSampler` seleciona, entre rotas candidatas, o subconjunto compatível com contagens medidas.

Cada ferramenta é chamada por meio de um `run` injetável. Essa é a mesma costura de adaptador já usada para `netconvert` (`arteria/network/build.py`) — a quarta instância desse padrão rastreada nesta trilha, depois de `goodness_of_fit.py`, `study_area.py` e `osm_fetch.py`/`build.py` (entradas de 2026-10-25).

Um teste de bancada local, separado da suíte remota, roda um ciclo completo contra os binários reais do SUMO 1.28.0, numa rede de brinquedo de 4 nós. Segundo o resumo repassado, esse teste passa — mas não foi reexecutado nesta sessão.

Três comandos de CLI novos (`arteria demand od2trips`/`duarouter`/`routesampler`) expõem esse mecanismo.

Nenhuma execução, porém, ocorreu contra dados reais de SJC. A matriz OD do modelo gravitacional de P3.2 continua bloqueada no lado de atração (camada de uso do solo do GeoSanja ainda não obtida, ADR 0017 Proposta — ver entrada de 2026-10-29 (2) deste log). As contagens de tráfego necessárias para calibrar o `routeSampler` continuam `deferred` no inventário de dados da cidade, sem contato autorizado com a agência.

Segundo o resumo repassado, a suíte completa (192 testes) e as checagens de lint/tipagem estão limpas. A versão do projeto subiu para 1.6.0 no mesmo commit. Esse bump cobre também os pesos de produção da etapa P3.2, do commit anterior (`264e8fc`), que não tinha feito o bump.

**Por que importa.** Este commit fecha, do lado da mecânica — não da execução —, a lacuna de uma ferramenta já nomeada, mas ainda não codificada. A ADR 0013 já tinha reservado essa ferramenta para o roteiro de demanda sintética calibrada por contagem. Até aqui, `od2trips`, `duarouter` e `routeSampler` eram só texto de metodologia citado em prosa (entrada de 2026-10-25, revisão do commit `975fec7`). Agora, passam a ser três comandos de CLI testáveis e injetáveis.

Esse fato é relevante ao Capítulo 4. É a primeira peça de código concreta que, uma vez executada contra dados reais, produziria o "cenário sintético calibrado a fluxos observados" já exigido pela terminologia da ADR 0013, na descrição do ambiente de treinamento/avaliação de RL.

Mas a mecânica isolada não resolve nenhuma das duas lacunas de dado que já bloqueavam esse cenário. Sem a matriz OD de P3.2 — ela mesma bloqueada pelo lado de atração do modelo gravitacional, GeoSanja — não há entrada para `od2trips`. Sem contagens reais (`deferred`), não há alvo de calibração para `routeSampler`.

O commit é, portanto, evidência de que a tubulação do pipeline de demanda está pronta para ser acionada — não de que a demanda de SJC já foi gerada ou calibrada. A dissertação deve preservar essa distinção, com o mesmo rigor já aplicado a `randomTrips.py` e a `replication.py`.

Esse é a quarta vez que se repete o mesmo padrão arquitetural: isolar a única costura de sistema externo — aqui, três binários externos em vez de um — atrás de um `Callable` injetável, testável só com fakes. Essa repetição reforça, sem alterar, a observação de engenharia já registrada nas entradas sobre `study_area.py` e `osm_fetch.py`/`build.py`.

Trata-se de um precedente consistente do ArterIA. É relevante como referência, caso o pipeline de dados desta dissertação (Objetivo específico 1) venha a adotar um desenho semelhante para sua própria integração com SUMO/TraCI. Mas essa repetição não constitui, por si só, decisão de arquitetura desta trilha.

**Impacto na tese.** Em `chapters/04-experimentos.md`, a Seção 4.1 passa a registrar que a mecânica de geração de rotas (`od2trips`/`duarouter`/`routeSampler`) já existe como código testável. O cenário de demanda, porém, continua apenas desenhado, não calculado — pelas mesmas duas razões já citadas na entrada anterior (ADR 0017 ainda Proposta no lado de atração; contagens reais ainda `deferred`). A diferença é que, agora, a lacuna remanescente é inteiramente de dado, não mais de ferramenta.

No `outline.md`, a equipe acrescentou uma nota ao Capítulo 3 (quarta instância do padrão de fronteira da ADR 0009) e ao Capítulo 4 (fechamento da lacuna de ferramenta do pipeline de demanda; a lacuna de dado não mudou).

**Perguntas abertas/riscos.**
1. A matriz OD de P3.2 continua bloqueada no lado de atração (GeoSanja, ADR 0017 Proposta). Sem ela, `od2trips` não tem entrada real para converter. A mecânica deste commit continua não exercida contra SJC.
2. As contagens de tráfego de SJC continuam `deferred` no inventário de dados, sem contato autorizado com a agência. Sem elas, `routeSampler` não tem alvo de calibração. O critério de aderência (GEH/RMSE, já citado na ADR 0013) não pode ser medido.
3. O teste de bancada local contra os binários reais do SUMO 1.28.0 não foi reexecutado nesta sessão. Os números (192 testes, lint/tipagem limpos) foram só repassados no resumo do commit, não verificados em código.
4. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-10-29 (4) — Esquema de configuração de cenário (P3.6) formaliza, por primeiro, os elementos de uma "rodada de simulação" exigidos pelo roteiro — rede, demanda, janela de tempo e política de sementes/repetições —, ainda sem nenhuma instância real

**Commit:** `0c0c07a` ("feat: add scenario config schema (P3.6)"). A equipe leu o módulo `arteria/config.py` diretamente nesta sessão. O teste novo (`tests/fixtures/toy-scenario.yaml`), e a contagem de 195 testes/lint/tipagem, não foram reexecutados — só repassados.

**O que foi feito.** A equipe implementou a metade "apenas esquema" da etapa P3.6 do roteiro, a definição de cenário-base. `ScenarioConfig` e `load_scenario_config` foram acrescentados a `arteria/config.py`, ao lado dos esquemas já existentes de `CityConfig`/`DataManifest` (ADR 0003, já tratada nesta trilha na entrada do commit `0cbb61e`, 2026-10-25).

O esquema pydantic valida um arquivo de cenário (`cities/<cidade>/scenarios/<nome>/scenario.yaml`). Ele tem nome, cidade, descrição opcional, arquivo de rede, arquivo de zona de análise de tráfego (TAZ) opcional, lista de arquivos de rota, lista de arquivos adicionais, janela de tempo opcional, e uma política de sementes/repetições. Um validador de pós-carga rejeita o cenário se o número de sementes fornecidas não bater com o campo `replications` — quando sementes de fato forem fornecidas.

O commit segue, de forma explícita no próprio módulo, o mesmo padrão minimalista já usado no esquema do catálogo de intervenções da etapa P5.1 (`arteria/interventions/catalog.py`, ADR 0006, já tratada nesta trilha nas entradas de 2026-10-25): esquema apenas, sem nenhum comando de CLI associado.

O próprio módulo declara que uma instância real de `cities/sjc/scenarios/baseline/` exigiria arquivos de rota reais (rotas de veículo), que ainda não existem. Essa instância depende de dois bloqueadores a montante, já registrados nas duas entradas imediatamente anteriores deste log: o lado de atração do modelo gravitacional de P3.2 (camada de uso do solo do GeoSanja, ADR 0017 ainda Proposta) e a execução real orientada por contagem de P3.3 (contagens de tráfego reais de SJC, ainda `deferred`).

Por decisão deliberada, o commit não cria um `cities/sjc/scenarios/baseline/scenario.yaml` de fato, com referências de arquivo falsas. Isso evita apresentar um stub não executável como se fosse um cenário-base.

**Por que importa.** Esta é a primeira vez que o repositório reúne, sob um único esquema validado, exatamente os elementos que definiriam uma rodada/episódio de simulação para o Objetivo específico 1 desta trilha (ambiente de treinamento via TraCI): qual rede usar, qual demanda (arquivos de rota), qual janela de tempo, e quantas repetições com quais sementes.

Antes deste commit, cada um desses elementos existia isoladamente. A rede estava em `build.py`. A demanda prevista estava em `trips.py` (entrada de 2026-10-29 (3)). As sementes/repetições existiam só como ferramenta estatística pós-hoc em `replication.py` (entrada do commit `2af2152`, 2026-10-25). Não havia nenhum contrato único que amarrasse todos esses elementos como definição de uma rodada, antes dela começar.

Nesse sentido, o esquema contribui de forma distinta e complementar à lacuna "número de seeds/repetições", já nomeada no Capítulo 4 e já parcialmente endereçada por `replication.py`. Aquele módulo calcula média/IC por aproximação normal, depois de uma rodada já executada. Já `ScenarioConfig` valida, no momento de carregar a configuração, que a lista de sementes declaradas é consistente com o número de repetições pretendido. É uma checagem de contrato antes da execução, não uma análise estatística depois dela.

Mas o esquema em si não decide quantas repetições bastam, nem qual aproximação estatística usar. Essas perguntas continuam em aberto — agora só com um lugar formal onde a resposta eventual seria declarada.

A decisão deliberada de não criar um `scenario.yaml` placeholder, com caminhos de arquivo falsos, reforça — sem alterar — a mesma linha de honestidade já aplicada ao longo deste log a outros stubs e marcos de engenharia (fronteira da ADR 0009; ressalva de Cities: Skylines no pré-projeto; `randomTrips.py` como checagem visual, nunca baseline). Em vez de simular que um cenário-base já existe, o commit prefere deixar a lacuna explicitamente aberta, até que os dois bloqueadores de dado sejam resolvidos.

**Impacto na tese.** Em `chapters/04-experimentos.md`, a Seção 4.1 recebeu um parágrafo novo. Ele registra que a lacuna "seeds/repetições" tem, agora, uma segunda peça de infraestrutura: validação de contrato na carga do cenário, distinta e anterior à análise estatística pós-hoc de `replication.py`. Mesmo assim, ainda não existe nenhuma instância real de cenário, por depender dos mesmos dois bloqueadores de dado já registrados nas duas entradas anteriores (P3.2/ADR 0017; contagens `deferred`).

O parágrafo já foi redigido no registro acadêmico do guia de estilo: nível conceitual, sem caminho de arquivo, nome de classe/função ou número de ADR no corpo do texto, voz impessoal. O guia foi lido por completo nesta rodada, antes da edição. O restante da Seção 4.1, ao redor desse parágrafo, continua no registro técnico anterior (cita caminho de arquivo e números de ADR) — não foi reescrito, porque não é o trecho afetado por este commit.

No `outline.md`, a equipe acrescentou uma nota de rastreio ao Capítulo 3 (terceira instância do padrão "esquema primeiro, mecanismo/execução depois", já visto em `catalog.py`/ADR 0006) e ao Capítulo 4 (esquema de cenário como segunda peça da lacuna de seeds/repetições).

**Perguntas abertas/riscos.**
1. Nenhuma instância real de cenário existe ainda. `ScenarioConfig` continua bloqueado pelos mesmos dois gaps de dado já registrados nas entradas de 2026-10-29 (2) e (3) deste log: lado de atração do modelo gravitacional; contagens reais de SJC.
2. A relação entre `ScenarioConfig` e o manifesto de proveniência (`RunManifest`, `arteria/provenance.py`, já rastreado na entrada do commit `eefc81c`, 2026-10-24) ainda não foi definida em código. Não está claro se uma futura execução de treinamento vai gravar o hash do arquivo de cenário como parte da proveniência de uma rodada, ou se os dois artefatos vão continuar desconectados.
3. A contagem de 195 testes, e a fixture `tests/fixtures/toy-scenario.yaml`, não foram reexecutadas nem lidas nesta sessão — só repassadas. O próprio esquema (`arteria/config.py`), porém, foi lido diretamente.
4. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---

## 2026-11-03 — Sem conteúdo para esta trilha: ferramenta de preparo de mapa para Cities: Skylines (trilha hobby decoupled)

**Commit:** `8bb6175` ("feat: add Cities: Skylines map-prep tool and mod-set decision"). Resumo repassado pelo orquestrador, não verificado nesta sessão.

**Avaliação.** O commit decide a edição e o conjunto de mods do Cities: Skylines (ADR 0011). Ele adiciona um comando de CLI que calcula centróide/bbox de um corredor, para colagem manual em Overpass/Cimtographer. Também documenta um procedimento manual de desktop (Windows, GUI) para importação de terreno, ruas e imagem de referência.

Trata-se de trabalho da Fase 8 do roteiro (P8.3). É uma trilha ilustrativa, de comunicação com stakeholders, explicitamente desacoplada (ADR 0015) do pipeline de demanda/RL em andamento na Fase 3. Não tem conteúdo de arquitetura de RL/GNN, de dados de rede/demanda, nem de literatura.

Este trabalho não altera a ressalva já fixada nesta trilha (`chapters/04-experimentos.md`, L24; pré-projeto, Seção 13): Cities: Skylines é camada de comunicação, nunca evidência quantitativa. Pelo contrário, este trabalho reforça essa ressalva, com rotulagem obrigatória "ilustrativo, não calibrado" em toda captura ou vídeo.

Nenhum capítulo, `outline.md` ou `pre-projeto.md` foi editado nesta entrada.

---

## 2026-11-04 — Sem conteúdo para esta trilha: manutenção de mods, aquisição de heightmap e primeira cidade jogável do Cities: Skylines 1 (trilha hobby desacoplada, três commits)

**Commits:** `4be1977` ("fix: correct C:S 1 mod picks in ADR 0011 after Cimtographer went unmaintained"), `4b0833c` ("feat: build C:S 1 heightmaps from real SRTM data instead of terrain.party"), `2ee4eab` ("docs: build first playable C:S 1 city and document the import pitfalls"). Resumo repassado pelo orquestrador, não verificado nesta sessão.

**Avaliação.** Os três commits continuam o mesmo roteiro da Fase 8 (P8.3/P8.5), já avaliado na entrada anterior (2026-11-03, `8bb6175`): preparo de mapa e construção de uma cidade de Cities: Skylines 1, para comunicação visual com stakeholders. É uma trilha explicitamente desacoplada do pipeline de demanda/RL/GNN em andamento na Fase 3 (ADR 0015).

O primeiro commit corrige a escolha de mod de importação na ADR 0011, depois de o mod original ficar sem manutenção. Ele substitui esse mod por um fork verificado.

O segundo commit troca uma ferramenta de heightmap dependente de navegador por um comando de CLI. Esse comando busca elevação real (SRTM) numa API pública roteirizável.

O terceiro commit documenta a construção, de ponta a ponta, da primeira cidade jogável para os corredores B+D de SJC. Ele traz dois achados técnicos sobre a combinação do jogo com o mod de importação: um limite de ~7.378-12.173 vias para uma exceção de importação, cuja causa raiz é um limite de ~32.768 segmentos/nós de rede por cidade, do próprio motor do jogo; e a descoberta de que a etapa de busca e filtro de dados do OpenStreetMap (OSM) é roteirizável via Overpass, ao contrário das ferramentas de terreno travadas por navegador.

Nenhum dos três commits introduz arquitetura de aprendizado por reforço multiagente, de redes neurais em grafos, dado de rede/demanda da rede SUMO/OSM da trilha principal (Fase 3), ou literatura relevante à dissertação.

Os achados sobre o limite de segmentos do motor do jogo, e sobre a diferença entre ferramentas roteirizáveis (Overpass) e travadas por navegador (terrain.party/Heightmapper), são específicos à cadeia de importação de um motor de jogo. Eles não se transferem ao pipeline de construção de rede SUMO, já documentado nas entradas de 2026-10-26 a 2026-10-29 deste log. São ferramentas, formatos e limites de engine inteiramente distintos.

A ressalva já fixada nesta trilha (`chapters/04-experimentos.md`; pré-projeto, Seção 13) — de que Cities: Skylines nunca é evidência quantitativa — permanece intacta. Este trabalho não a afeta.

Nenhum capítulo, `outline.md` ou `pre-projeto.md` foi editado nesta entrada.

---

## 2026-11-06 — Lote de seis itens do roadmap em paralelo: conector novo fecha metade do gap estrutural do catálogo; checagens de validade isoladas; relatórios de calibração e de antes/depois; primeiro otimizador evolutivo (NSGA-II) sobre o catálogo de intervenções, ainda sobre avaliador sintético

**Commits:** `3ce3287`, `992b9de`, `dea95f8`, `f4f9387`, `5ad4339`, `88f145c`, `6cba0f2` (branch `ccr-0ddc589e-4ijfgg`, já mesclada ao `main` e enviada). O resumo repassado pelo agente orquestrador é a fonte autoritativa desta entrada. Nenhum dos seis módulos foi lido diretamente nesta sessão — todos foram só descritos pelo resumo recebido. Vale a mesma ressalva de verificação já aplicada a outros lotes repassados neste log.

**O que foi feito.** Seis itens do roteiro foram tentados em paralelo, em sessões isoladas (subagentes em worktrees distintas), e depois mesclados em sequência nessa branch. A versão do projeto passou para 1.11, com a entrada correspondente no histórico de versões do ArterIA.

O primeiro item (roteiro P5.2) adicionou a transformação de conector novo. Dadas duas junções existentes da rede, a função cria uma aresta nova ligando as duas. Ela reporta conexões plausíveis e as junções recém-reconectadas, mas não decide por conta própria quais conexões criar dentro das novas interseções.

Um commit separado ligou essa transformação ao despachante de catálogo já existente (`apply_intervention()`, já rastreado nesta trilha nas entradas de 2026-10-25 sobre os commits `3f4cf1d`/`2624762`). Com isso, dos dez tipos do catálogo, só faixa reversível e prioridade semafórica para transporte público continuam sem mecanismo de transformação.

O segundo item (P5.4) adicionou um módulo independente de checagens de validade de rede. Ele junta três verificações sob uma única função: conectividade (detecção de junção desconectada), continuidade de rotas nomeadas (verificação por conexão direta, pensada para rotas de emergência e de transporte público) e continuidade para pedestres.

Esse módulo foi deliberadamente deixado fora do despachante de catálogo. A razão: ainda falta decidir, por desenho, quais rotas checar e com que critério, por cidade.

O terceiro item (P4.7) adicionou um gerador de relatório de calibração. Ele junta o resumo de aderência (estatísticas GEH, RMSE e MAPE) e os resumos de repetição por métrica — já existentes como ferramentas isoladas (entradas de 2026-10-25 sobre `goodness_of_fit.py`/`replication.py`) — num relatório único, em texto estruturado.

Esse relatório traz um veredito de aprovação/reprovação, a ressalva da aproximação normal do intervalo de confiança (explicitada no próprio relatório), e um aviso: nenhum número gerado em sessão remota é achado de dissertação, nem de relatório de política, até ser validado por uma execução real de desktop, com o registro de proveniência correspondente.

O quarto item (P6.6) adicionou um gerador de relatório de antes/depois. Ele transforma pares de resumos de métrica em tabelas comparativas de texto estruturado, mais uma narrativa em linguagem simples. Essa narrativa aponta a maior melhoria e a maior regressão entre um cenário de referência e um cenário de intervenção.

Por decisão deliberada, este item se restringe a tabelas. Mapas e gráficos ficam fora do escopo desta entrega remota.

O quinto item tem a relevância mais direta para esta trilha, por ser um candidato a otimizador de nível superior. Ele implementou um otimizador evolutivo multiobjetivo (NSGA-II, biblioteca `pymoo`, nova dependência do projeto) sobre o catálogo de intervenções.

O problema de otimização define um vetor de decisão booleano, uma entrada por item do catálogo. A viabilidade é restrita pelas exclusões mútuas já declaradas no esquema de catálogo (ADR 0006, já rastreada nesta trilha) e por um orçamento monetário opcional. A avaliação de cada pacote candidato é, por ora, inteiramente sintética: uma função substituta explícita, documentada como nunca equivalente a uma estimativa real de impacto de tráfego. Um mecanismo de cache em texto estruturado evita reavaliar um pacote idêntico já visto.

Segundo o próprio resumo repassado, continuam em aberto: a redação de uma ADR específica para essa decisão de otimizador; a ausência de alternativas bayesianas (optuna/BoTorch) e de linhas de base aleatória/greedy para comparação; a ausência de um backend de avaliação paralela; a ausência de registro de experimentos no estilo MLflow; e o fato de que uma execução "retomada" reaproveita os acertos de cache, mas reinicia a população do algoritmo genético do zero.

Nenhuma camada substituta em rede neural em grafos (GNN, roteiro P7.4), nem nenhuma trilha de aprendizado por reforço (RL, roteiro P7.5), foi tocada neste item. Trata-se só da camada evolutiva clássica (NSGA-II), operando sobre um avaliador sintético.

O sexto item, de demanda (P3.1-P3.3), foi, com razão, um não-evento. A sessão correspondente verificou que os módulos de zoneamento, população e geração de viagens, além da ADR 0017, já estavam implementados e mesclados ao `main` (ver entradas de 2026-10-29 deste log). A sessão recuou, em vez de duplicar ou sobrescrever código já funcional.

Todos os itens implementados (do primeiro ao quinto) foram testados só contra fixtures de brinquedo escritas à mão — ou, no caso do otimizador, contra o avaliador sintético, com dados também sintéticos. Conforme a fronteira de sessão remota já fixada pela ADR 0009, nenhum dos cinco tocou dado real de SJC, nem uma execução real do simulador.

**Por que importa.** O primeiro item é o mais direto sobre o gap de catálogo que esta trilha já vinha acompanhando, desde a entrada de 2026-10-25 sobre o commit `bf725e9`. Naquela entrada, registrou-se que o Candidato B (primeira prioridade de produto do ArterIA) provavelmente exigiria uma primitiva de conector novo, até então inexistente. Registrou-se também que a fratura entre primitivas estruturais (alocação de faixas e sentidos, centrais a esta dissertação) e primitivas de sinalização (correlatas) ficaria mais nítida à medida que cada tipo fosse implementado.

Com o conector novo agora com mecanismo de transformação, e ligado ao despachante, a lacuna estrutural do catálogo passa a conter só faixa reversível. A lacuna de sinalização passa a conter só prioridade semafórica para transporte público. Ou seja: as duas lacunas remanescentes já não se confundem com nenhuma outra primitiva. O catálogo estrutural está, pela primeira vez, mais completo do que o catálogo de sinalização. Isso reforça, e não contradiz, o enquadramento original desta dissertação.

A ressalva já registrada, porém, continua válida, sem alteração: a viabilidade de um conector novo para o Candidato B ainda não foi confirmada. Qualquer alegação de benefício em nível de rede para esse conector continuaria vedada pela ADR 0013 (microdados de pesquisa origem-destino permanentemente recusados) — restrita ao efeito local ou de corredor.

O quinto item tem a maior relevância conceitual para esta trilha. É a primeira peça de código do ArterIA que de fato instancia um otimizador de nível superior sobre o catálogo de intervenções — exatamente o papel que o pré-projeto, na Seção 9, reserva de forma deliberadamente aberta a um algoritmo genético, a otimização bayesiana, ou a aprendizado por reforço.

Ao escolher, nesta primeira instância, a camada evolutiva clássica (NSGA-II) em vez de aprendizado por reforço multiagente, o ArterIA como produto oferece um primeiro ponto de comparação concreto — ainda que com avaliador sintético. Esse ponto de comparação ajuda a dissertação a justificar por que o aprendizado por reforço multiagente é preferível a uma busca evolutiva sobre o mesmo espaço de decisão booleano. A Seção 6 do pré-projeto já antecipa essa comparação, como parte da literatura de desenho bi-nível de rede (*bi-level network design problem*). Até este item, porém, não havia nenhum concorrente de código real do próprio projeto para servir de contraponto.

Esse avaliador sintético, contudo, significa que nenhuma conclusão sobre desempenho de busca, qualidade da frente de Pareto ou custo computacional é, por ora, transferível a uma avaliação real de tráfego. A função substituta mede só se o mecanismo de busca funciona sobre o espaço de decisão do catálogo — não se a solução encontrada é boa para o tráfego de SJC.

Os itens segundo, terceiro e quarto são infraestrutura de avaliação e de relato. Eles começam a dar forma concreta ao que os Capítulos 4 e 5 vão precisar descrever quando houver resultado real.

A checagem de validade formaliza, pela primeira vez como função de biblioteca (ainda não ligada ao despachante), um critério mínimo de aceitabilidade de um pacote de intervenções, antes de qualquer avaliação de tráfego. O relatório de calibração, e o relatório de antes/depois, formalizam o formato em que a aderência do modelo e a comparação de cenários seriam comunicadas. Os dois incluem, de forma explícita e já no próprio artefato de código, as mesmas ressalvas de honestidade que esta trilha já exige na prosa: aproximação normal do intervalo de confiança; número de sessão remota nunca é achado de dissertação sem validação de desktop.

Nenhum dos três, porém, está ligado a um agente de aprendizado por reforço, a uma GNN, ou a dado real de SJC.

**Impacto na tese.** Em `chapters/03-arquitetura-do-sistema.md`, a Seção 3.6 (estágio de esboço) foi atualizada. O número de tipos de catálogo já despachados pela função de aplicação de intervenções passou de sete para oito dos dez — o conector novo saiu da lista de primitivas sem mecanismo. A mesma seção recebeu uma nota nova, registrando a existência do otimizador evolutivo como primeiro concorrente de código real ao papel de otimizador de nível superior, com a ressalva do avaliador sintético.

Em `chapters/04-experimentos.md`, a Seção 4.2.1 (orçamento computacional) recebeu uma frase registrando que a política de retomada do otimizador reinicia a população do algoritmo genético do zero, mesmo reaproveitando acertos de cache. Esse detalhe é relevante para o planejamento de campanhas de busca, dentro do teto de hardware já registrado naquela seção.

No `outline.md`, notas de rastreio foram adicionadas aos Capítulos 3 e 4, cobrindo os cinco itens implementados. Nenhuma prosa adicional foi reescrita, além dessas inserções pontuais.

**Perguntas abertas/riscos.**
1. A viabilidade de um conector novo para o Candidato B continua não confirmada. Mesmo com o mecanismo de transformação já disponível, qualquer leitura de recompensa ou de política associada a essa primitiva — caso venha a ser exposta a um agente de aprendizado por reforço desta dissertação — deve continuar restrita ao efeito local/de corredor, nunca a uma alegação de benefício de rede (ADR 0013).
2. O avaliador sintético do otimizador evolutivo não tem, por ora, nenhuma ligação com o simulador de tráfego. A comparação conceitual entre busca evolutiva e aprendizado por reforço multiagente, mencionada acima como relevante ao Capítulo 2, só se torna evidência quando — e se — um avaliador real de tráfego substituir a função substituta sintética nos dois lados.
3. A decisão de desenho pendente sobre quais rotas checar na continuidade de emergência/transporte público (segundo item), e a ausência de linhas de base aleatória/greedy e de alternativas bayesianas para o otimizador evolutivo (quinto item), são lacunas nomeadas pelo próprio resumo repassado. Elas não foram verificadas em código nesta sessão.
4. Os números e detalhes de mecanismo relatados nesta entrada vêm do resumo repassado pelo agente orquestrador. Eles não foram lidos em código nem reexecutados nesta sessão. Valem as mesmas ressalvas de verificação já aplicadas a outros lotes deste log, antes de qualquer um desses números ser citado como fato consolidado em capítulo.
5. O(A) orientador(a) ainda não foi contatado(a). A arquitetura de agentes continua não validada. A escolha acadêmica de corredor segue pendente.

---
