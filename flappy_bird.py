import streamlit as st

st.set_page_config(page_title="Flappy Bird RL", layout="centered")

# Sidebar controls
st.sidebar.title("Controls")
paused = st.sidebar.checkbox("Pause Training", value=False)
training_speed = st.sidebar.slider("Training Speed (steps per frame)", 1, 100, 10)

# Display info
st.markdown("## Flappy Bird Q-Learning Training")
st.markdown("""
- The yellow circle is the bird.
- Green vertical bars are pipes.
- Score increments as pipes are passed.
- Use controls to pause/resume and adjust training speed.
""")

# Prepare the HTML and JS for the game
game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0; padding: 0; background: #0a0f1a; font-family: 'Space Mono', monospace;
    color: #f9c74f;
    user-select: none;
  }}
  #gameCanvas {{
    display: block;
    margin: 0 auto;
    background: #0a0f1a;
    border: 2px solid #f9c74f;
    border-radius: 8px;
  }}
  #infoPanel {{
    text-align: center;
    margin-top: 10px;
    font-size: 18px;
  }}
</style>
</head>
<body>
<canvas id="gameCanvas" width="400" height="600"></canvas>
<div id="infoPanel">
  Generation: <span id="gen">1</span> |
  Best Score: <span id="bestScore">0</span> |
  Alive: <span id="alive">1</span> |
  Current Score: <span id="score">0</span>
</div>

<script>
(() => {{
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // Q-learning parameters and environment constants
  const statesY = 10;  // Discretize bird y position
  const statesVY = 10; // Discretize bird velocity
  const PIPE_GAP = 140;
  const PIPE_WIDTH = 50;
  const PIPE_SPEED = 3;
  const BIRD_RADIUS = 12;

  let Q = {{}};

  let generation = 1;
  let bestScore = 0;

  // From Streamlit Python controls
  let paused = {str(paused).lower()};
  let trainingSpeed = {training_speed};

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

  // Discretize state for Q table key
  function getState(bird, pipe) {{
    const yState = Math.min(statesY - 1, Math.floor(bird.y / (H / statesY)));
    const vyState = Math.min(statesVY - 1, Math.floor((bird.vy + 15) / 30 * statesVY));
    const pipeDist = Math.min(9, Math.floor((pipe.x - bird.x) / 40));
    const gapY = Math.min(statesY - 1, Math.floor(pipe.gapY / (H / statesY)));
    return `${{yState}},${{vyState}},${{pipeDist}},${{gapY}}`;
  }}

  // Epsilon-greedy action selection
  function chooseAction(state, epsilon) {{
    if (!Q[state]) {{
      Q[state] = [0, 0];
    }}
    if (Math.random() < epsilon) {{
      return Math.floor(Math.random() * 2);
    }}
    return Q[state][0] > Q[state][1] ? 0 : 1;
  }}

  // Q-learning update
  function updateQ(state, action, reward, nextState, alpha, gamma) {{
    if (!Q[nextState]) Q[nextState] = [0, 0];
    const maxNext = Math.max(...Q[nextState]);
    Q[state][action] += alpha * (reward + gamma * maxNext - Q[state][action]);
  }}

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

    for (let i = 0; i < trainingSpeed; i++) {{
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

        // Collision detection with pipes
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

      if (!birds.some(b => b.alive)) {{
        if (score > bestScore) bestScore = score;
        generation++;
        reset();
      }}
    }}
  }}

  function draw() {{
    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = '#0a0f1a';
    ctx.fillRect(0, 0, W, H);

    // Draw pipes
    pipes.forEach(pipe => {{
      ctx.fillStyle = '#1a5c2a';
      ctx.fillRect(pipe.x, 0, PIPE_WIDTH, pipe.gapY);
      ctx.fillRect(pipe.x, pipe.gapY + PIPE_GAP, PIPE_WIDTH, H - pipe.gapY - PIPE_GAP - 80);

      ctx.fillStyle = '#1a7030';
      ctx.fillRect(pipe.x - 5, pipe.gapY - 16, PIPE_WIDTH + 10, 16);
      ctx.fillRect(pipe.x - 5, pipe.gapY + PIPE_GAP, PIPE_WIDTH + 10, 16);
    }});

    // Draw bird
    birds.forEach(bird => {{
      ctx.fillStyle = bird.alive ? '#f9c74f' : 'rgba(100, 100, 120, 0.15)';
      ctx.beginPath();
      ctx.arc(bird.x, bird.y, BIRD_RADIUS, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = bird.alive ? '#ff9f00' : 'rgba(100,100,120,0.15)';
      ctx.lineWidth = 2;
      ctx.stroke();
    }});

    // Ground
    ctx.fillStyle = '#0d2a1a';
    ctx.fillRect(0, H - 80, W, 80);

    // Score text
    ctx.fillStyle = '#f9c74f';
    ctx.font = 'bold 28px Space Mono';
    ctx.textAlign = 'center';
    ctx.fillText('Score: ' + score, W / 2, 50);

    ctx.font = '14px Space Mono';
    ctx.fillText('Gen: ' + generation, 60, H - 40);
  }}

  function loop() {{
    gameStep();
    draw();

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

# Embed the game HTML in Streamlit with scrolling disabled and full height
st.components.v1.html(game_html, height=650, scrolling=False)
