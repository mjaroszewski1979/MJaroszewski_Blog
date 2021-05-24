from fastapi import FastAPI, Depends, status, Response, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from typing import List
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db
import models
import schemas
import security




app = FastAPI()

models.Base.metadata.create_all(engine)

@app.get('/',response_class=HTMLResponse, tags=['index'])
def index():
    return """
    <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-+0n0xVW2eSR5OomGNYDnhzAbDsOXxcvSN1TPprVMTNDbiYZCxYbOOl7+AMvyTG2x" crossorigin="anonymous">

            <title>MJaroszewski Blog</title>
        </head>
        <body>
        <div class="text-center">
  <img src="https://source.unsplash.com/random/2000x1000" class="img-fluid" style="height:100vh;">
</div>
        <div style="width: 80vw" class="position-absolute top-0 start-50 translate-middle-x"> 
                    <div class="container mt-4">
                <nav class="navbar navbar-light" style="background-color: #e3f2fd;">
                    <div style="text-align:center;" class="container-fluid ps-5">
                        <h3>MJaroszewski Blog</h3>
                    </div>
                </nav>
            </div>
            <div class="container">
            <div class="row">
            <div class="col"></div>
            <div class="col-md-auto">
                <div class="card text-center mt-5">
                <div class="card-header">
                </div>
                <div class="card-body">
                    <h5 class="card-title">This is a blog application created with FastAPI.</h5>
                    <p class="card-text">The main features includes: creating, updating, deleting and displaying posts, 
                    registering and authenticating users. Posts section is protected with OAuth2 and JWT "password flow", 
                    which involves generating security tokens called bearer tokens. To gain access to secured resources 
                    client/user must send a username(email address) and password fields as form data. Please click the 
                    button below to view automatic interactive documentation.</p>
                    <a href="/docs" class="btn btn-primary">Click here</a>
                </div>
                <div class="card-footer text-muted">
                </div>
                </div>
            </div>
            <div class="col"></div>
            </div>
            </div>
        </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-gtEjrD/SeCtmISkJkNUaaKMoLD0//ElJ19smozuHV6z3Iehds+3Ulb9Bn9Plx0x4" crossorigin="anonymous"></script>
        </body>
        </html>
    """



@app.post('/post', status_code=status.HTTP_201_CREATED, tags=['posts'])
def create(request: schemas.Post, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    new_post = models.Post(title=request.title, body=request.body, user_id=request.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.delete('/post{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['posts'])
def delete(id, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()


@app.put('/post{id}', status_code=status.HTTP_202_ACCEPTED, tags=['posts'])
def update(id, request: schemas.Post, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} does not exist")
    post.update({"title" : request.title, "body" : request.body})
    db.commit()
    return 'Post updated'


@app.get('/post', response_model=List[schemas.ShowPost], tags=['posts'])
def all_posts(db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    posts = db.query(models.Post).all()
    return posts

@app.get('/post/{id}', status_code=200, response_model=schemas.ShowPost, tags=['posts'])
def post_by_id(id, response: Response, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with the id {id} does not exist")
    return post

@app.post('/user', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowUser, tags=['users'])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    new_user = models.User(name=request.name, email=request.email, password=security.Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}', response_model=schemas.ShowUser, tags=['users'])
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"User with the id {id} does not exist")
    return user

@app.post('/login', tags=['authentication'])
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid Credentials")
    if not security.Hash.verify(user.password, request.password):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid Password")
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}







