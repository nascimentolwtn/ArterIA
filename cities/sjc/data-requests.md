# SJC data requests (roadmap P1.2)

Tracks what's logged in `cities/sjc/data-manifest.yaml` and drafts the actual outbound
requests. A remote Claude session can draft and log these (roadmap feature R3) but
cannot send them — no email/contact channel is available here. **The owner sends
these from their own email/contact channel**, then updates the status table below
and the matching `status` field in `data-manifest.yaml`.

Drafts are in Brazilian Portuguese since that's the language the recipients use;
everything else in this repo stays in English per `CLAUDE.md`.

## Status tracker

| Manifest id(s) | Agency | Status | Sent on | Notes |
|---|---|---|---|---|
| `planmob-diagnostico-prognostico`, `od-survey-atlas`, `od-survey-microdata` | Ipplan | to_request | — | Draft below |
| `master-plan-lc612-2018`, `linha-verde-project`, `fgv-transit-tender-studies`, `gtfs-feed`, `traffic-counts`, `signal-timing-plans`, `crash-data`, `emergency-routes` | SEMOB | to_request | — | Draft below; SEMOB can route specific items to Urbam, the transit operator, or Corpo de Bombeiros/SAMU |

Update this table (and the manifest) the moment a request is actually sent or a reply
arrives — this file is a to-do, not a log of what happened.

## Before sending — verify, don't assume

This session found the following from public web sources, not from the agencies
directly; confirm current details before using them:

- **Ipplan** is the Instituto de Pesquisa e Planejamento Urbano de São José dos
  Campos (IPPSJC), created by Lei Complementar 576/2000. Current address/contact
  not verified here — check `sjc.sp.gov.br` or call the Prefeitura's general line.
- **SEMOB** (Secretaria de Mobilidade Urbana) address found in a September 2023
  document: Rua Aurora Pinto da Cunha, 131 – Jardim América – CEP 12235-190 – São
  José dos Campos/SP. Confirm it's still current.
- **Transit operator**: public sources point to Consórcio 123 (Expresso Maringá,
  Joseense Transporte, and a third company not confirmed here) under SEMOB, but a
  2021 bidding process to replace the concession was reported annulled and this
  session could not confirm the contract status as of now — ask SEMOB who currently
  holds the GTFS feed rather than contacting an operator that may have changed.
- Do not guess exact document URLs (e.g. the LC 612/2018 text) — search
  `servicos.sjc.sp.gov.br/Legislacao` or ask the agency for the current link.

## Draft 1 — Ipplan

**To:** Instituto de Pesquisa e Planejamento Urbano de São José dos Campos (Ipplan)
**Subject:** Solicitação de dados para pesquisa acadêmica — mobilidade urbana em São José dos Campos

> Prezados(as),
>
> Meu nome é [NOME], e desenvolvo uma pesquisa de mestrado ([PROGRAMA/INSTITUIÇÃO])
> sobre otimização assistida por IA de intervenções na malha viária de São José dos
> Campos (conversões de mão única, faixas reversíveis, realocação de faixas, faixas
> exclusivas de ônibus, corredores de pedestres/ciclovias e conectores viários),
> avaliadas por simulação de tráfego calibrada (SUMO) antes de qualquer recomendação.
>
> Para isso, preciso de dados que entendo estarem sob a responsabilidade do Ipplan.
> Poderiam, por gentileza, indicar como obter:
>
> 1. O **Diagnóstico e Prognóstico do PlanMob SJC** (Lei Complementar 576/2016), na
>    versão mais atual disponível;
> 2. O **Atlas da Pesquisa Origem-Destino**, caso exista versão consolidada/pública;
> 3. A **microdados (base desagregada) da Pesquisa Origem-Destino**, usada no
>    projeto "Mobilidade do Futuro" — estou ciente de que pode haver restrições de
>    uso/redistribuição, e me comprometo a tratar os dados conforme os termos que
>    me forem indicados (uso exclusivamente acadêmico, sem redistribuição, dados
>    agregados/anonimizados em qualquer publicação).
>
> Fico à disposição para assinar termo de uso ou confidencialidade, se necessário, e
> para apresentar mais detalhes do projeto caso seja útil.
>
> Desde já agradeço a atenção,
> [NOME]
> [CONTATO — e-mail/telefone]
> [INSTITUIÇÃO / PROGRAMA DE MESTRADO]

## Draft 2 — SEMOB

**To:** Secretaria de Mobilidade Urbana de São José dos Campos (SEMOB)
**Subject:** Solicitação de dados para pesquisa acadêmica — mobilidade urbana em São José dos Campos

> Prezados(as),
>
> Meu nome é [NOME], e desenvolvo uma pesquisa de mestrado ([PROGRAMA/INSTITUIÇÃO])
> sobre otimização assistida por IA de intervenções na malha viária de São José dos
> Campos, avaliadas por simulação de tráfego calibrada (SUMO) antes de qualquer
> recomendação (detalhes adicionais disponíveis caso sejam úteis).
>
> Gostaria de solicitar orientação sobre como obter, ou ser direcionado(a) ao setor
> responsável por:
>
> 1. O texto vigente do **Plano Diretor (Lei Complementar 612/2018)**, caso o link
>    oficial atual seja diferente do que encontro publicamente;
> 2. Documentação do **Projeto Linha Verde**;
> 3. Os **estudos da FGV** para o edital do novo transporte público (resultados de
>    oferta/demanda e projeções da rede proposta);
> 4. O **feed GTFS** (ou dados equivalentes de linhas, pontos e frequências) do
>    transporte público, e quem o mantém atualmente;
> 5. **Contagens volumétricas de tráfego** (por hora/sentido) em vias e cruzamentos
>    do município, mesmo que parciais ou de anos anteriores;
> 6. **Planos de tempo semafórico** (programação de sinais) de interseções
>    sinalizadas, ao menos nas vias de maior movimento;
> 7. **Dados de sinistros/acidentes de trânsito** em nível de via/cruzamento, além
>    das estatísticas agregadas já públicas pelo Infosiga/Detran-SP;
> 8. Dados ou contato responsável por **rotas e tempos de resposta de emergência**
>    (bombeiros/SAMU), caso a Secretaria tenha essa informação ou possa indicar o
>    órgão responsável.
>
> Entendo que alguns desses itens podem envolver outros órgãos (Urbam, o(s)
> operador(es) do transporte público, Corpo de Bombeiros/SAMU) — agradeço desde já
> se puderem me indicar os contatos corretos para cada um.
>
> Comprometo-me a usar os dados exclusivamente para fins de pesquisa acadêmica, sem
> redistribuição, e a publicar apenas resultados agregados/anonimizados.
>
> Desde já agradeço a atenção,
> [NOME]
> [CONTATO — e-mail/telefone]
> [INSTITUIÇÃO / PROGRAMA DE MESTRADO]
