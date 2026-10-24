# Esqueleto de Capítulos — Dissertação (PG/EEC, ITA, Área Informática)

> Esqueleto de alto nível derivado de `pre-projeto.md`. Não é rascunho de conteúdo — serve apenas para orientar a estrutura da dissertação e mapear o que já está coberto versus o que ainda falta pesquisar/escrever.

## 1. Introdução

- **Já coberto no pré-projeto**: motivação, problema de pesquisa (Seção 3), contexto de SJC (Seção 4), recorte geográfico (Seção 5), objetivo geral e específicos (Seções 7-8), contribuição esperada (Seção 11).
- **Falta pesquisar/escrever**: texto narrativo de introdução propriamente dito (contextualização, pergunta de pesquisa formal, estrutura do documento); versão final do título após validação com orientador.

## 2. Fundamentação Teórica em IA/RL/GNN

- **Já coberto no pré-projeto**: levantamento inicial de trabalhos relacionados em três linhas — RL multiagente para alocação de faixas/configuração de grafos, GNNs como surrogate, RL para controle de sinalização (Seção 6); lista de referências-base (Seção 16).
- **Falta pesquisar/escrever**: revisão sistemática mais profunda (busca estruturada, não apenas lista curada) de RL multiagente cooperativo (MARL), arquiteturas de GNN para grafos dinâmicos/heterogêneos, bi-level network design problem; formalização matemática de MDP/POMDP multiagente e de convoluções em grafo que serão usadas; comparação crítica entre candidatos de algoritmo (ex. MAPPO, QMIX, actor-critic com crítico centralizado).

## 3. Arquitetura do Sistema

- **Já coberto no pré-projeto**: desenho conceitual em quatro componentes — pipeline de dados, ambiente de treinamento via TraCI, arquitetura de agentes + GNN compartilhada, infraestrutura de experimentação (Seção 9); integração prevista com a estrutura `cities/sjc/` do ArterIA.
- **Falta pesquisar/escrever**: especificação técnica detalhada (diagramas de componentes, contratos de interface observação/ação/recompensa, escolha concreta de framework de RL e de GNN, formato de dados/versionamento de experimentos); decisões de arquitetura que mereçam ADR formal.

## 4. Experimentos

- **Já coberto no pré-projeto**: cronograma tentativo por semestre (Seção 14), métricas de avaliação definidas (Seção 10), baselines propostos (regras fixas, metaheurísticas, configuração atual de SJC) e intervenção real de referência (Linha Verde) (Seções 8, 11).
- **Falta pesquisar/escrever**: desenho experimental detalhado (protocolo de treino/validação/teste, número de seeds/repetições, cenários de demanda específicos a simular, critérios de parada); construção e calibração efetiva do modelo SUMO do corredor escolhido; definição final do corredor/subárea dentro de SJC.

## 5. Resultados

- **Já coberto no pré-projeto**: nada ainda — é um pré-projeto, sem resultados experimentais.
- **Falta pesquisar/escrever**: todo o capítulo depende da execução dos experimentos (Capítulo 4); inclui apresentação de métricas de tráfego e de ML/engenharia (Seção 10), comparação política aprendida vs. baselines vs. simulação completa, e resultados de generalização entre cenários de demanda.

## 6. Discussão

- **Já coberto no pré-projeto**: riscos e limitações já identificados de forma explícita (Seção 12: dados limitados, validação apenas em simulação, custo computacional, overfitting a um corredor, instabilidade de MARL); compromissos para evitar que o trabalho seja apenas "RL com aplicação ilustrativa" (Seção 11); lista do que evitar (Seção 13).
- **Falta pesquisar/escrever**: interpretação crítica dos resultados reais à luz dessas limitações; discussão sobre generalização para outros corredores/cidades; comparação honesta com a literatura de controle de sinalização (por que alocação estrutural é diferente/mais difícil).

## 7. Conclusão

- **Já coberto no pré-projeto**: contribuição dupla pretendida — engenharia de sistema reprodutível e evidência empírica sobre viabilidade de GNN como surrogate (Seção 11).
- **Falta pesquisar/escrever**: síntese final pós-resultados, trabalhos futuros concretos, avaliação de até que ponto os objetivos específicos (Seção 8) foram atingidos.

## 8. Referências

- **Já coberto no pré-projeto**: lista inicial de 10 referências, incluindo trabalhos de RL/GNN e documentos institucionais de SJC (PlanMob, Plano Diretor, Pesquisa OD) (Seção 16).
- **Falta pesquisar/escrever**: expansão para revisão de literatura completa (Capítulo 2); formatação ABNT/padrão exigido pelo PG/EEC; inclusão de referências de métodos (bibliotecas, frameworks de RL/GNN, SUMO) conforme forem adotadas.
