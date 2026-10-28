# Log de Progresso — Trilha ITA PG/EEC (Informática) — append-only

Status: ativo
Profundidade: completo

> Formato: entradas em ordem cronológica, **mais recente ao final**. Histórico anterior a 2026-10-26 (modo `leve`, mais recente no topo) permanece em `progress.md`, congelado como arquivo histórico.

---

## 2026-10-26 — Marco v1.0: primeira rede real do corredor B; validador expõe a distância entre fixtures e rede real

**Commits:** `72ef5cb` (ADR 0014, WSL2), `25eb78f`/`1d2c6ad`/`ca6b153` (docs de setup), mais alterações ainda não commitadas na data (`arteria/network/build.py`, `cities/sjc/study-areas.yaml`/`.geojson`, `docs/visualization-plan.md`, `CHANGELOG.md` [1.0]). TODO(rastreio): substituir por hash quando o commit existir.

**O que foi feito.** Realizou-se a primeira execução real ponta a ponta no desktop WSL2: `arteria studyarea build` (Nominatim) → `arteria osm fetch --candidate b` → `arteria network build` (`osmium cat` PBF→XML, depois `netconvert`) → `sumo-gui` com 1.800 veículos aleatórios (415 viagens inviáveis descartadas). Apenas o corredor B foi renderizado.

A execução exigiu correções: o `netconvert` não lê PBF; três consultas Nominatim estavam erradas (uma resolvia ~30 km ao norte); e `ARTERIA_DATA` passou a ser `data/`, ignorado pelo git. O validador (`arteria network validate`), por sua vez, acusou 729 erros e 7.562 avisos na rede real, em grande parte falsos positivos ou efeito de recorte; contudo, 2 erros de `traffic_light_logic` são reais (2 de 18 junções semafóricas), de impacto não verificado.

**Por que importa.** Pela primeira vez, a trilha dispõe de um grafo viário real (ainda não medido) e de evidência de que a qualidade desse grafo condiciona tudo o que vem depois: a observação dos agentes, a escolha de nós e arestas da GNN e a definição de métricas de acessibilidade. Ademais, observa-se que validadores desenvolvidos sobre fixtures não se transferem para redes reais, argumento metodológico próprio da dissertação.

**Impacto na tese.** No Cap. 3 (`chapters/03-arquitetura-do-sistema.md`), criaram-se as novas Seções 3.2 a 3.5 em `rascunho` (construção da rede, validação estrutural real vs. fixtures, rede como grafo e implicações para RL/GNN, proveniência), ficando o capítulo com status `rascunho` parcial. No Cap. 4 (`chapters/04-experimentos.md`), a Seção 4.2 "Estudo de caso: corredor B" entrou em `rascunho`, explicitamente sem valor probatório. Os Caps. 1, 2, 5, 6 e 7 foram criados como `stub`, e o `references.bib` foi iniciado com 5 entradas (SUMO, OSM x2, OSMnx, Tarjan) a conferir. No `pre-projeto.md`, por fim, a Seção 9 foi corrigida (calibração de demanda não mais "a partir da Pesquisa OD", conforme ADR 0013), e os riscos de qualidade do grafo foram adicionados à Seção 12.

**Perguntas abertas/riscos.**
1. A escolha de corredor da dissertação ainda não é decisão acadêmica; B é prioridade de produto. Há, assim, risco de coincidência por conveniência de engenharia.
2. Rede unificada vs. por corredor altera o tamanho do grafo e o número de agentes; trata-se de decisão futura do responsável (talvez ADR).
3. Nenhum número de tamanho da rede foi reportado; nada além das contagens acima foi usado.
4. Risco de a dissertação deslocar-se para "engenharia de dados geoespaciais"; como contrapeso, mantém-se RL/GNN como núcleo e trata-se a qualidade do grafo como fator experimental (ablações), não como fim.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-26 (2) — Rede única de SJC (ADR 0016), validador adaptado a redes reais, benchmark de hardware

**Commits:** `a55c9d7` (ADR 0016), `72ab33e` (validador), `814f4c9` (benchmark), `ffcbd8e` (smoke real com SUMO); merges `8948351`, `736af5d`, `467ba96`, `e9b9d64`.

**O que foi feito (no repositório).** Em primeiro lugar, construíram-se redes OSM->SUMO para D, C e A, e decidiu-se (ADR 0016, `Accepted`) usar uma única rede de SJC no envelope de todos os candidatos: 11.035 arestas, 94,0% no maior componente fortemente conexo (individuais: B 2.074/85,1%; D 1.203/69,9%; C 919/86,9%; A 2.256/88,3%), com B/D/C/A como áreas de avaliação. Em seguida, o `arteria network validate` foi reescrito para SCC, pares de arestas opostas e becos de borda; na rede real de B, os erros passaram de 729 para 0. O benchmark do PC (6c/12t, 9,7 GiB RAM), por sua vez, estimou um NSGA-II de 10k execuções em 35-45 h (inviável como planejado), levando à adoção de lotes de sementes com 4 trabalhadores. Por fim, o `nox -s smoke` real passa com SUMO (wheel `eclipse-sumo`); trata-se de infraestrutura, sem conteúdo de pesquisa, e não foi registrada em capítulo.

**Por que importa.** A rede única fixa o grafo sobre o qual agentes e GNN operarão (ordem de 10^4 arestas) e evita cortar fluxos de passagem via Anel Viário; contudo, aumenta o custo por simulação. O fechamento dos 729 erros mostra, ademais, que o validador, e não a rede, era a principal fonte de ruído, reforçando o argumento de 3.3 (validação em fixtures não se transfere). O benchmark, por fim, delimita o orçamento de episódios de treinamento e fortalece a motivação do surrogate em GNN.

**Impacto na tese.** No Cap. 3, a 3.2 foi parcialmente reescrita (rede única, tamanhos da ADR) e a 3.3 recebeu atualização (`rascunho`). No Cap. 4, o TODO de 4.2 foi atualizado e criou-se a nova 4.2.1 de orçamento computacional (`rascunho`). O `outline.md` recebeu duas notas; os demais capítulos ficaram inalterados.

**Perguntas abertas/riscos.**
1. Com rede única e quatro áreas, como definir agentes e recompensa (por área, junção ou aresta)? Há risco de explosão do espaço de ação em 11 mil arestas.
2. A escolha acadêmica do corredor segue pendente e distinta da prioridade de produto; a rede única pode, ademais, induzir um escopo de quatro corredores incompatível com um mestrado.
3. O detalhe do `72ab33e` (destino dos 2 erros `traffic_light_logic`; distribuição de componentes) não foi verificado nesta entrada, apenas a mensagem do commit.
4. Orçamento computacional: MARL com SUMO em 9,7 GiB de RAM é restritivo, e a decisão de nuvem/nó universitário está pendente. As estimativas não foram medidas.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-27 — Corredores como sequências de arestas na rede unificada; áreas B e C estendidas; desk check de tags OSM (trabalho NÃO commitado; base `b24377a`)

**Commits:** nenhum. Registro do working tree: `cities/sjc/corridors/` (README, `corridors.geojson`, `summary.json`, KML, `build_corridors.py`), `cities/sjc/study-areas.{yaml,geojson}`, `candidate-corridors.md`, `data-manifest.yaml`, ADR 0016, `CHANGELOG.md` [Unreleased]. Itens sujeitos a mudança antes do commit.

**O que foi feito (no repositório, segundo README/CHANGELOG; não reexecutado aqui).**
1. Os corredores A, B (derivado), C, D e a ligação A-B foram desenhados como sequências ordenadas de arestas SUMO sobre a rede unificada (ADR 0016), por caminho de menor custo dirigido entre pontos de referência do OSM, roteando cada trecho nos dois sentidos. A ligação A-B, por exemplo, tem 14 arestas/883 m (A para B) e 18 arestas/1.286 m (B para A), e nenhum trecho ficou inroteável. O README atribui a assimetria a rampas de mão única, a partir da geometria OSM.
2. As áreas de estudo foram estendidas: B de 5,31 para 7,67 km2 (ao sul, Av. Cassiopeia/Av. Perseu) e C de 1,54 para 4,17 km2 (Parque Vicentina Aranha, Av. Rio Branco etc.). A rede unificada foi, em seguida, reconstruída: 14.225 arestas, 6.655 junções, 93,1% das junções no componente principal, 0 erros de validação (eram 11.035 arestas na ADR 0016 inicial). Os ids de arestas mudaram com a reconstrução.
3. No desk check de dados de SJC, mediu-se a completude de tags OSM no candidato B: vias principais bem etiquetadas; ruas residenciais com `lanes` em ~4% e `maxspeed` em ~5%. GeoSanja e IBGE NÃO foram confirmados como fontes disponíveis.
4. O SUMO 1.28 carrega a rede real sem avisos; os 2 clusters `traffic_light` sem programa carregam como não semaforizados (inofensivos).
5. A reconciliação do roteiro com a ADR 0014 (WSL2) é de dev-process, sem conteúdo para a trilha, e não foi registrada em capítulo.

**Ressalvas obrigatórias.** Toda a geometria dos corredores deriva do OSM e AINDA NÃO foi verificada por imagem aérea pelo responsável. O corredor B por arestas é novo (antes só existia o polígono, checado por imagem aérea), de modo que não herda aquela verificação. A direção da extensão de C (oeste/sudoeste, não norte) aguarda, ademais, confirmação do responsável. Nada disso é validação nem escolha acadêmica de corredor, e nenhum agente, GNN ou recompensa foi conectado a estes artefatos.

**Por que importa.** Em primeiro lugar, as sequências de arestas dão a primeira definição concreta de "corredor" como subgrafo orientado, útil para delimitar observação, ação e recompensa por área (pergunta aberta 1 da entrada anterior) sem tratar 14 mil arestas como espaço de ação. Em segundo lugar, o desk check (lanes ~4%, maxspeed ~5% em ruas residenciais) indica que os atributos de faixa e velocidade serão em grande parte imputados fora das vias principais, o que afeta as características de aresta da GNN e os torna candidatos a fator de ablação, reforçando o risco de qualidade do grafo já registrado. Por fim, as assimetrias direcionais (883 m vs 1.286 m) são exemplos reais do que a representação em grafo orientado deve preservar.

**Impacto na tese.** O `outline.md` recebeu uma nota no Cap. 3. A prosa dos capítulos NÃO foi alterada: o número 11.035 em `chapters/03` (3.2) e `chapters/04` (TODO de 4.2) está defasado frente a 14.225 e deve ser atualizado após o commit e a resolução das ressalvas, para não consolidar números provisórios.

**Perguntas abertas/riscos.**
1. Agente/recompensa por corredor (subgrafo) versus por junção: decisão de modelagem pendente, com risco de quatro corredores excederem o escopo de um mestrado.
2. Os percentuais de 4% e 5% vêm do relato do CHANGELOG, não verificados aqui; a metodologia (denominador, escopo) precisa, por isso, ser citada antes de entrarem no Cap. 3.
3. Sem GeoSanja/IBGE confirmados, os atributos de ruas locais serão imputados ou omitidos.
4. Verificação aérea dos corredores e da direção de C pelo responsável pendente; até lá, rascunho. [Resolvida na entrada seguinte, 2026-10-27 (2).]
5. Orientador(a) não contatado(a); arquitetura de agentes não validada.

---

## 2026-10-27 (2) — Checagem aérea aprovada; reprodutibilidade da construção da rede (Fase 2; trabalho NÃO commitado; base `0125f01`)

**Commits:** nenhum. Fontes: `CHANGELOG.md` [Unreleased] e `docs/roadmap.md` (Fase 2), lidos; o código novo (`arteria/network/{snapshot,rebuild,diff,patches}.py`, `cities/sjc/network/osm-snapshot.yaml`) NÃO foi lido nem reexecutado, e os números abaixo são relatos do CHANGELOG.

**O que foi feito.**
1. Na checagem aérea do responsável (2026-10-27, Google Earth), os corredores A, B, C, D, a ligação A-B e as áreas estendidas de B e C foram aprovados, incluindo a extensão de C a oeste/sudoeste. Tal checagem supera duas ressalvas da entrada anterior (geometria sem imagem aérea; direção de C não confirmada). Os números vigentes da rede unificada são 14.225 arestas, 6.655 junções e 93,1% das junções no componente principal (substituem 11.035 arestas/94,0% da ADR 0016 inicial).
2. Quanto à reprodutibilidade (Fase 2), fixou-se um snapshot OSM (Geofabrik Sudeste, PBF de 2026-10-25, sha256), e o `arteria network rebuild` reproduz o hash de conteúdo da rede (cabeçalho de timestamp do `netconvert` ignorado), com duas execuções idênticas, 0 erros/127 avisos e ~16 s. Introduziram-se, ainda, patches como segunda passada do `netconvert` (nenhum necessário ainda) e o `arteria network diff` (demonstração: B isolada vs. unificada, 12.175 arestas adicionadas/24 removidas/137 alteradas). Um teste de desktop confirma que todas as arestas dos corredores existem na rede. Nenhum GTFS público de SJC foi encontrado, de modo que a P2.6 foi adiada.

**Por que importa.** Ids de aresta estáveis e reconstruíveis são pré-condição de qualquer ambiente de RL/GNN sobre o grafo, uma vez que baseline, demanda e calibração dependem deles (ADR 0016). A falta de GTFS implica, por sua vez, que a rede não terá ônibus por ora, o que restringe intervenções de faixa de ônibus/prioridade semafórica, correlatas e não centrais ao escopo; o objeto estrutural (faixas/sentidos) não é, contudo, afetado de imediato.

**Impacto na tese.** No Cap. 3, a 3.2 (atualização de tamanhos, corredores, aprovação aérea) e a 3.5 (mecanismo de reprodutibilidade) ficaram em `rascunho`, via anexos, preservando-se o texto antigo como histórico. No Cap. 4, dois trechos de 4.2 foram sinalizados como defasados/atualizados. O `outline.md` recebeu notas no Cap. 3, e os demais capítulos ficaram inalterados.

**Perguntas abertas/riscos.**
1. As frações 94,0% (arestas, ADR 0016) e 93,1% (junções, relato atual) usam unidades distintas; não devem, portanto, ser comparadas sem verificar o validador.
2. O formato do registro de proveniência do `rebuild` e sua relação com `RunManifest` não foram verificados; ademais, a reprodutibilidade cobre só a construção da rede, não treinamento/simulação.
3. Sem GTFS, não há demanda nem rota de transporte público; a decisão de fonte alternativa (rotas manuais) está pendente do responsável.
4. Todo o material está no working tree; se mudar antes do commit, os anexos precisam de revisão.
5. Agente/recompensa por corredor versus junção segue sem decisão, e o escopo de quatro corredores pode exceder um mestrado. Orientador(a) não contatado(a).

---

## 2026-10-28 — Cross-check da rede OSM contra IBGE e GeoSanja (P2.1, P2.7); resolve lacuna de fontes de atributo de rua

**Commits:** `1c4a7b4` ("feat: cross-check SJC network against IBGE and GeoSanja (P2.1, P2.7)"). Os números abaixo são relato repassado pelo responsável do ArterIA, não reexecutados nem lidos em código nesta sessão; os caminhos foram confirmados por existirem no repositório (`arteria/network/crosscheck.py`, `arteria/network/render.py`, `cities/sjc/data-manifest.yaml`). TODO(evidência): ler `crosscheck.py` e reexecutar o comando antes de citar os números como fato assentado no capítulo.

**O que foi feito.** Dois novos comandos (`arteria network crosscheck --city sjc`, `arteria network render --city sjc`) comparam a rede SUMO/OSM construída (14.225 arestas, ver entrada 2026-10-27 (2)) contra duas fontes públicas de referência registradas em `cities/sjc/data-manifest.yaml`: a Base de Faces de Logradouros do IBGE (2022, shapefile estadual) e as camadas `arruamentos`/Hierarquia Viária do GeoSanja (portal da prefeitura de SJC). O cross-check restringe-se aos quatro corredores do estudo (buffer de 50 m em torno da união dos polígonos) e compara por nome de rua normalizado (contra IBGE) e por geometria/cobertura de centro de linha amostrado a cada 5 m (contra IBGE e GeoSanja, limiar de 15 m).

Os resultados relatados (não commitados; saídas gitignored em `data/crosscheck/` e `data/renders/`) indicam 543 nomes de rua coincidentes dentro dos corredores (167 só-OSM, 201 só-IBGE); distância mediana amostra-referência de ~3,0 m; 6,4% das amostras acima de 15 m; 81,5% do comprimento OSM dentro de 15 m do GeoSanja e 97,2% do GeoSanja dentro de 15 m do OSM. Parte dos descasamentos de distância alta é atribuída a nomes de rua genéricos/reutilizados (ex. "Rua Dois", "Viela Três") que casam por nome entre ruas distintas, e não a erro de geometria. Geraram-se, também, renders de mapa (rede colorida por prioridade de aresta do SUMO, com os quatro contornos de área de estudo), não commitados.

Surgiu, ademais, uma questão nova e ainda não corrigida: os nomes de rua OSM na rede construída carregam um artefato de escape duplo de `&apos;` (afetando algumas dezenas de nomes com apóstrofo, ex. "D'Ávila"), com origem suspeita no `netconvert` ou depois, não diagnosticada.

**Por que importa.** A entrega resolve, com dados concretos, a lacuna registrada em duas entradas anteriores deste log ("GeoSanja e IBGE NÃO confirmados como fontes disponíveis", 2026-10-27) e no `outline.md` (Cap. 4: "apenas a topologia da malha viária tem fonte de autoatendimento confirmada [OSM/Geosanja/IBGE]" — agora com número de fato, não apenas fonte listada em manifesto). Trata-se do primeiro cross-check quantitativo da completude/precisão geométrica do grafo derivado de OSM contra fontes públicas independentes, pré-condição direta do Objetivo específico 1 (representação em grafo) e do argumento central de 3.3/3.4 (a qualidade do grafo OSM condiciona observação, ação e GNN).

Os números (81,5-97,2% de cobertura geométrica dentro de 15 m; ~37% dos nomes só-OSM ou só-IBGE) dão, por ora, a primeira medida substituta de completude referida como `TODO(citação)` em 3.3 (`haklay2010osm`/`barrington2017osm`); contudo, não substituem a literatura de qualidade do OSM, apenas a complementam com um dado local. O próprio commit e o relato classificam a entrega como cross-check de triagem (casamento de nome não ajustado fino), e não como etapa de calibração — distinção que a dissertação deve preservar, já que não se trata de validação de atributos de faixa/sentido (lanes/maxspeed, ainda ~4%/~5% em ruas residenciais segundo a entrada de 2026-10-27), apenas de nome e geometria de via.

**Impacto na tese.** No Cap. 3 (`chapters/03-arquitetura-do-sistema.md`), há uma nova atualização a registrar em 3.3 (cross-check como segunda camada de verificação, além do validador estrutural) e em 3.4 (completude do OSM, ponto 5, agora com número local além da citação genérica); o texto do capítulo ainda não foi editado nesta sessão, ficando como TODO para a próxima revisão de prosa. No `outline.md`, as notas do Cap. 3 e do Cap. 4 (linha sobre fonte confirmada de topologia) devem ser atualizadas para refletir que a confirmação de disponibilidade já ocorreu, com número associado.

**Perguntas abertas/riscos.**
1. O cross-check não cobre atributos estruturais (faixas, sentido, restrições de giro) — apenas nome e geometria do eixo da via; o risco de qualidade de `lanes`/`maxspeed` registrado em 2026-10-27 permanece, assim, integralmente aberto.
2. ~~Artefato de escape duplo (`&apos;`) em nomes de rua com apóstrofo~~ — **resolvido em `1895aeb`, ver addendum abaixo (2026-10-28 (2)).**
3. Os descasamentos de mediana alta por nomes genéricos reutilizados ("Rua Dois") sugerem que o casamento por nome tem limite estrutural nesta malha; qualquer uso futuro desse cross-check como insumo de qualidade de dado (não apenas triagem) precisaria, por isso, de casamento por nome+geometria conjunto, não nome isolado.
4. Números não verificados em código nesta sessão (apenas repassados); antes de citá-los no capítulo como fato, é preciso reexecutar `arteria network crosscheck --city sjc` e ler `crosscheck.py`.
5. Orientador(a) não contatado(a); arquitetura de agentes não validada; escolha acadêmica de corredor segue pendente.

---

## 2026-10-28 (2) — Addendum: artefato de escape duplo diagnosticado e corrigido (risco 2 acima resolvido)

**Commit:** `1895aeb` ("fix: undo netconvert's double-escaping of names"), CHANGELOG [1.3].

**O que foi feito.** A causa raiz foi confirmada por fixture OSM mínima de duas vias contra o binário real do `netconvert` 1.28.0: o `netconvert` escapa duplamente qualquer caractere especial de XML literal (`'`, `&`, `"`, `<`, `>`) presente numa tag `name` do OSM — primeiro substitui o caractere pela entidade XML nomeada internamente, e depois seu próprio escritor de saída escapa o `&` dessa entidade de novo (ex. apóstrofo vira `&amp;apos;`). Trata-se, portanto, de bug do próprio `netconvert`/SUMO, e não de erro de lógica do ArterIA.

Assim, `arteria.network.build.fix_double_escaped_names()` agora roda automaticamente após toda chamada de `netconvert` em `build_network`, corrigindo os atributos `name`/`origId` no `.net.xml` escrito; testes novos cobrem a função isolada, um caso no-op e um teste de ponta a ponta com fixture reproduzindo o padrão. A rede real de SJC foi, em seguida, reconstruída com a correção, e o snapshot OSM fixado (`cities/sjc/network/osm-snapshot.yaml`) foi repontado para o hash de conteúdo da rede corrigida: 58 caracteres corrigidos em exatamente 3 nomes de rua (ex. "Rua Armando D'Oliveira Cobra", antes "Rua Armando D&amp;apos;Oliveira Cobra"), com estrutura da rede inalterada (0 arestas/faixas/junções adicionadas, removidas ou alteradas; validação ainda com 0 erros, 127 avisos). Por fim, o cross-check de `1c4a7b4` foi reexecutado contra a rede corrigida: nomes coincidentes com IBGE passaram de 543 para 544 (um dos três nomes corrigidos agora casa corretamente), só-OSM de 167 para 166 e só-IBGE de 201 para 200; os números de geometria (mediana ~3,0 m, 6,4% acima de 15 m, 81,5%/97,2% de cobertura GeoSanja) ficaram essencialmente inalterados.

**Por que importa.** A correção fecha, com causa raiz identificada e correção automática aplicada (não apenas contorno manual), o risco 2 registrado na entrada anterior (2026-10-28) e já citado em `chapters/03-arquitetura-do-sistema.md` (3.3) como "achado colateral ainda não corrigido". Os nomes de rua em `sjc.net.xml` podem, agora, ser citados diretamente em figuras, tabelas e texto sem o artefato de apóstrofo — ponto relevante porque a nota de 3.3 havia marcado explicitamente esse artefato como impeditivo para qualquer uso futuro de nome de rua como chave de junção com dados de calibração/contagem municipal.

**Impacto na tese.** Em `chapters/03-arquitetura-do-sistema.md`, 3.3 (nota de `1c4a7b4`, trecho final), acrescentou-se uma frase registrando a correção e os novos totais (544/166/200), sem reescrever o restante da nota. No `outline.md`, a nota do Cap. 3 (2026-10-28, `1c4a7b4`) foi marcada como superada neste ponto específico.

**Perguntas abertas/riscos.**
1. Os três nomes afetados e o novo total 544/166/200 não foram verificados em código nesta sessão (apenas repassados do CHANGELOG); vale a mesma ressalva já registrada para os números de `1c4a7b4` — reexecutar `crosscheck.py` antes de consolidar na prosa.
2. `fix_double_escaped_names()` cobre `'`, `&`, `"`, `<`, `>`; não se verificou se há outros caracteres de nome de rua (acentos/Unicode fora do conjunto de escape XML) sujeitos a problema semelhante — lacuna de verificação desta trilha, não hipótese levantada pelo commit.
3. Orientador(a) não contatado(a); arquitetura de agentes não validada; escolha acadêmica de corredor segue pendente.

