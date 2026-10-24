# Progresso — Trilha de Mestrado ITA PG/EEC (Área Informática)

Status: ativo
Profundidade: leve

---

## 2026-10-24 (revisão dos commits `bf374e4` e `cd68b57`)

Dois commits da branch `ccr-b47695cc-ik89jg` revisados em conjunto (a execução anterior do `thesis-orchestrator` para eles não chegou a concluir por erro de ferramenta).

- `bf374e4` criou `cities/sjc/data-manifest.yaml` — inventário de todas as fontes de dados da Fase 1 de SJC (PlanMob, Plano Diretor, atlas e microdados da Pesquisa OD, estudos da FGV para a licitação de transporte, Linha Verde, feed GTFS, contagens volumétricas de tráfego, planos de tempo semafórico, dados de sinistros, rotas de emergência), cada item com agência, licença, visibilidade e status — e `cities/sjc/data-requests.md`, com minutas (ainda não enviadas) de carta de solicitação a Ipplan e SEMOB.
- `cd68b57` registrou a decisão do responsável pelo projeto de **não contatar nenhuma agência municipal de SJC nesta etapa**. Todo item do manifesto que dependeria de resposta municipal passou para `status: deferred` (carta não enviada). Em contrapartida, foram adicionadas três fontes públicas de autoatendimento (sem contato necessário) para a malha viária: OpenStreetMap (extração Geofabrik/Overpass, já prevista no roteiro), o portal Geosanja da própria prefeitura (camadas do Plano Diretor LC 612/2018 e do zoneamento LC 623/2019) e a Base de Faces de Logradouros do IBGE (edição 2022, status "preliminar"). O item do Plano Diretor no manifesto passou de "precisa de solicitação" para "público, download direto via Geosanja".

**Relevância para esta trilha:** o manifesto confirma, de forma rastreável, exatamente a limitação já antecipada na Seção 12 do `pre-projeto.md` ("dados de treinamento limitados") e no Capítulo 6 do `outline.md`: as fontes que alimentariam a calibração do ambiente SUMO/TraCI e, por extensão, o treinamento e a avaliação dos agentes de RL multiagente e do surrogate em GNN — contagens volumétricas de tráfego, planos de tempo semafórico, feed GTFS (necessário para a métrica de confiabilidade de ônibus da Seção 10), microdados da Pesquisa OD (usados para padrões de demanda, Seção 4/9) e dados de sinistros (proxy de segurança, Seção 10) — permanecem todas em `status: deferred`, ou seja, sem pedido formal enviado e sem previsão de resposta. Isso não bloqueia a formulação teórica do método (RL/GNN), mas bloqueia, por ora, a calibração factual do ambiente de treinamento que o Capítulo 3 (Arquitetura do Sistema) e o Capítulo 4 (Experimentos) do `outline.md` preveem construir. As três novas fontes de autoatendimento (OSM, Geosanja, IBGE) cobrem apenas a topologia/geometria da malha viária — suficiente para a representação em grafo da Seção 8.1 do pré-projeto — mas não cobrem demanda, sinalização nem transporte público, que são necessários para recompensa/avaliação realistas do RL e para a métrica de confiabilidade de ônibus.

Nenhuma prosa de capítulo foi alterada; apenas uma linha foi adicionada ao Capítulo 4 do `outline.md` apontando este manifesto como o artefato de rastreio da lacuna de dados de calibração, já que a decisão de `cd68b57` concretiza (em vez de apenas presumir) essa limitação.

**Observação de honestidade:** como no pré-projeto já se assume que toda validação ocorrerá em simulação (Seção 12), a decisão de não contatar agências não muda o enquadramento metodológico — apenas adia a calibração fina do cenário de demanda/sinalização, o que pode empurrar ainda mais a dissertação na direção do risco já identificado de depender de cenários sintéticos de demanda com viés desconhecido.

## 2026-10-24 (revisão do commit 62facb2)

Commit `62facb2` ("docs(roadmap): reframe remote work as Claude app sessions, not GitHub Actions") revisado: trata da divisão de trabalho entre sessões de desenvolvimento em nuvem e desktop do próprio processo de engenharia do ArterIA (não é RL multiagente nem GNN aplicados ao domínio de tráfego, que é o objeto desta trilha). Sem relevância para o pré-projeto ou para `outline.md` — nenhuma edição de conteúdo feita nesta entrada.

## 2026-10-24

O pré-projeto detalhado (`pre-projeto.md`) já existe e cobre título provisório, resumo, problema de pesquisa, contexto de São José dos Campos, recorte geográfico, fundamentação inicial em IA (RL multiagente + GNN), objetivos, metodologia/arquitetura proposta, métricas, resultado esperado, limitações, cronograma tentativo de 4 semestres e lista inicial de referências.

Nesta entrada, foram criados `outline.md` (esqueleto de capítulos da dissertação, mapeando o que o pré-projeto já cobre versus o que falta pesquisar/escrever em cada capítulo) e este arquivo `progress.md` (log de progresso).

**Próximos passos:**
1. Contatar um(a) possível orientador(a) no PG/EEC do ITA (área Informática) com interesse em RL/GNN/sistemas multiagente, conforme indicado na Seção 15 do pré-projeto — ainda nenhum nome foi buscado ou contatado.
2. Validar a viabilidade computacional da arquitetura multiagente + GNN + SUMO/TraCI proposta (Seção 9 do pré-projeto) — estimar custo de treinamento e necessidade de GPU/infraestrutura antes de comprometer o cronograma do primeiro semestre.
3. Iniciar a revisão de literatura mais profunda indicada no Capítulo 2 do `outline.md` (RL multiagente cooperativo, arquiteturas de GNN para grafos dinâmicos, bi-level network design), indo além da lista curada de referências já no pré-projeto.
