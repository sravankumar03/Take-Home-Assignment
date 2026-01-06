-- Asana Simulation Database Schema
-- SQLite DDL for realistic workspace simulation
-- Designed for RL environment seed data

-- ============================================
-- CORE ENTITIES
-- ============================================

-- Organizations: Top-level workspace container
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Company name
    created_at TIMESTAMP NOT NULL           -- Founding date
);

-- Teams: Departments/squads within the organization
CREATE TABLE teams (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Team name (e.g., "Platform Engineering")
    description TEXT,                       -- Team mission/purpose
    organization_id TEXT NOT NULL,          -- FK to organizations
    created_at TIMESTAMP NOT NULL,          -- Team creation date
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Users: All employees in the workspace
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID v4
    email TEXT NOT NULL UNIQUE,             -- firstname.lastname@company.com
    name TEXT NOT NULL,                     -- Full name
    role TEXT NOT NULL,                     -- junior | mid | senior | lead
    department TEXT NOT NULL,               -- Engineering | Marketing | Product | etc.
    is_active BOOLEAN NOT NULL DEFAULT 1,   -- Account status (95% active, 5% deactivated)
    created_at TIMESTAMP NOT NULL           -- Hire date
);

-- Team Memberships: User-team associations (many-to-many)
CREATE TABLE team_memberships (
    id TEXT PRIMARY KEY,                    -- UUID v4
    team_id TEXT NOT NULL,                  -- FK to teams
    user_id TEXT NOT NULL,                  -- FK to users
    role TEXT NOT NULL DEFAULT 'member',    -- member | lead
    joined_at TIMESTAMP NOT NULL,           -- When user joined team
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(team_id, user_id)                -- Prevent duplicate memberships
);

-- ============================================
-- PROJECT STRUCTURE
-- ============================================

-- Projects: Collections of tasks organized around goals
CREATE TABLE projects (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Project name
    description TEXT,                       -- Project goals and context
    team_id TEXT NOT NULL,                  -- Owning team
    owner_id TEXT NOT NULL,                 -- Project lead (senior+ user)
    status TEXT NOT NULL DEFAULT 'active',  -- active | paused | completed
    created_at TIMESTAMP NOT NULL,          -- Project start date
    due_date DATE,                          -- Target completion (60% have dates)
    archived BOOLEAN NOT NULL DEFAULT 0,    -- Hidden from default views
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Sections: Kanban columns or sprint subdivisions within projects
CREATE TABLE sections (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Section name (e.g., "To Do", "In Progress")
    project_id TEXT NOT NULL,               -- Parent project
    position INTEGER NOT NULL,              -- Order within project (0-indexed)
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- ============================================
-- WORK ITEMS
-- ============================================

-- Tasks: The fundamental unit of work
-- Subtasks are tasks with parent_task_id set (single table inheritance)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Task title
    description TEXT,                       -- Rich text description (20% empty)
    project_id TEXT NOT NULL,               -- Parent project
    section_id TEXT NOT NULL,               -- Current section (Kanban column)
    assignee_id TEXT,                       -- Assigned user (15% NULL = unassigned)
    created_by_id TEXT NOT NULL,            -- Creator
    parent_task_id TEXT,                    -- NULL = task, set = subtask
    due_date DATE,                          -- Target date (10% NULL)
    created_at TIMESTAMP NOT NULL,          -- Creation timestamp
    completed BOOLEAN NOT NULL DEFAULT 0,   -- Completion status
    completed_at TIMESTAMP,                 -- NULL if not completed
    position INTEGER NOT NULL DEFAULT 0,    -- Order within section
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (created_by_id) REFERENCES users(id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
);

-- ============================================
-- COLLABORATION
-- ============================================

-- Comments: Discussion and updates on tasks
CREATE TABLE comments (
    id TEXT PRIMARY KEY,                    -- UUID v4
    task_id TEXT NOT NULL,                  -- Parent task
    author_id TEXT NOT NULL,                -- Comment author
    text TEXT NOT NULL,                     -- Comment content
    created_at TIMESTAMP NOT NULL,          -- Posted timestamp
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- ============================================
-- METADATA & CUSTOM FIELDS
-- ============================================

-- Custom Field Definitions: Schema for user-defined fields
CREATE TABLE custom_field_definitions (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Field name (e.g., "Priority")
    field_type TEXT NOT NULL,               -- enum | number | text | date
    options TEXT,                           -- JSON array for enum options
    organization_id TEXT NOT NULL,          -- Scoped to organization
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Custom Field Values: Actual field data on tasks
CREATE TABLE custom_field_values (
    id TEXT PRIMARY KEY,                    -- UUID v4
    field_id TEXT NOT NULL,                 -- FK to definition
    task_id TEXT NOT NULL,                  -- FK to task
    value TEXT,                             -- Stored as text, parsed by field_type
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    UNIQUE(field_id, task_id)               -- One value per field per task
);

-- Tags: Cross-project labels
CREATE TABLE tags (
    id TEXT PRIMARY KEY,                    -- UUID v4
    name TEXT NOT NULL,                     -- Tag name (e.g., "bug", "p0")
    color TEXT NOT NULL,                    -- Hex color code
    organization_id TEXT NOT NULL,          -- Scoped to organization
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Task Tags: Many-to-many task-tag associations
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,                  -- FK to tasks
    tag_id TEXT NOT NULL,                   -- FK to tags
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- ============================================
-- INDEXES FOR QUERY PERFORMANCE
-- ============================================

CREATE INDEX idx_teams_org ON teams(organization_id);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_memberships_team ON team_memberships(team_id);
CREATE INDEX idx_memberships_user ON team_memberships(user_id);
CREATE INDEX idx_projects_team ON projects(team_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_sections_project ON sections(project_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_section ON tasks(section_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_custom_values_task ON custom_field_values(task_id);
CREATE INDEX idx_task_tags_task ON task_tags(task_id);
