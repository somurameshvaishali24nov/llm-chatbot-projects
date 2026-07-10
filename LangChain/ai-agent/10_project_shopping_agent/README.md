# 🛒 AI Shopping Assistant

A Streamlit shopping agent built with LangChain + LangGraph and Groq LLMs. It searches a local product catalog, pulls customer ratings, places orders, and can find products from an uploaded photo.

## Demo

<video src="resources/demo.mp4" controls width="700"></video>

If your Markdown viewer doesn't render inline video (e.g. GitHub.com without the asset-upload flow), [download/view the demo directly](resources/demo.mp4).

## How it works

The agent (`shopping_agent.py`) is a `langchain.agents.create_agent` ReAct-style agent with four tools:

| Tool | Purpose |
|---|---|
| `search_products` | Keyword search over `store.db` (name, description, category), with optional max price / organic filters |
| `get_rating` | Average rating + review count for a product, from the `reviews` table |
| `checkout` | Inserts an order into the `orders` table and returns a confirmation |
| `describe_product_image` | Sends an uploaded image to a vision model (`meta-llama/llama-4-scout-17b-16e-instruct`) to identify the product and generate a search query |

The main chat LLM is `qwen/qwen3-32b` via `langchain-groq`. The system prompt enforces a strict flow: search → rate → present a numbered list → only checkout after explicit user confirmation.

`app.py` is the Streamlit UI: a chat interface plus a sidebar for "shop by image" uploads.

Data lives in `store.db` (SQLite), with `products`, `reviews`, and `orders` tables. Sample product images for testing image search are in `resources/` (`honey.png`, `oats.png`, `elephant.png` as a negative example).

## Prerequisites

- A `GROQ_API_KEY`, set in a `.env` file at the repository root (`Tutorial/.env`):

  ```bash
  GROQ_API_KEY=your_groq_api_key_here
  ```

## Running the app

### Option A — Devcontainer / Docker Compose

The repo root has a `docker-compose.yml` and `.devcontainer/devcontainer.json` that build a Linux container with all dependencies installed via `uv`.

1. **Start the container:**

   ```bash
   cd ~/Tutorial
   docker compose up
   ```

   Or open the folder in VS Code / Cursor and choose **"Reopen in Container"** to load the devcontainer — this runs `docker compose up` for you and syncs dependencies with `uv sync --group dev`.

2. **Run the app inside the container.** The compose file only exposes port 8888 (Jupyter) by default, so run Streamlit from a shell inside the container and forward its port:

   ```bash
   docker compose exec rag streamlit run LangChain/ai-agent/10_project_shopping_agent/app.py \
     --server.address 0.0.0.0 --server.port 8501
   ```

   If you're using the VS Code devcontainer, just open an integrated terminal (already inside the container) and run:

   ```bash
   streamlit run LangChain/ai-agent/10_project_shopping_agent/app.py
   ```

   VS Code will auto-forward port 8501. Otherwise, add `- "8501:8501"` under the `rag` service's `ports` in `docker-compose.yml` to expose it manually.

3. Open **http://localhost:8501**.

### Option B — Local Python environment

```bash
cd ~/Tutorial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run LangChain/ai-agent/10_project_shopping_agent/app.py
```

Open **http://localhost:8501**.

### Quick terminal test (no UI)

```bash
python LangChain/ai-agent/10_project_shopping_agent/shopping_agent.py
```

Runs a single hardcoded query ("organic honey, 4.5+ rating, under $20") and prints the agent's response.

## Example prompts

- "I want organic honey under $15 with 4+ rating"
- "Show me steel-cut oats"
- Upload a product photo in the sidebar and click **Find similar products**

## Notes

- If the app errors on startup, confirm `.env` (repo root) has a valid `GROQ_API_KEY`.
- Orders are persisted to `store.db`, so `checkout` results carry over between runs.
