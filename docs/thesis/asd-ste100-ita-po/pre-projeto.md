# Pré-Projeto de Mestrado — ITA, PG/PO, Área de Pesquisa Operacional (versão em linguagem simples)

> Nota: este documento é uma reescrita em linguagem controlada (ASD-STE100, adaptada ao português) do pré-projeto completo. O texto-fonte está em `docs/thesis/ita-po/pre-projeto.md`. Esta versão não substitui o texto-fonte. Esta versão não remove nenhum fato do texto-fonte. Esta versão só muda a forma do texto, para frases curtas e vocabulário controlado.

## 1. Título provisório

**Otimização bi-nível multiobjetivo de intervenções discretas em redes viárias urbanas com surrogate baseado em aprendizado de máquina: um estudo de caso em corredor arterial de São José dos Campos, SP**

## 2. Resumo

Este pré-projeto defende uma ideia central: o redesenho de uma rede viária urbana deve seguir um método formal de otimização. Uma rede viária urbana tem ruas, cruzamentos e sentidos de tráfego. Um **pacote de intervenções** é um conjunto de mudanças físicas ou operacionais nessa rede. Exemplos de intervenção: conversão de sentido de uma via, faixa reversível, faixa exclusiva de ônibus, realocação de faixa, corredor protegido para pedestres ou bicicletas, restrição de conversão, e poucos conectores novos (ruas novas que ligam dois pontos já existentes).

Este trabalho chama o problema de escolher um pacote de intervenções de **problema de desenho de rede de transporte** (*Network Design Problem*, NDP). O trabalho propõe tratar esse problema com uma estrutura **bi-nível** e **multiobjetivo**.

A estrutura é bi-nível porque tem dois níveis de decisão. No **nível superior**, um planejador escolhe um subconjunto de intervenções. Essa escolha respeita um orçamento e regras técnicas. No **nível inferior**, o tráfego se redistribui pela rede nova. Essa redistribuição segue um modelo de equilíbrio, chamado **atribuição de tráfego**. O cálculo da atribuição de tráfego usa uma simulação microscópica calibrada. A simulação roda no simulador SUMO (*Simulation of Urban MObility*). A estrutura é multiobjetivo porque o nível superior tem vários objetivos ao mesmo tempo, e esses objetivos podem competir entre si.

Avaliar o nível inferior para cada pacote candidato do nível superior tem custo computacional alto. Por isso, este projeto propõe investigar um **surrogate aprendido**: um modelo mais simples e mais rápido, treinado para imitar a resposta da simulação de tráfego. O candidato principal de surrogate é uma rede neural em grafos (*Graph Neural Network*, GNN). Um surrogate rápido permite que métodos de otimização exatos, heurísticos e evolutivos explorem o espaço de soluções de forma viável.

O estudo de caso é um corredor arterial (uma via principal e as vias ao redor dela) delimitado em São José dos Campos (SP). O estudo usa dados do PlanMob municipal, do Plano Diretor, da Pesquisa Origem-Destino e do projeto Linha Verde.

Este trabalho espera produzir um sistema de apoio à decisão, com base em modelagem matemática e em simulação. A contribuição acadêmica central é avaliar uma pergunta: em que medida um surrogate de aprendizado consegue substituir, com precisão suficiente, uma simulação de tráfego cara, dentro de um laço de otimização aplicado a um cenário real?

## 3. Problema de pesquisa e justificativa

Muitas cidades planejam mudanças na malha viária de forma pontual. Isso ocorre sobretudo em cidades médias brasileiras, que têm poucos recursos técnicos e orçamentários. O planejamento pontual usa a experiência de engenheiros de tráfego e usa consultas públicas. O planejamento pontual não usa um processo sistemático de geração e comparação quantitativa de alternativas.

Essa falta de processo sistemático tem uma causa importante. O problema de fundo é um *Network Design Problem* (NDP) discreto, combinatório e bi-nível. "Discreto" significa que cada intervenção é escolhida ou não escolhida; não há meio-termo. "Combinatório" significa que o número de combinações possíveis de intervenções cresce muito rápido. "Bi-nível" segue a definição já dada na Seção 2. A escolha de quais vias converter, onde instalar faixas exclusivas ou corredores protegidos, e quais restrições de conversão impor, interage com o comportamento dos usuários da rede. Os usuários redistribuem suas rotas em resposta a cada mudança, e essa interação não é linear: um pequeno ajuste pode gerar um efeito grande e inesperado.

A literatura de otimização de redes de transporte chama esse fenômeno de **equilíbrio do usuário**, ou **efeito Braess**. No efeito Braess, uma intervenção que parece boa pode, na prática, piorar o desempenho de toda a rede.

A área de Pesquisa Operacional estuda esse problema desde, pelo menos, Miandoabchi et al. (2011). Esse trabalho descreve formalmente o *Urban Network Design Problem* (UNDP, problema de desenho de rede urbana) como um problema bi-nível NP-difícil. "NP-difícil" é um termo técnico: indica que não existe, até hoje, um método conhecido e rápido para resolver o problema de forma exata em todos os casos. Depois desse trabalho, a área avançou em duas direções. Miandoabchi et al. (2013) propõem formulações multiobjetivo. Miandoabchi e Farahani (2010) propõem meta-heurísticas, isto é, métodos de busca aproximados, usados quando o método exato é inviável.

Trabalhos recentes avançam ainda mais. Verbas et al. (2023) propõem formulações bi-objetivo bi-nível. Essas formulações incluem o fechamento e a reversão de faixas em redes de evacuação. Liu et al. (2023) propõem uma arquitetura híbrida: ela combina aprendizado profundo com meta-heurísticas, para reduzir o custo do nível inferior.

O trabalho de Liu et al. (2023) aponta a lacuna de pesquisa deste projeto. A literatura já tem consenso sobre a formulação bi-nível. A literatura também já tem consenso sobre a necessidade de meta-heurísticas no nível superior. Mas a literatura ainda não tem avaliações sistemáticas sobre um ponto específico: em redes reais de porte médio, quando um surrogate aprendido pode substituir a simulação de tráfego dentro do laço de otimização, e com que grau de confiança? Essa pergunta é central por dois motivos. Primeiro, ela decide se ferramentas de apoio à decisão são viáveis na prática. Segundo, ela afeta o rigor metodológico da otimização bi-nível aplicada a sistemas de transporte.

Este projeto também tem uma justificativa prática. Municípios como São José dos Campos precisam de instrumentos de avaliação de cenários de mobilidade. Esses instrumentos devem ser replicáveis: outra pessoa deve conseguir repetir a avaliação e chegar ao mesmo resultado. Esses instrumentos devem ser auditáveis: outra pessoa deve conseguir checar cada passo da avaliação. Esses instrumentos devem produzir evidência quantitativa comparável, antes de qualquer decisão de investimento público. Essa abordagem contrasta com outra abordagem possível: delegar a geração de alternativas a um modelo generativo de inteligência artificial sem restrições de engenharia de tráfego. Este projeto não segue essa outra abordagem.

## 4. Contexto local: São José dos Campos

São José dos Campos (SJC) é um polo industrial e tecnológico do Vale do Paraíba, no estado de São Paulo. SJC serve como piloto empírico (teste com dados reais) do projeto ArterIA. Este mestrado é o núcleo de modelagem matemática do projeto ArterIA. O município tem instrumentos de planejamento. Esses instrumentos dão o diagnóstico de mobilidade da cidade e dão o conjunto de regras sobre quais intervenções são permitidas.

O primeiro instrumento é o **Plano de Mobilidade Urbana de São José dos Campos** (PlanMob-SJC). A Lei Complementar nº 576/2016 instituiu o PlanMob-SJC. O PlanMob-SJC define três coisas: a hierarquia das vias; a prioridade do transporte coletivo e dos modos ativos (pedestres e ciclistas); e metas de desempenho da rede.

O segundo instrumento é o **Plano Diretor de Desenvolvimento Integrado**. A Lei Complementar nº 612/2018 instituiu o Plano Diretor. O Plano Diretor define o zoneamento da cidade, os eixos de adensamento (áreas onde mais construção é permitida), e os parâmetros urbanísticos. Esses parâmetros condicionam se uma alteração viária é juridicamente viável.

Do lado da demanda de viagens, a **Pesquisa Origem-Destino** (OD) de São José dos Campos dá as matrizes de demanda por zona de tráfego. Essas matrizes são necessárias para calibrar o modelo de atribuição de tráfego do nível inferior. Além disso, a **Fundação Getulio Vargas** (FGV) apoiou estudos técnicos de mobilidade em SJC. Esses estudos ajudam a caracterizar a situação socioeconômica da população, e ajudam a definir os parâmetros de valoração do tempo de viagem. Por fim, o projeto **Linha Verde** é uma intervenção de mobilidade e de requalificação urbana, já implantada ou em implantação no município. O projeto Linha Verde oferece duas coisas a este trabalho: um precedente de intervenção de corredor, e uma possível referência para validação parcial. Essa validação parcial compararia a situação antes e depois ("*before/after*") usando dados observados.

Juntos, esses instrumentos dão duas coisas a este trabalho: a base de dados para calibrar o modelo de rede, e o conjunto de restrições de viabilidade jurídica e urbanística que o nível superior do problema de otimização deve respeitar.

## 5. Recorte geográfico e escopo

Este estudo limita seu recorte por dois motivos. O primeiro motivo é a tratabilidade computacional: o estudo precisa ser viável de executar com os recursos de computação disponíveis. O segundo motivo é o rigor na calibração. Por esses dois motivos, o estudo não vai cobrir a rede viária completa do município.

O recorte será um corredor arterial único, ou uma subárea compacta de SJC. O candidato preferencial é um trecho do eixo ligado ao projeto Linha Verde. Outra opção é um corredor arterial diferente, com conflitos documentados entre tráfego geral, transporte coletivo e modos ativos. A escolha final depende da orientação do(a) orientador(a), e da disponibilidade de dados da Pesquisa OD por zona.

O recorte incluirá a via arterial principal, e suas vias paralelas e transversais de impacto direto. Esse raio tem, em geral, de algumas centenas de metros a poucos quilômetros. O recorte vai delimitar uma rede de algumas dezenas a poucas centenas de arcos (trechos de via, no vocabulário de rede). Essa escala tem duas vantagens: é compatível com a calibração de um modelo SUMO confiável; e permite gerar, em tempo viável de simulação, dados de treinamento do surrogate em quantidade suficiente. Este mestrado não tem, como objetivo, generalizar o método para a rede completa do município. Essa generalização fica como trabalho futuro.

## 6. Formulação formal do problema

A rede viária do corredor de estudo tem um nome matemático: $G = (N, A)$. $N$ é o conjunto de nós (cruzamentos). $A$ é o conjunto de arcos (trechos de via).

O vetor $y$ representa a decisão do nível superior. A notação é $y \in \{0,1\}^{|\mathcal{I}|}$. Cada componente $y_i$ vale 1 se a intervenção $i$ for escolhida, e vale 0 se não for escolhida. A intervenção $i$ pertence a um catálogo finito e restrito, chamado $\mathcal{I}$. O catálogo $\mathcal{I}$ tem estes tipos de intervenção: conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas, corredores protegidos para bicicleta/pedestre, restrições de conversão, novos conectores, retemporização semafórica e prioridade semafórica para transporte público. Cada vetor $y$ gera uma rede modificada, chamada $G(y)$.

O nível inferior recebe dois insumos: a rede modificada $G(y)$, e uma matriz de demanda origem-destino $Q$. A matriz $Q$ diz quantas viagens cada zona faz para cada outra zona. No nível inferior, o fluxo de equilíbrio $x^*(y)$ resolve o problema de atribuição de tráfego. O nome técnico desse problema é **equilíbrio do usuário de Wardrop**. Este trabalho usa, na prática, uma aproximação estocástica ou dinâmica desse equilíbrio, obtida por simulação microscópica. A fórmula do problema é:

$$x^*(y) = \arg\min_{x \in \Omega(G(y), Q)} \; \Phi(x, G(y))$$

Nessa fórmula, $\Omega$ é o conjunto de fluxos viáveis. Um fluxo é viável quando respeita a conservação de fluxo (tudo que entra num nó sai dele) e a capacidade de cada arco. $\Phi$ é o potencial de Beckmann, que usa as funções de custo de cada arco, chamadas $c_a(x_a)$.

Na prática computacional deste trabalho, $x^*(y)$ não vem de uma fórmula matemática fechada. Em vez disso, $x^*(y)$ vem de uma estimativa. Essa estimativa usa a simulação microscópica calibrada no SUMO. A interface TraCI (*Traffic Control Interface*) controla essa simulação durante a execução. Para a busca no nível superior, este trabalho aproxima $x^*(y)$ por um surrogate, chamado $\hat{x}(y)$. A notação $\hat{x}(y) \approx x^*(y)$ significa que o surrogate se aproxima do valor real, sem ser igual a ele. O surrogate é treinado sobre pares de dados: cada par tem uma intervenção e a resposta de tráfego correspondente, gerada pela simulação.

O nível superior é um problema multiobjetivo. Um problema multiobjetivo tem mais de um objetivo ao mesmo tempo, e esses objetivos podem competir entre si. A fórmula do nível superior é:

$$\min_{y \in \{0,1\}^{|\mathcal{I}|}} \; F(y) = \big(f_1(y), f_2(y), \dots, f_k(y)\big)$$

Cada $f_k(y)$ é um objetivo diferente. A tabela a seguir resume os objetivos típicos.

| Componente | Descrição |
|---|---|
| $f_1$ | tempo total de viagem / tempo médio de viagem na rede, dado $x^*(y)$ |
| $f_2$ | atraso agregado nas interseções críticas |
| $f_3$ | emissões estimadas (proxy baseado em velocidade/parada, ex. modelo HBEFA do SUMO) |
| $f_4$ | custo de implantação do pacote de intervenções |
| $f_5$ | perda (ou ganho) de acessibilidade por zona |
| $f_6$ | confiabilidade do transporte público (variância do tempo de viagem das linhas de ônibus afetadas) |
| $f_7$ | indicador de equidade (dispersão dos impactos entre bairros/zonas censitárias) |

O problema tem cinco tipos de restrição.

1. **Restrição orçamentária**: $\sum_i c_i \, y_i \le B$. A soma do custo $c_i$ de cada intervenção escolhida não pode passar do orçamento $B$.
2. **Capacidade mínima residual**: arcos críticos, como acessos hospitalares e corredores de emergência, devem manter uma capacidade mínima depois da intervenção.
3. **Continuidade da rede cicloviária e de pedestres**: o subgrafo formado pelas intervenções de modo ativo selecionadas deve manter conectividade topológica. "Conectividade topológica" significa que é possível ir de um ponto a outro desse subgrafo sem interrupção.
4. **Viabilidade jurídico-urbanística**: toda intervenção $i$ incompatível com o zoneamento do Plano Diretor (Lei Complementar nº 612/2018) tem $y_i = 0$ obrigatoriamente, ou seja, não pode ser escolhida. A mesma regra vale para intervenções incompatíveis com as diretrizes do PlanMob (Lei Complementar nº 576/2016).
5. **Compatibilidade topológica**: duas intervenções mutuamente exclusivas não podem ser escolhidas juntas. Por exemplo, uma via não pode ser convertida em mão única em dois sentidos opostos ao mesmo tempo.

A solução do problema é uma **fronteira de Pareto**: o conjunto de pacotes de intervenção $\{y^*\}$ não dominados. Um pacote é "não dominado" quando nenhum outro pacote é melhor que ele em todos os objetivos ao mesmo tempo. Este trabalho extrai, dessa fronteira, recomendações para a análise "antes e depois" (*before/after*).

## 7. Objetivo geral

O objetivo geral deste trabalho tem quatro partes. Primeira parte: formular o problema de seleção de um pacote de intervenções viárias discretas para um corredor arterial de São José dos Campos. Segunda parte: resolver esse problema, com método de otimização bi-nível multiobjetivo apoiado por um surrogate de aprendizado de máquina. Terceira parte: produzir, como resultado, um sistema de apoio à decisão reprodutível — outra pessoa deve conseguir repetir o processo e chegar a resultados equivalentes. Quarta parte: fundamentar esse sistema em evidência quantitativa de simulação calibrada.

## 8. Objetivos específicos

O objetivo geral se divide em sete objetivos específicos. Esses sete objetivos seguem uma ordem: da construção do modelo até a recomendação final.

1. Construir e calibrar um modelo de rede do corredor de estudo no SUMO. Esse modelo usa dados do OpenStreetMap, convertidos e ajustados pelas ferramentas de construção de rede do próprio SUMO. O modelo deve ser validado contra contagens de tráfego e contra a Pesquisa Origem-Destino de SJC.
2. Definir formalmente o catálogo restrito de intervenções viáveis $\mathcal{I}$, com seus parâmetros, seus custos de implantação, e as restrições de viabilidade jurídico-urbanística derivadas do PlanMob e do Plano Diretor.
3. Formular matematicamente o problema de desenho de rede como um programa bi-nível multiobjetivo. Essa formulação especifica as funções objetivo, as restrições, e a relação entre as variáveis de decisão do nível superior e o equilíbrio de tráfego do nível inferior.
4. Projetar e treinar um surrogate de aprendizado de máquina (candidato principal: GNN), capaz de aproximar a resposta de tráfego das simulações a partir da topologia da rede e do vetor de intervenções. Este objetivo também avalia a precisão do surrogate e os limites de generalização do surrogate.
5. Comparar o desempenho (qualidade de solução, custo computacional, escalabilidade) de, no mínimo, três classes de métodos de otimização do nível superior: um método exato ou de relaxação, para instâncias reduzidas; uma meta-heurística evolutiva, como o NSGA-II; e um método de otimização Bayesiana. A comparação roda tanto sobre o simulador direto quanto sobre o surrogate.
6. Conduzir uma avaliação "antes e depois" (*before/after*), comparando o cenário-base calibrado com os pacotes de intervenção recomendados pela fronteira de Pareto obtida, segundo as métricas da Seção 10 deste documento.
7. Propor e documentar um pacote de intervenções priorizado para o corredor de estudo, acompanhado da análise de sensibilidade e das limitações da recomendação.

## 9. Metodologia e métodos propostos

O **SUMO** é o simulador de tráfego de referência deste trabalho. O SUMO tem duas funções: gerar o cenário-base calibrado; e servir de oráculo de avaliação (também chamado "*ground truth*", o valor de referência real) para treinar e validar o surrogate. Quando necessário, a interface **TraCI** controla a simulação durante a execução — por exemplo, para faixas reversíveis que dependem do horário. A rede do corredor vem de extratos do OpenStreetMap. O conversor de redes do SUMO, chamado **netconvert**, processa esses extratos. O editor gráfico do SUMO, chamado **netedit**, permite ajustes manuais, para a rede refletir a geometria real do corredor.

A formulação bi-nível deste trabalho segue a linha metodológica de Miandoabchi et al. (2011, 2013) e de Miandoabchi e Farahani (2010) para o *Urban Network Design Problem*. Este trabalho adapta o catálogo de intervenções dessa linha metodológica ao contexto de SJC. Para o nível superior, este trabalho compara três caminhos:

1. Uma formulação exata, ou uma relaxação linear/inteira, para uma versão simplificada da rede. Esse caminho serve de referência de qualidade de solução em instâncias pequenas.
2. Algoritmos genéticos multiobjetivo, como o NSGA-II ou variantes dele. Esse caminho segue a tradição de meta-heurísticas para o UNDP.
3. Otimização Bayesiana multiobjetivo. Esse caminho é adequado quando cada avaliação da função objetivo tem custo alto.

O componente de aprendizado de máquina segue a linha de trabalhos recentes que usam redes neurais em grafos como surrogate de modelos de atribuição de tráfego e de problemas de desenho de rede bi-nível (Liu et al., 2023). Esse surrogate explora a estrutura topológica da rede viária: os nós são interseções; as arestas são arcos; os atributos de cada aresta incluem a capacidade e a intervenção aplicada. O surrogate usa essa estrutura para prever métricas agregadas de desempenho de tráfego, sem executar uma simulação completa a cada avaliação do nível superior. A estratégia de treinamento combina duas técnicas: a **amostragem ativa**, que prioriza regiões do espaço de intervenções com maior incerteza do surrogate; e um orçamento fixo de simulações completas. Essa combinação torna explícito um compromisso (*trade-off*) entre custo computacional e fidelidade da aproximação — o próprio objeto de investigação deste projeto.

## 10. Métricas de avaliação before/after

A comparação entre o cenário-base e os pacotes de intervenção recomendados usa, no mínimo, as métricas da tabela a seguir.

| Dimensão | Métrica |
|---|---|
| Fluidez | tempo total de viagem na rede (veículo-hora e pessoa-hora) |
| Fluidez | atraso médio e atraso agregado nas interseções do corredor |
| Fluidez | veículos-hora de espera (filas) |
| Transporte público | confiabilidade (variância e percentil 95 do tempo de viagem das linhas de ônibus que cruzam o corredor) |
| Modos ativos | exposição de pedestres e ciclistas (tempo de exposição a tráfego motorizado, continuidade de rotas protegidas) |
| Ambiente | emissões estimadas (CO₂, poluentes locais, via modelo de emissões do SUMO) |
| Segurança | proxy de risco de acidentes (conflitos de conversão, velocidade em pontos críticos) |
| Segurança | manutenção do acesso de emergência (tempo de percurso estimado para rotas hospitalares) |
| Equidade | equidade de impacto entre bairros/zonas da Pesquisa OD (dispersão dos ganhos/perdas de acessibilidade) |
| Economia | relação custo-benefício do pacote (custo de implantação por unidade de melhoria agregada) |

## 11. Resultado esperado / contribuição

O resultado esperado não é um algoritmo isolado. O resultado esperado é um **sistema de apoio à decisão**: um pipeline computacional integrado, com seis partes — um modelo de rede calibrado; um catálogo de intervenções; um gerador e avaliador de cenários; um surrogate treinado; um otimizador multiobjetivo; e um módulo de análise "antes e depois". Esse pipeline produz, para o corredor de estudo, uma fronteira de pacotes de intervenção não dominados, documentada e auditável.

A contribuição acadêmica específica em Pesquisa Operacional tem duas partes. Primeira parte: este trabalho propõe uma formulação bi-nível multiobjetivo do *Urban Network Design Problem*, adaptada às restrições de viabilidade jurídico-urbanística de um caso real brasileiro. A literatura internacional pouco explora esse tipo de caso; ela aplica, na maioria das vezes, o UNDP a redes sintéticas ou a redes norte-americanas e europeias. Segunda parte: este trabalho faz uma avaliação empírica, sobre essa rede real, de quando, e com que grau de confiança, um surrogate aprendido aproxima resultados caros de simulação de tráfego. A avaliação também pergunta se essa aproximação é suficiente para substituir o simulador dentro do laço de otimização. Se for suficiente, métodos exatos e heurísticos podem explorar o espaço de intervenções com custo computacional viável, em um cenário de porte prático.

Por isso, a contribuição deste trabalho vai além do corredor estudado. Este trabalho mostra as condições em que a otimização apoiada por surrogate produz evidência confiável. Com isso, este trabalho oferece a municípios de porte médio um caminho replicável e auditável, para fundamentar decisões de investimento em mobilidade antes da implantação dessas decisões.

## 12. Limitações e riscos

A primeira limitação é **dados incompletos ou desatualizados**. A Pesquisa OD de SJC, e as contagens de tráfego de SJC, podem não cobrir todo o corredor escolhido, ou podem estar desatualizadas. Se isso ocorrer, este trabalho vai precisar de contagens próprias, ou de estimativas indiretas, para completar os dados.

A segunda limitação é o **custo computacional da simulação**. Treinar e validar o surrogate exige um volume grande de simulações. Gerar esse volume pode ser limitado pelo tempo de execução disponível durante o mestrado. Esse limite de tempo condiciona o tamanho do corredor de estudo, e o tamanho do catálogo de intervenções.

A terceira limitação é o risco de **sobreajuste do surrogate** (*overfitting*). O surrogate é treinado sobre um conjunto limitado de configurações de rede. Por isso, o surrogate pode generalizar mal para combinações de intervenções que ele nunca viu durante o treino. Esse risco exige validação cruzada cuidadosa, e quantificação explícita de incerteza.

A quarta limitação vem do ponto de vista institucional: a **viabilidade jurídica e política das intervenções**. As restrições formais do Plano Diretor e do PlanMob podem não capturar todas as barreiras políticas ou sociais à implantação real. Por isso, a recomendação final deste trabalho deve ser lida como evidência técnica, não como decisão administrativa.

A quinta limitação é o **erro de especificação do modelo de equilíbrio**. O simulador aproxima o comportamento dos usuários da rede — as rotas escolhidas e a elasticidade da demanda. Essa aproximação é, em si, uma simplificação da realidade. Os parâmetros de calibração dessa aproximação introduzem incerteza adicional, que se propaga por todo o pipeline.

Em 2026-10-26, este documento recebeu uma sexta limitação: a **incerteza estrutural da rede viária**. A rede $G$ vem do OpenStreetMap, processada pelo conversor de redes do SUMO. Essa rede $G$ pode conter três tipos de imperfeição: omissões; atributos inferidos, inclusive semáforos, quando a inferência automática os gera; e efeitos de borda do recorte espacial sobre a conectividade e a acessibilidade. Essas imperfeições alimentam o nível inferior como erro estrutural. Esse erro estrutural existe antes da calibração de demanda, e é distinto dela. Este trabalho prevê três medidas de mitigação: validar a rede real, não só redes de teste; fazer uma revisão manual documentada no editor de redes; e registrar a proveniência de cada construção da rede (versão do simulador, parâmetros de conversão, e identificação do extrato de dados usado). O Capítulo 3 discute esse assunto com mais detalhe.

## 13. O que evitar

Este trabalho tem três cautelas. Essas cautelas definem o que este trabalho não deve propor.

Primeira cautela: este trabalho não deve usar um modelo de inteligência artificial generativa que "invente" ruas ou geometrias de rede livremente. Toda intervenção precisa pertencer ao catálogo restrito e tecnicamente viável, definido na Seção 6.

Segunda cautela: o jogo Cities: Skylines não deve servir como evidência quantitativa de desempenho de tráfego. Este trabalho pode usar o jogo Cities: Skylines só para comunicação com as partes interessadas (*stakeholders*). Este trabalho nunca deve usar o jogo Cities: Skylines para avaliação ou para validação do modelo.

Terceira cautela: este projeto não deve começar por uma formulação de aprendizado por reforço (RL, *Reinforcement Learning*). Antes de considerar o RL, este projeto precisa estabelecer, com rigor, a formulação de otimização bi-nível multiobjetivo e suas restrições. Se este projeto vier a considerar o RL, o RL será apenas uma possível técnica de solução do nível superior, subordinada à formulação matemática. O RL não será o ponto de partida do projeto.

## 14. Cronograma tentativo (4 semestres)

| Semestre | Atividades principais |
|---|---|
| 1º | Revisão sistemática da literatura de UNDP bi-nível e surrogates de ML para atribuição de tráfego; definição do recorte geográfico; levantamento de dados (OSM, Pesquisa OD, PlanMob, Plano Diretor); construção inicial do modelo de rede em SUMO. |
| 2º | Calibração do modelo de rede; definição formal do catálogo de intervenções e das restrições de viabilidade; formulação matemática completa do problema bi-nível multiobjetivo; geração do primeiro lote de simulações para treinamento do surrogate. |
| 3º | Treinamento e validação do surrogate (GNN); implementação e comparação dos métodos de otimização do nível superior (exato/relaxado, evolutivo, Bayesiano); análise de sensibilidade. |
| 4º | Avaliação before/after dos pacotes recomendados; consolidação do pipeline como sistema de apoio à decisão; redação e defesa da dissertação; submissão de artigo(s) derivado(s). |

## 15. Orientadores em potencial

Este trabalho busca um(a) orientador(a) vinculado(a) ao programa de PG/PO do ITA. Esse(a) orientador(a) deve ter interesse em pelo menos um destes temas: otimização bi-nível/multiobjetivo; modelagem matemática de problemas de decisão combinatória; ou meta-heurísticas aplicadas a problemas de engenharia.

Este trabalho também deseja um(a) colaborador(a) complementar, com experiência em transporte, em simulação de tráfego, ou em planejamento urbano. Esse(a) colaborador(a) pode participar como coorientador(a) formal, ou como colaborador(a) técnico(a). Essa participação assegura o rigor da formulação de otimização e o rigor da calibração do modelo de simulação.

Este pré-projeto não indica nenhum nome específico. A coordenação do programa vai conduzir, junto com este trabalho, a identificação do(a) orientador(a) e do(a) eventual colaborador(a).

## 16. Referências

1. MIANDOABCHI, E.; DAZIANO, R. A.; ZANJIRANI FARAHANI, R.; SZETO, W. Y. Bi-level optimization for the urban road network design problem. *Networks and Spatial Economics*, v. 11, 2011.
2. MIANDOABCHI, E.; DAZIANO, R. A.; ZANJIRANI FARAHANI, R.; SZETO, W. Y. Multi-objective discrete urban road network design. *Computers & Operations Research*, v. 40, n. 10, 2013, p. 2429–2449.
3. MIANDOABCHI, E.; FARAHANI, R. Z. A meta-heuristic approach for solving the Urban Network Design Problem. *International Journal of Industrial Engineering Computations* / aplicação em transporte urbano, 2010.
4. VERBAS, Ö. et al. Bi-objective bi-level optimization for integrating lane-level closure and reversal in evacuation network design. *Operational Research*, 2023.
5. LIU, H. et al. A hybrid deep-learning-metaheuristic framework for bi-level network design problems. *Expert Systems with Applications*, v. 230, 2023.
6. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Plano de Mobilidade Urbana de São José dos Campos (PlanMob-SJC) — Diagnóstico e Prognóstico*. Lei Complementar nº 576/2016.
7. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Plano Diretor de Desenvolvimento Integrado de São José dos Campos*. Lei Complementar nº 612/2018.
8. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Pesquisa Origem-Destino de São José dos Campos* — matrizes de demanda por zona de tráfego.
9. FUNDAÇÃO GETULIO VARGAS (FGV). Estudos técnicos de mobilidade urbana aplicados a São José dos Campos.
10. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Projeto Linha Verde* — documentação técnica de intervenção de corredor.
11. SUMO — Simulation of Urban MObility. Documentação oficial de netconvert, netedit e TraCI. Eclipse Foundation / DLR.
