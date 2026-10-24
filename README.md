# ArterIA

Apoio à decisão com IA para o planejamento de redes viárias, projetado para ser reutilizável em qualquer cidade. As ruas são as artérias da cidade, e o ArterIA ajuda a testar quais mudanças realmente as melhoram.

O ArterIA não "inventa ruas". Ele pesquisa um catálogo restrito de intervenções viáveis (conversão para mão única, faixas reversíveis, faixas de ônibus, realocação de faixas, corredores protegidos para bicicletas e pedestres, restrições de conversão, alguns novos trechos de ligação) e avalia cada pacote em relação a uma simulação de base calibrada.

## Como funciona

1. **Linha de base:** construir a área de estudo a partir do OpenStreetMap no SUMO e, em seguida, calibrar com contagens de tráfego, tempos de viagem e dados de origem-destino locais.
2. **Candidatas:** definir as intervenções com custo, limites legais, segurança, acesso de emergência e observações de equidade.
3. **Otimização:** um otimizador de nível superior (algoritmo genético, otimização bayesiana ou RL, com substitutos baseados em GNN no futuro) escolhe os pacotes. O SUMO atua como nível inferior e retorna a resposta do tráfego.
4. **Antes/depois:** comparar veículos-hora, tempo de viagem no percentil 95, confiabilidade do transporte por ônibus, emissões, indicadores indiretos de segurança e equidade por bairro.
5. **Comunicação:** narrativa visual opcional para as partes interessadas (por exemplo, com o Cities: Skylines), sem uso como evidência quantitativa.

## Usando na sua cidade

Cada cidade fica em sua própria pasta em `cities/<nome-da-cidade>/`, com seus próprios dados, calibração e cenários, enquanto o código do otimizador e da avaliação é compartilhado. Para adicionar uma cidade, você precisa de um extrato do OSM da área de estudo, algumas contagens de tráfego ou tempos de viagem e quaisquer dados de demanda disponíveis.

## Pilotos

- **São José dos Campos, SP, Brasil** (primeiro piloto, em andamento)

## Tecnologias

SUMO (netedit, sumo-gui, TraCI), Python, OpenStreetMap, sumo-rl ou otimizadores customizados.

## Status

Fase inicial, versão 0.1 (planejamento). Próximos passos: construir a linha de base do primeiro piloto e definir a estrutura do projeto independente de cidade. Veja o `CHANGELOG.md` para o que mudou.

## Dados e créditos

Dados de mapa © colaboradores do OpenStreetMap (ODbL). As fontes locais de cada cidade são creditadas em sua própria pasta.

## Licença

A definir
