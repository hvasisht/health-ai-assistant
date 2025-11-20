# Personal Health AI Assistant

## 🎯 Project Overview

A conversational AI health assistant that helps users track glucose levels, meals, and exercise through natural language interactions. Built using multi-agent architecture with LangChain and Streamlit.

## 🏗️ System Architecture

### Multi-Agent Design

The system uses 4 specialized AI agents:

1. **Router Agent** - Analyzes user messages and routes to appropriate specialist
2. **Diabetes Agent** - Manages glucose tracking and provides diabetes insights
3. **Fitness Agent** - Handles exercise logging and fitness coaching
4. **Nutrition Agent** - Tracks meals and provides dietary guidance

### Technology Stack

**Backend:**
- Python 3.13
- LangChain & LangGraph (AI agent orchestration)
- OpenAI GPT-3.5-turbo (Language model)
- SQLite (Data storage)

**Frontend:**
- Streamlit (Web interface)
- Plotly (Interactive visualizations)

**Key Libraries:**
- `langchain-openai`: LLM integration
- `pandas`: Data processing
- `plotly`: Chart generation

## 🗄️ Database Schema

### Tables

**users** - User accounts
- id, name, created_at, is_demo

**glucose_readings** - Blood glucose measurements
- id, user_id, timestamp, glucose_level, notes

**meals** - Food tracking
- id, user_id, timestamp, meal_name, meal_type, calories, carbs, protein, fats

**exercise** - Activity tracking
- id, user_id, timestamp, activity_type, duration, calories_burned, intensity

## 🤖 Agent Workflows

### Example: Multi-Intent Message

User: "I ate pasta, my blood sugar is 160"

1. **Smart Parser** extracts:
   - Meal: "pasta"
   - Glucose: 160 mg/dL

2. **Nutrition Agent** logs meal and estimates nutrition

3. **Diabetes Agent** logs glucose and provides feedback

4. **Response**: Combined insights from both agents

## 📊 Key Features

- **Natural Language Processing** - Understands conversational input
- **Multi-Intent Handling** - Processes multiple data types in one message
- **Real-time Visualizations** - Interactive glucose and activity charts
- **Personalized Insights** - AI-generated health recommendations
- **Data Persistence** - SQLite database maintains user history
- **ADA Guidelines** - Follows American Diabetes Association standards

## 🎓 Learning Outcomes

This project demonstrates:
- Multi-agent AI architecture
- LangChain framework usage
- Natural language understanding
- Data visualization
- Full-stack development
- Healthcare data management