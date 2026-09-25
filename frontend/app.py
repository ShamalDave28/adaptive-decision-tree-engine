import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import os

BACKEND_BASE = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
API_URL = f"{BACKEND_BASE}/api"

st.set_page_config(
    page_title="AI Animal Guessing Game",
    page_icon="🤖",
    layout="wide"
)

# Initialize frontend session tracking
if "path" not in st.session_state:
    st.session_state.path = []

if "learning" not in st.session_state:
    st.session_state.learning = False

st.title("🤖 Smart AI Decision Tree Engine")

# Create tabs for playing and visualizing
tab_play, tab_visualize = st.tabs(["🎮 Play Game", "🌳 Knowledge Tree Graph"])

# =====================================================
# TAB 1: GAMEPLAY
# =====================================================
with tab_play:
    st.write("Think of an animal, and let the AI deduce it through question branching.")
    path_str = "/".join(st.session_state.path)

    try:
        response = requests.get(f"{API_URL}/state", params={"path": path_str}, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # SCENARIO A: AI reached a leaf node (Guess)
            if data["is_leaf"] and not st.session_state.learning:
                st.subheader(f"🤔 Is it a **{data['guess']}**?")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes"):
                        st.balloons()
                        st.success(f"🎉 I guessed correctly in {len(st.session_state.path)} questions!")
                with col2:
                    if st.button("❌ No"):
                        st.session_state.learning = True
                        st.rerun()

            # SCENARIO B: Learning Mode
            elif st.session_state.learning:
                st.warning("🧠 I couldn't guess it. Teach me!")

                correct_animal = st.text_input("What animal were you thinking of?")
                new_question = st.text_input("Enter a YES/NO question to distinguish it from my guess:")
                answer = st.radio("For your animal, what is the answer?", ["Yes", "No"])

                if st.button("📚 Teach AI"):
                    if correct_animal.strip() and new_question.strip():
                        payload = {
                            "node_path": st.session_state.path,
                            "correct_animal": correct_animal.strip().title(),
                            "new_question": new_question.strip(),
                            "answer_for_new": answer
                        }

                        teach_res = requests.post(f"{API_URL}/teach", json=payload, timeout=5)

                        if teach_res.status_code == 200:
                            st.success(f"✅ Learned '{correct_animal.strip().title()}' successfully!")
                            st.session_state.path = []
                            st.session_state.learning = False
                            st.rerun()
                        else:
                            error_detail = teach_res.json().get("detail", "Failed to teach backend.")
                            st.error(f"⚠️ {error_detail}")
                    else:
                        st.error("Please fill in all fields.")

            # SCENARIO C: Question Node
            else:
                st.subheader(data["question"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes"):
                        st.session_state.path.append("yes")
                        st.rerun()
                with col2:
                    if st.button("❌ No"):
                        st.session_state.path.append("no")
                        st.rerun()

        else:
            st.error(f"Backend error: {response.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot reach the backend engine. Ensure FastAPI is running on port 8000.")


# =====================================================
# TAB 2: INTERACTIVE TREE VISUALIZATION
# =====================================================
with tab_visualize:
    st.subheader("Interactive Decision Tree Architecture")
    st.write("Below is the live structure of the AI's memory. Drag or zoom to inspect nodes.")

    if st.button("🔄 Refresh Graph"):
        st.rerun()

    try:
        tree_res = requests.get(f"{API_URL}/tree", timeout=5)
        if tree_res.status_code == 200:
            tree_data = tree_res.json()

            # Initialize PyVis network graph
            net = Network(height="500px", width="100%", directed=True, bgcolor="#ffffff", font_color="#000000")

            def add_nodes_to_graph(node, parent_id=None, edge_label=""):
                if not node:
                    return

                # Unique node ID
                current_id = str(id(node)) if "id" not in node else str(node["id"])
                
                # Check if it's a guess (leaf) or a question
                if node.get("guess"):
                    label = f"🐾 {node['guess']}"
                    color = "#2ECC71"  # Emerald Green for answers
                    shape = "box"
                else:
                    label = f"❓ {node['question']}"
                    color = "#3498DB"  # Blue for questions
                    shape = "ellipse"

                # Add current node
                net.add_node(current_id, label=label, color=color, shape=shape)

                # Connect to parent if not root
                if parent_id is not None:
                    net.add_edge(parent_id, current_id, label=edge_label, color="#7F8C8D")

                # Recurse through Yes / No branches
                if node.get("yes"):
                    add_nodes_to_graph(node["yes"], parent_id=current_id, edge_label="YES")
                if node.get("no"):
                    add_nodes_to_graph(node["no"], parent_id=current_id, edge_label="NO")

            add_nodes_to_graph(tree_data)

            # Generate and embed the HTML
            graph_path = "tree_graph.html"
            net.save_graph(graph_path)
            with open(graph_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            components.html(html_content, height=550)

    except Exception as e:
        st.error(f"Error rendering visual graph: {e}")

# Sidebar controls
st.sidebar.title("📊 Game Controls")
st.sidebar.write(f"Questions Asked: **{len(st.session_state.path)}**")

if st.sidebar.button("🔄 Restart Game"):
    st.session_state.path = []
    st.session_state.learning = False
    st.rerun()