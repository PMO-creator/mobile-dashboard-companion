
# Plano — Versão mobile do Dashboard MAZ 2026

## Objetivo
Criar um **novo `mobile.html`** com paridade completa de funcionalidades do `index.html` desktop (todas as abas: Gantt, Status Report, REQs, Diretoria — Gantt/SR/Comparativo — e Pauta N2), otimizado para toque e telas ≤768px. Mantendo a arquitetura client-side (Google Sheets API Key no browser).

## Garantia de segurança dos seus arquivos
Você mencionou receio de eu alterar arquivos além do mobile. Compromisso explícito deste plano:

- **Único arquivo criado/modificado:** `mobile.html` (na raiz do repo).
- **NÃO tocarei em:** `index.html`, `AGENTS.md`, `CLAUDE.md`, `ONBOARDING.md`, `Manual/`, `doc-sync/`, `00. Apoio/`, `SERVE_DASHBOARD.bat`, `.github/`, nem em qualquer outro arquivo.
- **Sem git:** não rodo `git add/commit/push` — regra #2 do seu AGENTS.md/CLAUDE.md respeitada.
- **Sem conexão GitHub agora:** trabalhamos só neste ambiente Lovable. Quando estiver aprovado, você mesmo copia o `mobile.html` para o repo e faz o PR do jeito que quiser (branch `dev` → PR para `main`).
- Ao final de cada etapa mostro um diff/resumo do que mudou **apenas em `mobile.html`**.

## Escopo funcional (paridade com desktop)
Cada aba será portada preservando fonte de dados, lógica de filtros e cores/status:

1. **Header + indicador de status** (🟢🟡🔴) e refresh manual.
2. **Cronograma / EAP** com Gantt adaptado a mobile (scroll horizontal + zoom, tarefa em cards colapsáveis como fallback).
3. **Status Report** (KPIs, gráficos Chart.js redimensionados).
4. **Requisições (REQs)** — lista filtrada, busca, detalhe em drawer.
5. **Diretoria** — Gantt Diretoria, Status Report Diretoria, Comparativo de Status.
6. **Pauta N2** com export PPTX (pptxgenjs) — mantém funcionalidade; testo se o export funciona no Safari iOS/Chrome Android.
7. **Filtros globais** (WBS, responsável, status, período) em bottom-sheet mobile.
8. **Exports PDF** (jsPDF + svg2pdf) — mantidos; validados no mobile.

## Estratégia técnica
- **Base:** cópia do `index.html` renomeada para `mobile.html`, depois enxugada e reestilizada. Mesmas dependências CDN (Chart.js 4.5.1, jsPDF 2.5.1, svg2pdf 2.2.3, pptxgenjs 3.12.0) — sem novas libs.
- **Layout:** mobile-first (~360–430px), navegação por **bottom tab bar** + drawer lateral para filtros. Header sticky compacto.
- **Gantt mobile:** dois modos — (a) barra horizontal com scroll+pinch-zoom; (b) toggle para "lista compacta" (cards por tarefa) para leitura rápida.
- **Tabelas → cards:** REQs e Status Report em cards empilhados, com ações em swipe/long-press opcional.
- **Toque:** alvos ≥44×44px, sem hover-only, tooltips convertidos em tap-to-reveal.
- **Performance:** lazy render por aba (só monta Chart.js/Gantt da aba ativa), debounce em filtros.
- **Dados:** mesma API Key e endpoints do `index.html` — copio as funções `fetchCronograma`/`fetchReqs` intactas. Zero mudança na planilha.

## Método de trabalho (respeita CLAUDE.md regra #3)
- Edito `mobile.html` via scripts Python `str.replace()` no bash quando o arquivo crescer, nunca via edit tool cego em blocos grandes.
- Faço em iterações pequenas: (1) esqueleto + header + navegação, (2) uma aba por vez, (3) polimento.
- Depois de cada iteração, você abre `mobile.html` no `SERVE_DASHBOARD.bat` (ou eu levanto preview aqui) e valida antes de seguir.

## Entregáveis
- `mobile.html` funcional, standalone, na raiz.
- Um resumo final listando cada aba portada + notas de teste (o que testar em iOS/Android).
- Nenhum outro arquivo alterado.

## O que preciso confirmar antes de codar
1. Ok criar o `mobile.html` a partir de uma cópia do `index.html` atual que você anexou (5154 linhas)?
2. Você prefere que eu implemente **uma aba por turno** (mais controle, você valida a cada passo) ou **tudo de uma vez** e você revisa no fim?
3. Alguma aba tem prioridade (por ex. começar por REQs ou Diretoria)?
