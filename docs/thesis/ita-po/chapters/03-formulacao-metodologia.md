# Capítulo 3 — Formulação e Metodologia

Status: stub (com um rascunho de seção, abaixo). Evidência ainda necessária: notação final revisada por orientador(a); arquitetura do surrogate; protocolo de validação cruzada; contagens reais para a demanda (ADR 0013).

Fonte de fundo: `../pre-projeto.md`, Seções 6 e 9. A formulação bi-nível ($y \in \{0,1\}^{|\mathcal{I}|}$, $F(y)$, oráculo $\mathcal{L}(y)$) não é reescrita aqui.

## 3.x Incerteza estrutural da rede no nível inferior (RASCUNHO, 2026-10-26)

> RASCUNHO: texto de intenção metodológica. Não contém resultados.

No problema bi-nível proposto, o nível inferior é avaliado por simulação microscópica sobre uma rede $G$. Neste trabalho, $G$ é construída a partir de um extrato do OpenStreetMap convertido por `netconvert` (SUMO) e não é um objeto medido: é uma representação com erro. Distinguem-se, portanto, ao menos duas camadas de incerteza no oráculo $\mathcal{L}(y)$:

1. **Incerteza estrutural (da rede):** omissões e erros de atributo do OSM (sentidos, número de faixas, restrições de conversão), semáforos inferidos automaticamente (opção `--tls.guess-signals` do `netconvert`, quando usada) e efeito de borda do recorte espacial sobre conectividade e acessibilidade.
2. **Incerteza paramétrica e estocástica (da demanda e da simulação):** demanda sintética calibrada por contagem (ADR 0013) e variabilidade entre sementes (`arteria/calibration/replication.py`, ver ressalva do IC por aproximação normal em `progress.md`, entrada 2026-10-25 (7)).

A segunda camada tem tratamento previsto no pré-projeto (Seções 9 e 12). A primeira só passa a ser observável depois que existe uma rede real, o que ocorreu em 2026-10-26 para o Candidato B (ver Capítulo 4). Hipótese de trabalho, a ser testada e não assumida: a ordenação de pacotes de intervenção $y$ é menos sensível ao erro estrutural da rede do que os valores absolutos de $F(y)$. TODO(evidência): nenhuma análise de sensibilidade foi feita.

Opções de tratamento a decidir (TODO(decisão), orientador(a)): (a) tratar a rede como fixa e declarar a limitação; (b) análise de sensibilidade a variantes da rede (com e sem correções manuais em `netedit`; com e sem semáforos inferidos); (c) ensemble de redes propagado ao surrogate como fonte adicional de incerteza. A opção (a) é o ponto de partida; (b) e (c) dependem de custo computacional (Seção 12 do pré-projeto).

Fronteira da ADR 0013 (preservada): a demanda é "cenário de tráfego sintético calibrado a fluxos observados", nunca "o tráfego real de São José dos Campos"; alegações de benefício de novos conectores em nível de rede ficam fora do que o regime de dados sustenta.
