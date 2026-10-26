# Pré-Projeto de Mestrado Profissional — PPGAO/ITA (Área AO-EL)

## 1. Título provisório

**Sistema de apoio à decisão para otimização de mobilidade e logística no entorno de instalações da Força Aérea Brasileira em São José dos Campos**

## 2. Resumo

Este pré-projeto propõe o desenvolvimento de um sistema de apoio à decisão baseado em simulação e otimização para problemas de mobilidade e logística viária no entorno de instalações da Força Aérea Brasileira (FAB) em São José dos Campos (SJC), SP — em particular o complexo formado pelo Instituto Tecnológico de Aeronáutica (ITA), pelo Departamento de Ciência e Tecnologia Aeroespacial (DCTA/CTA) e pela infraestrutura aeroportuária e aérea militar da região. O trabalho parte de uma ferramenta em desenvolvimento, o ArterIA, que modela o problema como um desenho de rede de transporte em dois níveis: um nível superior de otimização seleciona pacotes discretos de intervenções viárias (conversões de mão única, faixas reversíveis, faixas exclusivas, restrições de conversão, novos conectores) e um nível inferior de simulação de tráfego (SUMO) estima a resposta de equilíbrio resultante. Em vez de tratar esse arcabouço como uma aplicação genérica de mobilidade urbana — o que não se alinha ao escopo do PPGAO —, propõe-se reorientá-lo para problemas de análise operacional e logística de interesse da FAB: acesso e fluxo de pessoal, cargas e viaturas de serviço ao entorno de instalações aéreas; resiliência da malha viária sob cenários de interdição, degradação ou emergência; e alocação de recursos logísticos sob incerteza operacional. O produto esperado é um protótipo de sistema de apoio à decisão, com métricas de tempo de acesso, resiliência a interdições e continuidade operacional, aplicável tanto a rotinas normais quanto a cenários de crise, com potencial de uso dual civil-militar. O projeto reconhece explicitamente que esse reenquadramento depende da aceitação de um orientador do PPGAO na área AO-EL, cujos temas de pesquisa partem, em geral, de demandas previamente definidas pela FAB.

## 3. Problema de pesquisa e justificativa

O problema de pesquisa **não é** "como melhorar o trânsito de São José dos Campos" — essa formulação pertence à mobilidade urbana civil e não se justifica, por si só, como objeto de um mestrado profissional em Análise Operacional e Engenharia Logística (AO-EL) do ITA, cujos temas derivam majoritariamente de necessidades operacionais da Força Aérea Brasileira. O problema que este pré-projeto propõe é, especificamente: **como apoiar decisões logísticas e de mobilidade de interesse da FAB no entorno imediato de suas instalações em São José dos Campos — ITA, DCTA/CTA e infraestrutura aérea associada — sob condições normais e sob condições de interdição, degradação da malha viária ou crise?**

A justificativa operacional decorre de três pontos. Primeiro, instalações de ensino, pesquisa e comando militar como o ITA e o DCTA dependem de corredores de acesso viário civis compartilhados com o tráfego urbano geral; qualquer obra, acidente, enchente ou evento que degrade esses corredores afeta diretamente o deslocamento de pessoal militar, civil e discente, o transporte de cargas técnicas e a continuidade de atividades de ensino e pesquisa de interesse estratégico. Segundo, a literatura de desenho de redes de transporte (Miandoabchi et al., 2011; os trabalhos de desenho multiobjetivo de redes urbanas de 2010 e 2013) oferece formulações bi-nível de otimização combinatória sob restrições que são diretamente aplicáveis a problemas clássicos de análise operacional — alocação de rotas, dimensionamento de capacidade, decisão sob restrição de recursos — mas raramente são aplicadas ao caso de proteção e resiliência de acesso a instalações de defesa. Terceiro, cenários de interdição viária (bloqueios, obras, desastres naturais, eventos de grande porte na região do Vale do Paraíba) são problemas de decisão sob incerteza com estrutura operacional clara: que rotas alternativas usar, que recursos logísticos realocar, qual o impacto no tempo de resposta e na continuidade das atividades da instalação.

Este reenquadramento é, em si, o ponto crítico deste pré-projeto: o valor acadêmico para o PPGAO não está em otimizar semáforos ou faixas de uma cidade, mas em tratar o entorno de instalações da FAB como um nó logístico sujeito a risco de interrupção, e em formular isso como um problema de pesquisa operacional com método replicável para outras bases e unidades da FAB no Brasil.

## 4. Contexto local: São José dos Campos e a presença da FAB/ITA/CTA-DCTA

São José dos Campos é sede histórica da presença aeroespacial militar brasileira: abriga o ITA, o DCTA (antigo CTA), e tem forte vínculo urbano com a Força Aérea Brasileira desde a criação do Centro Técnico Aeroespacial. A cidade também concentra um ecossistema industrial aeroespacial civil-militar (Embraer, fornecedores, institutos de pesquisa) cujos deslocamentos e cargas frequentemente compartilham a mesma malha viária de acesso às instalações da FAB.

Os instrumentos de planejamento urbano da cidade constituem fontes de dados de mobilidade relevantes mesmo para um recorte operacional militar, porque descrevem a malha viária civil que serve de acesso às instalações: o **PlanMob SJC** (Plano de Mobilidade Urbana, Lei Complementar Municipal nº 576/2016), com seus relatórios de diagnóstico e prognóstico, caracteriza hierarquia viária, demanda de deslocamento e padrões de pico; o **Plano Diretor de SJC** (Lei nº 612/2018) define a macroestrutura viária e trata mobilidade como elemento estrutural do planejamento territorial; e a **Pesquisa Origem-Destino (OD) de São José dos Campos**, usada no projeto municipal "Mobilidade do Futuro", fornece estimativas de demanda que podem ser filtradas para a região de interesse. Esses documentos não substituem dados operacionais específicos da FAB — que não são públicos e cuja obtenção é incerta, como discutido na seção de limitações —, mas estabelecem a linha de base civil sobre a qual qualquer intervenção no entorno das instalações terá de operar.

## 5. Recorte geográfico e escopo

O estudo não trata da cidade inteira, e sim de um recorte geográfico delimitado: **o entorno viário imediato do complexo ITA/DCTA-CTA** (os acessos à Praça Marechal Eduardo Gomes e vias adjacentes que conectam o campus à malha urbana e às principais rotas regionais) e, como alternativa ou complemento, **um corredor de acesso crítico único** identificado em conjunto com um futuro orientador — por exemplo, a via de ligação entre a instalação e a rodovia regional (Via Dutra/Tamoios) usada para deslocamento de pessoal e cargas. A escolha de um recorte pequeno e bem definido, em vez da malha completa de SJC, é condição necessária para (a) manter o projeto tratável dentro do prazo de um mestrado profissional e (b) justificar o enquadramento operacional-militar: um recorte amplo tende a recair, naturalmente, em um problema de mobilidade urbana geral.

## 6. Formulação do problema

O problema é formulado como um problema de análise operacional e logística com estrutura de decisão em dois níveis, adaptando o arcabouço de desenho de redes de transporte usado no ArterIA:

- **Nível superior (decisão):** seleção de um pacote de intervenções e/ou de uma política de alocação de rotas e recursos — por exemplo, qual conjunto de vias priorizar para acesso de viaturas de serviço, qual rota alternativa designar sob interdição, onde alocar capacidade reversível em horários de pico institucional (entrada/saída de turnos, eventos do ITA/DCTA).
- **Nível inferior (resposta):** simulação de tráfego calibrada (SUMO) que estima o tempo de deslocamento, a formação de filas e a capacidade residual da malha para cada cenário, sob demanda normal e sob demanda degradada.
- **Cenários de interdição:** conjunto parametrizado de eventos que removem ou reduzem a capacidade de um ou mais elos da malha (obra, acidente, alagamento, evento de grande porte, cenário simplificado de emergência), análogo a problemas clássicos de confiabilidade e resiliência de redes em pesquisa operacional.
- **Decisão sob incerteza:** a demanda e a probabilidade/duração de cada cenário de interdição são tratadas como incertas, o que aproxima o problema de formulações estocásticas ou robustas de otimização, e não de uma otimização determinística single-shot.

Essa formulação preserva a arquitetura técnica já descrita na documentação do ArterIA (otimizador de nível superior + simulação SUMO de nível inferior), mas desloca o objetivo de "melhorar o tráfego da cidade" para "garantir e otimizar o acesso logístico-operacional às instalações da FAB sob condições normais e adversas".

## 7. Objetivo geral

Desenvolver e avaliar, para o entorno de instalações da Força Aérea Brasileira em São José dos Campos, um sistema de apoio à decisão baseado em simulação de tráfego calibrada e otimização de rotas/alocação de recursos, capaz de comparar estratégias de mobilidade e logística em condições operacionais normais e em cenários de interdição ou crise da malha viária.

## 8. Objetivos específicos

1. Caracterizar a malha viária do entorno imediato das instalações do ITA/DCTA-CTA (ou do corredor de acesso crítico selecionado), a partir de dados do OpenStreetMap, do PlanMob SJC e do Plano Diretor (Lei 612/2018).
2. Construir um catálogo restrito de intervenções e cenários operacionais aplicáveis ao recorte — faixas reversíveis, prioridade de acesso, restrições de conversão, rotas alternativas designadas — distinto do catálogo genérico de mobilidade urbana por incluir explicitamente cenários de interdição e resposta a emergência.
3. Construir e calibrar um modelo de simulação de tráfego (SUMO) do recorte geográfico definido, utilizando contagens, dados da Pesquisa OD de SJC e, quando disponíveis, dados operacionais de fluxo de acesso às instalações.
4. Formular e implementar um modelo de otimização de rotas e alocação de recursos logísticos para dois regimes: operação normal (picos de entrada/saída institucional) e operação sob interdição/degradação parcial da malha.
5. Avaliar a resiliência da malha de acesso a cenários de interdição, medindo a degradação do tempo de resposta e da capacidade de acesso sob diferentes estratégias.
6. Comparar quantitativamente estratégias logísticas alternativas (por exemplo, rota única designada vs. conjunto de rotas alternativas pré-definidas vs. realocação dinâmica) em termos de custo operacional e tempo de acesso.
7. Propor recomendações de protocolo operacional (não normativas, mas técnicas) para priorização de rotas e alocação de recursos em cenários de interdição no entorno das instalações estudadas.

## 9. Metodologia proposta

A metodologia combina simulação de tráfego microscópica e otimização operacional, nos seguintes passos:

1. **Delimitação e coleta de dados**: definição do recorte geográfico (Seção 5); extração da malha viária via OpenStreetMap; levantamento de contagens de tráfego, geometria viária e dados de demanda disponíveis em fontes públicas (PlanMob, Plano Diretor, Pesquisa OD, estudos FGV, projeto Linha Verde) e, quando possível e autorizado, dados operacionais específicos de acesso às instalações da FAB.
2. **Construção e calibração do modelo de simulação**: uso de SUMO (netconvert/netedit para a malha baseada em OSM, TraCI para controle em tempo de execução) para construir um modelo de linha de base calibrado contra volumes de tráfego observados e tempos de viagem, conforme o método já adotado no projeto ArterIA (ADR 0001) e detalhado no `docs/research-brief-sjc.md`.
3. **Definição de cenários de interdição**: parametrização de eventos de interdição/degradação (fechamento parcial ou total de vias, redução de capacidade, picos de demanda extraordinária) com base em registros históricos de incidentes e em cenários hipotéticos plausíveis para a região.
4. **Formulação de otimização**: modelagem bi-nível — nível superior de seleção de rotas/alocação de recursos (heurísticas evolutivas, otimização bayesiana ou programação estocástica, a definir com o orientador) e nível inferior de simulação de resposta de tráfego.
5. **Experimentação e avaliação comparativa**: execução de cenários normais e de interdição, comparação de estratégias segundo as métricas da Seção 10, com análise de sensibilidade e incerteza.
6. **Síntese e recomendação**: consolidação dos resultados em recomendações técnicas de protocolo operacional, incluindo discussão sobre viabilidade de adoção pela FAB/ITA.

O Cities: Skylines, se usado, seria restrito a uma camada opcional de comunicação visual dos cenários para stakeholders — nunca como fonte de evidência quantitativa (ver Seção 13).

## 10. Métricas de avaliação

- **Tempo de acesso/resposta**: tempo de deslocamento entre pontos de origem relevantes (eixos de acesso regional, bairros de moradia de pessoal) e as instalações, em condição normal e sob interdição.
- **Resiliência da malha a interdições**: variação do tempo de acesso e da capacidade residual quando um ou mais elos são removidos ou degradados; identificação de pontos únicos de falha (single points of failure) nos acessos.
- **Custo logístico**: custo operacional estimado das estratégias de roteamento e alocação de recursos comparadas (veículo-hora, desvio de rota, uso de capacidade reversível).
- **Continuidade operacional**: probabilidade e duração esperada de perda de acesso adequado às instalações sob os cenários de interdição modelados.
- **Confiabilidade de rotas designadas**: variabilidade (e.g., percentil 95) do tempo de deslocamento em rotas de acesso prioritário.
- **Métricas de segurança**, quando aplicável: exposição a conflitos em pontos críticos de interseção nas rotas de acesso.

## 11. Resultado esperado / contribuição

Espera-se entregar um protótipo de sistema de apoio à decisão — construído sobre a arquitetura de simulação e otimização já em desenvolvimento no projeto ArterIA, mas redirecionado ao recorte e aos objetivos descritos — que permita à FAB/ITA avaliar, de forma quantitativa e reprodutível, estratégias de mobilidade e logística para o entorno de suas instalações em São José dos Campos, tanto em operação normal quanto em cenários de interdição ou crise. A contribuição acadêmica pretendida é metodológica: uma formulação de análise operacional para resiliência de acesso logístico a instalações de defesa, replicável para outras unidades da FAB, e que explora um gap na literatura de desenho de redes de transporte (tipicamente aplicada a mobilidade urbana geral) ao aplicá-la a um objetivo de continuidade operacional militar. O valor é explicitamente dual: a mesma malha viária e os mesmos dados civis de mobilidade (PlanMob, Plano Diretor, Pesquisa OD) que servem ao planejamento urbano de SJC também sustentam uma análise de interesse direto da FAB.

## 12. Limitações e riscos

- **Dependência de aceitação do enquadramento por um orientador do PPGAO**: os temas de pesquisa do PPGAO são definidos majoritariamente a partir de necessidades previamente estabelecidas pela Força Aérea Brasileira, e não a partir de propostas externas de candidatos. Este pré-projeto é uma proposta de ponto de partida, não um tema já validado; sua viabilidade depende de um docente da área AO-EL reconhecer o recorte logístico-militar como relevante e orientável, e possivelmente de ajustá-lo a uma linha de pesquisa já em curso no programa.
- **Dados sensíveis ou restritos**: dados operacionais reais de fluxo de pessoal, cargas e viaturas de instalações da FAB podem ser sigilosos, de acesso restrito ou simplesmente inexistentes em formato utilizável, o que pode limitar a calibração do modelo a dados civis substitutos (contagens de tráfego públicas, Pesquisa OD) e reduzir o realismo operacional dos resultados.
- **Risco de descaracterização**: existe risco real de o projeto ser lido como "mobilidade urbana de SJC disfarçada de tema militar" caso o recorte geográfico, as métricas e os cenários não sejam claramente centrados em continuidade operacional e logística, e não em bem-estar do tráfego urbano geral. Esse risco deve ser mitigado ativamente ao longo do desenvolvimento, não apenas na redação do pré-projeto.
- **Escopo versus prazo**: por se tratar de mestrado profissional, com prazo tipicamente mais curto que o mestrado acadêmico, o recorte geográfico restrito (Seção 5) é necessário; uma ambição maior (toda a malha de SJC, múltiplas instalações) provavelmente não é exequível no prazo.
- **Maturidade do projeto de origem**: o ArterIA está em estágio inicial; parte do trabalho de mestrado corresponde à própria construção da ferramenta, não apenas à sua aplicação. *Atualização 2026-10-26:* já existe código, e uma primeira execução real construiu e renderizou a rede do corredor B (Av. Andrômeda <-> DCTA) no SUMO, com demanda aleatória apenas para teste de roteabilidade. Não há baseline calibrado nem cenário de interdição, e o enquadramento operacional/FAB segue sem validação por orientador do PPGAO. A construção e a validação da rede são tratadas em `chapters/04-metodologia.md` (seção 4.1).

## 13. O que evitar

- Não propor uma "IA que cria ruas" ou que gera livremente novos traçados viários; o sistema deve sempre operar sobre um catálogo restrito e explícito de intervenções e estratégias viáveis.
- Não usar o Cities: Skylines como evidência quantitativa de desempenho de tráfego ou de resiliência logística; seu uso, se houver, fica restrito à comunicação visual com stakeholders.
- Não apresentar o projeto, em nenhuma seção ou apresentação posterior, como um projeto de mobilidade urbana civil pura. Isso descaracteriza o enquadramento exigido pelo PPGAO e compromete a aderência à área AO-EL — o enquadramento operacional-logístico-militar deve estar explícito desde o título até as métricas de avaliação.
- Não tratar o problema como uma otimização determinística de "melhor caso único"; a dimensão de incerteza e de cenários de interdição é parte constitutiva do problema, não um extra opcional.

## 14. Cronograma tentativo

Considerando o formato de mestrado profissional do PPGAO, com prazo geralmente mais curto que o mestrado acadêmico (cronograma indicativo de aproximadamente 18 a 20 meses):

| Período | Atividade |
|---|---|
| Meses 1–2 | Validação do enquadramento com orientador do PPGAO/AO-EL; ajuste do recorte e dos objetivos ao tema aceito. |
| Meses 3–4 | Revisão de literatura (desenho de redes de transporte, resiliência de redes, análise operacional logística militar); levantamento de dados civis (PlanMob, Plano Diretor, OD) e verificação de disponibilidade de dados operacionais da FAB. |
| Meses 5–7 | Delimitação final do recorte geográfico; construção da malha viária base (OSM/SUMO) do entorno ITA/DCTA-CTA ou do corredor escolhido. |
| Meses 8–10 | Calibração do modelo de simulação; definição e parametrização dos cenários de interdição/crise. |
| Meses 11–13 | Formulação e implementação do modelo de otimização de rotas/alocação de recursos (nível superior) integrado à simulação (nível inferior). |
| Meses 14–15 | Experimentos comparativos entre estratégias logísticas; cálculo das métricas de avaliação (Seção 10). |
| Meses 16–17 | Consolidação dos resultados; elaboração de recomendações de protocolo operacional. |
| Meses 18–20 | Redação final da dissertação, revisão e defesa. |

## 15. Orientadores em potencial

Este pré-projeto não indica nomes de orientadores específicos, por não haver, até o momento, contato formal estabelecido. Busca-se um orientador do corpo docente do PPGAO na área de concentração Análise Operacional e Engenharia Logística (AO-EL). É condição explícita e prévia para o avanço deste projeto que esse orientador aceite o enquadramento operacional-logístico-militar proposto (Seções 3 e 6), já que os temas do programa partem de uma estrutura de linhas de pesquisa previamente definida a partir de demandas da Força Aérea Brasileira, e não de propostas de tema trazidas prontas por candidatos externos. Este documento deve ser tratado como material de discussão inicial para essa conversa, sujeito a revisão substancial conforme a orientação recebida.

## 16. Referências

1. MIANDOABCHI, E. et al. Hybrid Evolutionary Metaheuristics for Concurrent Multi-Objective Design of Urban Road and Public Transit Networks. *Networks and Spatial Economics*, 2011.
2. Multi-objective discrete urban road network design. *Computers & Operations Research*, 2013.
3. A meta-heuristic approach for solving the Urban Network Design Problem. 2010.
4. Bi-objective bi-level optimization for integrating lane-level closure and reversal in redesigning transportation networks. *Operational Research*, 2023.
5. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *PlanMob SJC — Diagnóstico e Prognóstico.* Lei Complementar Municipal nº 576/2016.
6. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Plano Diretor de São José dos Campos.* Lei Municipal nº 612/2018.
7. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Mobilidade do Futuro: um Modelo Disruptivo para São José dos Campos* (Pesquisa Origem-Destino).
8. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Estudos da FGV para a construção do edital do novo transporte público.*
9. PREFEITURA DE SÃO JOSÉ DOS CAMPOS. *Projeto Linha Verde.*
10. INSTITUTO TECNOLÓGICO DE AERONÁUTICA. *ICA 37-461 — normas e documentos institucionais do Programa de Pós-Graduação em Análise Operacional (PPGAO).*
11. ArterIA — documentação interna do projeto: `README.md`, `docs/research-brief-sjc.md` e `docs/adr/0001-traffic-simulator-choice.md` (repositório ArterIA).
12. Literatura de referência em análise operacional e resiliência de redes logísticas sob interdição, a ser complementada com o orientador do PPGAO/AO-EL (por exemplo, trabalhos clássicos de otimização de redes sob falha/interdição e de localização/alocação de recursos logísticos em cenários de defesa, a selecionar conforme a linha de pesquisa aceita).

---

*Documento preparado como pré-projeto de discussão para submissão ao PPGAO/ITA, área AO-EL. Sujeito a revisão substancial conforme orientação recebida.*
