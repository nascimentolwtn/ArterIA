# Log de progresso — Mestrado ITA PG/PO

Status: ativo
Profundidade: leve

---

## 2026-10-24 (3)

Dois commits no ramo `ccr-b47695cc-ik89jg` tocam diretamente nos dados que sustentam a calibração do nível inferior e a confirmação do recorte geográfico desta trilha (Seções 5, 8-item-1 e 12 do `pre-projeto.md`):

1. Commit `bf374e4` acrescentou `cities/sjc/data-manifest.yaml` (inventário de toda fonte de dados prevista para a Fase 1 de SJC — PlanMob, Plano Diretor, atlas e microdados da Pesquisa OD, estudos FGV do edital de transporte, Linha Verde, GTFS, contagens de tráfego, planos de tempo semafórico, dados de sinistros, rotas de emergência — cada item marcado com agência, licença, visibilidade e status) e `cities/sjc/data-requests.md` (minutas de ofício a Ipplan e SEMOB, ainda não enviadas).
2. Commit `cd68b57` registrou a decisão do responsável pelo ArterIA de **não contatar nenhuma agência de SJC nesta etapa**. Todo item do manifesto que dependia de resposta municipal passou a `status: deferred` (minuta existe, mas não foi enviada) — isso inclui explicitamente a Pesquisa OD (tanto o atlas agregado `od-survey-atlas` quanto os microdados `od-survey-microdata`), as contagens de tráfego (`traffic-counts`) e os planos de tempo semafórico (`signal-timing-plans`). Em contrapartida, três fontes públicas de autoatendimento (sem contato necessário) foram adicionadas para a malha viária/hierarquia de vias: extrato OSM via Geofabrik/Overpass (já previsto no roteiro do ArterIA), o portal Geosanja da prefeitura (camadas do Plano Diretor LC 612/2018 e do zoneamento LC 623/2019) e a Base de Faces de Logradouros do IBGE (edição 2022, status "preliminar"). Com isso, o item do Plano Diretor migrou de "precisa de ofício" para "público, download direto via Geosanja".

**Por que isso importa para a trilha PG/PO:** a formulação bi-nível (Seção 6 do pré-projeto) separa claramente a topologia da rede $G$ — que as três fontes de autoatendimento agora cobrem razoavelmente bem, sem depender de contato institucional — da demanda $Q$ e dos parâmetros de calibração $c_a(x_a)$ do nível inferior, que continuam sem fonte confirmada: o atlas agregado da Pesquisa OD, os microdados da Pesquisa OD, as contagens volumétricas e os planos de tempo semafórico estão todos `deferred`, isto é, sem previsão de solicitação formal neste momento. Isso transforma o risco genérico já antecipado na Seção 12 ("dados incompletos ou desatualizados", "exigindo complementação por contagens próprias ou por estimativas indiretas") em uma condição concreta e datada do projeto, e tem duas implicações diretas:

- O objetivo específico 1 (Seção 8: calibrar o modelo SUMO "validado contra contagens de tráfego e a Pesquisa Origem-Destino de SJC") precisa, por ora, assumir como premissa de trabalho que essa validação dependerá de estimativas indiretas/demanda sintética (ver roadmap do ArterIA, risco P1.2/P10.2) até que — ou a menos que — o atlas público da Pesquisa OD seja localizado e obtido sem necessidade de ofício, ou a decisão de não contatar agências seja revista.
- O próximo passo nº 2 já registrado nesta trilha ("confirmar o corredor exato de SJC... verificando disponibilidade de dados da Pesquisa OD por zona para esse recorte específico") fica, por ora, bloqueado pela mesma decisão: não há, neste momento, um caminho ativo para obter dados de demanda por zona específicos de um corredor, o que pode forçar a escolha do recorte a critérios menos dependentes de dados finos de OD (ex. disponibilidade de contagens públicas, cobertura OSM, ou adoção de demanda sintética calibrada por proxies).

Nenhuma edição foi feita no `pre-projeto.md` nesta sessão (é a referência de fundo, não se reescreve sem motivo); o `outline.md` foi ajustado nos Capítulos 1, 3 e 4 para registrar essa dependência de dados como item pendente explícito.

**Próximos passos (atualizados):**
1. Contatar a coordenação do programa PG/PO do ITA para identificar possíveis orientadores(as) (sem alteração).
2. Confirmar o corredor exato de SJC — agora condicionado também à decisão sobre se/quando a Pesquisa OD (atlas ou microdados) será solicitada; na ausência de contato institucional, considerar como alternativa um recorte cuja escolha dependa apenas de fontes de autoatendimento (OSM, Geosanja, IBGE) e de demanda sintética, e registrar essa escolha como limitação metodológica explícita (Seção 12).
3. Iniciar a revisão sistemática de literatura (Capítulo 2 do outline) — sem alteração; adicionalmente, revisar literatura sobre estimação de matriz OD sintética/indireta a partir de contagens esparsas, caso a Pesquisa OD de SJC permaneça indisponível — pode se tornar parte necessária da metodologia, não apenas do catálogo de riscos.

## 2026-10-24 (2)

Commit `62facb2` ("docs(roadmap): reframe remote work as Claude app sessions, not GitHub Actions") apenas reorganiza a divisão de tarefas entre sessões de nuvem e desktop do Claude Code no projeto ArterIA (infraestrutura/processo de desenvolvimento) e rescopa ADRs de execução remota. Não toca em escolha de simulador, formulação de otimização bi-nível/multiobjetivo nem no recorte de dados de SJC, e o pré-projeto desta trilha não aborda o fluxo de trabalho de pesquisa/engenharia como parte do seu objeto de estudo. Sem relevância para esta trilha; nenhuma edição de conteúdo foi feita.

## 2026-10-24

O pré-projeto detalhado (`pre-projeto.md`) já existia, cobrindo título provisório, resumo, problema de pesquisa, contexto de São José dos Campos, recorte geográfico, formulação matemática bi-nível multiobjetivo, objetivos, metodologia, métricas before/after, limitações, cronograma tentativo e referências iniciais. Nesta sessão foram criados `outline.md` (esqueleto dos oito capítulos da dissertação, mapeando o que já está coberto pelo pré-projeto e o que ainda falta pesquisar/escrever em cada um) e este arquivo de progresso.

**Próximos passos:**
1. Contatar a coordenação do programa PG/PO do ITA para identificar possíveis orientadores(as) com interesse em otimização bi-nível/multiobjetivo e meta-heurísticas (ver Seção 15 do pré-projeto, ainda sem nome indicado).
2. Confirmar o corredor exato de SJC a usar como estudo de caso (candidato preferencial: trecho do eixo Linha Verde — Seção 5 do pré-projeto), verificando disponibilidade de dados da Pesquisa OD por zona para esse recorte específico.
3. Iniciar a revisão sistemática de literatura (Capítulo 2 do outline), ampliando além dos ~5 trabalhos já citados no pré-projeto, cobrindo especialmente GNNs como surrogate de simulação de tráfego e otimização Bayesiana multiobjetivo aplicada a UNDP.
