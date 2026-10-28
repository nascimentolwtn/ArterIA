# Capítulo 5 — Resultados / Estudo de caso: corredor B (RASCUNHO)

Status: stub com esboço de estudo de caso. Não há resultados. O corredor B é apenas a primeira rede construída pelo ArterIA (prioridade B>D>C>A); não foi escolhido como recorte da dissertação.

> RASCUNHO: esta seção descreve o desenho do estudo de caso e o que já existe. Nenhum número de desempenho de tráfego é apresentado porque nenhuma linha de base calibrada existe.

Este capítulo sustenta, no estado atual, uma tese deliberadamente modesta: o corredor B dispõe de uma rede de simulação roteável, mas ainda não de nenhuma das condições necessárias para que se reporte um resultado de desempenho. As seções a seguir caracterizam o corredor, descrevem o que existe e enumeram, em ordem de dependência, o que falta.

## 5.1 Um problema de ligação, não de congestionamento

O corredor B liga a Av. Andrômeda ao DCTA / Jardim Satélite, em São José dos Campos. O problema qualitativo registrado no ArterIA é de ausência de ligação direta e de desvio longo, e não de congestionamento de pico; diferentemente dos candidatos A e D, cuja janela de pico foi aceita com base em experiência local qualitativa, não há para B base qualitativa equivalente. O polígono do corredor conecta-se, ademais, ao Anel Viário do Candidato A.

## 5.2 O que existe: uma rede roteável (2026-10-26)

Existe uma rede SUMO do corredor B, construída a partir do OpenStreetMap (Capítulo 4, Seção 4.1) e inspecionada na interface gráfica do simulador com 1.800 veículos aleatórios não calibrados. Trata-se de um teste de roteabilidade e de inspeção visual, não de um resultado.

## 5.3 O que falta antes de qualquer resultado

Cinco condições precedem qualquer resultado. Em primeiro lugar, são necessários o validador adaptado a redes reais e a revisão manual da rede (Capítulo 4, Seção 4.1.3). Em segundo lugar, a demanda deve ser construída como cenário sintético calibrado por contagem, caminho metodológico adotado em lugar de microdados de pesquisa origem-destino; as contagens reais de SJC, contudo, seguem adiadas. Em terceiro lugar, exige-se uma linha de base calibrada pelos critérios de aderência GEH/RMSE, com réplicas e intervalo de confiança. Em quarto lugar, o catálogo $\mathcal{I}$ do corredor provavelmente requer um novo conector, classe de intervenção ainda sem transformação implementada; as alegações de benefício de tal conector ficam, ademais, limitadas ao corredor, por força do regime de demanda sintética. Por fim, resta a avaliação before/after das métricas da Seção 10 do pré-projeto, acompanhada da sensibilidade à incerteza estrutural da rede (Capítulo 3, Seção 3.x).

TABELA(TODO): comparação before/after de $f_1$ e $f_2$ no corredor B. Sem dados.

A limitação central deste capítulo, no estado atual, é a inexistência de linha de base calibrada, o que impede qualquer afirmação sobre o desempenho do corredor. Tal cautela não é meramente formal: ela resguarda o uso futuro do estudo de caso como evidência técnica para o planejamento municipal, evitando que uma verificação visual de pipeline seja tomada por resultado.
