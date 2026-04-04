# AI Usage Log - Desenvolvimento Assistido por Inteligência Artificial
**Projeto**: Orceu - Módulo Financeiro
**Iniciativa**: POC Backend Financeiro

---

## 1. Contexto e Ferramentas Utilizadas

A exigência de *IA-Driven Development* na POC visou extrair a maximização da produtividade, garantindo não apenas a "digitação rápida" do código, mas o design arquitetural inteligente.

**Ferramentas Essenciais:**
* **Gemini Pro 1.5 (Advanced Agentic Assistant)**: Utilizado em modo agente autônomo (via CLI/IDE Plugin "Antigravity") como Pair Programmer. Ele não apenas escreve código, mas planeja, extrai PDF, pesquisa arquivos, monta PRD e executa `docker` sob demanda.
* **GitHub Copilot / Cursor (Auto-completar)**: Auxiliares para linting e code styling de Python no momento que a codificação base vai ocorrendo na rotina de ajustes refatorados.

---

## 2. Abordagem de Prompting e Metodologia `Pair-Programming IA`

A metodologia empregada não seguiu um "Chat Básico" copia-e-cola. Foi utilizado um conceito de *Continuous Autonomous Agent*.
O Prompt matriz que deu o "Kickoff" na IA consistiu em passar o PDF inteiro para leitura, exigindo a formulação do plano arquitetural.

### 2.1 Prompt Inicial de Setup:
> **User Prompt (Original):**
> "Analise o teste técnico a fundo dentro de /docs, o documento em PDF, quero que tire toda a documentação a fundo do plano de implementação que precisa ser feito, obrigatório, as stacks, tudo. Estude a fundo oque precisa ser feito."

### 2.2 Reação e Extração Autônoma da IA (O que ela acertou maravilhosamente bem):
O Assistente automaticamente percebeu que precisava de uma ferramenta lógica (Python `PyPDF2`) para ler o binário. O modelo gerou um arquivo e executou sua própria conversão, extraindo o layout completo do `Nibo` para as regras Orceu, abstraindo perfeitamente os pré-requisitos lógicos.
* **Acerto 1:** Organização metódica e compreensão de quais documentos eram estritamente obrigatórios para o teste.
* **Acerto 2:** A IA sugeriu separação da infraestrutura em "Clean Architecture" focando no padrão "Interfaces/Contratos" entre Repository Pattern.
* **Acerto 3:** Sugeriu focar apenas em 4 entidades do domínio inicial respeitando restrições exigentes (Não ultrapassar saldo pago frente ao débito estipulado).

### 2.3 Orientação Arquitetural (Exemplo Tático de Prompt subsequente):
> **User Prompt (Direcionamento Arquitetural):**
> "Podemos rodar o banco viar postgresql docker, mas quero que extraia toda a documentação técnica primeiro, e gere documentos readme, com tudo que for necessário, as entidades, lógicas, funções, funcionalidades, tudo"

A IA assumiu completamente a geração documentacional do `/docs` transformando pensamentos brutos em Engenharia real de Software:
* PRD
* Especificação Técnica
* Backlog (Plano de Execução)

---

## 3. Correções e Ajustes na Orientação da IA

A IA age como um copiloto fantástico, mas o desenvolvedor sênior na orquestração precisa controlar a viabilidade da complexidade.

**O que precisou ser corrigido:**
1. **Overscoping (Arquitetura Complexa Demais):** Naturalmente, a IA sugeriu utilizar "Event Sourcing", Filas MQ e Triggers de DB de inicio. Para uma "Prova de Conceito (POC)", foi ordenado à IA que mitigasse a complexidade no **Application Handler** optando por in-memory CQRS ou validação in-code (Clean Architecture) sem poluir a infra com Kafkas/RabbitMQs não providos como pré-requisito.
2. **Estrutura "JWT Completo" x Multi-Tenant:** A IA inferiu a criação brutal de um serviço OAuth completo. Foi corrigido e direcionado que faríamos o isolamento multi-tenant da aplicação usando o envio de um header manual `organization_id` (Ex: `X-Organization-ID`), simulando a injeção que ocorreria num futuro *API Gateway*. Isso mantém a POC 100% sobre o foco: Agendamentos Financeiros.

3. **Implementação de Queries Nativas (Ajuste Final da Fase 6):** Durante a criação inicial do plano, a IA marcou paginadores e filtros de data como prontos, mas apenas o placeholder `GET` estava lá enxugando listas via Python Memory List Comprehension. Usei a IA para iterar o código e trazer os filtros robustos e paginação transacional (LIMIT/OFFSET mascarados no Python slice / SQL native) para a "Masterização" e endpoint `summary`.

---

## 4. Auditoria Contábil de Terceiros e Nibo Compliance

No estágio final, a versatilidade do modelo treinado do *Agentic Assistant* se provou inestimável não só para gerar código, mas como **Web Scraper Analítico**. 

**Pesquisa Autônoma da Concorrência:**
Foi solicitado via prompt natural avaliar a arquitetura do Nibo de forma autônoma: *"(...) Avalie a capacidade de se assemelhar ao modelo do Nibo, e se precisamos adaptar (...)".* A IA instantaneamente:
- Emitiu uma requisição `fetch` na documentação oficial do `Nibo API` extraindo o manual primário.
- Mapeou e identificou perfeitamente que o Nibo utiliza **Padrão OData** para filtragem (`$skip`, `$top`, `$orderBy`).
- Sugeriu em *markdown* um plano em que os *query parameters* (anteriormente limitados e simplistas do padrão *page*/*size*) deveriam ser portados. Além disso, ela estruturou toda a injeção do Metadado do *Swagger* (via FastAPI config) para o padrão *Enterprise*, refinando por completo a visão do portfólio.
- Gerou toda a documentação reflexiva explicando os *Trade-offs* da escolha (como o limite em memória e conversão da nomenclatura `skip/top`).

---

## 5. Portfólio Polish (Fase 7)

Para o lançamento online, a IA foi orientada a atuar como um **Marketing Engineer**, refinando a apresentação visual do README e as metadados do Swagger.

*   **Design de Experiência (UX) no Swagger:** Injeção de exemplos de preenchimento automático em todos os Schemas de entrada, reduzindo o atrito de quem testa a POC pela primeira vez.
*   **Copywriting Técnico:** Reescrita do README para focar em "Destaques do Projeto" e justificativas arquiteturais de alto impacto (Clean Arch, CQRS, DDD).

---

## 6. Conclusão do IA-Driven
Trabalhar junto com o Agente garantiu padronização excelente de Markdown, validações precisas da estrutura REST e a possibilidade de se focar no design de negócio, deixando as tarefas braçais ("boilerplate") aos cuidados do algoritmo autônomo.
