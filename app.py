"""
Personal Health AI Assistant - Enhanced Version with Visualizations
A conversational health assistant that tracks glucose, meals, and exercise with visual insights.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.db_manager import (
    initialize_database, create_user, get_all_users,
    add_glucose_reading, get_glucose_readings, get_glucose_stats,
    add_meal, get_meals, add_exercise, get_exercises
)
from agents.router import RouterAgent
from agents.diabetes import DiabetesAgent
from agents.fitness import FitnessAgent
from agents.nutrition import NutritionAgent
from utils.helpers import parse_glucose_input, parse_meal_input, parse_exercise_input

# Page configuration
st.set_page_config(
    page_title="Health AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Chat styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid #e0e0e0;
    }
    
    /* Sidebar styling */
    .sidebar-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    /* Info boxes */
    .insight-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .danger-box {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def init_db():
    initialize_database()
    return True

@st.cache_resource
def init_agents():
    return {
        'router': RouterAgent(),
        'diabetes': DiabetesAgent(),
        'fitness': FitnessAgent(),
        'nutrition': NutritionAgent()
    }

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'show_chart' not in st.session_state:
        st.session_state.show_chart = False

def create_glucose_chart(user_id: int, days: int = 7):
    """Create a simple, clear daily average glucose chart."""
    readings = get_glucose_readings(user_id, limit=200)
    
    if not readings:
        return None
    
    df = pd.DataFrame(readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Get only last 7 days
    cutoff = datetime.now() - timedelta(days=days)
    df = df[df['timestamp'] >= cutoff]
    
    if df.empty:
        return None
    
    # Group by DATE only - one point per day (average)
    df['date'] = df['timestamp'].dt.date
    daily = df.groupby('date')['glucose_level'].agg(['mean', 'min', 'max']).reset_index()
    daily['date_str'] = pd.to_datetime(daily['date']).dt.strftime('%b %d')
    
    fig = go.Figure()
    
    # Add average line
    fig.add_trace(go.Scatter(
        x=daily['date_str'],
        y=daily['mean'],
        mode='lines+markers',
        name='Average',
        line=dict(color='#1976d2', width=4),
        marker=dict(size=12, color='#1976d2'),
        text=[f"{val:.0f} mg/dL" for val in daily['mean']],
        textposition='top center',
        hovertemplate='<b>%{y:.0f} mg/dL</b><extra></extra>'
    ))
    
    # Reference lines
    fig.add_hline(y=80, line_dash="dot", line_color="gray", line_width=1)
    fig.add_hline(y=130, line_dash="dot", line_color="gray", line_width=1)
    fig.add_hline(y=180, line_dash="dot", line_color="orange", line_width=2)
    
    # Add shaded zones
    fig.add_hrect(y0=80, y1=130, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=130, y1=180, fillcolor="lightgreen", opacity=0.1, line_width=0)
    fig.add_hrect(y0=180, y1=300, fillcolor="orange", opacity=0.1, line_width=0)
    
    fig.update_layout(
        title={
            'text': "📊 Daily Average Glucose - Last 7 Days",
            'font': {'size': 18}
        },
        xaxis_title="Date",
        yaxis_title="Glucose (mg/dL)",
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#eeeeee')
    fig.update_yaxes(showgrid=True, gridcolor='#eeeeee', range=[60, 220])
    
    return fig


def create_weekly_activity_chart(user_id: int):
    """Create a clear bar chart with activity labels."""
    exercises = get_exercises(user_id, limit=50)
    
    if not exercises:
        return None
    
    df = pd.DataFrame(exercises)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['day'] = df['timestamp'].dt.strftime('%b %d')
    
    # Get activity types for each day
    daily = df.groupby(['date', 'day']).agg({
        'duration': 'sum',
        'activity_type': lambda x: ', '.join(x.unique())
    }).reset_index()
    
    # Get last 7 days
    daily = daily.sort_values('date').tail(7)
    
    # Create text labels with activity type and duration
    daily['label'] = daily.apply(
        lambda row: f"{row['activity_type'].title()}<br>{int(row['duration'])} min", 
        axis=1
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily['day'],
        y=daily['duration'],
        marker_color='#667eea',
        text=daily['label'],
        textposition='outside',
        textfont=dict(size=12, color='#333'),
        hovertemplate='<b>%{x}</b><br>%{customdata}<br>%{y} minutes<extra></extra>',
        customdata=daily['activity_type']
    ))
    
    fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=2,
                  annotation_text="Daily Goal: 30 min", annotation_position="right")
    
    fig.update_layout(
        title={
            'text': "💪 Daily Activity - Last 7 Days",
            'font': {'size': 18, 'color': '#333'}
        },
        xaxis_title="Date",
        yaxis_title="Minutes",
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333', size=13)
    )
    
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='#333',
        tickfont=dict(size=12, color='#333')
    )
    
    fig.update_yaxes(
        showgrid=True, 
        gridcolor='#eeeeee',
        range=[0, max(daily['duration'])*1.4],
        showline=True,
        linewidth=2,
        linecolor='#333',
        tickfont=dict(size=12, color='#333')
    )
    
    return fig

def create_nutrition_pie_chart(user_id: int):
    """Create nutrition breakdown pie chart."""
    meals = get_meals(user_id, limit=20)
    
    if not meals:
        return None
    
    total_carbs = sum(m.get('carbs', 0) for m in meals if m.get('carbs'))
    total_protein = sum(m.get('protein', 0) for m in meals if m.get('protein'))
    total_fats = sum(m.get('fats', 0) for m in meals if m.get('fats'))
    
    if total_carbs + total_protein + total_fats == 0:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=['Carbs', 'Protein', 'Fats'],
        values=[total_carbs, total_protein, total_fats],
        marker=dict(colors=['#ffd54f', '#66bb6a', '#ef5350']),
        hole=0.4
    )])
    
    fig.update_layout(
        title="Nutrition Balance (Recent Meals)",
        height=300,
        showlegend=True
    )
    
    return fig

def smart_response(user_message: str, agents: dict, user_id: int):
    """Enhanced response with smart parsing and multi-agent coordination."""
    
    # Parse all possible data types from message
    glucose = parse_glucose_input(user_message)
    meal = parse_meal_input(user_message)
    exercise = parse_exercise_input(user_message)
    
    responses = []
    charts = []
    
    # Handle multi-intent messages (e.g., "I ate pasta, my blood sugar is 160")
    if glucose:
        response = agents['diabetes'].process_message(user_id, f"Log glucose: {glucose}")
        responses.append(response)
        
        # Add contextual suggestions
        if glucose > 160:
            responses.append("\n💡 **Suggestion**: A 15-minute walk can help lower your levels. Would you like some lower-carb meal ideas?")
        
    if meal:
        response = agents['nutrition'].process_message(user_id, user_message)
        responses.append(response)
    
    if exercise:
        response = agents['fitness'].process_message(user_id, user_message)
        responses.append(response)
    
    # Check if asking for visualization
    message_lower = user_message.lower()
    if any(keyword in message_lower for keyword in ['show', 'chart', 'graph', 'visualize', 'see my']):
        if 'glucose' in message_lower or 'sugar' in message_lower or 'diabetes' in message_lower:
            chart = create_glucose_chart(user_id)
            if chart:
                charts.append(('glucose', chart))
                responses.append("\n📊 Here's your glucose chart:")
        
        if 'exercise' in message_lower or 'workout' in message_lower or 'activity' in message_lower:
            chart = create_weekly_activity_chart(user_id)
            if chart:
                charts.append(('activity', chart))
                responses.append("\n📊 Here's your activity summary:")
        
        if 'nutrition' in message_lower or 'food' in message_lower or 'meal' in message_lower:
            chart = create_nutrition_pie_chart(user_id)
            if chart:
                charts.append(('nutrition', chart))
                responses.append("\n📊 Here's your nutrition breakdown:")
    
    # If no specific data parsed, route normally
    if not (glucose or meal or exercise or charts):
        route = agents['router'].route(user_message)
        
        if route == "DIABETES_AGENT":
            response = agents['diabetes'].process_message(user_id, user_message)
            responses.append(response)
        elif route == "FITNESS_AGENT":
            response = agents['fitness'].process_message(user_id, user_message)
            responses.append(response)
        elif route == "NUTRITION_AGENT":
            response = agents['nutrition'].process_message(user_id, user_message)
            responses.append(response)
        else:
            responses.append("👋 Hi! I can help you track your glucose, meals, and exercise. Try saying:\n- 'Log glucose: 120'\n- 'I ate chicken salad'\n- 'Show me my glucose this week'")
    
    return "\n\n".join(responses), charts

def main():
    init_db()
    agents = init_agents()
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏥 Your Health AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Track glucose, meals & exercise • Get personalized insights</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 Your Profile")
        
        users = get_all_users()
        
        if st.session_state.user_id:
            # Show current user
            # Show current user
            st.success(f"✅ **Logged in as:** {st.session_state.user_name}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")

            # Data summary button
            if st.button("📋 My Data Summary", use_container_width=True):
                glucose_count = len(get_glucose_readings(st.session_state.user_id, limit=100))
                meal_count = len(get_meals(st.session_state.user_id, limit=100))
                exercise_count = len(get_exercises(st.session_state.user_id, limit=100))
                
                summary = f"📊 **Your Health Data**\n\n"
                summary += f"🩸 Glucose readings: {glucose_count}\n"
                summary += f"🥗 Meals logged: {meal_count}\n"
                summary += f"💪 Workouts logged: {exercise_count}\n\n"
                summary += "💡 Ask me to 'show my glucose chart' or 'what's my average?'"
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": summary,
                    "charts": []
                })
                st.rerun()
            
            if st.button("📊 Show Glucose Chart", use_container_width=True):
                # Add user message
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Show me my glucose this week",
                    "charts": []
                })
                
                # Generate the response and chart
                chart = create_glucose_chart(st.session_state.user_id)
                if chart:
                    response = "📊 Here's your glucose chart for the past week:"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "charts": [('glucose', chart)]
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No glucose readings found in the past week. Start logging with 'Log glucose: 120'",
                        "charts": []
                    })
                
                st.rerun()
            
            if st.button("💪 Weekly Activity", use_container_width=True):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Show me my weekly activity",
                    "charts": []
                })
                
                # Generate response
                summary = agents['fitness'].get_weekly_summary(st.session_state.user_id)
                chart = create_weekly_activity_chart(st.session_state.user_id)
                
                charts = [('activity', chart)] if chart else []
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": summary,
                    "charts": charts
                })
                st.rerun()
            
            if st.button("🥗 Nutrition Summary", use_container_width=True):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Show me my nutrition summary",
                    "charts": []
                })
                
                # Generate response
                summary = agents['nutrition'].get_daily_summary(st.session_state.user_id)
                chart = create_nutrition_pie_chart(st.session_state.user_id)
                
                charts = [('nutrition', chart)] if chart else []
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": summary,
                    "charts": charts
                })
                st.rerun()
        
        else:
            # User selection/creation
            if users:
                user_options = {f"{u['name']} (ID: {u['id']})": u['id'] for u in users}
                selected = st.selectbox("Select user:", list(user_options.keys()))
                
                if st.button("Login", use_container_width=True):
                    st.session_state.user_id = user_options[selected]
                    st.session_state.user_name = selected.split(" (ID:")[0]
                    
                    # Add welcome message with data summary
                    welcome_msg = f"👋 Welcome back, {st.session_state.user_name}!\n\n"
                    
                    # Check if user has data
                    glucose_count = len(get_glucose_readings(st.session_state.user_id, limit=100))
                    meal_count = len(get_meals(st.session_state.user_id, limit=100))
                    exercise_count = len(get_exercises(st.session_state.user_id, limit=100))
                    
                    if glucose_count > 0 or meal_count > 0 or exercise_count > 0:
                        welcome_msg += "📊 **Your data is here!**\n\n"
                        if glucose_count > 0:
                            welcome_msg += f"🩸 {glucose_count} glucose readings\n"
                        if meal_count > 0:
                            welcome_msg += f"🥗 {meal_count} meals logged\n"
                        if exercise_count > 0:
                            welcome_msg += f"💪 {exercise_count} workouts logged\n"
                        welcome_msg += "\n💡 Try: 'Show me my glucose chart' or 'What's my glucose average?'"
                    else:
                        welcome_msg += "Ready to start tracking your health! Try:\n• 'Log glucose: 120'\n• 'I ate oatmeal'\n• 'I ran for 30 minutes'"
                    
                    st.session_state.messages = [{"role": "assistant", "content": welcome_msg, "charts": []}]
                    st.rerun()
            
            st.markdown("**Or create new account:**")
            new_name = st.text_input("Your name:")
            if st.button("Create Account", use_container_width=True):
                if new_name:
                    user_id = create_user(new_name)
                    st.session_state.user_id = user_id
                    st.session_state.user_name = new_name
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🤖 AI Agents")
        st.markdown("🩸 Diabetes • 💪 Fitness • 🥗 Nutrition")
    
    # Main chat area
    if not st.session_state.user_id:
        st.info("👈 Please login or create an account to start!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🩸 Diabetes")
            st.write("Track blood glucose and get personalized insights")
        with col2:
            st.markdown("### 💪 Fitness")
            st.write("Log workouts and reach your activity goals")
        with col3:
            st.markdown("### 🥗 Nutrition")
            st.write("Track meals and balance your diet")
        
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show charts if present
            if "charts" in message and message["charts"]:
                for chart_type, chart in message["charts"]:
                    st.plotly_chart(chart, use_container_width=True)
    
    # Chat input
    if prompt := st.chat_input("💬 Type here... (e.g., 'I ate pasta, my blood sugar is 160')"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt, "charts": []})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, charts = smart_response(prompt, agents, st.session_state.user_id)
            
            st.markdown(response)
            
            # Show charts
            for chart_type, chart in charts:
                st.plotly_chart(chart, use_container_width=True)
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "charts": charts
        })

if __name__ == "__main__":
    main()