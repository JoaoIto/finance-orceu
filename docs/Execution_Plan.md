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
* [x] **[DOC]** Criação do AI_Usage.md rastreando o trabalho da IA.
* [x] **[DOC]** Criação do README.md completo na raiz.
* [x] **[INFRA]** Subir DB relacional (PostgreSQL) usando Docker (docker-compose.yml).
* [x] **[APP]** Scaffold das subpastas para `domain`, `app`, `infra`, e `presenter`.
* [x] **[DOMAIN]** Implementar modelo `Organization`, `Contact`, `Category` e `CostCenter`.
* [x] **[DOMAIN]** Implementar Entidades Base `Schedule` e `Payment`.
* [x] **[APP]** Estabelecer arquitetura base do Command Handler e Query Bus local.
* [x] **[INFRA]** Rodar `alembic init` e escrever Migration Mestre com relacionamentos e schemas.
* [x] **[INFRA]** Construção do Adapter do Repositório (SQLAlchemy).
* [x] **[PRESENTER]** Dependência de Multi-tenant ID por request.
* [x] **[API]** Endpoints `POST`: Setup completo dos básicos (Category, CostCenter, Contacts).
* [x] **[API]** Endpoint `POST /schedules/debit` e `POST /schedules/credit`.
* [x] **[API]** Endpoint `POST /schedules/{id}/payments`. Contabilizando validação de valor teto.
* [x] **[API]** Endpoint `DELETE /schedules/{id}/cancel`.
* [x] **[API]** Endpoint `GET /schedules` suportando paginação nativa (skip/limit), e filtros flexíveis (status, type, due_date_from, etc).
* [x] **[API]** Endpoint `GET /schedules/summary` agrupando valores monetários periódicos.
* [x] **[API]** Endpoint `GET /schedules/{schedule_id}` detalhando o agendamento no padrão Rest.
* [x] **[TESTS]** Codificação de Unit Test para testar bloqueio de super-pagamento e bloqueio de estorno pago.

---

## 4. Registro de Implementação (Fase 3 Executada)

Nesta fase consolidada do projeto, unimos o Scaffold de Infraestrutura, as Definições Estritas de Domínio (DDD) e as Camadas de Interface RESTful (FastAPI), alcançando a totalidade básica dos Milestones 1 a 4.

### 4.1 Estratégia de Isolamento de Domínio (DDD)
Para garantir que a lógica de negócios ficasse separada da persistência, adotou-se o uso maciço do **Pydantic** (`app/domain/entities.py`) para tipagem pura, em oposição aos models do ORM.

**Invariante de Estouro Transacional (Business Rule):**
A regra que estipula *"O limite de pagamento não pode superar o valor do agendamento"* foi consolidada dentro do próprio Agregado `Schedule`:

```python
# app/domain/entities.py
class Schedule(DomainEntity):
    ...
    value: Decimal
    payments: List[Payment] = Field(default_factory=list)

    @property
    def total_paid(self) -> Decimal:
        return sum(p.value_paid for p in self.payments)

    def can_receive_payment(self, amount: Decimal) -> bool:
        """ Impeditivo de Estouro Transacional """
        return (self.total_paid + amount) <= self.value
```

O `CommandHandler` consume esse método para negar pagamentos ilegais, enviando HTTP `400 Bad Request` antes de bater no banco.

### 4.2 Multi-Tenant via Header Middleware
A segurança arquitetural Multi-Tenant foi resolvida injetando no FastAPI um `Depends` que monitora obrigatoriamente um cabeçalho HTTP:

```python
# app/presentation/dependencies.py
async def get_organization_id(x_organization_id: str = Header(...)) -> uuid.UUID:
    return uuid.UUID(x_organization_id)
```
Qualquer endpoint no sistema (como `/contacts`), imediatamente embute esse id e repassa para o Query Handler, o qual filtra a tabela no nível do Repositório Relacional: `.filter(Contact.organization_id == org_id)`.

### 4.3 Database, Alembic e Seeds
Devido a conflitos locais de portas de serviços nativos (como outra instância do postgres rodando), a arquitetura orquestrada pelo Docker utilizou a porta mapeada `5433` (no Host).
A migration *Initial Schema* foi devidamente autogerada pelo Alembic mapeando Relacionamentos (`FOREIGN KEY` e Constraints em `RESTRICT` e `CASCADE`).

Por fim, o arquivo `scripts/seed_db.py` populou com sucesso o Tenant Zero:
`99999999-9999-4999-9999-999999999999` (Orceu Construtora Matriz).

### 4.4 Testabilidade Verificada
O servidor rodou estavelmente (`uvicorn`) e executamos um `curl` de sucesso resgatando os contatos pré-semeados pelo tenant.
Todos os mapeamentos CRUD foram acoplados nos "Routers": `basics.py` (Básicos do ERP) e `schedules.py` (Core Financeiro).

---

## 5. Registro de Implementação (Fase 5 Executada)

Na fase final desta iteração, o foco foi garantir Segurança de Interface (Tratamento limpo de Erros), Documentação expressiva (Swagger orgânico auto-explicativo) e *Quality Assurance* através de testes enxutos `In-Memory`.

### 5.1 Global Exception Handling
O framework FastAPI foi desenhado no `main.py` para eliminar os `try/except` redundantes. Todo repasse transacional proibido que quebra regras de negócio no Domínio emite um `ValueError`. Este é então interceptado no Top-Level:

```python
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "Business Logic Violation", "message": str(exc)},
    )
```
Assim todas as rotas (como de Pagamento) desidratam, e o payload é consistente para o Client Front-end!

### 5.2 Schemas Pydantic como Documentação
Foi inserido `examples=[...]` e `description="..."` nas validações do Pydantic (ex: propriedades de `value_paid`, `receipt_document`, `contact_id`). Isso transforma o Swagger auto-gerado em um "Tutorial Interativo" onde o body do Request já surge preenchido com dados coerentes, impedindo a adivinhação.

### 5.3 Quality Assurance (Pytest Unit & E2E)
Em `tests/` comprovamos a teoria em dois pilares:
- **`test_domain_rules.py`**: Instancia objetos `Schedule` sem tocar em Banco de Dados (Velocidade Máxima), infundindo dinheiro irreal na Entidade apenas para provar que uma transação maior que a dívida retorna _Falso_.
- **`test_api_endpoints.py`**: Acopla o Router num Pool `Static` do SQLite puramente In-Memory. Confirma as proteções _Restful_, confirmando por Ex-Ante a rejeição (HTTP 422 para Auth faltante) e o recebimento de JSONs com `Business Logic Violation` quando regras quebram simulando transações vivas!

---

4. **Professional Swagger & Metadados:** Injeção de tags enriquecidas, descrições detalhadas e link de portfólio no próprio `main.py` injetado diretamente no frontend do Swagger.

---

## 7. Fase Final: Portfólio & Launch Ready

Nesta etapa, o projeto foi blindado com documentação interativa corporativa.

1. **Exemplos Reais em Schemas:** Todos os objetos de entrada (`POST`) agora possuem dados reais de exemplo no Swagger, permitindo testes sem consulta de documentação externa.
2. **Nomenclature Refinement (Nibo Pattern):** Alinhamento total com as terminologias `$top`, `$skip` e `$orderBy` citadas na API oficial do Nibo pesquisada.
3. **README Estratégico:** Reestruturado para destacar "Key Features", Decisões Arquiteturais e Guia de Início Rápido.
