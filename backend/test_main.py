import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_create_and_login():
    r = client.post("/user", json={"username": "alice", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["status"] == "created"
    r2 = client.post("/user", json={"username": "alice", "password": "pw"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "logged_in"
    r3 = client.post("/user", json={"username": "alice", "password": "wrong"})
    assert r3.status_code == 401

def test_post_and_feed():
    client.post("/user", json={"username": "bob", "password": "pw"})
    r = client.post("/post", json={"user": "bob", "content": "Hello world!"})
    assert r.status_code == 200
    feed = client.get("/feed")
    assert feed.status_code == 200
    assert any(p["content"] == "Hello world!" for p in feed.json())

def test_like_and_reply():
    client.post("/user", json={"username": "carol", "password": "pw"})
    r = client.post("/post", json={"user": "carol", "content": "Test post"})
    post_id = r.json()["id"]
    like = client.post(f"/like/{post_id}")
    assert like.status_code == 200
    assert like.json()["likes"] == 1
    reply = client.post(f"/reply/{post_id}", json={"user": "carol", "content": "Reply!"})
    assert reply.status_code == 200
    assert any(r["content"] == "Reply!" for r in reply.json()["replies"])

def test_profile():
    client.post("/user", json={"username": "dave", "password": "pw"})
    client.post("/post", json={"user": "dave", "content": "Dave's post"})
    r = client.get("/profile/dave")
    assert r.status_code == 200
    assert any(p["content"] == "Dave's post" for p in r.json()["posts"])
