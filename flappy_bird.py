import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="GridWorld Live Training", layout="centered")

st.title("🧠 GridWorld Q-Learning (Live Training)")

# ---------- CONTROLS ----------
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    alpha = st.slider("Learning rate", 0.01, 1.0, 0.1)
    gamma = st.slider("Discount", 0.1, 0.99, 0.9)
    epsilon = st.slider("Exploration", 0.01, 1.0, 0.2)
    speed = st.slider("⚡ Speed", 1, 20, 5)

# ---------- GRID ----------
n = 5
goal = (4,4)
trap = (3,3)

actions = ["↑","↓","←","→"]

# ---------- STATE ----------
if "Q" not in st.session_state:
    st.session_state.Q = np.zeros((n,n,4))
    st.session_state.running = False
    st.session_state.state = (0,0)
    st.session_state.episode = 0

Q = st.session_state.Q

# ---------- STEP FUNCTION ----------
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

if col1.button("▶ Start"):
    st.session_state.running = True

if col2.button("⏸ Pause"):
    st.session_state.running = False

st.metric("Episode", st.session_state.episode)

# ---------- GRID DRAW ----------
grid_placeholder = st.empty()

def draw_grid(agent_pos):
    grid = []
    for i in range(n):
        row = []
        for j in range(n):
            if (i,j)==agent_pos:
                row.append("🟡")  # agent
            elif (i,j)==goal:
                row.append("🏁")
            elif (i,j)==trap:
                row.append("💀")
            else:
                a = np.argmax(Q[i,j])
                row.append(actions[a])
        grid.append(" ".join(row))
    return grid

# ---------- TRAINING STEP ----------
if st.session_state.running:
    for _ in range(speed):

        state = st.session_state.state

        # choose action
        if np.random.rand() < epsilon:
            action = np.random.randint(4)
        else:
            action = np.argmax(Q[state[0],state[1]])

        new_state, reward, done = step(state, action)

        # Q update
        Q[state[0],state[1],action] += alpha * (
            reward + gamma * np.max(Q[new_state[0],new_state[1]])
            - Q[state[0],state[1],action]
        )

        st.session_state.state = new_state

        # reset if done
        if done:
            st.session_state.state = (0,0)
            st.session_state.episode += 1
            break

# ---------- DISPLAY ----------
grid = draw_grid(st.session_state.state)

for row in grid:
    grid_placeholder.write(row)

# ---------- AUTO REFRESH ----------
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()
