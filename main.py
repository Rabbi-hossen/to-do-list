#!/usr/bin/env python3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import uvicorn

#databse setup
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoItem(Base):   
    __tablename__ = "todo"
    id = Column(Integer, primary_key = True, index= True)
    title = Column (String, nullable=False)
    is_active= Column (Boolean, default=True)
 
#create table if they don't exist
Base.metadata.create_all(bind=engine)

#dependency to get db session
def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()

#pydantic schemas
class Todocreate(BaseModel):
    title:str

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class TodoOut(BaseModel):
    id:int
    title: str
    is_active: bool

    class config: 
        orm_mode = True

#fastapi app
app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins= ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/todo", response_model=List[TodoOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(TodoItem).all()

@app.post("/api/v1/todo", response_model= TodoOut, status_code=201)
def create_todo(todo: Todocreate, db: Session = Depends(get_db)):
    new_item = TodoItem(title=todo.title)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/api/v1/todo/{item_id}", response_model=TodoOut)
def get_one(todo_id: int, db: Session = Depends(get_db)):
    item= db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/v1/todo/{item_id}", response_model=TodoOut)
def update_todo(item_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    item= db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code= 404, details= "Items not found")
    if todo.title is not None:
        item.title = todo.title
    if todo.is_active is not None:
        item.is_active = todo.is_active
    db.commit()
    db.refresh(item)
    return item

@app.patch("/api/v1/todo/{item_id}", response_model=TodoOut)
def toggle_status(item_id: int, db: Session = Depends(get_db)):
    item= db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, details="Item not found")
    item.is_active = not item.is_active
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/v1/todo/{item_id}")
def delete_todo(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code = 404, details= "Item not found")
    db.delete(item)
    db.commit()
    return { "status": "sucess"}

if __name__ == "__main__":
#run with python  
    uvicorn.run("main:app",host="127.0.0.1", port=8000, reload=True)

    
