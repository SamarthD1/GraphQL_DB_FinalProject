# Project Report: Skill-Based Team Formation API

## 1. Project Overview
The **Project Team Formation API** is a specialized GraphQL service designed to help organizations or educators form optimized project teams. It matches students to projects based on their skills, manages the application/approval workflow, and enforces team size constraints.

By using a **Graph Database**, the system excels at managing complex relationships between students, their varying skill levels, and their memberships in project teams.

---

## 2. Tech Stack & Rationale

| Technology | Role | Why it was used? |
| :--- | :--- | :--- |
| **Python** | Language | High developer productivity and excellent library support for GraphQL and Neo4j. |
| **FastAPI** | Web Framework | Modern, high-performance web framework with automatic docs and seamless async support. |
| **Graphene** | GraphQL Library | A Pythonic way to define GraphQL schemas, providing a type-safe and flexible API. |
| **Neo4j Aura** | Database | A native Graph Database that simplifies "joining" data. Perfect for many-to-many relationships like Students ↔ Skills and Students ↔ Projects. |
| **Uvicorn** | ASGI Server | The standard for running FastAPI applications in production. |

---

## 3. File Structure & Responsibilities

### `main.py`
The entry point of the application. It initializes the **FastAPI** app, configures CORS (Cross-Origin Resource Sharing) for frontend compatibility, and mounts the **Graphene GraphQL** endpoint at `/graphql`.

### `schema.py`
The "brain" of the API. It contains:
- **Type Definitions**: Maps Neo4j data structures to GraphQL types (`StudentType`, `ProjectType`, etc.).
- **Queries**: Logic to fetch data (e.g., listing projects or matching students by skill).
- **Mutations**: Business logic to modify data (Applying for projects, approving members).

### `database.py`
Handles communication with the Neo4j Aura instance. It uses the official `neo4j` Python driver and includes helpers to execute Cypher queries and handle connection lifecycle.

### `seed.py`
A utility script to populate the database. It clears existing data and creates initial `Student`, `Skill`, and `Project` nodes to make the system ready for testing.

---

## 4. Ready-to-Use Test Suite (Copy-Paste)

You can run these directly in the GraphQL Playground at `http://localhost:8000/graphql`.

### A. Fetch All Projects & Existing Teams
```graphql
query GetAllProjects {
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

### B. Search Students by Skill
Find students who know "Python" with a level of at least 4.
```graphql
query SearchBySkill {
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

### C. Apply for a Project
Student 2 (Atharva) applies for Project "p1" (AI Platform) as a "developer".
```graphql
mutation StudentApply {
  applyProject(input: {
    projectId: "p1",
    studentId: "2",
    role: "developer"
  }) {
    id
  }
}
```

### D. Approve the Application
Use the `id` returned from the mutation above (usually `app_2_p1`).
```graphql
mutation ApproveStudent {
  approveApplication(applicationId: "app_2_p1") {
    success
  }
}
```

### E. Verify Team Update
Run this to see if the student is now a formal member.
```graphql
query VerifyTeam {
  projects {
    title
    teamMembers {
      student {
        name
      }
      role
    }
  }
}
```

---

## 5. Data Flow Architecture

The project follows a systematic 4-layer data flow pattern to ensure separation of concerns and data integrity:

1. **Client Request**: The user sends a GraphQL query/mutation to `http://localhost:8000/graphql`.
2. **FastAPI Middleware**: Receives the request and passes it to the Graphene handler.
3. **Graphene Resolvers**: Logic in `schema.py` validates the request, checks constraints, and constructs a Cypher query.
4. **Neo4j Driver**: `database.py` executes the Cypher query on Neo4j Aura and returns the result back up the chain.

---

## 6. How to Use the System
1. **Initialize DB**: Run `python3 seed.py`.
2. **Start Server**: Run `python3 main.py`.
3. **Open IDE**: Go to `http://localhost:8000/graphql`.
4. **Test Matching**: Run a `studentsBySkill` query.
5. **Form a Team**:
    - Use `applyProject` to submit an application.
    - Use `approveApplication` to finalize the team membership.
