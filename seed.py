from database import get_db

def seed():
    db = get_db()
    
    # Clear database
    print("Clearing database...")
    db.execute_query("MATCH (n) DETACH DELETE n")
    
    # Create Constraints
    print("Creating constraints...")
    try:
        db.execute_query("CREATE CONSTRAINT student_id FOR (s:Student) REQUIRE s.id IS UNIQUE")
        db.execute_query("CREATE CONSTRAINT project_id FOR (p:Project) REQUIRE p.id IS UNIQUE")
        db.execute_query("CREATE CONSTRAINT skill_id FOR (sk:Skill) REQUIRE sk.id IS UNIQUE")
    except Exception as e:
        print(f"Constraints might already exist: {e}")

    # Create Students
    print("Seeding students...")
    students = [
        {"id": "1", "name": "Ritesh", "email": "ritesh@gmail.com"},
        {"id": "2", "name": "Atharva", "email": "atharva@gmail.com"},
        {"id": "3", "name": "Rizwan", "email": "rizwan@gmail.com"},
        {"id": "4", "name": "Sarthak", "email": "sarthak@gmail.com"},
    ]
    for s in students:
        db.execute_query("CREATE (:Student {id: $id, name: $name, email: $email})", s)

    # Create Skills
    print("Seeding skills...")
    skills = [
        {"id": "s1", "name": "Python", "level": 5},
        {"id": "s2", "name": "React", "level": 4},
        {"id": "s3", "name": "Design", "level": 3},
        {"id": "s4", "name": "Testing", "level": 4},
    ]
    for sk in skills:
        db.execute_query("CREATE (:Skill {id: $id, name: $name, level: $level})", sk)

    # Assign Skills
    print("Assigning skills...")
    db.execute_query("MATCH (s:Student {id: '1'}), (sk:Skill {id: 's1'}) CREATE (s)-[:HAS_SKILL]->(sk)")
    db.execute_query("MATCH (s:Student {id: '1'}), (sk:Skill {id: 's2'}) CREATE (s)-[:HAS_SKILL]->(sk)")
    db.execute_query("MATCH (s:Student {id: '2'}), (sk:Skill {id: 's3'}) CREATE (s)-[:HAS_SKILL]->(sk)")
    db.execute_query("MATCH (s:Student {id: '3'}), (sk:Skill {id: 's1'}) CREATE (s)-[:HAS_SKILL]->(sk)")
    db.execute_query("MATCH (s:Student {id: '4'}), (sk:Skill {id: 's4'}) CREATE (s)-[:HAS_SKILL]->(sk)")

    # Create Projects
    print("Seeding projects...")
    projects = [
        {"id": "p1", "title": "AI Platform", "description": "Building an AI platform", "max_members": 2},
        {"id": "p2", "title": "Web App", "description": "Developing a web application", "max_members": 3},
    ]
    for p in projects:
        db.execute_query("CREATE (:Project {id: $id, title: $title, description: $description, max_members: $max_members})", p)

    print("Seed complete.")

if __name__ == "__main__":
    seed()
