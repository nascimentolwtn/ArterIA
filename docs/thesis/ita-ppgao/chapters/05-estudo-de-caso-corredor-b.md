# Capítulo 5 — Estudo de caso: corredor B (rascunho)

> Status: rascunho. Rótulo: RASCUNHO — NÃO CITÁVEL COMO RESULTADO. O corredor B é prioridade de construção do produto ArterIA (decisão qualitativa do responsável), e não recorte validado desta dissertação. O enquadramento operacional/FAB não foi validado por nenhum orientador do PPGAO. Nada neste capítulo contém resultado de simulação calibrada. A rastreabilidade técnica está registrada em `progress.md`.

Este capítulo sustenta que o corredor B, no estágio atual, é um caso plausível de acesso crítico único às instalações do DCTA, mas que o material disponível autoriza apenas afirmações sobre a existência e a roteabilidade da rede, e não sobre desempenho logístico ou resiliência.

## 5.1 O corredor B como caso plausível de acesso crítico único

O corredor B liga a Av. Andrômeda ao DCTA e ao Jardim Satélite, em São José dos Campos. Segundo o levantamento qualitativo do responsável do projeto, não há ligação direta entre os dois pontos: o trajeto para oeste exige a Rodovia Presidente Dutra ou um laço longo por viadutos, e o retorno é assimétrico. Trata-se, entre os quatro candidatos do produto, do mais próximo da alternativa de "corredor de acesso crítico único" da Seção 5 do pré-projeto. Tal levantamento não se baseia, contudo, em contagens nem em dados da Pesquisa Origem-Destino (OD), esta última recusada permanentemente como escolha metodológica justificada por razões de privacidade.

## 5.2 A primeira execução ponta a ponta como verificação técnica (2026-10-26)

A primeira execução real, ponta a ponta, ocorreu na estação de trabalho do responsável, sob ambiente Linux em Windows. Compreendeu a delimitação do recorte por geocodificação (serviço Nominatim), a extração recortada do extrato regional Geofabrik Sudeste, a conversão do formato binário do OpenStreetMap para XML, a construção da rede pela ferramenta de conversão do SUMO e a visualização na interface gráfica do simulador com 1.800 veículos aleatórios (415 viagens inviáveis descartadas). Apenas o corredor B foi renderizado; os corredores D, C e A têm polígonos, mas não têm rede. Ademais, a execução revelou correções necessárias na cadeia de construção — a ferramenta de conversão não lê o formato binário, e três consultas de geocodificação falhavam ou erravam, uma delas resolvendo cerca de 30 km ao norte —, registradas no Capítulo 4, Seção 4.1.

FIGURA(TODO): captura do `sumo-gui` do corredor B, caso o responsável autorize sua inclusão e após conferência com imagem de satélite. A figura ilustraria a rede, não o desempenho.

## 5.3 O que o planejador ou gestor pode concluir neste nível de maturidade

Para a decisão aplicada, própria da área de Análise Operacional e Engenharia Logística (AO-EL) do PPGAO, convém separar o que o material disponível sustenta do que não sustenta. A Tabela 5.1 organiza essa leitura; o repositório sustenta apenas o que consta da coluna "Pode-se afirmar".

**Tabela 5.1 — Quadro de leitura para decisão aplicada**

| Pode-se afirmar | Não se pode afirmar |
|---|---|
| Existe uma cadeia reproduzível em princípio (ainda sem manifesto de proveniência) que produz uma rede SUMO do corredor B a partir de dados abertos | Que a rede reproduz fielmente a malha real (não auditada contra imagem/campo) |
| A rede é majoritariamente roteável por demanda aleatória | Que a demanda representa o tráfego real, ou que há linha de base calibrada |
| Há erros de validador, em sua maior parte atribuíveis à inadequação das verificações (Cap. 4, 4.1.2) | Que a rede esteja livre de defeitos reais: a análise individual não foi feita |
| O corredor B é plausível como caso de acesso único (levantamento qualitativo) | Que B seja o recorte correto da dissertação, ou que o enquadramento FAB esteja validado |
| Nenhuma conclusão sobre tempo de acesso, resiliência, continuidade ou custo logístico | Qualquer afirmação quantitativa sobre essas métricas |

Fonte: elaborado pelo autor.

## 5.4 Etapas operacionais que antecedem qualquer cenário

TODO(evidência), em ordem lógica proposta:

1. adaptar o procedimento de verificação da rede à realidade de uma malha real (pares de arestas opostas; componentes fortemente conexos; separar becos de borda);
2. investigar as 415 viagens inviáveis e os dois cruzamentos semaforizados que ainda não têm plano de fases definido, hoje tratados como não semaforizados;
3. revisão manual da topologia da rede, comparada a imagem aérea, com registro de cada ajuste aplicado (Cap. 4, 4.1.4);
4. decidir sobre rede unificada versus por corredor e regra de portais de borda (Cap. 4, 4.1.3);
5. obter contagens de tráfego reais (hoje ausentes, sem previsão de levantamento) ou definir proxy declarado para calibrar demanda sintética, dentro do limite de escopo já fixado como escolha metodológica para a geração de demanda;
6. só então parametrizar cenários de interdição de corredor, sem alegação de evacuação em escala de rede (mesmo limite de escopo do item anterior).

## 5.5 Cenários de interdição e resultados

Nenhum cenário foi parametrizado ou executado. Seção mantida como `stub`.

## 5.6 Síntese e limitações do capítulo

Em síntese, o corredor B reúne as características qualitativas de um acesso crítico único às instalações do DCTA, e a cadeia de construção da rede foi executada com sucesso sobre ele, mas apenas como verificação técnica de roteabilidade. A limitação central é que não há demanda calibrada, cenário de interdição, auditoria de campo da rede nem validação do enquadramento por orientador; os trabalhos futuros são, portanto, as etapas enumeradas na Seção 5.4.

Dessa forma, explicitar desde já o que o estudo de caso não autoriza concluir é o que permitirá, no futuro, apresentar à FAB e ao município recomendações de acesso com credibilidade técnica.
