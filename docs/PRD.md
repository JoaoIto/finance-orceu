# PRD - Product Requirements Document
**Projeto**: Orceu - Módulo Financeiro
**Iniciativa**: POC (Proof of Concept) Backend

## 1. Problema
O Orceu está em rápida evolução no seu ecossistema de gestão focado no setor da construção civil. Atualmente, há uma lacuna no gerenciamento das particularidades financeiras das contas (receita e despesa) dos projetos, de forma que seja essencial ter um controle robusto de pagamentos e recebimentos, acompanhando fluxo, vencimentos e regras contábeis, garantindo o isolamento da informação por cliente no contexto Multi-tenant da construtora ou empreendimento.

## 2. Objetivo
Construir uma prova de conceito (POC) robusta de backend que servirá como pilar fundacional para o módulo financeiro do Orceu, adotando os rigorosos padrões do mercado como referência (API Nibo). O foco da POC é estabelecer os trilhos de arquitetura aplicando conceitos de Clean Architecture, DDD, e CQRS, orquestrando fluxos primários de agendamentos financeiros (contas a pagar e contas a receber).

## 3. Escopo
O escopo desta POC cobre as primitivas de um módulo de agendamento financeiro, incluindo o cadastro de pré-requisitos lógicos e de categorização.

**In/Scope (O que entra):**
* Gestão básica de pré-requisitos: Criação de Centros de Custo (CostCenters), Categorias (Categories) e Contatos/Participantes (Contacts).
* Gestão de Contas a Pagar: Criação de agendamentos de débitos (Schedules Debit).
* Gestão de Contas a Receber: Criação de agendamentos de créditos (Schedules Credit).
* Efetivação Financeira: Registro transacional de pagamentos (schedules pagos total ou parcialmente) ou recebimentos em conta.
* Cancelamento lógico de agendamentos não integralmente pagos.
* Isolamento lógico de todo o dado acima por Organizacão (Tenant ID).
* Conjunto de queries paginadas e baseadas em filtros elaborados.
* Resumo financeiro consolidado por período consultado.

**Out/Scope (O que fica de fora no momento):**
* Interface Front-end / Portal de Construção Civil.
* Fluxo de Caixa avançado/Consolidado completo por múltiplas obras (Previsto em Roadmaps futuros).
* Conciliação Bancária com APIs de Open Finance (Previsto em Roadmaps futuros).
* Arquivo de anexos (extratos pdf, boletos, nfe).
* Autenticação via IAM/SSO robusto (focaremos no simulação do Auth com envio de ID da organização pelo header).

## 4. Usuários
Embora atuemos no backend, os personas que guiam as necessidades e endpoints do sistema são:
1. **Analista Financeiro da Construtora**: Operador diário de fluxo de recebíveis (medições, clientes, vendas) e pagamentos (fornecedores de material, folha). Ele executa recebimentos parciais e cria conciliações. Precisa de agilidade em buscas textuais.
2. **Gestor de Obra / Gerente Administrativo**: Foca nos resumos de contas a pagar atrelados a determinados "Centros de Custo" (cada obra funciona como um hub financeiro).
3. **Sistemas Integradores/Microserviços Orceu**: Aplicações internas do ecossistema que postarão transações de notas de serviço ou contratos automaticamente gerando obrigações no módulo financeiro (usarão as APIs da POC).

## 5. Funcionalidades Detalhadas (Épicos & User Stories)

### 5.1 Épico: Setup de Domínio Multi-Tenant
- **Criação de Entidades de Apoio**: A API deve possibilitar a criação de `Category`, `CostCenter`, e `Contact`. Todas vinculadas sempre ao escopo de uma `Organization` explícita que está no domínio da requisição.

### 5.2 Épico: Gestão de Contas a Pagar (Accounts Payable)
- **Criação de Agendamento (Schedules Debit)**: Inserir premissa de um valor devido (`value`), um emissor (`contact_id`), tipo (`category_id` e `cost_center_id`) para uma data (`due_date`).
- **Registro de Pagamento (Payment Debit)**: Execução parcial ou total de saldo sobreposto ao Agendamento vinculado. 
- **Cancelamento**: Caso o "Schedule Debit" não esteja finalizado (Totalmente Pago), viabilizar exclusão/arquivamento da programação de conta a pagar.

### 5.3 Épico: Gestão de Contas a Receber (Accounts Receivable)
- **Criação de Agendamento (Schedules Credit)**: Dinamismo espelhado em crédito. Direto do Contact pagador para os cofres do emissor.
- **Registro de Recebimento (Payment Credit)**: Extensão equivalente com liquidação positiva do valor estipulado no schedule de crédito.

### 5.4 Épico: Monitoramento e Listagens (Queries Complexas)
- **Status Control**: Status (Pending/Open, Overdue (Vencida), Paid) e automação reativa desse estado usando base de dados em queries.
- **Filtros Flexíveis**: Pesquisar usando Query Parameters avançados (`status`, `due_date_from`, `due_date_to`, `category_id`).
- **Paginação**: Estruturação estrita de retorno utilizando `page` e `page_size`.
- **Summary**: Gerar totalizadores agrupados baseados em filtros temporais da performance financeira do agendamento (Ex: Total a Receber, Total a Pagar, Total Recebido em atraso).

---
## 6. Referência 
* Nibo Developers Documentation. (Base inspiracional, readaptação rigorosa para o problema civil e isolamento Orceu).
