# Esqueleto do Produto Técnico — PPGAO/ITA (AO-EL)

> Este é um esqueleto de capítulos, não um rascunho. Cada item abaixo resume, em 2-4 linhas, o que já está coberto pelo `pre-projeto.md` e o que ainda falta pesquisar ou escrever para transformar aquele material em capítulo de dissertação/produto técnico.

## 1. Introdução e Enquadramento Operacional

Já coberto: título provisório, resumo, problema de pesquisa e justificativa, e a distinção explícita entre "mobilidade urbana de SJC" e "logística de acesso a instalações da FAB" (Seções 1-3 e 13 do pré-projeto).

Falta: redigir a introdução como narrativa contínua (não como seções isoladas), com motivação institucional para o PPGAO/AO-EL citando explicitamente a ICA 37-461 e exemplos de dissertações anteriores do programa; falta também a validação formal do enquadramento por um orientador, que pode alterar substancialmente este capítulo.

Atualização (commit `cdbdb01`, ADR 0002 do ArterIA): o responsável pelo projeto de software registrou, como reflexão própria (não como indicação de orientador), que um futuro orientador do PPGAO ou o próprio método podem exigir validar o ArterIA contra mais de uma cidade — possivelmente uma mais próxima de outra instalação da FAB — antes do previsto no roadmap do produto. Isso foi, por ora, apenas uma pergunta aberta a levar à conversa com um orientador (ver `progress.md`).

Atualização (commit `dcf417b`): a pergunta acima foi respondida pelo responsável pelo projeto de software — **SJC permanece a única cidade por ora**; a validação multi-cidade continua disponível como capacidade da ferramenta (emenda à ADR 0002), mas é explicitamente tratada como capacidade e não como plano de escopo. É uma decisão do responsável do projeto sobre o escopo do ArterIA, não uma indicação de orientador do PPGAO. Com isso, este capítulo pode seguir assumindo um único recorte geográfico, salvo revisão futura por um orientador.

## 2. Revisão de Literatura em Análise Operacional/Logística

Já coberto: lista inicial de referências sobre desenho de redes de transporte bi-nível (Miandoabchi et al. 2011, trabalhos de 2010/2013, bi-objective bi-level 2023) e menção geral a resiliência de redes sob interdição (Seção 3 e referência 12 do pré-projeto).

Falta: revisão sistemática da literatura de pesquisa operacional militar/logística de defesa (localização-alocação de recursos, resiliência de redes sob ataque/falha, otimização robusta e estocástica aplicada a continuidade operacional); mapeamento de dissertações/teses do próprio PPGAO em temas correlatos; esta é a lacuna mais crítica do pré-projeto atual, pois a referência 12 explicitamente delega a complementação ao futuro orientador.

## 3. Caracterização da Área

Já coberto: contexto histórico-institucional de SJC/ITA/DCTA (Seção 4), recorte geográfico proposto — entorno do complexo ITA/DCTA-CTA ou corredor de acesso único (Seção 5) — e fontes de dados civis já identificadas (PlanMob, Plano Diretor, Pesquisa OD).

Falta: extração e análise efetiva dos dados do OpenStreetMap, PlanMob e Pesquisa OD para o recorte escolhido; levantamento de disponibilidade real de dados operacionais da FAB (sigilo, formato, pontos de contato); decisão final entre as duas alternativas de recorte geográfico dentro de SJC, hoje ainda abertas.

Atualização (commits `bf374e4`/`cd68b57`, `cities/sjc/data-manifest.yaml`): para a malha viária civil de base, três fontes públicas de autoatendimento (sem necessidade de contato com órgão algum) foram identificadas — extrato OpenStreetMap, portal Geosanja (Plano Diretor/zoneamento) e Base de Faces de Logradouros do IBGE —, com qualidade ainda não verificada (acesso bloqueado nesta sessão remota) e marcadas como pendência de mesa. Em contrapartida, todo item do manifesto que dependia de resposta de um órgão municipal (contagens de tráfego, planos semafóricos, dados de sinistros em nível de via, rotas/tempos de resposta de emergência, microdados OD) foi marcado `deferred` por decisão do responsável pelo projeto de não contatar nenhuma agência de SJC nesta etapa — isso **não é dado operacional da FAB** (que continua sem qualquer levantamento, mesmo preliminar), mas reforça, com evidência concreta, a limitação da Seção 12 do pré-projeto sobre dependência de dados sensíveis/restritos. A rota de emergência (`emergency-routes`) é explicitamente apontada no manifesto como a fonte mais sensível e difícil de obter, com possível substituição por isócronas a partir de localizações conhecidas de postos — relevante à métrica de continuidade operacional (Seção 10 do pré-projeto). Os dados de sinistros do Infosiga/Detran-SP (`crash-data`) aparecem como possível proxy público agregado para as métricas de segurança da Seção 10, caso dado municipal detalhado não seja obtido.

Atualização (commit `cdbdb01`): o ArterIA agora oferece um comando de scaffolding por cidade (`arteria city new <nome>`), o que tornaria tecnicamente mais barato montar um segundo recorte, caso isso um dia fosse necessário. Isso não resolveria, de todo modo, a limitação de dados operacionais da FAB por cidade (Seção 12 do pré-projeto), que teria de ser levantada de novo para qualquer segunda instalação candidata; é apenas uma facilidade de ferramenta, não um avanço de evidência.

Atualização (commit `396caf7`): o ArterIA passou a ter checagens de validação de malha de rede (`arteria/network/validate.py` — conectividade, becos sem saída, contagem de faixas, mão única, consistência de conexões, limites de velocidade, presença de semáforo), testadas apenas contra fixtures toy `.net.xml`. É uma pré-condição técnica útil para quando a malha real do recorte ITA/DCTA-CTA for extraída do OpenStreetMap, mas não constitui, ainda, qualquer avanço na extração ou análise efetiva dos dados desse recorte (que permanece pendente, ver acima).

Atualização (commit `dcf417b`): o responsável pelo projeto de software decidiu manter SJC como única cidade por ora; um segundo recorte não está no plano, embora a capacidade de ferramenta acima permaneça disponível para uso futuro (pelo próprio responsável, ou por um orientador que venha a exigir validação multi-caso). O recorte geográfico desta trilha pode seguir assumindo um único caso (entorno ITA/DCTA-CTA em SJC), sujeito a revisão por um futuro orientador do PPGAO.

## 4. Metodologia

Já coberto: metodologia proposta em 6 passos (delimitação/coleta, construção/calibração SUMO, cenários de interdição, otimização bi-nível, experimentação, síntese) e papel do Cities: Skylines como camada opcional de comunicação (Seção 9), além das métricas de avaliação já listadas (Seção 10).

Falta: detalhamento técnico de cada etapa (parâmetros de calibração, algoritmo de otimização de nível superior a ser efetivamente escolhido — hoje em aberto entre heurísticas evolutivas, otimização bayesiana ou programação estocástica), desenho experimental formal e plano de validação do modelo de simulação.

Atualização (commit `eefc81c`): o ArterIA passou a ter um mecanismo de proveniência de execução (`arteria/provenance.py`, `RunManifest` com SHA do git, versão do SUMO, seed, hash de configuração e checksums de entrada, gravado em `runs/<cidade>/<run_id>/manifest.json`), ainda não ligado a nenhum comando de execução (previsto para as Fases 3/4/7 do roadmap). É infraestrutura de rastreabilidade, não dado ou resultado; relevante como futuro componente do "plano de validação do modelo de simulação" acima e como suporte à promessa de resultados "reprodutíveis" da Seção 11 do pré-projeto, mas não há ainda experimento real a documentar com ele.

Atualização (commit `cbb53da`): o ArterIA passou a ter métricas de qualidade de ajuste de calibração (`arteria/calibration/goodness_of_fit.py` — estatística GEH por elo com a convenção "GEH<5 em 85% dos elos", RMSE/MAPE de tempo de viagem, resumo combinado passa/falha), testadas só contra contagens e tempos de viagem sintéticos feitos à mão. É exatamente a classe de estatística que o "plano de validação do modelo de simulação" (pendência já listada acima) precisará citar, mas é ferramenta de fidelidade da simulação — distinta das métricas de avaliação operacional da Seção 10 do pré-projeto (tempo de acesso, resiliência, custo logístico, continuidade operacional) — e ainda sem qualquer dado observado do recorte ITA/DCTA-CTA.

Atualização (commit `396caf7`): ver nota equivalente no Capítulo 3 — a validação de malha também apoia o passo 2 (construção/calibração) desta metodologia, como pré-condição técnica antes de calibrar, ainda só testada contra fixtures toy.

Atualização (commit `563d679`): o ArterIA passou a ter uma transformação de restrição de conversão (`arteria/interventions/turn_restriction.py`), que remove uma conexão de uma rede toy e verifica por BFS se os elos afetados permanecem conectados por outro caminho. É a implementação concreta de um item do catálogo de intervenções já citado na Seção 6 e no Objetivo específico 2 do pré-projeto ("restrições de conversão"), mas é infraestrutura de catálogo compartilhada entre cidades do ArterIA, sem relação ainda com o recorte de SJC ou com um cenário de interdição específico; a checagem de conectividade por BFS usada aqui serve para validar a intervenção, não para modelar resiliência (ver nota no Capítulo 5 sobre a distinção).

## 5. Cenários e Resultados

Já coberto: tipologia qualitativa de cenários de interdição (obra, acidente, alagamento, evento de grande porte, emergência simplificada) e lista de estratégias logísticas a comparar (Seções 6 e 9).

Falta: todo o trabalho empírico — construção da malha SUMO, calibração, parametrização quantitativa dos cenários, execução dos experimentos e cálculo das métricas da Seção 10; nenhum resultado existe ainda, pois o ArterIA está em estágio pré-código.

Atualização (commit `563d679`): o ArterIA passou a ter uma primeira implementação de intervenção de catálogo (restrição de conversão, `arteria/interventions/turn_restriction.py`), com checagem de conectividade por BFS após remover a conexão — útil, no futuro, para a mecânica de aplicar intervenções, mas **não** é modelagem de cenário de interdição nem resultado de resiliência: a checagem serve para validar se a própria intervenção proposta deixa a malha conectada, não para medir degradação de acesso sob um evento de interdição (obra, acidente, alagamento etc., Seção 6 do pré-projeto). Nenhum cenário de interdição real foi parametrizado ou executado por este commit.

## 6. Recomendações Operacionais

Já coberto: natureza esperada da recomendação (protocolo técnico, não normativo, de priorização de rotas e alocação de recursos) e o objetivo específico 7 do pré-projeto.

Falta: conteúdo concreto das recomendações, que depende dos resultados do Capítulo 5; falta também avaliar formato de entrega esperado pelo orientador/FAB (relatório técnico, protótipo de software, memorando) e critérios de viabilidade de adoção institucional.

## 7. Conclusão

Já coberto: nada diretamente; a Seção 11 (resultado esperado/contribuição) antecipa o tipo de contribuição metodológica pretendida (formulação de AO para resiliência de acesso logístico a instalações de defesa, replicável a outras unidades da FAB).

Falta: síntese final a escrever somente após resultados e recomendações estarem consolidados; discussão de limitações realizadas (vs. as antecipadas na Seção 12) e sugestões de trabalhos futuros.

## 8. Referências

Já coberto: lista inicial de 12 referências (literatura técnica de desenho de redes, documentos de planejamento urbano de SJC, documentação interna do ArterIA, normas do PPGAO) — Seção 16 do pré-projeto.

Falta: expandir a referência 12 (literatura de AO/logística de defesa) com itens concretos, idealmente indicados pelo orientador; formatar segundo norma ABNT ou padrão exigido pelo PPGAO; adicionar referências que surgirem da revisão de literatura do Capítulo 2.
