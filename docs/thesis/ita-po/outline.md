# Esqueleto de capítulos — Dissertação (ITA, PG/PO)

> Esqueleto superficial de capítulos, derivado de `pre-projeto.md`. Não é um rascunho de capítulo — apenas aponta o que já está coberto e o que falta pesquisar/escrever em cada parte. Deve ser revisado com o(a) orientador(a) assim que definido(a).

## 1. Introdução

Cobertura atual: o pré-projeto já traz problema de pesquisa, justificativa, contexto de SJC, recorte geográfico e objetivos (Seções 2–5, 7–8). Boa parte do texto introdutório pode ser adaptado diretamente dessas seções.
Falta: redigir a narrativa de abertura (motivação em prosa, pergunta de pesquisa explícita em uma frase, estrutura da dissertação) e confirmar o corredor exato de estudo antes de fixar o recorte na versão final. TODO(decisão): a confirmação do corredor dependia de disponibilidade de dados de OD por zona; `cities/sjc/data-manifest.yaml` (commit `cd68b57`) marcou a Pesquisa OD (atlas e microdados) como `deferred` — sem ofício às agências de SJC nesta etapa — o que bloqueia esse critério de escolha até nova decisão (ver `progress.md`, entrada 2026-10-24 (3)).

## 2. Revisão de Literatura

Cobertura atual: núcleo de referências já levantado (Miandoabchi et al. 2011/2013, Miandoabchi e Farahani 2010, Verbas et al. 2023, Liu et al. 2023) e a lacuna de pesquisa (surrogate de ML substituindo simulação no laço de otimização bi-nível) já está identificada na Seção 3.
Falta: revisão sistemática mais ampla (não apenas os ~5 trabalhos citados) cobrindo UNDP bi-nível, meta-heurísticas multiobjetivo (NSGA-II e variantes), otimização Bayesiana multiobjetivo, GNNs como surrogate de simulação de tráfego, e trabalhos aplicados a cidades médias/contexto brasileiro. Organizar em quadro comparativo de lacunas.

## 3. Formulação / Metodologia

Cobertura atual: formulação matemática bi-nível multiobjetivo já esboçada (Seção 6: variáveis de decisão, nível superior/inferior, funções objetivo $f_1$–$f_7$, restrições) e metodologia proposta já descrita (Seção 9: SUMO/TraCI, netconvert/netedit, três classes de otimizadores, surrogate GNN com amostragem ativa).
Falta: formalizar a notação de forma definitiva (revisão com orientador), detalhar a arquitetura do surrogate (features de entrada/saída, função de perda, quantificação de incerteza), especificar o protocolo exato de validação cruzada e os critérios de parada dos otimizadores. TODO(evidência): a matriz de demanda $Q$ do nível inferior (Seção 6) depende da Pesquisa OD, hoje `deferred` em `cities/sjc/data-manifest.yaml`; sem ela, a metodologia precisa prever explicitamente um caminho de demanda sintética/indireta como alternativa, não só como risco de rodapé.

## 4. Desenvolvimento

Cobertura atual: nenhum código ou experimento existe ainda (projeto ArterIA está em estágio pré-código, conforme `CLAUDE.md` do repositório); o catálogo de intervenções está descrito em alto nível (Seção 6) e o cronograma tentativo (Seção 14) prevê a sequência de construção.
Falta: tudo — construção e calibração do modelo SUMO do corredor, definição formal e parametrizada do catálogo $\mathcal{I}$, geração do dataset de simulações, implementação do surrogate e dos três otimizadores do nível superior. Este será o capítulo mais extenso e depende de dados (OSM, Pesquisa OD, contagens). TODO(decisão): per `cities/sjc/data-manifest.yaml` (commits `bf374e4`/`cd68b57`), a construção da topologia $G$ tem caminho de autoatendimento viável (OSM/Geofabrik, Geosanja, IBGE Faces de Logradouros), mas a calibração contra contagens de tráfego, planos de tempo semafórico e a Pesquisa OD está `deferred` (sem ofício enviado); o objetivo específico 1 (Seção 8 do pré-projeto) pode precisar ser reescrito para refletir calibração por estimativas indiretas/dados sintéticos como cenário-padrão, não excepcional.

## 5. Resultados

Cobertura atual: métricas de avaliação before/after já definidas (Seção 10: tempo de viagem, atraso, filas, confiabilidade de transporte público, exposição de pedestres/ciclistas, emissões, proxy de risco, acesso de emergência, equidade, custo-benefício).
Falta: todos os resultados empíricos (calibração validada, acurácia do surrogate vs. simulação direta, fronteira de Pareto obtida, comparação de desempenho entre os três otimizadores, análise de sensibilidade) — nada disso existe ainda.

## 6. Discussão

Cobertura atual: limitações e riscos já antecipados (Seção 12: dados incompletos, custo computacional, overfitting do surrogate, viabilidade jurídico-política, erro de especificação do equilíbrio) e contribuições esperadas já articuladas (Seção 11).
Falta: discussão real à luz dos resultados obtidos — em que condições o surrogate foi/não foi confiável, implicações práticas para SJC, comparação com a literatura revisada no Capítulo 2, generalização (ou não) para outros corredores/cidades.

## 7. Conclusão

Cobertura atual: objetivo geral e objetivos específicos já formulados (Seções 7–8), o que facilita redigir a conclusão em espelho a eles; "o que evitar" (Seção 13) já estabelece limites claros do que a dissertação não deve afirmar.
Falta: síntese final pós-resultados, recomendação priorizada de pacote de intervenções para o corredor (Seção 7, objetivo específico 7), agenda de trabalhos futuros (ex.: generalização para a rede completa do município, mencionada na Seção 5 como fora de escopo).

## 8. Referências

Cobertura atual: lista inicial de 11 referências já compilada (Seção 16), incluindo os marcos teóricos de UNDP bi-nível e os documentos normativos/institucionais de SJC (PlanMob, Plano Diretor, Pesquisa OD, FGV, Linha Verde, SUMO).
Falta: expandir substancialmente a partir da revisão sistemática do Capítulo 2; padronizar formato de citação (ABNT ou outro exigido pelo ITA); adicionar literatura primária sobre GNNs em grafos de transporte e sobre NSGA-II/otimização Bayesiana multiobjetivo.
