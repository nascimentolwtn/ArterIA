# Pré-Projeto de Mestrado — UNIFA, PPGCA (Programa de Pós-Graduação em Ciências Aeroespaciais)

> **Nota sobre o enquadramento.** Diferentemente dos pré-projetos preparados para o Instituto Tecnológico de Aeronáutica (PG/PO, PG/EEC, PPGAO), este documento representa um **reposicionamento profundo** do projeto, e não uma reinterpretação de resultados. O PPGCA está classificado na grande área de Ciência Política e Relações Internacionais, com linhas de pesquisa voltadas a segurança, defesa e pensamento estratégico — e não a engenharia de transportes, otimização ou simulação. Para que o projeto ArterIA tenha aderência real a esse programa, o **núcleo da dissertação precisa deixar de ser um problema de desenho de rede viária e passar a ser um problema de segurança e defesa**, no qual a mobilidade urbana e a ferramenta ArterIA aparecem como **objeto empírico e instrumento de mensuração**, e não como o objetivo da pesquisa. Este pré-projeto assume esse reposicionamento até o fim, conforme solicitado, e é explícito quanto aos riscos metodológicos envolvidos.

## 1. Título provisório

**Resiliência de infraestrutura viária dual-use no entorno de instalações aeroespaciais estratégicas: um estudo de caso sobre acesso e continuidade operacional em São José dos Campos**

## 2. Resumo

Este pré-projeto propõe investigar, sob a linha de pesquisa "Poder Aeroespacial Brasileiro, Segurança e Defesa" do PPGCA da Universidade da Força Aérea (UNIFA), como a resiliência da infraestrutura viária civil no entorno de instalações aeroespaciais estratégicas — no caso, o complexo formado pelo Instituto Tecnológico de Aeronáutica (ITA), pelo Departamento de Ciência e Tecnologia Aeroespacial (DCTA/CTA) e pela infraestrutura aérea militar em São José dos Campos (SJC), SP — constitui um fator relevante, e hoje pouco estudado no Brasil, para a preparação e a continuidade operacional do poder aeroespacial nacional. A literatura internacional de segurança e defesa já reconhece a infraestrutura de transporte civil como um ativo de "duplo uso" (*dual-use infrastructure*): a mesma malha viária que atende ao deslocamento cotidiano da população é também o que permite o acesso de pessoal, cargas técnicas e recursos a instalações de ensino, pesquisa e comando aeroespacial, especialmente em cenários de disrupção (obras, acidentes, desastres naturais, eventos de grande porte na região do Vale do Paraíba). O exemplo mais conhecido desse reconhecimento institucional é a iniciativa de "Mobilidade Militar" (*Military Mobility*) da Organização do Tratado do Atlântico Norte (OTAN) e da União Europeia (UE), que trata explicitamente a infraestrutura civil de transporte como um multiplicador — ou um ponto de estrangulamento — da capacidade de projeção de poder. Propõe-se adaptar esse tipo de raciocínio ao caso brasileiro, usando SJC como estudo de caso e, como instrumento de mensuração empírica, um modelo de simulação e otimização de tráfego (o projeto ArterIA, em desenvolvimento), que permite quantificar, sob diferentes cenários de interdição da malha viária, o tempo de acesso, a existência de rotas alternativas e a robustez do entorno das instalações estudadas. A contribuição pretendida não é, portanto, um algoritmo de otimização de trânsito, mas uma análise de política de defesa fundamentada empiricamente: até que ponto a infraestrutura civil de acesso é hoje um ponto de vulnerabilidade silenciosa do poder aeroespacial brasileiro, e que medidas de planejamento urbano-militar conjunto poderiam mitigar esse risco.

## 3. Problema de pesquisa e justificativa

O problema de pesquisa **não é** "como melhorar o trânsito de São José dos Campos" nem "como otimizar uma rede viária com IA": tais formulações pertencem à engenharia de transportes e não têm aderência direta às linhas do PPGCA. O problema de pesquisa, reformulado para a linha de Segurança e Defesa, é o seguinte:

> **Em que medida a resiliência (ou a fragilidade) da infraestrutura viária civil de acesso a instalações aeroespaciais estratégicas representa um fator relevante — e atualmente não mensurado — na capacidade do Estado brasileiro de preparar e empregar o poder aeroespacial, e quais intervenções de planejamento urbano-militar conjunto reduziriam essa vulnerabilidade?**

A justificativa apoia-se em três pontos. O primeiro é uma **lacuna conceitual no debate brasileiro de defesa**. A Política Nacional de Defesa e a Estratégia Nacional de Defesa tratam de capacidade industrial, dissuasão e articulação das Forças Armadas, mas a literatura brasileira de estudos estratégicos dá pouca atenção explícita à dependência de infraestrutura civil de transporte como condição de prontidão operacional — ao contrário do que ocorre na literatura euro-atlântica sobre *military mobility*, em que o tema é tratado como central à política de defesa desde, pelo menos, o Plano de Ação de Mobilidade Militar da UE (2018) e as discussões correlatas na OTAN.

O segundo ponto é a existência de um **caso empírico concreto e acessível**. São José dos Campos concentra, em um raio reduzido, o ITA, o DCTA/CTA e infraestrutura aérea militar, formando um polo aeroespacial de relevância nacional cujo acesso viário é inteiramente compartilhado com o tráfego urbano civil — sujeito a enchentes, obras, acidentes e eventos que já são hoje objeto de diagnóstico no PlanMob municipal e no Plano Diretor da cidade. Tal configuração permite um estudo de caso único (*single case study*) com dados civis já disponíveis, sem exigir acesso a informação sensível ou classificada na fase inicial.

O terceiro ponto é a existência de um **instrumento de mensuração já em desenvolvimento**. O projeto ArterIA, em construção pelo autor deste pré-projeto, já propõe modelar a rede viária no simulador microscópico de tráfego SUMO (*Simulation of Urban MObility*) e avaliar pacotes de intervenção contra uma simulação calibrada. Esse instrumento pode ser redirecionado — sem que seu núcleo técnico deixe de existir — para gerar cenários de interdição (bloqueios, obras, desastres) e medir tempo de acesso, existência de rotas alternativas e grau de redundância da malha no entorno das instalações estudadas, fornecendo a evidência quantitativa que normalmente falta em análises qualitativas de segurança de infraestrutura.

## 4. Contexto local: São José dos Campos como polo aeroespacial

SJC concentra o ITA, o DCTA/CTA (que inclui o Instituto de Aeronáutica e Espaço — IAE — e o Instituto de Estudos Avançados — IEAv, citados inclusive como parceiros do programa de pós-graduação em Ciências e Tecnologias Espaciais do próprio ITA) e infraestrutura aérea militar associada. A cidade possui, ademais, um Plano de Mobilidade Urbana formal (PlanMob SJC, Lei Complementar 576/2016) e um Plano Diretor vigente (Lei 612/2018), que tratam a mobilidade como direito estrutural da cidade, além de uma Pesquisa Origem-Destino usada no projeto "Mobilidade do Futuro". Nenhum desses instrumentos, no entanto, trata explicitamente do acesso viário a instalações aeroespaciais como questão de segurança nacional — o que reforça a lacuna identificada acima e demarca o espaço de contribuição original deste projeto: cruzar o diagnóstico de mobilidade civil já existente com uma leitura de segurança e defesa que hoje não é feita.

## 5. Recorte do estudo

O recorte não será a cidade inteira, mas os corredores de acesso viário a um conjunto delimitado de instalações aeroespaciais em SJC (por exemplo, o entorno do ITA/DCTA e as vias de acesso à infraestrutura aérea associada), tratados como uma "zona de interesse" para efeito de análise de resiliência. A escolha exata do perímetro e do nível de detalhe dependerá de orientação do PPGCA quanto ao que pode ser tratado com dados públicos e ao que exigiria interlocução formal com a Força Aérea Brasileira (FAB).

## 6. Formulação do problema

O projeto combina dois níveis de análise, deliberadamente distintos em método.

O **nível conceitual** constitui o núcleo da dissertação e segue o método dos estudos estratégicos e de segurança. Compreende a revisão e a aplicação da literatura de infraestrutura crítica dual-use e de *military mobility* ao caso brasileiro; a análise documental da Política Nacional de Defesa, da Estratégia Nacional de Defesa e de instrumentos municipais de mobilidade; e uma eventual coleta qualitativa (entrevistas ou questionários, sujeitos a aprovação ética) com atores de planejamento urbano e, na medida do possível, de planejamento de instalações, para entender como o tema é hoje percebido e tratado institucionalmente.

O **nível instrumental**, por sua vez, é ferramenta de apoio e segue o método da engenharia. Consiste em um modelo de simulação de tráfego calibrado (ArterIA/SUMO), usado não para otimizar intervenções de mobilidade civil em geral, mas para gerar cenários de interdição da malha viária (bloqueios parciais, obras, eventos climáticos) e medir, para a zona de interesse definida, indicadores de resiliência: tempo de acesso sob interdição, número e qualidade de rotas alternativas e sensibilidade do tempo de acesso a diferentes pontos de falha da rede.

A pesquisa é, portanto, um estudo de caso de política de segurança e defesa **apoiado em evidência quantitativa de engenharia de transportes**, e não um projeto de otimização de tráfego com uma camada de discurso estratégico. Tal distinção precisa estar clara desde a qualificação.

## 7. Objetivo geral

Avaliar, a partir do estudo de caso de São José dos Campos, em que medida a resiliência da infraestrutura viária civil de acesso a instalações aeroespaciais estratégicas é um fator relevante para a continuidade do poder aeroespacial brasileiro, e propor diretrizes de planejamento urbano-militar conjunto para mitigar as vulnerabilidades identificadas.

## 8. Objetivos específicos

O primeiro objetivo específico é revisar a literatura internacional de infraestrutura crítica dual-use e de *military mobility* e discutir sua aplicabilidade ao contexto brasileiro e à Política/Estratégia Nacional de Defesa. O segundo consiste em caracterizar o polo aeroespacial de São José dos Campos (ITA, DCTA/CTA, infraestrutura aérea associada) e seus corredores de acesso viário civis. O terceiro é levantar, a partir de documentos públicos (PlanMob, Plano Diretor, histórico de obras e ocorrências), os principais pontos de vulnerabilidade já conhecidos na malha viária de acesso à zona de interesse.

O quarto objetivo é adaptar o modelo de simulação do projeto ArterIA para gerar cenários de interdição (bloqueios, obras, eventos climáticos) sobre a zona de interesse definida, e o quinto, medir, para cada cenário, indicadores de resiliência de acesso (tempo de deslocamento, redundância de rotas, pontos únicos de falha). O sexto consiste em analisar, qualitativamente, como atores de planejamento urbano e de defesa hoje percebem (ou não) essa vulnerabilidade, na medida em que o acesso a esses atores for viável dentro do prazo do mestrado. Por fim, o sétimo objetivo é propor diretrizes de planejamento urbano-militar conjunto — por exemplo, critérios de priorização de obras de manutenção viária ou protocolos de rota alternativa em cenário de interdição — fundamentadas na evidência quantitativa e qualitativa levantada.

## 9. Metodologia proposta

A pesquisa adota método misto, predominantemente qualitativo no núcleo teórico-conceitual e quantitativo na etapa instrumental.

A **revisão documental e teórica** abrange a literatura de segurança de infraestrutura crítica, a de *military mobility* (OTAN/UE), a Política Nacional de Defesa e a Estratégia Nacional de Defesa do Brasil, e a literatura de desenho e resiliência de redes de transporte (a mesma base de Pesquisa Operacional já mapeada para os pré-projetos do ITA: Miandoabchi et al., 2011; trabalhos de desenho multiobjetivo de redes urbanas de 2010 e 2013). O delineamento é o de **estudo de caso único incorporado** (SJC), com a zona de interesse como unidade de análise.

A **modelagem quantitativa de resiliência** emprega simulação de tráfego calibrada (SUMO) sob cenários de interdição, reaproveitando a arquitetura de simulação já planejada para o ArterIA, mas com cenários desenhados para medir resiliência de acesso, e não para otimizar pacotes de intervenção de mobilidade geral. Por fim, a **coleta qualitativa complementar** (entrevistas, análise documental de planejamento institucional) está sujeita a aprovação de comitê de ética e a eventuais restrições de acesso a informação institucional da FAB, sendo tratada aqui como etapa condicional, e não como pré-requisito para a viabilidade mínima do projeto.

> **Nota de atualização (2026-10-26).** A rede viária real do Corredor B (acesso Av. Andrômeda ↔ DCTA) foi construída pela primeira vez a partir de dados abertos do OpenStreetMap (OSM) e renderizada em simulação, como teste de rotabilidade; não se trata de linha de base calibrada nem de seleção de corredor. A construção e a validação da rede (incluindo efeito de borda do recorte, completude do OSM e semáforos inferidos) passam a ser etapa metodológica a documentar, conforme registrado nas notas de trabalho desta trilha. O enquadramento de segurança/defesa segue **não validado** por orientador do PPGCA.

## 10. Métricas de avaliação

As métricas de avaliação articulam a dimensão quantitativa e a qualitativa do estudo, conforme a Tabela 1.

**Tabela 1 — Métricas de avaliação propostas**

| Métrica | Natureza |
| :-- | :-- |
| Tempo de acesso sob condição normal versus sob cenários de interdição | Quantitativa |
| Número e qualidade de rotas alternativas disponíveis por ponto de interesse | Quantitativa |
| Identificação de pontos únicos de falha (*single points of failure*) na malha de acesso | Quantitativa |
| Tempo estimado de resposta/recuperação após um evento de interdição, com base em dados históricos de obras e ocorrências, quando disponíveis | Quantitativa |
| Grau de consciência institucional sobre essa vulnerabilidade (por documentos e, se viável, entrevistas) | Qualitativa |

Fonte: elaborado pelo autor.

## 11. Resultado esperado e contribuição

O resultado esperado não é um otimizador de tráfego, mas um **diagnóstico de política de defesa fundamentado empiricamente**: uma caracterização, com evidência quantitativa, de quão resiliente (ou vulnerável) é hoje o acesso viário civil às instalações aeroespaciais de SJC, acompanhada de diretrizes de planejamento conjunto entre o município e as instituições aeroespaciais locais. A contribuição acadêmica consiste em introduzir, no debate brasileiro de estudos estratégicos aeroespaciais, uma discussão já consolidada internacionalmente (a infraestrutura civil como condição de prontidão operacional), testada em um caso concreto e mensurável, preenchendo uma lacuna que a revisão de literatura brasileira de defesa hoje não cobre.

## 12. Limitações e riscos

Esta é a seção mais importante do pré-projeto e deve ser tratada com total transparência.

O primeiro é o **risco disciplinar**. O autor é engenheiro de computação, sem formação prévia em Ciência Política, Relações Internacionais ou Estudos Estratégicos — as disciplinas que de fato sustentam o PPGCA. Sem apoio metodológico forte do orientador (e, idealmente, coorientação ou disciplinas de nivelamento em teoria estratégica, segurança internacional e metodologia qualitativa), há risco real de a dissertação permanecer superficial no núcleo teórico e "engenheira demais" para o programa — exatamente o erro que este reenquadramento busca evitar, mas que exige vigilância constante ao longo do mestrado.

O segundo é a **dependência de aceitação do enquadramento**. Diferentemente do PG/PO, do PG/EEC e do PPGAO — que já tratam de otimização e análise operacional como núcleo —, o PPGCA exigirá que um orientador aceite explicitamente que a infraestrutura de mobilidade é um tema legítimo de "Poder Aeroespacial, Segurança e Defesa". Tal aceitação não pode ser assumida como garantida, e o pré-projeto deve ser apresentado como uma proposta a ser validada, e não como um encaixe óbvio.

O terceiro diz respeito ao **acesso a dados e atores institucionais**. A etapa qualitativa (entrevistas, documentos de planejamento institucional da FAB) pode depender de autorizações que vão além do que o autor controla; por isso, o projeto foi desenhado para ser viável mesmo que essa etapa seja reduzida ou substituída por análise documental pública.

O quarto é o **risco de sensibilidade do tema**. Qualquer análise de vulnerabilidade de acesso a instalações militares, mesmo com dados públicos, deve ser conduzida com cuidado quanto ao nível de detalhe divulgado publicamente na dissertação final, evitando produzir um "mapa de vulnerabilidades" irresponsável. Tal cuidado deve ser discutido com o orientador e, se necessário, com a instituição, desde o início.

Por fim, há a tensão entre **escopo e prazo**: um mestrado acadêmico tem prazo definido, e o projeto deve ser dimensionado para produzir resultado completo mesmo que a etapa qualitativa institucional seja limitada.

## 13. O que evitar

Alguns cuidados delimitam o que este trabalho não deve ser. Não se deve apresentar o projeto como "otimização de trânsito de SJC com um verniz estratégico", o que descaracterizaria o enquadramento para o PPGCA e repetiria o erro que a análise original já identificou como "fraco e provavelmente rejeitado por falta de aderência às linhas de pesquisa". Tampouco se deve tratar a simulação de tráfego como o resultado principal da dissertação, uma vez que ela é evidência de apoio a um argumento de política de defesa; e o jogo Cities: Skylines não deve ser usado como evidência quantitativa em nenhuma hipótese.

Ademais, não se devem divulgar, na versão final e pública da dissertação, detalhes operacionais sensíveis sobre vulnerabilidades específicas de acesso que possam ser usados de forma mal-intencionada; qualquer achado desse tipo deve ser tratado com o orientador quanto ao nível de divulgação apropriado. Por fim, não se deve assumir que o orientador aceitará o enquadramento sem conversa prévia: este pré-projeto deve ser tratado como ponto de partida de negociação, e não como proposta fechada.

## 14. Cronograma tentativo

O cronograma distribui as atividades em quatro semestres (Tabela 2).

**Tabela 2 — Cronograma tentativo**

| Semestre | Atividades principais |
| :-- | :-- |
| 1º | Revisão de literatura de segurança de infraestrutura crítica e *military mobility*; nivelamento metodológico em estudos estratégicos/qualitativos; delimitação final da zona de interesse em SJC; validação do enquadramento com o orientador. |
| 2º | Levantamento documental (PlanMob, Plano Diretor, histórico de obras/ocorrências); adaptação do modelo ArterIA para cenários de interdição; qualificação. |
| 3º | Execução dos cenários de simulação de resiliência; coleta qualitativa complementar (se viável); análise integrada quantitativa-qualitativa. |
| 4º | Redação da dissertação, formulação das diretrizes de planejamento conjunto, defesa. |

Fonte: elaborado pelo autor.

## 15. Orientadores em potencial

Busca-se um orientador do PPGCA vinculado à linha "Poder Aeroespacial Brasileiro, Segurança e Defesa", com interesse em infraestrutura crítica, segurança de instalações ou políticas de defesa aplicadas. Dada a natureza interdisciplinar do projeto, é desejável — embora não estritamente necessária na fase de pré-projeto — a possibilidade de coorientação ou consultoria metodológica de alguém com experiência em infraestrutura de transporte ou engenharia de resiliência, para sustentar a etapa instrumental sem comprometer o núcleo teórico do programa. Nomes específicos não são indicados aqui; devem ser identificados em conversa direta com a coordenação do PPGCA.

Em síntese, o que se propõe é deslocar a infraestrutura viária civil do campo exclusivo do planejamento urbano para o da preparação do poder aeroespacial, de modo que a continuidade do acesso às instalações estratégicas de São José dos Campos passe a ser tratada como questão de segurança e defesa, mensurável e passível de planejamento conjunto entre o município e a Força.

## 16. Referências

1. European Union / NATO. *EU-NATO Action Plan on Military Mobility* (2018) e documentos correlatos sobre mobilidade militar e infraestrutura civil dual-use. *(referência institucional; recomenda-se verificação e aprofundamento bibliográfico específico antes da qualificação, pois este pré-projeto não teve acesso a busca bibliográfica dedicada sobre o tema.)*
2. Ministério da Defesa do Brasil. *Política Nacional de Defesa* e *Estratégia Nacional de Defesa* (versões vigentes).
3. Miandoabchi, E. et al. (2011). *Hybrid Evolutionary Metaheuristics for Concurrent Multi-Objective Design of Urban Road and Public Transit Networks.* Networks and Spatial Economics.
4. *Multi-objective discrete urban road network design.* Computers & Operations Research, 2013.
5. *A meta-heuristic approach for solving the Urban Network Design Problem.* 2010.
6. Prefeitura de São José dos Campos. *PlanMob SJC — Diagnóstico e Prognóstico.*
7. Prefeitura de São José dos Campos. *Plano Diretor de Desenvolvimento Integrado*, Lei Complementar 612/2018.
8. Instituto Tecnológico de Aeronáutica. Documentos institucionais sobre o Departamento de Ciência e Tecnologia Aeroespacial (DCTA/CTA) e sua relação com o ITA.
9. Literatura geral de infraestrutura crítica e segurança (*critical infrastructure protection*), a ser complementada com busca bibliográfica dedicada em bases de Relações Internacionais e Estudos de Segurança durante o primeiro semestre do mestrado.

> **Observação metodológica final:** as referências 1 e 9 marcam honestamente os pontos em que este pré-projeto se apoia em conhecimento geral do autor sobre o tema de *military mobility*, e não em uma revisão bibliográfica sistemática de Relações Internacionais/Segurança — que é, precisamente, o trabalho a ser feito nos primeiros meses do mestrado, idealmente sob orientação direta de um docente do PPGCA.
