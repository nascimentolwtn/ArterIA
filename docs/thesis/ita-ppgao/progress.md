# Log de Progresso — Trilha PPGAO/ITA (AO-EL)

Status: ativo
Profundidade: leve

---

## 2026-10-24 (revisão dos commits bf374e4 e cd68b57)

Dois commits de preparação de dados do ArterIA para SJC (roadmap P1.1/P1.2, fora desta trilha) têm reflexo direto no Capítulo 3 (Caracterização da Área) desta trilha e foram registrados no `outline.md`.

**`bf374e4`** criou `cities/sjc/data-manifest.yaml` (inventário de todas as fontes de dados civis de Fase 1 para SJC — PlanMob, Plano Diretor, atlas e microdados da Pesquisa OD, estudos FGV, Linha Verde, GTFS, contagens de tráfego, planos semafóricos, dados de sinistros, rotas de emergência, cada um com agência, licença, visibilidade e status) e `cities/sjc/data-requests.md` (rascunhos de cartas de solicitação ao Ipplan e à SEMOB, ainda não enviadas).

**`cd68b57`** registrou a decisão do responsável pelo projeto ArterIA de **não contatar nenhum órgão de SJC nesta etapa**. Todo item do manifesto que dependia de resposta municipal passou a `status: deferred`. Em substituição, para a malha viária de base, três fontes públicas de autoatendimento foram adicionadas (OpenStreetMap, portal Geosanja do Plano Diretor/zoneamento, Base de Faces de Logradouros do IBGE), sem necessidade de contato com qualquer agência — qualidade e completude ainda não verificadas por bloqueio de rede desta sessão remota, sinalizadas como pendência de mesa em `.claude/napkin.md`.

Relevância específica para a trilha AO-EL:

- **Nenhum dado operacional da FAB** foi levantado nestes commits — o escopo tratado é inteiramente civil (malha viária, trânsito, transporte público de SJC). Isso não altera o enquadramento operacional-militar proposto, mas é evidência concreta e rastreável de que a limitação da Seção 12 do pré-projeto ("dados sensíveis ou restritos... podem limitar a calibração do modelo a dados civis substitutos") permanece integralmente em aberto, e que nem mesmo o levantamento preliminar de disponibilidade de dados operacionais da FAB (próximo passo 3 do log anterior) foi iniciado.
- **`emergency-routes`** (rotas e tempos de resposta de emergência) é explicitamente descrito no manifesto como "a fonte mais sensível e de obtenção mais difícil", com uma proxy sugerida (isócronas a partir de postos de bombeiros/SAMU conhecidos) caso o dado não seja obtido. Isso é diretamente relevante à métrica de "continuidade operacional" da Seção 10 do pré-projeto e ao próprio recorte logístico-militar: se essa fonte permanecer indisponível, a dissertação precisará se apoiar em proxy civil (isócronas) em vez de dado real de resposta a emergências no entorno ITA/DCTA-CTA.
- **`crash-data`** aponta o Infosiga/Detran-SP como possível fonte pública agregada de sinistros, cobrindo SJC em nível estadual (detalhe municipal/por via ainda não confirmado). É um proxy civil plausível para as "métricas de segurança" já previstas na Seção 10 do pré-projeto, na ausência de dado de sinistralidade específico do entorno das instalações da FAB.
- A decisão de **não contatar agências** nesta etapa é do projeto ArterIA como um todo, não uma decisão específica desta trilha de mestrado — mas, por ora, mantém o levantamento de dados desta dissertação limitado a fontes públicas e de autoatendimento (OSM, Geosanja, IBGE, Infosiga), o que é compatível com o Capítulo 3 do `outline.md` tal como está hoje (ainda não iniciado empiricamente).

Nenhuma mudança de status, risco principal ou próximo passo anterior foi revertida por este registro; o risco de validação do enquadramento pelo orientador (ver entrada abaixo) permanece o item crítico, independentemente do avanço no levantamento de dados civis.

## 2026-10-24 (revisão do commit 62facb2)

Commit `62facb2` ("docs(roadmap): reframe remote work as Claude app sessions, not GitHub Actions") revisado para esta trilha. Trata-se de reorganização do fluxo de trabalho de desenvolvimento do ArterIA (divisão de tarefas entre sessões em nuvem e desktop, escopo de ADR 0009/0010, IDs de features) — matéria de infraestrutura de execução do projeto de software, sem relação com o enquadramento operacional-militar, a formulação bi-nível, a metodologia ou o recorte geográfico que constituem o objeto desta dissertação. Nenhuma ação necessária; nenhum capítulo do `outline.md` é afetado.

## 2026-10-24

O pré-projeto detalhado (`pre-projeto.md`) já existia e cobre com profundidade o enquadramento operacional-militar, o problema de pesquisa, a formulação bi-nível (otimização + simulação SUMO), os objetivos, a metodologia, as métricas de avaliação, as limitações/riscos e um cronograma tentativo de 18-20 meses. Nesta sessão foram criados `outline.md` (esqueleto de capítulos do produto técnico, mapeando o que já está coberto pelo pré-projeto e o que falta pesquisar/escrever em cada capítulo) e este arquivo de log de progresso.

Próximos passos realistas:

1. **Buscar contato formal com um orientador do PPGAO na área AO-EL** e apresentar o pré-projeto para validação do enquadramento operacional-logístico-militar — este é o maior risco em aberto do projeto. Os temas do programa partem, em geral, de demandas já definidas pela FAB, de modo que o reenquadramento proposto (entorno de instalações ITA/DCTA-CTA como nó logístico sujeito a interdição) pode precisar de ajuste substancial, ou mesmo não ser aceito, dependendo do orientador e das linhas de pesquisa já em curso.
2. Avançar a revisão de literatura em análise operacional/logística de defesa e resiliência de redes sob interdição (hoje a lacuna mais evidente do pré-projeto, delegada ao futuro orientador na referência 12), para chegar à primeira conversa com mais substância própria.
3. Levantar, mesmo que preliminarmente, a disponibilidade real de dados operacionais da FAB (fluxo de pessoal, cargas, viaturas) para o recorte geográfico candidato, já que a viabilidade de calibração do modelo depende diretamente disso e é citada como limitação relevante no pré-projeto.

**Risco principal em aberto:** a aceitação do enquadramento operacional/FAB por um orientador do PPGAO/AO-EL. Sem essa validação, nenhum dos capítulos de metodologia, cenários/resultados ou recomendações do `outline.md` pode avançar com segurança, pois o recorte, as métricas e até o tema podem precisar ser substancialmente redefinidos pelo orientador.
