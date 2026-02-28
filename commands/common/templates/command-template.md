# Template Padrão para Comandos - Claude Code

> Nota: Commands foram integrados com Skills no Claude Code. Arquivos em `.claude/commands/` continuam funcionando e suportam o mesmo frontmatter. Skills são recomendados para novos trabalhos.

---

## Estrutura YAML Obrigatória

```yaml
---
name: nome-do-comando
description: |
  Descrição clara em 1-2 linhas do propósito do comando.
  Use para [caso de uso principal].
---
```

---

## Tabela de Campos

### Campos Recomendados

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `name` | string | filename sem `.md` | Nome de exibição / slash-command. Lowercase, números, hyphens. Max 64 chars. |
| `description` | string | 1o parágrafo | O que faz e quando usar. Claude usa isso para decisões de invocação. |

### Campos Opcionais

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `argument-hint` | string | — | Hint durante autocomplete. Ex: `[issue-number]`, `[filename] [format]`. |
| `disable-model-invocation` | boolean | `false` | `true` = apenas usuário pode invocar via `/name`. Previne auto-loading. |
| `user-invocable` | boolean | `true` | `false` = escondido do menu `/`. Apenas Claude pode invocar. |
| `allowed-tools` | comma-separated string | — | Ferramentas que Claude pode usar sem permissão quando este command está ativo. |
| `model` | string | — | Override de modelo quando command está ativo. |
| `context` | string | — | Set `fork` para rodar em contexto isolado de subagente. |
| `agent` | string | `general-purpose` | Qual tipo de subagente usar quando `context: fork`. |
| `hooks` | object | — | Hooks com escopo no lifecycle deste command. |

### Controle de Invocação

| Frontmatter | Usuário invoca | Claude invoca | Carregamento de contexto |
|-------------|----------------|---------------|--------------------------|
| *(default)* | Sim | Sim | Descrição sempre carregada; conteúdo completo ao invocar |
| `disable-model-invocation: true` | Sim | Não | Descrição NÃO no contexto; carrega ao invocar pelo usuário |
| `user-invocable: false` | Não | Sim | Descrição sempre carregada; conteúdo completo ao invocar |

### Substituições de String

| Variável | Descrição |
|----------|-----------|
| `$ARGUMENTS` | Todos os argumentos passados ao invocar |
| `$ARGUMENTS[N]` | Argumento específico por índice (0-based) |
| `$N` | Shorthand para `$ARGUMENTS[N]` (`$0`, `$1`, etc.) |
| `${CLAUDE_SESSION_ID}` | ID da sessão atual |

---

## Ferramentas Permitidas (allowed-tools)

### Ferramentas Core

```yaml
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, TodoWrite, Agent, NotebookEdit, AskUserQuestion, Skill
```

### Sintaxe de Permissões

| Regra | Efeito |
|-------|--------|
| `Bash` | Todos os comandos Bash |
| `Bash(npm run *)` | Wildcard para comandos |
| `Bash(npm run build)` | Comando exato |
| `Read(./.env)` | Arquivo específico |
| `Read(src/**)` | Glob pattern |
| `Edit(/docs/**)` | Relativo à raiz do projeto |
| `WebFetch(domain:example.com)` | Fetch com filtro de domínio |
| `Task(Explore)` | Subagente específico |
| `mcp__server__tool` | Ferramenta MCP específica |

---

## Estrutura do Corpo (Máximo ~400 linhas)

### Seções Obrigatórias

```markdown
# Nome do Comando

[Descrição breve - 1-2 frases]

## Objetivo

[O que este comando faz e quando usar]

## Fluxo de Execução

### Passo 1: [Nome]
[Instruções claras]

### Passo 2: [Nome]
[Instruções claras]

## Output Esperado

[Formato de saída esperado]
```

### Seções Opcionais

```markdown
## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| param1 | string | Sim | Descrição |
| param2 | string | Não | Descrição |

## Comandos Relacionados

- `/category/cmd1` - Para X
- `/category/cmd2` - Para Y

## Notas Importantes

- Nota 1
- Nota 2
```

---

## Limites e Regras

### Tamanho Máximo

| Tipo | Limite | Ação se Exceder |
|------|--------|-----------------|
| Comando simples | ~200 linhas | OK |
| Comando médio | ~300 linhas | OK |
| Comando complexo | ~400 linhas | Modularizar |
| **Máximo absoluto** | **400 linhas** | **Obrigatório modularizar** |

### Estratégias de Modularização

1. **Extrair para prompts/** - Seções repetitivas para `common/prompts/`
2. **Dividir em sub-comandos** - `/category/main.md` + `/category/sub1.md`
3. **Referenciar agentes** - `Para detalhes técnicos, use @specialist-agent`

---

## Checklist de Qualidade

### Header YAML
- [ ] `name` em kebab-case (ou derivado do filename)
- [ ] `description` clara em 1-2 linhas
- [ ] Sem campos inválidos (`category`, `tags`, `version`, `updated`, `related_commands`, `related_agents`, `parameters`, `includes`)

### Corpo
- [ ] Objetivo claro
- [ ] Fluxo de execução step-by-step
- [ ] Output esperado definido
- [ ] < 400 linhas total

---

## Exemplo Completo

```yaml
---
name: example-command
description: |
  Comando exemplo demonstrando estrutura padrão Claude Code.
  Use como referência para criar novos comandos.
argument-hint: "[target]"
allowed-tools: Read, Grep, Glob, Bash
---

# Example Command

Comando de exemplo para demonstrar a estrutura correta.

## Objetivo

Demonstrar a estrutura correta de um comando Onion para Claude Code.

## Fluxo de Execução

### Passo 1: Validar Input
- Verificar se `$0` (target) foi fornecido
- Validar formato esperado

### Passo 2: Processar
- Executar lógica principal
- Gerar output

### Passo 3: Finalizar
- Apresentar resultado
- Sugerir próximos passos

## Output Esperado

Resultado formatado com próximos passos sugeridos.
```

### Exemplo com Context Fork

```yaml
---
name: heavy-analysis
description: Análise pesada que roda em contexto isolado.
context: fork
agent: general-purpose
model: opus
---

# Heavy Analysis

Análise que executa em subagente isolado para proteger o contexto principal.

[...]
```

---

## Locais de Armazenamento

| Local | Escopo |
|-------|--------|
| `.claude/commands/` | Projeto |
| `~/.claude/commands/` | Pessoal |

Se um skill e um command compartilham o mesmo nome, o **skill tem precedência**.

---

**Referência**: [reference/docs/claude-code/frontmatter-and-tools-reference.md](../../reference/docs/claude-code/frontmatter-and-tools-reference.md)
