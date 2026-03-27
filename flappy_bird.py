import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RL Flappy Bird", page_icon="🐦", layout="wide")

# --- Minimal Clean UI Styling ---
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: system-ui, sans-serif;
}
.stApp {
    background: #0a0f1a;
}
h1 {
    color: #f9c74f !important;
    font-size: 1.6rem !important;
}
section[data-testid="stSidebar"] {
    background: #060b14 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🐦 RL Flappy Bird")

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    pop_size = st.slider("Population", 10, 200, 50, 10)
    sim_speed = st.slider("Speed", 1, 20, 5, 1)
    mut_rate = st.slider("Mutation (%)", 1, 50, 10, 1)

# --- Game HTML ---
game_html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;background:#0a0f1a;">
<canvas id="gc" width="400" height="500"></canvas>

<script>
const POP_SIZE = {pop_size};
const SIM_SPEED = {sim_speed};
const MUT_RATE = {mut_rate/100};

const canvas = document.getElementById('gc');
const ctx = canvas.getContext('2d');
const W=400, H=500;

function rand() {{ return Math.random()*2-1; }}

class Net {{
  constructor(w) {{
    this.w = w ? [...w] : Array.from({{length:24}}, rand);
  }}
  forward(i) {{
    let h=[0,0,0,0];
    for(let j=0;j<4;j++){{
      for(let k=0;k<5;k++) h[j]+=i[k]*this.w[j*5+k];
      h[j]=Math.tanh(h[j]);
    }}
    let o=0;
    for(let j=0;j<4;j++) o+=h[j]*this.w[20+j];
    return Math.tanh(o);
  }}
  mutate(r) {{
    return new Net(this.w.map(v=>Math.random()<r ? v+(Math.random()*2-1)*0.3 : v));
  }}
}}

function bird(net) {{
  return {{x:80,y:H/2,vy:0,alive:true,fitness:0,net:net||new Net()}};
}}

let birds=[], pipes=[], frame=0;

function pipe() {{
  let top = 80 + Math.random()*(H-200);
  pipes.push({{x:W, top, bot:top+140}});
}}

function init() {{
  birds = Array.from({{length:POP_SIZE}},()=>bird());
  pipes=[]; frame=0; pipe();
}}

function evolve() {{
  birds.sort((a,b)=>b.fitness-a.fitness);
  let best = birds[0];
  let next=[bird(best.net)];
  while(next.length<POP_SIZE){{
    next.push(bird(best.net.mutate(MUT_RATE)));
  }}
  birds=next; pipes=[]; frame=0; pipe();
}}

function step() {{
  frame++;
  if(frame%80===0) pipe();

  pipes.forEach(p=>p.x-=2.5);

  for(let b of birds){{
    if(!b.alive) continue;

    let p=pipes[0];
    let out=b.net.forward([
      b.y/H,
      b.vy/10,
      (p.x-b.x)/W,
      p.top/H,
      p.bot/H
    ]);

    if(out>0) b.vy=-6;
    b.vy+=0.4;
    b.y+=b.vy;

    b.fitness++;

    if(b.y<0||b.y>H) b.alive=false;

    if(b.x>p.x && b.x<p.x+50){{
      if(b.y<p.top||b.y>p.bot) b.alive=false;
    }}
  }}

  if(birds.every(b=>!b.alive)) evolve();
}}

function draw() {{
  ctx.fillStyle="#0a0f1a";
  ctx.fillRect(0,0,W,H);

  // pipes
  ctx.fillStyle="#2a8c3a";
  for(let p of pipes){{
    ctx.fillRect(p.x,0,50,p.top);
    ctx.fillRect(p.x,p.bot,50,H-p.bot);
  }}

  // birds
  ctx.fillStyle="#f9c74f";
  for(let b of birds){{
    if(b.alive) ctx.fillRect(b.x,b.y,8,8);
  }}
}}

function loop(){{
  for(let i=0;i<SIM_SPEED;i++) step();
  draw();
  requestAnimationFrame(loop);
}}

init();
loop();
</script>
</body>
</html>
"""

components.html(game_html, height=520)

# --- Bottom Metrics ---
c1, c2, c3 = st.columns(3)
c1.metric("Population", pop_size)
c2.metric("Speed", f"{sim_speed}x")
c3.metric("Mutation", f"{mut_rate}%")
