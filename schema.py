import graphene
from database import get_db

class SkillType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    level = graphene.Int()

class StudentType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    skills = graphene.List(SkillType)

    def resolve_skills(self, info):
        db = get_db()
        query = """
        MATCH (s:Student {id: $id})-[:HAS_SKILL]->(sk:Skill)
        RETURN sk.id as id, sk.name as name, sk.level as level
        """
        return db.execute_query(query, {"id": self.id})

class TeamMemberType(graphene.ObjectType):
    student_id = graphene.ID()
    role = graphene.String()
    student = graphene.Field(StudentType)

    def resolve_student(self, info):
        db = get_db()
        query = "MATCH (s:Student {id: $id}) RETURN s"
        result = db.execute_query(query, {"id": self.student_id})
        if result:
            s = result[0]['s']
            return StudentType(id=s['id'], name=s['name'], email=s['email'])
        return None

class ProjectType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    max_members = graphene.Int()
    teamMembers = graphene.List(TeamMemberType)

    def resolve_teamMembers(self, info):
        db = get_db()
        query = """
        MATCH (s:Student)-[r:MEMBER_OF]->(p:Project {id: $id})
        RETURN s.id as student_id, r.role as role
        """
        results = db.execute_query(query, {"id": self.id})
        return [TeamMemberType(student_id=res['student_id'], role=res['role']) for res in results]

class ApplicationType(graphene.ObjectType):
    id = graphene.ID()
    projectId = graphene.ID()
    studentId = graphene.ID()
    status = graphene.String()

class Query(graphene.ObjectType):
    projects = graphene.List(ProjectType)
    students = graphene.List(StudentType)
    studentsBySkill = graphene.List(StudentType, skill_name=graphene.String(required=True), min_level=graphene.Int())

    def resolve_projects(self, info):
        db = get_db()
        query = "MATCH (p:Project) RETURN p"
        results = db.execute_query(query)
        return [ProjectType(**res['p']) for res in results]

    def resolve_students(self, info):
        db = get_db()
        query = "MATCH (s:Student) RETURN s"
        results = db.execute_query(query)
        return [StudentType(**res['s']) for res in results]

    def resolve_studentsBySkill(self, info, skill_name, min_level=1):
        db = get_db()
        query = """
        MATCH (s:Student)-[:HAS_SKILL]->(sk:Skill)
        WHERE sk.name =~ $skill_name AND sk.level >= $min_level
        RETURN s
        """
        results = db.execute_query(query, {"skill_name": f"(?i){skill_name}", "min_level": min_level})
        return [StudentType(**res['s']) for res in results]

class CreateProjectInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    description = graphene.String(required=True)
    maxMembers = graphene.Int(required=True)

class CreateProject(graphene.Mutation):
    class Arguments:
        input = CreateProjectInput(required=True)

    project = graphene.Field(ProjectType)

    def mutate(self, info, input):
        db = get_db()
        # Check if project already exists
        check = db.execute_query("MATCH (p:Project {id: $id}) RETURN p", {"id": input['id']})
        if check:
            raise Exception("Project with this ID already exists")

        query = """
        CREATE (p:Project {id: $id, title: $title, description: $description, max_members: $maxMembers})
        RETURN p
        """
        result = db.execute_query(query, input)
        return CreateProject(project=ProjectType(**result[0]['p']))

class CreateStudentInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    email = graphene.String(required=True)

class CreateStudent(graphene.Mutation):
    class Arguments:
        input = CreateStudentInput(required=True)

    student = graphene.Field(StudentType)

    def mutate(self, info, input):
        db = get_db()
        # Check if student already exists
        check = db.execute_query("MATCH (s:Student {id: $id}) RETURN s", {"id": input['id']})
        if check:
            raise Exception("Student with this ID already exists")

        query = """
        CREATE (s:Student {id: $id, name: $name, email: $email})
        RETURN s
        """
        result = db.execute_query(query, input)
        return CreateStudent(student=StudentType(**result[0]['s']))

class AddSkillToStudentInput(graphene.InputObjectType):
    studentId = graphene.ID(required=True)
    skillName = graphene.String(required=True)
    level = graphene.Int(required=True)

class AddSkillToStudent(graphene.Mutation):
    class Arguments:
        input = AddSkillToStudentInput(required=True)

    success = graphene.Boolean()

    def mutate(self, info, input):
        db = get_db()
        # Check student exists
        check = db.execute_query("MATCH (s:Student {id: $studentId}) RETURN s", {"studentId": input['studentId']})
        if not check:
            raise Exception("Student not found")

        # Create or find the skill and link it
        query = """
        MATCH (s:Student {id: $studentId})
        MERGE (sk:Skill {name: $skillName})
        ON CREATE SET sk.id = $skillId, sk.level = $level
        MERGE (s)-[:HAS_SKILL]->(sk)
        RETURN true as success
        """
        skill_id = f"s_{input['skillName'].lower()}"
        db.execute_query(query, {**input, "skillId": skill_id})
        return AddSkillToStudent(success=True)

class ApplyProjectInput(graphene.InputObjectType):
    projectId = graphene.ID(required=True)
    studentId = graphene.ID(required=True)
    role = graphene.String(required=True)

class ApplyProject(graphene.Mutation):
    class Arguments:
        input = ApplyProjectInput(required=True)

    id = graphene.ID()

    def mutate(self, info, input):
        db = get_db()
        # 1. Duplicate prevention
        check_query = """
        MATCH (s:Student {id: $studentId})-[r:APPLIED_TO|MEMBER_OF]->(p:Project {id: $projectId})
        RETURN count(r) as count
        """
        count = db.execute_query(check_query, input)[0]['count']
        if count > 0:
            raise Exception("Already applied or already a member")

        # 2. Member limit check (though this is application, limit check might be on approval)
        # But let's check if project exists
        proj_query = "MATCH (p:Project {id: $projectId}) RETURN p.max_members as max_members"
        proj_res = db.execute_query(proj_query, {"projectId": input['projectId']})
        if not proj_res:
            raise Exception("Project not found")
        
        # 3. Create Application
        app_id = f"app_{input['studentId']}_{input['projectId']}"
        create_query = """
        MATCH (s:Student {id: $studentId}), (p:Project {id: $projectId})
        CREATE (s)-[r:APPLIED_TO {id: $id, status: 'pending', role: $role}]->(p)
        RETURN r.id as id
        """
        params = {**input, "id": app_id}
        result = db.execute_query(create_query, params)
        return ApplyProject(id=result[0]['id'])

class ApproveApplication(graphene.Mutation):
    class Arguments:
        applicationId = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, applicationId):
        db = get_db()
        
        # Get application details
        app_query = """
        MATCH (s:Student)-[r:APPLIED_TO {id: $id}]->(p:Project)
        RETURN s.id as studentId, p.id as projectId, r.role as role, p.max_members as max_members
        """
        app_res = db.execute_query(app_query, {"id": applicationId})
        if not app_res:
            raise Exception("Application not found")
        
        app = app_res[0]
        
        # Member limit check
        member_count_query = "MATCH (:Student)-[:MEMBER_OF]->(p:Project {id: $projectId}) RETURN count(*) as count"
        current_members = db.execute_query(member_count_query, {"projectId": app['projectId']})[0]['count']
        
        if current_members >= app['max_members']:
            raise Exception("Project is full")
        
        # Approve: Remove APPLIED_TO, Create MEMBER_OF
        approve_query = """
        MATCH (s:Student {id: $studentId})-[r:APPLIED_TO {id: $id}]->(p:Project {id: $projectId})
        DELETE r
        CREATE (s)-[:MEMBER_OF {role: $role}]->(p)
        RETURN true as success
        """
        db.execute_query(approve_query, {
            "studentId": app['studentId'],
            "projectId": app['projectId'],
            "role": app['role'],
            "id": applicationId
        })
        
        return ApproveApplication(success=True)

class Mutation(graphene.ObjectType):
    createProject = CreateProject.Field()
    createStudent = CreateStudent.Field()
    addSkillToStudent = AddSkillToStudent.Field()
    applyProject = ApplyProject.Field()
    approveApplication = ApproveApplication.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
