import streamlit as st
import json
import os
from datetime import date

# Page Config
st.set_page_config(page_title="Solo Leveling System", page_icon="⚔️", layout="centered")

# Custom Styling (Solo Leveling Dark Theme)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #00d2ff;
    }
    .main-title {
        text-align: center;
        color: #00d2ff;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff;
    }
    .quest-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00d2ff;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "player_data.json"

DEFAULT_DATA = {
    "level": 1,
    "xp": 0,
    "gold": 0,
    "stats": {"STR": 10, "INT": 10, "DEX": 10, "VIT": 10},
    "last_completed": None,
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            # Fill in any missing keys from older save files
            for key, value in DEFAULT_DATA.items():
                data.setdefault(key, value)
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return json.loads(json.dumps(DEFAULT_DATA))  # fresh deep copy

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "player" not in st.session_state:
    st.session_state.player = load_data()
if "messages" not in st.session_state:
    st.session_state.messages = []

player = st.session_state.player
today = str(date.today())

# Show messages queued before the last rerun
for kind, text in st.session_state.messages:
    if kind == "success":
        st.success(text)
    elif kind == "error":
        st.error(text)
    elif kind == "balloons":
        st.balloons()
st.session_state.messages = []

# Header
st.markdown("<h1 class='main-title'>⚡ SYSTEM: PLAYER ASCENSION ⚡</h1>", unsafe_allow_html=True)
st.write("---")

# Stats Section
xp_needed = player["level"] * 500
col1, col2, col3 = st.columns(3)
col1.metric("🛡️ LEVEL", f"Lvl {player['level']}")
col2.metric("⚡ XP", f"{player['xp']} / {xp_needed}")
col3.metric("💰 GOLD", f"{player['gold']} G")

st.progress(min(player["xp"] / xp_needed, 1.0))

# Character Attributes
st.subheader("📊 Attributes")
st.text(
    f"💪 STR: {player['stats']['STR']} | 🧠 INT: {player['stats']['INT']} | "
    f"🎯 DEX: {player['stats']['DEX']} | 🛡️ VIT: {player['stats']['VIT']}"
)

st.write("---")
st.subheader("⚔️ DAILY QUESTS")

already_done = player.get("last_completed") == today

if already_done:
    st.info("✅ Today's quests are already submitted. Come back tomorrow, Player.")

# Daily Quests Form
with st.form("daily_quest_form"):
    q1 = st.checkbox("🏋️ [STR] Gym Session / Heavy Workout (+25 XP, +1 STR)", disabled=already_done)
    q2 = st.checkbox("💻 [INT] 1h-2h Focus Video Editing & Skill Practice (+25 XP, +1 INT)", disabled=already_done)
    q3 = st.checkbox("🎯 [DEX] Send 3-5 Proposals/DMs for Outreach (+25 XP, +1 DEX, +20 Gold)", disabled=already_done)
    q4 = st.checkbox("💤 [VIT] Sleep Schedule Met & 2.5L+ Water (+25 XP, +1 VIT)", disabled=already_done)

    submitted = st.form_submit_button("COMPLETE QUESTS ⚔️", disabled=already_done)

if submitted and not already_done:
    gained_xp = 0
    gained_gold = 0

    if q1:
        gained_xp += 25
        player["stats"]["STR"] += 1
    if q2:
        gained_xp += 25
        player["stats"]["INT"] += 1
    if q3:
        gained_xp += 25
        gained_gold += 20
        player["stats"]["DEX"] += 1
    if q4:
        gained_xp += 25
        player["stats"]["VIT"] += 1

    # Bonus for full clear
    if q1 and q2 and q3 and q4:
        gained_xp += 50
        gained_gold += 50
        st.session_state.messages.append(
            ("success", "🎉 DAILY QUEST ALL CLEARED! Bonus +50 XP & +50 Gold Granted!")
        )

    if gained_xp == 0:
        st.warning("Select at least one quest before submitting.")
    else:
        player["xp"] += gained_xp
        player["gold"] += gained_gold
        player["last_completed"] = today

        # Level Up Check
        xp_needed = player["level"] * 500
        while player["xp"] >= xp_needed:
            player["xp"] -= xp_needed
            player["level"] += 1
            st.session_state.messages.append(("balloons", ""))
            st.session_state.messages.append(
                ("success", f"🎊 LEVEL UP! You are now Level {player['level']}!")
            )
            xp_needed = player["level"] * 500

        st.session_state.messages.append(
            ("success", f"Quests complete: +{gained_xp} XP, +{gained_gold} Gold")
        )
        save_data(player)
        st.rerun()

# Shop / Penalty Section
st.write("---")
st.subheader("🎁 REWARDS & SHOP")
if st.button("🎮 Buy Gaming Session (Cost: 100 Gold)"):
    if player["gold"] >= 100:
        player["gold"] -= 100
        save_data(player)
        st.session_state.messages.append(
            ("success", "Reward unlocked! Enjoy your gaming session.")
        )
        st.rerun()
    else:
        st.error("Not enough Gold!")
