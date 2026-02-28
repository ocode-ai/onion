#!/usr/bin/env python3
"""
Database Schema Visualizer
Parses Prisma, TypeORM, or SQL schemas and generates an interactive HTML ERD.
"""

import argparse
import json
import os
import re
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Column:
    name: str
    data_type: str
    is_primary: bool = False
    is_nullable: bool = False
    is_unique: bool = False
    default: Optional[str] = None
    is_relation: bool = False


@dataclass
class Relationship:
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    rel_type: str  # "one-to-one", "one-to-many", "many-to-many"


@dataclass
class Table:
    name: str
    columns: list = field(default_factory=list)


@dataclass
class Schema:
    tables: list = field(default_factory=list)
    relationships: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Prisma Parser
# ---------------------------------------------------------------------------

def parse_prisma(file_paths: list[str]) -> Schema:
    schema = Schema()
    full_text = ""
    for fp in file_paths:
        with open(fp, "r") as f:
            full_text += f.read() + "\n"

    # Extract enums for reference
    enums = set(re.findall(r'enum\s+(\w+)\s*\{', full_text))

    # Extract models
    model_blocks = re.finditer(
        r'model\s+(\w+)\s*\{(.*?)\}', full_text, re.DOTALL
    )

    tables_by_name = {}

    for match in model_blocks:
        model_name = match.group(1)
        body = match.group(2)
        table = Table(name=model_name)

        for line in body.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("@@"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            col_name = parts[0]
            if col_name.startswith("@@") or col_name.startswith("//"):
                continue

            raw_type = parts[1]
            is_nullable = raw_type.endswith("?")
            is_array = raw_type.endswith("[]")
            clean_type = raw_type.rstrip("?").rstrip("[]")

            # Determine if this is a relation field
            is_relation = clean_type in tables_by_name or clean_type not in (
                "String", "Int", "Float", "Boolean", "DateTime", "BigInt",
                "Decimal", "Bytes", "Json"
            ) and clean_type not in enums and not clean_type.startswith("Unsupported")

            # Check for @id
            is_primary = "@id" in line

            # Check for @unique
            is_unique = "@unique" in line

            # Check for @default
            default_match = re.search(r'@default\(([^)]+)\)', line)
            default_val = default_match.group(1) if default_match else None

            # Check for @relation
            relation_match = re.search(
                r'@relation\([^)]*fields:\s*\[([^\]]+)\][^)]*references:\s*\[([^\]]+)\]',
                line
            )

            if relation_match:
                fk_fields = [f.strip() for f in relation_match.group(1).split(",")]
                ref_fields = [f.strip() for f in relation_match.group(2).split(",")]
                for fk, ref in zip(fk_fields, ref_fields):
                    rel_type = "one-to-many" if not is_array else "many-to-many"
                    schema.relationships.append(Relationship(
                        from_table=model_name,
                        from_column=fk,
                        to_table=clean_type,
                        to_column=ref,
                        rel_type=rel_type,
                    ))
                # Skip adding relation fields as columns (they're virtual)
                continue

            if is_relation and not relation_match:
                # Virtual relation field without @relation (implicit)
                continue

            display_type = raw_type
            if clean_type in enums:
                display_type = f"enum({clean_type})"

            col = Column(
                name=col_name,
                data_type=display_type,
                is_primary=is_primary,
                is_nullable=is_nullable,
                is_unique=is_unique,
                default=default_val,
            )
            table.columns.append(col)

        tables_by_name[model_name] = table
        schema.tables.append(table)

    # Second pass: re-check relation types for models discovered after first encounter
    full_model_names = {t.name for t in schema.tables}
    # Re-parse to catch relations to models defined later
    schema_pass2 = Schema()
    schema_pass2.tables = schema.tables
    schema_pass2.relationships = schema.relationships

    return schema_pass2


# ---------------------------------------------------------------------------
# SQL Parser
# ---------------------------------------------------------------------------

def parse_sql(directory: str) -> Schema:
    schema = Schema()
    full_sql = ""

    sql_dir = Path(directory)
    sql_files = sorted(sql_dir.rglob("*.sql"))
    for sf in sql_files:
        with open(sf, "r") as f:
            full_sql += f.read() + "\n"

    # Parse CREATE TABLE statements
    create_stmts = re.finditer(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.*?)\)\s*;',
        full_sql, re.DOTALL | re.IGNORECASE
    )

    for match in create_stmts:
        table_name = match.group(1)
        body = match.group(2)
        table = Table(name=table_name)

        # Split by comma, but respect parentheses
        parts = _split_sql_columns(body)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            upper = part.upper().strip()

            # Table-level constraints
            if upper.startswith("PRIMARY KEY"):
                pk_cols = re.findall(r'["`]?(\w+)["`]?', part.split("(", 1)[1].split(")")[0])
                for c in table.columns:
                    if c.name in pk_cols:
                        c.is_primary = True
                continue

            if upper.startswith("FOREIGN KEY"):
                fk_match = re.search(
                    r'FOREIGN\s+KEY\s*\(["`]?(\w+)["`]?\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\(["`]?(\w+)["`]?\)',
                    part, re.IGNORECASE
                )
                if fk_match:
                    schema.relationships.append(Relationship(
                        from_table=table_name,
                        from_column=fk_match.group(1),
                        to_table=fk_match.group(2),
                        to_column=fk_match.group(3),
                        rel_type="one-to-many",
                    ))
                continue

            if upper.startswith(("UNIQUE", "INDEX", "KEY", "CONSTRAINT", "CHECK")):
                continue

            # Column definition
            col_match = re.match(r'["`]?(\w+)["`]?\s+(.+)', part, re.IGNORECASE)
            if not col_match:
                continue

            col_name = col_match.group(1)
            rest = col_match.group(2)

            # Extract type (first word or word with parens)
            type_match = re.match(r'(\w+(?:\([^)]*\))?)', rest)
            col_type = type_match.group(1) if type_match else rest.split()[0]

            is_primary = bool(re.search(r'PRIMARY\s+KEY', rest, re.IGNORECASE))
            is_nullable = "NOT NULL" not in rest.upper()
            is_unique = bool(re.search(r'\bUNIQUE\b', rest, re.IGNORECASE))

            default_match = re.search(r"DEFAULT\s+('?[^',)]+[']?)", rest, re.IGNORECASE)
            default_val = default_match.group(1) if default_match else None

            # Inline REFERENCES
            ref_match = re.search(
                r'REFERENCES\s+["`]?(\w+)["`]?\s*\(["`]?(\w+)["`]?\)', rest, re.IGNORECASE
            )
            if ref_match:
                schema.relationships.append(Relationship(
                    from_table=table_name,
                    from_column=col_name,
                    to_table=ref_match.group(1),
                    to_column=ref_match.group(2),
                    rel_type="one-to-many",
                ))

            col = Column(
                name=col_name,
                data_type=col_type,
                is_primary=is_primary,
                is_nullable=is_nullable,
                is_unique=is_unique,
                default=default_val,
            )
            table.columns.append(col)

        schema.tables.append(table)

    # Also parse ALTER TABLE ... ADD FOREIGN KEY
    alter_fks = re.finditer(
        r'ALTER\s+TABLE\s+["`]?(\w+)["`]?\s+ADD\s+(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(["`]?(\w+)["`]?\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\(["`]?(\w+)["`]?\)',
        full_sql, re.IGNORECASE
    )
    for m in alter_fks:
        schema.relationships.append(Relationship(
            from_table=m.group(1),
            from_column=m.group(2),
            to_table=m.group(3),
            to_column=m.group(4),
            rel_type="one-to-many",
        ))

    return schema


def _split_sql_columns(body: str) -> list[str]:
    """Split SQL column definitions respecting parentheses."""
    parts = []
    depth = 0
    current = []
    for char in body:
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append(''.join(current))
    return parts


# ---------------------------------------------------------------------------
# TypeORM Parser
# ---------------------------------------------------------------------------

def parse_typeorm(directory: str) -> Schema:
    schema = Schema()
    entities_dir = Path(directory)
    ts_files = sorted(entities_dir.rglob("*.ts"))

    for tf in ts_files:
        with open(tf, "r") as f:
            content = f.read()

        # Find @Entity() decorated classes
        entity_match = re.search(
            r'@Entity\([^)]*\)\s*(?:export\s+)?class\s+(\w+)',
            content
        )
        if not entity_match:
            continue

        class_name = entity_match.group(1)
        # Try to get table name from @Entity('name') or @Entity({ name: 'name' })
        table_name_match = re.search(r"@Entity\(['\"](\w+)['\"]\)", content)
        if not table_name_match:
            table_name_match = re.search(r"@Entity\(\{[^}]*name:\s*['\"](\w+)['\"]", content)
        table_name = table_name_match.group(1) if table_name_match else class_name

        table = Table(name=table_name)

        # Find columns with @PrimaryGeneratedColumn or @PrimaryColumn
        for pm in re.finditer(
            r'@(?:PrimaryGeneratedColumn|PrimaryColumn)\([^)]*\)\s*(\w+)\s*[!?]?\s*:\s*(\w+)',
            content
        ):
            table.columns.append(Column(
                name=pm.group(1),
                data_type=pm.group(2),
                is_primary=True,
            ))

        # Find @Column() fields
        for cm in re.finditer(
            r'@Column\(([^)]*)\)\s*(\w+)\s*[!?]?\s*:\s*(\w+)',
            content
        ):
            opts = cm.group(1)
            col_name = cm.group(2)
            col_type = cm.group(3)

            is_nullable = "nullable: true" in opts or "nullable:true" in opts
            is_unique = "unique: true" in opts or "unique:true" in opts
            default_match = re.search(r"default:\s*['\"]?([^'\"}, ]+)", opts)

            table.columns.append(Column(
                name=col_name,
                data_type=col_type,
                is_nullable=is_nullable,
                is_unique=is_unique,
                default=default_match.group(1) if default_match else None,
            ))

        # Find relationships
        for rel_match in re.finditer(
            r'@(ManyToOne|OneToMany|OneToOne|ManyToMany)\(\s*\(\)\s*=>\s*(\w+)',
            content
        ):
            rel_decorator = rel_match.group(1)
            target_entity = rel_match.group(2)

            rel_type_map = {
                "ManyToOne": "one-to-many",
                "OneToMany": "one-to-many",
                "OneToOne": "one-to-one",
                "ManyToMany": "many-to-many",
            }

            # Find JoinColumn if present
            join_col_match = re.search(
                r'@JoinColumn\(\{[^}]*name:\s*[\'"](\w+)[\'"]',
                content[rel_match.end():rel_match.end() + 200]
            )
            from_col = join_col_match.group(1) if join_col_match else f"{target_entity.lower()}_id"

            if rel_decorator in ("ManyToOne", "OneToOne"):
                schema.relationships.append(Relationship(
                    from_table=table_name,
                    from_column=from_col,
                    to_table=target_entity,
                    to_column="id",
                    rel_type=rel_type_map[rel_decorator],
                ))

        schema.tables.append(table)

    return schema


# ---------------------------------------------------------------------------
# HTML Generator
# ---------------------------------------------------------------------------

def schema_to_json(schema: Schema) -> str:
    data = {
        "tables": [],
        "relationships": [],
    }
    for t in schema.tables:
        cols = []
        for c in t.columns:
            cols.append({
                "name": c.name,
                "type": c.data_type,
                "pk": c.is_primary,
                "nullable": c.is_nullable,
                "unique": c.is_unique,
                "default": c.default,
            })
        data["tables"].append({"name": t.name, "columns": cols})

    for r in schema.relationships:
        data["relationships"].append({
            "from": r.from_table,
            "fromCol": r.from_column,
            "to": r.to_table,
            "toCol": r.to_column,
            "type": r.rel_type,
        })

    return json.dumps(data, indent=2)


def generate_html(schema: Schema, output_path: str):
    schema_json = schema_to_json(schema)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Database Schema — ERD</title>
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface-hover: #222632;
    --border: #2a2e3a;
    --text: #e2e4e9;
    --text-dim: #8b8fa3;
    --primary: #6c8dfa;
    --primary-dim: #4a6ad4;
    --pk: #f0b429;
    --fk: #6c8dfa;
    --nullable: #8b8fa3;
    --unique: #a78bfa;
    --rel-one: #34d399;
    --rel-many: #f97316;
    --rel-mm: #ec4899;
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'JetBrains Mono', monospace;
    background: var(--bg);
    color: var(--text);
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }}

  #toolbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 52px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 16px;
    z-index: 100;
    box-shadow: var(--shadow);
  }}

  #toolbar h1 {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
  }}

  #toolbar .stats {{
    font-size: 11px;
    color: var(--text-dim);
    white-space: nowrap;
  }}

  #search {{
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-family: inherit;
    width: 220px;
    outline: none;
    transition: border-color 0.2s;
  }}
  #search:focus {{ border-color: var(--primary); }}
  #search::placeholder {{ color: var(--text-dim); }}

  .toolbar-btn {{
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-dim);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }}
  .toolbar-btn:hover {{ border-color: var(--primary); color: var(--text); }}

  .spacer {{ flex: 1; }}

  #canvas {{
    position: absolute;
    top: 52px;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
    cursor: grab;
  }}
  #canvas:active {{ cursor: grabbing; }}

  #world {{
    position: absolute;
    transform-origin: 0 0;
  }}

  .table-node {{
    position: absolute;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    min-width: 240px;
    max-width: 340px;
    box-shadow: var(--shadow);
    cursor: move;
    user-select: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }}
  .table-node:hover {{ border-color: var(--primary-dim); }}
  .table-node.highlight {{
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary), var(--shadow);
  }}
  .table-node.dimmed {{ opacity: 0.25; }}

  .table-header {{
    padding: 10px 14px;
    background: linear-gradient(135deg, rgba(108,141,250,0.1), rgba(108,141,250,0.03));
    border-bottom: 1px solid var(--border);
    border-radius: 10px 10px 0 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .table-icon {{
    width: 18px; height: 18px;
    fill: var(--primary);
    flex-shrink: 0;
  }}

  .table-name {{
    font-size: 13px;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 0.3px;
  }}

  .col-count {{
    margin-left: auto;
    font-size: 10px;
    color: var(--text-dim);
    background: var(--bg);
    padding: 2px 7px;
    border-radius: 10px;
  }}

  .table-columns {{
    padding: 6px 0;
  }}

  .col-row {{
    padding: 4px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    transition: background 0.15s;
  }}
  .col-row:hover {{ background: var(--surface-hover); }}

  .col-badge {{
    font-size: 9px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 4px;
    flex-shrink: 0;
    letter-spacing: 0.5px;
  }}
  .badge-pk {{ background: rgba(240,180,41,0.15); color: var(--pk); }}
  .badge-fk {{ background: rgba(108,141,250,0.15); color: var(--fk); }}
  .badge-uq {{ background: rgba(167,139,250,0.15); color: var(--unique); }}

  .col-name {{ color: var(--text); flex-shrink: 0; }}
  .col-type {{ color: var(--text-dim); font-size: 11px; margin-left: auto; }}
  .col-nullable {{ color: var(--nullable); font-size: 10px; }}
  .col-default {{ color: var(--text-dim); font-size: 10px; font-style: italic; }}

  svg#relationships {{
    position: absolute;
    top: 0; left: 0;
    pointer-events: none;
    overflow: visible;
  }}

  .rel-path {{
    fill: none;
    stroke-width: 1.5;
    opacity: 0.5;
    transition: opacity 0.2s, stroke-width 0.2s;
  }}
  .rel-path.highlight {{
    opacity: 1;
    stroke-width: 2.5;
  }}
  .rel-path.dimmed {{ opacity: 0.08; }}

  .rel-label {{
    font-size: 10px;
    fill: var(--text-dim);
    pointer-events: none;
    opacity: 0.7;
    transition: opacity 0.2s;
  }}
  .rel-label.dimmed {{ opacity: 0.08; }}
  .rel-label.highlight {{ opacity: 1; fill: var(--text); }}

  #minimap {{
    position: fixed;
    bottom: 16px;
    right: 16px;
    width: 180px;
    height: 120px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    z-index: 50;
    box-shadow: var(--shadow);
  }}
  #minimap canvas {{ width: 100%; height: 100%; }}

  #legend {{
    position: fixed;
    bottom: 16px;
    left: 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 11px;
    z-index: 50;
    box-shadow: var(--shadow);
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }}
  .legend-item:last-child {{ margin-bottom: 0; }}
  .legend-line {{
    width: 24px;
    height: 2px;
    border-radius: 1px;
  }}
</style>
</head>
<body>

<div id="toolbar">
  <svg class="table-icon" viewBox="0 0 24 24" style="width:20px;height:20px;fill:var(--primary)">
    <path d="M3 3h18v18H3V3zm2 2v4h14V5H5zm0 6v2h6v-2H5zm8 0v2h6v-2h-6zm-8 4v4h6v-4H5zm8 0v4h6v-4h-6z"/>
  </svg>
  <h1>DB Schema</h1>
  <span class="stats" id="stats"></span>
  <div class="spacer"></div>
  <input type="text" id="search" placeholder="Search tables..." />
  <button class="toolbar-btn" onclick="resetView()">Reset View</button>
  <button class="toolbar-btn" onclick="autoLayout()">Re-layout</button>
</div>

<div id="canvas">
  <div id="world">
    <svg id="relationships"></svg>
  </div>
</div>

<div id="legend">
  <div class="legend-item"><div class="legend-line" style="background:var(--rel-one)"></div><span>One-to-One</span></div>
  <div class="legend-item"><div class="legend-line" style="background:var(--rel-many)"></div><span>One-to-Many</span></div>
  <div class="legend-item"><div class="legend-line" style="background:var(--rel-mm)"></div><span>Many-to-Many</span></div>
</div>

<div id="minimap"><canvas id="minimap-canvas"></canvas></div>

<script>
const SCHEMA = {schema_json};

const world = document.getElementById('world');
const canvas = document.getElementById('canvas');
const svgRels = document.getElementById('relationships');
const searchInput = document.getElementById('search');
const statsEl = document.getElementById('stats');

let nodes = {{}};
let zoom = 1;
let panX = 60, panY = 80;
let dragging = null;
let dragStartX, dragStartY, dragNodeX, dragNodeY;
let isPanning = false;
let panStartX, panStartY, panStartPanX, panStartPanY;
let selectedTable = null;

const relColors = {{
  'one-to-one': 'var(--rel-one)',
  'one-to-many': 'var(--rel-many)',
  'many-to-many': 'var(--rel-mm)',
}};

// FK columns for badge display
const fkCols = new Set();
SCHEMA.relationships.forEach(r => fkCols.add(r.from + '.' + r.fromCol));

function init() {{
  statsEl.textContent = SCHEMA.tables.length + ' tables · ' + SCHEMA.relationships.length + ' relationships';

  SCHEMA.tables.forEach((t, i) => {{
    const el = createTableNode(t);
    world.appendChild(el);
    nodes[t.name] = {{ el, x: 0, y: 0, w: 0, h: 0 }};
  }});

  autoLayout();
  requestAnimationFrame(() => {{
    Object.keys(nodes).forEach(name => {{
      const rect = nodes[name].el.getBoundingClientRect();
      nodes[name].w = rect.width;
      nodes[name].h = rect.height;
    }});
    drawRelationships();
    updateMinimap();
  }});

  setupPanZoom();

  searchInput.addEventListener('input', (e) => {{
    const q = e.target.value.toLowerCase();
    Object.keys(nodes).forEach(name => {{
      const match = !q || name.toLowerCase().includes(q);
      nodes[name].el.style.display = match ? '' : 'none';
    }});
    drawRelationships();
  }});
}}

function createTableNode(table) {{
  const div = document.createElement('div');
  div.className = 'table-node';
  div.dataset.table = table.name;

  let colsHtml = '';
  table.columns.forEach(c => {{
    let badges = '';
    if (c.pk) badges += '<span class="col-badge badge-pk">PK</span>';
    if (fkCols.has(table.name + '.' + c.name)) badges += '<span class="col-badge badge-fk">FK</span>';
    if (c.unique) badges += '<span class="col-badge badge-uq">UQ</span>';

    let extras = '';
    if (c.nullable) extras += '<span class="col-nullable">?</span>';
    if (c.default) extras += '<span class="col-default">=' + escHtml(c.default) + '</span>';

    colsHtml += '<div class="col-row">' + badges +
      '<span class="col-name">' + escHtml(c.name) + '</span>' +
      extras +
      '<span class="col-type">' + escHtml(c.type) + '</span></div>';
  }});

  div.innerHTML = `
    <div class="table-header">
      <svg class="table-icon" viewBox="0 0 24 24"><path d="M3 3h18v18H3V3zm2 2v4h14V5H5zm0 6v2h6v-2H5zm8 0v2h6v-2h-6zm-8 4v4h6v-4H5zm8 0v4h6v-4h-6z"/></svg>
      <span class="table-name">${{escHtml(table.name)}}</span>
      <span class="col-count">${{table.columns.length}}</span>
    </div>
    <div class="table-columns">${{colsHtml}}</div>`;

  // Drag
  div.addEventListener('mousedown', (e) => {{
    if (e.button !== 0) return;
    e.stopPropagation();
    dragging = table.name;
    const rect = div.getBoundingClientRect();
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    dragNodeX = nodes[table.name].x;
    dragNodeY = nodes[table.name].y;
  }});

  // Click to select
  div.addEventListener('click', (e) => {{
    e.stopPropagation();
    if (Math.abs(e.clientX - dragStartX) > 3 || Math.abs(e.clientY - dragStartY) > 3) return;
    toggleSelect(table.name);
  }});

  return div;
}}

function toggleSelect(name) {{
  if (selectedTable === name) {{
    selectedTable = null;
    Object.values(nodes).forEach(n => n.el.classList.remove('highlight', 'dimmed'));
    svgRels.querySelectorAll('.rel-path, .rel-label').forEach(p => p.classList.remove('highlight', 'dimmed'));
  }} else {{
    selectedTable = name;
    const connected = new Set([name]);
    SCHEMA.relationships.forEach(r => {{
      if (r.from === name) connected.add(r.to);
      if (r.to === name) connected.add(r.from);
    }});

    Object.keys(nodes).forEach(n => {{
      nodes[n].el.classList.toggle('highlight', n === name);
      nodes[n].el.classList.toggle('dimmed', !connected.has(n));
    }});

    svgRels.querySelectorAll('.rel-path').forEach(p => {{
      const from = p.dataset.from, to = p.dataset.to;
      const isConn = from === name || to === name;
      p.classList.toggle('highlight', isConn);
      p.classList.toggle('dimmed', !isConn);
    }});
    svgRels.querySelectorAll('.rel-label').forEach(l => {{
      const from = l.dataset.from, to = l.dataset.to;
      const isConn = from === name || to === name;
      l.classList.toggle('highlight', isConn);
      l.classList.toggle('dimmed', !isConn);
    }});
  }}
}}

function autoLayout() {{
  const cols = Math.ceil(Math.sqrt(SCHEMA.tables.length));
  const padX = 320, padY = 60;

  // Sort tables: those with more relationships first, for better layout
  const relCount = {{}};
  SCHEMA.tables.forEach(t => relCount[t.name] = 0);
  SCHEMA.relationships.forEach(r => {{
    relCount[r.from] = (relCount[r.from] || 0) + 1;
    relCount[r.to] = (relCount[r.to] || 0) + 1;
  }});
  const sorted = [...SCHEMA.tables].sort((a, b) => (relCount[b.name] || 0) - (relCount[a.name] || 0));

  sorted.forEach((t, i) => {{
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = col * padX;
    const y = row * (200 + padY);
    if (nodes[t.name]) {{
      nodes[t.name].x = x;
      nodes[t.name].y = y;
      nodes[t.name].el.style.left = x + 'px';
      nodes[t.name].el.style.top = y + 'px';
    }}
  }});

  requestAnimationFrame(() => {{
    Object.keys(nodes).forEach(name => {{
      const rect = nodes[name].el.getBoundingClientRect();
      nodes[name].w = rect.width / zoom;
      nodes[name].h = rect.height / zoom;
    }});
    drawRelationships();
    updateMinimap();
  }});
}}

function drawRelationships() {{
  svgRels.innerHTML = '';

  // Marker definitions
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');

  ['one', 'many', 'mm'].forEach((type, idx) => {{
    const colors = ['var(--rel-one)', 'var(--rel-many)', 'var(--rel-mm)'];
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrow-' + type);
    marker.setAttribute('viewBox', '0 0 10 7');
    marker.setAttribute('refX', '10');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('markerWidth', '8');
    marker.setAttribute('markerHeight', '6');
    marker.setAttribute('orient', 'auto');
    const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    poly.setAttribute('points', '0 0, 10 3.5, 0 7');
    poly.setAttribute('fill', colors[idx]);
    marker.appendChild(poly);
    defs.appendChild(marker);
  }});

  svgRels.appendChild(defs);

  SCHEMA.relationships.forEach(r => {{
    const fromNode = nodes[r.from];
    const toNode = nodes[r.to];
    if (!fromNode || !toNode) return;
    if (fromNode.el.style.display === 'none' || toNode.el.style.display === 'none') return;

    const x1 = fromNode.x + fromNode.w;
    const y1 = fromNode.y + fromNode.h / 2;
    const x2 = toNode.x;
    const y2 = toNode.y + toNode.h / 2;

    // Determine better connection points
    let sx, sy, ex, ey;
    const dx = toNode.x - (fromNode.x + fromNode.w / 2);
    const dy = toNode.y - (fromNode.y + fromNode.h / 2);

    if (Math.abs(dx) > Math.abs(dy)) {{
      // Connect left/right
      if (dx > 0) {{
        sx = fromNode.x + fromNode.w; sy = fromNode.y + fromNode.h / 2;
        ex = toNode.x; ey = toNode.y + toNode.h / 2;
      }} else {{
        sx = fromNode.x; sy = fromNode.y + fromNode.h / 2;
        ex = toNode.x + toNode.w; ey = toNode.y + toNode.h / 2;
      }}
    }} else {{
      // Connect top/bottom
      if (dy > 0) {{
        sx = fromNode.x + fromNode.w / 2; sy = fromNode.y + fromNode.h;
        ex = toNode.x + toNode.w / 2; ey = toNode.y;
      }} else {{
        sx = fromNode.x + fromNode.w / 2; sy = fromNode.y;
        ex = toNode.x + toNode.w / 2; ey = toNode.y + toNode.h;
      }}
    }}

    const cpDist = Math.min(Math.abs(ex - sx) * 0.5, 120);
    const isHorizontal = Math.abs(dx) > Math.abs(dy);
    let cp1x, cp1y, cp2x, cp2y;

    if (isHorizontal) {{
      cp1x = sx + (dx > 0 ? cpDist : -cpDist); cp1y = sy;
      cp2x = ex + (dx > 0 ? -cpDist : cpDist); cp2y = ey;
    }} else {{
      cp1x = sx; cp1y = sy + (dy > 0 ? cpDist : -cpDist);
      cp2x = ex; cp2y = ey + (dy > 0 ? -cpDist : cpDist);
    }}

    const color = relColors[r.type] || 'var(--rel-many)';
    const markerType = r.type === 'one-to-one' ? 'one' : r.type === 'many-to-many' ? 'mm' : 'many';

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M${{sx}},${{sy}} C${{cp1x}},${{cp1y}} ${{cp2x}},${{cp2y}} ${{ex}},${{ey}}`);
    path.setAttribute('stroke', color);
    path.setAttribute('marker-end', `url(#arrow-${{markerType}})`);
    path.classList.add('rel-path');
    path.dataset.from = r.from;
    path.dataset.to = r.to;
    svgRels.appendChild(path);

    // Label
    const mx = (sx + ex) / 2;
    const my = (sy + ey) / 2 - 8;
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', mx);
    label.setAttribute('y', my);
    label.setAttribute('text-anchor', 'middle');
    label.classList.add('rel-label');
    label.dataset.from = r.from;
    label.dataset.to = r.to;
    label.textContent = r.fromCol + ' → ' + r.toCol;
    svgRels.appendChild(label);
  }});
}}

function setupPanZoom() {{
  canvas.addEventListener('mousedown', (e) => {{
    if (e.button !== 0) return;
    isPanning = true;
    panStartX = e.clientX;
    panStartY = e.clientY;
    panStartPanX = panX;
    panStartPanY = panY;
  }});

  window.addEventListener('mousemove', (e) => {{
    if (dragging) {{
      const dx = (e.clientX - dragStartX) / zoom;
      const dy = (e.clientY - dragStartY) / zoom;
      nodes[dragging].x = dragNodeX + dx;
      nodes[dragging].y = dragNodeY + dy;
      nodes[dragging].el.style.left = nodes[dragging].x + 'px';
      nodes[dragging].el.style.top = nodes[dragging].y + 'px';
      drawRelationships();
      updateMinimap();
    }} else if (isPanning) {{
      panX = panStartPanX + (e.clientX - panStartX);
      panY = panStartPanY + (e.clientY - panStartY);
      applyTransform();
      updateMinimap();
    }}
  }});

  window.addEventListener('mouseup', () => {{
    dragging = null;
    isPanning = false;
  }});

  canvas.addEventListener('wheel', (e) => {{
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const oldZoom = zoom;
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    zoom = Math.max(0.1, Math.min(3, zoom * delta));

    panX = mx - (mx - panX) * (zoom / oldZoom);
    panY = my - (my - panY) * (zoom / oldZoom);
    applyTransform();
    updateMinimap();
  }}, {{ passive: false }});

  canvas.addEventListener('click', (e) => {{
    if (e.target === canvas || e.target === world) {{
      if (selectedTable) toggleSelect(selectedTable);
    }}
  }});

  applyTransform();
}}

function applyTransform() {{
  world.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{zoom}})`;
}}

function resetView() {{
  zoom = 1; panX = 60; panY = 80;
  applyTransform();
  if (selectedTable) toggleSelect(selectedTable);
  updateMinimap();
}}

function updateMinimap() {{
  const mc = document.getElementById('minimap-canvas');
  const ctx = mc.getContext('2d');
  mc.width = 180; mc.height = 120;
  ctx.clearRect(0, 0, 180, 120);

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  Object.values(nodes).forEach(n => {{
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + n.w);
    maxY = Math.max(maxY, n.y + n.h);
  }});

  const pad = 40;
  const rangeX = (maxX - minX + pad * 2) || 1;
  const rangeY = (maxY - minY + pad * 2) || 1;
  const scale = Math.min(180 / rangeX, 120 / rangeY);

  SCHEMA.relationships.forEach(r => {{
    const a = nodes[r.from], b = nodes[r.to];
    if (!a || !b) return;
    ctx.beginPath();
    ctx.moveTo((a.x + a.w / 2 - minX + pad) * scale, (a.y + a.h / 2 - minY + pad) * scale);
    ctx.lineTo((b.x + b.w / 2 - minX + pad) * scale, (b.y + b.h / 2 - minY + pad) * scale);
    ctx.strokeStyle = 'rgba(108,141,250,0.2)';
    ctx.stroke();
  }});

  Object.values(nodes).forEach(n => {{
    ctx.fillStyle = 'rgba(108,141,250,0.6)';
    ctx.fillRect(
      (n.x - minX + pad) * scale,
      (n.y - minY + pad) * scale,
      Math.max(n.w * scale, 3),
      Math.max(n.h * scale, 2)
    );
  }});
}}

function escHtml(s) {{
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}}

init();
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Database Schema Visualizer — Interactive ERD Generator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prisma", nargs="+", help="Path(s) to Prisma schema file(s)")
    group.add_argument("--sql", help="Path to directory containing .sql migration files")
    group.add_argument("--typeorm", help="Path to directory containing TypeORM entity files")
    parser.add_argument("-o", "--output", default="db-schema.html", help="Output HTML file path")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser automatically")

    args = parser.parse_args()

    if args.prisma:
        for p in args.prisma:
            if not os.path.isfile(p):
                print(f"Error: File not found: {p}", file=sys.stderr)
                sys.exit(1)
        schema = parse_prisma(args.prisma)
        print(f"Parsed {len(schema.tables)} models from Prisma schema")

    elif args.sql:
        if not os.path.isdir(args.sql):
            print(f"Error: Directory not found: {args.sql}", file=sys.stderr)
            sys.exit(1)
        schema = parse_sql(args.sql)
        print(f"Parsed {len(schema.tables)} tables from SQL migrations")

    elif args.typeorm:
        if not os.path.isdir(args.typeorm):
            print(f"Error: Directory not found: {args.typeorm}", file=sys.stderr)
            sys.exit(1)
        schema = parse_typeorm(args.typeorm)
        print(f"Parsed {len(schema.tables)} entities from TypeORM")

    print(f"Found {len(schema.relationships)} relationships")

    generate_html(schema, args.output)
    print(f"Generated: {args.output}")

    if not args.no_open:
        abs_path = os.path.abspath(args.output)
        try:
            webbrowser.open("file://" + abs_path)
            print("Opened in browser")
        except Exception:
            print(f"Open manually: file://{abs_path}")


if __name__ == "__main__":
    main()