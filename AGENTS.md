# AGENTS.md — Trilhas de mestrado (docs/thesis/)

Este arquivo documenta os 4 agentes de Claude Code dedicados a explorar, em paralelo, quatro possíveis trilhas de mestrado ligadas ao tema do ArterIA (otimização de rede viária urbana com IA), já que cada programa tem um período de inscrição diferente e a decisão de qual seguir só será tomada quando a inscrição efetivamente abrir. As definições executáveis estão em `.claude/agents/*.md`; este arquivo é o mapa de alto nível.

## Os 4 agentes

| Agente (`subagent_type`) | Programa | Pasta exclusiva | Enquadramento |
| :-- | :-- | :-- | :-- |
| `thesis-ita-po` | ITA — PG/PO (Pesquisa Operacional) | `docs/thesis/ita-po/` | Otimização bi-nível multiobjetivo de intervenções viárias, com surrogate de ML. |
| `thesis-ita-eec` | ITA — PG/EEC (Informática) | `docs/thesis/ita-eec-informatica/` | RL multiagente + GNN para alocação dinâmica de faixas/direções; núcleo é o método de IA. |
| `thesis-ita-ppgao` | ITA — PPGAO (AO-EL) | `docs/thesis/ita-ppgao/` | Reenquadrado como apoio à decisão logística/operacional da FAB no entorno de SJC. |
| `thesis-unifa-ppgca` | UNIFA — PPGCA | `docs/thesis/unifa-ppgca/` | Reposicionamento profundo: resiliência de infraestrutura dual-use como fator de poder aeroespacial; ArterIA vira instrumento de mensuração, não o núcleo. |

(PPGDHO da UNIFA foi considerado e descartado por ora — ver histórico de conversa; pode ser retomado depois se necessário.)

## Regra de isolamento

Cada agente só lê e escreve dentro da sua própria subpasta em `docs/thesis/`. Nenhum agente edita a pasta de outro, nem código do produto ArterIA (`cities/`, código-fonte quando existir). Isso permite rodar os 4 em paralelo sem conflito.

## Estágio atual: superficial

Por enquanto, cada agente mantém apenas dois artefatos leves por pasta:

- **`outline.md`** — esqueleto de capítulos da dissertação, apontando o que já está coberto no `pre-projeto.md` (documento detalhado já escrito para as 4 trilhas) e o que falta pesquisar/escrever.
- **`progress.md`** — log de progresso datado, com um campo `Status: ativo` ou `Status: descontinuado` no topo.

Nenhum agente deve, por padrão, escrever capítulos completos da dissertação nesta fase — isso só deve acontecer quando o usuário decidir avançar com uma trilha específica.

## Fluxo de decisão (quando a inscrição de um programa abrir)

1. O usuário decide seguir com uma trilha específica (ex.: aplicar para o ITA PG/PO).
2. Marque `Status: descontinuado` no `progress.md` das outras 3 trilhas (as pastas e o `pre-projeto.md` de cada uma permanecem como histórico, não são apagadas).
3. A trilha ativa passa a receber trabalho de profundidade real (desenvolvimento de capítulos, dados, experimentos), deixando de ser "superficial".
4. Se mais de uma inscrição acabar sendo levada adiante ao mesmo tempo, mais de uma trilha pode ficar `ativo` simultaneamente — a regra de isolamento por pasta já suporta isso.

## Como invocar

Use a ferramenta Agent com `subagent_type` igual ao nome na tabela acima (ex.: `thesis-ita-po`) para atualizar o outline/progresso de uma trilha específica. Para atualizar as 4 de uma vez, chame as 4 em paralelo numa única mensagem — elas não têm dependência entre si.
