# 0002 — Estrutura de pastas

**Data:** 25/09/2026 · **Status:** aceita

## Decisão
- Layout `src/` no backend: o pacote é instalado, e todas as ferramentas
  (API, testes, migrações, worker) o encontram do mesmo jeito.
- Um módulo por Bounded Context da Arquitetura v0.1: `identidade`, `itens`,
  `correspondencia`, `verificacao`, `auditoria`, mais `compartilhado`.
- Todo módulo tem a mesma forma interna: `dominio.py`, `modelos.py`,
  `esquemas.py`, `servicos.py`, `rotas.py`.
- Dependências num só sentido: rotas → serviços → modelos/domínio.
  Módulos conversam entre si só pelos `servicos.py`.
- Idioma: português para tudo o que nós nomeamos; inglês só onde a
  ferramenta exige (`src`, `tests`, `README.md`...). Nunca acento em nomes
  de arquivo ou código.
- Código de IA de produção fica em `correspondencia/`; experimentos ficam
  em `pesquisa/`, que o backend nunca importa.

## Motivo
Achar qualquer coisa sem perguntar, corrigir num lugar só e evitar
importações circulares.
