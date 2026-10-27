# Capítulo 4 — Experimentos

> Status: **rascunho parcial** (Seção 4.2 é rascunho; demais seções `stub`).
> RASCUNHO: nenhum experimento de RL/GNN foi executado. Não há resultados quantitativos neste capítulo; os únicos números são contagens operacionais do primeiro teste de rotabilidade (v1.0, 2026-10-26).

## 4.1 Desenho experimental (stub)

TODO(evidência): protocolo de treino/validação/teste, número de sementes (ferramenta candidata: `arteria/calibration/replication.py`, aproximação normal informal — declarar a limitação ou usar t de Student), critérios de parada, baselines (Seção 10 do `pre-projeto.md`). Cenário de demanda: sempre "cenário sintético calibrado a fluxos observados" (ADR 0013; microdados de OD `declined`).

## 4.2 Estudo de caso: corredor B — Av. Andrômeda ↔ DCTA / Jardim Satélite (RASCUNHO)

**Natureza do que foi feito.** Em 2026-10-26, a cadeia `studyarea build` → `osm fetch --candidate b` → `network build` → `sumo-gui` foi executada pela primeira vez contra ferramentas e dados reais, no desktop WSL2 (`CHANGELOG.md`, [1.0]). Trata-se de **teste de rotabilidade e inspeção visual**, não de experimento.

**Fatos registrados.**
- Rede construída apenas para o corredor B; D, C e A têm polígonos sem rede. [Defasado desde a ADR 0016: existe hoje uma rede unificada de SJC com 14.225 arestas; o registro acima descreve a primeira execução de 2026-10-26, mantido como histórico. Em 2026-10-27, B passou a ter também uma linha de eixo por arestas (derivada) e a área estendida de 5,31 para 7,67 km², com geometria conferida em imagem aérea pelo responsável.]
- Demanda de teste: 1.800 veículos aleatórios (`randomTrips.py`); 415 viagens adicionais inviáveis foram descartadas.
- Validador estrutural: 729 erros e 7.562 avisos, majoritariamente falsos positivos ou efeitos de recorte (detalhamento em `chapters/03-arquitetura-do-sistema.md`, Seção 3.3).
- Pendente: classificar as 415 inviabilidades (rede desconexa, restrições de giro, borda do recorte, ou erro de OSM).

**Motivação do corredor.** O problema do corredor B é de desvio forçado: não há ligação direta entre a Av. Andrômeda e a DCTA/Jardim Satélite, exigindo desvio longo via Dutra ou viadutos (`cities/sjc/candidate-corridors.md`, observação qualitativa do responsável, sem contagens). É, portanto, uma instância real de problema de alcançabilidade em grafo, alinhada ao objeto da dissertação (alocação de faixas/sentidos), mas pode requerer um conector novo, primitiva ainda sem transformação no catálogo e cujo benefício em rede está fora do escopo defensável sob a ADR 0013.

**O que este estudo de caso não é.** Não é baseline calibrado, não é validação de escolha de corredor (a ordem B > D > C > A é prioridade de produto, não critério acadêmico) e não é evidência para os Capítulos 5 ou 6. Equipara-se, quanto ao status probatório, ao tratamento dado a Cities: Skylines (camada de comunicação, nunca evidência quantitativa).

**Riscos específicos do corredor B.**
1. Não há base qualitativa de pico para B (a ADR 0003 cobre A e D); a janela `am-peak` é "best guess".
2. B conecta-se ao Anel Viário (A); uma rede recortada em B isola efeitos de transbordamento da Dutra/BR-116 que são parte do problema.
3. A escolha do corredor da dissertação deve ser decisão acadêmica, a tomar com orientador(a), e não herdar a prioridade de engenharia.

TODO(evidência): estatísticas da rede de B (ver 3.2); análise de componentes; contagem de semáforos (18 junções semafóricas, 2 sem `<tlLogic>`, informadas pelo responsável); decisão rede unificada vs. por corredor (resolvida em favor da rede única pela ADR 0016: B é área de avaliação dentro da rede unificada, hoje de 14.225 arestas e 6.655 junções após a extensão das áreas de B e C em 2026-10-27, ver 3.2, que supera as 11.035 arestas da ADR 0016 inicial; falta definir como isso afeta o número de agentes e o escopo de recompensa por área).

## 4.2.1 Orçamento computacional (RASCUNHO)

O benchmark do PC de desenvolvimento (`docs/local/dev-pc-benchmark.md`, 2026-10-26, `814f4c9`) registra: Intel Core i5-11400F, 6 núcleos/12 threads; 9,7 GiB de RAM visíveis ao WSL2 (limite `memory=10GB` em `.wslconfig`); 831 GB livres em disco. Teste sintético de CPU em Python indica escala efetiva de cerca de 5-6 trabalhadores (execução única e ruidosa, não benchmark rigoroso). Nenhum benchmark de SUMO foi executado nessa sessão. Estimativas do próprio documento: lotes de 10 sementes viáveis com 4 trabalhadores (cerca de 40 minutos ou mais); calibração `duaIterate` viável durante a noite; campanha NSGA-II planejada de 10 mil execuções mesoscópicas inviável localmente (estimativa de 35-45 h com 4-5 trabalhadores), com sugestão de campanha inicial menor (por exemplo, 500 pacotes x 3 sementes) ou nó em nuvem/universidade. Implicação para esta trilha: o treinamento de MARL, que exige muitos episódios, enfrentará restrição ainda mais severa; o protocolo experimental deve prever um simulador reduzido (corredor) ou o surrogate em GNN como motivação central, e declarar a limitação de hardware. Estas são estimativas do produto, não medições de treinamento. TODO(evidência): medir passos/s de SUMO na rede unificada e consumo de memória por execução.

## 4.3 Calibração, métricas e execuções (stub)

TODO(evidência): contagens de tráfego (`deferred`), GEH/RMSE (`arteria/calibration/goodness_of_fit.py`), métricas (`arteria/evaluate/metrics.py`; leitura de `tripinfo.xml` real ainda por fazer).
