# Esqueleto de Capítulos — Dissertação (ITA, PG/PO) — versão em linguagem simples

> Este esqueleto espelha `docs/thesis/ita-po/outline.md`, a trilha-fonte. O esqueleto-fonte tem muito mais detalhe técnico: hashes de commit, nomes de módulo de código, e o histórico completo de decisões. Este esqueleto dá só o nível de detalhe necessário para um leitor sem fundo técnico entender o estágio de cada capítulo. Para o detalhe técnico completo, leia a trilha-fonte.

> A profundidade desta trilha é `completo`, desde 2026-10-26. Cada capítulo tem um arquivo em `chapters/`. Cada capítulo tem um status: `stub` (não escrito), `rascunho` (parte escrita), ou mais avançado. O registro de progresso desta trilha fica em `progress.md`.

## Status por capítulo

| Cap. | Arquivo | Status | O que falta |
|---|---|---|---|
| 1 | `chapters/01-introducao.md` | stub (não escrito) | confirmar o corredor final de estudo; confirmar o(a) orientador(a) |
| 2 | `chapters/02-revisao-literatura.md` | stub (não escrito) | revisão mais ampla da literatura; fontes sobre a qualidade de redes do OpenStreetMap |
| 3 | `chapters/03-formulacao-metodologia.md` | stub, com uma seção em rascunho | notação final revisada por orientador(a); decisão sobre o tratamento do erro estrutural da rede; contagens reais de tráfego; decisão, ainda pendente, sobre o método de otimização exato ou de relaxação, prometido pelo pré-projeto mas ainda não discutido na prática |
| 4 | `chapters/04-desenvolvimento.md` | rascunho (três seções escritas) | validador de rede adaptado e reexecutado; dados reais de atração de viagens; contagens reais de tráfego; execução real da geração de rotas contra a rede de SJC; uma linha de base calibrada |
| 5 | `chapters/05-estudo-de-caso-corredor-b.md` | stub (só esboço, sem resultados) | todos os resultados |
| 6 | `chapters/06-discussao.md` | stub (não escrito) | os resultados, para poder discuti-los |
| 7 | `chapters/07-conclusao.md` | stub (não escrito) | os resultados, para poder concluir a partir deles |
| 8 | `references.bib` | lista inicial (5 referências, alguns campos ainda incompletos) | expandir a lista a partir da revisão de literatura |

## 1. Introdução

O pré-projeto já traz boa parte do material desta introdução: o problema de pesquisa, a justificativa, o contexto de SJC, o recorte geográfico e os objetivos. Falta escrever o texto de abertura propriamente dito: a motivação em prosa corrida, a pergunta de pesquisa em uma frase, e a estrutura da dissertação. Falta, também, confirmar o corredor exato de estudo antes da versão final, e confirmar o(a) orientador(a).

## 2. Revisão de Literatura

O núcleo de referências já existe: os trabalhos de Miandoabchi et al. (2011, 2013), de Miandoabchi e Farahani (2010), de Verbas et al. (2023) e de Liu et al. (2023). A lacuna de pesquisa deste projeto — um surrogate de aprendizado substituindo a simulação dentro do laço de otimização bi-nível — já está identificada. Falta uma revisão sistemática mais ampla: meta-heurísticas multiobjetivo, otimização Bayesiana multiobjetivo, GNNs como surrogate de simulação de tráfego, e trabalhos aplicados a cidades médias ou ao contexto brasileiro.

## 3. Formulação / Metodologia

A formulação matemática bi-nível multiobjetivo já tem um primeiro esboço (variáveis de decisão, nível superior, nível inferior, objetivos $f_1$ a $f_7$, restrições). A metodologia proposta também já está descrita (SUMO/TraCI, três classes de otimizador, surrogate GNN com amostragem ativa). Falta formalizar a notação final com um(a) orientador(a), detalhar a arquitetura do surrogate, e especificar o protocolo de validação cruzada. Falta, também, resolver uma divergência: a metodologia já nomeia um algoritmo evolutivo, a otimização Bayesiana e duas referências de comparação simples, mas ainda não discute o método exato/relaxado que o pré-projeto também promete comparar. Esse ponto depende de esclarecimento com um(a) orientador(a).

## 4. Desenvolvimento

Esta é a parte mais avançada da dissertação até agora. Uma primeira rede real do corredor foi construída a partir do OpenStreetMap, verificada por várias checagens independentes, e tornada reprodutível. O zoneamento de tráfego e o peso de população de cada zona já foram obtidos. A cadeia que converte uma matriz de origem e destino em rotas já existe como código, mas ainda não rodou contra dados reais de SJC. Falta, ainda: um validador de rede já adaptado e reexecutado sobre a rede final; o peso de atração de viagens (o peso de produção já existe); contagens reais de tráfego; e, por fim, uma linha de base calibrada de fato.

## 5. Resultados

As métricas de avaliação "antes e depois" já estão definidas: tempo de viagem, atraso, filas, confiabilidade de transporte público, exposição de pedestres e ciclistas, emissões, risco de acidente, acesso de emergência, equidade, e custo-benefício. Falta, porém, todo resultado empírico: a calibração validada, a acurácia do surrogate em comparação com a simulação direta, a fronteira de Pareto obtida, e a comparação de desempenho entre os três otimizadores.

## 6. Discussão

As limitações e os riscos já foram antecipados no pré-projeto: dados incompletos, custo computacional, risco de sobreajuste do surrogate, viabilidade jurídica e política, e erro de especificação do modelo de equilíbrio. As contribuições esperadas também já foram descritas. Falta a discussão em si, feita à luz dos resultados: em que condições o surrogate foi (ou não foi) confiável, e o que isso significa na prática para SJC.

## 7. Conclusão

O objetivo geral e os objetivos específicos já estão formulados, o que facilita escrever a conclusão em espelho a eles. A lista do "que evitar" já marca, com clareza, o que esta dissertação não deve afirmar. Falta a síntese final, depois dos resultados, e a recomendação priorizada de pacote de intervenções para o corredor de estudo.

## 8. Referências

A lista inicial de 11 referências já está compilada: os marcos teóricos do problema de desenho de rede urbana bi-nível, e os documentos institucionais de SJC (PlanMob, Plano Diretor, Pesquisa OD, FGV, Linha Verde, SUMO). Falta expandir essa lista a partir da revisão sistemática do Capítulo 2, e padronizar o formato de citação exigido pelo ITA.
