# 0003 — Construir primeiro o fluxo do hub institucional

**Data:** 25/09/2026 · **Status:** proposta (aguardando validação na Fase 0)

## Contexto
O objetivo principal é tornar o projeto vendável. A análise de 16/08/2026
concluiu que um app de achados e perdidos só para o consumidor já tem
concorrentes e não vira negócio sozinho; o mercado que paga é o institucional
(shoppings, rodoviárias, aeroportos, hotéis, hospitais, eventos).
O roteiro v0.1–v0.6 dos documentos canônicos começava pelo consumidor.

## Decisão
Ordem de construção:
1. Fase 0 — validar com 3 a 5 instituições reais, sem código.
2. Fase 1 — balcão: Instituição, Operador, Achado, Custódia, prazo legal,
   verificação conduzida pelo operador, Devolução, auditoria.
3. Fase 2 — ponte com o público: busca e formulário "Perdi".
4. Fase 3 — Match heurístico, depois IA.
5. Fase 4 — rede entre instituições.

## Motivos
- O hub resolve o cold start: já tem objetos.
- O hub pode pagar, ou viabilizar que o dono pague (ver O-01 em oportunidades.md).
- A conformidade legal (CC 1.233/1.234, CP 169, LGPD) é argumento de venda
  para a instituição.

## Consequências
O domínio (DOMAIN_MODEL e ERD) não muda; muda a ordem em que é construído.
A IA deixa de ser o primeiro argumento de venda e passa a ser o que aumenta
a taxa de devolução.
