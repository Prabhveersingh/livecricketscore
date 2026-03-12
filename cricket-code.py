import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Pro Cricket League",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS ---
DB_FILE = "data.json"
HISTORY_FILE = "history.json"
ADMIN_PIN = "sidhu-amg"  # Change this in production

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "last_update" not in st.session_state:
    st.session_state["last_update"] = time.time()
if "ball_by_ball" not in st.session_state:
    st.session_state["ball_by_ball"] = []
if "match_events" not in st.session_state:
    st.session_state["match_events"] = []

# --- DATA MANAGEMENT CLASS ---
class CricketDataManager:
    @staticmethod
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
                        "current_bowler": "None", "is_finished": False, "winner": "", "toss_winner": "",
                        "match_start_time": "", "partnership_runs": 0, "partnership_balls": 0,
                        "run_rate": 0.0, "required_run_rate": 0.0, "extras": 0
                    }
                    for key, val in defaults.items():
                        if key not in d: d[key] = val
                    return d
                except: 
                    return CricketDataManager.get_default_data()
        return CricketDataManager.get_default_data()
    
    @staticmethod
    def get_default_data():
        return {
            "team_a": "Team A", "team_b": "Team B", "max_overs": 20, "innings": 1,
            "score": 0, "wickets": 0, "balls": 0, "overs": 0.0, "target": 0,
            "team_a_squad": [], "team_b_squad": [], "batting_stats": {}, "bowling_stats": {},
            "out_players": [], "current_striker": "None", "current_non_striker": "None", 
            "current_bowler": "None", "is_finished": False, "winner": "", "toss_winner": "",
            "match_start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "partnership_runs": 0, "partnership_balls": 0, "run_rate": 0.0,
            "required_run_rate": 0.0, "extras": 0
        }
    
    @staticmethod
    def save_data(data):
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def save_to_history(data):
        history_file = "history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                try: 
                    history = json.load(f)
                except: 
                    history = []
        # Calculate economy rates and strike rates
        batting_performance = []
        for player, stats in data["batting_stats"].items():
            strike_rate = (stats["r"] / stats["b"] * 100) if stats["b"] > 0 else 0
            batting_performance.append({
                "player": player,
                "runs": stats["r"],
                "balls": stats["b"],
                "strike_rate": round(strike_rate, 2)
            })
        
        bowling_performance = []
        for player, stats in data["bowling_stats"].items():
            overs_bowled = stats["balls"] // 6 + (stats["balls"] % 6) / 10
            economy = stats["r"] / overs_bowled if overs_bowled > 0 else 0
            bowling_performance.append({
                "player": player,
                "overs": overs_bowled,
                "maidens": stats.get("maidens", 0),
                "runs": stats["r"],
                "wickets": stats["w"],
                "economy": round(economy, 2)
            })
        
        match_summary = {
            "match_id": len(history) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "teams": f"{data['team_a']} vs {data['team_b']}",
            "winner": data['winner'],
            "score": f"{data['score']}/{data['wickets']} ({data['overs']} ov)",
            "batting_stats": batting_performance,
            "bowling_stats": bowling_performance,
            "man_of_match": CricketDataManager.get_man_of_match(data)
        }
        
        if not history or history[-1].get("match_id") != match_summary["match_id"]:
            history.append(match_summary)
            with open(history_file, "w") as f:
                json.dump(history, f, indent=4)
    
    @staticmethod
    def get_man_of_match(data):
        # Simple logic for MOM - can be enhanced
        top_score = 0
        mom = "TBD"
        for player, stats in data["batting_stats"].items():
            if stats["r"] > top_score:
                top_score = stats["r"]
                mom = player
        for player, stats in data["bowling_stats"].items():
            if stats["w"] > 3:  # 3+ wickets
                mom = player
        return mom
    
    @staticmethod
    def load_history():
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                try: 
                    return json.load(f)
                except: 
                    return []
        return []

# --- CSS STYLING ---
def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');
        
        * {
            font-family: 'Montserrat', sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .main-score {
            background: linear-gradient(135deg, #141E30 0%, #243B55 100%);
            padding: 40px;
            border-radius: 25px;
            color: white;
            text-align: center;
            border: 3px solid #ff4b4b;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        
        .target-box {
            background: linear-gradient(90deg, #ff4b4b, #ff6b6b);
            color: white;
            padding: 20px;
            border-radius: 15px;
            font-weight: bold;
            margin-top: 15px;
            font-size: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .winner-box {
            background: linear-gradient(90deg, #28a745, #1e7e34);
            color: white;
            padding: 40px;
            border-radius: 25px;
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            margin: 20px 0;
            border: 5px solid gold;
            animation: glow 2s ease-in-out infinite;
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 5px gold; }
            50% { box-shadow: 0 0 30px gold; }
            100% { box-shadow: 0 0 5px gold; }
        }
        
        .player-box {
            background: white;
            padding: 25px;
            border-radius: 20px;
            border: 2px solid #667eea;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .player-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        
        .commentary-box {
            background: #1a1a1a;
            color: #fff;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #ff4b4b;
            margin: 10px 0;
        }
        
        .run-rate-indicator {
            width: 100%;
            height: 10px;
            background: #eee;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .run-rate-fill {
            height: 100%;
            background: linear-gradient(90deg, #00b09b, #96c93d);
            border-radius: 5px;
            transition: width 0.5s ease;
        }
        </style>
    """, unsafe_allow_html=True)
# Check match end conditions
                        if data["innings"] == 2:
                            if data["score"] >= data["target"]:
                                data["is_finished"] = True
                                data["winner"] = data["team_b"]
                                add_match_event("MATCH_END", f"{data['team_b']} wins by {10 - data['wickets']} wickets!", {})
                                CricketDataManager.save_to_history(data)
                            elif data["wickets"] >= len(batting_team) - 1:  # All out
                                data["is_finished"] = True
                                data["winner"] = data["team_a"]
                                add_match_event("MATCH_END", f"{data['team_a']} wins by {data['target'] - data['score']} runs!", {})
                                CricketDataManager.save_to_history(data)
                            elif data["balls"] >= data["max_overs"] * 6:
                                data["is_finished"] = True
                                if data["score"] >= data["target"]:
                                    data["winner"] = data["team_b"]
                                else:
                                    data["winner"] = data["team_a"]
                                add_match_event("MATCH_END", f"{data['winner']} wins!", {})
                                CricketDataManager.save_to_history(data)
                        
                        # Update current players
                        data["current_striker"] = striker
                        data["current_non_striker"] = non_striker
                        data["current_bowler"] = bowler
                        
                        # Swap strike if runs are odd
                        if actual_runs % 2 == 1 and not is_wicket and ball_type not in ["Wide", "No Ball"]:
                            data["current_striker"], data["current_non_striker"] = data["current_non_striker"], data["current_striker"]
                            add_match_event("STRIKE", f"Strike swapped! {data['current_striker']} on strike", {})
                        
                        # End of over - swap strike
                        if data["balls"] % 6 == 0 and data["balls"] > 0:
                            data["current_striker"], data["current_non_striker"] = data["current_non_striker"], data["current_striker"]
                            add_match_event("OVER_END", f"Over {int(data['balls']/6)} completed. Strike swapped.", {})
                        
                        # Add commentary for the ball
                        if is_wicket:
                            comment = f"WICKET! {striker} is out!"
                        elif actual_runs == 0:
                            comment = f"No run. {bowler} to {striker}"
                        else:
                            comment = f"{actual_runs} run{'s' if actual_runs > 1 else ''}. {striker} scores"
                        
                        add_match_event("BALL", comment, ball_record)
                        
                        CricketDataManager.save_data(data)
                        st.rerun()
                
                else:
                    st.error("Not enough players available! Need at least 2 batsmen.")
            else:
                st.success(f"Match Complete! Winner: {data['winner']}")
        
        with tabs[2]:
            st.subheader("📊 Advanced Statistics")
            
            if data["batting_stats"] or data["bowling_stats"]:
                col_adv1, col_adv2 = st.columns(2)
                
                with col_adv1:
                    st.write("**Batting Stats with Strike Rates**")
                    bat_df = pd.DataFrame([
                        {
                            "Player": k,
                            "Runs": v["r"],
                            "Balls": v["b"],
                            "4s": v.get("4s", 0),
                            "6s": v.get("6s", 0),
                            "SR": round(v["r"] / v["b"] * 100 if v["b"] > 0 else 0, 2)
                        }
                        for k, v in data["batting_stats"].items()
                    ])
                    if not bat_df.empty:
                        st.dataframe(bat_df, use_container_width=True)
                    else:
                        st.info("No batting data available")
                
                with col_adv2:
                    st.write("**Bowling Stats with Economy**")
                    bowl_df = pd.DataFrame([
                        {
                            "Player": k,
                            "Overs": round(v["balls"] / 6 + (v["balls"] % 6) / 10, 1),
                            "Maidens": v.get("maidens", 0),
                            "Runs": v["r"],
                            "Wkts": v["w"],
                            "Econ": round(v["r"] / (v["balls"] / 6) if v["balls"] > 0 else 0, 2)
                        }
                        for k, v in data["bowling_stats"].items()
                    ])
                    if not bowl_df.empty:
                        st.dataframe(bowl_df, use_container_width=True)
                    else:
                        st.info("No bowling data available")
# Visualization
                if not bat_df.empty:
                    fig = go.Figure(data=[
                        go.Bar(name='Runs', x=bat_df['Player'], y=bat_df['Runs'], marker_color='#FF6B6B'),
                        go.Bar(name='Balls', x=bat_df['Player'], y=bat_df['Balls'], marker_color='#4ECDC4')
                    ])
                    fig.update_layout(
                        title="Batting Performance",
                        barmode='group',
                        template='plotly_dark',
                        xaxis_title="Batsmen",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Worm graph for ball-by-ball progression
                if st.session_state["ball_by_ball"]:
                    st.subheader("📈 Match Progression")
                    cumulative_runs = []
                    ball_numbers = []
                    total = 0
                    for i, ball in enumerate(st.session_state["ball_by_ball"]):
                        if not ball.get('is_wicket', False):
                            total += ball.get('runs', 0)
                        cumulative_runs.append(total)
                        ball_numbers.append(i + 1)
                    
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=ball_numbers,
                        y=cumulative_runs,
                        mode='lines+markers',
                        name='Runs',
                        line=dict(color='#FFD93D', width=3),
                        marker=dict(size=6)
                    ))
                    fig2.update_layout(
                        title="Run Progression (Ball by Ball)",
                        xaxis_title="Balls",
                        yaxis_title="Total Runs",
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No statistics available yet")
        
        with tabs[3]:
            st.subheader("📝 Live Commentary")
            
            # Display recent events
            if st.session_state["match_events"]:
                for event in reversed(st.session_state["match_events"][-15:]):
                    if event["type"] == "WICKET":
                        st.markdown(f"<div class='commentary-box' style='border-left-color: #ff0000;'>🔴 {event['time']} - {event['description']}</div>", unsafe_allow_html=True)
                    elif event["type"] == "FOUR":
                        st.markdown(f"<div class='commentary-box' style='border-left-color: #00ff00;'>🟢 {event['time']} - {event['description']}</div>", unsafe_allow_html=True)
                    elif event["type"] == "SIX":
                        st.markdown(f"<div class='commentary-box' style='border-left-color: #ffff00;'>🟡 {event['time']} - {event['description']}</div>", unsafe_allow_html=True)
                    elif event["type"] == "OVER_END":
                        st.markdown(f"<div class='commentary-box' style='border-left-color: #00ffff;'>🔵 {event['time']} - {event['description']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='commentary-box'>⚪ {event['time']} - {event['description']}</div>", unsafe_allow_html=True)
            else:
                st.info("No commentary available yet")
            
            # Add custom commentary
            with st.form("commentary_form"):
                custom_comment = st.text_area("Add Custom Commentary", placeholder="Enter your commentary here...")
                if st.form_submit_button("Add Commentary"):
                    add_match_event("COMMENTARY", custom_comment, {})
                    st.success("Commentary added!")
                    st.rerun()

elif page == "📺 Live Match":
    # --- LIVE MATCH VIEWER PAGE ---
    
    if data["is_finished"] and data["winner"]:
        st.markdown(f"<div class='winner-box'>🏆 {data['winner'].upper()} WON THE MATCH! 🏆</div>", unsafe_allow_html=True)
        st.balloons()
        st.snow()
    
    # Match Header
    st.markdown(f"""
        <div class='main-header'>
            <h1>{data['team_a']} vs {data['team_b']}</h1>
            <p style='font-size: 20px;'>Live from Pro Cricket Stadium • {data['max_overs']} Overs Match</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main Score Display
    batting_team = data["team_a"] if data["innings"] == 1 else data["team_b"]
    bowling_team = data["team_b"] if data["innings"] == 1 else data["team_a"]
    
    # Calculate required runs if in second innings
    target_text = ""
    required_run_rate = 0
    if data["innings"] == 2 and not data["is_finished"] and data["target"] > 0:
        runs_needed = data["target"] - data["score"]
        balls_left = (data["max_overs"] * 6) - data["balls"]
        wickets_left = 10 - data["wickets"]
        if runs_needed > 0 and balls_left > 0:
            required_run_rate = (runs_needed / balls_left) * 6
            target_text = f"""
                <div class='target-box'>
                    🎯 TARGET: {data['target']} | NEED {runs_needed} RUNS IN {balls_left} BALLS
                    <br>RRR: {required_run_rate:.2f} | CRR: {data['run_rate']:.2f} | WKTS LEFT: {wickets_left}
                </div>
            """
    
    st.markdown(f"""
        <div class="main-score">
            <h2 style='color: #fff;'>{batting_team} - Batting</h2>
            <h1 style='font-size: 100px; margin: 10px 0;'>{data['score']}/{data['wickets']}</h1>
            <p style='font-size: 24px;'>Overs: {data['overs']:.1f} / {data['max_overs']}</p>
            <p style='font-size: 20px;'>Current Run Rate: {data['run_rate']:.2f}</p>
            {target_text}
        </div>
    """, unsafe_allow_html=True)
# Get non-striker stats
        non_striker_stats = data['batting_stats'].get(data['current_non_striker'], {})
        non_striker_runs = non_striker_stats.get('r', 0)
        non_striker_balls = non_striker_stats.get('b', 0)
        non_striker_sr = round(non_striker_runs / non_striker_balls * 100, 2) if non_striker_balls > 0 else 0
        
        with col_p2:
            st.markdown(f"""
                <div class="player-box">
                    <h3>🏃 Non-Striker</h3>
                    <h2>{data['current_non_striker']}</h2>
                    <p>{non_striker_runs} runs from {non_striker_balls} balls</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Get bowler stats
        bowler_stats = data['bowling_stats'].get(data['current_bowler'], {})
        bowler_wickets = bowler_stats.get('w', 0)
        bowler_runs = bowler_stats.get('r', 0)
        bowler_balls = bowler_stats.get('balls', 0)
        bowler_overs = round(bowler_balls / 6 + (bowler_balls % 6) / 10, 1)
        
        with col_p3:
            st.markdown(f"""
                <div class="player-box">
                    <h3>🎯 Bowler</h3>
                    <h2>{data['current_bowler']}</h2>
                    <p>{bowler_wickets}/{bowler_runs} in {bowler_overs} overs</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_p4:
            partnership = f"{data['partnership_runs']} ({data['partnership_balls']})"
            st.markdown(f"""
                <div class="player-box">
                    <h3>🤝 Partnership</h3>
                    <h2>{partnership}</h2>
                </div>
            """, unsafe_allow_html=True)
    
    # Run Rate Indicator for second innings
    if data["innings"] == 2 and data["target"] > 0:
        progress = min(100, (data["score"] / data["target"]) * 100)
        st.markdown(f"""
            <div class="run-rate-indicator">
                <div class="run-rate-fill" style="width: {progress}%;"></div>
            </div>
            <p style='text-align: center;'>Progress towards target: {progress:.1f}%</p>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed Stats Tabs
    tab_match, tab_bat, tab_bowl, tab_squad, tab_commentary = st.tabs(["📊 Match Stats", "🏏 Batting", "🎯 Bowling", "👥 Squad", "📝 Commentary"])
    
    with tab_match:
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.subheader("📋 Match Information")
            info_data = {
                "Teams": f"{data['team_a']} vs {data['team_b']}",
                "Batting Team": f"{batting_team}",
                "Overs Left": f"{data['max_overs'] - data['overs']:.1f}",
                "Wickets in Hand": f"{10 - data['wickets']}",
                "Current Run Rate": f"{data['run_rate']:.2f}",
                "Extra Runs": f"{data['extras']}"
            }
            if data["innings"] == 2:
                info_data["Target Score"] = f"{data['target']}"
                info_data["Required Run Rate"] = f"{required_run_rate:.2f}"
            
            df_info = pd.DataFrame(info_data.items(), columns=["Match Details", "Value"])
            st.table(df_info)
        
        with col_info2:
            st.subheader("Recent Events")
            if st.session_state["match_events"]:
                for event in st.session_state["match_events"][-5:]:
                    st.info(f"{event['time']} - {event['description']}")
            else:
                st.info("No recent events")
    
    with tab_bat:
        st.subheader(f"🏏 {batting_team} - Batting Scorecard")
        
        batting_data = []
        for player, stats in data["batting_stats"].items():
            strike_rate = (stats["r"] / stats["b"] * 100) if stats["b"] > 0 else 0
            batting_data.append({
                "Batsman": player,
                "R": stats["r"],
                "B": stats["b"],
                "4s": stats.get("4s", 0),
                "6s": stats.get("6s", 0),
                "SR": round(strike_rate, 2)
            })
if batting_data:
            df_bat = pd.DataFrame(batting_data)
            st.dataframe(df_bat, use_container_width=True)
        else:
            st.info("No batting data available")
    
    with tab_bowl:
        st.subheader(f"🎯 {bowling_team} - Bowling Scorecard")
        
        bowling_data = []
        for player, stats in data["bowling_stats"].items():
            overs = stats["balls"] // 6 + (stats["balls"] % 6) / 10
            economy = stats["r"] / overs if overs > 0 else 0
            bowling_data.append({
                "Bowler": player,
                "O": round(overs, 1),
                "M": stats.get("maidens", 0),
                "R": stats["r"],
                "W": stats["w"],
                "Econ": round(economy, 2)
            })
        
        if bowling_data:
            bowl_df = pd.DataFrame(bowling_data)
            st.dataframe(bowl_df, use_container_width=True)
        else:
            st.info("No bowling data available")
    
    with tab_squad:
        col_sq1, col_sq2 = st.columns(2)
        
        with col_sq1:
            st.subheader(f"{batting_team} Squad")
            batting_squad = data["team_a_squad"] if data["innings"] == 1 else data["team_b_squad"]
            for player in batting_squad:
                if player in data["out_players"]:
                    st.markdown(f"~~{player}~~ ❌")
                elif player in [data["current_striker"], data["current_non_striker"]]:
                    st.markdown(f"**{player}** 🏏 (Batting)")
                else:
                    st.write(f"• {player}")
        
        with col_sq2:
            st.subheader(f"{bowling_team} Squad")
            bowling_squad = data["team_b_squad"] if data["innings"] == 1 else data["team_a_squad"]
            for player in bowling_squad:
                if player == data["current_bowler"]:
                    st.markdown(f"**{player}** 🎯 (Bowling)")
                else:
                    st.write(f"• {player}")
    
    with tab_commentary:
        st.subheader("📝 Live Commentary")
        if st.session_state["match_events"]:
            for event in reversed(st.session_state["match_events"][-20:]):
                if event["type"] == "WICKET":
                    st.error(f"{event['time']} - {event['description']}")
                elif event["type"] in ["FOUR", "SIX"]:
                    st.success(f"{event['time']} - {event['description']}")
                else:
                    st.info(f"{event['time']} - {event['description']}")
        else:
            st.info("No commentary available")

elif page == "📊 Statistics":
    st.markdown("<div class='main-header'><h1>📊 Match Statistics</h1></div>", unsafe_allow_html=True)
    
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.subheader("🏆 Highest Run Scorers")
        if data["batting_stats"]:
            top_batsmen = sorted(data["batting_stats"].items(), key=lambda x: x[1]["r"], reverse=True)[:5]
            for player, stats in top_batsmen:
                strike_rate = (stats['r'] / stats['b'] * 100) if stats['b'] > 0 else 0
                st.metric(
                    player, 
                    f"{stats['r']} runs", 
                    f"{stats['b']} balls, SR: {strike_rate:.1f}"
                )
        else:
            st.info("No batting data")
    
    with col_stat2:
        st.subheader("🎯 Best Bowlers")
        if data["bowling_stats"]:
            top_bowlers = sorted(data["bowling_stats"].items(), key=lambda x: x[1]["w"], reverse=True)[:5]
            for player, stats in top_bowlers:
                overs = stats['balls'] // 6 + (stats['balls'] % 6) / 10
                economy = stats['r'] / overs if overs > 0 else 0
                st.metric(
                    player, 
                    f"{stats['w']} wickets", 
                    f"{stats['r']} runs, Econ: {economy:.1f}"
                )
        else:
            st.info("No bowling data")
    
    # Match Summary
    st.subheader("📊 Innings Summary")
    summary_data = {
        "Runs Scored": f"{data['score']}",
        "Wickets Lost": f"{data['wickets']}",
        "Overs Completed": f"{data['overs']:.1f}",
        "Current Run Rate": f"{data['run_rate']:.2f}",
        "Extras (Wd/Nb/Bye/Leg Bye)": f"{data['extras']}",
        "Current Partnership": f"{data['partnership_runs']} runs ({data['partnership_balls']} balls)"
    }
    
    df_summary = pd.DataFrame(summary_data.items(), columns=["Innings Stats", "Value"])
    st.table(df_summary)
    
    # Ball-by-ball analysis
    if st.session_state["ball_by_ball"]:
        st.subheader("🎯 Ball by Ball Analysis")
        ball_df = pd.DataFrame(st.session_state["ball_by_ball"])
        st.dataframe(ball_df, use_container_width=True)

elif page == "📜 History":
    st.markdown("<div class='main-header'><h1>📜 Match History</h1></div>", unsafe_allow_html=True)
    
    match_history = CricketDataManager.load_history()
    
    if match_history:
        for match in reversed(match_history[-10:]):  # Show last 10 matches
            with st.expander(f"🏏 Match {match['match_id']}: {match['teams']} - {match['date']}"):
                col_hist1, col_hist2 = st.columns(2)
                
                with col_hist1:
                    st.success(f"**Winner:** {match['winner']}")
                    st.info(f"**Final Score:** {match['score']}")
                    st.info(f"**Man of the Match:** {match.get('man_of_match', 'TBD')}")
                
                with col_hist2:
                    st.write("**Top Performers**")
                    if match.get('batting_stats'):
                        if match['batting_stats']:
                            top_bat = max(match['batting_stats'], key=lambda x: x['runs'])
                            st.write(f"🏏 Best Bat: {top_bat['player']} - {top_bat['runs']}({top_bat['balls']}) SR: {top_bat['strike_rate']}")
                    
                    if match.get('bowling_stats'):
                        if match['bowling_stats']:
                            top_bowl = max(match['bowling_stats'], key=lambda x: x['wickets'])
                            st.write(f"🎯 Best Bowl: {top_bowl['player']} - {top_bowl['wickets']}/{top_bowl['runs']} Econ: {top_bowl['economy']}")
                
                # Detailed stats in tabs
                tab_hist_bat, tab_hist_bowl = st.tabs(["Batting Details", "Bowling Details"])
                
                with tab_hist_bat:
                    if match.get('batting_stats'):
                        df_hist_bat = pd.DataFrame(match['batting_stats'])
                        st.dataframe(df_hist_bat, use_container_width=True)
                    else:
                        st.info("No batting stats available")
                
                with tab_hist_bowl:
                    if match.get('bowling_stats'):
                        df_hist_bowl = pd.DataFrame(match['bowling_stats'])
                        st.dataframe(df_hist_bowl, use_container_width=True)
                    else:
                        st.info("No bowling stats available")
    else:
        st.info("No match history available yet. Complete a match to see history!")

# Auto-refresh for live match page
if page == "📺 Live Match" and not data["is_finished"]:
    if time.time() - st.session_state["last_update"] > 5:  # Refresh every 5 seconds
        st.session_state["last_update"] = time.time()
        time.sleep(0.1)  # Small delay to prevent multiple refreshes
        st.rerun()