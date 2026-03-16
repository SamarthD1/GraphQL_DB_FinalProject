# Skill-Based Project Team Formation API

A robust GraphQL API built with **FastAPI** and **Neo4j** to manage student skills and optimize project team formation.

## 🚀 Overview
This project solves the challenge of forming balanced project teams by matching students' skills to project requirements. It features a complete workflow from skill-based student discovery to application submission and administrative approval with team capacity enforcement.

## ✨ Key Features
- **Graph-Powered Relationships**: Uses Neo4j to manage complex connections between Students, Skills, and Projects.
- **Skill-Based Matching**: Query students based on specific skills and proficiency levels.
- **Team Management**: Complete application/approval workflow.
- **Automated Constraints**:
    - Member limit checks (prevents overfilling projects).
    - Duplicate application prevention.
    - Role-based assignments (Developer, Designer, Tester).
- **Interactive API**: Built-in GraphQL playground for testing.

## 🛠️ Tech Stack
- **Language**: Python 3.12+
- **Database**: Neo4j Aura (Graph Database)
- **API Framework**: FastAPI
- **GraphQL Library**: Graphene
- **Server**: Uvicorn

## 📋 Prerequisites
1. **Neo4j Aura Instance**: Create a free instance at [Neo4j Console](https://console.neo4j.io).
2. **Python**: Version 3.12 or higher.

## ⚙️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd GraphQL_DB_Project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory and add your Neo4j credentials:
   ```env
   NEO4J_URI=neo4j+ssc://<your-instance-id>.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=<your-password>
   NEO4J_DATABASE=neo4j
   ```
   *Note: Using `neo4j+ssc://` bypasses local SSL certificate issues common on some systems.*

## 🚀 Running the Project

1. **Seed the Database**:
   Populate the graph with initial students, skills, and projects:
   ```bash
   python3 seed.py
   ```

2. **Start the API Server**:
   ```bash
   python3 main.py
   ```

3. **Access the API**:
   Open your browser and navigate to: `http://localhost:8000/graphql`

## 🔍 Example GraphQL Usage

### Find Students with Python Skills (Level 4+)
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

### Apply for a Project
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

### List Teams & Members
```graphql
query {
  projects {
    title
    teamMembers {
      role
      student {
        name
      }
    }
  }
}
```

## 📂 Project Structure
- `main.py`: Entry point, FastAPI & GraphQL setup.
- `schema.py`: GraphQL Type definitions, Queries, and Mutations.
- `database.py`: Neo4j driver initialization and connectivity logic.
- `seed.py`: Database initialization script.
- `project_report.md`: Detailed technical architectural report.


