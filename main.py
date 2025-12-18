from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, get_db
from sqlalchemy import Column, Integer, String, Boolean

# Database Table
class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas for Validation
class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    title: str
    is_active: bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local dev, this is easiest
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. GET ALL
@app.get("/api/v1/todo")
def get_all(db: Session = Depends(get_db)):
    return db.query(TodoItem).all()

# 2. POST CREATE
@app.post("/api/v1/todo")
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    new_item = TodoItem(title=todo.title)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# 3. GET SINGLE
@app.get("/api/v1/todo/{todo_id}")
def get_one(todo_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item: raise HTTPException(404, "Not found")
    return item

# 4. PUT UPDATE (Full edit)
@app.put("/api/v1/todo/{todo_id}")
def update_full(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item: raise HTTPException(404, "Not found")
    item.title = data.title
    item.is_active = data.is_active
    db.commit()
    return item

# 5. PATCH TOGGLE (Status flip)
@app.patch("/api/v1/todo/{todo_id}")
def toggle_status(todo_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item: raise HTTPException(404, "Not found")
    item.is_active = not item.is_active
    db.commit()
    return item

# 6. DELETE
@app.delete("/api/v1/todo/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item: raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
    return {"status": "success"}