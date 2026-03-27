import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Q-Learning Flappy Bird", page_icon="🐦", layout="wide")

st.title("🐦 Flappy Bird — Q Learning")

with st.sidebar:
    st.header("⚙️ Settings")
    alpha = st.slider("Learning rate (α)", 0.01, 1.0, 0.1)
    gamma = st.slider("Discount (γ)", 0.1, 0.99, 0.9)
    epsilon = st.slider("Exploration (ε)", 0.0, 1.0, 0.1)

game_html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;background:#0a0f1a;">
<canvas id="game" width="400" height="500"></canvas>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = 400, H = 500;
let bird = {{y:250, vy:0}};
let pipe = {{x:400, gapY:200}};
let score = 0;

// Q-table
let Q = {{}};

// parameters
const alpha = {alpha};
const gamma = {gamma};
const epsilon = {epsilon};

function getState() {{
    let dy = Math.floor((bird.y - pipe.gapY)/20);
    let dx = Math.floor((pipe.x - 80)/20);
    let vy = Math.floor(bird.vy/2);
    return `${{dy}}_${{dx}}_${{vy}}`;
}}

function chooseAction(state) {{
    if (Math.random() < epsilon || !(state in Q)) {{
        return Math.random() < 0.5 ? 0 : 1; // 0=do nothing, 1=jump
    }}
    return Q[state][0] > Q[state][1] ? 0 : 1;
}}

function updateQ(s, a, r, s2) {{
    if (!(s in Q)) Q[s] = [0,0];
    if (!(s2 in Q)) Q[s2] = [0,0];

    Q[s][a] += alpha * (r + gamma * Math.max(...Q[s2]) - Q[s][a]);
}}

function reset() {{
    bird.y = 250;
    bird.vy = 0;
    pipe.x = 400;
    pipe.gapY = 150 + Math.random()*200;
    score = 0;
}}

function step() {{
    let state = getState();
    let action = chooseAction(state);

    if (action === 1) bird.vy = -7;

    bird.vy += 0.5;
    bird.y += bird.vy;

    pipe.x -= 2;

    if (pipe.x < -50) {{
        pipe.x = 400;
        pipe.gapY = 150 + Math.random()*200;
        score++;
    }}

    let reward = 0.1;

    // collision
    if (bird.y < 0 || bird.y > H ||
        (pipe.x < 100 && pipe.x > 50 &&
        (bird.y < pipe.gapY || bird.y > pipe.gapY+120))) {{
        reward = -10;
        reset();
    }}

    let newState = getState();
    updateQ(state, action, reward, newState);
}}

function draw() {{
    ctx.fillStyle="#0a0f1a";
    ctx.fillRect(0,0,W,H);

    // bird
    ctx.beginPath();
    ctx.arc(80, bird.y, 10, 0, Math.PI*2);
    ctx.fillStyle="#f9c74f";
    ctx.fill();

    // pipe
    ctx.fillStyle="#2ecc71";
    ctx.fillRect(pipe.x, 0, 50, pipe.gapY);
    ctx.fillRect(pipe.x, pipe.gapY+120, 50, H);

    ctx.fillStyle="white";
    ctx.fillText("Score: " + score, 10, 20);
}}

function loop() {{
    step();
    draw();
    requestAnimationFrame(loop);
}}

loop();
</script>
</body>
</html>
"""

components.html(game_html, height=520)
