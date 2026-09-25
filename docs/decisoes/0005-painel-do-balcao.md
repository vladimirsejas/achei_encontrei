# 0005 — Painel do balcão servido pelo próprio backend

**Data:** 25/09/2026 · **Status:** aceita

## Contexto
A API devolve dados em JSON, que são confusos para quem não é programador.
Para demonstrar o sistema a uma instituição, é preciso uma tela que um gerente
ou um operador de balcão entenda de relance.

## Decisão
Uma página única (HTML + CSS + JavaScript puro, sem bibliotecas) dentro do
pacote, em `achei_encontrei/painel/estatico/`, servida pelo FastAPI em `/painel/`.
A raiz `/` redireciona para o painel.

- Roda com o mesmo comando do servidor: nada a mais para instalar.
- Toda a linguagem é a de quem usa o balcão: "4 objetos esperando o dono",
  "Vence em 4 dias", "Devolver ao dono". Nenhum termo técnico aparece.
- As mensagens de erro de regra de negócio também foram reescritas nessa linguagem.
- Identidade visual: cada objeto é uma etiqueta de papel pardo com o prazo como
  carimbo (verde, amarelo, vermelho). Fonte Atkinson Hyperlegible, criada para
  máxima legibilidade.

## Consequências
Quando o produto crescer (várias telas, login, aplicativo), o painel migra para
um frontend próprio na pasta `frontend/`. Até lá, esta página é a demonstração.
Ainda não há login: qualquer pessoa com acesso ao servidor escolhe o operador.
A autenticação é o próximo requisito antes de qualquer uso real.
