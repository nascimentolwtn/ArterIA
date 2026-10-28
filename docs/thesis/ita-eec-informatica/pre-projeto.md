# Pré-Projeto de Mestrado — ITA, PG/EEC, Área de Concentração Informática

## 1. Título provisório

**Aprendizado por reforço multiagente e redes neurais em grafos para alocação dinâmica de faixas e direções viárias em redes urbanas**

## 2. Resumo

Este pré-projeto propõe investigar métodos de inteligência artificial — aprendizado por reforço (*Reinforcement Learning*, RL) multiagente combinado a redes neurais em grafos (*Graph Neural Networks*, GNN) — para a alocação dinâmica de faixas de tráfego e sentidos de vias em redes urbanas, tendo como estudo de caso a cidade de São José dos Campos (SJC), SP. O trabalho insere-se no desenvolvimento do sistema ArterIA, uma ferramenta de apoio à decisão que avalia pacotes de intervenções viárias (conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas) contra uma simulação de tráfego calibrada no simulador microscópico SUMO (*Simulation of Urban MObility*). Diferentemente de uma abordagem de pesquisa operacional centrada no problema de desenho de rede em si, esta dissertação tem como núcleo o método de IA e a engenharia do sistema: modelar a rede viária como grafo, treinar agentes de RL que cooperam sobre esse grafo, empregar uma GNN como preditor substituto (*surrogate*) do impacto de intervenções — reduzindo a dependência de simulações completas e computacionalmente caras — e integrar tais componentes em um pipeline de treinamento e avaliação reprodutível, acoplado ao simulador por sua interface de controle em tempo de execução (*Traffic Control Interface*, TraCI). O recorte geográfico será um corredor ou subárea de SJC, e os resultados serão avaliados tanto por métricas de tráfego (tempo de viagem, atraso, confiabilidade de ônibus) quanto por métricas de aprendizado de máquina (acurácia do surrogate, custo computacional, convergência), buscando contribuir tanto para a engenharia de sistemas inteligentes de apoio à decisão quanto para o método de RL multiagente aplicado a grafos de infraestrutura.

## 3. Problema de pesquisa e justificativa

Sustenta-se, nesta seção, que a reconfiguração estrutural de redes viárias constitui um problema de pesquisa em Informática, e não apenas de otimização de tráfego. O desenho e a reconfiguração de redes viárias urbanas — decidir sentidos de vias, alocação de faixas e prioridades de interseção — é tradicionalmente tratado como um problema de otimização combinatória de desenho de rede de transporte (*Network Design Problem*, NDP), resolvido por heurísticas, metaheurísticas ou programação bi-nível clássica. Tal formulação enfrenta, contudo, limitações quando se deseja (i) representar explicitamente a topologia da rede e suas dependências espaciais, (ii) lidar com decisões distribuídas e correlacionadas entre múltiplos pontos da rede e (iii) responder a mudanças de padrão de demanda sem reotimizar do zero. Do ponto de vista de Informática e IA, esse cenário apresenta três desafios centrais.

O primeiro é a **representação da rede viária como grafo heterogêneo e dinâmico**. Vias, interseções, faixas e sentidos formam um grafo cuja topologia e cujos atributos (capacidade, tempo de viagem, fluxo) variam no tempo e são afetados pelas próprias decisões de alocação, o que exige arquiteturas de GNN capazes de operar sobre grafos com atributos de aresta mutáveis e de generalizar para subgrafos não vistos no treinamento.

O segundo é a **coordenação multiagente sob não-estacionariedade**. Formular a alocação de faixas e sentidos como decisão de múltiplos agentes (um por interseção, corredor ou zona) introduz não-estacionariedade do ambiente do ponto de vista de cada agente, problemas de atribuição de crédito compartilhado (*credit assignment*) e risco de políticas instáveis quando o tráfego responde de forma não linear e com atraso às mudanças de infraestrutura.

O terceiro é o **custo computacional do laço "ação → simulação → recompensa"**. Avaliar cada ação candidata por meio de simulação microscópica completa é caro demais para ser usado ingenuamente como função de recompensa em milhões de passos de treinamento de RL, o que motiva o uso de uma GNN como modelo substituto que aproxima o impacto de uma intervenção a um custo computacional ordens de grandeza menor, com validação periódica contra a simulação completa.

Assim, os três desafios definem um problema de pesquisa em Informática — representação de grafos, aprendizado multiagente, modelos substitutos e engenharia de pipelines de treinamento e avaliação —, e não um problema de otimização de tráfego *per se*, o que justifica o enquadramento na área de concentração Informática do PG/EEC do ITA.

## 4. Contexto local: São José dos Campos como estudo de caso

São José dos Campos foi escolhida como piloto do sistema ArterIA e serve de estudo de caso real para esta dissertação, fornecendo dados, restrições regulatórias e um ambiente de validação não sintético. A cidade possui instrumentos de planejamento já consolidados que ancoram o trabalho. O **Plano de Mobilidade Urbana (PlanMob/SJC)**, instituído pela Lei Complementar 576/2016, traz diagnóstico e prognóstico de mobilidade; o **Plano Diretor** (Lei 612/2018) define diretrizes de uso do solo e de sistema viário; a **Pesquisa Origem-Destino** do município caracteriza os padrões de deslocamento e de demanda. Somam-se a eles estudos técnicos produzidos com apoio da FGV e o projeto **Linha Verde**, intervenção de corredor de transporte já discutida e implementada na cidade, que serve de referência de intervenção real contra a qual o sistema pode ser comparado. Tais documentos fornecem tanto a malha viária de referência (combinada a dados do OpenStreetMap, OSM) quanto padrões de demanda plausíveis para a calibração da simulação de linha de base, e oferecem, ao mesmo tempo, justificativa de uso real e riscos de generalização, discutidos na seção de limitações.

## 5. Recorte geográfico e escopo

Para manter a dissertação tratável computacionalmente e metodologicamente rigorosa, o escopo experimental será restrito a **um corredor ou subárea de SJC** — candidato preferencial: o corredor associado ao projeto Linha Verde ou uma subárea do centro ou de região com alta densidade de interseções e dados de origem-destino disponíveis —, e não à rede viária completa do município. Essa subárea será modelada no simulador a partir de extração do OSM, por meio das ferramentas de conversão e de edição de rede do próprio SUMO, com ajuste conforme o PlanMob e o Plano Diretor, e servirá como ambiente de treinamento e avaliação dos agentes de RL e da GNN. A escolha de um recorte único e bem delimitado é deliberada, uma vez que permite profundidade metodológica (treinamento, ablações, comparação com linhas de base) em vez de cobertura superficial de toda a cidade.

## 6. Fundamentação em IA

A dissertação apoia-se em três linhas de trabalhos relacionados. A primeira é a de **RL multiagente para alocação de faixas e configuração dinâmica de vias**: o trabalho de alocação coordenada de faixas via aprendizado (*Coordinated Learning-based Lane Allocation*, CLLA, ECML PKDD 2020) trata exatamente o problema de atribuir faixas dinamicamente por meio de agentes que aprendem de forma coordenada, e "Dynamic Graph Configuration with Reinforcement Learning" (arXiv:1910.06788) formula a reconfiguração de um grafo de infraestrutura como problema de RL, ambos diretamente relevantes à formulação central desta dissertação. A segunda é a de **GNNs como representação e modelo substituto de redes de tráfego**, exploradas como forma de aprender a estrutura espacial da rede viária e de prever o impacto de uma intervenção sem recorrer à simulação completa a cada avaliação — direção consistente com o uso de modelos substitutos em problemas de desenho de rede bi-nível, como discutido em frameworks híbridos de aprendizado profundo e metaheurísticas para *bi-level network design problems* (Expert Systems with Applications, 2023). A terceira, **RL aplicado a controle de tráfego em nível de sinalização ou de interseção**, é tratada como trabalho relacionado, mas não central ao escopo: Wei et al. (2016, arXiv:1611.01142) e Tong et al. (2018, IEEE ITSC) aplicam RL ao controle adaptativo de sinais de trânsito, problema correlato, mas distinto — controle de tempo de sinal versus alocação estrutural de faixas e sentidos —, o que ajuda a demarcar precisamente a contribuição pretendida. Complementam a fundamentação trabalhos sobre controle adaptativo de transporte baseado em RL em cenários mais amplos (*A Reinforcement Learning-based Adaptive Control Model for Future Transportation*, arXiv 2021) e sobre reconfiguração de vias para interação segura entre veículos autônomos e pedestres via RL (arXiv 2023), que ilustram a viabilidade e os limites atuais de RL aplicado à configuração física de vias.

## 7. Objetivo geral

Desenvolver e avaliar uma arquitetura de aprendizado por reforço multiagente apoiada em redes neurais em grafos para a alocação dinâmica de faixas e sentidos de vias em redes urbanas, integrada a um ambiente de simulação de tráfego calibrado, usando um corredor de São José dos Campos como estudo de caso real.

## 8. Objetivos específicos

O primeiro objetivo específico é definir uma representação formal da rede viária do recorte de estudo como grafo heterogêneo e dinâmico (nós correspondendo a interseções ou segmentos, arestas a faixas ou sentidos, atributos a capacidade, fluxo e tempo de viagem), adequada tanto ao consumo por agentes de RL quanto por uma GNN. O segundo é projetar e implementar uma arquitetura multiagente de RL para a decisão de alocação de faixas e sentidos, incluindo a definição de espaço de ação, de função de recompensa e de mecanismo de coordenação entre agentes. O terceiro é treinar uma rede neural em grafo como modelo substituto do impacto de uma intervenção no desempenho da rede, a partir de dados gerados por simulações, e avaliar seu uso como função de recompensa de baixo custo durante o treinamento de RL.

O quarto objetivo é construir um pipeline reprodutível de treinamento e avaliação que combine o ambiente de simulação, o surrogate em GNN e os agentes de RL, com versionamento de experimentos e registro de métricas. O quinto, complementar ao anterior, é integrar o simulador como ambiente de treinamento de RL por meio de sua interface de controle em tempo de execução, definindo a interface de observação, ação e recompensa entre os agentes e o simulador.

Por fim, o sexto objetivo é comparar o desempenho da política aprendida contra linhas de base heurísticas (regras fixas, metaheurísticas de busca local e a configuração viária atual de SJC) no mesmo corredor de estudo, e o sétimo é avaliar a generalização da política e do surrogate entre cenários de demanda distintos (horário de pico e fora de pico, dias atípicos) dentro do mesmo recorte geográfico, identificando limites de transferência.

## 9. Metodologia e arquitetura de sistema proposta

A metodologia segue cinco componentes de engenharia, consistentes com a arquitetura já delineada para o ArterIA.

O primeiro é o **pipeline de dados**: extração da malha viária do recorte a partir do OSM, ajuste pelas ferramentas de conversão e de edição de rede do simulador conforme o PlanMob e o Plano Diretor, calibração de demanda sintética a contagens observadas e geração de cenários de tráfego sintéticos complementares para cobrir condições não observadas. A calibração dispensa, por escolha metodológica justificada (atualização de 2026-10-26), o uso de microdados da Pesquisa Origem-Destino, por razões de privacidade e de risco de reidentificação dos respondentes. A construção da rede passa, ademais, por verificação estrutural da qualidade do grafo (componentes conexos, efeito de borda do recorte, semáforos inferidos), documentada no capítulo de arquitetura do sistema.

O segundo é o **ambiente de treinamento**: o simulador, acessado por sua interface de controle em tempo de execução, será encapsulado como ambiente compatível com interfaces padrão de RL (observação, ação, recompensa, reinício de episódio), expondo estados por agente (locais) e o estado global da rede (para avaliação).

O terceiro é a **arquitetura de agentes**: um agente de RL por unidade de decisão (interseção ou subcorredor), com política parametrizada por rede neural, treinado com algoritmo de RL multiagente cooperativo (por exemplo, variantes *actor-critic* com crítico centralizado e atores descentralizados), e uma GNN compartilhada que processa o grafo da rede para fornecer representações de estado e/ou estimar a recompensa substituta.

O quarto é a **infraestrutura de experimentação**: rotinas em Python para orquestração do treinamento, armazenamento de configurações e resultados por experimento e avaliação comparativa entre política aprendida, surrogate e simulação completa.

O quinto, por fim, é a **engenharia de software do sistema de apoio à decisão**: o resultado do treinamento será exposto como um módulo do ArterIA, mantendo a separação entre o código compartilhado (otimização e avaliação) e os dados específicos de cada cidade, com o registro formal das decisões arquiteturais relevantes.

## 10. Métricas de avaliação

A avaliação combinará métricas de desempenho de tráfego e métricas de aprendizado de máquina e de engenharia, sintetizadas na Tabela 1.

| Dimensão | Métricas |
|---|---|
| Tráfego | Tempo total de viagem; atraso médio e por veículo; veículos-hora na rede; confiabilidade de horário de linhas de ônibus; proxies de emissões e de segurança (conforme já previstos na avaliação de linha de base do ArterIA); indicadores de equidade de acesso entre diferentes origens e destinos do recorte |
| Aprendizado de máquina e sistema | Acurácia e erro do modelo substituto (GNN) em relação à simulação completa; tempo e estabilidade de convergência do treinamento multiagente; custo computacional (tempo de parede, uso de GPU/CPU) do ciclo completo de treinamento, comparado ao custo de usar exclusivamente a simulação completa como função de recompensa; taxa de degradação do desempenho do surrogate em cenários de demanda não vistos no treinamento (generalização) |

*Tabela 1 — Métricas de avaliação por dimensão.*

## 11. Resultado esperado / contribuição

Espera-se como resultado um protótipo funcional de módulo de decisão baseado em RL multiagente e GNN, integrado ao simulador e validado em um corredor real de SJC, acompanhado de evidência quantitativa que compare essa abordagem a linhas de base heurísticas e à simulação completa em termos de qualidade de decisão e de custo computacional.

A contribuição pretendida é dupla. Em engenharia de sistemas, consiste em um pipeline reprodutível de treinamento e avaliação que integra simulação de tráfego, RL multiagente e GNN como componentes compostos de um sistema de apoio à decisão, documentado de forma a ser reutilizável para outro corredor ou cidade. Em método de aprendizado, consiste em evidência empírica sobre a viabilidade e os limites de usar GNN como substituto de simulação para acelerar RL aplicado à configuração estrutural de vias — ponto ainda pouco explorado na literatura relacionada, que trata majoritariamente de controle de sinalização, e não de alocação estrutural de faixas e sentidos.

Cabe, contudo, reconhecer um risco real: esta dissertação pode degenerar em "um trabalho sobre algoritmo de RL com aplicação urbana apenas ilustrativa", caso o estudo de caso de SJC seja tratado como pretexto, e não como restrição real. Para evitá-lo, o projeto compromete-se a usar dados e malha viária reais do recorte escolhido, não apenas redes sintéticas de benchmark; a validar a política aprendida contra a configuração viária e contra a intervenção real já existente (Linha Verde), não apenas contra linhas de base artificiais; a relatar explicitamente onde o método falha ou não generaliza no contexto de SJC, e não apenas os casos de sucesso; e a manter a avaliação ancorada nas métricas de mobilidade que o PlanMob e o Plano Diretor de SJC definem como relevantes, não apenas em métricas internas de RL. Dessa forma, a contribuição metodológica permanece subordinada à utilidade do sistema como instrumento de apoio à decisão para o planejamento urbano municipal.

## 12. Limitações e riscos

A primeira limitação diz respeito aos **dados de treinamento limitados**: a Pesquisa OD e os dados de fluxo disponíveis para SJC podem não cobrir toda a variabilidade de demanda necessária para treinar e validar agentes de RL de forma robusta, o que exige a geração de cenários sintéticos, com risco de viés.

A segunda é a **dificuldade de validação em ambiente real**. Por razões evidentes de segurança e de custo, não é possível testar a política aprendida na malha viária real da cidade; toda a validação ocorrerá em simulação, o que limita a confiança externa dos resultados.

A terceira é o **custo computacional**. O treinamento de RL multiagente sobre um ambiente de simulação de tráfego é computacionalmente caro, mesmo com o uso de um surrogate em GNN; o escopo do corredor foi deliberadamente limitado por essa razão, mas pode ainda exigir infraestrutura de computação significativa.

A quarta é o **risco de sobreajuste (*overfitting*) a um único corredor**: os resultados e a política aprendida podem não generalizar para outras partes da malha viária de SJC ou para outras cidades, o que será tratado explicitamente como limitação, e não ocultado como generalização implícita.

A quinta é o **risco de instabilidade do treinamento multiagente**. A não-estacionariedade e a atribuição de crédito compartilhado entre agentes são problemas conhecidos de RL multiagente cooperativo e podem exigir ajustes de formulação ao longo do trabalho.

A sexta, acrescentada em 2026-10-26, refere-se à **qualidade do grafo derivado do OSM**. A primeira rede real do corredor B mostrou que o validador estrutural, ajustado a redes de teste construídas à mão, gerou 729 erros e 7.562 avisos em grande parte espúrios; a rede recortada tem componentes desconexos e bordas artificiais, e os semáforos são inferidos. Tais erros no grafo propagam-se para a observação dos agentes e para o surrogate em GNN, que aprende a rede simulada, e não a cidade. Como mitigação, adotam-se validação estrutural sobre rede real, revisão manual documentada e proveniência completa; o efeito dessas escolhas pode, ademais, ser tratado como fator de ablação.

## 13. O que evitar

Três cautelas delimitam o escopo. Em primeiro lugar, não se propõe uma "IA que cria ruas" ou que gera livremente novos traçados viários: todas as ações permanecem restritas ao catálogo de intervenções viáveis do ArterIA (conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas, entre outras). Em segundo lugar, o jogo Cities: Skylines não é usado como evidência quantitativa de desempenho; seu uso, se houver, fica restrito à comunicação com as partes interessadas, nunca à avaliação científica dos resultados. Por fim, não se promete otimizar a rede viária completa de São José dos Campos de uma só vez, permanecendo o escopo experimental limitado ao corredor ou subárea definido na Seção 5.

## 14. Cronograma tentativo (4 semestres)

| Semestre | Atividades principais |
|---|---|
| 1 | Revisão de literatura (RL multiagente, GNNs, bi-level network design); definição formal da representação do grafo viário; levantamento e tratamento de dados de SJC (PlanMob, Plano Diretor, Pesquisa OD); construção do modelo de simulação do corredor escolhido e calibração inicial. |
| 2 | Implementação do ambiente de treinamento (simulador acoplado por sua interface de controle); definição e implementação da arquitetura multiagente de RL; primeiros experimentos de treinamento em escala reduzida; definição de linhas de base heurísticas. |
| 3 | Desenvolvimento e treinamento do modelo substituto em GNN; integração do surrogate ao laço de treinamento de RL; experimentos completos de treinamento e comparação com as linhas de base e com a simulação completa; estudo de generalização entre cenários de demanda. |
| 4 | Consolidação dos resultados; testes de generalização e análise crítica de limitações; redação da dissertação; preparação da defesa; documentação do protótipo integrado ao ArterIA (registros de decisão arquitetural e histórico de versões). |

## 15. Orientadores em potencial

Busca-se um(a) orientador(a) vinculado(a) ao Programa de Pós-Graduação em Engenharia Eletrônica e Computação (PG/EEC) do ITA, na área de concentração Informática (EEC-I), com interesse em inteligência artificial aplicada e sistemas inteligentes — em particular aprendizado por reforço, redes neurais em grafos, sistemas multiagente ou engenharia de sistemas de apoio à decisão baseados em IA. Nenhum nome específico é indicado neste pré-projeto; a escolha será conduzida junto à coordenação do programa, considerando a aderência de linha de pesquisa e a disponibilidade de orientação.

## 16. Referências

1. CLLA — *Coordinated Learning-based Lane Allocation*. ECML PKDD, 2020.
2. *Dynamic Graph Configuration with Reinforcement Learning*. arXiv:1910.06788.
3. WEI, H. et al. *IntelliLight: A Reinforcement Learning Approach for Intelligent Traffic Light Control* (e trabalhos relacionados de RL para controle de sinais). arXiv:1611.01142, 2016.
4. TONG, Y. et al. *A Reinforcement Learning Approach for Traffic Signal Control*. IEEE International Conference on Intelligent Transportation Systems (ITSC), 2018.
5. *A hybrid deep-learning-metaheuristic framework for bi-level network design problems*. Expert Systems with Applications, 2023.
6. *A Reinforcement Learning-based Adaptive Control Model for Future Transportation*. arXiv, 2021.
7. *Adaptive Road Configurations for Improved Autonomous Vehicle-Pedestrian Interactions using Reinforcement Learning*. arXiv, 2023.
8. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *PlanMob/SJC — Plano de Mobilidade Urbana: Diagnóstico e Prognóstico*. Lei Complementar 576/2016.
9. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Plano Diretor de São José dos Campos*. Lei 612/2018.
10. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Pesquisa Origem-Destino de São José dos Campos*.
