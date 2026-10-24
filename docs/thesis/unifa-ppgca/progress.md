# Progresso — Trilha UNIFA/PPGCA

Status: ativo
Profundidade: leve

---

## 2026-10-24 (dados de SJC: inventário e decisão de não contatar agências)

Dois commits do lado de engenharia do ArterIA foram avaliados para esta trilha (a execução anterior do `thesis-orchestrator` para eles não chegou a concluir por erro de ferramenta):

- `bf374e4` — criou `cities/sjc/data-manifest.yaml` (inventário de toda fonte de dado prevista para a Fase 1 em SJC: PlanMob, Plano Diretor, atlas e microdados da Pesquisa OD, estudos FGV do edital de transporte, Projeto Linha Verde, GTFS, contagens de tráfego, planos de tempo semafórico, dados de sinistros e rotas de emergência) e `cities/sjc/data-requests.md` (minutas de ofício a Ipplan e SEMOB, não enviadas).
- `cd68b57` — o responsável pelo repositório decidiu **não contatar nenhuma agência de SJC nesta fase**. Todo item do manifesto que dependeria de resposta municipal passou a `status: deferred`. Em seu lugar, entraram três fontes autosserviço, sem contato institucional, para a malha viária: extrato OpenStreetMap (Geofabrik/Overpass), o portal municipal Geosanja (que publica as camadas do Plano Diretor LC 612/2018 e do zoneamento LC 623/2019 para download direto) e a Base de Faces de Logradouros do IBGE (edição 2022, com status "preliminar"). O item do Plano Diretor no manifesto passou de "precisa de ofício" para "público, download autosserviço via Geosanja". Várias dessas informações (catálogo exato do Geosanja, status final do IBGE, completude do OSM especificamente para SJC) não puderam ser verificadas ao vivo nesta sessão remota (acesso de saída a sjc.sp.gov.br, ibge.gov.br, overpass-api.de e nominatim.openstreetmap.org bloqueado pela política de rede da sessão) e ficaram registradas como pendências de mesa em `.claude/napkin.md` do repositório principal.

**Por que importa para esta trilha:** o manifesto (`cities/sjc/data-manifest.yaml`) é o documento mais concreto até hoje sobre quais dados de resiliência de acesso viário estarão de fato disponíveis para a etapa instrumental do pré-projeto (seção 9-10). Dois pontos merecem destaque:

1. **Rotas de resposta de emergência (`emergency-routes`) permanecem `deferred`/indisponíveis**, e o próprio manifesto já assinala que esta é provavelmente "a fonte mais sensível/difícil de obter", sugerindo isócronas a partir de localizações conhecidas de estações como proxy documentado caso o dado real não seja obtido. Isso afeta diretamente a métrica de "tempo estimado de resposta/recuperação" da seção 10 do pré-projeto e o objetivo específico 5 — sem esse dado (ou um proxy validado), essa métrica específica da dissertação fica mais fraca.
2. **Dados de sinistros/acidentes (`crash-data`)** seguem `deferred` no nível municipal, mas o manifesto aponta o Infosiga (Detran-SP) como possível substituto público agregado de nível estadual, ainda não verificado quanto a exportação aberta em nível municipal. É um candidato razoável de métrica de resiliência/segurança substituta, mas carece de verificação — não deve ser citado no texto da dissertação como fonte confirmada enquanto isso não ocorrer.
3. A decisão de **não contatar nenhuma agência municipal nesta fase** é, em si, um dado relevante para o Capítulo 4 (Metodologia) e para a seção de limitações: reforça, em escala menor (municipal, não FAB), o risco já descrito na seção 12 do pré-projeto sobre dependência de acesso a dados e atores institucionais. Não se trata de um bloqueio da FAB — é uma escolha de priorização do lado de engenharia do ArterIA — mas estabelece um precedente que a trilha PPGCA deve monitorar quando a etapa qualitativa (entrevistas, documentos institucionais) for desenhada.

**Impacto na tese:** `outline.md`, capítulo 3 (Estudo de Caso de SJC) e capítulo 5 (Modelagem de Resiliência), receberam uma frase cada apontando essas descobertas — ver commits deste repositório de trilha. Nenhuma prosa de capítulo foi escrita; o inventário é só instrumental (dado de entrada), não altera o núcleo teórico/conceitual do Capítulo 2 nem o problema de pesquisa da seção 3 do pré-projeto.

**Decisão pendente:** nenhuma decisão é exigida agora desta trilha — a decisão de não contatar agências foi tomada pelo lado de engenharia do ArterIA, por razões de priorização do roadmap, não por razão específica desta dissertação. Mas fica registrado que, quando a etapa qualitativa do pré-projeto for desenhada (seção 9, "coleta qualitativa complementar"), será necessário decidir separadamente se e quando contato institucional (municipal e/ou FAB) será buscado — essa decisão ainda não foi tomada e não deve ser confundida com a decisão de engenharia registrada aqui.

## 2026-10-24 (nota)

Commit `62facb2` ("docs(roadmap): reframe remote work as Claude app sessions, not GitHub Actions") foi avaliado e considerado fora do escopo desta trilha: trata da divisão operacional de trabalho de desenvolvimento do ArterIA entre sessões em nuvem e desktop (fixtures de teste, ADRs, revisão de PR vs. SUMO em dados reais, ferramentas GUI), não da literatura de segurança/defesa, do caso de SJC, da metodologia mista ou do instrumento de modelagem de resiliência em si. Não há decisão de simulador, método de IA ou escopo de cidade/dados envolvida. Nenhuma edição de conteúdo foi feita em `outline.md` nesta entrada.

## 2026-10-24

O pré-projeto detalhado (`pre-projeto.md`) já existe e está completo em sua estrutura: título, resumo, problema de pesquisa reformulado para a linha "Poder Aeroespacial Brasileiro, Segurança e Defesa", contexto de SJC, metodologia mista, métricas de resiliência, limitações/riscos e cronograma tentativo de 4 semestres. Nesta sessão foram criados `outline.md` (esqueleto de capítulos da dissertação, mapeando o que já está coberto pelo pré-projeto e o que falta pesquisar/escrever em cada capítulo) e este arquivo de progresso.

**Próximos passos realistas:**

1. **Nivelamento metodológico em Ciência Política/RI** — este é o principal risco em aberto do projeto. O autor é engenheiro de computação sem formação prévia em Ciência Política, Relações Internacionais ou Estudos Estratégicos, que são as disciplinas que sustentam o PPGCA. Sem disciplinas de nivelamento (teoria estratégica, segurança internacional, métodos qualitativos) e sem apoio metodológico forte de um orientador, há risco concreto de a dissertação ficar teoricamente superficial e "engenheira demais" para o programa — o próprio pré-projeto já sinaliza isso explicitamente na seção de limitações.
2. **Revisão bibliográfica sistemática de infraestrutura crítica / military mobility** — o pré-projeto admite abertamente que as referências sobre esse tema (OTAN/UE, critical infrastructure protection) vêm de conhecimento geral do autor, não de busca bibliográfica dedicada. Esta é a lacuna mais crítica a resolver antes da qualificação.
3. **Validação do enquadramento com um orientador do PPGCA** — buscar docente vinculado à linha "Poder Aeroespacial Brasileiro, Segurança e Defesa" e apresentar o pré-projeto como ponto de partida de negociação (não como proposta fechada), já que o encaixe do tema de mobilidade urbana nessa linha não pode ser assumido como garantido.

**Risco em destaque:** o déficit de formação do autor em Ciência Política/Relações Internacionais, combinado com a dependência de um orientador que aceite o reposicionamento do núcleo da pesquisa (de otimização de tráfego para segurança/defesa), é hoje o maior fator de incerteza desta trilha — maior do que qualquer limitação técnica do instrumento ArterIA.
