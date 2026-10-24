# Research Brief: AI-Assisted Traffic and Street-Network Optimization in São José dos Campos, SP

## Objective

Study and propose traffic changes for São José dos Campos (SJC), São Paulo, Brazil, combining:

- Real local mobility data and plans.
- AI-assisted optimization of street directions, lane allocation, dedicated lanes, and possible new links.
- Traffic simulation with explicit before/after comparison.
- Cities: Skylines only as a communication and stakeholder-engagement layer, not as the primary quantitative evidence base.

The defensible formulation is:

> AI-assisted selection and sequencing of candidate interventions—such as one-way conversions, reversible lanes, lane reallocation, bus lanes, pedestrian corridors, and a limited set of new links—subject to budget, safety, equity, emissions, emergency access, and user-equilibrium traffic response.

## Local context: São José dos Campos

SJC has an official Urban Mobility Plan, **PlanMob SJC**, approved through Municipal Complementary Law No. 576/2016. The plan's diagnostic and prognostic reports are key baseline documents for demand, road hierarchy, public transport, cycling, and pedestrian mobility. [74]

The city's 2016–2018 Master Plan analysis uses PlanMob data and identifies strong peak-hour commuting patterns; for example, the Pedro Friggi axis toward Parque Novo Horizonte has high morning peak volumes toward the center and high saturation on those lines. [71]

The current Master Plan, Law No. 612/2018, establishes "quality transport and an accessible city" as fundamental citizen rights and treats mobility as one of the city's structural elements. [72] It also defines the road macrostructure, road hierarchy, and cycling network based on the municipal mobility plan. [75]

Relevant local data sources and projects include:

- **Pesquisa Origem-Destino (OD) de São José dos Campos**: used for demand estimation in the "Mobilidade do Futuro" project. [73]
- **FGV studies for the public-transport tender**: include analysis of supply/demand results and projections for the proposed network. [70]
- **Linha Verde project**: a municipal mobility project aligned with the Master Plan. [82]
- **ITA / Ipplan / UNIBAGUE agent-based modeling research**: a 2015 collaboration proposed an agent-based model to analyze individual modal-choice behavior in SJC. [76]
- **PlanMob sustainability analysis (2025)**: evaluates active mobility and public transport strategies, including "Vou de Bike," cycling-network expansion, and Linha Verde. [77][79]
- **Critical PlanMob analyses**: examine public/private transport axes, social impacts, and the "right to the city"; useful for equity constraints and stakeholder framing. [78][83]

## Research gaps in SJC

The existing local literature and plans provide demand, policy, and diagnostic context, but there appears to be little publicly available work that combines:

1. A calibrated microscopic or mesoscopic traffic model of SJC.
2. AI-based optimization of physical/topological interventions.
3. Explicit before/after evaluation of street-direction changes, lane reallocation, bus lanes, pedestrian corridors, and candidate new links.
4. Equity, safety, emergency access, and public-transport impacts—not only private-car delay.

That is the likely original contribution of this study.

## Academic foundations

### 1. Urban network design and street-direction changes

These works optimize road directions, lane additions, new links, and lane allocation under traffic-assignment constraints.

- **Miandoabchi et al., "Hybrid Evolutionary Metaheuristics for Concurrent Multi-Objective Design of Urban Road and Public Transit Networks," *Networks and Spatial Economics*, 2011.**
  Jointly designs road and bus networks, including new street construction, lane additions, lane allocation, and one-way/two-way conversion. [45]

- **"Multi-objective discrete urban road network design," *Computers & Operations Research*, 2013.**
  Evaluates link construction, lane additions, lane allocation, and one-way/two-way decisions under multi-objective criteria. [50]

- **"A meta-heuristic approach for solving the Urban Network Design Problem," 2010.**
  Optimizes directions of existing roads, capacity expansion, and signal settings using a bi-level nonlinear constrained model. [52]

- **"Bi-objective bi-level optimization for integrating lane-level closure and reversal in redesigning transportation networks," *Operational Research*, 2023.**
  Optimizes lane closures and reversals under budget constraints using a hybrid ML/bi-level optimization approach. [42]

- **"A hybrid deep-learning-metaheuristic framework for bi-level network design problems," *Expert Systems with Applications*, 2023.**
  Uses a graph neural network as a surrogate for traffic assignment and a genetic algorithm to search lane-addition designs. [43]

### 2. Dedicated lanes and modal priority

These studies are relevant to bus lanes, cycling corridors, pedestrian space, and possible AV/connected-vehicle lanes.

- **"Optimization of dedicated bus lane location on a network," *Transportation*, 2021.**
  Bi-level optimization for selecting dedicated bus-lane locations, accounting for dynamic traffic effects and trade-offs between bus priority and general-traffic delay. [27]

- **"Simulation-based optimization of large-scale dedicated bus lanes allocation," *Transportation Research Part C*, 2022.**
  Uses machine-learning surrogate models to make large-scale bus-lane allocation optimization computationally feasible. [29]

- **"Urban public transport optimization by bus lanes," WIT Press.**
  Uses neural networks to predict bus-speed improvements and a greedy heuristic to select bus-lane locations in Palermo. [35]

- **"A Reinforcement Learning-based Adaptive Control Model for Future Transportation," arXiv, 2021.**
  Uses multi-agent DDPG in SUMO to dynamically allocate street space among sidewalks, AV lanes, and on-street parking. [36]

- **"Adaptive Road Configurations for Improved Autonomous Vehicle-Pedestrian Interactions using Reinforcement Learning," arXiv, 2023.**
  Uses RL to evolve road configurations and right-of-way allocation among vehicles and pedestrians in microscopic simulation. [37]

### 3. AI traffic-signal and flow optimization

Useful as a complementary layer, but not the central focus if the study proposes physical street changes.

- **Yau et al., "A survey on Reinforcement Learning Models and Algorithms for Traffic Signal Control," *ACM Computing Surveys*, 2017.**
  Foundational survey of RL formulations for signal control. [21]

- **Wei et al., "Using a Deep Reinforcement Learning Agent for Traffic Signal Control," arXiv:1611.01142, 2016.**
  Early influential DRL study using SUMO. [22]

- **Liang et al., "Adaptive Traffic Signal Control: Deep Reinforcement Learning Algorithm with Real-time Traffic Data," arXiv:1705.02755, 2017.**
  Learns adaptive signal policies from real-time traffic data. [24]

- **Tong et al., "Traffic Signal Control Based on Reinforcement Learning with Graph Convolutional Neural Nets," *IEEE ITSC*, 2018.**
  Combines RL and graph convolutional networks to capture road-network dependencies. [17]

- **"A comprehensive review of artificial intelligence techniques for traffic signal control in intelligent transportation systems," *Discover Applied Sciences*, 2026.**
  Reviews deep learning, GNNs, evolutionary methods, fuzzy logic, transformers, and LLM-based approaches. [1]

- **"Reinforcement learning for traffic signal control in large-scale transportation networks: a systematic literature review," *Artificial Intelligence Review*, 2026.**
  Systematic review focused on scalable RL-based traffic-signal control. [11]

- **"A survey of reinforcement and deep reinforcement learning for coordination in intelligent traffic light control," *Journal of Big Data*, 2025.**
  Reviews RL/DRL coordination across intersections. [12]

### 4. Dynamic lane-direction allocation

Most relevant to real-time or scenario-based changes in street direction.

- **"Real-time Lane Configuration with Coordinated Learning-based Lane Allocation (CLLA)," ECML PKDD, 2020.**
  Uses a two-layer multi-agent RL architecture: lower-level agents configure lane directions near intersections; upper-level agents coordinate them to avoid transferring congestion. Reported 20% average travel-time reduction in congested networks versus uncoordinated RL. [28]

- **"Dynamic Graph Configuration with Reinforcement Learning," arXiv:1910.06788.**
  Introduces CLLA for dynamic lane-direction configuration. [38]

### 5. Simulation and Cities: Skylines

- **"Uso do 'Cities: Skylines' para avaliação de cenários urbanos," SINGEURB, 2019.**
  Recreates the Cidade Jardim neighborhood in São Carlos, SP, and evaluates a mobility scenario including cycling improvements, a street extension, one-way conversion, and pedestrian-only paths. Reports improved mobility and an estimated 2.5% urban-cost increase. This is the closest Brazilian before/after Cities: Skylines case, but it is a conference paper and should not be treated as decision-grade evidence. [57]

- **"Cities: Skylines as a Tool for Traffic Analysis and Urban Planning," Springer, 2025.**
  Uses Cities: Skylines to compare transport-network designs, but in stylized rather than real-city settings. [55]

- **Yogyakarta case study, Universitas Gadjah Mada.**
  Attempted to use Cities: Skylines for real-area transport planning but reported technical and operational limitations. [56]

- **"Precision of city simulations using publicly available city data," Universität zu Lübeck thesis.**
  Finds that mods can materially affect simulated traffic behavior and hotspots in Cities: Skylines. [59]

- **"The Case of Cities: Skylines Versions—Affordances in Urban Planning," 2025.**
  Notes that native traffic management is limited and that more realistic traffic management often depends on mods. [64]

## Recommended method

### Phase 1 — Define study area

Select one or more pilot corridors or neighborhoods in SJC, preferably where PlanMob/OD data already indicate congestion, transit demand, or modal-conflict problems. Candidate criteria:

- High peak-hour congestion.
- Strong home-to-work commuting flow.
- Existing or planned bus corridors.
- Presence of cycling/pedestrian demand.
- Feasibility of lane reallocation without major land acquisition.
- Availability of traffic counts and signal-timing data.

### Phase 2 — Build the baseline

Collect:

- Road geometry, lane counts, turn restrictions, and one-way status.
- Traffic counts by hour and direction.
- Signal locations, phasing, and timing.
- Bus routes, frequencies, stops, and passenger loads.
- OD matrix or trip-generation estimates.
- Cycling and pedestrian counts.
- Crash history and emergency-service routes.

Build and calibrate a baseline model in **SUMO**, **MATSim**, **AIMSUN**, **PTV Vissim**, or **TransModeler**. SUMO is a strong open-source choice; MATSim is strong for city-scale demand and policy scenarios.

Calibration targets should include:

- Link volumes.
- Turning movements.
- Queue lengths.
- Travel times.
- Transit travel times.
- Mode split, if using a demand model.

### Phase 3 — Generate intervention candidates

Do not let an AI model freely invent streets. Start from a constrained intervention catalog:

- One-way conversions.
- Reversible or tidal lanes.
- Bus lanes or bus priority corridors.
- Protected cycling corridors.
- Pedestrian corridors or shared streets.
- Turn restrictions.
- New local connector streets, only where land and feasibility allow.
- Intersection redesigns.
- Signal retiming and transit-signal priority.

Each candidate should have:

- Cost estimate.
- Implementation complexity.
- Legal/property constraints.
- Safety implications.
- Emergency-access implications.
- Equity impact.
- Expected beneficiaries and losers.

### Phase 4 — AI optimization

Use AI to search the combinatorial space of interventions, not to replace traffic modeling.

Recommended architecture:

- **Upper level:** optimization or RL selects an intervention package.
- **Lower level:** traffic-assignment or simulation estimates user-equilibrium flows, travel times, queues, transit performance, emissions, and safety proxies.
- **Surrogate model:** GNN or ML model approximates expensive simulation outputs after enough simulation samples are available.
- **Constraints:** budget, minimum transit service, emergency access, pedestrian continuity, and equity thresholds.

Suitable methods:

- Bi-level optimization with genetic algorithms or evolutionary local search.
- Bayesian optimization.
- Multi-objective evolutionary algorithms.
- Graph neural network surrogates.
- Multi-agent RL for dynamic lane allocation.
- Scenario-based simulation optimization.

### Phase 5 — Before/after evaluation

For every scenario, compare against the calibrated baseline using:

- Total vehicle-hours traveled.
- Average and 95th-percentile travel time.
- Delay and queue length.
- Bus travel time and reliability.
- Pedestrian and cyclist exposure/delay.
- Emissions and fuel/energy estimates.
- Crash-risk proxies and conflict analysis.
- Emergency-response accessibility.
- Equity metrics by neighborhood or income group.
- Implementation cost and benefit-cost ratio.

Report uncertainty, not only point estimates.

### Phase 6 — Cities: Skylines role

Use Cities: Skylines as a **visual digital twin and participatory-planning tool**, not as the final quantitative model.

Possible uses:

- Communicate one-way changes, lane reallocation, bus lanes, pedestrian corridors, and new links to residents.
- Run public workshops or scenario co-design.
- Produce intuitive before/after visualizations.
- Test broad land-use and mobility narratives.

Do not use Cities: Skylines outputs as the primary basis for engineering recommendations. Use a calibrated traffic model for the quantitative before/after evidence. [56][59][64]

## SJC-specific research questions

1. Which SJC corridors would benefit most from reversible lanes, one-way conversions, or lane reallocation?
2. Where should dedicated bus lanes be introduced to improve total person-throughput rather than only bus speed?
3. Can protected cycling corridors and pedestrian-priority streets be added without unacceptable car-delay penalties?
4. Are there low-cost new connector streets or turn restrictions that materially reduce cut-through traffic?
5. How do proposed changes affect emergency access, freight movement, and neighborhoods outside the direct intervention area?
6. Can an AI optimizer identify intervention packages that improve multiple objectives—delay, transit reliability, safety, emissions, and equity—rather than only minimizing car travel time?
7. What is the difference between results from a game-based visualization and a calibrated SUMO/MATSim/AIMSUN model?

## Deliverables

- Calibrated baseline model of the selected SJC area.
- Candidate intervention catalog with constraints and costs.
- AI-assisted optimization workflow.
- Before/after simulation results.
- Multi-objective ranking of intervention packages.
- Equity and safety assessment.
- Cities: Skylines visualization for stakeholder engagement.
- Final policy report with implementation phases and monitoring indicators.

## Important caution

Do not frame the project as "AI creates new streets." That understates land acquisition, utilities, drainage, zoning, environmental review, emergency access, and political feasibility. Frame it as:

> AI-assisted planning and evaluation of feasible street-network interventions, using calibrated simulation to compare before/after impacts.

## Citation-ready reference list

1. Miandoabchi, E. et al. (2011). *Hybrid Evolutionary Metaheuristics for Concurrent Multi-Objective Design of Urban Road and Public Transit Networks.* Networks and Spatial Economics. [45]
2. *Multi-objective discrete urban road network design.* Computers & Operations Research, 2013. [50]
3. *A meta-heuristic approach for solving the Urban Network Design Problem.* 2010. [52]
4. *Bi-objective bi-level optimization for integrating lane-level closure and reversal in redesigning transportation networks.* Operational Research, 2023. [42]
5. *A hybrid deep-learning-metaheuristic framework for bi-level network design problems.* Expert Systems with Applications, 2023. [43]
6. *Optimization of dedicated bus lane location on a network.* Transportation, 2021. [27]
7. *Simulation-based optimization of large-scale dedicated bus lanes allocation: Using efficient machine learning models as surrogates.* Transportation Research Part C, 2022. [29]
8. *Urban public transport optimization by bus lanes.* WIT Press. [35]
9. *A Reinforcement Learning-based Adaptive Control Model for Future Transportation.* arXiv, 2021. [36]
10. *Adaptive Road Configurations for Improved Autonomous Vehicle-Pedestrian Interactions using Reinforcement Learning.* arXiv, 2023. [37]
11. Yau, K. L. A. et al. (2017). *A survey on Reinforcement Learning Models and Algorithms for Traffic Signal Control.* ACM Computing Surveys. [21]
12. Wei, H. et al. (2016). *Using a Deep Reinforcement Learning Agent for Traffic Signal Control.* arXiv:1611.01142. [22]
13. Liang, X. et al. (2017). *Adaptive Traffic Signal Control: Deep Reinforcement Learning Algorithm with Real-time Traffic Data.* arXiv:1705.02755. [24]
14. Tong, Y. et al. (2018). *Traffic Signal Control Based on Reinforcement Learning with Graph Convolutional Neural Nets.* IEEE ITSC. [17]
15. *A comprehensive review of artificial intelligence techniques for traffic signal control in intelligent transportation systems.* Discover Applied Sciences, 2026. [1]
16. *Reinforcement learning for traffic signal control in large-scale transportation networks: a systematic literature review.* Artificial Intelligence Review, 2026. [11]
17. *A survey of reinforcement and deep reinforcement learning for coordination in intelligent traffic light control.* Journal of Big Data, 2025. [12]
18. *Real-time Lane Configuration with Coordinated Learning-based Lane Allocation (CLLA).* ECML PKDD, 2020. [28]
19. *Dynamic Graph Configuration with Reinforcement Learning.* arXiv:1910.06788. [38]
20. *Uso do "Cities: Skylines" para avaliação de cenários urbanos.* SINGEURB, 2019. [57]
21. *Cities: Skylines as a Tool for Traffic Analysis and Urban Planning.* Springer, 2025. [55]
22. Prefeitura de São José dos Campos. *PlanMob SJC — Diagnóstico e Prognóstico.* [74]
23. Prefeitura de São José dos Campos. *Plano Diretor 2016–2018.* [71]
24. Prefeitura de São José dos Campos. *Plano Diretor de Desenvolvimento Integrado.* [75]
25. Prefeitura de São José dos Campos. *Mobilidade do Futuro: um Modelo Disruptivo para São José dos Campos.* [73]
26. Prefeitura de São José dos Campos. *Estudos da FGV para a construção do edital do novo transporte público.* [70]
27. Prefeitura de São José dos Campos. *Projeto Linha Verde.* [82]
28. *Sustentabilidade no Plano de Mobilidade Urbana de São José dos Campos: estratégias para a micromobilidade e o transporte coletivo.* 2025. [77]
29. *Mobilidade urbana em São José dos Campos: uma construção como direito de ir e vir ou direito à cidade?* [83]
30. *Entre o direito à cidade e a mercantilização.* UNESP, 2026. [78]
