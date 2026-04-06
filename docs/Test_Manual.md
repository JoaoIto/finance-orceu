# 📑 Guia de Testes Passo a Passo (Manual de Requisições POST)

Este documento foi criado para facilitar a apresentação do projeto. Abaixo, você encontrará o fluxo lógico para testar todas as funcionalidades do sistema Orceu Financeiro, com corpos JSON prontos para copiar e colar.

---

## 🔑 Configuração Inicial Obrigatória

Em todas as requisições abaixo, você deve incluir o seguinte Header Parâmetro:
- **Key:** `x-organization-id`
- **Value:** `99999999-9999-4999-9999-999999999999` (ID da Organização padrão do Seed)

---

## 🛠️ Etapa 1: Cadastros Básicos (Infraestrutura)

Antes de criar agendamentos, precisamos de contatos, categorias e centros de custo.

### 1.1. Criar um Contato (Fornecedor/Cliente)
- **Rota:** `POST /api/v1/contacts`
- **O que faz:** Cadastra uma entidade externa que receberá ou enviará dinheiro.
- **Corpo JSON:**
```json
{
  "name": "Construtora Horizonte Ltda",
  "document_number": "12.345.678/0001-99",
  "email": "financeiro@horizonte.com.br"
}
```
- **Resposta Esperada:** `201 Created` com o ID gerado.
- **O que isso quer dizer?** O sistema agora reconhece esta empresa como um favorecido válido. **Copie o "id" recebido.**

### 1.2. Criar uma Categoria Financeira
- **Rota:** `POST /api/v1/categories`
- **O que faz:** Classifica a natureza da despesa ou receita.
- **Corpo JSON:**
```json
{
  "name": "Materiais de Acabamento"
}
```
- **Resposta Esperada:** `201 Created`.
- **O que isso quer dizer?** Você criou uma "etiqueta" para o seu plano de contas. **Copie o "id" recebido.**

### 1.3. Criar um Centro de Custo (Obra)
- **Rota:** `POST /api/v1/cost_centers`
- **O que faz:** Identifica para qual projeto ou obra o dinheiro está indo.
- **Corpo JSON:**
```json
{
  "name": "Edifício Solar - Torre Norte"
}
```
- **Resposta Esperada:** `201 Created`.
- **O que isso quer dizer?** A despesa será vinculada especificamente a esta obra. **Copie o "id" recebido.**

---

## 💰 Etapa 2: Movimentações Financeiras (Schedules)

Agora vamos criar as contas a pagar e receber utilizando os IDs copiados acima.

### 2.1. Criar um Agendamento de Débito (Conta a Pagar)
- **Rota:** `POST /api/v1/schedules/debit`
- **O que faz:** Registra uma dívida que a empresa possui.
- **Corpo JSON (Substitua os UUIDs pelos que você copiou):**
```json
{
  "contact_id": "COLE_O_ID_DO_CONTATO_AQUI",
  "category_id": "COLE_O_ID_DA_CATEGORIA_AQUI",
  "cost_center_id": "COLE_O_ID_DO_CENTRO_DE_CUSTO_AQUI",
  "description": "Compra de Pisos Porcelanato",
  "value": 5000.00,
  "issue_date": "2026-04-01",
  "due_date": "2026-05-15"
}
```
- **Resposta Esperada:** `201 Created`. Note que o campo `"status"` virá como `"OPEN"`.
- **O que isso quer dizer?** O sistema gerou uma obrigação financeira pendente. **Copie o "id" deste agendamento.**

### 2.2. Criar um Agendamento de Crédito (Conta a Receber)
- **Rota:** `POST /api/v1/schedules/credit`
- **O que faz:** Registra um valor que a empresa espera receber.
- **Corpo JSON:**
```json
{
  "contact_id": "COLE_O_ID_DO_CONTATO_AQUI",
  "category_id": "COLE_O_ID_DA_CATEGORIA_AQUI",
  "cost_center_id": "COLE_O_ID_DO_CENTRO_DE_CUSTO_AQUI",
  "description": "Medição de Serviços Abril",
  "value": 12000.00,
  "issue_date": "2026-04-05",
  "due_date": "2026-04-30"
}
```
- **Resposta Esperada:** `201 Created`.

---

## 💳 Etapa 3: Liquidação e Pagamentos

Aqui testamos a lógica de abatimento de saldo.

### 3.1. Realizar um Pagamento (Baixa Parcial)
- **Rota:** `POST /api/v1/schedules/{id}/payments` (Substitua `{id}` pelo ID do débito criado em 2.1)
- **O que faz:** Registra que você pagou uma parte da dívida.
- **Corpo JSON:**
```json
{
  "value_paid": 2000.00,
  "payment_date": "2026-04-10",
  "receipt_document": "COMPROVANTE-VOUCHER-001"
}
```
- **Resposta Esperada:** `201 Created`.
- **O que isso quer dizer?** Você amortizou R$ 2.000 da dívida de R$ 5.000. Se consultar o agendamento agora, verá que o `total_paid` subiu, mas o status continua `OPEN`.

### 3.2. Teste de Erro: Estouro Transacional (Regra de Negócio)
- **Rota:** `POST /api/v1/schedules/{id}/payments`
- **O que faz:** Tenta pagar um valor maior do que o saldo restante para testar a robustez do sistema.
- **Corpo JSON:**
```json
{
  "value_paid": 4000.00,
  "payment_date": "2026-04-11",
  "receipt_document": "ERRO-TESTE"
}
```
- **Resposta Esperada:** `400 Bad Request`.
- **Mensagem:** `"Business Logic Violation: Estouro Transacional. O valor (4000.00) excede o saldo restante da conta (3000.00)."`
- **O que isso quer dizer?** A **Arquitetura Clean** barrou a operação incorreta na camada de Domínio, garantindo a integridade financeira.

### 3.3. Pagamento de Quitação (Status PAID)
- **Rota:** `POST /api/v1/schedules/{id}/payments`
- **Corpo JSON:**
```json
{
  "value_paid": 3000.00,
  "payment_date": "2026-04-12",
  "receipt_document": "QUITACAO-FINAL"
}
```
- **O que isso quer dizer?** Ao pagar o saldo exato restante, o status do agendamento mudará automaticamente para `PAID` na próxima consulta.

---

## 📊 Consulta Final de Resumo
- **Rota:** `GET /api/v1/schedules/summary?due_date_from=2026-04-01&due_date_to=2026-05-31`
- **O que ver?** O sistema mostrará o consolidado de Débitos (5000), Créditos (12000) e o Saldo Projetado (7000).
