# 🏥 Personal Health AI Assistant

A sophisticated multi-agent AI system for personalized diabetes, fitness, and nutrition management with pattern analysis and RAG-powered medical knowledge.

## ✨ Key Features

- 🩸 **Diabetes Management** - Track glucose with ADA 2024-compliant feedback
- 💪 **Fitness Coaching** - Exercise tracking with safety protocols
- 🥗 **Nutrition Guidance** - Meal tracking with glycemic index data
- 🔍 **Pattern Analysis** - Discover user-specific health correlations
- 🧠 **Multi-Agent Coordination** - Complex queries analyzed by multiple specialists
- 📚 **RAG Medical Knowledge** - Evidence-based advice from ADA guidelines
- 📊 **Visual Insights** - Interactive charts showing health trends

## 🏗️ Architecture

### 6 Specialized AI Agents:

1. **Router** (GPT-4o-mini) - Intent classification
2. **Diabetes** (GPT-3.5-turbo + RAG) - Glucose management
3. **Fitness** (GPT-4o-mini + RAG) - Exercise coaching
4. **Nutrition** (GPT-3.5-turbo + RAG) - Dietary guidance
5. **Pattern Analysis** (GPT-4o-mini) - Correlation detection
6. **Insights Coordinator** (GPT-4o) - Multi-agent orchestration

### RAG Knowledge Bases:
- ADA 2024 Guidelines
- Glycemic Index Database
- Exercise Safety Protocols
- Medication Interactions

## 🛠️ Tech Stack

- **Python 3.13**
- **LangChain 1.0 / LangGraph** - Agent orchestration
- **Multiple OpenAI LLMs:**
  - GPT-4o (Coordinator)
  - GPT-4o-mini (Router, Fitness, Patterns)
  - GPT-3.5-turbo (Diabetes, Nutrition)
- **ChromaDB** - Vector database for RAG
- **Streamlit** - Web interface
- **Plotly** - Interactive visualizations
- **SQLite** - Data persistence
- **Pandas/NumPy** - Statistical analysis

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/health-ai-assistant.git
cd health-ai-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
echo 'OPENAI_API_KEY=your-key-here' > .env

# Initialize database
python database/db_manager.py

# Load medical knowledge into RAG
cd rag
python load_documents.py
cd ..

# Generate demo data (optional)
python data/generate_demo_data.py

# Run the app
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 💬 Usage Examples

**Simple logging:**
```
"Log glucose: 125"
"I ate oatmeal with berries"
"I ran for 30 minutes"
```

**Multi-intent:**
```
"I ate pasta, my blood sugar is 160"
→ Logs BOTH meal and glucose, provides coordinated feedback
```

**Pattern discovery:**
```
"What patterns do you see in my data?"
→ Pattern Agent analyzes correlations and provides insights
```

**Complex coordination:**
```
"Why is my glucose always high after dinner?"
→ Coordinator orchestrates Diabetes + Nutrition + Pattern agents
```

**RAG-powered queries:**
```
"What are the ADA target glucose ranges?"
→ Retrieves from ADA 2024 guidelines
"Can I exercise with glucose at 260?"
→ Retrieves safety protocols
```

## 📊 Demo User

Login as **Sarah (Demo)** to explore:
- 7 days of glucose, meal, and exercise data
- Pattern analysis showing correlations
- Interactive charts and visualizations

## 🎯 Why This Project is Different

| Single LLM | Our Multi-Agent System |
|------------|------------------------|
| Generic advice | User-specific patterns from their data |
| Outdated knowledge | ADA 2024 guidelines via RAG |
| "Try walking" | "Your data shows 20-min walks reduce glucose by 35mg/dL" |
| One-size-fits-all | Personalized based on YOUR correlations |
| No data analysis | Statistical pattern detection |

## 🎓 Academic Context

**Course**: Applied Generative AI  
**Institution**: Northeastern University  
**Program**: MS Data Analytics Engineering  
**Author**: Harini Vasisht  
**Date**: November 2025

**Addresses TA Feedback:**
- ✅ Complex problem requiring multi-agent solution
- ✅ Pattern analysis provides actionable insights from logged data
- ✅ RAG adds medical knowledge beyond LLM training
- ✅ Multi-agent coordination for comprehensive analysis

## 📂 Project Structure
```
health-ai-assistant/
├── agents/                 # All AI agents
│   ├── router.py
│   ├── diabetes.py
│   ├── fitness.py
│   ├── nutrition.py
│   ├── pattern_analysis.py
│   └── insights_coordinator.py
├── rag/                    # RAG system
│   ├── medical_knowledge.py
│   ├── load_documents.py
│   └── documents/          # Medical knowledge base
├── database/               # Data persistence
├── utils/                  # Helper functions
├── data/                   # Demo data generator
├── docs/                   # Documentation
└── app.py                  # Main Streamlit app
```

## 📝 License

MIT License

## 🔗 Links

- **GitHub**: [Your Repository URL]
- **Portfolio**: [Your Portfolio Site]
- **LinkedIn**: [Your LinkedIn]