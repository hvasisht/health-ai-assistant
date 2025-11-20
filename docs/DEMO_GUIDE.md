# Demo Guide - Personal Health AI Assistant

## 🎬 Presentation Flow (10 minutes)

### 1. Introduction (1 min)
"I built a conversational AI health assistant that helps people manage diabetes, fitness, and nutrition through natural chat interactions."

### 2. Show the Problem (1 min)
"Traditional health tracking apps require navigating multiple screens. My solution? Just talk naturally."

### 3. Live Demo (6 mins)

#### Demo User: Sarah
Login as "Sarah (Demo)" - she has 7 days of data

**Demo Script:**

**A. Show Existing Data**
Click: "📊 Show Glucose Chart"
- Point out: 7 days of data, color-coded zones, trends visible

Click: "💪 Weekly Activity" 
- Show: Different workouts each day, labels show activity types

**B. Natural Language Interaction**

Type: `What's my average glucose this week?`
- Shows: AI analyzes data and provides insights

Type: `I ate chicken salad for lunch`
- Shows: Logs meal with nutrition estimates

Type: `Log glucose: 145`
- Shows: Immediate feedback with ADA-compliant ranges

Type: `I ran for 25 minutes`
- Shows: Logs workout, calculates calories

**C. Multi-Intent Message** (KEY FEATURE)

Type: `I ate pizza, my blood sugar is 175`
- Shows: System handles BOTH meal and glucose in one message
- Provides: Combined insights from nutrition and diabetes agents

**D. Show Charts Again**
- New data now appears in charts
- Demonstrate real-time updates

### 4. Technical Overview (2 mins)

Show architecture:
- "4 specialized AI agents work together"
- "Router decides which agent handles each message"
- "LangChain orchestrates the agents"
- "SQLite stores all data persistently"

Show code (optional):
- `agents/router.py` - Routing logic
- `app.py` - Streamlit interface

## 🎯 Key Points to Emphasize

1. **Multi-Agent Architecture** - Each agent is an expert
2. **Natural Language** - No forms, just conversation
3. **Smart Parsing** - Extracts multiple data types from one message
4. **Real-time Feedback** - Instant health insights
5. **Data Visualization** - Clear, interactive charts
6. **Medical Standards** - Follows ADA glucose guidelines

## 💡 Questions You Might Get

**Q: How accurate is the glucose feedback?**
A: Uses ADA guidelines (80-130 before meals, <180 after meals)

**Q: Can it handle complex queries?**
A: Yes, the router agent directs to specialists, and they coordinate responses

**Q: How do you prevent hallucinations?**
A: Agents use structured prompts with context from database, not free generation

**Q: What's the LLM cost?**
A: ~$0.002 per interaction with GPT-3.5-turbo

**Q: Could this scale?**
A: Yes - SQLite for demo, would use PostgreSQL for production

## 🚀 Backup Demos (if something breaks)

If live demo fails:
1. Show pre-recorded screenshots
2. Walk through code instead
3. Discuss architecture diagram