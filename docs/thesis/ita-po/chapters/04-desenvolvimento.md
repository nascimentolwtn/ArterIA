# Capítulo 4 — Desenvolvimento

Status: rascunho (Seções 4.1 e 4.2). Evidência ainda necessária: linha de base calibrada; validador adaptado a redes reais; manifesto de proveniência da execução real; dados de população e de atração de viagens que alimentam o modelo gravitacional (hoje apenas propostos); geração do dataset de simulações; surrogate e otimizadores.

A infraestrutura de transformações de rede e do catálogo de intervenções está descrita no esqueleto de capítulos (Cap. 4) e no log de progresso da trilha; não é repetida aqui.

## 4.1 A rede-base de São José dos Campos: construída e verificada, mas ainda não calibrada (RASCUNHO, 2026-10-26)

> RASCUNHO. Descreve o que foi executado e observado a partir de 2026-10-26 (marco v1.0 do ArterIA). Não é linha de base calibrada nem validação de corredor.

Esta seção argumenta que a rede-base de São José dos Campos, derivada do OpenStreetMap (OSM), acumulou entre 2026-10-26 e 2026-10-28 evidências convergentes, ainda que preliminares, de construção reprodutível e de consistência geométrica, sem constituir, contudo, linha de base calibrada nem validação de demanda. Para sustentar tal argumento, examinam-se sucessivamente a cadeia de construção, o comportamento do validador em rede real, a adoção de uma rede única para o município, a representação dos corredores, a reprodutibilidade do processo de construção e o confronto com fontes públicas externas.

### 4.1.1 A primeira execução real revela falhas invisíveis em testes

A cadeia executada na estação de trabalho local (ambiente Linux sobre Windows, WSL2) compreendeu quatro etapas. Na primeira, delimitou-se um polígono-rascunho por candidato, por meio da geocodificação de pontos de referência no serviço Nominatim, do fecho convexo desses pontos e da aplicação de um buffer. Na segunda, um extrato regional do Sudeste disponibilizado pela Geofabrik foi recortado pelo polígono do Candidato B com a ferramenta osmium. Na terceira, o extrato foi convertido do formato binário PBF para XML — conversão necessária porque o conversor de redes do SUMO não lê PBF — e, em seguida, transformado em rede de simulação com as opções padrão de importação OSM do SUMO, versão 1.28.0. Por fim, a rede foi inspecionada na interface gráfica do simulador com 1.800 veículos gerados aleatoriamente pelo gerador de viagens do próprio SUMO, tendo sido descartadas 415 viagens inviáveis.

A primeira execução real exigiu correções de duas classes: a incompatibilidade entre o conversor de redes e o formato PBF e três consultas de geocodificação que falhavam ou erravam — uma delas, "Centro", resolvia a cerca de 30 km ao norte do local pretendido. Observa-se que nenhuma das duas classes de falha era detectável em testes com dados fictícios, o que ilustra a necessidade de execução contra dados reais como etapa de verificação.

### 4.1.2 O validador em rede real mede o instrumento, não a rede

O validador de boa formação apontou 729 erros e 7.562 avisos na rede real do Candidato B. A análise dos achados indica, contudo, que a maior parte é ruído do instrumento, e não defeito da rede, como sintetiza a tabela a seguir.

| Verificação | Contagem | Leitura | Ação necessária |
|---|---|---|---|
| Sentido único (aviso) | 7.522 (5.448 em arestas internas de junção) | falso positivo: o formato de rede do SUMO não possui atributo explícito de sentido único | detectar pares de arestas opostas |
| Conectividade (erro) | 727 | medida a partir de uma única junção inicial em extrato recortado; esperado | análise de componentes fortemente conexos (principal vs. órfãos) |
| Becos sem saída (aviso) | 40 | majoritariamente borda do recorte | distinguir borda de beco sem saída real |
| Lógica semafórica (erro) | 2 | real; dois agrupamentos de travessia exclusiva de bicicletas classificados como semafóricos sem programa semafórico definido (2 de 18 junções semafóricas) | impacto na simulação não verificado; revisar no editor de redes |

FIGURA(TODO): captura da interface gráfica do SUMO com o Candidato B. Legenda obrigatória: "tráfego sintético não calibrado, fins de verificação visual do pipeline; recorte por fecho convexo mais buffer, não revisado".

Conclui-se, nos limites do que as observações sustentam, que o validador, afinado em redes de teste de pequeno porte, não é ainda um instrumento confiável de qualidade para redes reais; as contagens acima não devem, portanto, ser citadas como medida de qualidade da rede. TODO(evidência): reexecutar após a adaptação do validador e reportar por componente conexo.

### 4.1.3 Etapas de controle ainda não documentadas

Restam, ainda, etapas de controle sem documentação. A revisão manual no editor de redes, contra imagem de satélite e contra o próprio OSM, não foi realizada ou não foi documentada (TODO(evidência)). Tampouco se verificou se as 18 junções semafóricas incluem as geradas por inferência automática (TODO(evidência)). Quanto à proveniência, falta confirmar que a execução registrou a identificação criptográfica do extrato, a versão do SUMO (1.28.0) e as opções de conversão no manifesto de proveniência (TODO(evidência)). A extensão do domínio, por sua vez, é tratada na Seção 4.1.4, tendo sido decidida em 2026-10-26.

### 4.1.4 Uma rede única preserva os fluxos entre áreas vizinhas (RASCUNHO, 2026-10-26)

Decidiu-se, em 2026-10-26, construir uma única rede de SJC, recortada pelo envelope retangular dos polígonos de todos os candidatos, com B, D, C e A como áreas de avaliação nomeadas — conjuntos de arestas e, posteriormente, zonas de análise de tráfego (TAZ). A justificativa declarada é que os polígonos não são independentes: B e C tocam A, e D está a cerca de 0,3 km de A, de modo que recortar cada um isoladamente cortaria fluxos de passagem em fronteiras arbitrárias. A alternativa considerada, redes por candidato, foi mantida apenas para checagens visuais, sem servir de base de resultados.

Os registros dessa decisão reportam, para a construção padrão (recorte com osmium e conversão pelo SUMO 1.28), as medidas do maior componente fortemente conexo sintetizadas a seguir.

| Rede | Arestas | Fração no maior componente fortemente conexo |
|---|---|---|
| B | 2.074 | 85,1% |
| D | 1.203 | 69,9% |
| C | 919 | 86,9% |
| A | 2.256 | 88,3% |
| Envelope (rede única) | 11.035 | 94,0% |

A rede única tem cerca de 1,7 vez a soma das quatro redes por polígono e, portanto, simulações mais lentas; admite-se, por isso, uma rede derivada menor, caso tal custo prejudique o laço do otimizador. Persistem, ademais, becos sem saída de borda e uma cauda não roteável de 6%.

Em seguida, o validador foi adaptado a redes reais, passando a analisar componentes fortemente conexos, pares de arestas opostas no lugar de um atributo de sentido único e becos sem saída de borda. Segundo o relato da alteração, os 729 erros da rede B caem a zero. Tal resultado, lido com cautela, demonstra que o instrumento deixou de produzir os achados espúrios da Seção 4.1.2, e não que a rede esteja livre de defeitos; os dois casos de lógica semafórica e a cauda não roteável devem ser reavaliados. TODO(evidência): reexecutar sobre a rede única e reportar estatística por componente.

Quanto ao ambiente computacional, o registro de desempenho da estação de desenvolvimento (6 núcleos/12 threads, 9,7 GiB de RAM) estima de 35 a 45 h para um NSGA-II de 10 mil execuções, tido como inviável localmente; adota-se, assim, o processamento em lotes por sementes com 4 processos paralelos. Tais valores foram extraídos do relato da alteração; TODO(evidência): conferir o documento antes de citar números. Além disso, o teste de fumaça automatizado passa com o SUMO real — o que constitui teste de fumaça, não validação.

### 4.1.5 Os corredores tornam-se sequências de arestas na rede única (RASCUNHO, 2026-10-27)

Os candidatos A, C e D, uma linha central de B derivada pelo mesmo método (B nunca teve definição em nível de aresta, existindo apenas como polígono) e uma ligação A-B foram desenhados como sequências ordenadas de arestas do SUMO sobre a rede única. Segundo a documentação do método, pontos de passagem do OSM são ajustados à aresta de veículos de passageiros mais próxima e unidos por menor caminho dirigido, em cada sentido, com custo igual ao comprimento, multiplicado por 8 fora das ruas preferidas e por 1,5 em rampas sem nome; mãos únicas e conversões ausentes são, portanto, respeitadas. Relata-se que nenhuma perna ficou inroteável e que a ligação A-B tem 883 m de A para B e 1.286 m de B para A, assimetria decorrente de rampas de mão única.

Em 2026-10-27, os polígonos de B (de 5,31 para 7,67 km²) e de C (de 1,54 para 4,17 km²) foram estendidos, e a rede única reconstruída passou a ter 14.225 arestas e 6.655 junções, com 93,1% das junções no componente principal e nenhum erro de validação. Observa-se que tal porcentagem é calculada por junções e não é comparável à da Seção 4.1.4, calculada por arestas no maior componente fortemente conexo. Os identificadores de arestas, ademais, mudam a cada reconstrução.

Ainda em 2026-10-27, conforme o registro de alterações do projeto, o responsável conferiu os corredores A, B, C e D, a ligação A-B e as áreas estendidas de B e C contra imagem aérea (Google Earth), considerando-os adequados "por ora", inclusive a extensão de C a oeste/sudoeste. Tal verificação supera as ressalvas originais (i), geometria não verificada, e (ii), direção de C não confirmada, com a cautela de que se trata de verificação visual por um único avaliador, sem registro de critério nem de evidência arquivada nesta trilha, e de que a aprovação diz respeito à geometria, não à demanda nem ao desempenho.

Permanecem vigentes, contudo, três ressalvas. A ressalva (iii) lembra que C é uma área (labirinto de mão única) e D é uma junção, de modo que as sequências são leituras defensáveis, não delimitações. A ressalva (iv) registra que a completude de atributos foi medida apenas no candidato B — vias principais bem etiquetadas; ruas residenciais com número de faixas informado em cerca de 4% e velocidade máxima em cerca de 5% —, de modo que, nessas vias, capacidade e velocidade resultam de valores padrão do conversor de redes. A ressalva (v), por fim, assinala que GeoSanja e IBGE não haviam sido confirmados como fontes. TODO(evidência): documentar o método de medição da completude de atributos; registrar o critério da checagem aérea; associar a identificação criptográfica do arquivo de rede aos identificadores de arestas no manifesto (ver 4.1.6, que fixa a identificação por conteúdo). Figuras que usem estes corredores devem declarar "geometria derivada de OSM, verificada visualmente pelo responsável em 2026-10-27; não é validação de demanda".

(Nota de leitura: a Seção 4.1.4 cita 11.035 arestas e 94,0% no maior componente fortemente conexo; tais números descrevem a rede anterior à extensão de B e C e são mantidos por histórico. A rede vigente tem 14.225 arestas e 6.655 junções.)

### 4.1.6 A construção da rede é determinística e auditável (RASCUNHO, 2026-10-27; trabalho ainda não incorporado ao repositório na data da redação)

Este rascunho apoia-se no registro de alterações do projeto e no relato do responsável; o código e os arquivos de fixação do insumo existiam na cópia de trabalho, mas não foram lidos na elaboração do texto. Segundo tais fontes, o insumo OSM passa a ser fixado por um retrato (snapshot) do extrato Geofabrik Sudeste, em formato PBF de 2026-10-25, com a identificação criptográfica (sha256) do arquivo-fonte e do extrato recortado da cidade; a obtenção de dados recusa fonte ou extrato divergente do fixado, e a refixação exige ação deliberada.

O procedimento de reconstrução, por sua vez, verifica o retrato, recorta o extrato, executa o conversor de redes, valida, compara o resultado com a rede de referência fixada e grava um registro de proveniência. A comparação usa uma identificação por conteúdo que ignora o comentário de data e hora inserido pelo conversor, de modo que a identificação bruta do arquivo muda a cada construção, ao passo que a de conteúdo permanece estável. Relata-se, ainda, uma execução real em bancada: a rede reconstruída é idêntica à existente (14.225 arestas), uma segunda execução a reproduziu, a validação registrou 0 erros e 127 avisos (becos sem saída, junções semafóricas sem uso, 93,1% das junções no componente principal) e o tempo foi de cerca de 16 s.

De modo complementar, uma ferramenta de comparação entre redes lista arestas, faixas e junções adicionadas, removidas ou alteradas, em formato estruturado e textual; como demonstração de sanidade, a rede antiga, restrita a B, comparada à rede unificada, resulta em 12.175 arestas adicionadas, 24 removidas e 137 alteradas (relato). As correções manuais, por sua vez, serão mantidas como pequenos arquivos de correção em XML simples, registrados numa lista própria e aplicados por uma segunda passada do conversor, uma vez que o SUMO 1.28 não oferece opção nativa de correção; nenhuma correção foi necessária até agora, de modo que o mecanismo não foi exercido sobre um caso real. Um teste apenas de bancada confere que toda aresta de corredor existe na rede construída.

Por fim, nenhum feed público GTFS de SJC foi encontrado, de modo que a camada de transporte público está adiada. Tal ausência limita a avaliação de objetivos de transporte coletivo (por exemplo, a confiabilidade de ônibus, Seção 10 do pré-projeto) a dados ainda inexistentes.

Interpreta-se tal reprodutibilidade com cautela: significa que o mesmo retrato e as mesmas opções geram a mesma rede — determinismo da construção em duas execuções, numa única máquina e numa única versão do SUMO, a 1.28 —, e não implica que a rede represente a realidade, nem que seja robusta a mudanças do OSM. Atualizar o retrato torna-se, assim, uma decisão explícita que gera uma comparação auditável. TODO(evidência): confirmar a leitura do código e dos arquivos de fixação; testar a reprodutibilidade em outra máquina/versão do SUMO; medir o impacto de mudanças do OSM sobre a rede e sobre os identificadores de arestas.

### 4.1.7 O confronto com fontes públicas externas corrobora a geometria da rede (RASCUNHO, 2026-10-28)

Este rascunho apoia-se no relato do responsável sobre a alteração que introduziu o confronto (cross-check); o código e as saídas geradas, mantidas fora do controle de versão, não foram lidos na elaboração do texto. Dois novos procedimentos comparam a rede OSM/SUMO contra duas fontes públicas de referência registradas no manifesto de dados da cidade — a Base de Faces de Logradouros do IBGE (2022) e as camadas de arruamentos e de Hierarquia Viária do GeoSanja, da prefeitura — dentro de um buffer de 50 m em torno da união dos polígonos dos quatro corredores, e geram representações cartográficas da rede.

O método relatado combina dois casamentos. O primeiro é por nome de rua normalizado (sem acento, espaço ou prefixo de tipo de via) entre arestas OSM e segmentos do IBGE. O segundo é geométrico: o centro de linha das arestas OSM é amostrado a cada 5 m, mede-se a distância ao segmento IBGE de mesmo nome e calcula-se a fração de cobertura dentro de um limiar de 15 m contra o GeoSanja, sem exigência de nome igual.

Os resultados reportados, reprodutíveis pelo procedimento, mas não armazenados como dado e, portanto, não verificados nesta trilha, indicam 543 nomes de rua coincidentes entre OSM e IBGE nos corredores (167 apenas no OSM, 201 apenas no IBGE), distância mediana entre amostra e referência de cerca de 3,0 m e 6,4% das amostras acima do limiar de 15 m. Verifica-se, ainda, que 81,5% do comprimento de centro de linha do OSM está a até 15 m do GeoSanja e que 97,2% do GeoSanja está a até 15 m do OSM. O próprio relato atribui parte dos descasamentos de mediana alta a nomes de rua genéricos ou reutilizados (por exemplo, "Rua Dois", "Viela Três"), que produzem falsos casamentos de nome entre ruas distintas, não necessariamente erro de geometria. Foram geradas, também, representações cartográficas da rede por prioridade de aresta do SUMO, com os contornos das quatro áreas de estudo, igualmente não armazenadas.

Registrou-se, na ocasião, uma questão aberta: os nomes de rua do OSM apresentavam um artefato de escape duplo da entidade XML de apóstrofo, afetando algumas dezenas de nomes (por exemplo, "D'Ávila"), com origem suspeita no conversor de redes ou em etapa posterior. Tal artefato não afetava geometria nem topologia, apenas a cadeia de texto do nome, mas precisaria ser resolvido antes de citar nomes de rua em figuras ou tabelas desta dissertação.

**Atualização 2026-10-28.** A questão acima foi diagnosticada e corrigida, conforme relato do responsável (código e testes não lidos nesta trilha). A causa raiz é um defeito do próprio conversor de redes, confirmado com um caso mínimo isolado executado contra o binário real, que escapa duas vezes qualquer caractere especial de XML (apóstrofo, e comercial, aspas, sinais de menor e maior) presente no nome de uma via do OSM. A correção passa a ser aplicada automaticamente após toda conversão, tanto na construção quanto na reconstrução da rede, ajustando os atributos de nome e de identificador de origem na rede gravada. A rede real de SJC foi reconstruída com a correção, e o retrato fixado (Seção 4.1.6) foi repontado para a identificação de conteúdo da rede corrigida. Relata-se que 58 caracteres foram corrigidos em exatamente 3 nomes de rua (por exemplo, "Rua Armando D'Oliveira Cobra"), sem alteração estrutural da rede — nenhuma aresta, faixa ou junção adicionada, removida ou alterada —, permanecendo a validação com 0 erros e 127 avisos. O confronto com IBGE e GeoSanja foi reexecutado contra a rede corrigida: os nomes coincidentes passaram de 543 para 544 (um dos três nomes corrigidos passou a casar corretamente com o IBGE), os exclusivos do OSM de 167 para 166 e os exclusivos do IBGE de 201 para 200, enquanto os números de geometria (mediana de cerca de 3,0 m, 6,4% acima de 15 m, coberturas de 81,5% e 97,2% em relação ao GeoSanja) permaneceram essencialmente inalterados. A correção foi publicada na versão 1.3 do ArterIA.

Cabe, contudo, uma leitura cautelosa. Trata-se de um confronto de triagem, com casamento de nome deliberadamente grosseiro, e não de calibração: mede completude e cobertura geométrica contra duas fontes externas independentes, não capacidade, demanda nem desempenho. Constitui, assim, evidência adicional, de tipo diferente das Seções 4.1.2 a 4.1.6 (validador interno, completude de atributos, verificação aérea, reprodutibilidade da construção), a favor da qualidade geométrica da rede-base antes de uma linha de base calibrada; os números acima, tanto os originais quanto os da atualização de 2026-10-28, provêm, porém, apenas de relato, ainda não lido em código nem reproduzido nesta trilha. O artefato de apóstrofo, antes um risco a vigiar, está encerrado: os nomes de rua da rede de SJC podem agora ser citados diretamente em figuras e tabelas, sujeitos à ressalva geral de não leitura do código. TODO(evidência): ler o código do confronto, das representações cartográficas e da correção de nomes, bem como uma amostra das saídas; avaliar se a camada de Hierarquia Viária do GeoSanja pode informar os atributos de capacidade e velocidade ainda ausentes nas vias residenciais (Seção 4.1.5, ressalva iv).

### 4.1.8 Síntese e limitações da seção (RASCUNHO, 2026-10-28)

O primeiro argumento desta seção mostrou que a execução contra dados reais revela falhas que testes com dados fictícios não detectam. O segundo evidenciou que o validador original media mais o próprio instrumento do que a rede, e que sua adaptação eliminou achados espúrios sem atestar a ausência de defeitos. O terceiro justificou a rede única como forma de preservar os fluxos entre áreas vizinhas; o quarto e o quinto mostraram, respectivamente, que os corredores passaram a existir em nível de aresta, com verificação visual, e que a construção da rede se tornou determinística e auditável. O sexto, por fim, apresentou o confronto com fontes externas como evidência, de natureza distinta, a favor da consistência geométrica da rede.

A limitação central da seção é que boa parte dos números citados provém de relato, ainda não reproduzido nem lido em código nesta trilha, e que nenhuma das verificações alcança capacidade, demanda ou desempenho de tráfego. As pendências de evidência estão registradas nos marcadores de cada subseção e constituem o trabalho imediato desta etapa.

Dessa forma, a rede-base deixa de ser uma caixa-preta e passa a ser um objeto com proveniência, verificações e limites declarados — condição necessária para que as recomendações futuras do sistema de apoio à decisão possam ser auditadas pelo planejamento municipal.

## 4.2 A delimitação por zonas de análise de tráfego inicia a geração de demanda (RASCUNHO, 2026-10-29)

Esta seção sustenta que a geração da demanda sintética, primeiro passo de implementação do caminho metodológico já decidido na Seção 3.x, começou por reaproveitar a geometria das áreas de estudo já verificada para os corredores, em vez de desenhar uma nova delimitação, e que tal reaproveitamento transporta para o lado da demanda as mesmas cautelas já registradas para essa geometria no Capítulo 4.1.

O modelo gravitacional que gera a demanda sintética inicial exige que a rede seja particionada em zonas de análise de tráfego, unidade padrão de agregação de origens e destinos em simulação de tráfego. Cada uma das quatro áreas de avaliação (B, D, C e A) passou a corresponder a uma zona, e toda aresta fora das quatro áreas foi agrupada numa zona residual, que representa o tráfego de passagem e o restante do envelope da rede única. A atribuição de cada aresta à sua zona segue um teste de pertencimento geométrico do ponto médio da aresta a cada polígono, exportado no formato padrão de zonas de análise de tráfego do simulador.

Uma execução real contra a rede vigente de São José dos Campos confirma a cobertura da partição, sintetizada na tabela a seguir.

| Zona | Arestas |
|---|---|
| B (Av. Andrômeda <-> DCTA / Jardim Satélite) | 3.020 |
| C (Centro / São Dimas / Vila Adyana) | 1.786 |
| A (Anel Viário) | 1.146 |
| D (Jardim Colinas / Ponte Estaiada) | 1.103 |
| Residual (tráfego de passagem) | 7.170 |
| **Total** | 14.225 |

O total coincide com o número conhecido de arestas da rede única (Seção 4.1.5), e nenhuma zona permanece vazia — ao contrário das evidências citadas nas Seções 4.1.5 a 4.1.7, este resultado foi conferido diretamente nesta rodada, e não apenas relatado.

Permanecem, contudo, três ressalvas. A primeira é que esta etapa só fixa geometria, sem ainda atribuir peso de produção ou de atração de viagens a cada zona — o modelo gravitacional propriamente dito depende de uma decisão de dados ainda não aceita, discutida na Seção 3.x. A segunda é que os quatro polígonos reaproveitados herdam as cautelas já registradas na Seção 4.1.5: a verificação aérea foi feita por um único avaliador, sem critério arquivado; a área C é um labirinto de mão única, não uma linha; e a área D é uma junção, não um corredor — de modo que a zona correspondente a cada uma delas é uma leitura defensável da geometria de avaliação, não uma delimitação administrativa de zoneamento. A terceira é que a zona residual concentra a maior parte das arestas da rede (7.170 de 14.225, pouco mais da metade), o que antecipa que qualquer agregação de resultados restrita às quatro áreas nomeadas deixará de fora a maior parte da rede em número de arestas — ainda que não necessariamente em volume de viagens, hoje desconhecido.

Conclui-se, portanto, que a camada de zonas fixa apenas a geometria da futura demanda, não a incerteza associada a ela: enquanto os pesos de produção e atração não forem obtidos e aceitos, a geração de demanda permanece uma etapa de infraestrutura, não um cenário calibrado. Tal distinção, lida em conjunto com a Seção 3.x, reforça que cada camada do modelo — rede, zoneamento, peso de viagem, simulação — precisa ter seus próprios limites declarados antes que qualquer resultado seja apresentado ao planejamento municipal como evidência.
