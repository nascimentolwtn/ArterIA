# Capítulo 4 — Desenvolvimento

Status: rascunho (apenas a Seção 4.1). Evidência ainda necessária: linha de base calibrada; validador adaptado a redes reais; manifesto de proveniência da execução real; geração do dataset de simulações; surrogate e otimizadores.

Infraestrutura de transformações e catálogo (`apply.py`, `one_way.py` etc.) está descrita em `../outline.md` (Cap. 4) e em `../progress.md`; não é repetida aqui.

## 4.1 Construção e validação da rede (RASCUNHO, 2026-10-26)

> RASCUNHO. Descreve o que foi executado e observado em 2026-10-26 (marco v1.0 do ArterIA, `CHANGELOG.md` [1.0]). Não é linha de base calibrada nem validação de corredor.

### 4.1.1 Cadeia de construção

A cadeia executada no desktop (WSL2, ADR 0014) foi: (i) `arteria studyarea build`: polígono-rascunho por candidato via geocodificação Nominatim, fecho convexo de landmarks e buffer; (ii) `arteria osm fetch --candidate b`: extrato regional Sudeste da Geofabrik recortado com `osmium extract` pelo polígono do Candidato B; (iii) `arteria network build`: conversão PBF para XML por `osmium cat` (necessária porque `netconvert` não lê PBF), seguida de `netconvert` com as opções padrão de importação OSM do SUMO (versão 1.28.0); (iv) inspeção em `sumo-gui` com 1.800 veículos gerados por `randomTrips.py`, tendo sido descartadas 415 viagens inviáveis.

Correções exigidas pela primeira execução real: a incompatibilidade `netconvert`/PBF; três consultas de geocodificação que falhavam ou erravam (uma delas, "Centro", resolvia a cerca de 30 km ao norte do local pretendido). Ambas as classes de falha não eram detectáveis em testes com fixtures, o que ilustra a necessidade de execução contra dados reais como etapa de verificação.

### 4.1.2 Resultado do validador na rede real

`arteria network validate` apontou 729 erros e 7.562 avisos na rede real do Candidato B. A análise dos achados indica que a maior parte é ruído do instrumento, não defeito da rede:

| Verificação | Contagem | Leitura | Ação necessária |
|---|---|---|---|
| `oneway_status` (aviso) | 7.522 (5.448 em arestas internas ":") | falso positivo: `.net.xml` não tem atributo `oneway` | detectar pares de arestas opostas |
| `connectivity` (erro) | 727 | medido a partir de uma única junção inicial em extrato recortado; esperado | análise de componentes fortemente conexos (principal vs. órfãos) |
| `dead_end` (aviso) | 40 | majoritariamente borda do recorte | distinguir borda de beco sem saída real |
| `traffic_light_logic` (erro) | 2 | real; dois clusters de travessia só-bicicleta tipo `traffic_light` sem `<tlLogic>` (2 de 18 junções semafóricas) | impacto na simulação não verificado; revisar em `netedit` |

FIGURA(TODO): captura do `sumo-gui` do Candidato B. Legenda obrigatória: "tráfego sintético não calibrado, fins de verificação visual do pipeline; recorte por fecho convexo mais buffer, não revisado".

Conclusão deste rascunho, limitada ao que as observações sustentam: o validador, afinado em fixtures de brinquedo, não é ainda um instrumento confiável de qualidade para redes reais; as contagens acima não devem ser citadas como medida de qualidade da rede. TODO(evidência): reexecutar após a adaptação do validador e reportar por componente conexo.

### 4.1.3 Etapas de controle ainda não documentadas

- Revisão manual em `netedit` contra imagem de satélite/OSM: não realizada ou não documentada. TODO(evidência).
- Semáforos inferidos: a quantidade de junções semafóricas (18) inclui as geradas por inferência? Não verificado. TODO(evidência).
- Proveniência (`arteria/provenance.py`): TODO(evidência) confirmar que a execução registrou hash do extrato, versão do SUMO (1.28.0) e flags do `netconvert` em `manifest.json`.
- Extensão do domínio: ver 4.1.4 (decidida pela ADR 0016 em 2026-10-26).

### 4.1.4 Rede única de SJC e validador adaptado (RASCUNHO, 2026-10-26)

A ADR 0016 (`docs/adr/0016-unified-sjc-network.md`, Accepted) decide construir uma única rede de SJC, recortada pelo envelope retangular dos polígonos de todos os candidatos, com B, D, C e A como áreas de avaliação nomeadas (conjuntos de arestas e, depois, TAZs). Justificativa declarada: os polígonos não são independentes (B e C tocam A; D está a cerca de 0,3 km de A), e recortar cada um isoladamente corta fluxos de passagem em fronteiras arbitrárias. Alternativa considerada: redes por candidato, mantidas apenas para checagens visuais, sem servir de base de resultados.

Medidas reportadas na ADR (construção padrão `osmium extract` + `netconvert`, SUMO 1.28), maior componente fortemente conexo: B, 2.074 arestas, 85,1%; D, 1.203, 69,9%; C, 919, 86,9%; A, 2.256, 88,3%; envelope, 11.035 arestas, 94,0%. A rede única tem cerca de 1,7 vez a soma das quatro redes por polígono e, portanto, simulações mais lentas; a ADR admite uma rede derivada menor se isso prejudicar o laço do otimizador. Persistem becos sem saída de borda e uma cauda não roteável de 6%.

O commit `72ab33e` adapta `arteria network validate` a redes reais (componentes fortemente conexos, pares de arestas opostas no lugar de `oneway`, becos sem saída de borda). Segundo o relato do commit, os 729 erros da rede B caem a 0. Leitura cautelosa: isso demonstra que o instrumento deixou de produzir os achados espúrios da Seção 4.1.2, não que a rede esteja livre de defeitos; os 2 casos de `traffic_light_logic` e a cauda não roteável devem ser reavaliados. TODO(evidência): reexecutar sobre a rede única e reportar estatística por componente.

Ambiente computacional: `docs/local/dev-pc-benchmark.md` (commit `814f4c9`) registra o PC de desenvolvimento (6 núcleos/12 threads, 9,7 GiB de RAM) e estima 35 a 45 h para um NSGA-II de 10 mil execuções, tido como inviável localmente; adota-se lote por sementes com 4 workers. Valores extraídos do relato do commit; TODO(evidência): conferir o documento antes de citar números. `nox -s smoke` passa com SUMO real (`eclipse-sumo`, commit `ffcbd8e`): teste de fumaça, não validação.
