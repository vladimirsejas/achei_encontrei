# 0004 — Decisões de domínio tomadas ao construir o balcão

**Data:** 25/09/2026 · **Status:** aceita · Alimenta o futuro DOMAIN_MODEL v0.2

Ao programar o balcão, cinco pontos que os documentos canônicos deixavam em
aberto precisaram de decisão.

## 1. Significado de EM_CUSTODIA
O ERD diz que todo Achado tem Custódia desde o registro, o que parecia tornar o
estado EM_CUSTODIA redundante. Interpretação adotada:
- **REGISTRADO:** o objeto está com quem encontrou (custódia informal, Fase 2).
- **EM_CUSTODIA:** o objeto está sob custódia formal de um hub institucional.
Um achado registrado no balcão já nasce EM_CUSTODIA.

## 2. Responsável pela custódia é polimórfico
`responsavel_tipo` (PESSOA, OPERADOR ou INSTITUICAO) + `responsavel_id`.
O mesmo vale para `de` e `para` na TransferenciaCustodia.

## 3. O sistema nunca encaminha sozinho à autoridade
O objeto físico continua com alguém. No 10º dia o sistema emite
PRAZO_ENTREGA_PROXIMO_DO_LIMITE (uma única vez por achado) e mostra os prazos
vencidos. Quem age é o custodiante, que registra a entrega pela rota
`/achados/{id}/entrega-autoridade`. Para isso foi criado o evento
**ENTREGA_AUTORIDADE_REGISTRADA**.

## 4. Devolução presencial sem Match
No balcão, a pessoa pode aparecer sem ter passado pelo matching. Por isso
`Devolucao.match_id` é opcional; vira chave estrangeira quando Match existir.

## 5. Verificação proporcional ao risco, sem guardar número de documento
- BAIXO: resumo curto do que a pessoa informou.
- MÉDIO: resumo detalhado (mínimo de 20 caracteres).
- ALTO (documentos): resumo detalhado **e** documento de identificação conferido.
Guardamos só o **tipo** de documento conferido (RG, CNH...), nunca o número (LGPD).
Quem decide é sempre o operador; o sistema só impede verificação fraca demais.

## Nota de arquitetura
Um módulo pode importar o **vocabulário** (enums de `dominio.py`) de outro, desde que
numa direção só. Ex.: `verificacao` usa `NivelRisco` de `itens`; o contrário não acontece.
