# Project Architecture: Smart Menu Concierge (RAG-Enabled)

## 1. Project Overview
**Goal:** Build a restaurant menu application with an integrated AI Concierge.
**Key Features:**
- Admin dashboard to manage menu items (CRUD).
- Customer view to browse the menu.
- RAG-powered Chat Widget allowing customers to query the menu (e.g., "What is spicy?", "Do you have vegan options?") using a local LLM.
- Real-time streaming responses via WebSockets.

---

## 2. Technology Stack

### **Frontend**
- **Framework:** Angular v21 (Standalone Components, Signals).
- **Styling:** SCSS + TailwindCSS (Utility-first), Dark Mode.
- **Architecture:** Single Page Application (SPA).
- **Communication:** HTTP Client (REST), RxJS/WebSocketSubject (Real-time Chat).

### **Backend**
- **Runtime:** Python 3.11-slim (Dockerized).
- **Framework:** FastAPI (Async).
- **AI Integration:** OpenAI Client (pointing to LM Studio).
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (Local Python execution) or LM Studio Embedding Endpoint.

### **Database**
- **Primary DB:** PostgreSQL 16+.
- **Extension:** `pgvector` (For storing and querying vector embeddings).

### **Infrastructure**
- **Orchestration:** Docker Compose.
- **LLM Host:** LM Studio (Running locally on host machine or separate container, exposed via generic OpenAI API format).

---

## 3. Database Schema (PostgreSQL + pgvector)

We require two primary tables. One for raw data and one specifically for RAG search efficiency (or combined if preferred, but separated here for clarity).

### Table: `menu_items`
*Standard relational data for the UI.*

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `gen_random_uuid()` | Unique identifier |
| `name` | `VARCHAR(255)` | NOT NULL | Name of the dish |
| `description` | `TEXT` | NOT NULL | Detailed text (ingredients, taste) |
| `price` | `DECIMAL(10,2)` | NOT NULL | Price of the item |
| `image_data` | `TEXT` | NULL | Base64 encoded string or file relative path |
| `category` | `VARCHAR(50)` | NULL | e.g., "Starter", "Main" |
| `created_at` | `TIMESTAMP` | Default NOW() | Audit trail |

### Table: `menu_embeddings`
*Vector data for the AI brain.*

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `item_id` | `UUID` | FK -> `menu_items.id` | Link to the actual item |
| `embedding` | `VECTOR(384)` | NOT NULL | Vector representation (Dimension depends on model, e.g., 384 for MiniLM) |
| `content_chunk` | `TEXT` | NOT NULL | Text representation used to generate embedding (e.g., "Name: Pad Thai. Desc: Spicy noodles...") |

---

## 4. Backend Architecture (FastAPI)

### **Core Modules**
1.  **`main.py`**: App entry point, CORS configuration, WebSocket route mounting.
2.  **`database.py`**: Async SQLAlchemy setup with PostgreSQL connection string.
3.  **`models.py`**: SQLAlchemy ORM definitions (`MenuItem`, `MenuEmbedding`).
4.  **`schemas.py`**: Pydantic models for request/response validation.
    * `MenuItemCreate`, `MenuItemResponse`, `ChatRequest`, `ChatResponse`.
5.  **`routers/`**:
    * `menu.py`: REST endpoints (GET /menu, POST /menu, DELETE /menu/{id}, PUT /menu/{id}).
        * *Trigger:* On POST/PUT, the backend must also generate a new embedding and upsert into `menu_embeddings`.
    * `chat.py`: WebSocket endpoint (`/ws/chat`).

### **RAG Pipeline (The "Brain" Logic)**
Located in `services/rag_service.py`.

**Flow for Chat:**
1.  **Receive:** User question from WebSocket (e.g., "Do you have non-spicy food?").
2.  **Embed:** Convert question to vector using `sentence-transformers` (local) or LM Studio Embedding API.
3.  **Search (Retrieval):** Perform Cosine Similarity search on `menu_embeddings` table via `pgvector` SQL query.
    * *Query:* `SELECT content_chunk FROM menu_embeddings ORDER BY embedding <=> query_vector LIMIT 3;`
4.  **Context Construction:** Combine retrieved chunks into a system prompt.
    * *Prompt:* "You are a waiter. Answer the user question using ONLY this context: [Chunk 1, Chunk 2, Chunk 3]."
5.  **Generate:** Send Prompt + User Question to LM Studio (via `openai.AsyncOpenAI` client).
6.  **Stream:** Iterate over the AsyncGenerator from LM Studio and push chunks to WebSocket.

---

## 5. Frontend Architecture (Angular v21)

### **Key Standalone Components**

#### 1. `AdminMenuComponent` (`/admin`)
* **Responsibility:** Menu Management.
* **Features:**
    * Reactive Form for inputs (Name, Desc, Price).
    * File Input handler: Converts uploaded image to Base64 string before sending to API.
    * Data Table: Lists current items with Delete/Edit actions.
* **State:** Uses `Signals` to hold the list of menu items.

#### 2. `CustomerMenuComponent` (`/menu`)
* **Responsibility:** The public facing display.
* **Features:**
    * Grid layout displaying cards (Image + Name + Price).
    * "Ask AI" Floating Action Button (FAB) to toggle the Chat Widget.

#### 3. `ChatWidgetComponent` (Selector: `app-chat-widget`)
* **Responsibility:** The RAG interface.
* **Features:**
    * **UI:** Chat bubble interface (User message right, AI message left).
    * **Logic:**
        * On `ngOnInit`, establish `WebSocket` connection to FastAPI.
        * Input field sends string to Server.
        * Server response is streamed. The component must append incoming tokens to the *current* AI message bubble in real-time (not waiting for full response).
        * Auto-scroll to bottom on new token.

### **Services**
* **`MenuService`**: HTTP calls for CRUD.
* **`ChatService`**:
    * Manages the WebSocket instance.
    * Exposes a Signal or Observable for `messages$`.
    * Handles connection lifecycle (connect, disconnect, reconnect).

---

## 6. Docker & Infrastructure Setup

### `docker-compose.yml`

```yaml
services:
  # 1. Database
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: menudb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  # 2. Backend API
  backend:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db/menudb
      LM_STUDIO_URL: [http://host.docker.internal:1234/v1](http://host.docker.internal:1234/v1) # Access host machine LM Studio
    ports:
      - "8000:8000"
    depends_on:
      - db

  # 3. Frontend (Dev Mode)
  frontend:
    build: ./frontend
    command: ng serve --host 0.0.0.0 --poll 2000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "4200:4200"