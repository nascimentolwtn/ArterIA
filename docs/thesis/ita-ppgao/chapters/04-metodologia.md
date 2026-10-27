# Capítulo 4 — Metodologia

> Status: rascunho (apenas a seção 4.1; demais seções permanecem `outline`). Rótulo geral: RASCUNHO. Este texto descreve procedimento e limites, não resultados. Os números citados são registros de execução de verificação técnica do pipeline (CHANGELOG [1.0], 2026-10-26), não achados de pesquisa.

## Seções ainda em estágio de esqueleto

- 4.2 Geração de demanda sintética calibrada por contagem (ADR 0013; modelo gravitacional + `routeSampler`). TODO(evidência): nenhuma contagem do recorte existe; nenhuma calibração foi executada.
- 4.3 Calibração e qualidade de ajuste (GEH, RMSE/MAPE; `arteria/calibration/goodness_of_fit.py`). TODO(evidência): sem dado observado.
- 4.4 Catálogo restrito de intervenções e delimitação de escala dos cenários de interdição (corredor/acesso único, não evacuação em escala de rede; ver `progress.md`, entrada de `975fec7`). TODO(decisão): formalizar com orientador.
- 4.5 Formulação bi-nível e métricas (Seções 6, 9 e 10 do `pre-projeto.md`). TODO(evidência): métricas de resiliência e continuidade operacional não implementadas.

## 4.1 Construção e validação da rede viária (RASCUNHO)

### 4.1.1 Cadeia de construção

A malha viária de um recorte é construída por uma cadeia de quatro etapas, executada por comandos do ArterIA, com ferramentas externas versionadas (simulador SUMO, versão 1.28.0 conforme registro da execução; sobre o SUMO, ver Lopez et al., 2018 [`lopez2018sumo`]; sobre o OSM, Haklay e Weber, 2008 [`haklay2008osm`]):

1. **Delimitação do recorte.** O polígono de estudo é rascunhado por geocodificação de marcos via Nominatim, fecho convexo e buffer (`arteria studyarea build`; `arteria/network/study_area.py`; `cities/sjc/study-areas.yaml`). O polígono é tratado como ponto de partida, não como recorte final: não deriva da malha real nem de limites administrativos.
2. **Extração do OpenStreetMap (OSM).** Um extrato regional (Geofabrik, Sudeste) é recortado ao polígono com `osmium` (`arteria osm fetch --candidate b`).
3. **Conversão e construção.** O arquivo PBF é convertido para OSM XML com `osmium cat`, pois o `netconvert` não lê PBF; em seguida o `netconvert` aplica o conjunto padrão de opções de importação OSM, que inclui inferência de semáforos (`--tls.guess-signals`) e de rotatórias/junções (`arteria network build`; `arteria/network/build.py`).
4. **Verificação de roteabilidade.** A rede é aberta em `sumo-gui` e carregada com demanda aleatória (`randomTrips.py`), apenas para confirmar que veículos conseguem percorrê-la. Essa demanda não tem relação com a demanda real e não é insumo de qualquer análise.

Cada etapa produz artefatos não versionados (`data/`, `.net.xml`, `.osm.xml`, `.rou.xml` ignorados pelo git); versionam-se apenas configurações e, futuramente, correções manuais exportadas como patches.

TODO(evidência): conectar a cadeia ao `RunManifest` (`arteria/provenance.py`), que ainda não é invocado por nenhum comando; só então a reprodutibilidade (SHA do git, versão do SUMO, seed, hash de configuração, checksums de entrada, opções do `netconvert`) poderá ser afirmada para a rede construída.

### 4.1.2 Por que a validação em rede real difere da validação em fixtures

O validador de rede (`arteria network validate`; `arteria/network/validate.py`) foi desenvolvido e testado contra fixtures sintéticas pequenas. A primeira execução sobre uma rede real (corredor B) retornou 729 erros e 7.562 avisos. A análise desses números mostra que a maior parte decorre da inadequação das verificações à escala e à natureza de uma rede real recortada, e não de defeitos da rede. Esse achado é metodológico: uma verificação afinada em fixtures não se transfere automaticamente a redes reais. A Tabela abaixo organiza a interpretação registrada.

FIGURA(TODO): tabela "verificação / contagem / natureza / ação metodológica".

| Verificação | Contagem | Natureza (conforme registro) | Ação metodológica prevista |
|---|---|---|---|
| `oneway_status` | 7.522 avisos (5.448 em arestas internas ":") | Falso positivo: o `.net.xml` do SUMO não possui atributo `oneway` | Substituir por detecção de pares de arestas opostas |
| `connectivity` | 727 erros | Esperado: medido a partir de uma única junção inicial em extrato recortado | Substituir por análise de componentes fortemente conexos (principal vs. órfãos) |
| `dead_end` | 40 avisos | Majoritariamente arestas na borda do recorte | Distinguir becos de borda de becos internos |
| `traffic_light_logic` | 2 erros | Reais: dois clusters de travessia só-bicicleta (`allow="bicycle"`) tipo `traffic_light` sem `<tlLogic>` (2 de 18 junções semafóricas) | Verificar impacto na simulação; provavelmente inofensivo, mas não verificado |

Observação: as classificações acima foram registradas pelo responsável do produto na primeira execução; a verificação individual dos itens (por exemplo, quantos dos 727 erros de conectividade correspondem a componentes órfãos de fato) ainda não foi feita. TODO(evidência).

Atualização (commit `72ab33e`): o validador foi adaptado a redes SUMO reais, com análise de componentes fortemente conexos (SCC), detecção de pares de arestas opostas e distinção de becos sem saída de borda, correspondendo às ações previstas na tabela acima. Segundo o registro do commit, os 729 erros na rede real do corredor B passaram a 0. Essa redução resulta de verificações mais adequadas à rede real, não de correção da rede; a contagem de avisos após a adaptação e a verificação individual dos achados não foram conferidas por esta trilha. TODO(evidência): estado antes/depois por verificação (contagens de avisos e de componentes órfãos).

### 4.1.3 Efeito de borda do recorte

Recortar a rede a um polígono remove vias que, na realidade, oferecem rotas alternativas. Três consequências metodológicas precisam ser tratadas antes de qualquer métrica de acesso ou resiliência:

- componentes desconexos e becos sem saída artificiais surgem na borda, e podem ser confundidos com defeitos da rede;
- tempos de acesso e redundância de rotas podem ser subestimados ou superestimados, pois desvios externos ao polígono não existem no modelo; em particular, o corredor B conecta-se ao Anel Viário (corredor A), de modo que a escolha entre rede unificada e rede por corredor afeta diretamente a medição de desvio;
- origens e destinos nas bordas precisam de regra explícita (portais/gateways), ainda não definida.

TODO(decisão): rede unificada versus por corredor (decisão futura do produto, ainda em aberto).

Atualização (2026-10-27; ADR 0016 e `CHANGELOG.md` [Unreleased], trabalho não commitado): a decisão foi tomada pelo produto em favor de rede unificada de SJC. Após a extensão das áreas B e C, a rede reconstruída tem 14.225 arestas e 6.655 junções, com 93,1% das junções no maior componente (números informados pelo chamador/CHANGELOG, não reproduzidos aqui; a cifra anterior de 11.035 arestas está superada). O corredor B deixa de ser tratado como rede isolada: é um subconjunto de arestas da rede unificada, e desvios externos ao antigo polígono passam a existir no modelo. Os 6,9% de junções fora do maior componente ainda exigem explicação. A verificação aérea dos corredores A, B, C, D, da ligação A–B e das áreas estendidas B/C foi feita pelo responsável do produto em 2026-10-27 (Google Earth; registro no CHANGELOG), sem revisão por especialista do PPGAO. TODO(decisão): a dissertação deve decidir se adota a rede unificada como unidade de análise e como justificar o recorte B dentro dela.

### 4.1.4 Qualidade do OSM e revisão manual como etapa documentada

A rede deriva de dados colaborativos (OSM). Completude e correção de atributos (sentido, número de faixas, restrições de conversão, velocidade) variam e não foram auditadas para o recorte. A semaforização é parcialmente inferida (`--tls.guess-signals`), o que introduz incerteza sobre pontos de controle que podem não existir, ou deixar de existir, na realidade. Propõe-se tratar a revisão manual no `netedit` como etapa operacional documentada do método, e não como ajuste informal. Esboço da etapa, a ser refinado:

1. comparar a rede renderizada com imagem de satélite e mapas para o mesmo recorte;
2. listar discrepâncias (junção emaranhada, rotatória mal formada, faixas ausentes, sentido incorreto, semáforo inferido inexistente);
3. registrar cada correção como patch versionado (nunca editar o `.net.xml` gerado nem versioná-lo);
4. reexecutar a validação e registrar o estado antes/depois;
5. registrar o responsável e a data da revisão.

TODO(citação): literatura sobre qualidade de dados OSM e sua adequação a modelagem de tráfego (a referência `haklay2008osm` em `references.bib` é apenas introdutória sobre OSM).

### 4.1.5 Proveniência e reprodutibilidade

Para que a rede construída seja reconstruível por terceiros, devem ser registrados: data e versão do extrato Geofabrik e seu hash; versão do `osmium`; versão do SUMO (1.28.0 na execução registrada); opções completas do `netconvert`; polígono utilizado; patches manuais aplicados. A execução de 2026-10-26 não gerou `RunManifest` (ver 4.1.1).

Atualização (2026-10-27; Fase 2 do roadmap, trabalho não commitado, lido em `CHANGELOG.md` [Unreleased] e `docs/roadmap.md`; não verificado por esta trilha): o produto passou a implementar parte dos itens acima. (i) Snapshot OSM fixado (Geofabrik Sudeste, timestamp do PBF 2026-10-25), com sha256 registrado em `cities/sjc/network/osm-snapshot.yaml`. (ii) Correções manuais como patches aplicados em segunda passada do `netconvert` (`arteria/network/patches.py`), conforme o item 3 do esboço de 4.1.4. (iii) Comandos `arteria network diff` e `arteria network rebuild` (`arteria/network/{diff,rebuild,snapshot}.py`); o rebuild reproduz o hash de conteúdo da rede (cabeçalho de timestamp removido do cálculo), com duração informada de cerca de 16 s. (iv) Validação informada: 0 erros e 127 avisos. Ressalvas: reprodutibilidade de hash prova determinismo do build, não correção da rede; "0 erros" segue sujeito à ressalva de 4.1.2; a camada de transporte público (GTFS) não foi montada, pois nenhum GTFS público de SJC foi encontrado (P2.6 adiada), o que limita cenários com ônibus. A versão de `osmium`/`netconvert` e o `RunManifest` do build continuam como TODO(evidência).

### 4.1.6 Limites do que a rede atual sustenta

Registrado para evitar sobre-interpretação: a rede do corredor B foi verificada apenas quanto à roteabilidade (1.800 veículos aleatórios circularam; 415 viagens inviáveis foram descartadas). Isso não constitui baseline calibrado, validação do corredor como recorte da dissertação nem evidência sobre tempo de acesso, resiliência ou continuidade operacional. A origem das 415 viagens inviáveis (componentes desconexos, efeito de borda, restrições de acesso OSM) não foi investigada. TODO(evidência).
