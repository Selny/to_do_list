from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import connection_string
from models import Base, Task,User
from fastapi.middleware.cors import CORSMiddleware
import re
from hashlib import sha256
from auth import AuthHandler

username = connection_string['username']
password = connection_string['password']
host = connection_string['host']
db_name = connection_string['db_name']

engine = create_engine(f'mysql+mysqldb://{username}:{password}@{host}/{db_name}')
Session = sessionmaker(bind=engine)

def recreate_database():
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

recreate_database()

app = FastAPI()

auth_handler = AuthHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/')
async def sign_up(username:str,password:str,repeatpassword:str):
    s=Session()
    user=s.query(User).get(username)
    if s.query(User).filter(User.username==username).first() is not None :
        return 'Username already exists'
    if password != repeatpassword:
        return 'Password'
    if re.search('^(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[]:;<>,.?/~_+-=|\]).{8,32}$', password) is False:
        return'Password is not valid'
    user=User(
        username=username,
        password=auth_handler.get_password_hash(password)
    )
    s.add(user)
    s.commit()
    s.close()
    return 'user created'

@app.get('/')
async def login(username:str,password:str):
    s = Session()
    user = s.query(User).filter(User.username == username).first()
    if user.username == username and auth_handler.verify_password(password, user.password):
        token = auth_handler.encode_token(user.id)
        return token
    return 'Username or password is wrong'

@app.get('/tasks')
def show_tasks(id = Depends(auth_handler.auth_wrapper)):
    s = Session()

    tasks = s.query(Task).filter(Task.user_id==id).all()
    s.close
    return tasks

@app.post('/tasks')
async def add_task(title: str, rank: int, id = Depends(auth_handler.auth_wrapper)):

    s = Session()

    task = Task(
        title = title,
        rank = rank,
        user_id = id
    )

    s.add(task)
    s.commit()
    s.close()

@app.put('/tasks/{task_id}')
async def update_task(task_id: int, title: str | None = None, rank: int | None = None, id = Depends(auth_handler.auth_wrapper)):

    s = Session()

    task = s.query(Task).filter(Task.user_id==id, Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code = 404, detail = 'Id does not exist')
    
    if title:
        task.title = title
    if rank:
        task.rank = rank
    
    s.commit()
    s.close()

@app.delete('/tasks/{task_id}')
async def delete_task(task_id: int, id = Depends(auth_handler.auth_wrapper)):

    s = Session()

    task = s.query(Task).filter(Task.user_id==id, Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code = 404, detail = 'Id does not exist')
    
    s.delete(task)
    s.commit()
    s.close()

@app.put('/tasks/check/{task_id}')
async def check_task(id: int):
    if s.query(Task).filter(Task.id!=id).first():
        raise HTTPException(status_code = 404, detail = 'Id does not exist')
    s = Session()
    task = s.query(Task).filter(Task.user_id==id, Task.id == task_id).first()
    task.done = not task.done
    s.commit()
    s.close()

@app.get('/tasks_done')
async def show_completed_tasks(id = Depends(auth_handler.auth_wrapper)):
    s = Session()
    task = s.query(Task).filter(Task.user_id==id, Task.done == True).all()
    s.close()
    return task

@app.get('/sort_tasks')
async def sort_task(id = Depends(auth_handler.auth_wrapper)):
    s = Session()
    task = s.query(Task).filter(Task.user_id==id).order_by(Task.rank).all()
    s.close()
    return task
