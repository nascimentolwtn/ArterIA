# AGENTS.md — Trilhas de mestrado (docs/thesis/)

Este arquivo documenta os agentes de Claude Code dedicados a explorar, em paralelo, quatro possíveis trilhas de mestrado ligadas ao tema do ArterIA (otimização de rede viária urbana com IA), já que cada programa tem um período de inscrição diferente e a decisão de qual seguir só será tomada quando a inscrição efetivamente abrir. As definições executáveis estão em `.claude/agents/*.md`; este arquivo é o mapa de alto nível. `CLAUDE.md` invoca apenas o orquestrador; o orquestrador decide quais das 4 trilhas chamar.

## Orquestrador

| Agente (`subagent_type`) | Papel |
| :-- | :-- |
| `thesis-orchestrator` | Chamado pelo `CLAUDE.md` após commits relevantes de código/docs/ADR. Lê o campo `Status:` de cada trilha e chama, em paralelo, só os agentes das trilhas `ativo`. Não escreve conteúdo de tese ele mesmo — só decide e delega. Nunca commita/pusha. |

## As 4 trilhas

| Agente (`subagent_type`) | Programa | Pasta exclusiva | Enquadramento |
| :-- | :-- | :-- | :-- |
| `thesis-ita-po` | ITA — PG/PO (Pesquisa Operacional) | `docs/thesis/ita-po/` | Otimização bi-nível multiobjetivo de intervenções viárias, com surrogate de ML. |
| `thesis-ita-eec` | ITA — PG/EEC (Informática) | `docs/thesis/ita-eec-informatica/` | RL multiagente + GNN para alocação dinâmica de faixas/direções; núcleo é o método de IA. |
| `thesis-ita-ppgao` | ITA — PPGAO (AO-EL) | `docs/thesis/ita-ppgao/` | Reenquadrado como apoio à decisão logística/operacional da FAB no entorno de SJC. |
| `thesis-unifa-ppgca` | UNIFA — PPGCA | `docs/thesis/unifa-ppgca/` | Reposicionamento profundo: resiliência de infraestrutura dual-use como fator de poder aeroespacial; ArterIA vira instrumento de mensuração, não o núcleo. |

(PPGDHO da UNIFA foi considerado e descartado por ora — ver histórico de conversa; pode ser retomado depois se necessário.)

Estes 4 agentes absorveram as regras de redação do antigo agente `thesis-student` (removido): nunca inventar resultado/citação/dado, profundidade acompanhando evidência, voz acadêmica em pt-BR, decisões viram capítulo. A diferença é que cada trilha vive isolada na sua própria pasta em vez de um `thesis/` único genérico — porque hoje nenhum programa foi escolhido ainda.

## Regra de isolamento

Cada um dos 4 agentes de trilha só lê e escreve dentro da sua própria subpasta em `docs/thesis/`. Nenhum edita a pasta de outro, nem código do produto ArterIA (`cities/`, código-fonte quando existir). O orquestrador não edita nenhuma pasta de trilha diretamente. Isso permite rodar as 4 trilhas em paralelo sem conflito.

## Dois eixos de estágio: Status e Profundidade

Cada `docs/thesis/<trilha>/progress.md` tem dois campos no topo:

- **`Status: ativo` / `Status: descontinuado`** — se a trilha ainda está em jogo. Só trilhas `ativo` são chamadas pelo orquestrador.
- **`Profundidade: leve` / `Profundidade: completo`** — hoje as 4 estão em `leve`: só `outline.md` + `progress.md`, esqueleto de capítulos e log de progresso, sem prosa real. `completo` (herdado do antigo `thesis-student`) só deve ser ativado na trilha efetivamente escolhida, e passa a usar `progress-log.md` (append-only), `chapters/NN-nome.md` e `references.bib` — ver `.claude/agents/thesis-*.md` para o detalhe de cada formato.

## Fluxo de decisão (quando a inscrição de um programa abrir)

1. O usuário decide seguir com uma trilha específica (ex.: aplicar para o ITA PG/PO).
2. Marque `Status: descontinuado` no `progress.md` das outras 3 trilhas (as pastas, `pre-projeto.md`, `outline.md` e `progress.md` de cada uma permanecem como histórico, não são apagadas).
3. Na trilha escolhida, mude `Profundidade: leve` para `Profundidade: completo`. Isso faz o agente daquela trilha passar a escrever capítulos reais, log append-only e `references.bib`.
4. Se mais de uma inscrição acabar sendo levada adiante ao mesmo tempo, mais de uma trilha pode ficar `ativo` (e até `completo`) simultaneamente — a regra de isolamento por pasta já suporta isso.

## Como invocar

- **Rotina normal (após commits):** deixe o `CLAUDE.md` chamar `thesis-orchestrator`; ele decide quais trilhas tocar.
- **Atualizar uma trilha específica na mão:** use a ferramenta Agent com `subagent_type` igual ao nome na tabela (ex.: `thesis-ita-po`).
- **Atualizar as 4 de uma vez manualmente:** chame as 4 em paralelo numa única mensagem — elas não têm dependência entre si (ou simplesmente invoque `thesis-orchestrator`, que faz essa seleção por você).
