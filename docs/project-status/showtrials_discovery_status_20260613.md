# ShowTrials Discovery — Inventário Consolidado Pós Path Normalization

**Data:** 2026-06-13  
**Baseline:** `path-normalization-baseline-20260611`  
**HEAD:** `2cf51da` (`refactor: complete repository path normalization`)

---

# 1. Estado Geral do Projeto

O ciclo de normalização de paths foi concluído em todo o repositório.

Objetivos alcançados:

- Centralização dos paths em `scripts/lib/showtrials_paths.py`
- Eliminação de referências hardcoded para:
  - `/tmp/showtrials-discovery`
  - `/srv/projects/showtrials-discovery`
  - artefatos root-relative antigos
- Auditoria de readiness implementada e validada
- Motores de busca validados após refatoração
- Baseline Git criada para retomadas futuras

Tag de referência:

```text
path-normalization-baseline-20260611
```

---

# 2. Fase A — Corpus Principal

Fonte principal:

```text
showtrials.ru
```

Estado:

- Corpus coletado
- Exportação JSON concluída
- Catálogo mestre produzido
- Taxonomia documental produzida
- Motores de busca funcionais

Métricas atuais:

```text
519 documentos
```

Artefatos principais:

```text
showtrials_master_catalog.tsv
showtrials_document_types_v4.tsv
showtrials_document_index.tsv
```

Status:

```text
VALIDADO
```

---

# 3. Fase B — Motores de Busca

Motores de busca operacionais e testados.

Capacidades atuais:

- busca por processo
- busca por tipo documental
- busca textual
- exportação TSV
- amostragem para auditorias

Exemplos validados:

```bash
showtrials-search-v2.py --process ...
showtrials-search-v2.py --doctype ...
```

Status:

```text
VALIDADO
```

---

# 4. Fase C — Taxonomia Documental

Estado:

```text
CONCLUÍDA
```

Entregas:

- Master Catalog
- Document Index
- Document Types
- Document Types V2
- Document Types V3
- Document Types V4

Auditorias:

- validation v2
- validation v3
- validation v4

Status:

```text
LOW RISK
```

após normalização.

---

# 5. Fase D — Chunk Builder

Estado atual:

```text
NÃO EXECUTADO
```

Importante:

O trabalho de Translation Assets não substitui nem elimina a necessidade da fase D.

Arquitetura pretendida:

```text
Corpus
    ↓
Chunk Builder
    ↓
Semantic Layer
    ↓
Glossary
    ↓
Translation Assets
    ↓
Adaptive Translation
```

Situação:

```text
PENDENTE
```

---

# 6. Fase E — Semantic Layer

## E1 — Foundation

Concluído:

- people index
- canonical people
- literal people
- aliases
- truncations
- merge candidates

Status:

```text
LOW
```

---

## E2 — Organizations

Concluído:

- organization index
- organization families
- hierarchy
- document matrices

Status:

```text
LOW
```

---

## E3 — Roles, Positions e Processes

Concluído:

- roles v2
- positions
- process layer
- process profiles

Status:

```text
LOW
```

---

## E4 — Profiles e Matrizes

Concluído:

- person organization matrix
- centrality
- institution profiles
- institution profiles v2

Status:

```text
LOW
```

---

# 7. Fase G — Glossary

Estado:

```text
CONCLUÍDA
```

Componentes:

- glossary seeds
- canonicalization
- enrichment
- freeze readiness
- validações G3 e G4.1

Status:

```text
LOW
```

---

# 8. Fase T1 — Traduções Históricas Existentes

Fonte:

```text
~/coleta_showtrials/data/showtrials.db
```

Diagnóstico executado.

Resultados:

```text
documentos: 519
traduções: 18
idioma: en
modelo: Google NMT
```

Consulta realizada:

```sql
select count(*) from traducoes;
```

Resultado:

```text
18
```

Status:

```text
IDENTIFICADO
NÃO EXPORTADO
```

Prioridade:

```text
ALTA
```

Motivo:

São pares paralelos reais produzidos sobre o corpus ShowTrials.

---

# 9. Fase T2 — Translation Asset Program

Estrutura criada:

```text
scripts/t-translation-assets
data/t-translation-assets
reports/t-translation-assets
```

Objetivo:

Construir um acervo multilíngue antes da tradução massiva do corpus.

---

# 10. T2.1 — Moscow Trials (English)

Documentos incorporados:

```text
1936-trotskyite-zinovievite-terrorist-centre-en.pdf
1937-anti-soviet-trotskyite-centre-en.pdf
1938-anti-soviet-bloc-rights-trotskyites-en.pdf
```

Local:

```text
translation-assets/source-documents/moscow-trials/en-pdf
```

Texto extraído:

```text
translation-assets/extracted-text/moscow-trials/en-txt
```

Status:

```text
PRONTO
```

Valor:

Transcrições integrais dos três grandes julgamentos.

---

# 11. T2.2 — Processo Tukhachevsky

Documentos incorporados:

Russo:

```text
1937-tukhachevsky-trial-ru-rgaspi-17-171-392.pdf
```

Inglês:

```text
1937-tukhachevsky-trial-en-furr-bobrov-appendix.pdf
```

Status:

```text
COLETADO
NÃO EXTRAÍDO
```

Valor:

Par paralelo acadêmico russo ↔ inglês.

---

# 12. T2.3 — Moscow Trials via MIA

Fonte:

```text
marxists.org
```

Diagnóstico concluído.

Índice identificado:

```text
The Case of the Trotskyite-Zinovievite Terrorist Centre
```

Conteúdo identificado:

- indictment
- examinations
- witness testimonies
- prosecution speeches
- last pleas
- verdict

Estimativa:

```text
37 seções navegáveis
```

Status:

```text
ALTO VALOR
```

---

# 13. T2.4 — Bukharin Trial via MIA

Arquivos coletados:

```text
1.htm
2.htm
3.htm
```

Status:

```text
PARCIAL
```

Próximo passo:

Mapear a estrutura completa do julgamento.

---

# 14. T2.5 — Ezhov Interrogations

Extração executada.

Resultado:

```text
23 documentos
~98 mil caracteres
```

Artefatos produzidos:

```text
ezhov_parallel_documents.tsv
ezhov_parallel_search_corpus.tsv
```

Status:

```text
PESQUISÁVEL
```

Observação:

Atualmente apenas versão inglesa foi processada.

---

# 15. T2.6 — Perpetrator2004

Diagnóstico concluído.

Métricas:

```text
113 links
13 hubs HTML
```

Hubs identificados:

- Lenin
- Kirov
- Yezhov
- Yagoda
- Moscow Show Trials
- Kremlin Affair
- Bukharin
- Tukhachevsky
- Great Terror
- Doctors Plot
- Leningrad Affair
- Khrushchev
- Books

Conclusão:

```text
NÃO É DUPLICATA SIMPLES DO SHOWTRIALS
```

Trata-se de uma fonte independente com potencial de expansão do corpus.

Prioridades:

```text
Show_Trials_Links.htm
Tukhachevsky.htm
documents/Yezhov/Yezhov.htm
```

---

# 16. Fase T3 — Estratégia de Tradução

Pesquisa preliminar realizada.

Tecnologias avaliadas:

- Google Glossary
- Placeholders
- Stopwording
- Adaptive Translation
- AutoML Translation

Conclusões atuais:

```text
Glossary .............. recomendado
Placeholders .......... recomendado
Stopwording ........... recomendado

Adaptive Translation .. potencialmente útil
AutoML Translation .... prematuro
```

Motivo:

Ainda não existe volume suficiente de pares paralelos.

Meta mínima desejável:

```text
100+ documentos paralelos
```

---

# 17. Próximos Passos Recomendados

## Curto Prazo

1. Exportar as 18 traduções do SQLite
2. Extrair PDF russo de Tukhachevsky
3. Extrair PDF inglês de Tukhachevsky
4. Coletar `Show_Trials_Links.htm`
5. Coletar `Tukhachevsky.htm`
6. Coletar `documents/Yezhov/Yezhov.htm`

---

## Médio Prazo

1. Consolidar inventário de Translation Assets
2. Medir volume real de corpus paralelo
3. Avaliar Adaptive Translation novamente
4. Avaliar viabilidade econômica do AutoML

---

## Longo Prazo

1. Executar Chunk Builder (Fase D)
2. Integrar Semantic Layer aos Translation Assets
3. Construir corpus paralelo consolidado
4. Criar pipeline de tradução assistida por glossário
5. Avaliar treinamento adaptativo sobre o domínio Show Trials

---

# Estado Geral

```text
Path Normalization .......... CONCLUÍDA
Search Layer ................. VALIDADA
Catalog Taxonomy ............. CONCLUÍDA
Semantic Layer ............... CONCLUÍDA
Glossary Layer ............... CONCLUÍDA
Translation Assets ........... EM CONSTRUÇÃO
Chunk Builder ............... PENDENTE
Adaptive Translation ........ ESTUDO PRELIMINAR
```
