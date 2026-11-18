# Pré-Projeto de Mestrado — ITA, PG/EEC, Área de Concentração Informática

## 1. Título provisório

**Aprendizado por reforço multiagente e redes neurais em grafos para alocação dinâmica de faixas e direções viárias em redes urbanas**

## 2. Resumo

Este pré-projeto propõe investigar métodos de inteligência artificial para a alocação dinâmica de faixas de tráfego e de sentidos de vias em redes urbanas. Esses métodos são o aprendizado por reforço (*Reinforcement Learning*, RL) multiagente e as redes neurais em grafos (*Graph Neural Networks*, GNN). O estudo de caso é a cidade de São José dos Campos (SJC), SP.

O trabalho faz parte do desenvolvimento do sistema ArterIA. O ArterIA é uma ferramenta de apoio à decisão. Ele avalia pacotes de intervenções viárias — conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas — contra uma simulação de tráfego calibrada. Essa simulação usa o simulador microscópico SUMO (*Simulation of Urban MObility*).

Uma abordagem de pesquisa operacional trataria o problema de desenho de rede em si como o centro do trabalho. Esta dissertação não segue esse caminho. O centro desta dissertação é o método de IA e a engenharia do sistema. O trabalho modela a rede viária como grafo. Ele treina agentes de RL que cooperam sobre esse grafo. Ele usa uma GNN como preditor substituto (*surrogate*) do impacto de intervenções — isso reduz a dependência de simulações completas, que são caras em termos computacionais. O trabalho integra esses componentes em um pipeline de treinamento e de avaliação reprodutível. Esse pipeline se conecta ao simulador pela interface de controle em tempo de execução (*Traffic Control Interface*, TraCI).

O recorte geográfico será um corredor ou uma subárea de SJC. Os resultados serão avaliados por dois tipos de métrica: métricas de tráfego (tempo de viagem, atraso, confiabilidade de ônibus) e métricas de aprendizado de máquina (acurácia do surrogate, custo computacional, convergência). O objetivo é contribuir tanto para a engenharia de sistemas inteligentes de apoio à decisão quanto para o método de RL multiagente aplicado a grafos de infraestrutura.

## 3. Problema de pesquisa e justificativa

Esta seção sustenta que a reconfiguração estrutural de redes viárias é um problema de pesquisa em Informática. Ela não é apenas um problema de otimização de tráfego.

O desenho e a reconfiguração de redes viárias urbanas envolvem decidir sentidos de vias, alocação de faixas e prioridades de interseção. Esse problema é tratado, de forma tradicional, como um problema de otimização combinatória de desenho de rede de transporte (*Network Design Problem*, NDP). Ele é resolvido por heurísticas, por metaheurísticas, ou por programação bi-nível clássica.

Essa formulação tradicional tem limitações. A primeira limitação aparece quando se quer representar, de forma explícita, a topologia da rede e suas dependências espaciais. A segunda aparece quando se precisa lidar com decisões distribuídas e correlacionadas entre múltiplos pontos da rede. A terceira aparece quando se precisa responder a mudanças de padrão de demanda sem reotimizar do zero. Do ponto de vista de Informática e de IA, esse cenário traz três desafios centrais.

O primeiro desafio é **representar a rede viária como um grafo heterogêneo e dinâmico**. Vias, interseções, faixas e sentidos formam um grafo. A topologia desse grafo, e seus atributos — capacidade, tempo de viagem, fluxo —, variam no tempo. Eles também são afetados pelas próprias decisões de alocação. Isso exige arquiteturas de GNN capazes de operar sobre grafos com atributos de aresta mutáveis. Essas arquiteturas também precisam generalizar para subgrafos não vistos no treinamento.

O segundo desafio é a **coordenação multiagente sob não-estacionariedade**. Formular a alocação de faixas e sentidos como decisão de múltiplos agentes — um por interseção, por corredor ou por zona — traz três problemas. O primeiro é a não-estacionariedade do ambiente, do ponto de vista de cada agente. O segundo é a atribuição de crédito compartilhado (*credit assignment*) entre os agentes. O terceiro é o risco de políticas instáveis, porque o tráfego responde de forma não linear e com atraso às mudanças de infraestrutura.

O terceiro desafio é o **custo computacional do laço "ação → simulação → recompensa"**. Avaliar cada ação candidata por meio de simulação microscópica completa é caro demais. Esse custo é alto demais para usar essa simulação, de forma ingênua, como função de recompensa em milhões de passos de treinamento de RL. Isso motiva o uso de uma GNN como modelo substituto. Esse modelo aproxima o impacto de uma intervenção, a um custo computacional ordens de grandeza menor. O modelo passa, ainda assim, por validação periódica contra a simulação completa.

Esses três desafios definem, juntos, um problema de pesquisa em Informática: representação de grafos, aprendizado multiagente, modelos substitutos e engenharia de pipelines de treinamento e de avaliação. Eles não definem um problema de otimização de tráfego *per se*. Isso justifica o enquadramento na área de concentração Informática do PG/EEC do ITA.

## 4. Contexto local: São José dos Campos como estudo de caso

São José dos Campos foi escolhida como piloto do sistema ArterIA. Ela serve de estudo de caso real para esta dissertação. Ela fornece dados, restrições regulatórias e um ambiente de validação não sintético.

A cidade tem instrumentos de planejamento já consolidados. Esses instrumentos ancoram o trabalho. O **Plano de Mobilidade Urbana (PlanMob/SJC)** foi instituído pela Lei Complementar 576/2016; ele traz diagnóstico e prognóstico de mobilidade. O **Plano Diretor** (Lei 612/2018) define diretrizes de uso do solo e de sistema viário. A **Pesquisa Origem-Destino** do município caracteriza os padrões de deslocamento e de demanda.

A esses três instrumentos se somam estudos técnicos produzidos com apoio da FGV, e o projeto **Linha Verde** — uma intervenção de corredor de transporte já discutida e implementada na cidade. A Linha Verde serve de referência de intervenção real, contra a qual o sistema pode ser comparado.

Esses documentos fornecem a malha viária de referência, combinada a dados do OpenStreetMap (OSM). Eles fornecem, também, padrões de demanda plausíveis para a calibração da simulação de linha de base. Eles oferecem, ao mesmo tempo, justificativa de uso real e riscos de generalização; esses riscos são discutidos na seção de limitações.

## 5. Recorte geográfico e escopo

O escopo experimental será restrito a **um corredor ou subárea de SJC**. Ele não cobrirá a rede viária completa do município. Essa restrição mantém a dissertação tratável, em termos computacionais e metodológicos.

O candidato preferencial é o corredor associado ao projeto Linha Verde, ou uma subárea do centro, ou de uma região com alta densidade de interseções e com dados de origem-destino disponíveis.

Essa subárea será modelada no simulador a partir de uma extração do OSM. Essa extração usará as ferramentas de conversão e de edição de rede do próprio SUMO. O ajuste seguirá o PlanMob e o Plano Diretor. A subárea servirá como ambiente de treinamento e de avaliação dos agentes de RL e da GNN.

A escolha de um recorte único e bem delimitado é deliberada. Ela permite profundidade metodológica — treinamento, ablações, comparação com linhas de base —, em vez de cobertura superficial de toda a cidade.

## 6. Fundamentação em IA

A dissertação apoia-se em três linhas de trabalhos relacionados.

A primeira linha é **RL multiagente para alocação de faixas e configuração dinâmica de vias**. O trabalho de alocação coordenada de faixas via aprendizado (*Coordinated Learning-based Lane Allocation*, CLLA, ECML PKDD 2020) trata exatamente o problema de atribuir faixas de forma dinâmica. Ele usa agentes que aprendem de forma coordenada. O trabalho "Dynamic Graph Configuration with Reinforcement Learning" (arXiv:1910.06788) formula a reconfiguração de um grafo de infraestrutura como problema de RL. Os dois trabalhos são diretamente relevantes à formulação central desta dissertação.

A segunda linha é a de **GNNs como representação e modelo substituto de redes de tráfego**. Essas redes neurais são exploradas de duas formas: para aprender a estrutura espacial da rede viária, e para prever o impacto de uma intervenção sem recorrer à simulação completa a cada avaliação. Essa direção é consistente com o uso de modelos substitutos em problemas de desenho de rede bi-nível. Um exemplo é o framework híbrido de aprendizado profundo e metaheurísticas para *bi-level network design problems* (Expert Systems with Applications, 2023).

A terceira linha é **RL aplicado a controle de tráfego em nível de sinalização ou de interseção**. Esta linha é tratada como trabalho relacionado, mas não é central ao escopo. Wei et al. (2016, arXiv:1611.01142) e Tong et al. (2018, IEEE ITSC) aplicam RL ao controle adaptativo de sinais de trânsito. Esse problema é correlato, mas é distinto: ele trata de controle de tempo de sinal, não de alocação estrutural de faixas e sentidos. Essa distinção ajuda a demarcar com precisão a contribuição pretendida.

Complementam a fundamentação dois outros trabalhos. Um deles trata de controle adaptativo de transporte baseado em RL, em cenários mais amplos (*A Reinforcement Learning-based Adaptive Control Model for Future Transportation*, arXiv 2021). O outro trata da reconfiguração de vias para interação segura entre veículos autônomos e pedestres, via RL (arXiv 2023). Os dois ilustram a viabilidade e os limites atuais de RL aplicado à configuração física de vias.

## 7. Objetivo geral

Desenvolver e avaliar uma arquitetura de aprendizado por reforço multiagente, apoiada em redes neurais em grafos, para a alocação dinâmica de faixas e sentidos de vias em redes urbanas. Essa arquitetura será integrada a um ambiente de simulação de tráfego calibrado. O estudo de caso real será um corredor de São José dos Campos.

## 8. Objetivos específicos

O primeiro objetivo específico é definir uma representação formal da rede viária do recorte de estudo. Essa representação é um grafo heterogêneo e dinâmico: os nós correspondem a interseções ou a segmentos; as arestas correspondem a faixas ou a sentidos; os atributos correspondem a capacidade, a fluxo e a tempo de viagem. Essa representação precisa ser adequada tanto ao consumo por agentes de RL quanto por uma GNN.

O segundo objetivo é projetar e implementar uma arquitetura multiagente de RL para a decisão de alocação de faixas e sentidos. Isso inclui definir o espaço de ação, a função de recompensa e o mecanismo de coordenação entre agentes.

O terceiro objetivo é treinar uma rede neural em grafo como modelo substituto do impacto de uma intervenção no desempenho da rede. Esse treinamento usa dados gerados por simulações. O objetivo inclui avaliar o uso desse modelo como função de recompensa de baixo custo, durante o treinamento de RL.

O quarto objetivo é construir um pipeline reprodutível de treinamento e de avaliação. Esse pipeline combina o ambiente de simulação, o surrogate em GNN e os agentes de RL. Ele inclui versionamento de experimentos e registro de métricas.

O quinto objetivo é complementar ao quarto: integrar o simulador como ambiente de treinamento de RL, por meio de sua interface de controle em tempo de execução. Isso exige definir a interface de observação, de ação e de recompensa entre os agentes e o simulador.

O sexto objetivo é comparar o desempenho da política aprendida contra linhas de base heurísticas. Essas linhas de base são regras fixas, metaheurísticas de busca local e a configuração viária atual de SJC. A comparação ocorre no mesmo corredor de estudo.

O sétimo objetivo é avaliar a generalização da política e do surrogate entre cenários de demanda distintos — horário de pico e fora de pico, dias atípicos. Essa avaliação ocorre dentro do mesmo recorte geográfico. O objetivo é identificar limites de transferência.

## 9. Metodologia e arquitetura de sistema proposta

A metodologia segue cinco componentes de engenharia. Esses componentes são consistentes com a arquitetura já delineada para o ArterIA.

O primeiro componente é o **pipeline de dados**. Ele extrai a malha viária do recorte a partir do OSM. Ele ajusta essa malha pelas ferramentas de conversão e de edição de rede do simulador, conforme o PlanMob e o Plano Diretor. Ele calibra a demanda sintética a contagens observadas. Ele gera, por fim, cenários de tráfego sintéticos complementares, para cobrir condições não observadas. A calibração não usa microdados da Pesquisa Origem-Destino — essa é uma escolha metodológica justificada (atualização de 2026-10-26), por razões de privacidade e de risco de reidentificação dos respondentes. A construção da rede passa, ademais, por uma verificação estrutural da qualidade do grafo. Essa verificação cobre componentes conexos, efeito de borda do recorte e semáforos inferidos. Ela está documentada no capítulo de arquitetura do sistema.

O segundo componente é o **ambiente de treinamento**. O simulador será acessado por sua interface de controle em tempo de execução. Ele será encapsulado como um ambiente compatível com interfaces padrão de RL — observação, ação, recompensa, reinício de episódio. Esse ambiente expõe estados por agente (locais) e o estado global da rede (para avaliação).

O terceiro componente é a **arquitetura de agentes**. Há um agente de RL por unidade de decisão — uma interseção ou um subcorredor. Cada agente tem uma política parametrizada por rede neural. O treinamento usa um algoritmo de RL multiagente cooperativo — por exemplo, variantes *actor-critic* com crítico centralizado e atores descentralizados. Uma GNN compartilhada processa o grafo da rede. Ela fornece representações de estado e/ou estima a recompensa substituta.

O quarto componente é a **infraestrutura de experimentação**. Ela traz rotinas em Python para a orquestração do treinamento, o armazenamento de configurações e de resultados por experimento, e a avaliação comparativa entre a política aprendida, o surrogate e a simulação completa.

O quinto componente é a **engenharia de software do sistema de apoio à decisão**. O resultado do treinamento será exposto como um módulo do ArterIA. Esse módulo mantém a separação entre o código compartilhado (otimização e avaliação) e os dados específicos de cada cidade. Ele traz, também, o registro formal das decisões arquiteturais relevantes.

## 10. Métricas de avaliação

A avaliação combina dois tipos de métrica: métricas de desempenho de tráfego, e métricas de aprendizado de máquina e de engenharia. A Tabela 1 sintetiza essas métricas.

| Dimensão | Métricas |
|---|---|
| Tráfego | Tempo total de viagem; atraso médio e por veículo; veículos-hora na rede; confiabilidade de horário de linhas de ônibus; proxies de emissões e de segurança (conforme já previstos na avaliação de linha de base do ArterIA); indicadores de equidade de acesso entre diferentes origens e destinos do recorte |
| Aprendizado de máquina e sistema | Acurácia e erro do modelo substituto (GNN) em relação à simulação completa; tempo e estabilidade de convergência do treinamento multiagente; custo computacional (tempo de parede, uso de GPU/CPU) do ciclo completo de treinamento, comparado ao custo de usar exclusivamente a simulação completa como função de recompensa; taxa de degradação do desempenho do surrogate em cenários de demanda não vistos no treinamento (generalização) |

*Tabela 1 — Métricas de avaliação por dimensão.*

## 11. Resultado esperado / contribuição

O resultado esperado é um protótipo funcional de módulo de decisão. Esse módulo usa RL multiagente e GNN. Ele é integrado ao simulador e validado em um corredor real de SJC. Ele vem acompanhado de evidência quantitativa, que compara essa abordagem a linhas de base heurísticas e à simulação completa — em qualidade de decisão e em custo computacional.

A contribuição pretendida é dupla. Em engenharia de sistemas, ela é um pipeline reprodutível de treinamento e de avaliação. Esse pipeline integra simulação de tráfego, RL multiagente e GNN como componentes de um sistema de apoio à decisão. Ele é documentado de forma a ser reutilizável para outro corredor ou cidade. Em método de aprendizado, a contribuição é evidência empírica sobre a viabilidade e os limites de usar GNN como substituto de simulação, para acelerar RL aplicado à configuração estrutural de vias. Esse ponto ainda é pouco explorado na literatura relacionada; essa literatura trata, majoritariamente, de controle de sinalização, não de alocação estrutural de faixas e sentidos.

Cabe, contudo, reconhecer um risco real. Esta dissertação pode degenerar em "um trabalho sobre algoritmo de RL com aplicação urbana apenas ilustrativa", se o estudo de caso de SJC for tratado como pretexto, e não como restrição real. Para evitar esse risco, o projeto assume quatro compromissos. O primeiro é usar dados e malha viária reais do recorte escolhido, não apenas redes sintéticas de benchmark. O segundo é validar a política aprendida contra a configuração viária atual e contra a intervenção real já existente (Linha Verde), não apenas contra linhas de base artificiais. O terceiro é relatar, de forma explícita, onde o método falha ou não generaliza no contexto de SJC — não apenas os casos de sucesso. O quarto é manter a avaliação ancorada nas métricas de mobilidade que o PlanMob e o Plano Diretor de SJC definem como relevantes, não apenas em métricas internas de RL. Dessa forma, a contribuição metodológica permanece subordinada à utilidade do sistema como instrumento de apoio à decisão, para o planejamento urbano municipal.

## 12. Limitações e riscos

A primeira limitação é a dos **dados de treinamento limitados**. A Pesquisa OD e os dados de fluxo disponíveis para SJC podem não cobrir toda a variabilidade de demanda necessária, para treinar e validar agentes de RL de forma robusta. Isso exige a geração de cenários sintéticos, com risco de viés.

A segunda limitação é a **dificuldade de validação em ambiente real**. Por razões evidentes de segurança e de custo, não é possível testar a política aprendida na malha viária real da cidade. Toda a validação ocorrerá em simulação. Isso limita a confiança externa dos resultados.

A terceira limitação é o **custo computacional**. O treinamento de RL multiagente, sobre um ambiente de simulação de tráfego, é caro em termos computacionais — mesmo com o uso de um surrogate em GNN. O escopo do corredor foi, por essa razão, limitado de forma deliberada. Ainda assim, o trabalho pode exigir infraestrutura de computação significativa.

A quarta limitação é o **risco de sobreajuste (*overfitting*) a um único corredor**. Os resultados e a política aprendida podem não generalizar para outras partes da malha viária de SJC, nem para outras cidades. Essa limitação será tratada de forma explícita; ela não será ocultada como generalização implícita.

A quinta limitação é o **risco de instabilidade do treinamento multiagente**. A não-estacionariedade e a atribuição de crédito compartilhado entre agentes são problemas conhecidos de RL multiagente cooperativo. Eles podem exigir ajustes de formulação ao longo do trabalho.

A sexta limitação foi acrescentada em 2026-10-26. Ela se refere à **qualidade do grafo derivado do OSM**. A primeira rede real do corredor B mostrou que o validador estrutural — ajustado a redes de teste construídas à mão — gerou 729 erros e 7.562 avisos, em grande parte espúrios. A rede recortada tem componentes desconexos e bordas artificiais; os semáforos são inferidos. Esses erros no grafo se propagam para a observação dos agentes e para o surrogate em GNN. Esse surrogate aprende a rede simulada, não a cidade real. Como mitigação, adotam-se três medidas: validação estrutural sobre a rede real, revisão manual documentada, e proveniência completa. O efeito dessas escolhas pode, ademais, ser tratado como fator de ablação.

## 13. O que evitar

Três cautelas delimitam o escopo.

Em primeiro lugar, este trabalho não propõe uma "IA que cria ruas", nem uma IA que gera livremente novos traçados viários. Todas as ações permanecem restritas ao catálogo de intervenções viáveis do ArterIA — conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas, entre outras.

Em segundo lugar, o jogo Cities: Skylines não é usado como evidência quantitativa de desempenho. Seu uso, se houver, fica restrito à comunicação com as partes interessadas. Ele nunca serve à avaliação científica dos resultados.

Por fim, este trabalho não promete otimizar a rede viária completa de São José dos Campos de uma só vez. O escopo experimental permanece limitado ao corredor ou à subárea definida na Seção 5.

## 14. Cronograma tentativo (4 semestres)

| Semestre | Atividades principais |
|---|---|
| 1 | Revisão de literatura (RL multiagente, GNNs, bi-level network design); definição formal da representação do grafo viário; levantamento e tratamento de dados de SJC (PlanMob, Plano Diretor, Pesquisa OD); construção do modelo de simulação do corredor escolhido e calibração inicial. |
| 2 | Implementação do ambiente de treinamento (simulador acoplado por sua interface de controle); definição e implementação da arquitetura multiagente de RL; primeiros experimentos de treinamento em escala reduzida; definição de linhas de base heurísticas. |
| 3 | Desenvolvimento e treinamento do modelo substituto em GNN; integração do surrogate ao laço de treinamento de RL; experimentos completos de treinamento e comparação com as linhas de base e com a simulação completa; estudo de generalização entre cenários de demanda. |
| 4 | Consolidação dos resultados; testes de generalização e análise crítica de limitações; redação da dissertação; preparação da defesa; documentação do protótipo integrado ao ArterIA (registros de decisão arquitetural e histórico de versões). |

## 15. Orientadores em potencial

Busca-se um(a) orientador(a) vinculado(a) ao Programa de Pós-Graduação em Engenharia Eletrônica e Computação (PG/EEC) do ITA, na área de concentração Informática (EEC-I). O(a) orientador(a) deve ter interesse em inteligência artificial aplicada e em sistemas inteligentes — em particular, aprendizado por reforço, redes neurais em grafos, sistemas multiagente, ou engenharia de sistemas de apoio à decisão baseados em IA. Este pré-projeto não indica nenhum nome específico. A escolha será conduzida junto à coordenação do programa. Essa escolha vai considerar a aderência de linha de pesquisa e a disponibilidade de orientação.

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
