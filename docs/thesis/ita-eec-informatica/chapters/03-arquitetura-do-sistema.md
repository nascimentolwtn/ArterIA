# Capítulo 3 — Arquitetura do Sistema

> Status: **rascunho parcial** (apenas as Seções 3.2 a 3.5 têm prosa; 3.1 e 3.6 em `stub`).
> RASCUNHO: texto sujeito a revisão com orientador(a), ainda não contatado(a). Nenhum resultado de RL/GNN existe; as seções abaixo descrevem a construção e a verificação da **rede de simulação**, pré-condição do grafo de RL/GNN.
> Rastreabilidade: os caminhos de arquivo, comandos e commits que lastreiam cada afirmação estão registrados no `progress-log.md` e no `progress.md` desta trilha, e não no corpo do capítulo. Itens sem lastro estão como `TODO(evidência)` ou `TODO(citação)`.

Este capítulo sustenta que, antes de qualquer agente ou modelo substituto, a qualidade do grafo viário derivado de dados abertos constitui parte do próprio método, e não um detalhe de preparação: o grafo sobre o qual a política e a GNN operam é uma representação com erro, cuja construção, verificação e reprodutibilidade precisam ser tratadas com o mesmo rigor que o aprendizado.

## 3.1 Visão geral da arquitetura (stub)

TODO(evidência): diagrama de componentes (pipeline de dados, ambiente TraCI, agentes + GNN, infraestrutura de experimentação), conforme Seção 9 de `pre-projeto.md`. FIGURA(TODO): diagrama de componentes com as fronteiras de execução (sessão remota vs. desktop, ADR 0009).

## 3.2 Uma rede de simulação construída em cadeia a partir de dados abertos (RASCUNHO)

A rede viária do recorte é obtida por uma cadeia de quatro etapas, executada na estação de trabalho local, em ambiente Linux sob Windows, conforme a escolha de ambiente de desenvolvimento adotada no projeto.

Na primeira etapa, de **delimitação da área de estudo**, uma lista de pontos de referência por candidato é geocodificada por um serviço público de geocodificação baseado no OpenStreetMap (OSM); toma-se, em seguida, o fecho convexo desses pontos e expande-se tal fecho por uma distância fixa (*buffer*), produzindo um polígono provisório, em formato geoespacial aberto. Trata-se de rascunho, a ser conferido contra imagem de satélite.

Na segunda, de **extração do OSM**, obtém-se o extrato regional do Sudeste brasileiro distribuído publicamente e recorta-se tal extrato ao polígono da área de estudo.

Na terceira, de **conversão para rede do simulador**, o extrato recortado é primeiro convertido do formato binário compactado para o formato XML do OSM e só então submetido ao conversor de redes do SUMO. A conversão intermediária mostrou-se necessária porque o conversor de redes não lê o formato binário, o que fez falhar a primeira execução real, corrigida na versão 1.0 do ArterIA. As opções padrão de importação adotadas removem nós geométricos redundantes, inferem rotatórias e rampas, unem junções próximas, inferem semáforos, descartam semáforos em junções simples, agrupam semáforos vizinhos e preservam os nomes de rua e os identificadores originais do OSM; segundo o histórico de versões, as demais opções padrão foram aceitas como escritas.

Na quarta, de **inspeção e demanda de teste**, a rede foi aberta na interface gráfica do simulador com 1.800 veículos gerados aleatoriamente; 415 viagens inviáveis (sem rota) foram descartadas pelo gerador. O objetivo é exclusivamente verificar a roteabilidade e a plausibilidade visual.

**Escopo da execução.** A primeira execução construiu apenas o candidato B (Av. Andrômeda ↔ DCTA / Jardim Satélite). Posteriormente, em 2026-10-26, foram construídas redes também para D, C e A, e adotou-se, como escolha de arquitetura formalmente aceita, **uma única rede de SJC**, recortada ao envelope retangular de todos os polígonos candidatos, com B, D, C e A como *áreas de avaliação* nomeadas (conjuntos de arestas e, futuramente, zonas de tráfego) dentro dela. A justificativa frente à alternativa de redes isoladas é que os polígonos não são independentes (B e C tocam A; D dista cerca de 0,3 km de A) e que recortes isolados cortam fluxos de passagem em fronteiras arbitrárias.

Os tamanhos registrados naquela decisão (SUMO 1.28, parâmetros padrão) estão sintetizados na Tabela 3.1.

| Rede | Arestas | Fração no maior componente fortemente conexo |
|---|---|---|
| B | 2.074 | 85,1% |
| D | 1.203 | 69,9% |
| C | 919 | 86,9% |
| A | 2.256 | 88,3% |
| Envelope unificado | 11.035 | 94,0% |

*Tabela 3.1 — Tamanho das redes por candidato e da rede unificada inicial.*

O envelope unificado corresponde a cerca de 1,7 vez a soma das quatro redes individuais (26 MB de arquivo de rede). Os 6% fora do componente principal e os becos de borda permanecem, e as redes por candidato ficam apenas para checagem visual, não como base de resultados. A própria decisão reconhece seu custo: simulações mais lentas, com possibilidade futura de uma rede derivada só do corredor caso o laço do otimizador sofra; reconhece, ainda, que a escolha é de difícil reversão, pois a linha de base, a demanda e a calibração ficam amarradas aos identificadores de aresta.

Decorre daí uma implicação para esta trilha, ainda como hipótese de projeto: o grafo do ambiente de RL/GNN passa a ter ordem de 10^4 arestas, e a definição de "agente" (por área de avaliação, por junção ou por aresta) precisa ser decidida sobre esse grafo único; nenhuma dessas escolhas foi implementada. Ademais, a ordem B > D > C > A é prioridade de engenharia de produto, e não critério acadêmico de seleção de corredor.

**Ressalvas.** Três ressalvas delimitam o alcance da execução. Em primeiro lugar, a demanda aleatória de teste não guarda relação com a demanda real de SJC; o cenário de treinamento e de avaliação será sempre um "cenário sintético calibrado a fluxos observados", nunca "o tráfego real de SJC", em decorrência da escolha metodológica de dispensar microdados de origem-destino. Em segundo lugar, o resultado não é linha de base calibrada nem escolha validada de corredor. Por fim, não constitui evidência para este capítulo além do registro de que o pipeline executa de ponta a ponta.

**Atualização (2026-10-27, trabalho ainda não incorporado ao repositório na data da redação).** Após a primeira inspeção do responsável, as áreas de estudo de B (de 5,31 para 7,67 km²) e C (de 1,54 para 4,17 km²) foram estendidas, e a rede unificada foi reconstruída para o envelope maior. Os tamanhos de 11.035 arestas e 94,0% acima correspondem à construção inicial e estão superados: a rede vigente tem **14.225 arestas e 6.655 junções, com 93,1% das junções no componente principal roteável e 0 erros de validação** (127 avisos: becos sem saída, junções semafóricas sem uso e componentes fora do principal). Cabe, contudo, uma atenção metodológica: a fração de 94,0% referia-se a arestas, e a de 93,1% refere-se a junções, de modo que as duas não são diretamente comparáveis. TODO(evidência): confirmar no código do validador a unidade de cada fração antes de compará-las no texto final.

Os identificadores de aresta mudaram com a reconstrução, o que invalida referências a identificadores da rede de 11.035 arestas. Os corredores A, B (derivado), C, D e a ligação A-B existem como sequências ordenadas de arestas dessa rede e, segundo o histórico de versões, tiveram a geometria conferida em imagem aérea pelo responsável em 2026-10-27, inclusive a extensão de C a oeste/sudoeste e as áreas estendidas de B e C. Tal verificação é visual e feita pelo responsável, não constituindo validação de atributos (faixas, velocidades, restrições de giro). TODO(evidência): comprimento total da rede unificada (não reportado nas fontes lidas).
TODO(citação): citar SUMO (ver `references.bib`, chave `lopez2018sumo`) e documentação do `netconvert` para versão 1.28.0 (versão informada pelo responsável; a ser confirmada em `manifest.json`).

## 3.3 Uma validação ajustada a redes de teste não se transfere a redes reais (RASCUNHO)

O validador estrutural do projeto foi desenvolvido e ajustado exclusivamente contra redes de teste escritas à mão, em decorrência da divisão de trabalho que restringe as sessões remotas a dados sintéticos. Sua primeira aplicação a uma rede real (candidato B) produziu **729 erros e 7.562 avisos**. A análise do responsável do projeto indica que a maior parte é ruído de um validador mal calibrado para redes reais, e não defeito da rede, conforme sintetiza a Tabela 3.2.

| Verificação | Contagem | Diagnóstico | Ação prevista |
|---|---|---|---|
| Sentido único | 7.522 avisos | Falso positivo: o formato de rede do SUMO não possui atributo de sentido único; 5.448 dessas arestas são internas às junções | Substituir por detecção de pares de arestas opostas; ignorar arestas internas |
| Conectividade | 727 erros | Medida a partir de uma única junção inicial em extrato recortado; esperada | Substituir por análise de componentes fortemente conexos (principal vs. órfãos) |
| Becos sem saída | 40 avisos | Majoritariamente arestas de borda do recorte | Tratar separadamente os becos de borda |
| Lógica semafórica | 2 erros | Reais: dois aglomerados de travessia exclusiva de bicicleta tipados como semafóricos sem programa semafórico associado (2 de 18 junções semafóricas); impacto na simulação não verificado | Verificar no simulador se há efeito; decidir entre correção manual no editor de redes ou ajuste de parâmetro |

*Tabela 3.2 — Achados do validador estrutural na primeira rede real. Fonte: histórico de versões do ArterIA (versão 1.0) e notas de trabalho do projeto (2026-10-26). Conferência aritmética: 727 + 2 = 729 erros e 7.522 + 40 = 7.562 avisos; as quatro categorias esgotam os totais relatados.*

**Atualização.** O validador foi, em seguida, adaptado à semântica de redes reais do SUMO: passou a usar componentes fortemente conexos, detecção de pares de arestas opostas e tratamento separado de becos de borda. Segundo o registro da alteração, os 729 erros anteriormente reportados na rede real do corredor B caíram para 0. Tal resultado confirma, em sentido restrito, que os erros eram em sua maior parte artefatos do validador, e não da rede; não implica, contudo, que a rede esteja correta, uma vez que o diagnóstico dos 2 erros de lógica semafórica e a validade das heurísticas permanecem como descritos abaixo. TODO(evidência): conferir no código/relatório se a verificação `traffic_light_logic` continua apontando os 2 aglomerados ou foi reclassificada, e qual passou a ser a distribuição de componentes reportada.

**Atualização (2026-10-28) — verificação cruzada contra fontes públicas independentes.** Além do validador estrutural (conectividade, arestas opostas, becos), a rede unificada passou por um segundo tipo de verificação, que a compara contra duas fontes externas: a Base de Faces de Logradouros do Instituto Brasileiro de Geografia e Estatística (IBGE), edição 2022, e as camadas de arruamentos e de Hierarquia Viária do portal geoespacial da prefeitura (GeoSanja), ambas registradas no inventário de dados da cidade e obtidas por download público, sem contato com órgão. A comparação restringe-se aos quatro corredores do estudo (faixa de 50 m), por nome de rua normalizado (contra o IBGE) e por geometria de centro de linha amostrado a cada 5 m, com limiar de 15 m (contra o IBGE e o GeoSanja).

Os resultados relatados pelo responsável do projeto, não reexecutados nem lidos em código nesta revisão, indicam 543 nomes de rua coincidentes entre o OSM e o IBGE dentro dos corredores (167 só no OSM, 201 só no IBGE); distância mediana amostra-referência de cerca de 3,0 m, com 6,4% das amostras acima do limiar; 81,5% do comprimento de centro de linha do OSM dentro de 15 m do GeoSanja; e 97,2% do GeoSanja dentro de 15 m do OSM. Parte dos descasamentos de maior distância é atribuída a nomes de rua genéricos reaproveitados em vias distintas (ex. "Rua Dois", "Viela Três"), e não a erro geométrico real. Trata-se, portanto, de verificação de triagem — o próprio casamento por nome é deliberadamente grosseiro —, e não de calibração: não cobre faixas, sentido de via ou restrições de giro, que permanecem com a baixa cobertura de atributos já registrada (número de faixas em cerca de 4% e velocidade máxima em cerca de 5% das ruas residenciais, conforme a entrada de 2026-10-27 do log desta trilha).

Um achado colateral foi, em seguida, resolvido. O escape duplo de apóstrofos em nomes de rua (ex. "D'Ávila") tinha causa raiz no próprio conversor de redes do SUMO — defeito confirmado em caso de teste isolado contra a versão 1.28.0, no qual o caractere literal é substituído pela entidade XML internamente e a própria entidade é escapada de novo na escrita —, e não em etapa do ArterIA. Uma correção automática passou a ser aplicada após toda conversão, e a rede real foi reconstruída com ela (58 caracteres corrigidos em 3 nomes de rua; estrutura de rede inalterada). A verificação cruzada foi reexecutada contra a rede corrigida, resultando em 544 nomes coincidentes com o IBGE (166 só no OSM, 200 só no IBGE), que substituem os números 543/167/201 citados acima; os números de geometria ficaram inalterados. Geraram-se, também, mapas da rede coloridos por prioridade de aresta, com os quatro contornos de área de estudo, sem valor probatório além da inspeção visual. TODO(evidência): ler `crosscheck.py` e reexecutar o comando antes de tratar estes números (originais ou corrigidos) como consolidados.

**Interpretação metodológica (hipóteses, sem resultado experimental).** Cinco hipóteses decorrem dos achados acima.

A primeira é que *a validação sobre redes de teste não se transfere a redes reais*. Os verificadores devem ser reescritos contra a semântica do formato de rede do simulador (arestas internas, ausência de atributo de sentido único) e testados com uma fatia de rede real incluída nos testes, tarefa já registrada nas notas de trabalho do projeto.

A segunda é que *a conectividade em extrato recortado é, por construção, parcial*. A métrica adequada é a distribuição dos tamanhos dos componentes fortemente conexos (algoritmo de Tarjan, `tarjan1972`), com declaração do componente principal e dos órfãos; os trechos órfãos devem ser excluídos ou marcados antes de se definirem observações e ações.

A terceira diz respeito ao *efeito de borda*. As arestas de corte criam fontes e sumidouros artificiais, e viagens entre origens e destinos dentro do recorte podem exigir rotas que, na rede completa, usariam vias externas a ele, o que afeta as métricas de tempo de viagem e de acessibilidade. TODO(evidência): quantificar a fração de viagens inviáveis atribuível ao recorte (as 415 viagens descartadas não foram classificadas por causa).

A quarta refere-se à *completude e à qualidade do OSM*. A qualidade do OSM varia no espaço (TODO(citação): `haklay2010osm`, `barrington2017osm` para completude), de modo que a revisão manual no editor de redes é etapa metodológica a documentar, sob a forma de correções versionadas, nunca de edição direta da rede gerada, conforme a política de dados adotada no projeto. TODO(evidência): spot-check de completude de SJC ainda não realizado (`.claude/napkin.md`, item 6).

A quinta, por fim, refere-se aos *semáforos inferidos*. As opções de inferência e de agrupamento de semáforos do conversor de redes deduzem a presença e o agrupamento de semáforos a partir de heurísticas, constituindo fonte de incerteza capaz de gerar casos como os 2 aglomerados sem programa semafórico. Sem planos semafóricos reais, cuja obtenção foi adiada, os tempos são os padrão do conversor.

## 3.4 A qualidade da rede condiciona observação, ação e GNN (RASCUNHO — hipóteses de projeto)

O primeiro objetivo específico do pré-projeto exige uma representação formal da rede como grafo heterogêneo e dinâmico. A rede do simulador contém arestas, faixas, junções, conexões e programas semafóricos, e a passagem para o grafo de RL/GNN exige decisões que a qualidade da rede condiciona. Cinco delas merecem registro.

A primeira concerne às **arestas internas às junções**, que representam trajetórias dentro das interseções (5.448 das 7.522 ocorrências de aviso de sentido único na rede do corredor B). Permanece em aberto se devem ser excluídas do grafo da GNN, tratando-se a junção como nó, ou mantidas como arestas; tal escolha altera o tamanho do grafo e o alcance da passagem de mensagens (*message passing*). TODO(evidência): comparação empírica das duas opções, se viável.

A segunda concerne aos **componentes órfãos**. Componentes desconectados do principal não participam de roteamento realista, e incluí-los na observação adiciona nós sem fluxo; propõe-se, por isso, filtrar a rede pelo componente fortemente conexo principal antes de construir o grafo.

A terceira concerne aos **nós e arestas de borda do recorte**, que, conforme a Seção 3.3, têm grau e fluxo artificiais. Propõe-se um atributo binário de borda nas características de nó e de aresta, para que a política e o surrogate possam distinguir o comportamento de fronteira do comportamento interior — hipótese ainda não testada.

A quarta concerne aos **semáforos inferidos**. O tipo e o programa semafórico são características candidatas de nó, e sua incerteza (Seção 3.3) sugere marcar a origem da informação (inferida vs. observada). O controle de sinalização permanece, contudo, fora do escopo central (Seção 6 do pré-projeto).

A quinta, por fim, concerne à **fidelidade do grafo frente às conclusões do surrogate**. Erros estruturais do grafo (arestas ausentes por OSM incompleto, restrições de giro erradas) propagam-se para o surrogate, que aprende a dinâmica da rede *simulada*, e não a de SJC. A dissertação deve, assim, distinguir a validade interna (surrogate vs. simulador) da validade externa (simulador vs. cidade).

Nenhuma dessas escolhas foi implementada, e não há, até esta data, código de extração de grafo para a GNN no repositório. TODO(evidência): protótipo de conversão `.net.xml` → grafo (por exemplo, com `sumolib`; TODO(citação): confirmar API) e estatísticas do grafo resultante.

## 3.5 A reprodutibilidade da construção da rede como pré-condição do aprendizado (RASCUNHO)

Cada construção de rede deve ser rastreável ao extrato de dados de origem (data e identificação criptográfica do arquivo), ao polígono da área de estudo (identificação criptográfica do arquivo geoespacial), à versão da ferramenta de recorte, à versão do SUMO (1.28.0, segundo o responsável), à lista exata de opções do conversor de redes e às eventuais correções manuais. O repositório dispõe de um registro de proveniência por execução (identificação da versão do código, versão do SUMO, semente, identificação da configuração e somas de verificação das entradas), mas, até esta data, nenhuma rotina de construção de rede o invoca. O diretório de dados passou, ademais, a ficar dentro do repositório, porém excluído do controle de versão, assim como os arquivos de rede gerados. TODO(evidência): confirmar se `arteria network build` grava manifesto; caso contrário, registrar como lacuna de reprodutibilidade.

**Atualização (2026-10-27; Fase 2 do roteiro; trabalho não incorporado ao repositório na data da redação, relatado no histórico de versões e não reexecutado nesta revisão).** A lacuna descrita acima passou a ser endereçada por um mecanismo de reconstrução reprodutível da rede, composto por quatro elementos.

O primeiro é um **retrato fixo do OSM**: registra-se o arquivo regional do Sudeste (gerado em 2026-10-25), sua identificação criptográfica e a do extrato recortado da cidade, e a etapa de obtenção recusa fonte ou extrato que difira do fixado, salvo atualização deliberada.

O segundo é uma **rotina de reconstrução** que confere o retrato, recorta, converte, valida, compara com a rede de referência fixada e grava o registro de proveniência. Segundo o relato, a rede reconstruída é idêntica à existente (14.225 arestas), e uma segunda execução a reproduziu. Como o conversor de redes grava um comentário com data e hora a cada construção, a identificação do arquivo bruto muda sempre, razão pela qual a comparação usa uma **identificação de conteúdo** que ignora esse cabeçalho. A reconstrução dura cerca de 16 s.

O terceiro é um **mecanismo de correções**: as correções à rede passam a ser arquivos XML simples, listados em um inventário próprio e aplicados por uma segunda passada do conversor, uma vez que o SUMO 1.28 não oferece opção nativa de correção incremental. Nenhuma correção foi necessária até aqui, de modo que o mecanismo não foi exercido sobre um caso real.

O quarto é uma **comparação entre versões de rede**, que lista arestas, faixas e junções adicionadas, removidas ou alteradas, em formato estruturado e textual. Como demonstração de sanidade, a rede antiga, só de B, comparada à unificada, resultou em 12.175 arestas adicionadas, 24 removidas e 137 alteradas; trata-se de verificação de que a ferramenta funciona, e não de resultado de pesquisa.

A importância desse mecanismo para esta trilha é direta: um ambiente de RL e uma GNN treinada sobre o grafo exigem que o grafo, com seus identificadores de aresta, seja reconstruível de forma idêntica em conteúdo a partir de entradas fixadas, pois a linha de base, a demanda e a calibração ficam amarradas a tais identificadores. Seus limites são, contudo, igualmente claros: a reprodutibilidade aqui é a da *construção da rede*, não a do treinamento (sementes, pontos de verificação) nem a da simulação, e o retrato fixo do OSM é uma fotografia, não uma validação do OSM. Quanto à pergunta acima, o registro de proveniência da reconstrução é relatado como existente, mas seu formato e sua relação com o registro de proveniência por execução não foram verificados. TODO(evidência): ler `arteria/network/rebuild.py` e `arteria/provenance.py` após o commit e descrever os campos efetivamente gravados.

## 3.6 Ambiente de controle do simulador, agentes e GNN (stub)

TODO(evidência): nada implementado. Contrato ação → transformação de rede: ver `arteria/interventions/apply.py` (`apply_intervention()`), sete dos dez tipos de catálogo despachados (após `2624762`); `reversible_lane`, `new_connector` e `transit_signal_priority` sem transformação.

## 3.7 Síntese e limitações do capítulo

Em síntese, o capítulo mostra que a rede de simulação de SJC já existe como artefato construído em cadeia a partir de dados abertos, verificado estruturalmente, cruzado contra fontes públicas independentes e reconstruível de forma reprodutível, mas que cada uma dessas etapas introduz decisões e incertezas que condicionam diretamente o grafo sobre o qual os agentes e a GNN operarão.

As limitações são, contudo, explícitas. Nenhum componente de aprendizado foi implementado; os números de validação e de verificação cruzada provêm de relatos do responsável, ainda não reexecutados nesta revisão; a verificação geométrica não cobre atributos de capacidade nem restrições de giro; e a reprodutibilidade demonstrada restringe-se à construção da rede. Como trabalho futuro, restam o protótipo de conversão da rede em grafo, a definição da unidade de agente sobre a rede unificada e a análise do efeito das escolhas de construção como fator de ablação.

Dessa forma, tratar a qualidade do grafo como parte do método é o que permite que um sistema de apoio à decisão baseado em aprendizado seja apresentado ao planejamento urbano com limites de validade declarados, e não como caixa-preta treinada sobre uma cidade que ele apenas aproxima.
