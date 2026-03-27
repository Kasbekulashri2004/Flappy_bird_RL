import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="RL Flappy Bird - Q Learning",
    page_icon="🐦",
    layout="wide",
)

st.title("🐦 RL Flappy Bird with Q-Learning (Live Training)")

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    training_speed = st.slider("Training speed (steps per frame)", 1, 50, 10)
    paused = st.checkbox("Pause training", False)
    st.markdown("---")
    st.markdown("Q-learning parameters are fixed in JS for simplicity.")

# HTML + JS for game + training + UI
game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; background:#0a0f1a; color:#f9c74f; font-family: 'Space Mono', monospace; }}
  #app {{ display:flex; max-width:900px; margin:20px auto; gap:20px; }}
  #gameCanvas {{
    border: 2px solid #1a2540;
    border-radius: 8px;
    background: #0a0f1a;
    display: block;
    width: 400px;
    height: 600px;
  }}
  #infoPanel {{
    width: 300px;
    font-size: 14px;
    line-height: 1.3;
  }}
  h2 {{ margin-top: 0; }}
  .metric {{
    background: #0d1525;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 12px;
  }}
  .metric strong {{
    color: #f9c74f;
    font-size: 18px;
  }}
  button {{
    background: none;
    border: 1.5px solid #f9c74f;
    color: #f9c74f;
    font-family: 'Space Mono', monospace;
    font-weight: 600;
    padding: 8px 15px;
    margin-top: 10px;
    cursor: pointer;
    border-radius: 5px;
    width: 100%;
  }}
  button:hover {{
    background: #f9c74f;
    color: #0a0f1a;
  }}
</style>
</head>
<body>
<div id="app">
  <canvas id="gameCanvas" width="400" height="600"></canvas>
  <div id="infoPanel">
    <h2>RL Flappy Bird</h2>
    <div class="metric">Generation: <strong id="gen">1</strong></div>
    <div class="metric">Best Score: <strong id="bestScore">0</strong></div>
    <div class="metric">Alive Birds: <strong id="alive">0</strong></div>
    <div class="metric">Current Score: <strong id="score">0</strong></div>
    <button id="toggleBtn">Pause Training</button>
    <label>Training speed:</label>
    <input type="range" id="speedSlider" min="1" max="50" value="{training_speed}" />
  </div>
</div>

<script>
(() => {{
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // Q-learning params
  const statesY = 10;  // Discretize y pos
  const statesVY = 10; // Discretize velocity
  const PIPE_GAP = 140;
  const PIPE_WIDTH = 50;
  const PIPE_SPEED = 3;
  const BIRD_RADIUS = 12;

  let Q = {}; // Q table

  let generation = 1;
  let bestScore = 0;

  // For pause and speed control
  let paused = {str(paused).lower()};
  let trainingSpeed = {training_speed};

  // Bind controls
  const toggleBtn = document.getElementById('toggleBtn');
  const speedSlider = document.getElementById('speedSlider');
  toggleBtn.onclick = () => {{
    paused = !paused;
    toggleBtn.textContent = paused ? 'Resume Training' : 'Pause Training';
  }};
  speedSlider.oninput = () => {{
    trainingSpeed = Number(speedSlider.value);
  }};

  // Bird class
  class Bird {{
    constructor() {{
      this.x = 100;
      this.y = H / 2;
      this.vy = 0;
      this.alive = true;
      this.score = 0;
    }}
    flap() {{
      this.vy = -8;
    }}
    update() {{
      this.vy += 0.5;
      this.y += this.vy;
      if (this.y < BIRD_RADIUS) {{
        this.y = BIRD_RADIUS;
        this.vy = 0;
      }}
      if (this.y > H - BIRD_RADIUS - 80) {{
        this.alive = false;
      }}
    }}
  }}

  // Pipe class
  class Pipe {{
    constructor() {{
      this.x = W;
      this.gapY = 100 + Math.random() * (H - 280);
      this.passed = false;
    }}
    update() {{
      this.x -= PIPE_SPEED;
    }}
    offscreen() {{
      return this.x < -PIPE_WIDTH;
    }}
  }}

  // Discretize state for Q table
  function getState(bird, pipe) {{
    const yState = Math.min(statesY-1, Math.floor(bird.y / (H / statesY)));
    const vyState = Math.min(statesVY-1, Math.floor((bird.vy + 15) / 30 * statesVY));
    const pipeDist = Math.min(9, Math.floor((pipe.x - bird.x) / 40));
    const gapY = Math.min(statesY-1, Math.floor(pipe.gapY / (H / statesY)));
    return `${{yState}},${{vyState}},${{pipeDist}},${{gapY}}`;
  }}

  // Choose action with epsilon-greedy
  function chooseAction(state, epsilon) {{
    if (!Q[state]) {{
      Q[state] = [0,0];
    }}
    if (Math.random() < epsilon) {{
      return Math.floor(Math.random() * 2);
    }}
    return Q[state][0] > Q[state][1] ? 0 : 1;
  }}

  // Q-learning update
  function updateQ(state, action, reward, nextState, alpha, gamma) {{
    if (!Q[nextState]) Q[nextState] = [0,0];
    const maxNext = Math.max(...Q[nextState]);
    Q[state][action] += alpha * (reward + gamma * maxNext - Q[state][action]);
  }}

  // Initialize
  let birds = [];
  let pipes = [];
  let frameCount = 0;
  let score = 0;
  let epsilon = 0.2;
  let alpha = 0.7;
  let gamma = 0.9;

  function reset() {{
    birds = [];
    pipes = [];
    birds.push(new Bird());
    pipes.push(new Pipe());
    score = 0;
  }}

  reset();

  function gameStep() {{
    if (paused) return;

    for (let i=0; i<trainingSpeed; i++) {{
      frameCount++;

      if (frameCount % 90 === 0) {{
        pipes.push(new Pipe());
      }}

      pipes.forEach(pipe => pipe.update());
      if (pipes.length > 0 && pipes[0].offscreen()) {{
        pipes.shift();
      }}

      const pipe = pipes.find(p => p.x + PIPE_WIDTH > birds[0].x) || pipes[0];

      birds.forEach(bird => {{
        if (!bird.alive) return;

        const state = getState(bird, pipe);
        const action = chooseAction(state, epsilon);
        if (action === 1) bird.flap();

        bird.update();

        // Collision check with pipes
        if (bird.x + BIRD_RADIUS > pipe.x && bird.x - BIRD_RADIUS < pipe.x + PIPE_WIDTH) {{
          if (bird.y - BIRD_RADIUS < pipe.gapY || bird.y + BIRD_RADIUS > pipe.gapY + PIPE_GAP) {{
            bird.alive = false;
          }}
        }}

        // Reward system
        let reward = 0;
        if (!bird.alive) reward = -100;
        else if (pipe.x + PIPE_WIDTH < bird.x && !pipe.passed) {{
          pipe.passed = true;
          score++;
          reward = 100;
        }} else {{
          reward = 1;
        }}

        const nextState = getState(bird, pipe);
        updateQ(state, action, reward, nextState, alpha, gamma);
      }});

      // Check if all birds dead
      if (!birds.some(b => b.alive)) {{
        if (score > bestScore) bestScore = score;
        generation++;
        reset();
      }}
    }}
  }}

  // Drawing functions
  function draw() {{
    ctx.clearRect(0,0,W,H);

    // Background stars
    ctx.fillStyle = '#0a0f1a';
    ctx.fillRect(0, 0, W, H);

    // Draw pipes
    pipes.forEach(pipe => {{
      ctx.fillStyle = '#1a5c2a';
      ctx.fillRect(pipe.x, 0, PIPE_WIDTH, pipe.gapY);
      ctx.fillRect(pipe.x, pipe.gapY + PIPE_GAP, PIPE_WIDTH, H - pipe.gapY - PIPE_GAP - 80);

      // Pipe caps
      ctx.fillStyle = '#1a7030';
      ctx.fillRect(pipe.x - 5, pipe.gapY - 16, PIPE_WIDTH + 10, 16);
      ctx.fillRect(pipe.x - 5, pipe.gapY + PIPE_GAP, PIPE_WIDTH + 10, 16);
    }});

    // Draw bird
    birds.forEach(bird => {{
      if (!bird.alive) {{
        ctx.fillStyle = 'rgba(100, 100, 120, 0.15)';
      }} else {{
        ctx.fillStyle = '#f9c74f';
      }}
      ctx.beginPath();
      ctx.arc(bird.x, bird.y, BIRD_RADIUS, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = bird.alive ? '#ff9f00' : 'rgba(100,100,120,0.15)';
      ctx.lineWidth = 2;
      ctx.stroke();
    }});

    // Draw ground
    ctx.fillStyle = '#0d2a1a';
    ctx.fillRect(0, H - 80, W, 80);

    // Draw score
    ctx.fillStyle = '#f9c74f';
    ctx.font = 'bold 28px Space Mono';
    ctx.textAlign = 'center';
    ctx.fillText('Score: ' + score, W/2, 50);

    // Draw generation
    ctx.font = '14px Space Mono';
    ctx.fillText('Gen: ' + generation, 60, H - 40);
  }}

  function loop() {{
    gameStep();
    draw();

    // Update UI
    document.getElementById('gen').textContent = generation;
    document.getElementById('bestScore').textContent = bestScore;
    document.getElementById('alive').textContent = birds.filter(b => b.alive).length;
    document.getElementById('score').textContent = score;

    requestAnimationFrame(loop);
  }}

  loop();

}})();
</script>
</body>
</html>
"""

components.html(game_html, height=650, scrolling=False)

st.markdown("---")
st.caption("Use the sidebar controls to pause training or change speed. The agent learns live using Q-learning, flapping to avoid pipes and improve over generations.")
