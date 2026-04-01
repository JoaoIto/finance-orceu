# Technical Spec - Especificação Técnica
**Projeto**: Orceu - Módulo Financeiro
**Iniciativa**: POC (Proof of Concept) Backend

---

## 1. Arquitetura

O sistema será construído usando a metodologia **Clean Architecture** (Arquitetura Limpa), guiada pelos princípios do **Domain-Driven Design (DDD)** e segregada nas transações de leitura/escrita com o padrão **CQRS (Command-Query Responsibility Segregation)**. A infraestrutura e persistência das informações ficará centralizada em um banco relacional utilizando **PostgreSQL**. A API será disponibilizada em formato RESTful usando **FastAPI**.

### Adoção de Clean Architecture
As responsabilidades do projeto serão modularizadas em camadas (da mais isolada/interna para a mais dependente/externa):

1. **Domain Layer (Domínio)**
   - Coração da aplicação.
   - Entidades e Value Objects sem nenhuma instrução técnica atrelada (e.g. Models limpos do Nibo adaptados).
   - Abstração (Interfaces/Protocolos) dos repositórios.
   - Encapta regras de negócio e limites de operações (exemplo: não ultrapassar saldo).

2. **Application Layer (Aplicação/Casos de Uso)**
   - Orquestra os Fluxos da Aplicação e regra de fluxo (Use Cases).
   - Divide-se no padrão **CQRS**:
     - `Commands/Handlers`: Rotas mutáveis (`POST`/`PUT`/`DELETE`). Efetuam regras rígidas no repositório de gravação do banco e acionam Eventos (caso necessário).
     - `Queries/Handlers`: Rotas informativas (`GET`). Ignoram as entidades do domínio ricas e geram consultas otimizadas diretamente para DTOs na leitura (alta performance).

3. **Infrastructure Layer (Infraestrutura)**
   - Código que fala com o exterior.
   - Repositórios concretos do banco de dados relacional (`SQLAlchemy`).
   - Módulos de migração com `Alembic`.
   - Setup de orquestração com Docker.

4. **Presentation/Interface Layer (Interface)**
   - API de entrada. Controladores.
   - O framework escolhido (**FastAPI**) atuando como servidor de rotas, dependências, middleware Multi-tenant e Pydantic para Schemas/Validações de Payload REST.

---

## 2. Decisões Técnicas & Trade-offs

* **PostgreSQL Native (Dockerizado):** Melhor suporte a ACID compliance do mercado. O uso de Docker facilita controle de versão local.
* **Separation by Organization Header:** Em prol da agilidade estipulada para a POC e alinhamento do Multi-tenant (isolamento radical de dados), um `Header: x-organization-id` será estritamente validado na `Dependency Injection` do FastAPI, anexando o `tenant_id` atual para todos os Casos de Uso que a requisição tocar, garantindo impossibilidade de misturar agendamentos. Em prd, utilizaríamos claims de JWT.
* **Date Based Status Calculation:** O status de um agendamento ("open", "paid", "overdue") poderia ser mantido via triggers assíncronos de banco. Decidimos usar cálculo DTO ou Query Dinâmica para a leitura: Se a `Due_Date` já passou de `hoje` e o total pago é inferior ao valor do agendamento, o retorno para o client será dinamicamente `"overdue"`.
* **Idempotência (Diferencial):** Ao criar pagamentos parciais transacionais críticos, haverá validação contra redundâncias lógicas nativas pelo FastAPI e `IntegrityError` do SQLAlchemy no mesmo instante temporal.
* **UUIDv4 vs Auto-increment:** Para o banco principal, as PKs serão expostas nas URIs REST como UUID (string) impossibilitando navegação dedutiva de agendamento por ID incremental, melhorando segurança.

---

## 3. Modelagem de Dados e Entidades (Domain Entities)

Os conceitos foram extraídos a partir da estrutura API corporativa base estabelecida pelo Nibo, transmutada para o vocabulário Orceu Construção Civil.

### Entidades Core:

1. `Organization`: (Tenant)
   - *Atributos:* `organization_id(UUID)`, `name`, `tax_id` (CNPJ/CPF).

2. `Contact`: (Terceiros: Empreiteiros, Clientes, Fornecedores)
   - *Atributos:* `contact_id`, `organization_id`, `name`, `cpf_cnpj`, `email`.

3. `Category`: (Plano de Contas/Classificação Orçamentária)
   - *Atributos:* `category_id`, `organization_id`, `name` (Ex: "Material Elétrico", "Cimento"), `type` (Credit/Debit).

4. `CostCenter`: (Centro de Custo / Obras)
   - *Atributos:* `cost_center_id`, `organization_id`, `name` (Ex: "Obra Edifício Alfa - Setor B").

5. `Schedule` (Debit / Credit) - (Agendamento de Conta)
   - *Atributos:* `schedule_id(UUID)`, `organization_id`, `contact_id`, `category_id`, `cost_center_id`.
   - *Dados Financeiros:* `reference`: string, `value`: Decimal, `type`: enum(CREDIT, DEBIT).
   - *Temporalidade:* `issue_date` (Emissão), `due_date` (Vencimento).
   - *Sumarizações Virtuais:* `amount_paid` (Dinâmico), `status` (OPEN, OVERDUE, PAID).

6. `Payment` - (Pagamentos/Recebimentos transacionais efetivos)
   - *Atributos:* `payment_id`, `schedule_id`, `organization_id`, `value_paid`: Decimal, `payment_date`: Date, `receipt_document`: string (nota de comprovante).

### Relacionamentos Invariantes:
- Todo `Schedule`, `Contact`, `CostCenter`, e `Category` obrigatoriamente se remete a **1 e 1** `Organization`. (FK Restritiva).
- Um `Schedule` possui **1 e 1** `Category`, `CostCenter` e `Contact` (não podem ser nulos no Orceu - Restrição Forte).
- Um `Schedule` pode ter **N** `Payments`. (Relação 1:N). O saldo estipulado no Schedule (`value`) deve ser maior ou igual a SOMATÓRIA dos `values_paid` registrados (Regra de Negócio Pura).

---

## 4. Evolução (Respondendo Pergunta Obrigatória / README Base)

*A POC implementa as bases. O que faríamos para escalar?*

**1. Fluxo de Caixa Consolidado:** Em produção, adicionaríamos tabelas fato pré-agregadas (Materialized Views) ou elasticsearch para evitar o processamento de milhões de agendamentos no momento das consultas de Dashboards.
**2. Múltiplas Obras Simultâneas:** O `CostCenter` serve como representativo atual da Obra. Em grande escala, existiria forte RBAC (Role-Based Access Control) dentro de uma `Organization` (e.g. O gerente X só pode ver "CostCenter Y" - Obras Alfa).
**3. Conciliação Bancária:** Incorporaria APIs como Pluggy ou StarkBank para capturar `BankStatements` em uma cronjob periódica. Haveria uma camada Anti-Corruption layer tentando confrontar valor exato, data aproximada e NF entre `BankStatement` (Extrato) e o `Schedule`. O status viraria "Reconciliado Automático" caso batesse.
