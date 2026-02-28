# Template Padrão para Agentes - Claude Code

---

## Estrutura YAML Obrigatória

```yaml
---
name: nome-em-kebab-case
description: |
  Descrição clara em 1-2 linhas do propósito do agente.
  Use para [caso de uso principal]. Relacionado: @agente1, @agente2.
model: sonnet                    # sonnet | opus | haiku | inherit
tools:                           # Ferramentas Claude Code
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - WebSearch
  - TodoWrite
---
```

---

## Tabela de Campos

### Campos Obrigatórios

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `name` | string | Identificador único. Lowercase e hyphens apenas. | `code-reviewer` |
| `description` | string | Quando Claude deve delegar a este agente. Incluir "use proactively" para auto-delegação. | `Especialista em revisão...` |

### Campos Opcionais

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `tools` | comma-separated string | inherit all | Allowlist de ferramentas. Use `Task(worker, researcher)` para restringir subagentes. |
| `disallowedTools` | comma-separated string | — | Denylist de ferramentas, removidas da lista herdada/especificada. |
| `model` | string | `inherit` | `sonnet`, `opus`, `haiku`, ou `inherit`. |
| `permissionMode` | string | `default` | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, ou `plan`. |
| `maxTurns` | number | — | Máximo de turns agentic antes de parar. |
| `skills` | list of skill names | — | Skills injetadas no contexto do agente no startup (conteúdo completo). |
| `mcpServers` | list/object | — | Nomes de MCP servers ou definições inline disponíveis ao agente. |
| `hooks` | object | — | Lifecycle hooks com escopo neste agente (`PreToolUse`, `PostToolUse`, `Stop`). |
| `memory` | string | — | Escopo de memória persistente: `user`, `project`, ou `local`. |
| `background` | boolean | `false` | Sempre executar como tarefa em background. |
| `isolation` | string | — | Set `worktree` para executar em worktree git temporário. |

---

## Ferramentas Claude Code

### Ferramentas Core

```yaml
tools:
  - Read              # Ler arquivos (texto, imagens, PDFs, notebooks)
  - Write             # Criar ou sobrescrever arquivos
  - Edit              # Substituições exatas em arquivos
  - Glob              # Busca rápida por padrão de arquivo (ex: **/*.ts)
  - Grep              # Busca regex em conteúdo (baseado em ripgrep)
  - Bash              # Executar comandos shell
  - WebSearch         # Pesquisa web
  - WebFetch          # Buscar e processar conteúdo de URL
  - TodoWrite         # Criar e gerenciar listas de tarefas
  - Agent             # Lançar subagentes (alias: Task)
  - NotebookEdit      # Editar cells de Jupyter notebooks
  - AskUserQuestion   # Fazer perguntas ao usuário
  - Skill             # Invocar uma skill na conversa
```

### Ferramentas MCP

Ferramentas MCP usam duplo underscore: `mcp__<server>__<tool>`

| Pattern | Descrição |
|---------|-----------|
| `mcp__<server>` | Todas as ferramentas de um server |
| `mcp__<server>__*` | Wildcard: todas as ferramentas |
| `mcp__<server>__<tool>` | Ferramenta específica |

### Regra de Ouro para MCPs

**Agentes Agnósticos** (maioria):
- Usar APENAS ferramentas core
- MCPs listados na seção "Integrações Opcionais" do corpo

**Agentes Especializados** (exceções):
- `clickup-specialist` → inclui `mcp__ClickUp__*`
- Outros especialistas MCP → incluem seus MCPs no `tools`

### Sintaxe de Permissões

| Regra | Efeito |
|-------|--------|
| `Bash` | Todos os comandos Bash |
| `Bash(npm run *)` | Wildcard para comandos Bash |
| `Read(src/**)` | Glob pattern para leitura |
| `Task(Explore)` | Subagente específico |
| `Task(agent1, agent2)` | Múltiplos subagentes permitidos |
| `mcp__server__tool` | Ferramenta MCP específica |

---

## Estrutura do Corpo do Agente

```markdown
# Nome do Agente

## Identidade e Propósito

Você é o **@nome-do-agente**, especialista em [área].

### Missão
[Descrição da missão principal]

### Princípios
- Princípio 1
- Princípio 2
- Princípio 3

## Configurações Necessárias
<!-- APENAS para agentes especializados (com MCPs) -->

Este agente requer as seguintes variáveis de ambiente:

| Variável | Obrigatória | Descrição | Como Obter |
|----------|-------------|-----------|------------|
| `VAR_NAME` | Sim | Descrição | [Link](url) |

## Integrações Opcionais
<!-- APENAS para agentes agnósticos (sem MCPs) -->

Este agente pode ser potencializado com MCPs quando disponíveis:

| MCP | Ferramentas | Uso |
|-----|-------------|-----|
| ClickUp | `mcp__ClickUp__*` | Gestão de tasks |

## Protocolo de Operação

### Fase 1: [Nome da Fase]
1. Passo 1
2. Passo 2

### Fase 2: [Nome da Fase]
1. Passo 1
2. Passo 2

## Guidelines

### Fazer
- Ação recomendada 1
- Ação recomendada 2

### Evitar
- Anti-pattern 1
- Anti-pattern 2

## Referências

- Agente relacionado: @outro-agente
- Comando relacionado: /categoria/comando
```

---

## Checklist de Validação

### Header YAML
- [ ] `name` único e em kebab-case (lowercase + hyphens)
- [ ] `description` clara em 1-2 linhas
- [ ] `tools` com nomes Claude Code válidos (PascalCase)
- [ ] Sem campos inválidos (`color`, `priority`, `category`, `expertise`, `related_agents`, `related_commands`, `version`, `updated`)

### Corpo
- [ ] Seção "Identidade e Propósito"
- [ ] Seção "Protocolo de Operação" com fases
- [ ] Seção "Guidelines"
- [ ] Seção "Configurações" OU "Integrações Opcionais"

---

## Exemplos

### Exemplo 1: Agente Agnóstico

```yaml
---
name: code-reviewer
description: |
  Especialista em revisão de código focado em qualidade, segurança e padrões.
  Use para reviews de PRs, validação de código e identificação de problemas.
model: opus
tools:
  - Read
  - Grep
  - Bash
  - WebSearch
  - TodoWrite
---

# Code Reviewer

## Identidade e Propósito
[...]

## Integrações Opcionais
[...]

## Protocolo de Operação
[...]
```

### Exemplo 2: Agente Especializado (com MCP)

```yaml
---
name: clickup-specialist
description: |
  Especialista em ClickUp MCP para otimizações técnicas e operações em bulk.
  Use para operações avançadas no ClickUp, automações e integrações.
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Grep
  - WebSearch
  - TodoWrite
  - Bash
  - mcp__ClickUp__clickup_search
  - mcp__ClickUp__clickup_create_task
  - mcp__ClickUp__clickup_update_task
  - mcp__ClickUp__clickup_get_task
  - mcp__ClickUp__clickup_create_task_comment
---

# ClickUp Specialist

## Identidade e Propósito
[...]

## Configurações Necessárias

| Variável | Obrigatória | Descrição | Como Obter |
|----------|-------------|-----------|------------|
| `CLICKUP_API_TOKEN` | Sim | Token de API | [ClickUp Settings](https://app.clickup.com/settings/apps) |
| `CLICKUP_WORKSPACE_ID` | Sim | ID do workspace | URL do ClickUp |

## Protocolo de Operação
[...]
```

### Exemplo 3: Agente com Campos Avançados

```yaml
---
name: security-auditor
description: |
  Auditor de segurança que analisa código proativamente.
  Use proactively para detecção automática de vulnerabilidades.
model: opus
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebSearch
disallowedTools: Write, Edit
permissionMode: plan
maxTurns: 15
background: true
---

# Security Auditor
[...]
```

---

## Locais de Armazenamento (por prioridade)

| Local | Escopo | Prioridade |
|-------|--------|------------|
| `--agents` CLI flag (JSON) | Sessão atual | 1 (mais alta) |
| `.claude/agents/` | Projeto atual | 2 |
| `~/.claude/agents/` | Todos os projetos | 3 |
| Plugin `agents/` directory | Onde habilitado | 4 (mais baixa) |

---

**Referência**: [reference/docs/claude-code/frontmatter-and-tools-reference.md](../../reference/docs/claude-code/frontmatter-and-tools-reference.md)
