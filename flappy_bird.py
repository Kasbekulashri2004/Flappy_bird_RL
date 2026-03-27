import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Q-Learning Flappy Bird", page_icon="🐦", layout="wide")

st.markdown("# 🐦 Q-Learning Flappy Bird")
st.caption("Reinforcement Learning • Real-time Training")

with st.sidebar:
    st.markdown("### ⚙️ Controls")

    alpha = st.slider("Learning rate (α)", 0.01, 1.0, 0.1)
    gamma = st.slider("Discount (γ)", 0.1, 0.99, 0.9)
    epsilon = st.slider("Exploration (ε)", 0.0, 1.0, 0.1)

    st.markdown("---")

    sim_speed = st.slider("⚡ Training Speed", 1, 20, 5)

    st.markdown("---")
    st.markdown("**Controls**")
    st.markdown("• Adjust speed to train faster\n• Lower ε over time")

game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin:0;
    background:#0a0f1a;
    font-family: Arial;
}}

#wrap {{
    display:flex;
    gap:10px;
    padding:10px;
}}

canvas {{
    border-radius:10px;
    border:1px solid #1a2540;
}}

#panel {{
    width:160px;
    color:#ccc;
    font-size:12px;
}}

.card {{
    background:#0d1525;
    border:1px solid #1a2540;
    border-radius:8px;
    padding:8px;
    margin-bottom:8px;
    text-align:center;
}}

.val {{
    font-size:20px;
    color:#f9c74f;
}}

button {{
    width:100%;
    padding:6px;
    background:#111;
    border:1px solid #333;
    color:#ccc;
    cursor:pointer;
}}

button:hover {{
    border-color:#f9c74f;
    color:#f9c74f;
}}
</style>
</head>

<body>
<div id="wrap">
    <canvas id="game" width="400" height="500"></canvas>

    <div id="panel">
        <div class="card">
            Score
            <div class="val" id="score">0</div>
        </div>

        <div class="card">
            Episodes
            <div class="val" id="episodes">0</div>
        </div>

        <div class="card">
            Alive
            <div class="val" id="status">RUN</div>
        </div>

        <button onclick="togglePause()">Pause / Resume</button>
    </div>
</div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W=400, H=500;

let bird = {{y:250, vy:0}};
let pipe = {{x:400, gapY:200}};
let score = 0;
let episodes = 0;

let paused = false;

// Q-table
let Q = {{}};

const alpha = {alpha};
const gamma = {gamma};
const epsilon = {epsilon};
const SPEED = {sim_speed};

function getState() {{
    let dy = Math.floor((bird.y - pipe.gapY)/20);
    let dx = Math.floor((pipe.x - 80)/20);
    let vy = Math.floor(bird.vy/2);
    return `${{dy}}_${{dx}}_${{vy}}`;
}}

function chooseAction(s) {{
    if (Math.random()<epsilon || !(s in Q)) {{
        return Math.random()<0.5 ? 0 : 1;
    }}
    return Q[s][0] > Q[s][1] ? 0 : 1;
}}

function updateQ(s,a,r,s2) {{
    if (!(s in Q)) Q[s]=[0,0];
    if (!(s2 in Q)) Q[s2]=[0,0];

    Q[s][a] += alpha*(r + gamma*Math.max(...Q[s2]) - Q[s][a]);
}}

function reset() {{
    bird.y=250;
    bird.vy=0;
    pipe.x=400;
    pipe.gapY=150+Math.random()*200;
    score=0;
    episodes++;
}}

function step() {{
    let s = getState();
    let a = chooseAction(s);

    if (a===1) bird.vy=-7;

    bird.vy+=0.5;
    bird.y+=bird.vy;

    pipe.x-=2;

    if (pipe.x<-50) {{
        pipe.x=400;
        pipe.gapY=150+Math.random()*200;
        score++;
    }}

    let reward = 0.1;

    if (bird.y<0 || bird.y>H ||
        (pipe.x<100 && pipe.x>50 &&
        (bird.y<pipe.gapY || bird.y>pipe.gapY+120))) {{

        reward = -10;
        updateQ(s,a,reward,getState());
        reset();
        return;
    }}

    updateQ(s,a,reward,getState());
}}

function draw() {{
    ctx.fillStyle="#0a0f1a";
    ctx.fillRect(0,0,W,H);

    // bird
    ctx.beginPath();
    ctx.arc(80,bird.y,10,0,Math.PI*2);
    ctx.fillStyle="#f9c74f";
    ctx.fill();

    // pipes
    ctx.fillStyle="#2ecc71";
    ctx.fillRect(pipe.x,0,50,pipe.gapY);
    ctx.fillRect(pipe.x,pipe.gapY+120,50,H);

    ctx.fillStyle="#fff";
    ctx.fillText("Score: "+score,10,20);

    document.getElementById("score").innerText = score;
    document.getElementById("episodes").innerText = episodes;
}}

function togglePause() {{
    paused = !paused;
    document.getElementById("status").innerText = paused ? "PAUSE" : "RUN";
}}

function loop() {{
    if (!paused) {{
        for (let i=0;i<SPEED;i++) step();
    }}
    draw();
    requestAnimationFrame(loop);
}}

loop();
</script>
</body>
</html>
"""

components.html(game_html, height=520)
