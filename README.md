# 🏥 Personal Health AI Assistant

An intelligent conversational assistant for managing diabetes, fitness, and nutrition using multi-agent AI architecture.

## ✨ Features

- 🩸 **Glucose Tracking** - Monitor blood sugar with ADA-compliant feedback
- 💪 **Fitness Coaching** - Log workouts and track weekly activity
- 🥗 **Nutrition Guidance** - Track meals with automatic nutrition estimates
- 📊 **Visual Insights** - Interactive charts showing health trends
- 🤖 **Natural Language** - Just talk naturally, no forms needed
- 🧠 **Multi-Agent AI** - Specialized agents for each health domain

## 🏗️ Architecture

Built with a **multi-agent system** using LangChain:

- **Router Agent** - Routes messages to specialists
- **Diabetes Agent** - Glucose management & insights
- **Fitness Agent** - Exercise tracking & coaching
- **Nutrition Agent** - Meal tracking & dietary advice

## 🛠️ Tech Stack

- **Python 3.13**
- **LangChain / LangGraph** - AI agent orchestration
- **OpenAI GPT-3.5-turbo** - Language model
- **Streamlit** - Web interface
- **Plotly** - Interactive visualizations
- **SQLite** - Data persistence

## 🚀 Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd health-ai-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
echo 'OPENAI_API_KEY=your-key-here' > .env

# Initialize database
python database/db_manager.py

# Generate demo data (optional)
python data/generate_demo_data.py

# Run the app
streamlit run app.py
```

## 💬 Usage Examples
```
"Log glucose: 125"
"I ate oatmeal with berries"
"I ran for 30 minutes"
"Show me my glucose chart"
"I ate pasta, my blood sugar is 160"  ← Multi-intent!
```

## 📊 Demo Data

Login as **Sarah (Demo)** to see a week of sample health data.

## 🎓 Project Context

Built for **Applied Generative AI** course at Northeastern University.

**Author**: Harini Vasisht  
**Program**: MS Data Analytics Engineering  
**Date**: November 2025

## 📝 License

MIT License