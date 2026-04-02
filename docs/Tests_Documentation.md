# Referencial de Testes: Qualidade Orceu API

Este documento detalha a suíte técnica de testes implementada na Fase 5, a qual valida e protege arquiteturalmente este núcleo financeiro contra falhas lógicas e estruturais.

Utilizamos o pacote `pytest` com arquitetura baseada no isolamento das responsabilidades impostas pela _Clean Architecture_. Ou seja, regras de código puro não precisam interagir com bancos de dados.

## 1. Testes de Domínio Puro (`test_domain_rules.py`)

**Localização:** `tests/test_domain_rules.py`
**Objetivo:** Garantir que o "Coração" do sistema (as _Entities_ agregadas) não sofra com bugs matemáticos, sem nenhuma manipulação pelo API.

O teste instancia um Agrado Virtual na memória: uma "Obrigação" de R$ 1.500,00 e força as funções locais para descobrir se ela aceita novos dinheiros ou não:

```python
# Tenta adicionar R$ 600 em algo que só vale R$ 500
def test_schedule_blocks_extravagant_payment():
    schedule = Schedule(
        type=ScheduleType.DEBIT,
        value=Decimal("500.00"), 
        # ... parametros truncados para legibilidade
    )
    # Regra Fundamental: Ele precisa negar pagamentos que ultrapassem o total (500)
    assert schedule.can_receive_payment(Decimal("600.00")) == False
```

Também certificamos que a propriedade `"Virtual"` de mudança de estado ocorre se a gente anexar transações artificialmente, mudando da Inércia `OPEN` para a Completude `PAID`.

## 2. Testes de Endpoints E2E (`test_api_endpoints.py`)

**Localização:** `tests/test_api_endpoints.py`
**Objetivo:** Simular *client requests* (via `httpx` e `TestClient`) batendo no FastAPI e percorrendo banco, garantindo o Middleware Multi-Tenant e o bloqueio global de erros lógicos.

Aqui instanciamos um **SQLite na Memória In-Memory (`sqlite:///:memory:`)**, o que nos permite rodar bancos que duram apenas alguns milisegundos para simular as transações.

```python
@pytest.fixture(scope="module", autouse=True)
def setup_basics():
    # Semeando a API real via TestClient para ter dados Base válidos
    contact = client.post("/api/v1/contacts", json={"name": "Test Contact"}, headers=HEADERS).json()
    ...
    return {"contact_id": contact["id"]}
```

O Teste principal valida se o Router realmente "Cospe" um erro `HTTP 400 Bad Request` com o alerta configurado "Business Logic Violation" caso o programador force um pagamento com estorno/excesso:

```python
def test_create_schedule_and_prevent_overpayment(setup_basics):
    # 1. Cria Fatura valendo $100
    resp = client.post("/api/v1/schedules/debit", json=sched_payload, headers=HEADERS)
    schedule_id = resp.json()["id"]
    
    # 2. Bate na API forçando pagamento de $150!
    pay_resp = client.post(f"/api/v1/schedules/{schedule_id}/payments", json={"value_paid": "150.00"}, headers=HEADERS)
    
    # 3. O Teste força a confirmação! A API tem que obrigatóriamente dar erro (HTTP 400)!
    assert pay_resp.status_code == 400
    assert "Business Logic Violation" in pay_resp.json()["error"]
```

## Como Rodar

Para executar este escopo, com o `.venv` ativado, basta rodar:
```bash
# Seta a raiz como path Python
$env:PYTHONPATH="."  
pytest tests/
```

Isso processará instâncias dinâmicas retornando sucesso de passing! Se você alterar as regras de matemática no `app/domain/entities.py`, estes testes gritarão falhas acusando a regressão!
