from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_graphene import GraphQLApp
from schema import schema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/graphql", GraphQLApp(schema=schema))

@app.get("/")
def read_root():
    return {"message": "GraphQL API for Project Team Formation is running. Visit /graphql for the IDE."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
