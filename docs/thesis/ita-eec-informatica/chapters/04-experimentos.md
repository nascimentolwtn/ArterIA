# Capítulo 4 — Experimentos

> Status: **rascunho parcial** (Seção 4.2 é rascunho; demais seções `stub`).
> RASCUNHO: nenhum experimento de RL/GNN foi executado. Não há resultados quantitativos neste capítulo; os únicos números são contagens operacionais do primeiro teste de rotabilidade (v1.0, 2026-10-26).

Este capítulo sustenta, no estado atual, uma tese deliberadamente modesta: o que existe até aqui é um teste de roteabilidade da rede e uma estimativa de orçamento computacional, e ambos, em vez de resultados, delimitam as condições sob as quais os experimentos de aprendizado poderão ser desenhados.

## 4.1 Desenho experimental (stub)

TODO(evidência): protocolo de treino/validação/teste, número de sementes (ferramenta candidata: `arteria/calibration/replication.py`, aproximação normal informal — declarar a limitação ou usar t de Student), critérios de parada, baselines (Seção 10 do `pre-projeto.md`). Cenário de demanda: sempre "cenário sintético calibrado a fluxos observados" (ADR 0013; microdados de OD `declined`). A fonte de dado concreta para o modelo gravitacional que alimentaria esse cenário (população por setor censitário do Censo demográfico; proxy de uso do solo para atração de empregos, à falta de contagem real de emprego alcançável sem contato com órgão) foi proposta pela ADR 0017, ainda não aceita; até a aceitação e a obtenção do dado real, o cenário de demanda permanece apenas desenhado, não calculado.

## 4.2 O corredor B como teste de roteabilidade, não como experimento (RASCUNHO)

**Natureza do que foi feito.** Em 2026-10-26, a cadeia de delimitação da área de estudo, extração do OpenStreetMap (OSM), construção da rede e abertura na interface gráfica do simulador foi executada pela primeira vez contra ferramentas e dados reais, na estação de trabalho local (versão 1.0 do ArterIA). Trata-se de **teste de rotabilidade e de inspeção visual**, e não de experimento.

**Fatos registrados.** A rede foi construída apenas para o corredor B, ao passo que D, C e A tinham polígonos sem rede. Tal registro está, contudo, defasado desde a adoção da rede única: existe hoje uma rede unificada de SJC com 14.225 arestas, e o registro acima descreve a primeira execução de 2026-10-26, mantido como histórico. Em 2026-10-27, B passou a ter, ademais, uma linha de eixo por arestas (derivada) e a área estendida de 5,31 para 7,67 km², com geometria conferida em imagem aérea pelo responsável.

A demanda de teste consistiu em 1.800 veículos aleatórios, e 415 viagens adicionais inviáveis foram descartadas pelo gerador. O validador estrutural, por sua vez, apontou 729 erros e 7.562 avisos, majoritariamente falsos positivos ou efeitos de recorte, conforme detalhado na Seção 3.3. Resta, ainda, classificar as 415 inviabilidades segundo sua causa (rede desconexa, restrições de giro, borda do recorte ou erro do OSM).

**Motivação do corredor.** O problema do corredor B é de desvio forçado: não há ligação direta entre a Av. Andrômeda e o DCTA/Jardim Satélite, o que exige desvio longo pela Rodovia Presidente Dutra ou por viadutos, segundo observação qualitativa do responsável, sem contagens. Trata-se, portanto, de uma instância real de problema de alcançabilidade em grafo, alinhada ao objeto da dissertação (alocação de faixas e sentidos). Pode, contudo, requerer um conector novo, primitiva ainda sem transformação no catálogo e cujo benefício em nível de rede fica fora do que a demanda sintética calibrada por contagem permite defender.

**O que este estudo de caso não é.** Não é linha de base calibrada nem validação de escolha de corredor — a ordem B > D > C > A é prioridade de produto, e não critério acadêmico —, tampouco evidência para os Capítulos 5 ou 6. Quanto ao status probatório, equipara-se ao tratamento dado ao jogo Cities: Skylines, isto é, camada de comunicação, nunca evidência quantitativa.

**Riscos específicos do corredor B.** Três riscos merecem registro. Em primeiro lugar, não há base qualitativa de horário de pico para B, uma vez que a base qualitativa aceita no esquema de configuração da cidade cobre apenas A e D, de modo que a janela de pico da manhã é uma melhor estimativa ("best guess"). Em segundo lugar, B conecta-se ao Anel Viário (A), e uma rede recortada em B isolaria efeitos de transbordamento da Dutra/BR-116 que são parte do problema. Por fim, a escolha do corredor da dissertação deve ser decisão acadêmica, a tomar com orientador(a), e não herdar a prioridade de engenharia.

TODO(evidência): estatísticas da rede de B (ver 3.2); análise de componentes; contagem de semáforos (18 junções semafóricas, 2 sem `<tlLogic>`, informadas pelo responsável); decisão rede unificada vs. por corredor (resolvida em favor da rede única pela ADR 0016: B é área de avaliação dentro da rede unificada, hoje de 14.225 arestas e 6.655 junções após a extensão das áreas de B e C em 2026-10-27, ver 3.2, que supera as 11.035 arestas da ADR 0016 inicial; falta definir como isso afeta o número de agentes e o escopo de recompensa por área).

## 4.2.1 O orçamento computacional local restringe o treinamento multiagente (RASCUNHO)

O levantamento de desempenho da estação de trabalho de desenvolvimento, realizado em 2026-10-26, registra um processador Intel Core i5-11400F, com 6 núcleos e 12 threads; 9,7 GiB de memória visíveis ao ambiente Linux sob Windows (limitado a 10 GB por configuração); e 831 GB livres em disco. Um teste sintético de processamento em Python indica escala efetiva de cerca de 5 a 6 processos paralelos, em execução única e ruidosa, não em benchmark rigoroso. Nenhum benchmark do simulador foi executado nessa sessão.

As estimativas do próprio levantamento indicam que lotes de 10 sementes são viáveis com 4 processos paralelos (cerca de 40 minutos ou mais) e que a calibração iterativa de equilíbrio de rotas é viável durante a noite. Em contrapartida, a campanha planejada de otimização evolutiva multiobjetivo (NSGA-II) com 10 mil execuções mesoscópicas é inviável localmente (estimativa de 35 a 45 h com 4 a 5 processos), sugerindo-se uma campanha inicial menor (por exemplo, 500 pacotes × 3 sementes) ou um nó em nuvem ou universitário.

Decorre daí uma implicação para esta trilha: o treinamento de aprendizado por reforço multiagente (*Multi-Agent Reinforcement Learning*, MARL), que exige muitos episódios, enfrentará restrição ainda mais severa. O protocolo experimental deve, por isso, prever um simulador reduzido (corredor) ou adotar o surrogate em GNN como motivação central, e declarar a limitação de hardware. Tais valores são estimativas do produto, e não medições de treinamento. TODO(evidência): medir passos/s de SUMO na rede unificada e consumo de memória por execução.

## 4.3 Calibração, métricas e execuções (stub)

TODO(evidência): contagens de tráfego (`deferred`), GEH/RMSE (`arteria/calibration/goodness_of_fit.py`), métricas (`arteria/evaluate/metrics.py`; leitura de `tripinfo.xml` real ainda por fazer).

## 4.4 Síntese e limitações do capítulo

Em síntese, o capítulo registra que a cadeia de construção da rede executa de ponta a ponta sobre dados reais e que o hardware local disponível impõe um teto de avaliações por simulação incompatível com treinamento multiagente ingênuo, o que reforça a motivação do surrogate em GNN.

A limitação central, contudo, é que nenhum experimento de aprendizado existe: os números apresentados são contagens operacionais de um teste de roteabilidade e estimativas de orçamento, não medições de desempenho, e a demanda usada é aleatória, sem relação com a de SJC. Como trabalho futuro, restam o protocolo de treino, validação e teste, a classificação das viagens inviáveis e a medição do desempenho do simulador na rede unificada.

Dessa forma, delimitar desde já o que o estudo de caso não demonstra é o que preserva sua credibilidade como base de evidência para o planejamento municipal quando os experimentos forem, de fato, executados.
