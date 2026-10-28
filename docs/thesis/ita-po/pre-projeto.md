# Pré-projeto de Mestrado Acadêmico — ITA, Programa de Pós-Graduação em Engenharia Aeronáutica e Mecânica, Área de Pesquisa Operacional (PG/PO)

## 1. Título provisório

**Otimização bi-nível multiobjetivo de intervenções discretas em redes viárias urbanas com surrogate baseado em aprendizado de máquina: um estudo de caso em corredor arterial de São José dos Campos, SP**

## 2. Resumo

Este pré-projeto defende que o redesenho de uma rede viária urbana — a escolha de um pacote de intervenções físicas e operacionais, como conversões de sentido, faixas reversíveis, faixas exclusivas de ônibus, realocação de faixas, corredores protegidos para modos ativos, restrições de conversão e poucos conectores novos — deve ser formulado como um problema de **desenho de rede de transporte (Network Design Problem, NDP)** com estrutura **bi-nível e multiobjetivo**. No nível superior, um planejador seleciona um subconjunto discreto de intervenções sujeito a restrições orçamentárias e técnicas; no nível inferior, o tráfego se redistribui segundo um modelo de equilíbrio (atribuição de tráfego), calculado por simulação microscópica calibrada no simulador SUMO (Simulation of Urban MObility).

Como a avaliação exaustiva do nível inferior para cada candidato do nível superior é computacionalmente onerosa, propõe-se investigar um **surrogate aprendido** — por exemplo, uma rede neural em grafos (Graph Neural Network, GNN) — que aproxime a resposta de tráfego com custo computacional muito menor, permitindo que métodos de otimização exatos, heurísticos e evolutivos explorem o espaço de soluções de forma tratável. O estudo de caso será um corredor arterial delimitado de São José dos Campos (SP), apoiado em dados do PlanMob municipal, do Plano Diretor, da Pesquisa Origem-Destino e do projeto Linha Verde.

Espera-se, assim, obter um sistema de apoio à decisão fundamentado em modelagem matemática e simulação, cuja contribuição acadêmica central é avaliar em que medida um surrogate de aprendizado consegue substituir, com precisão suficiente, uma simulação de tráfego cara dentro de um laço de otimização aplicado a um cenário real.

## 3. Problema de pesquisa e justificativa

O planejamento de intervenções em malhas viárias urbanas — sobretudo em cidades médias brasileiras com recursos técnicos e orçamentários limitados — tende a ser conduzido de forma pontual, baseada em experiência de engenharia de tráfego e em consultas públicas, sem um processo sistemático de geração e comparação quantitativa de alternativas. Tal fato decorre, em grande parte, de o problema subjacente ser um **Network Design Problem discreto, combinatório e bi-nível**: a escolha de que vias converter, onde instalar faixas exclusivas ou corredores protegidos e quais restrições de conversão impor interage não linearmente com o comportamento dos usuários da rede, que redistribuem suas rotas em resposta a cada mudança. Esse fenômeno é conhecido na literatura de otimização de redes de transporte como *equilíbrio do usuário* ou *efeito Braess*, em que uma intervenção aparentemente benéfica pode degradar o desempenho global do sistema.

A literatura de Pesquisa Operacional trata esse problema desde ao menos Miandoabchi et al. (2011), que caracterizam formalmente o Urban Network Design Problem (UNDP) como uma classe de problemas bi-nível NP-difíceis; a linha desenvolve-se, em seguida, com formulações multiobjetivo (Miandoabchi et al., 2013) e meta-heurísticas (Miandoabchi e Farahani, 2010). Trabalhos mais recentes avançam para formulações bi-objetivo bi-nível que integram fechamento e reversão de faixas (Verbas et al., 2023) e para arquiteturas híbridas que combinam aprendizado profundo com meta-heurísticas para reduzir o custo do nível inferior (Liu et al., 2023).

Esse último ponto delimita a lacuna de pesquisa que este projeto pretende explorar. Embora haja consenso sobre a formulação bi-nível e sobre a necessidade de meta-heurísticas no nível superior, a literatura ainda carece de avaliações sistemáticas, em redes reais de porte médio, de **quando e com que grau de confiança um surrogate aprendido pode substituir a simulação de tráfego** dentro do laço de otimização. Tal questão é central tanto para a viabilidade prática de ferramentas de apoio à decisão quanto para o rigor metodológico da otimização bi-nível aplicada a sistemas de transporte.

A justificativa prática do projeto, por sua vez, decorre da necessidade, em municípios como São José dos Campos, de instrumentos replicáveis e auditáveis de avaliação de cenários de mobilidade, que produzam evidência quantitativa comparável antes de decisões de investimento público, em contraste com abordagens que delegam a geração de alternativas a um modelo generativo sem restrições de engenharia de tráfego.

## 4. Contexto local: São José dos Campos

São José dos Campos (SJC), polo industrial e tecnológico do Vale do Paraíba (SP), serve como piloto empírico do projeto ArterIA, do qual este mestrado constitui o núcleo de modelagem matemática. O município dispõe de instrumentos de planejamento que fornecem tanto o diagnóstico de mobilidade quanto o arcabouço normativo das intervenções admissíveis.

O primeiro desses instrumentos é o **Plano de Mobilidade Urbana de São José dos Campos (PlanMob-SJC)**, instituído pela Lei Complementar nº 576/2016, que estabelece diretrizes de hierarquização viária, priorização do transporte coletivo e dos modos ativos, e metas de desempenho da rede. De modo complementar, o **Plano Diretor de Desenvolvimento Integrado**, Lei Complementar nº 612/2018, define o zoneamento, os eixos de adensamento e os parâmetros urbanísticos que condicionam a viabilidade jurídica de alterações viárias.

Do lado da demanda, a **Pesquisa Origem-Destino (OD) de São José dos Campos** fornece as matrizes de demanda por zona de tráfego necessárias para calibrar o modelo de atribuição de tráfego do nível inferior. Ademais, estudos técnicos de mobilidade conduzidos com apoio da **Fundação Getulio Vargas (FGV)** são relevantes para a caracterização socioeconômica e para os parâmetros de valoração do tempo de viagem. Por fim, o projeto **Linha Verde**, intervenção de mobilidade e requalificação urbana já implantada ou em implantação no município, oferece tanto um precedente de intervenção de corredor quanto uma possível referência de validação parcial, por meio de comparação before/after com dados observados.

Esses instrumentos fornecem, simultaneamente, a base de dados para a calibração do modelo de rede e o conjunto de restrições de viabilidade jurídico-urbanística que o nível superior do problema de otimização deve respeitar.

## 5. Recorte geográfico e escopo

Por razões de tratabilidade computacional e de rigor na calibração, o estudo **não abrangerá a rede viária completa do município**. O recorte será um **corredor arterial único ou uma subárea compacta de SJC**, tendo como candidato preferencial um trecho do eixo associado ao projeto Linha Verde ou outro corredor arterial com conflitos documentados entre tráfego geral, transporte coletivo e modos ativos, a ser confirmado em conjunto com a orientação e com a disponibilidade de dados da Pesquisa OD por zona.

O recorte incluirá a via arterial principal e suas vias paralelas e transversais de impacto direto (tipicamente num raio de algumas centenas de metros a poucos quilômetros), delimitando uma rede de algumas dezenas a poucas centenas de arcos. Tal escala é compatível com a calibração de um modelo SUMO confiável e com o tempo de simulação necessário para gerar dados de treinamento do surrogate em quantidade suficiente. A generalização para a rede completa do município é tratada como trabalho futuro, não como objetivo deste mestrado.

## 6. Formulação formal do problema

Seja $G = (N, A)$ a rede viária do corredor de estudo, com nós $N$ e arcos $A$. Seja $y \in \{0,1\}^{|\mathcal{I}|}$ o vetor de decisão do **nível superior**, em que cada componente $y_i$ indica a seleção de uma intervenção $i$ pertencente a um catálogo finito e restrito $\mathcal{I}$ (conversões de mão única, faixas reversíveis, faixas de ônibus, realocação de faixas, corredores protegidos para bicicleta/pedestre, restrições de conversão, novos conectores, retemporização semafórica e prioridade semafórica para transporte público). A cada vetor $y$ corresponde uma rede modificada $G(y)$.

No **nível inferior**, dados $G(y)$ e uma matriz de demanda OD $Q$, o fluxo de equilíbrio $x^*(y)$ resolve o problema de atribuição de tráfego (equilíbrio do usuário de Wardrop, ou sua aproximação estocástica/dinâmica obtida por simulação microscópica):

$$x^*(y) = \arg\min_{x \in \Omega(G(y), Q)} \; \Phi(x, G(y))$$

em que $\Omega$ representa o conjunto de fluxos viáveis (conservação de fluxo, capacidade de arco) e $\Phi$ o potencial de Beckmann associado às funções de custo de arco $c_a(x_a)$. Na prática computacional, contudo, $x^*(y)$ não será obtido por otimização convexa fechada, mas estimado pela simulação microscópica calibrada no SUMO, controlada em tempo de execução pela interface TraCI (Traffic Control Interface), e aproximado, para fins de busca no nível superior, por um **surrogate** $\hat{x}(y) \approx x^*(y)$ treinado sobre pares (intervenção, resposta de tráfego) gerados por simulação.

O **nível superior** é um problema multiobjetivo:

$$\min_{y \in \{0,1\}^{|\mathcal{I}|}} \; F(y) = \big(f_1(y), f_2(y), \dots, f_k(y)\big)$$

cujos componentes típicos se sintetizam na tabela a seguir.

| Componente | Descrição |
|---|---|
| $f_1$ | tempo total de viagem / tempo médio de viagem na rede, dado $x^*(y)$ |
| $f_2$ | atraso agregado nas interseções críticas |
| $f_3$ | emissões estimadas (proxy baseado em velocidade/parada, ex. modelo HBEFA do SUMO) |
| $f_4$ | custo de implantação do pacote de intervenções |
| $f_5$ | perda (ou ganho) de acessibilidade por zona |
| $f_6$ | confiabilidade do transporte público (variância do tempo de viagem das linhas de ônibus afetadas) |
| $f_7$ | indicador de equidade (dispersão dos impactos entre bairros/zonas censitárias) |

O problema está sujeito, em primeiro lugar, a uma **restrição orçamentária**, $\sum_i c_i \, y_i \le B$. Em segundo lugar, exige-se **capacidade mínima residual** em arcos designados como críticos, como acessos hospitalares e corredores de emergência. Impõe-se, ainda, a **continuidade da rede cicloviária/pedonal**, expressa como restrições de conectividade topológica sobre o subgrafo induzido pelas intervenções de modo ativo selecionadas. Ademais, a **viabilidade jurídico-urbanística** obriga $y_i = 0$ para intervenções incompatíveis com o zoneamento do Plano Diretor (Lei Complementar nº 612/2018) ou com as diretrizes do PlanMob (Lei Complementar nº 576/2016). Por fim, a **compatibilidade topológica** veda a seleção simultânea de intervenções mutuamente exclusivas — por exemplo, uma via não pode ser convertida em mão única em dois sentidos opostos.

A solução do problema é, portanto, uma fronteira de Pareto $\{y^*\}$ de pacotes de intervenção não dominados, da qual se extraem recomendações para análise before/after.

## 7. Objetivo geral

Formular e resolver, por meio de métodos de otimização bi-nível multiobjetivo apoiados por um surrogate de aprendizado de máquina, o problema de seleção de um pacote de intervenções viárias discretas para um corredor arterial de São José dos Campos, produzindo um sistema reprodutível de apoio à decisão fundamentado em evidência quantitativa de simulação calibrada.

## 8. Objetivos específicos

O objetivo geral desdobra-se em sete objetivos específicos, encadeados da construção do modelo à recomendação final. O primeiro objetivo específico consiste em construir e calibrar um modelo de rede do corredor de estudo no SUMO, a partir de dados do OpenStreetMap convertidos e ajustados pelas ferramentas de construção de rede do próprio simulador, validado contra contagens de tráfego e contra a Pesquisa Origem-Destino de SJC. O segundo consiste em definir formalmente o catálogo restrito de intervenções viáveis $\mathcal{I}$, com seus parâmetros, custos de implantação e restrições de viabilidade jurídico-urbanística derivadas do PlanMob e do Plano Diretor.

O terceiro objetivo específico é formular matematicamente o problema de desenho de rede como um programa bi-nível multiobjetivo, especificando funções objetivo, restrições e a relação entre as variáveis de decisão do nível superior e o equilíbrio de tráfego do nível inferior. O quarto é projetar e treinar um surrogate de aprendizado de máquina (candidato principal: GNN) capaz de aproximar a resposta de tráfego das simulações a partir da topologia da rede e do vetor de intervenções, avaliando sua precisão e seus limites de generalização.

O quinto objetivo específico é comparar o desempenho (qualidade de solução, custo computacional, escalabilidade) de ao menos três classes de métodos de otimização do nível superior — um método exato ou de relaxação para instâncias reduzidas, uma meta-heurística evolutiva (ex. NSGA-II) e um método de otimização Bayesiana —, operando tanto sobre o simulador direto quanto sobre o surrogate. O sexto é conduzir uma avaliação before/after comparando o cenário-base calibrado com os pacotes de intervenção recomendados pela fronteira de Pareto obtida, segundo as métricas definidas na Seção 10. Por fim, o sétimo objetivo específico é propor e documentar um pacote de intervenções priorizado para o corredor de estudo, acompanhado da análise de sensibilidade e das limitações da recomendação.

## 9. Metodologia e métodos propostos

O simulador de tráfego de referência será o **SUMO**, utilizado tanto para gerar o cenário-base calibrado quanto como oráculo de avaliação (ground truth) para o treinamento e a validação do surrogate, com controle em tempo de execução via **TraCI** quando necessário — por exemplo, para faixas reversíveis dependentes de horário. A rede será construída a partir de extratos do OpenStreetMap processados pelo conversor de redes do SUMO (netconvert), com ajustes manuais no editor gráfico do simulador (netedit) para refletir a geometria real do corredor.

A formulação bi-nível seguirá a linhagem metodológica estabelecida por Miandoabchi et al. (2011, 2013) e por Miandoabchi e Farahani (2010) para o Urban Network Design Problem, adaptando o catálogo de intervenções ao contexto de SJC. Para o nível superior, serão comparados três caminhos: primeiro, uma formulação exata ou relaxação linear/inteira para uma versão simplificada da rede, que serve de referência de qualidade de solução em instâncias pequenas; em segundo lugar, algoritmos genéticos multiobjetivo (NSGA-II ou variantes), alinhados à tradição de meta-heurísticas para o UNDP; e, por fim, otimização Bayesiana multiobjetivo, adequada a avaliações caras da função objetivo.

O componente de aprendizado de máquina seguirá a linha de trabalhos recentes que empregam redes neurais em grafos como surrogate de modelos de atribuição de tráfego e de problemas de desenho de rede bi-nível (Liu et al., 2023), explorando a estrutura topológica da rede viária (nós como interseções, arestas como arcos/vias, atributos como capacidade e intervenção aplicada) para prever métricas agregadas de desempenho de tráfego sem executar uma simulação completa a cada avaliação do nível superior. A estratégia de treinamento combinará amostragem ativa, que prioriza regiões do espaço de intervenções com maior incerteza do surrogate, com um orçamento fixo de simulações completas, de modo a tornar explícito o trade-off entre custo computacional e fidelidade da aproximação — o próprio objeto de investigação do projeto.

## 10. Métricas de avaliação before/after

A comparação entre o cenário-base e os pacotes de intervenção recomendados empregará, no mínimo, as métricas sintetizadas a seguir.

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

O resultado esperado não é um algoritmo isolado, mas um **sistema de apoio à decisão**: um pipeline computacional integrado (modelo de rede calibrado, catálogo de intervenções, gerador e avaliador de cenários, surrogate treinado, otimizador multiobjetivo e módulo de análise before/after) capaz de produzir, para o corredor de estudo, uma fronteira de pacotes de intervenção não dominados, documentada e auditável.

A contribuição acadêmica específica em Pesquisa Operacional é dupla. Em primeiro lugar, propõe-se uma formulação bi-nível multiobjetivo do Urban Network Design Problem adaptada a restrições de viabilidade jurídico-urbanística de um caso real brasileiro, pouco explorada na literatura internacional, predominantemente aplicada a redes sintéticas ou norte-americanas/europeias. Em segundo lugar, realiza-se uma avaliação empírica, sobre essa rede real, de **quando e com que grau de confiança um surrogate aprendido aproxima resultados caros de simulação de tráfego** o suficiente para substituir o simulador dentro do laço de otimização, permitindo que métodos exatos e heurísticos explorem o espaço de intervenções com custo computacional tratável em um cenário de porte prático.

Dessa forma, a contribuição transcende o corredor estudado: ao demonstrar as condições em que a otimização apoiada por surrogate produz evidência confiável, o trabalho oferece a municípios de porte médio um caminho replicável e auditável para fundamentar decisões de investimento em mobilidade antes de sua implantação.

## 12. Limitações e riscos

A primeira limitação reside em **dados incompletos ou desatualizados**: a Pesquisa OD e as contagens de tráfego de SJC podem não cobrir integralmente o corredor escolhido ou estar defasadas, exigindo complementação por contagens próprias ou por estimativas indiretas.

Ademais, o **custo computacional da simulação** é um risco relevante, uma vez que a geração do volume de simulações necessário para treinar e validar o surrogate pode ser limitada pelo tempo de execução disponível ao longo do mestrado, condicionando o tamanho do corredor e do catálogo de intervenções.

Há, também, o **risco de overfitting do surrogate**: um modelo treinado sobre um conjunto limitado de configurações de rede pode generalizar mal para combinações de intervenções não amostradas, o que exige validação cruzada cuidadosa e quantificação explícita de incerteza.

Do ponto de vista institucional, a **viabilidade jurídica e política das intervenções** impõe outra limitação: as restrições formais do Plano Diretor e do PlanMob podem não capturar integralmente barreiras políticas ou sociais à implantação real, de modo que a recomendação final deve ser lida como evidência técnica, não como decisão administrativa.

Verifica-se, ainda, o **erro de especificação do modelo de equilíbrio**: a aproximação do comportamento dos usuários (rotas, elasticidade de demanda) no simulador é, em si, uma simplificação da realidade, cujos parâmetros de calibração introduzem incerteza adicional propagada a todo o pipeline.

Por fim, acrescentou-se em 2026-10-26 a **incerteza estrutural da rede viária**. A rede $G$ derivada do OpenStreetMap pelo conversor de redes do SUMO pode conter omissões, atributos inferidos (inclusive semáforos, quando inferidos automaticamente) e efeitos de borda do recorte espacial sobre conectividade e acessibilidade; tais imperfeições alimentam o nível inferior como erro estrutural, anterior à calibração de demanda. Como mitigação, preveem-se a validação da rede real (não apenas de redes de teste), uma revisão manual documentada no editor de redes e o registro de proveniência de cada construção (versão do simulador, parâmetros de conversão e identificação do extrato de dados), conforme discutido no Capítulo 3.

## 13. O que evitar

Três cautelas delimitam o que este trabalho não deve propor. Primeiro, não se deve adotar um modelo de inteligência artificial generativa que "invente" ruas ou geometrias de rede livremente: toda intervenção deve pertencer ao catálogo restrito e tecnicamente viável definido na Seção 6.

Em segundo lugar, o jogo Cities: Skylines não deve ser utilizado como evidência quantitativa de desempenho de tráfego; seu uso, se houver, restringe-se à comunicação com stakeholders, nunca à avaliação ou à validação do modelo.

Por fim, não se deve iniciar o projeto por uma formulação de aprendizado por reforço (RL) sem antes estabelecer rigorosamente a formulação de otimização bi-nível multiobjetivo e suas restrições. O RL, se vier a ser considerado, é uma possível técnica de solução do nível superior subordinada à formulação matemática, não o ponto de partida do projeto.

## 14. Cronograma tentativo (4 semestres)

| Semestre | Atividades principais |
|---|---|
| 1º | Revisão sistemática da literatura de UNDP bi-nível e surrogates de ML para atribuição de tráfego; definição do recorte geográfico; levantamento de dados (OSM, Pesquisa OD, PlanMob, Plano Diretor); construção inicial do modelo de rede em SUMO. |
| 2º | Calibração do modelo de rede; definição formal do catálogo de intervenções e das restrições de viabilidade; formulação matemática completa do problema bi-nível multiobjetivo; geração do primeiro lote de simulações para treinamento do surrogate. |
| 3º | Treinamento e validação do surrogate (GNN); implementação e comparação dos métodos de otimização do nível superior (exato/relaxado, evolutivo, Bayesiano); análise de sensibilidade. |
| 4º | Avaliação before/after dos pacotes recomendados; consolidação do pipeline como sistema de apoio à decisão; redação e defesa da dissertação; submissão de artigo(s) derivado(s). |

## 15. Orientadores em potencial

Busca-se um(a) orientador(a) vinculado(a) ao programa de PG/PO do ITA, com interesse em otimização bi-nível/multiobjetivo, modelagem matemática de problemas de decisão combinatória e/ou meta-heurísticas aplicadas a problemas de engenharia. Como colaborador(a) complementar, é desejável a participação de um(a) pesquisador(a) com experiência em transporte, simulação de tráfego ou planejamento urbano, seja em coorientação formal, seja em colaboração técnica, de modo a assegurar o rigor tanto da formulação de otimização quanto da calibração do modelo de simulação. Nenhum nome específico é indicado neste pré-projeto; a identificação de orientador(a) e de eventual colaborador(a) será conduzida junto à coordenação do programa.

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
