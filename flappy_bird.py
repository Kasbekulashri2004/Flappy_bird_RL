import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="GridWorld RL", layout="centered")

# ---------- UI STYLE ----------
st.markdown("""
<style>
.stApp { background-color: #0a0f1a; color: #e0e6f0; }
h1 { color: #f9c74f; }
.block-container { padding-top: 2rem; }
.metric-box {
    background: #0d1525;
    border: 1px solid #1a2540;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 GridWorld Q-Learning")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ Controls")

    episodes = st.slider("Episodes", 100, 5000, 1000)
    alpha = st.slider("Learning rate (α)", 0.01, 1.0, 0.1)
    gamma = st.slider("Discount (γ)", 0.1, 0.99, 0.9)
    epsilon = st.slider("Exploration (ε)", 0.01, 1.0, 0.2)

    st.markdown("---")
    speed = st.slider("⚡ Training Speed", 1, 50, 10)

# ---------- GRID ----------
n = 5
goal = (4,4)
trap = (3,3)

actions = ["↑","↓","←","→"]

if "Q" not in st.session_state:
    st.session_state.Q = np.zeros((n,n,4))
    st.session_state.episode = 0
    st.session_state.running = False

Q = st.session_state.Q

def step(state, action):
    x,y = state

    if action == 0: x -= 1
    if action == 1: x += 1
    if action == 2: y -= 1
    if action == 3: y += 1

    x = max(0, min(n-1, x))
    y = max(0, min(n-1, y))

    if (x,y) == goal:
        return (x,y), 10, True
    if (x,y) == trap:
        return (x,y), -10, True

    return (x,y), -0.1, False


# ---------- BUTTONS ----------
col1, col2 = st.columns(2)

if col1.button("▶ Start Training"):
    st.session_state.running = True

if col2.button("⏸ Pause"):
    st.session_state.running = False

# ---------- METRICS ----------
m1, m2 = st.columns(2)
m1.metric("Episode", st.session_state.episode)
m2.metric("Status", "RUNNING" if st.session_state.running else "PAUSED")

# ---------- GRID DISPLAY ----------
grid_placeholder = st.empty()

def draw_grid():
    grid = []
    for i in range(n):
        row = []
        for j in range(n):
            if (i,j)==goal:
                row.append("🏁")
            elif (i,j)==trap:
                row.append("💀")
            else:
                a = np.argmax(Q[i,j])
                row.append(actions[a])
        grid.append(" ".join(row))
    return grid

# ---------- TRAIN LOOP ----------
if st.session_state.running:
    for _ in range(speed):  # SPEED CONTROL
        if st.session_state.episode >= episodes:
            st.session_state.running = False
            break

        state = (0,0)

        while True:
            if np.random.rand() < epsilon:
                action = np.random.randint(4)
            else:
                action = np.argmax(Q[state[0],state[1]])

            new_state, reward, done = step(state, action)

            Q[state[0],state[1],action] += alpha * (
                reward + gamma * np.max(Q[new_state[0],new_state[1]])
                - Q[state[0],state[1],action]
            )

            state = new_state

            if done:
                break

        st.session_state.episode += 1

# ---------- DRAW GRID ----------
grid = draw_grid()
for row in grid:
    grid_placeholder.write(row)

# ---------- AUTO REFRESH ----------
if st.session_state.running:
    time.sleep(0.05)
    st.rerun()
