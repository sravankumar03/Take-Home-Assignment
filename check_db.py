"""Extended database validation with full stats."""
import sqlite3

conn = sqlite3.connect('output/asana_simulation.sqlite')

print("=" * 60)
print("ASANA SIMULATION DATABASE - FULL VALIDATION")
print("=" * 60)

# Table counts
tables = [
    'organizations', 'teams', 'users', 'team_memberships',
    'projects', 'sections', 'tasks', 'comments',
    'custom_field_definitions', 'custom_field_values',
    'tags', 'task_tags'
]

print("\n📊 Table Row Counts:")
print("-" * 40)
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count:,}")

# Task distribution
print("\n📋 Task Distribution:")
print("-" * 40)

# Completed vs incomplete
print("\nCompletion Status:")
completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
incomplete = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0").fetchone()[0]
total = completed + incomplete
print(f"  Completed: {completed:,} ({100*completed/total:.1f}%)")
print(f"  Incomplete: {incomplete:,} ({100*incomplete/total:.1f}%)")

# Assigned vs unassigned
print("\nAssignment Status:")
assigned = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id IS NOT NULL").fetchone()[0]
unassigned = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id IS NULL").fetchone()[0]
print(f"  Assigned: {assigned:,} ({100*assigned/total:.1f}%)")
print(f"  Unassigned: {unassigned:,} ({100*unassigned/total:.1f}%)")

# With/without description
print("\nDescription Status:")
with_desc = conn.execute("SELECT COUNT(*) FROM tasks WHERE description IS NOT NULL").fetchone()[0]
without_desc = conn.execute("SELECT COUNT(*) FROM tasks WHERE description IS NULL").fetchone()[0]
print(f"  With description: {with_desc:,} ({100*with_desc/total:.1f}%)")
print(f"  Without description: {without_desc:,} ({100*without_desc/total:.1f}%)")

# Tasks vs subtasks
print("\nTask Hierarchy:")
parent_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NULL").fetchone()[0]
subtasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NOT NULL").fetchone()[0]
print(f"  Parent tasks: {parent_tasks:,}")
print(f"  Subtasks: {subtasks:,}")

# Sample task names
print("\n📝 Sample Task Names:")
print("-" * 40)
for row in conn.execute("SELECT name FROM tasks WHERE parent_task_id IS NULL ORDER BY RANDOM() LIMIT 15").fetchall():
    print(f"  • {row[0]}")

# Sample project names
print("\n📁 Sample Project Names:")
print("-" * 40)
for row in conn.execute("SELECT name FROM projects ORDER BY RANDOM() LIMIT 8").fetchall():
    print(f"  • {row[0]}")

# Team distribution
print("\n👥 Team Department Distribution:")
print("-" * 40)
# (Department is stored in users table)
for row in conn.execute("SELECT department, COUNT(*) as cnt FROM users GROUP BY department ORDER BY cnt DESC").fetchall():
    print(f"  {row[0]}: {row[1]} users")

# Integrity checks
print("\n✅ Integrity Checks:")
print("-" * 40)

# Check temporal consistency
bad_temporal = conn.execute("""
    SELECT COUNT(*) FROM tasks 
    WHERE completed = 1 AND completed_at IS NOT NULL 
    AND completed_at < created_at
""").fetchone()[0]
print(f"  Tasks with completed_at < created_at: {bad_temporal}")

# Check orphaned subtasks
orphans = conn.execute("""
    SELECT COUNT(*) FROM tasks t
    WHERE t.parent_task_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM tasks p WHERE p.id = t.parent_task_id)
""").fetchone()[0]
print(f"  Orphaned subtasks: {orphans}")

# Check FK to users
invalid_assignees = conn.execute("""
    SELECT COUNT(*) FROM tasks t
    WHERE t.assignee_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = t.assignee_id)
""").fetchone()[0]
print(f"  Invalid assignee references: {invalid_assignees}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

conn.close()
