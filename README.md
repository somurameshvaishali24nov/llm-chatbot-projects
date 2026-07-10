# Running the RAG tutorial in Docker (Intel Mac fix)

Your Intel Mac can't install modern `torch` / `onnxruntime` because those
projects stopped shipping Intel-Mac wheels. This setup runs the tutorial in a
Linux x86_64 container — which is **native** on an Intel Mac, so it's fast —
where every wheel in `requirements.txt` installs cleanly, unmodified.

## One-time setup

1. Install **Docker Desktop**: https://www.docker.com/products/docker-desktop/
   Open it and wait until it says "Docker Desktop is running".

2. Put these four files in your project folder, next to `requirements.txt`:
   `~/Desktop/Simplilearn/RAG/Tutorial/`
   - `Dockerfile`
   - `docker-compose.yml`
   - `.dockerignore`
   - `.env.example`

3. If your tutorial needs API keys, create your `.env`:
   ```bash
   cd ~/Desktop/Simplilearn/RAG/Tutorial
   cp .env.example .env
   # then edit .env and paste in your keys
   ```

## Build and run

From the project folder:

```bash
cd ~/Desktop/Simplilearn/RAG/Tutorial

# Build the image (first time is slow — torch is a big download)
docker compose build

# Start Jupyter Lab
docker compose up
```

Then open the URL it prints, or just go to:

**http://localhost:8888**

Your notebooks and files are bind-mounted, so anything you edit or save in
Jupyter is written straight back to your Mac's folder. Stop with `Ctrl+C`, or
run `docker compose down` in another terminal.

## Everyday commands

| What | Command |
|------|---------|
| Start | `docker compose up` |
| Start in background | `docker compose up -d` |
| Stop | `docker compose down` |
| Rebuild after editing requirements.txt | `docker compose build` |
| Open a shell inside the container | `docker compose run --rm rag bash` |
| Run a script instead of Jupyter | `docker compose run --rm rag python your_script.py` |

## Notes

- **Don't** run `uv sync` / `uv add` on the Mac anymore — that's what hit the
  wheel error. Dependencies now live inside the container. Edit
  `requirements.txt` and re-run `docker compose build`.
- The container ignores your local `venv/` and `.venv/`, so they won't
  interfere.
- Jupyter runs without a token for local convenience. Don't expose port 8888
  to the internet.
- First build downloads torch (~hundreds of MB). Later builds are cached and
  fast unless `requirements.txt` changes.
