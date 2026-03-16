# Query Documentation: GraphQL & Neo4j (Cypher)

This document maps every GraphQL query/mutation to its corresponding Neo4j Cypher query that runs behind the scenes.

---

## 📖 QUERIES (Fetching Data)

---

### 1. Get All Projects

**GraphQL** (run in playground at `http://localhost:8000/graphql`):
```graphql
query {
  projects {
    id
    title
    description
    maxMembers
  }
}
```

**Neo4j Cypher** (runs behind the scenes):
```cypher
MATCH (p:Project) RETURN p
```

**What it does**: Fetches all Project nodes from the graph database and returns their properties.

---

### 2. Get All Projects with Team Members

**GraphQL**:
```graphql
query {
  projects {
    id
    title
    maxMembers
    teamMembers {
      role
      student {
        name
        email
      }
    }
  }
}
```

**Neo4j Cypher** (runs for each project):
```cypher
-- Step 1: Get all projects
MATCH (p:Project) RETURN p

-- Step 2: For each project, get team members
MATCH (s:Student)-[r:MEMBER_OF]->(p:Project {id: $id})
RETURN s.id as student_id, r.role as role

-- Step 3: For each team member, get student details
MATCH (s:Student {id: $id}) RETURN s
```

**What it does**: Uses nested resolvers. First fetches projects, then for each project fetches its team members via the `MEMBER_OF` relationship, then resolves each student's details.

---

### 3. Get All Students with Skills

**GraphQL**:
```graphql
query {
  students {
    id
    name
    email
    skills {
      name
      level
    }
  }
}
```

**Neo4j Cypher** (runs behind the scenes):
```cypher
-- Step 1: Get all students
MATCH (s:Student) RETURN s

-- Step 2: For each student, get their skills
MATCH (s:Student {id: $id})-[:HAS_SKILL]->(sk:Skill)
RETURN sk.id as id, sk.name as name, sk.level as level
```

**What it does**: Fetches all Student nodes, then traverses the `HAS_SKILL` relationship to find each student's connected Skill nodes.

---

### 4. Search Students by Skill (Skill-Based Matching)

**GraphQL**:
```graphql
query {
  studentsBySkill(skillName: "Python", minLevel: 4) {
    name
    email
    skills {
      name
      level
    }
  }
}
```

**Neo4j Cypher**:
```cypher
MATCH (s:Student)-[:HAS_SKILL]->(sk:Skill)
WHERE sk.name =~ '(?i)Python' AND sk.level >= 4
RETURN s
```

**What it does**: Traverses the graph from `Skill` nodes back to `Student` nodes. The `=~` operator performs a **regex match** (case-insensitive), so searching "python" will match "Python".

---

## ✏️ MUTATIONS (Modifying Data)

---

### 5. Apply for a Project

**GraphQL**:
```graphql
mutation {
  applyProject(input: {
    projectId: "p1",
    studentId: "2",
    role: "developer"
  }) {
    id
  }
}
```

**Neo4j Cypher** (3 queries run in sequence):
```cypher
-- Step 1: Duplicate Prevention Check
MATCH (s:Student {id: "2"})-[r:APPLIED_TO|MEMBER_OF]->(p:Project {id: "p1"})
RETURN count(r) as count

-- Step 2: Verify Project Exists
MATCH (p:Project {id: "p1"}) RETURN p.max_members as max_members

-- Step 3: Create the Application (only if Steps 1 & 2 pass)
MATCH (s:Student {id: "2"}), (p:Project {id: "p1"})
CREATE (s)-[r:APPLIED_TO {id: "app_2_p1", status: 'pending', role: "developer"}]->(p)
RETURN r.id as id
```

**What it does**:
1. Checks if the student already has an `APPLIED_TO` or `MEMBER_OF` relationship with the project → **Duplicate Prevention**.
2. Verifies the project exists.
3. Creates a new `APPLIED_TO` relationship (edge) between the Student and Project nodes with `status: pending`.

---

### 6. Approve an Application

**GraphQL**:
```graphql
mutation {
  approveApplication(applicationId: "app_2_p1") {
    success
  }
}
```

**Neo4j Cypher** (3 queries run in sequence):
```cypher
-- Step 1: Get Application Details
MATCH (s:Student)-[r:APPLIED_TO {id: "app_2_p1"}]->(p:Project)
RETURN s.id as studentId, p.id as projectId, r.role as role, p.max_members as max_members

-- Step 2: Member Limit Check
MATCH (:Student)-[:MEMBER_OF]->(p:Project {id: "p1"})
RETURN count(*) as count

-- Step 3: Approve (Delete APPLIED_TO, Create MEMBER_OF)
MATCH (s:Student {id: "2"})-[r:APPLIED_TO {id: "app_2_p1"}]->(p:Project {id: "p1"})
DELETE r
CREATE (s)-[:MEMBER_OF {role: "developer"}]->(p)
RETURN true as success
```

**What it does**:
1. Finds the application relationship by its ID.
2. Counts existing team members to enforce the **max_members limit**.
3. **Deletes** the `APPLIED_TO` edge and **creates** a new `MEMBER_OF` edge → transitions the student from applicant to team member.

---

## 🧪 RECOMMENDED TEST FLOW

Run these in order to test every feature:

| Step | Action | What it Tests |
| :--- | :--- | :--- |
| 1 | Run **Query #3** (students) | View all students and skills |
| 2 | Run **Query #4** (studentsBySkill: "Python") | **Skill-based matching** |
| 3 | Run **Mutation #5** (apply student 2 to p1) | **Application creation** |
| 4 | Run **Mutation #5** again (same inputs) | **Duplicate prevention** (should error) |
| 5 | Run **Mutation #6** (approve app_2_p1) | **Application approval + Role assignment** |
| 6 | Run **Query #2** (projects with teamMembers) | **Team listing** |
| 7 | Keep approving until project is full | **Member limit check** (should error) |

---

## 📊 Graph Relationship Summary

| Relationship | From | To | Properties | Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `HAS_SKILL` | Student | Skill | — | Student possesses this skill |
| `APPLIED_TO` | Student | Project | id, status, role | Pending application |
| `MEMBER_OF` | Student | Project | role | Approved team member |
