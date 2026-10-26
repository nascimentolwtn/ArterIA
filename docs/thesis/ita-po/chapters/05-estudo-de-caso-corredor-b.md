# Capítulo 5 — Resultados / Estudo de caso: corredor B (RASCUNHO)

Status: stub com esboço de estudo de caso. Não há resultados. O corredor B é apenas a primeira rede construída pelo ArterIA (prioridade B>D>C>A); não foi escolhido como recorte da dissertação.

> RASCUNHO: esta seção descreve o desenho do estudo de caso e o que já existe. Nenhum número de desempenho de tráfego é apresentado porque nenhuma linha de base calibrada existe.

## 5.1 Caracterização do corredor

Corredor B: Av. Andrômeda <-> DCTA / Jardim Satélite, em São José dos Campos (`cities/sjc/candidate-corridors.md`). O problema qualitativo registrado no ArterIA é de ausência de ligação direta e desvio longo, não de congestionamento de pico; não há, para B, base qualitativa de janela de pico equivalente à de A e D (ADR 0003, `progress.md` (9)). O polígono conecta-se ao Anel Viário do Candidato A.

## 5.2 O que existe (2026-10-26)

Uma rede SUMO do corredor B, construída a partir do OSM (Capítulo 4, Seção 4.1), renderizada em `sumo-gui` com 1.800 veículos aleatórios não calibrados. É um teste de rotabilidade e inspeção visual.

## 5.3 O que falta antes de qualquer resultado

1. Validador adaptado a redes reais e revisão manual da rede (Capítulo 4, Seção 4.1.3).
2. Demanda: cenário sintético calibrado por contagem (ADR 0013); contagens reais de SJC ainda `deferred`.
3. Linha de base calibrada (GEH/RMSE, `goodness_of_fit.py`), com réplicas e intervalo de confiança (`replication.py`).
4. Catálogo $\mathcal{I}$ do corredor: provável necessidade de `new_connector`, ainda sem transformação (`progress.md` (11)/(12)). Alegações de benefício do conector limitadas ao corredor (ADR 0013).
5. Avaliação before/after das métricas da Seção 10 do pré-projeto; sensibilidade à incerteza estrutural da rede (Capítulo 3, Seção 3.x).

TABELA(TODO): comparação before/after de $f_1$ e $f_2$ no corredor B. Sem dados.
