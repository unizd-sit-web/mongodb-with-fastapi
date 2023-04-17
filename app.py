import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List
import motor.motor_asyncio
import uuid

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
    app.db = app.mongodb_client.tododb
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

class TodoModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    title: str
    description: str

class UpdateTodoModel(BaseModel):
    title: Optional[str]
    description: Optional[str]

@app.post("/", response_description="Create a todo item", response_model=TodoModel)
async def create_todo(todo: TodoModel = Body(...)):
    todo = jsonable_encoder(todo)
    new_todo = await app.db["todos"].insert_one(todo)
    created_todo = await app.db["todos"].find_one({"_id": new_todo.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_todo)

@app.get("/", response_description="List all todos", response_model=List[TodoModel])
async def list_todos():
    todos = await app.db["todos"].find().to_list(1000)
    return todos


@app.get("/{id}", response_description="Get a todo", response_model=TodoModel)
async def get_todo(id: str):
    if (todo := await app.db["todos"].find_one({"_id": id})) is not None:
        return todo

    raise HTTPException(status_code=404, detail=f"Todo {id} not found")


@app.put("/{id}", response_description="Update a todo", response_model=TodoModel)
async def update_todo(id: str, todo: UpdateTodoModel = Body(...)):
    todo = {k: v for k, v in todo.dict().items() if v is not None}

    if len(todo) >= 1:
        update_result = await app.db["todos"].update_one({"_id": id}, {"$set": todo})

        if update_result.modified_count == 1:
            if (updated_todo := await app.db["todos"].find_one({"_id": id})) is not None:
                return updated_todo

    if (existing_todo := await app.db["todos"].find_one({"_id": id})) is not None:
        return existing_todo

    raise HTTPException(status_code=404, detail=f"Todo {id} not found")


@app.delete("/{id}", response_description="Delete a todo")
async def delete_todo(id: str):
    delete_result = await app.db["todos"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Todo {id} not found")
