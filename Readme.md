# Voice Assistant

A real-time AI voice assistant built with LiveKit, Groq, and Deepgram.

## Features
- Real-time voice conversation
- Weather information via OpenWeatherMap
- Islamic prayer times via Aladhan API
- Notes saving via MCP (Model Context Protocol)
- Course knowledge base via RAG (LangChain + ChromaDB)

## Tech Stack
- **LiveKit** — Real-time voice transport
- **Groq + Llama 3.3** — LLM
- **Deepgram** — Text to Speech
- **Silero** — Voice Activity Detection
- **LangChain + ChromaDB** — RAG Knowledge Base
- **MCP** — Notes integration

## Setup

1. Clone the repository
2. Create virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Create `.env` file with your keys:
```LIVEKIT_URL=your_livekit_url

    LIVEKIT_API_KEY=your_key

    LIVEKIT_API_SECRET=your_secret

    GROQ_API_KEY=your_key

    DEEPGRAM_API_KEY=your_key

    WEATHER_API_KEY=your_key
``` 

5. Add your PPTX slides to `slides/` folder
6. Run ingestion:
```bash
   python ingest.py
```
7. Start the agent:
```bash
   python agent.py dev
```
8. Start the server:
```bash
   python server.py
```
9. Open `http://127.0.0.1:5000`

## Project Structure
   
```
    voice-assistant/

    ├── agent.py              # Main voice agent

    ├── server.py             # Flask token server

    ├── index.html            # Frontend UI

    ├── notes_mcp_server.py   # MCP notes server

    ├── knowledge_tool.py     # RAG search tool

    ├── ingest.py             # Knowledge base builder

    ├── slides/               # Your course slides

    └── .env                  # API keys (not uploaded)
 ```
