from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./microblog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    posts = relationship("PostDB", back_populates="user")

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    likes = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="posts")
    replies = relationship("ReplyDB", back_populates="post")

class ReplyDB(Base):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user = Column(String)
    content = Column(Text)
    post = relationship("PostDB", back_populates="replies")

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    username: str
    password: str

class Post(BaseModel):
    id: Optional[int] = None
    user: str
    content: str
    likes: int = 0
    replies: List[dict] = []
    timestamp: Optional[str] = None

class Reply(BaseModel):
    user: str
    content: str

@app.post("/user")
def create_or_login_user(user: User):
    db = SessionLocal()
    db_user = db.query(UserDB).filter_by(username=user.username).first()
    if db_user:
        if db_user.password != user.password:
            db.close()
            raise HTTPException(status_code=401, detail="Incorrect password")
        db.close()
        return {"username": db_user.username, "status": "logged_in"}
    else:
        db_user = UserDB(username=user.username, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return {"username": db_user.username, "status": "created"}

@app.post("/post")
def create_post(post: Post):
    db = SessionLocal()
    db_user = db.query(UserDB).filter_by(username=post.user).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db_post = PostDB(user_id=db_user.id, content=post.content, likes=post.likes)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    result = Post(
        id=db_post.id,
        user=db_user.username,
        content=db_post.content,
        likes=db_post.likes,
        replies=[],
        timestamp=db_post.timestamp.isoformat()
    )
    db.close()
    return result

@app.get("/feed")
def get_feed():
    db = SessionLocal()
    db_posts = db.query(PostDB).order_by(PostDB.timestamp.desc()).all()
    result = []
    for p in db_posts:
        replies = [Reply(user=r.user, content=r.content).dict() for r in p.replies]
        result.append(Post(
            id=p.id,
            user=p.user.username,
            content=p.content,
            likes=p.likes,
            replies=replies,
            timestamp=p.timestamp.isoformat()
        ).dict())
    db.close()
    return result

@app.post("/like/{post_id}")
def like_post(post_id: int):
    db = SessionLocal()
    db_post = db.query(PostDB).filter_by(id=post_id).first()
    if not db_post:
        db.close()
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.likes += 1
    db.commit()
    db.refresh(db_post)
    result = Post(
        id=db_post.id,
        user=db_post.user.username,
        content=db_post.content,
        likes=db_post.likes,
        replies=[Reply(user=r.user, content=r.content).dict() for r in db_post.replies],
        timestamp=db_post.timestamp.isoformat()
    )
    db.close()
    return result

@app.post("/reply/{post_id}")
def reply_post(post_id: int, reply: Reply):
    db = SessionLocal()
    db_post = db.query(PostDB).filter_by(id=post_id).first()
    if not db_post:
        db.close()
        raise HTTPException(status_code=404, detail="Post not found")
    db_reply = ReplyDB(post_id=post_id, user=reply.user, content=reply.content)
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    replies = [Reply(user=r.user, content=r.content).dict() for r in db_post.replies]
    result = Post(
        id=db_post.id,
        user=db_post.user.username,
        content=db_post.content,
        likes=db_post.likes,
        replies=replies,
        timestamp=db_post.timestamp.isoformat()
    )
    db.close()
    return result

@app.get("/profile/{username}")
def get_user_profile(username: str):
    db = SessionLocal()
    db_user = db.query(UserDB).filter_by(username=username).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    user_posts = db.query(PostDB).filter_by(user_id=db_user.id).order_by(PostDB.timestamp.desc()).all()
    posts_list = []
    for p in user_posts:
        replies = [Reply(user=r.user, content=r.content).dict() for r in p.replies]
        posts_list.append(Post(
            id=p.id,
            user=db_user.username,
            content=p.content,
            likes=p.likes,
            replies=replies,
            timestamp=p.timestamp.isoformat()
        ).dict())
    db.close()
    return {"username": username, "posts": posts_list}
