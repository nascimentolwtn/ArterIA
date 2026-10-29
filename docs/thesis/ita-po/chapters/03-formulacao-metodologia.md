# Capítulo 3 — Formulação e Metodologia

Status: stub (com um rascunho de seção, abaixo). Evidência ainda necessária: notação final revisada por orientador(a); arquitetura do surrogate; protocolo de validação cruzada; contagens reais para a demanda sintética calibrada por contagem; aceite e obtenção efetiva dos dados que alimentam o modelo gravitacional (hoje apenas propostos).

Fonte de fundo: pré-projeto, Seções 6 e 9. A formulação bi-nível ($y \in \{0,1\}^{|\mathcal{I}|}$, $F(y)$, oráculo $\mathcal{L}(y)$) não é reescrita aqui.

## 3.x A rede viária como fonte de incerteza estrutural do nível inferior (RASCUNHO, 2026-10-26)

> RASCUNHO: texto de intenção metodológica. Não contém resultados.

Esta seção sustenta que a rede viária sobre a qual o nível inferior é avaliado deve ser tratada como uma representação com erro, e não como um objeto medido, e que tal erro constitui uma camada de incerteza distinta daquela associada à demanda e à simulação.

No problema bi-nível proposto, o nível inferior é avaliado por simulação microscópica sobre uma rede $G$. Neste trabalho, $G$ é construída a partir de um extrato do OpenStreetMap (OSM) convertido pelo conversor de redes do SUMO; não é, portanto, um objeto medido, mas uma representação com erro. Distinguem-se, assim, ao menos duas camadas de incerteza no oráculo $\mathcal{L}(y)$.

A primeira é a **incerteza estrutural**, própria da rede: omissões e erros de atributo do OSM (sentidos, número de faixas, restrições de conversão), semáforos inferidos automaticamente pelo conversor de redes, quando tal inferência é utilizada, e o efeito de borda do recorte espacial sobre a conectividade e a acessibilidade. A segunda é a **incerteza paramétrica e estocástica**, própria da demanda e da simulação: de um lado, a demanda sintética calibrada por contagem, adotada como caminho metodológico padrão; de outro, a variabilidade entre sementes de simulação, cujo intervalo de confiança entre réplicas é calculado, por ora, por aproximação normal, ressalva que deve acompanhar qualquer intervalo reportado.

A segunda camada tem tratamento previsto no pré-projeto (Seções 9 e 12). A primeira, contudo, só passa a ser observável depois que existe uma rede real, o que ocorreu em 2026-10-26 para o Candidato B (ver Capítulo 4). Adota-se, por isso, uma hipótese de trabalho a ser testada, e não assumida: a ordenação de pacotes de intervenção $y$ é menos sensível ao erro estrutural da rede do que os valores absolutos de $F(y)$. TODO(evidência): nenhuma análise de sensibilidade foi feita.

Três opções de tratamento permanecem em aberto (TODO(decisão), orientador(a)). A primeira trata a rede como fixa e declara a limitação; a segunda conduz uma análise de sensibilidade a variantes da rede, com e sem correções manuais no editor de redes e com e sem semáforos inferidos; a terceira propaga um ensemble de redes ao surrogate como fonte adicional de incerteza. A primeira opção é o ponto de partida, enquanto a segunda e a terceira dependem do custo computacional discutido na Seção 12 do pré-projeto.

Preserva-se, ademais, a fronteira imposta pela decisão de adotar demanda sintética calibrada por contagem: a demanda é um "cenário de tráfego sintético calibrado a fluxos observados", nunca "o tráfego real de São José dos Campos", e alegações de benefício de novos conectores em nível de rede ficam fora do que tal regime de dados sustenta.

À incerteza paramétrica da demanda acrescenta-se, desde 2026-10-29, uma decisão ainda provisória sobre a própria fonte de dados do modelo gravitacional que gera a demanda sintética inicial. Do lado da produção de viagens, propõe-se o uso de agregados populacionais do censo demográfico por setor censitário — a mesma granularidade já antecipada, nesta seção, como caminho possível para redefinir o indicador de equidade da Seção 6 do pré-projeto sem depender de Pesquisa OD; a proposta, contudo, ainda não foi aceita, e o arquivo correspondente ainda não foi obtido, de modo que a questão permanece aberta, agora com um caminho concreto, e não apenas hipotético. Do lado da atração de viagens, por sua vez, propõe-se adotar, como aproximação, a classificação de uso do solo do zoneamento municipal (comercial/institucional/misto versus residencial), na ausência de base pública de empregos acessível sem contato com órgão. Tal aproximação não equivale a uma contagem real de empregos e, portanto, preserva, sem alterar, a restrição já estabelecida de que este regime de dados não sustenta alegações de equidade ancoradas em empregos reais, distintas entre zonas do município.

Dessa forma, a distinção entre as camadas de incerteza não é apenas um cuidado técnico: é a condição para que a fronteira de Pareto obtida possa ser apresentada ao planejamento municipal como evidência com limites declarados, e não como previsão do tráfego real.
