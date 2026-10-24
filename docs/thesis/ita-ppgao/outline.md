# Esqueleto do Produto Técnico — PPGAO/ITA (AO-EL)

> Este é um esqueleto de capítulos, não um rascunho. Cada item abaixo resume, em 2-4 linhas, o que já está coberto pelo `pre-projeto.md` e o que ainda falta pesquisar ou escrever para transformar aquele material em capítulo de dissertação/produto técnico.

## 1. Introdução e Enquadramento Operacional

Já coberto: título provisório, resumo, problema de pesquisa e justificativa, e a distinção explícita entre "mobilidade urbana de SJC" e "logística de acesso a instalações da FAB" (Seções 1-3 e 13 do pré-projeto).

Falta: redigir a introdução como narrativa contínua (não como seções isoladas), com motivação institucional para o PPGAO/AO-EL citando explicitamente a ICA 37-461 e exemplos de dissertações anteriores do programa; falta também a validação formal do enquadramento por um orientador, que pode alterar substancialmente este capítulo.

## 2. Revisão de Literatura em Análise Operacional/Logística

Já coberto: lista inicial de referências sobre desenho de redes de transporte bi-nível (Miandoabchi et al. 2011, trabalhos de 2010/2013, bi-objective bi-level 2023) e menção geral a resiliência de redes sob interdição (Seção 3 e referência 12 do pré-projeto).

Falta: revisão sistemática da literatura de pesquisa operacional militar/logística de defesa (localização-alocação de recursos, resiliência de redes sob ataque/falha, otimização robusta e estocástica aplicada a continuidade operacional); mapeamento de dissertações/teses do próprio PPGAO em temas correlatos; esta é a lacuna mais crítica do pré-projeto atual, pois a referência 12 explicitamente delega a complementação ao futuro orientador.

## 3. Caracterização da Área

Já coberto: contexto histórico-institucional de SJC/ITA/DCTA (Seção 4), recorte geográfico proposto — entorno do complexo ITA/DCTA-CTA ou corredor de acesso único (Seção 5) — e fontes de dados civis já identificadas (PlanMob, Plano Diretor, Pesquisa OD).

Falta: extração e análise efetiva dos dados do OpenStreetMap, PlanMob e Pesquisa OD para o recorte escolhido; levantamento de disponibilidade real de dados operacionais da FAB (sigilo, formato, pontos de contato); decisão final entre as duas alternativas de recorte geográfico, hoje ainda abertas.

Atualização (commits `bf374e4`/`cd68b57`, `cities/sjc/data-manifest.yaml`): para a malha viária civil de base, três fontes públicas de autoatendimento (sem necessidade de contato com órgão algum) foram identificadas — extrato OpenStreetMap, portal Geosanja (Plano Diretor/zoneamento) e Base de Faces de Logradouros do IBGE —, com qualidade ainda não verificada (acesso bloqueado nesta sessão remota) e marcadas como pendência de mesa. Em contrapartida, todo item do manifesto que dependia de resposta de um órgão municipal (contagens de tráfego, planos semafóricos, dados de sinistros em nível de via, rotas/tempos de resposta de emergência, microdados OD) foi marcado `deferred` por decisão do responsável pelo projeto de não contatar nenhuma agência de SJC nesta etapa — isso **não é dado operacional da FAB** (que continua sem qualquer levantamento, mesmo preliminar), mas reforça, com evidência concreta, a limitação da Seção 12 do pré-projeto sobre dependência de dados sensíveis/restritos. A rota de emergência (`emergency-routes`) é explicitamente apontada no manifesto como a fonte mais sensível e difícil de obter, com possível substituição por isócronas a partir de localizações conhecidas de postos — relevante à métrica de continuidade operacional (Seção 10 do pré-projeto). Os dados de sinistros do Infosiga/Detran-SP (`crash-data`) aparecem como possível proxy público agregado para as métricas de segurança da Seção 10, caso dado municipal detalhado não seja obtido.

## 4. Metodologia

Já coberto: metodologia proposta em 6 passos (delimitação/coleta, construção/calibração SUMO, cenários de interdição, otimização bi-nível, experimentação, síntese) e papel do Cities: Skylines como camada opcional de comunicação (Seção 9), além das métricas de avaliação já listadas (Seção 10).

Falta: detalhamento técnico de cada etapa (parâmetros de calibração, algoritmo de otimização de nível superior a ser efetivamente escolhido — hoje em aberto entre heurísticas evolutivas, otimização bayesiana ou programação estocástica), desenho experimental formal e plano de validação do modelo de simulação.

## 5. Cenários e Resultados

Já coberto: tipologia qualitativa de cenários de interdição (obra, acidente, alagamento, evento de grande porte, emergência simplificada) e lista de estratégias logísticas a comparar (Seções 6 e 9).

Falta: todo o trabalho empírico — construção da malha SUMO, calibração, parametrização quantitativa dos cenários, execução dos experimentos e cálculo das métricas da Seção 10; nenhum resultado existe ainda, pois o ArterIA está em estágio pré-código.

## 6. Recomendações Operacionais

Já coberto: natureza esperada da recomendação (protocolo técnico, não normativo, de priorização de rotas e alocação de recursos) e o objetivo específico 7 do pré-projeto.

Falta: conteúdo concreto das recomendações, que depende dos resultados do Capítulo 5; falta também avaliar formato de entrega esperado pelo orientador/FAB (relatório técnico, protótipo de software, memorando) e critérios de viabilidade de adoção institucional.

## 7. Conclusão

Já coberto: nada diretamente; a Seção 11 (resultado esperado/contribuição) antecipa o tipo de contribuição metodológica pretendida (formulação de AO para resiliência de acesso logístico a instalações de defesa, replicável a outras unidades da FAB).

Falta: síntese final a escrever somente após resultados e recomendações estarem consolidados; discussão de limitações realizadas (vs. as antecipadas na Seção 12) e sugestões de trabalhos futuros.

## 8. Referências

Já coberto: lista inicial de 12 referências (literatura técnica de desenho de redes, documentos de planejamento urbano de SJC, documentação interna do ArterIA, normas do PPGAO) — Seção 16 do pré-projeto.

Falta: expandir a referência 12 (literatura de AO/logística de defesa) com itens concretos, idealmente indicados pelo orientador; formatar segundo norma ABNT ou padrão exigido pelo PPGAO; adicionar referências que surgirem da revisão de literatura do Capítulo 2.
