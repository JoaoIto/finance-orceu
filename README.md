# Orceu - Módulo Financeiro Backend (POC)

Esta é a Prova de Conceito (POC) para o Módulo Financeiro da Plataforma Orceu, com foco total no gerenciamento robusto de contas a pagar (Agendamentos / Schedules Debit) e receber (Credit). A solução adota Clean Architecture, Domain-Driven Design (DDD) e CQRS com tecnologias modernas.

## Stack Tecnológica

* **Linguagem**: Python 3.12+
* **Framework Web**: FastAPI
* **Banco de Dados Relacional**: PostgreSQL
* **Orquestração e Deploy**: Docker & Docker Compose
* **Manipulação e Migração de Dados**: SQLAlchemy & Alembic
* **Testes**: Pytest

---

## 🏃 Instruções para Execução

1. Certifique-se de ter o `Docker` e o `Docker Compose` instalados em sua máquina.
2. Clone este repositório.
3. Crie e/ou preencha um arquivo `.env` na raiz (um exemplo base estará no `.env.example`).
4. Inicialize a orquestração do banco e API com o comando:
   ```bash
   docker-compose up --build -d
   ```
5. O Alembic será executado garantindo a tabela atualizada no Postgres. Além de um seed mínimo que poderá ser auto-injetado.
6. A página interativa oficial do Swagger da API estará acessível via navegador em:
   ```
   http://localhost:8000/docs
   ```

*(Nota: Caso deseje rodar a API puramente em host local sem docker web, basta levantar o `docker-compose up db -d` e startar a API via `uvicorn app.main:app --reload`)*.

---

## 🏗️ Arquitetura e Decisões

Foi decidido utilizar um Design Limpo (**Clean Architecture**) aliado ao **CQRS in-memory**.
Isso significa que o banco de dados é um detalhe de infraestrutura e a API FastAPI atua unicamente como "Deliver mechanism/Interface".
O fluxo das requisições transita entre:
`Router/Endpoint -> Command Handler (Aplicação) -> Domain Entities (Negócio) -> Repository (Infraestrutura)`.

As leituras (`GET`) ignoram as instâncias densas de "Entities" por performance pura, operando os SQLs no `Query Handlers` e devolvendo um `Pydantic Schema (DTO)` ao front-end de forma supersônica.

Para o **Setup Multi-Tenant**, a decisão foi simular em FastAPI um extrator de dependência rigoroso no Cabeçalho HTTP `x-organization-id`. Agendamentos jamais vazarão para a `Organization` B se você passar no header o ID da `Organization` A.

## 📁 Guias Aprofundados (Documentação) 

Para análise corporativa do teste técnico e engenharia formal, verifique a pasta [`/docs`](./docs/):
* 📖 [PRD - Product Requirements Document](./docs/PRD.md)
* ⚙️ [Technical Spec](./docs/Technical_Spec.md)
* 📋 [Plano de Execução](./docs/Execution_Plan.md)
* 🤖 [Desempenho Gen-AI (Usage)](./docs/AI_Usage.md)

---

## ❓ Perguntas Obrigatórias do Teste Técnico

### 1. Quais foram os principais trade-offs da sua solução?
Para construir uma API concisa no contexto de uma "POC", optei por focar na entrega monolítica e fortemente tipada em Python ao invés de microserviços granulares puros com mensageria assíncrona. 
* **Trade-off 1 (Segurança):** Simulei a autenticação (OAUTH/JWT) por uma Injeção Simplificada de Headers. O isolamento de dados no DB é real (A Cláusula `WHERE organization_id = X` existe sempre no base repository acionado), porém sem Token validation, simplificando os testes.
* **Trade-off 2 (Validação de Status no Banco):** O Status ("open", "paid", "overdue") poderia rodar por Cronjob 1x por dia mudando campo nativo na tabela. Contudo, em favor de uma API com tempo real rigoroso, este dado pode ser validado como uma "Property Virtual".

### 2. O que você faria diferente em um ambiente de produção?
* **Mensageria**: Os comandos de inserção do *Payment*, num evento real, poderiam postar em um barramento (Kafka/SQS) comunicando o resto do Orceu que um saldo foi abatido, para reatividade de outros sistemas (estoque, folha de pagamento).
* **Banco de Dados (Read Replica):** Inseriria Read-Replicas no Postgres para escalonar Queries (CQRS) se descolando completamente do Banco de Write (Write Master / SQL Master).
* **Autenticação e CI/CD:** Uso massivo de CI no Github actions e deploy por Terraform. Validação total via Identity Provider (ex: AWS Cognito, Auth0) usando `claim` de token para capturar o `X-Organization-ID` sem chance de spoofing do Client.

### 3. Como sua arquitetura evoluiria para suportar:
**A) Fluxo de Caixa consolidado**
Na POC atual listamos os schedules de débito e crédito pontualmente. O passo futuro para um Fluxo Consolidado (que atua fortemente em Dashboard agregados) seria a inserção de `Materialized Views` no Postgres que consolidam todo valor por dia/mês/ano pre-calculado para leitura instantânea por rotas estelares (Sem gargalos de contagem infinita).

**B) Conciliação Bancária**
Teríamos um módulo independente ou novo Use Case que receberia (provavelmente via Open Banking APIs ou leitura de arquivo OFX) `BankTransactions`. A evolução contaria com um Agente assíncrono (*Anti-Corruption Layer*) tentando realizar `Matches` entre o "Valor X, Data Y, Contato Z" de um `Schedule` contra as transações. Se a probabilidade for alta (acima de 95% de matching), a aplicação dispara um `Command` de Payment transacional automático de status: `Reconciliado`.

**C) Múltiplas obras simultâneas**
Na POC, cada "Obra" estaria tecnicamente vinculada a um `CostCenter` único. Uma organização (`Organization` mestre da construtora) englobaria N CostCenters. O Banco Relacional criado com Postgres isola essas chaves, o que permitiria, do ponto de vista do código, introduzir "Hierarquias de Organização" ou Perfilamento de Usuário. Ex: O usuário João (Role: Engineer) só tem acesso nas Queries se atrelado a IDs das obras onde atua.
