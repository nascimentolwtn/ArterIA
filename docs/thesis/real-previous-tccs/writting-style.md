# Estilo de redação do autor (Luiz Wagner Tavares Nascimento)

Extraído de dois trabalhos de conclusão de curso do próprio autor presentes nesta pasta:

- `046_LUIZ NASCIMENTO_LuizWagnerTavaresNascimento_TCC.pdf` — ensaio acadêmico EAOAR/COMAER, 2025, "Inteligência artificial na gestão do conhecimento: rumo à prontidão operacional" (13 páginas). **Este é o modelo principal a seguir**: é o trabalho mais recente, no registro mais próximo de uma dissertação de mestrado (ensaio argumentativo, sem código/figuras técnicas).
- `TCC_LuizWagner_FinalCD.pdf` — TCC de especialização ITA, 2009, "Um ambiente para integração de processos em uma fábrica de software utilizando uma arquitetura orientada a serviços" (119 páginas). Útil para o tom de voz e conectivos, mas **não** para o nível de detalhe: é um TCC de engenharia com capítulos de implementação, prints de tela, código-fonte em apêndice — gênero diferente do que se espera de uma dissertação.

- `[TCC] - Aline Aparecida Buzato Borges Nascimento_posBanca_rev3.pdf` — TCC de MBA USP/ESALQ, 2023, "Aspectos essenciais do planejamento estratégico para implantação da gestão da inovação em empresas de tecnologia" (20 páginas). A autoria de conteúdo é de Aline Nascimento, mas a redação foi feita com apoio de Luiz Wagner e a revisão foi majoritariamente dele — por isso entra como **fonte complementar**: não define o registro geral (a seção 10 trata das técnicas específicas que vale incorporar), mas confirma e complementa os padrões já extraídos dos outros dois trabalhos.

## Diagnóstico do problema atual

Os capítulos de tese gerados pelos agentes (`thesis-ita-po`, `thesis-ita-eec`, `thesis-ita-ppgao`, `thesis-unifa-ppgca`) estão técnicos demais: citam arquivos, trechos de código, comandos de linha de comando. Isso é o registro de um **README de engenharia de software**, não o de uma **dissertação de mestrado**. O ensaio EAOAR de 2025 é a prova de que o próprio autor já escreve no registro certo quando o gênero exige — é esse registro que os agentes devem reproduzir.

## Regras de redação (aplicar em todos os capítulos de tese)

### 1. Nunca mencionar implementação ao nível de código
Proibido: nomes de arquivo, caminhos, comandos de shell/CLI, flags, nomes de funções/classes, snippets de código, nomes de branches/commits. Ferramentas e métodos (SUMO, `netconvert`, TraCI, algoritmos de otimização) são citados **no nível conceitual** — o que fazem e por quê foram escolhidos — nunca como "como rodar" ou "qual arquivo editar". Esse tipo de detalhe pertence ao código/ADRs do repositório, não à dissertação.

### 2. Voz impessoal, terceira pessoa, norma culta
Nunca "eu fiz/decidi/implementei". Usar construções impessoais e de voz passiva analítica: "observa-se que", "verifica-se que", "argumenta-se que", "conclui-se que", "pode-se obter", "foi possível", "constatou-se". Primeira pessoa do plural ("propõe-se", "adotou-se") é aceitável para descrever decisões metodológicas do próprio trabalho, mas a análise e a argumentação são sempre na voz impessoal.

### 3. Teses estabelecidas no início de cada seção/capítulo (padrão tese-argumento-conclusão)
No ensaio de 2025, o Resumo e a Introdução afirmam a tese explicitamente ("Este trabalho defende a aplicação de... Para sustentar essa tese, argumenta-se que... Adicionalmente...") antes de qualquer desenvolvimento. Cada subseção do corpo corresponde a **um argumento**, com título que nomeia o argumento (não a ferramenta usada). A Conclusão recapitula a tese e resume cada argumento num parágrafo próprio ("O primeiro argumento demonstrou que...", "O segundo argumento evidenciou que..."), e fecha com uma frase de alcance institucional/estratégico (ex.: "habilitando a FAB a atuar na vanguarda da GC").

Aplicar o mesmo padrão: declarar a tese do capítulo/seção na abertura, um argumento por subseção, fechar recapitulando e subindo o nível de abstração (implicação prática/institucional), nunca terminando num detalhe técnico.

### 4. Citação integrada à prosa, nunca como lista solta de referências
Padrão de citação do autor:
- Atribuição explícita antes ou depois da ideia: "Segundo X (ano)...", "X evidencia que...", "Conforme a pesquisa de X (ano)...", "Como respaldo quantitativo, uma meta-análise (X; Y, ano) constatou que...".
- Citação direta traduzida quando o original é em inglês, sempre com "(Autor, ano, p. N, tradução própria)".
- Números/estatísticos da literatura são trazidos para reforçar o argumento (ex.: "elevam o desempenho entre 20% a 25%"), não para decorar o texto.
- Cada citação serve ao argumento da seção — nunca aparece "solta", sem conectá-la à tese do parágrafo.

### 5. Parágrafos curtos, uma ideia por parágrafo, conectivos fortes
Parágrafos de 3 a 7 linhas, recuo de primeira linha, separados por linha em branco. Transições e conectivos recorrentes do autor: "Contudo,", "Entretanto,", "Ademais,", "Além disso,", "Assim,", "Dessa forma,", "Nesse contexto,", "Diante desse contexto,", "De modo complementar,", "Por exemplo,". Frases longas com subordinação ("embora... resulta em...", "à medida que...", "tendo em vista que...") são a norma, não a exceção — mas cada frase ainda carrega uma ideia controlável.

### 6. Sem listas com marcadores no corpo argumentativo
O ensaio de 2025 (gênero mais próximo da dissertação) não usa bullet points em nenhum momento — tudo é prosa corrida. Listas com marcadores só aparecem no TCC de 2009 em seções enumerativas de requisitos/premissas (gênero de relatório técnico). **Para os capítulos de dissertação, evitar bullet points**; preferir prosa encadeada mesmo ao enumerar itens ("primeiro..., em segundo lugar..., por fim...").

### 7. Siglas definidas na primeira ocorrência, glossário só quando necessário
Sigla sempre apresentada por extenso + sigla entre parênteses na primeira menção ("gestão do conhecimento (GC)"), depois usada apenas na forma abreviada. Um glossário formal (como no TCC de 2009) só se justifica em trabalhos com forte carga de jargão técnico-operacional específico; nos capítulos de dissertação, preferir a definição embutida no texto corrido.

### 8. Uso de "tal" como recurso coesivo
Tique estilístico recorrente: "tal diretriz", "tal fato", "tal abordagem", "tal análise" — retomando algo já dito sem repetir o substantivo completo. Pode ser reproduzido com moderação para dar coesão sem redundância.

### 9. Fechamento sempre em nível estratégico/institucional
As conclusões nunca terminam num resultado técnico isolado; sempre sobem um nível de abstração para a implicação prática, institucional ou de política pública do achado. Replicar isso ao final de cada capítulo de dissertação: a última frase aponta para o significado mais amplo do argumento, não para um detalhe de implementação.

## O que SIM pode aparecer (com moderação, fora do corpo argumentativo)
- Figuras/diagramas conceituais (arquitetura, fluxo, modelo) — como no TCC de 2009 — são aceitáveis quando ilustram um modelo ou resultado, não um passo de implementação.
- Tabelas de dados/resultados quantitativos.
- Código-fonte, scripts e comandos pertencem a apêndices técnicos ou ao próprio repositório de código — nunca ao corpo dos capítulos da dissertação.

## 10. Elementos complementares (do TCC coescrito/revisado com Aline Nascimento)

Este TCC segue o formato de artigo científico (Resumo/Abstract bilíngue, Introdução, Material e Métodos, Resultados e discussão, Considerações Finais, Agradecimentos, Referências, Apêndice) em vez do formato ensaio-argumentativo do EAOAR 2025. Mesmo assim, confirma vários padrões já listados e acrescenta técnicas úteis para capítulos empíricos/comparativos (ex.: comparação entre trilhas, estudos de caso de cidades, cenários de intervenção):

- **Subseções de estudo de caso com estrutura interna repetida.** Cada "Estudo de Caso – X" segue a mesma sequência: contexto da empresa/caso → prática/método adotado → estrutura de equipe/organização → papel da liderança/cultura → frase de síntese fechando com a citação da fonte entre parênteses. Usar esse molde ao comparar múltiplos casos (cidades, cenários, trilhas): mesma ordem de informação em cada subseção, para facilitar a comparação pelo leitor.
- **Citação de fechamento por parágrafo/subseção.** Quando todo um parágrafo ou subseção resume um único estudo de caso, a citação da fonte vem ao final, ancorando a síntese inteira — não apenas a última frase isoladamente.
- **Tabela de síntese comparativa é aceitável (e recomendada) para cruzar categorias.** A "Tabela 2" cruza tendências identificadas nos casos com as diretrizes da norma ISO 56002. Isso não contradiz a regra 6 (nada de bullet points no corpo argumentativo): tabelas de síntese comparativa (categoria × categoria, achado × referencial teórico) são um recurso diferente de lista e devem ser usadas quando há mais de ~3 itens a cruzar com uma mesma dimensão de análise.
- **Listas numeradas/com letras são aceitáveis quando reproduzem uma estrutura já enumerada por uma fonte citada** (ex.: "três condições de Drucker (2007): I) ... II) ... III)"; "quatro aspectos: a) ... b) ... c) ... d)"). É uma exceção pontual à regra 6, não uma licença geral para usar listas como atalho de redação própria.
- **Seção de Método com transparência metodológica explícita.** "Material e Métodos" descreve a fonte dos dados, o instrumento de coleta, o tamanho da amostra e a taxa de resposta sem embelezamento (ex.: "houve apenas um respondente... e este não respondeu ao tema 9"). Honestidade metodológica direta, sem inflar a robustez do dado coletado.
- **Parágrafo explícito de limitações do estudo, separado de "trabalhos futuros".** Antes de sugerir extensões, o texto nomeia a limitação central da pesquisa em uma frase direta ("Este estudo se limitou pelo baixo retorno de respondentes..."). Essa frase de limitação é curta, não defensiva, e vem **antes** do parágrafo de sugestões futuras — os agentes de trilha devem incluir esse parágrafo de limitações nas Considerações Finais de cada capítulo empírico, não só uma lista de "trabalhos futuros".
- **Anonimização de fontes identificáveis.** Quando uma entidade (empresa, respondente) precisa ser citada mas não identificada, ela recebe um nome fictício explicado no texto (ex.: "será denominada Empresa Alfa"). Aplicar o mesmo padrão sempre que um dado de trilha envolver uma fonte/stakeholder que não deva ser nomeado.

## Resumo para aplicação rápida pelos agentes de trilha
Antes de escrever ou revisar qualquer capítulo, perguntar: "isto leria bem num ensaio acadêmico argumentativo, ou parece um README/log de desenvolvimento?" Se parecer o segundo, reescrever subindo o nível de abstração, removendo qualquer referência a arquivo/código/comando, e reformulando como argumento apoiado em literatura, na voz impessoal, fechando no nível estratégico.
