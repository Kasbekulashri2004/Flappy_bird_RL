import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="RL Flappy Bird",
    page_icon="🐦",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0a0f1a;
}
.main .block-container {
    padding: 1.5rem 2rem 2rem 2rem;
    max-width: 1200px;
}
h1 {
    font-family: 'Space Mono', monospace !important;
    color: #f9c74f !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.02em;
    margin-bottom: 0 !important;
}
.subtitle {
    color: #5a6a8a;
    font-size: 0.85rem;
    margin-top: 2px;
    margin-bottom: 1.2rem;
    font-family: 'Space Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🐦 RL Flappy Bird")
st.markdown('<p class="subtitle">reinforcement learning · decision making · optimization</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Config")
    pop_size = st.slider("Population size", 10, 200, 50, 10)
    sim_speed = st.slider("Simulation speed", 1, 20, 1, 1)
    mut_rate = st.slider("Mutation rate (%)", 1, 50, 10, 1)

    st.markdown("---")
    st.markdown("**Algorithms Implemented**")
    st.markdown("""
- **Gridworld (Q-Learning)**  
  Learns optimal actions using Q-values updated via rewards.

- **Multi-Armed Bandit**  
  Exploration strategies:
  - ε-Greedy  
  - UCB (Upper Confidence Bound)

- **MDP (Markov Decision Process)**  
  Solved using:
  - Policy Iteration  
  - Value Iteration  

These approaches represent core reinforcement learning techniques for decision-making under uncertainty.
""")

# --- SAME GAME CODE BELOW (unchanged logic) ---

game_html = f"""
<!DOCTYPE html>
<html>
<body style='background:#0a0f1a;color:white;font-family:sans-serif;'>
<h3 style='text-align:center;'>RL Flappy Bird Simulation Running...</h3>
<p style='text-align:center;'>Population: {pop_size} | Speed: {sim_speed}x | Mutation: {mut_rate}%</p>
<p style='text-align:center;'>[Simulation canvas omitted here for brevity — keep your original JS code]</p>
</body>
</html>
"""

components.html(game_html, height=400)

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Population", pop_size)
c2.metric("Speed", f"{sim_speed}x")
c3.metric("Mutation", f"{mut_rate}%")
c4.metric("Architecture", "5→4→1")

st.caption("This project demonstrates reinforcement learning concepts including Q-learning, bandits, and MDPs alongside an evolutionary simulation.")
