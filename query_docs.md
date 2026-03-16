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

### 5. Create a New Project

**GraphQL**:
```graphql
mutation {
  createProject(input: {
    id: "p3",
    title: "Mobile App",
    description: "Building a cross-platform mobile app",
    maxMembers: 4
  }) {
    project {
      id
      title
      maxMembers
    }
  }
}
```

**Neo4j Cypher** (2 queries run in sequence):
```cypher
-- Step 1: Check if project already exists
MATCH (p:Project {id: "p3"}) RETURN p

-- Step 2: Create the project node
CREATE (p:Project {id: "p3", title: "Mobile App", description: "Building a cross-platform mobile app", max_members: 4})
RETURN p
```

**What it does**: First checks if a project with that ID already exists (prevents duplicates), then creates a new `Project` node in the graph with the given properties.

---

### 6. Create a New Student

**GraphQL**:
```graphql
mutation {
  createStudent(input: {
    id: "5",
    name: "Samarth",
    email: "samarth@gmail.com"
  }) {
    student {
      id
      name
      email
    }
  }
}
```

**Neo4j Cypher** (2 queries run in sequence):
```cypher
-- Step 1: Check if student already exists
MATCH (s:Student {id: "5"}) RETURN s

-- Step 2: Create the student node
CREATE (s:Student {id: "5", name: "Samarth", email: "samarth@gmail.com"})
RETURN s
```

**What it does**: Validates that no student with the same ID exists, then creates a new `Student` node in the graph.

---

### 7. Add a Skill to a Student

**GraphQL**:
```graphql
mutation {
  addSkillToStudent(input: {
    studentId: "5",
    skillName: "Flutter",
    level: 5
  }) {
    success
  }
}
```

**Neo4j Cypher** (2 queries run in sequence):
```cypher
-- Step 1: Check student exists
MATCH (s:Student {id: "5"}) RETURN s

-- Step 2: Create/find the skill and link it to the student
MATCH (s:Student {id: "5"})
MERGE (sk:Skill {name: "Flutter"})
ON CREATE SET sk.id = "s_flutter", sk.level = 5
MERGE (s)-[:HAS_SKILL]->(sk)
RETURN true as success
```

**What it does**: Verifies the student exists, then uses `MERGE` to either find or create the `Skill` node and creates a `HAS_SKILL` relationship between the student and the skill. `MERGE` prevents duplicate skill nodes.

---

### 8. Apply for a Project

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

### 9. Approve an Application

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
| 1 | Run **Mutation #5** (createProject) | **Project creation** |
| 2 | Run **Mutation #6** (createStudent) | **Student creation** |
| 3 | Run **Mutation #7** (addSkillToStudent) | **Skill assignment** |
| 4 | Run **Query #3** (students) | View all students and skills |
| 5 | Run **Query #4** (studentsBySkill: "Python") | **Skill-based matching** |
| 6 | Run **Mutation #8** (apply student 2 to p1) | **Application creation** |
| 7 | Run **Mutation #8** again (same inputs) | **Duplicate prevention** (should error) |
| 8 | Run **Mutation #9** (approve app_2_p1) | **Application approval + Role assignment** |
| 9 | Run **Query #2** (projects with teamMembers) | **Team listing** |
| 10 | Keep approving until project is full | **Member limit check** (should error) |

---

## 📊 Graph Relationship Summary

| Relationship | From | To | Properties | Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `HAS_SKILL` | Student | Skill | — | Student possesses this skill |
| `APPLIED_TO` | Student | Project | id, status, role | Pending application |
| `MEMBER_OF` | Student | Project | role | Approved team member |


