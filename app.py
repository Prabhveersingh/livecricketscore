import streamlit as st
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Cricket League", layout="wide")

DB_FILE = "data.json"
HISTORY_FILE = "history.json" # New file for match history

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                d = json.load(f)
                defaults = {
                    "team_a": "Team A", "team_b": "Team B", "max_overs": 20, "innings": 1,
                    "score": 0, "wickets": 0, "balls": 0, "overs": 0.0, "target": 0,
                    "team_a_squad": [], "team_b_squad": [], "batting_stats": {}, "bowling_stats": {},
                    "out_players": [], "current_striker": "None", "current_non_striker": "None", 
                    "current_bowler": "None", "is_finished": False, "winner": ""
                }
                for key, val in defaults.items():
                    if key not in d: d[key] = val
                return d
            except: pass
    return {
        "team_a": "Team A", "team_b": "Team B", "max_overs": 20, "innings": 1,
        "score": 0, "wickets": 0, "balls": 0, "overs": 0.0, "target": 0,
        "team_a_squad": [], "team_b_squad": [], "batting_stats": {}, "bowling_stats": {},
        "out_players": [], "current_striker": "None", "current_non_striker": "None", 
        "current_bowler": "None", "is_finished": False, "winner": ""
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- NEW HISTORY FUNCTIONS ---
def save_to_history(data):
    history_file = "history.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try: history = json.load(f)
            except: history = []
    
    match_summary = {
        "teams": f"{data['team_a']} vs {data['team_b']}",
        "winner": data['winner'],
        "score": f"{data['score']}/{data['wickets']} ({data['overs']} ov)",
        "batting_stats": data["batting_stats"], # Yeh line zaroori hai
        "bowling_stats": data["bowling_stats"]  # Yeh line zaroori hai
    }
    
    if not history or history[-1] != match_summary:
        history.append(match_summary)
        with open(history_file, "w") as f:
            json.dump(history, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

data = load_data()

# --- CSS ---
st.markdown("""
    <style>
    .main-score { background-color: grey; padding: 30px; border-radius: 20px; color: white; text-align: center; border-bottom: 5px solid #ff4b4b; }
    .target-box { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 10px; }
    .winner-box { background: linear-gradient(90deg, #28a745, #1e7e34); color: white; padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 20px; border: 4px solid white; }
    .player-box { background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #31333F; text-align: center;}
    </style>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", ["📺 Viewer Page", "⚙️ Admin Panel"])

if page == "⚙️ Admin Panel":
    st.title("Admin Control Room")
    if not st.session_state["authenticated"]:
        pwd = st.text_input("Admin PIN", type="password")
        if st.button("Login"):
            if pwd == "sidhu-amg": st.session_state["authenticated"] = True; st.rerun()
    else:
        tab1, tab2 = st.tabs(["🏗️ Setup & Innings", "🏏 Match Control"])
        with tab1:
            st.subheader("Update Team Names")
            with st.form("name_update"):
                new_a = st.text_input("Team A Name", value=data["team_a"])
                new_b = st.text_input("Team B Name", value=data["team_b"])
                if st.form_submit_button("Submit Names"):
                    data["team_a"] = new_a
                    data["team_b"] = new_b
                    save_data(data)
                    st.success("Names Updated!")
                    st.rerun()

            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"Squad: {data['team_a']}")
                with st.form("a_form", clear_on_submit=True):
                    name_a = st.text_input("Add Player")
                    if st.form_submit_button("Add to A"):
                        if name_a: data["team_a_squad"].append(name_a); save_data(data); st.rerun()
            with c2:
                st.write(f"Squad: {data['team_b']}")
                with st.form("b_form", clear_on_submit=True):
                    name_b = st.text_input("Add Player")
                    if st.form_submit_button("Add to B"):
                        if name_b: data["team_b_squad"].append(name_b); save_data(data); st.rerun()
            
            st.divider()
            
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                if st.button("🔄 START 2nd INNINGS", type="primary", use_container_width=True):
                    data["target"] = data["score"] + 1
                    data["score"] = 0; data["wickets"] = 0; data["balls"] = 0; data["overs"] = 0.0
                    data["innings"] = 2; data["out_players"] = []; data["batting_stats"] = {}; data["bowling_stats"] = {}
                    data["is_finished"] = False; data["winner"] = ""
                    save_data(data); st.rerun()
            
            with col_in2:
                if st.button("🚨 RESET FULL MATCH", type="secondary", use_container_width=True):
                    if os.path.exists(DB_FILE): os.remove(DB_FILE)
                    st.warning("Match Data Cleared! Refreshing...")
                    st.rerun()

        with tab2:
            bat_sq = data["team_a_squad"] if data["innings"] == 1 else data["team_b_squad"]
            bow_sq = data["team_b_squad"] if data["innings"] == 1 else data["team_a_squad"]
            
            if not data["is_finished"]:
                col1, col2 = st.columns(2)
                with col1:
                    avail = [p for p in bat_sq if p not in data["out_players"]]
                    if avail:
                        data["current_striker"] = st.selectbox("Striker", avail)
                        data["current_non_striker"] = st.selectbox("Non-Striker", [p for p in avail if p != data["current_striker"]])
                        data["current_bowler"] = st.selectbox("Bowler", bow_sq)
                        res = st.selectbox("Ball Result", [0, 1, 2, 3, 4, 6, "Wicket"])
                        
                        if st.button("Submit Ball"):
                            if data["current_striker"] not in data["batting_stats"]: data["batting_stats"][data["current_striker"]] = {"r":0, "b":0}
                            if data["current_bowler"] not in data["bowling_stats"]: data["bowling_stats"][data["current_bowler"]] = {"o":0.0, "w":0, "r":0, "balls":0}
                            
                            if res == "Wicket":
                                data["wickets"] += 1; data["out_players"].append(data["current_striker"])
                                data["bowling_stats"][data["current_bowler"]]["w"] += 1
                            else:
                                r = int(res); data["score"] += r
                                data["batting_stats"][data["current_striker"]]["r"] += r
                                data["batting_stats"][data["current_striker"]]["b"] += 1
                                data["bowling_stats"][data["current_bowler"]]["r"] += r
                            
                            data["balls"] += 1
                            data["overs"] = float(f"{data['balls'] // 6}.{data['balls'] % 6}")
                            
                            if data["innings"] == 2:
                                if data["score"] >= data["target"]:
                                    data["is_finished"] = True; data["winner"] = data["team_b"]
                                    save_to_history(data) # Logic for history
                                elif data["wickets"] >= len(bat_sq) or data["balls"] >= (data["max_overs"] * 6):
                                    data["is_finished"] = True; data["winner"] = data["team_a"]
                                    save_to_history(data) # Logic for history
                            
                            save_data(data); st.rerun()
                    else:
                        st.error("No Players Available")
            else:
                st.success(f"Match Over! Winner: {data['winner']}")

else:
    # --- VIEWER PAGE ---
    if data["is_finished"] and data["winner"]:
        st.markdown(f"<div class='winner-box'>🎊 {data['winner'].upper()} WON THE MATCH! 🎊</div>", unsafe_allow_html=True)
        st.balloons()
    
    bat_team = data["team_a"] if data["innings"] == 1 else data["team_b"]
    st.markdown(f"<h2 style='text-align: center;'>🏆 {data['team_a']} vs {data['team_b']}</h2>", unsafe_allow_html=True)
    
    target_text = ""
    if data["innings"] == 2 and not data["is_finished"] and data["target"] > 0:
        runs_needed = data["target"] - data["score"]
        balls_left = (data["max_overs"] * 6) - data["balls"]
        if runs_needed > 0:
            target_text = f"<div class='target-box'>TARGET: {data['target']} | Need {runs_needed} runs in {balls_left} balls</div>"

    st.markdown(f"""
        <div class="main-score">
            <h4 style='color:black'>{bat_team} - Batting</h4>
            <h1 style='font-size: 80px; margin: 0; color:black;'>{data['score']} - {data['wickets']}</h1>
            <p>Overs: {data['overs']} / {data['max_overs']}</p>
            {target_text}
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if not data["is_finished"]:
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='player-box'>🏏 <b>Striker</b><br>{data['current_striker']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='player-box'>🏃 <b>Non-Striker</b><br>{data['current_non_striker']}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='player-box'>🥎 <b>Bowler</b><br>{data['current_bowler']}</div>", unsafe_allow_html=True)

    st.divider()
    t1, t2 = st.tabs(["📊 Scorecard", "👥 Squad Status"])
    with t1:
        sc1, sc2 = st.columns(2)
        with sc1:
            st.write(f"**{bat_team} Batting**")
            st.table([{"Name": k, "R": v["r"], "B": v["b"]} for k, v in data["batting_stats"].items()])
        with sc2:
            bowling_team = data["team_b"] if data["innings"] == 1 else data["team_a"]
            st.write(f"**{bowling_team} Bowling**")
            st.table([{"Name": k, "O": v["o"], "W": v["w"], "R": v["r"]} for k, v in data["bowling_stats"].items()])
    
    with t2:
        s1, s2 = st.columns(2)
        batting_squad = data["team_a_squad"] if data["innings"] == 1 else data["team_b_squad"]
        with s1:
            st.write("**Remaining to Bat**")
            for p in batting_squad:
                if p not in data["out_players"] and p not in [data["current_striker"], data["current_non_striker"]]:
                    st.write(f"• {p}")
        with s2:
            st.write("**Out**")
            for p in data["out_players"]: st.write(f"~~{p}~~")

    # --- MATCH HISTORY SECTION AT THE BOTTOM ---
    st.divider()
    st.subheader("📜 Match Result")
    match_history = load_history()
    
    if match_history:
        # Show latest matches first
        for m in reversed(match_history):
            with st.expander(f"🏁 {m['teams']} | {m['winner']} Won"):
                st.write(f"**Final Score:** {m['score']}")
    else:
        st.info("No match history available yet.")

# --- DETAILED MATCH HISTORY SECTION ---
    st.divider()
    st.subheader("📜 Detailed Match History")
    match_history = load_history()
    
    if match_history:
        # Latest match sabse upar dikhane ke liye reverse kiya gaya hai
        for idx, m in enumerate(reversed(match_history)):
            with st.expander(f"Match Details: {m['teams']} | Winner: {m['winner']}"):
                st.write(f"**Final Summary:** {m['score']}")
                
                # Do columns banaye gaye hain stats ko side-by-side dikhane ke liye
                col_hist1, col_hist2 = st.columns(2)
                
                with col_hist1:
                    st.write("**Batting Performance**")
                    # Yahan purani batting stats ko table mein dikhaya jayega
                    if "batting_stats" in m:
                        hist_bat_data = [{"Player": k, "Runs": v["r"], "Balls": v["b"]} for k, v in m["batting_stats"].items()]
                        st.table(hist_bat_data)
                    else:
                        st.info("No detailed batting stats saved for this match.")
                
                with col_hist2:
                    st.write("**Bowling Performance**")
                    # Yahan purani bowling stats ko table mein dikhaya jayega
                    if "bowling_stats" in m:
                        hist_bowl_data = [{"Bowler": k, "Overs": v["o"], "Wickets": v["w"], "Runs": v["r"]} for k, v in m["bowling_stats"].items()]
                        st.table(hist_bowl_data)
                    else:
                        st.info("No detailed bowling stats saved for this match.")
    else:
        st.info("No detailed match history available yet.")