# Database Migrations - Alembic Guide

## 📋 Overview

Codorch използва Alembic за version control на database schema. Всички промени в моделите се управляват чрез migrations.

## 🎯 Migration Files

### Current Migrations

| Revision | Description | Tables |
|----------|-------------|--------|
| `e6006195c986` | Initial migration | users, projects, tree_nodes, goals, opportunities |

## 🚀 Usage

### 1. Apply Migrations (Upgrade to Latest)

```bash
cd backend
poetry run alembic upgrade head
```

### 2. Check Current Revision

```bash
cd backend
poetry run alembic current
```

### 3. View Migration History

```bash
cd backend
poetry run alembic history --verbose
```

### 4. Rollback (Downgrade)

```bash
# Rollback one version
poetry run alembic downgrade -1

# Rollback to specific revision
poetry run alembic downgrade e6006195c986

# Rollback all (DANGEROUS!)
poetry run alembic downgrade base
```

### 5. Create New Migration (Manual)

```bash
cd backend
poetry run alembic revision -m "Add new table"
```

### 6. Create New Migration (Auto-generate)

```bash
cd backend
poetry run alembic revision --autogenerate -m "Auto-detected changes"
```

**⚠️ Note**: Auto-generate може да не работи перфектно. Винаги проверявайте генерирания код!

## 📁 Table Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    goal TEXT,
    status VARCHAR(50) DEFAULT 'planning',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

### Tree Nodes Table
```sql
CREATE TABLE tree_nodes (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES tree_nodes(id) ON DELETE CASCADE,
    node_type VARCHAR(50) NOT NULL,
    content JSON,
    metadata JSON,
    embedding BYTEA,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

### Goals Table (Module 1)
```sql
CREATE TABLE goals (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tree_node_id UUID REFERENCES tree_nodes(id) ON DELETE SET NULL,
    parent_goal_id UUID REFERENCES goals(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    -- SMART validation
    is_smart_validated BOOLEAN DEFAULT false,
    specific_score FLOAT,
    measurable_score FLOAT,
    achievable_score FLOAT,
    relevant_score FLOAT,
    time_bound_score FLOAT,
    overall_smart_score FLOAT,
    -- Metrics
    metrics JSON,
    target_date TIMESTAMP,
    completion_percentage FLOAT DEFAULT 0.0,
    -- AI
    ai_feedback JSON,
    ai_suggestions JSON,
    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    priority VARCHAR(20),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

### Opportunities Table (Module 2)
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tree_node_id UUID REFERENCES tree_nodes(id) ON DELETE SET NULL,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    -- AI generation
    ai_generated BOOLEAN DEFAULT false,
    generation_prompt TEXT,
    ai_reasoning JSON,
    -- Scoring
    score FLOAT,
    feasibility_score FLOAT,
    impact_score FLOAT,
    innovation_score FLOAT,
    resource_score FLOAT,
    scoring_details JSON,
    -- Business
    target_market TEXT,
    value_proposition TEXT,
    estimated_effort VARCHAR(50),
    estimated_timeline VARCHAR(100),
    required_resources JSON,
    -- Status
    status VARCHAR(50) DEFAULT 'proposed',
    approved_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

## 🔄 Entity Relationships

```
users (1) ──> (*) projects
          └──> (*) opportunities.approved_by

projects (1) ──> (*) tree_nodes
             └──> (*) goals
             └──> (*) opportunities

tree_nodes (1) ──> (*) tree_nodes (self-reference)
               └──> (*) goals.tree_node_id
               └──> (*) opportunities.tree_node_id

goals (1) ──> (*) goals (subgoals)
          └──> (*) opportunities.goal_id
```

## 🛠️ Development Workflow

### Adding a New Model

1. **Update `backend/db/models.py`**
   ```python
   class NewModel(Base):
       __tablename__ = "new_table"
       # ...
   ```

2. **Create Migration**
   ```bash
   cd backend
   poetry run alembic revision -m "Add NewModel table"
   ```

3. **Edit Migration File**
   - Add `op.create_table()` in `upgrade()`
   - Add `op.drop_table()` in `downgrade()`

4. **Apply Migration**
   ```bash
   poetry run alembic upgrade head
   ```

5. **Commit to Git**
   ```bash
   git add backend/alembic/versions/*.py
   git commit -m "feat(db): add NewModel migration"
   ```

### Modifying Existing Model

1. **Update model in `backend/db/models.py`**

2. **Create migration**
   ```bash
   poetry run alembic revision -m "Modify XYZ table"
   ```

3. **Edit migration with alter commands**
   ```python
   # Add column
   op.add_column('table_name', sa.Column('new_col', sa.String(50)))
   
   # Drop column
   op.drop_column('table_name', 'old_col')
   
   # Alter column
   op.alter_column('table_name', 'col_name', type_=sa.Integer())
   ```

## ⚠️ Best Practices

1. **Always review auto-generated migrations** - они могат да имат грешки
2. **Test migrations локално** преди commit
3. **Never modify applied migrations** - създавайте нови
4. **Keep migrations small** - по една промяна на migration
5. **Write reversible migrations** - downgrade трябва да работи
6. **Test both upgrade and downgrade**
7. **Add migrations to version control** - .gitignore НЕ трябва да ги ignore

## 🐛 Troubleshooting

### Migration File Not Found
```bash
# Check migration directory
ls backend/alembic/versions/

# Check .gitignore
grep "alembic" .gitignore
```

### Connection Error
```bash
# Check DATABASE_URL in .env
cat config/.env.dev

# Test connection
psql -h localhost -U postgres -d codorch_dev
```

### Revision Not Found
```bash
# Reset alembic_version table
alembic stamp head

# Or start fresh
DROP TABLE alembic_version;
alembic upgrade head
```

### Dependency Cycle
Migrations се прилагат в ред. Ако имате circular dependencies:
1. Създайте първо таблиците без FK
2. Втора migration добавя FK constraints

## 📚 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/datatype-uuid.html)

---

**Status**: ✅ Initial migration complete  
**Last Updated**: September 30, 2025  
**Revision**: e6006195c986
