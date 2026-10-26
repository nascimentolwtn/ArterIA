# Capítulo 5 — Estudo de caso: corredor B (rascunho)

> Status: rascunho. Rótulo: RASCUNHO — NÃO CITÁVEL COMO RESULTADO. O corredor B é prioridade de construção do produto ArterIA (decisão qualitativa do responsável, `bf725e9`), não recorte validado desta dissertação. O enquadramento operacional/FAB não foi validado por nenhum orientador do PPGAO. Nada neste capítulo contém resultado de simulação calibrada.

## 5.1 Objeto

O corredor B liga a Av. Andrômeda ao DCTA / Jardim Satélite, em São José dos Campos. Segundo o levantamento qualitativo do responsável do projeto (`cities/sjc/candidate-corridors.md`), não há ligação direta entre os dois pontos: o trajeto para oeste exige a Rodovia Presidente Dutra ou um laço longo por viadutos, e o retorno é assimétrico. É, entre os quatro candidatos do produto, o mais próximo da alternativa de "corredor de acesso crítico único" da Seção 5 do `pre-projeto.md`. Esse levantamento não se baseia em contagens nem em dados de Pesquisa OD (esta última recusada permanentemente, ADR 0013).

## 5.2 O que foi executado (registro de verificação técnica, 2026-10-26)

Primeira execução real, ponta a ponta, no desktop do responsável (WSL2): delimitação por Nominatim, extração recortada do extrato Geofabrik Sudeste, conversão PBF para XML com `osmium cat`, construção com `netconvert` e visualização no `sumo-gui` com 1.800 veículos aleatórios (415 viagens inviáveis descartadas). Apenas o corredor B foi renderizado; os corredores D, C e A têm polígonos mas não têm rede. Fonte: CHANGELOG [1.0]; procedimento em `docs/local/sjc-quickstart.md`. A execução revelou correções necessárias no pipeline (netconvert não lê PBF; três consultas de geocodificação falhavam ou erravam, uma delas resolvendo cerca de 30 km ao norte) — registradas no Capítulo 4, seção 4.1.

FIGURA(TODO): captura do `sumo-gui` do corredor B, caso o responsável autorize sua inclusão e após conferência com imagem de satélite. A figura ilustraria a rede, não o desempenho.

## 5.3 O que o planejador/gestor pode e não pode concluir neste nível de maturidade

Quadro de leitura para decisão aplicada (PPGAO, AO-EL). Sustentado pelo repositório apenas o que está na coluna "pode".

| Pode-se afirmar | Não se pode afirmar |
|---|---|
| Existe uma cadeia reproduzível em princípio (ainda sem manifesto de proveniência) que produz uma rede SUMO do corredor B a partir de dados abertos | Que a rede reproduz fielmente a malha real (não auditada contra imagem/campo) |
| A rede é majoritariamente roteável por demanda aleatória | Que a demanda representa o tráfego real, ou que há baseline calibrado |
| Há erros de validador, em sua maior parte atribuíveis à inadequação das verificações (Cap. 4, 4.1.2) | Que a rede esteja livre de defeitos reais: a análise individual não foi feita |
| O corredor B é plausível como caso de acesso único (levantamento qualitativo) | Que B seja o recorte correto da dissertação, ou que o enquadramento FAB esteja validado |
| Nenhuma conclusão sobre tempo de acesso, resiliência, continuidade ou custo logístico | Qualquer afirmação quantitativa sobre essas métricas |

## 5.4 Etapas operacionais pendentes antes de qualquer cenário

TODO(evidência), em ordem lógica proposta:

1. adaptar o validador a redes reais (pares de arestas opostas; componentes fortemente conexos; separar becos de borda);
2. investigar as 415 viagens inviáveis e os dois nós semafóricos sem `<tlLogic>`;
3. revisão manual no `netedit` com registro de patches (Cap. 4, 4.1.4);
4. decidir sobre rede unificada versus por corredor e regra de portais de borda (Cap. 4, 4.1.3);
5. obter contagens (hoje `deferred`) ou definir proxy declarado para calibrar demanda sintética (ADR 0013);
6. só então parametrizar cenários de interdição de corredor, sem alegação de evacuação em escala de rede (limite da ADR 0013).

## 5.5 Cenários de interdição e resultados

Nenhum cenário foi parametrizado ou executado. Seção mantida como `stub`.
