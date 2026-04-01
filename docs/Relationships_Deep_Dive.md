# Deep Analysis: Relacionamentos e Restrições (Técnico e Funcional)
**Projeto**: Orceu - Módulo Financeiro Backend
**Escopo**: Entidades, Restrições de Integridade, Eventos de Transição e Isolamento de Multi-Tenant.

Este documento expande o modelo Arquitetural de Entidades (ER), descendo ao nível mais profundo de especificações técnicas, comportamentos em caso de remoção e restrições funcionais exigidas na documentação do teste (Referência: API do Nibo).

---

## 1. O Padrão Mestre de Relacionamento (Multi-Tenant Isolation)

### Relacionamento: `Organization` (1) ↔ (N) `Qualquer Entidade`
**Contexto Técnico**: Todas as tabelas no PostgreSQL (Schedules, Payments, Contacts, Categories, CostCenters) possuem primariamente um campo chamado `organization_id` [Tipo: UUIDv4].
**Contexto Funcional (Isolamento de Tenant)**:
- Para o ecossistema "Orceu", uma Organization é um cluster fechado de dados.
- Todo e qualquer registro inserido, listado, editado ou deletado **obrigatoriamente** sofre a checagem cruzada e indexada no banco: `WHERE organization_id = :current_tenant`.
- **Regra de Exclusão (Técnica)**: `ON DELETE CASCADE`. Isso significa que, se a construtora (Organization) decidir revogar a conta do sistema, apagá-la no banco executará uma reação em cadeia derrubando, em nível de C++ do próprio PostgreSQL, todas as tabelas filhas e financeiras, protegendo contra dados órfãos acidentais por erros de ORM.

---

## 2. A Malha de Dependências Financeiras (Schedules)

A tabela principal de agendamentos (`Schedules`) agrega 3 pontas fundamentais. Um agendamento é uma "Responsabilidade". Você não pode ter uma responsabilidade sem que se saiba: DE QUEM, PARA QUÊ e ONDE.

### 2.1 Relacionamento: `Contact` (1) ↔ (N) `Schedules`
- **Funcional**: O sistema precisa saber o emissor ou receptor do dinheiro. Um *Contact* (Terceirizado/Cliente/Fornecedor) emite uma Nota Fiscal gerando 1 Schedule. Esse mesmo *Contact* futuramente pode emitir dezenas de notas. O campo `document_number` (CPF/CNPJ) do contato garante que os resumos financeiros por credor sejam montados de maneira correta.
- **Técnico (Restrição de Banco)**: `FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE RESTRICT`.
- **Invariante Funcional**: Nunca será possível apagar um "Contact" do banco de dados (exemplo: Fornecedor de Cimento Cimenteira S\A) se existir pelo menos *um* agendamento fiscal atrelado a ele no passado ou no futuro. O banco negará (RESTRICT). Para desativá-lo com segurança no futuro, o ideal será criar um conceito de `is_active` (Logical Soft Delete) em vez de Drop Table.

### 2.2 Relacionamento: `Category` (1) ↔ (N) `Schedules`
- **Funcional**: Categorização (O Que É?). Um agendamento precisa nascer tipificado dentro do plano de contas da empresa. "Isto é um recebimento por Serviço?". "Isto é um Pagamento de Folha?".
- **Técnico**: A Categoria só enxerga schedules originários da exata mesma `organization_id`. O SQL Alchemy usará _Composite Foreign Keys_ lógicas limitando cruzamentos.
- **Transição**: O usuário deve poder filtrar relatórios DRE/Fluxo por esta ID de Categoria. Se deletada, afeta o histórico contábil, logo aplica-se o `ON DELETE RESTRICT`.

### 2.3 Relacionamento: `CostCenter` (1) ↔ (N) `Schedules`
- **Funcional**: Centros de Custos servem para a "Convergência Física". Onde ocorrem as receitas/despesas? Exemplo no fluxo Civil: "Obra Shopping Setor Alfa". Permite rateios. O fato de o Teste do Orceu evidenciar "multiplas obras simultâneas" faz o `CostCenter` ser o coração futuro para Relatórios Consolidados de Múltiplas Obras em dashbords separados.  
- **Técnico**: Similar a Categorias, usa `ON DELETE RESTRICT` (Impede apagar uma obra que possui movimentações contábeis, garantindo compliance financeiro). 

---

## 3. O Relacionamento Crítico-Temporal (Schedules & Payments)

Este é o relacionamento transacional exigido nos padrões "Regras de negócio inegociáveis" do documento. A transição e a liquidação do valor de dinheiro transita aqui. 

### Relacionamento: `Schedule` (1) ↔ (N) `Payments`

- **Funcionalidade (Pagamentos Múltiplos ou Único)**: 
  Schedules modelam a obrigação, e Payments modelam quando e quanto dessa obrigação foi saciada no tempo real e físico bancário. Você pode ter um agendamento original de `R$ 10.000,00` (Schedule) que está sendo pago em 5 transferências (Payments) pix aleatórias de valores soltos.

- **Detalhe Técnico Transacional**:
  - `Schedule` carrega a metadados: Data de Vencimento (`due_date`) e Valor estipulado (`value`).
  - `Payment` carrega carga horária: Valor amortizado (`value_paid`) e Data da Realização (`payment_date`).
  - Um `Payment` carrega estrita dependência UUID daquele "Schedule" referenciado e da "Organization", agindo sob proteção `ON DELETE CASCADE` limitante à instância do *Schedule* em si. 

### Invariantes e Triggers / Domain Rules Complexas

1. **Blindagem de Excesso de Liquidação (Valor Extrapolado)**
   - **Regra**: `SUM(payments.value_paid) <= MAX(schedules.value)`.
   - Um novo `Payment` originado via API (`POST /schedules/debit/{id}/payments`) passará por bloqueio no "Command Handler" (Clean Architecture). O backend somará a conta no instante X, travará o RowLock (`FOR UPDATE` statement) do Schedule, e checará se `Novo_Payment.valor_pago + Soma_Existente > Schedule.value`. Se for verdade, lança uma `HTTPException 422 - Valor superior à obrigação`. 

2. **Blindagem de Estorno de Registro (Não Cancele Conta Paga)**
   - **Regra**: Um agendamento financeiro totalmente pago NÃO pode ser arquivado/cancelado.
   - O comando de cancelamento buscará a agregação citada acima. Caso o saldo atingido mostre que não resta nenhum percentual faltante a ser pago (`Total Pago == Valor do Agendamento`), o domínio travará a deleção. Este é um mecanismo de segurança de auditoria contábil natural de ERPs como Nibo e Totvs.

3. **Status Flexível Reativo Temporal**
   Não deve haver campo físico chamado "Status" na modelagem do banco relacional, e sim nos schemas Pydantic de saída da API:
   - Se a query de leitura `GET /schedules` for feita e retornar no banco que a agregação dos payments relacionados == valor, exportamos na API o status de estado **PAID**.
   - Se ainda faltar valor e a Data Servidor (`Today()`) for MAIOR que a (`due_date`) daquele `Schedule`, a API sinaliza flag em vermelho **OVERDUE** instantâneamente sem rodar cronjobs pesadas durante a madrugada no banco de dados. Um dado reativo performatizado via Views materializadas ou query DTOs simples.
   - Restante entra no default status em progressão **OPEN**.

---

## 4. O Comportamento Operacional do "Soft Delete" e Agregação (CQRS) 

Em conformidade à regra de: *"cancelar agendamento quando permitido"*, um `Schedule` poderá ter a sua remoção via API, porém as informações analíticas necessitam não quebrar o `Entity-Relational (ER)`. 
Adotaríamos sob uma forte perspectiva técnica o seguinte:

* Em nível de Banco: Fazer com que o `DELETE CASCADE` nunca seja engatilhado no dia a dia pelo usuário e sim a criação e controle de estados por colunas como `canceled_at`. 
* Mas atendendo à uma modelagem simples de início de projeto, o SQLAlchemy pode ejetar as rows que não possuem pagamentos usando o `.delete()` nativo, o que, com segurança das regras acima implementadas nos Domínios, executará as checagens com máxima integridade.
