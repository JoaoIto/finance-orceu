# Execution Plan - Plano de Execução
**Projeto**: Orceu - Módulo Financeiro
**Iniciativa**: POC Backend Financeiro (FastAPI + Clean Architecture)

---

## 1. Estratégia de Entrega

A entrega desta POC será dividida em **Milestones Táticos** curtos, permitindo validação contínua e rápida iteração (Agile/Iterative approach). Em vez de tentarmos projetar tudo em um único *big-bang*, o desenvolvimento será guiado pelas camadas, começando pelos alicerces do domínio, passando pela infraestrutura de persistência, até alcançar a interface para o usuário final (endpoints REST).

Para simular um modelo real (onde entregas são feitas ao longo da Sprint), adotaremos o uso incisivo da IA para scaffold e testes de unidade nas bases lógicas.

---

## 2. Ordem de Implementação (Roadmap)

### Milestone 1: Documentação e Fundações
A base filosófica e os contratos arquiteturais ganham vida.
1. Elaboração dos Documentos Oficiais (`PRD.md`, `Technical_Spec.md`, `Execution_Plan.md`, `AI_Usage.md`, `README.md`).
2. Definição do esqueleto local da arquitetura (`app/domain`, `app/application`, `app/infrastructure`, `app/presentation`).
3. Setup da orquestração do PostgreSQL via `docker-compose.yml`.

### Milestone 2: Core Domain Model & Casos de Uso (Logics)
Garantir o coração da aplicação livre de impurezas do framework.
4. Codificação das Entities (`Organization`, `Contact`, `Category`, `CostCenter`, `Schedule`, `Payment`).
5. Implementação de Value Objects estruturados.
6. Criação dos contrados formais/Interfaces de Repositórios e CQRS Handlers.
7. Implementação do Caso de Uso de Validação: garantir que o **Saldo a Pagar** não exceda o agendamento real.

### Milestone 3: Persistência & Infraestrutura Relacional
Transformar lógicas abstratas em tabelas no PostgreSQL.
8. Configuração das `SQLAlchemy Models` injetando UUIDs transacionais.
9. Elaboração dos Repositórios concretos (`SQLAlchemyOrganizationRepository`, etc.).
10. Setup do `Alembic` e criação da migração V1 com script unificado contemplando DDLs (Constraints, FKs multi-tenant).
11. Criação do Seed Minímo do Banco (`Organization` default).

### Milestone 4: FastAPI & Presenter Layer
Criação dos Endpoints e injeção do tráfego web real.
12. Construção das Rotas FastAPI focadas nos **Commands** (POST/PUT).
13. Adição do Middleware / Dependência de Autenticação (`x-organization-id`).
14. Construção das Rotas FastAPI focadas em **Queries** (Listagens e Paginação).
15. Conversão e Validação da Entrada/Saída via Schemas (Pydantic).
16. Automação Dinâmica da Lógica do Status (`Open`, `Paid`, `Overdue`).

### Milestone 5: Testes, Polimento e Entrega Final
Garantia de que a POC resolve o problema inicialmente proposto.
17. Script local de execução End-to-End para rodar local.
18. Gravação/Exportação do Swagger formal de uso da API gerada pelo próprio framework.
19. Revisão de código e trade-offs.

---

## 3. Backlog de Tarefas (Pendente e Atualizado)

* [x] **[DOC]** Criação do PRD.md
* [x] **[DOC]** Criação do Technical_Spec.md
* [x] **[DOC]** Criação do Execution_Plan.md
* [ ] **[DOC]** Criação do AI_Usage.md rastreando o trabalho da IA.
* [ ] **[DOC]** Criação do README.md completo na raiz.
* [ ] **[INFRA]** Subir DB relacional (PostgreSQL) usando Docker (docker-compose.yml).
* [ ] **[APP]** Scaffold das subpastas para `domain`, `app`, `infra`, e `presenter`.
* [ ] **[DOMAIN]** Implementar modelo `Organization`, `Contact`, `Category` e `CostCenter`.
* [ ] **[DOMAIN]** Implementar Entidades Base `Schedule` e `Payment`.
* [ ] **[APP]** Estabelecer arquitetura base do Command Handler e Query Bus local.
* [ ] **[INFRA]** Rodar `alembic init` e escrever Migration Mestre com relacionamentos e schemas.
* [ ] **[INFRA]** Construção do Adapter do Repositório (SQLAlchemy).
* [ ] **[PRESENTER]** Dependência de Multi-tenant ID por request.
* [ ] **[API]** Endpoints `POST`: Setup completo dos básicos (Category, CostCenter, Contacts).
* [ ] **[API]** Endpoint `POST /schedules/debit` e `POST /schedules/credit`.
* [ ] **[API]** Endpoint `POST /schedules/{id}/payments`. Contabilizando validação de valor teto.
* [ ] **[API]** Endpoint `DELETE /schedules/{id}/cancel`.
* [ ] **[API]** Endpoint `GET /schedules` suportando `?status=paid&due_date_to=YYYY-MM-DD` com paginação nativa (skip/limit).
* [ ] **[API]** Endpoint `GET /schedules/summary` agrupando valores monetários mensais.
* [ ] **[TESTS]** Codificação de Unit Test para testar bloqueio de super-pagamento e bloqueio de estorno pago.
