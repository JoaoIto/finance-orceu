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

---

## 4. Conclusão do IA-Driven
Trabalhar junto com o Agente garantiu padronização excelente de Markdown, validações precisas da estrutura REST e a possibilidade de se focar no design de negócio, deixando as tarefas braçais ("boilerplate") aos cuidados do algoritmo autônomo.
