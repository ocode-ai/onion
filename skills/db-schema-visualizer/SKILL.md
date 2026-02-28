---
name: db-schema-visualizer
description: Generate an interactive ERD (Entity Relationship Diagram) from your Prisma schema, TypeORM entities, or raw SQL migrations. Use when onboarding to a project, reviewing database architecture, or documenting your data model.
allowed-tools: Bash(python *)
---

# Database Schema Visualizer

Generate an interactive HTML ERD that shows your database tables, columns, types, and relationships.

## Usage

Run the visualization script pointing to your schema source:

### Prisma

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/db-schema-visualizer/scripts/visualize.py --prisma prisma/schema.prisma
```

### Multiple Prisma files

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/db-schema-visualizer/scripts/visualize.py --prisma prisma/schema.prisma prisma/schema2.prisma
```

### SQL migrations folder

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/db-schema-visualizer/scripts/visualize.py --sql migrations/
```

### TypeORM entities folder

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/db-schema-visualizer/scripts/visualize.py --typeorm src/entities/
```

This creates `db-schema.html` in the current directory and opens it in your default browser.

## What the visualization shows

- **Interactive ERD**: Draggable table nodes with pan & zoom
- **Columns & types**: All fields with their data types, nullability, defaults
- **Primary keys**: Highlighted with a key icon
- **Relationships**: Arrows showing foreign keys, one-to-many, many-to-many
- **Search**: Filter tables by name
- **Click to highlight**: Click a table to highlight all its relationships
- **Color coding**: Different colors for different relationship types
