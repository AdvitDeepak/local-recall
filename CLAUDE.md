Your job is to help me implement this entire project. I will include the project proposal and technical spec below. Your job is to implement an alpha version of this with everything functioning basically, but it does not have to be production-level yet. Use ollama for local LLMs.


CS146S Final Project Proposal
Advit Deepak, Sriram Varun Vobilisetty
Autumn 2025

tl;dr: lightweight, local tool that captures/unifies a user’s digital text data for downstream tasks



Problem Statement
Personal data is scattered across websites, applications, messages, and local files, with no easy way to continuously capture and consolidate this information for a given user.

A lightweight background tool that automatically collects this data without disrupting workflows could enable many downstream tasks (ex. semantic analysis, personalization of LLMs, etc.) by integrating this text data while remaining private and user-controlled.

This affects any user of a digital device, especially those that write a lot of text data. However, this could easily be extended to include other forms of data (ex. preferences).

Target User
Individuals who want to capture and analyze their personal data to derive insights or enable personalization (ex. now, can fine-tune an assistant LLM on user’s actual writing)



Initial Business/Use Case Context
Designed for daily usage (running in background silently, with dashboard)

Value Prop: can extract actionable insights (ex. mapping your real network of interactions), can semantic search across fragmented information sources (a unified local data store for RAG), can fine-tune LLMs to understand a user’s style and context

Planned Features
Frontend:
Interface to define keybinds and background tool controls (start/pause/stop)
Dashboard to view and manage stored data (with stats on capture activity)
Downstream App V0: semantic search across all consolidated data w/ RAG

Backend:
Lightweight background app that triggers on user-defined events (ex. keypress)
Persistent, local database that will store user’s captured text data
Downstream App V0: ollama based RAG-system using database

Methods for Capture:
Keyboard bind to copy whatever text is selected by the user’s cursor
Keyboard binds to start/stop “recording” text that is on user’s screen
Upload feature for local files (.txt, .pdf, .docx)
Integration feature for external data (ex. port from GDrive, Outlook)

Application’s Core Values:
Local storage of data (should not leave the device for more user-control)
Clear opt-in/opt-out control with user-defined inclusion/exclusion of data

LLM Tool Usage Plan
Addressing each of the components in the guideline:
Code Generation: will use Cursor and GitHub Copilot for development
Automated Testing: will use agents to simulate laptop usage to run live tests
Code Review/QA: will generate unit tests per component for coverage
UI/UX Design: will use Figma Make (Figma’s Copilot) for wireframing
CI/CD & Deployment Automation: will use GitLab Duo for DevSecOps

Three Specific Tools:
Cursor: coding generation and assistance (primary developer)
Figma Make: UI/UX prototyping and design (all HTML/CSS/JS)
GitLab Duo: CI/CD automation and security integration (if any)



CS146S Technical Spec & LLM Integration
Advit Deepak, Sriram Varun Vobilisetty

Architecture 


Data flows from the user's machine (ex. from applications in-use) to the local database, triggered by specific keybinds or events. This process is controlled by a dashboard, which also visualizes collected data and uses it for semantic search and RAG-based generation.


The text/vector database (blue) and the dashboard both interface with LLMs during the downstream RAG task. The user can semantic search or perform RAG using stored data.

API Design 


Endpoint
Purpose
Expected Input
Expected Output
Endpoints for Defining/Updating Keybinds
POST /keybind/selected
Manually define a keybind upon which the selected text will be captured and written to the database
“key sequence” : SEQ_KEY_PRESS
“status”: STATUS
POST /keybind/screenshot
Manually define a keybind upon which all text on the screen will be captured and written to the database
“key sequence” : SEQ_KEY_PRESS


“status”: STATUS
Endpoints for Fetching/Updating Stored Data
POST /data
Write text to the database (triggered upon specific keybind presses)
“text”: STRING, 
“time”: DATETIME
“status”: STATUS
GET /data
Retrieve all stored entries with optional filters 
“id”: DATA_ID or “tag”: STRING or “time”: DATETIME
“id”: DATA_ID, 
“source”: APP_NAME, 
“time”: DATETIME, 
“content”: TEXT
DELETE /data/{id}
Delete a specific entry
“id”: DATA_ID
“status”: STATUS
Endpoints for Downstream Task of RAG
POST /query
Perform semantic search (and optionally RAG) over the local database
“query”: STR, “model”: LLM (optional, for RAG)
“results”: LIST(“id”: ID, “text”: STR, “score”: FLOAT)
Endpoints for Overall System/Background Collection Control 
POST /control/stop
Stop the background data capture service
-
“status”: STATUS
POST /control/start
Start the background data capture service
-
“status”: STATUS


The POST /query APIs interacts with LLMs using the local database. It first utilizes an embedding-based model to retrieve entries that are most relevant to the search query. Then, based on whether “model” is passed in, it uses those relevant entries from the database and passes those as context to the LLM along with the query for a richer answer.

Technical Stack 

Languages: Python3 for backend, data processing, and lightweight UI
Frameworks:
Streamlit (Frontend) -  for a simple, local web dashboard
Ex. UI for search, summaries, and privacy/control settings
FastAPI (Backend)
Libraries:
SQLite (local encrypted database for text, metadata, and embeddings)
asyncio/threading (concurrency for API calls, multithreading for capture)
tesseract (for user’s screen capture)
pyinput (defining and capturing keybinds)
ollama (for local RAG and LLM usage)
FAISS (local vector index for semantic retrieval)
LangGraph (orchestration layer for RAG, embedding, and LLM calls)
PyMuPDF & python-docx (document parsing (PDF, DOCX, TXT))
Pytest (for unit and integration tests)


Business Context Summary 
Knowledge workers constantly encounter valuable information across documents, emails, and screens but lack an easy, private way to capture and retrieve it. Existing tools rely on cloud storage and manual entry, creating friction and privacy risks.
This system offers a local, intelligent text-capture and retrieval assistant that automatically gathers text snippets and documents, stores them securely on-device, and enables semantic search and reasoning using a local LLM.
Target users: Knowledge workers, students, and privacy-conscious professionals handling sensitive data.
Success Metrics
≥95% successful capture rate across all input modes
≤10s indexing time and ≤5s average query latency
≥4.0/5 average relevance rating on retrieved results
30% faster task completion vs. manual context addition
Zero outbound data transmission in local mode
≥70% pilot users report continued-use intent

Specific Prompts/Instructions for LLM tools 

System Prompt
“You are a factual, privacy-preserving assistant operating entirely on local data. Answer the user’s question using only the provided text snippets. Do not invent details or access external sources. If the context is insufficient, respond with: ‘I don’t have enough local context to answer this.’ Keep responses under 150 words and cite snippet IDs in brackets.”
Debugging (Sample)
“My FastAPI POST /search route intermittently returns empty responses, even though embeddings are stored in FAISS. Here’s the handler code and index setup. Identify potential issues in how I serialize vectors or query FAISS (e.g., dimensionality mismatch, async timing, or DB cursor errors) and propose fixes”
Design Exploration (Sample)
“Design a modular architecture for a privacy-preserving text capture system that runs fully on-device. It should support: (a) real-time capture listeners for text or screenshots, (b) a background task queue for embedding computation, (c) an encrypted SQLite + FAISS datastore, and (d) a local LLM accessed via Ollama. Include clear module boundaries, communication flow, and scalability considerations.”
Code Generation (sample)
“Generate a Python EmbeddingPipeline class that consumes raw text records from SQLite, generates embeddings in batches using a local Ollama model, and updates a FAISS index. The class should handle backpressure with asyncio, log progress, and retry failed embedding calls gracefully.”




