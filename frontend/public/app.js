
let currentUser = null;
let currentPassword = null;
let posts = [];
const API = "/api";

document.getElementById('profile-form').onsubmit = async function(e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  if (!username || !password) return;
  try {
    const res = await fetch(`${API}/user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || 'Login failed');
      return;
    }
    const data = await res.json();
    currentUser = username;
    currentPassword = password;
    document.getElementById('profile-info').innerHTML = `<b>Logged in as:</b> ${username}`;
    loadFeed();
  } catch (err) {
    alert('Network error');
  }
};

document.getElementById('post-form').onsubmit = async function(e) {
  e.preventDefault();
  if (!currentUser) {
    alert('Login first!');
    return;
  }
  const content = document.getElementById('post-content').value.trim();
  if (!content) return;
  if (content.length > 280) {
    alert('Post too long!');
    return;
  }
  try {
    const res = await fetch(`${API}/post`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: currentUser, content })
    });
    if (!res.ok) {
      alert('Post failed');
      return;
    }
    await loadFeed();
    document.getElementById('post-content').value = '';
  } catch (err) {
    alert('Network error');
  }
};

async function loadFeed() {
  try {
    const res = await fetch(`${API}/feed`);
    posts = await res.json();
    renderPosts();
  } catch (err) {
    posts = [];
    renderPosts();
  }
}

function renderPosts() {
  const postsDiv = document.getElementById('posts');
  postsDiv.innerHTML = '';
  posts.forEach(post => {
    const postDiv = document.createElement('div');
    postDiv.className = 'post';
    postDiv.innerHTML = `
      <b>${post.user}</b> <span style="float:right;">${post.timestamp ? new Date(post.timestamp).toLocaleString() : ''}</span><br>
      ${post.content}<br>
      <span class="like-btn" onclick="likePost(${post.id})">&#x1F44D; ${post.likes}</span>
      <span style="margin-left:1em;cursor:pointer;color:#007bff;" onclick="showReplyForm(${post.id})">Reply</span>
      <span style="margin-left:1em;cursor:pointer;color:#007bff;" onclick="viewUserProfile('${post.user}')">View Profile</span>
      <div id="replies-${post.id}"></div>
      <div id="reply-form-${post.id}"></div>
    `;
    postsDiv.appendChild(postDiv);
    renderReplies(post);
  });
}

window.likePost = async function(id) {
  try {
    const res = await fetch(`${API}/like/${id}`, { method: 'POST' });
    if (!res.ok) {
      alert('Like failed');
      return;
    }
    await loadFeed();
  } catch (err) {
    alert('Network error');
  }
};

window.showReplyForm = function(id) {
  if (!currentUser) {
    alert('Login first!');
    return;
  }
  const replyFormDiv = document.getElementById(`reply-form-${id}`);
  replyFormDiv.innerHTML = `
    <form onsubmit="replyToPost(event, ${id})">
      <input type="text" id="reply-content-${id}" maxlength="280" placeholder="Reply... (max 280 chars)" required />
      <button class="btn" type="submit">Reply</button>
    </form>
  `;
};

window.replyToPost = async function(e, id) {
  e.preventDefault();
  const content = document.getElementById(`reply-content-${id}`).value.trim();
  if (!content) return;
  if (content.length > 280) {
    alert('Reply too long!');
    return;
  }
  try {
    const res = await fetch(`${API}/reply/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: currentUser, content })
    });
    if (!res.ok) {
      alert('Reply failed');
      return;
    }
    await loadFeed();
  } catch (err) {
    alert('Network error');
  }
};

function renderReplies(post) {
  const repliesDiv = document.getElementById(`replies-${post.id}`);
  repliesDiv.innerHTML = '';
  (post.replies || []).forEach(reply => {
    const replyDiv = document.createElement('div');
    replyDiv.className = 'reply';
    replyDiv.innerHTML = `<b>${reply.user}:</b> ${reply.content}`;
    repliesDiv.appendChild(replyDiv);
  });
}

window.viewUserProfile = async function(username) {
  try {
    const res = await fetch(`${API}/profile/${username}`);
    if (!res.ok) {
      alert('Profile not found');
      return;
    }
    const data = await res.json();
    let html = `<h2>Profile: ${username}</h2>`;
    html += `<div><b>Posts:</b></div>`;
    (data.posts || []).forEach(post => {
      html += `<div class="post">${post.content}<br><span style="font-size:smaller;">${post.timestamp ? new Date(post.timestamp).toLocaleString() : ''}</span></div>`;
    });
    document.getElementById('user-profile-view').innerHTML = html;
  } catch (err) {
    document.getElementById('user-profile-view').innerHTML = '<p>Network error</p>';
  }
};

loadFeed();
