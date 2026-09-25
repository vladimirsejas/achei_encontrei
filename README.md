# Achei, Encontrei

> Infraestrutura de confiança para reconciliar quem perdeu com quem encontrou.

Projeto particular e proprietário. Todos os direitos reservados.

---

## 🧭 O Norte do projeto — leia antes de qualquer trabalho

**O objetivo principal é tornar o Achei, Encontrei vendável. Ele ainda não é.**

Não vamos chegar lá por acaso, e não vamos chegar lá se esquecermos disso.
O projeto cresce junto com a gente e vai se moldando aos poucos, conforme é
construído. O caminho até algo vendável não está pronto: ele é descoberto
enquanto criamos, procurando as possibilidades escondidas no que já existe.

Toda sessão de trabalho termina com duas perguntas:

1. **O que construímos hoje nos aproxima de algo que alguém pagaria para usar?**
2. **Que possibilidade escondida isso revelou?**

Se a resposta à primeira pergunta for "nada", paramos e reavaliamos a direção
antes de continuar.

### Quando saberemos que chegamos lá

"Vendável" não é sensação, é fato. Chegamos lá quando estes três marcos forem
verdadeiros:

- [ ] **Uso real:** pelo menos uma instituição usa o sistema na operação do dia a dia.
- [ ] **Pagamento real:** alguém pagou pelo serviço (a instituição ou quem recebeu o objeto de volta).
- [ ] **Resultado medido:** a taxa de devolução foi medida e é melhor do que antes do sistema.

---

## 🤖 Diretriz para qualquer IA que trabalhe neste projeto

Copie o bloco abaixo no início de qualquer conversa com uma IA (Claude, ChatGPT,
Gemini ou outra) sobre o projeto:

```
Você está trabalhando no Achei, Encontrei.

CONTEXTO
- É um projeto particular com fins comerciais. Não é projeto acadêmico e não
  deve ser associado a faculdade, disciplina ou professor.
- O idealizador decide. As IAs aconselham, questionam e constroem.
- Leia docs/canonicos/ (na ordem numérica) e docs/decisoes/ antes de propor
  mudanças. O domínio já foi estabilizado; não o reinvente sem motivo.

OBJETIVO PRINCIPAL
- Tornar o projeto vendável. Ele ainda NÃO é.
- O projeto cresce e se molda conforme é construído. Parte do seu trabalho é
  enxergar o que ainda não enxergamos.

SEU MODO DE TRABALHO
- Mantenha o lado criador e preditivo sempre em alerta: aponte, sem esperar
  que peçam, possibilidades escondidas de valor comercial e riscos que estão
  chegando.
- Registre toda possibilidade em docs/oportunidades.md, com status
  (hipótese / validando / confirmada / descartada). Nunca descarte uma ideia
  sem registrar o motivo.
- Diga a verdade sobre viabilidade, mesmo quando desanimar. Uma ilusão agora
  custa mais caro depois.

PRINCÍPIOS DO DOMÍNIO (não negociáveis)
- Match é hipótese, nunca verdade. A IA sugere; a verificação avalia a
  reivindicação. Nunca declarar propriedade automaticamente.
- Custódia é pilar: sempre se sabe quem está com o objeto, onde e desde quando.
- Toda mudança relevante gera um evento auditável.
- Dados pessoais são minimizados e protegidos (LGPD). Documentos sensíveis
  nunca são públicos.
- A legislação faz parte do domínio: prazo de 15 dias (CP art. 169),
  entrega à autoridade competente (CC art. 1.233), achádego (CC art. 1.234).
```

---

## O que é

Quem perde um objeto não sabe onde procurar. Quem encontra não sabe quem é o
dono. As duas pessoas quase nunca se encontram.

O Achei, Encontrei cria a ponte entre elas, com segurança:

```
PERDI → ACHEI → MATCH → VERIFICAÇÃO → CUSTÓDIA → DEVOLUÇÃO → AGRADECIMENTO
```

Instituições que já concentram objetos encontrados (shoppings, rodoviárias,
aeroportos, hotéis, hospitais, universidades, eventos) funcionam como **hubs de
custódia**. Elas resolvem o problema do início vazio (cold start) e são a porta
de entrada comercial do projeto.

---

## Onde estamos

| Etapa | Situação |
|---|---|
| Domínio definido (entidades, estados, eventos, regras jurídicas) | ✅ Concluído |
| Revisão estratégica: começar pelo hub institucional | ✅ Concluído |
| **Fase 0** — Conversar com instituições reais e encontrar um piloto | ⏳ Próximo passo |
| **Fase 1** — Balcão institucional: registro, custódia, prazo legal, devolução, auditoria | ⏳ |
| **Fase 2** — Ponte com o público: busca e formulário "Perdi" | ⏳ |
| **Fase 3** — Inteligência: matching heurístico, depois IA | ⏳ |
| **Fase 4** — Rede entre instituições | ⏳ |

---

## Documentação

| Onde | O quê |
|---|---|
| `docs/canonicos/` | Documentos que valem hoje, numerados na ordem de leitura |
| `docs/historico/` | Documentos substituídos, preservados para contar a evolução |
| `docs/decisoes/` | Uma decisão técnica ou estratégica por arquivo, com data e motivo |
| `docs/oportunidades.md` | Radar de possibilidades comerciais e riscos |

---

## Como rodar

Em construção. As instruções entram aqui junto com o primeiro código.
