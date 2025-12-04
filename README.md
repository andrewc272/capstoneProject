# Capstone Project
## Contents

- [Introduction](#introduction)
- [Research](#research)
- [Requirements](#requirements)
- [Scope](#scope)
- [MVP](#mvp)
- [Application Architecture](#application-architecture)
- [Timeline](#timeline)
- [Resources](#resources)
- [How to use](#how-to-use)

## Introduction

The basic end goal of this project is to create a n-player game where human players conversate with m bots, where n is the number human players and m is the number of bots. 

## Research

### What is the turing test?

[The turing test](https://plato.stanford.edu/entries/turing-test/) is a test purposed by Allen Turing in 1949. It is a test of computers against the intellect of humans. It is performed with two humans, the *human* and the *interrogator*, and one computer whose goal is to impersonate a human. The interrogator will ask questions to the human and computer for 5 minutes. Turing thought that digital computers would, with enough computational power, be able to fool the interrogator 70% of the time. This happens to be a very difficult task something that LLM have only recently been able to accomplish well. 

In the context of this project we will wrestle with this test and I think if we succeed in making bots able to fool a human player into thinking they are a human we’ll be successful. In making the game bigger however and making the game more centered around questioning I think it may make it simpler for computers to imitate humans. Every person is both and interrogator and a player so it will be difficult for one to make obscure questioning line with out skepticism. I hypothesize this will make the corpus of language used inside of the game much smaller and therefore easier to duplicate. I think the most difficult thing to replicate is mistakes that human players will make. It will be interesting to see if we can successfully create a text corpus to duplicate mistakes well and be able to confuse a variety of people from different ages and backgrounds. Further research in its ability to play the game in other languages could also be interesting.

## Requirements

- Unit and Integration tests
- Web UI
- Support n users, where n > 1
- Support m AI models, where m >= 2
- AI models specifically trained inside of the game

## Scope

Ultimately the end product should be an engaging game that demonstrates the current state of the turing test with the aid of LLMs. The sign we have reached our goal is the capability of our model(s) to fool a human player into thinking the model is also human. Furthermore, if the bots themselves struggle to distinguish humans from the bots we have accomplished our goal.

## MVP 

With the AI model being the most unknown and potentially time consuming part of this project I think it is important we build out a low fidelity interface for the AI bots. The easier it is to interface the bots with the application the better and faster we can work to create the best bots. Also, the application should hopefully be designed with plenty of responsiveness with timing and latency being a factor in the game. I propose we design and build out a proper backend and web API. Then we can build out a front end to update a use r on the state of the game and use those same API calls to communicate with the bots what the state of the game is. For its current purposes the bots can respond the same way each time or answer basic questions based off pre generated lists.

- Backend that will serve the initial HTML/CSS/JS
- Web API that will update game state/data for the frontend with the JS
- Backend should manage connections either with session cookies

## Application Architecture

![Architecture](/images/architecture.svg)

## Timeline

| Approximate Date Range          | Description                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| September 15th - September 28th | Design and build frontend/backend, make with a Web API and connect a blind and oblivious bot |
| September 29th - October 26th   | Create models to play the game                                                               |
| October 27th - November 2nd     | Inter-group testing make note any fixes needed                                               |
| November 3rd - November 9th     | Implement fixes                                                                              |
| November 10th - November 16th   | Minor user testing                                                                           |
| November 17th - November 23rd   | Final polishing step to prep for final user testing                                          |
| November 24th - November 30th   | Final user testing stage - collect data to be used in presentations.                         |
| December 1st - December 20th    | Project completion - Preparation for Presentation                                            |

## Deveolopmental Resources

### People

<script src="https://kit.fontawesome.com/c180dbb141.js" crossorigin="anonymous"></script>

Grant, Xavier, Sanjay,

Andrew Carlson: 
<a href="https://github.com/andrewc272">
  <i class="fa-brands fa-github"></i>
</a>

Non-monetary Sponsor: Northrop Grumman 

### Hardware Requirements

- Either a Mac with xGB of RAM or a GPU with xGB of Ram

### Software Requirements

- Python w/ [Flask](https://flask.palletsprojects.com/en/stable/)
- HTML(+Jinja)
- CSS
- JS
- [HuggingFace](https://huggingface.co/)
- [Mistral 7B](https://mistral.ai/news/announcing-mistral-7b)
- SQLite

## How to use

As it sits currently, clone the repository, and enter the commad `flask run`

Dependancies: Python, flask, Browser(for previewing web app)

Also `flask run --host=0.0.0.0` will broadcast the app to the local network allowing other devices to connect as will be important when we want to add multi-player functionality.

## Local AI Bots

The first human that joins the lobby is treated as the host and now sees a **Match Setup** panel during the intro/lobby phases. That panel lets the host decide whether the round should rely on the original cloud/API bots or spin up fully local agents. Everyone else sees a read‑only summary of whichever option the host picked.

### Model presets

| ID      | Summary                     | Hardware Notes                                        |
| ------- | --------------------------- | ----------------------------------------------------- |
| pocket  | Pocket Chat (ultralight)    | Runs `llama3.2:1b` through Ollama – fine on almost any CPU. |
| lounge  | Campus Lounge (laptop)      | Targets `llama3.2`, ideal for 16 GB RAM laptops or Apple Silicon. |
| studio  | Studio 8G (dedicated GPU)   | Uses `llama3.1:8b`, best with ~8 GB VRAM or a beefy CPU. |

Each preset keeps replies short, injects 18‑23 year old slang, and can be multiplied by the host (1‑6 unique bot instances). Presets live in `bot_profiles.py`, so feel free to tweak prompts or add new entries.

### Running with Docker (macOS & Windows)

Use the helper script to launch the stack whether you are on macOS or Windows:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure it is running.
2. Open a terminal (macOS) or PowerShell (Windows) at the repo root and run:
   - macOS/Linux: `./scripts/dev.sh up`
   - Windows PowerShell: `bash scripts/dev.sh up` (requires Git Bash or WSL) or run the commands inside WSL.
3. The script will:
   - Generate `.env` with a random `SECRET_KEY` if it does not exist.
   - Build the Flask image.
   - Launch the stack defined in `docker-compose.yml` (Flask at `http://localhost:5000` by default).
4. When you are finished, run `./scripts/dev.sh down` (or `bash scripts/dev.sh down` on Windows) to stop everything. Add `-d` to run detached (`./scripts/dev.sh up -d`) and use `./scripts/dev.sh logs flask-app` to follow logs.
5. If Windows reports permissions errors running the script, execute the commands inside WSL (`wsl` → `cd /mnt/c/Users/.../capstone` → `./scripts/dev.sh up`).

**Enabling the OpenAI cloud bots:** add both `OPENAI_API_KEY=...` and `CAPSTONE_ENABLE_CLOUD_BOTS=1` to `.env` before running `./scripts/dev.sh up`. Those settings start the `bot1`/`bot2` containers (disabled by default so the stack still works without API access).

**Custom host port:** macOS Control Center already listens on port 5000. If you hit the “address already in use” error, set `CAPSTONE_HOST_PORT=5050` (or any free port) in `.env` and rerun `./scripts/dev.sh up`. Docker will map that host port to the container’s 5000.

**Using local AI bots with Docker (macOS/Windows):**

1. On the host OS (not in Docker) run `python scripts/setup_local_agents.py`. On Windows, run this in PowerShell or WSL using the Python that has network access.
2. Ensure Ollama is running on the host (`ollama serve`). Keep `OLLAMA_URL=http://host.docker.internal:11434` in `.env` so the containerized Flask app can reach the host’s Ollama endpoint.
3. Start the stack with `./scripts/dev.sh up` (or `bash scripts/dev.sh up` on Windows) and open the UI in a browser.
4. In the lobby, switch to **Local AI agents**. The Flask container will spawn `Bot/local_agent.py` processes that talk to the host’s Ollama server via `host.docker.internal`.

If you prefer to run everything directly on your OS instead of Docker (useful for debugging), you can still follow `setup.sh` → `source .venv/bin/activate` → `flask run` and then follow the local agent instructions below.

### Running local agents

1. Run `python scripts/setup_local_agents.py`. This helper tries to install Ollama (winget on Windows, the official install script on macOS/Linux) and automatically pulls every model referenced by the presets. If you already have Ollama, it just refreshes the required models.
2. Start the Flask server with `flask run`. If you expose it on a non‑default port, set `LOCAL_BOT_SERVER_URL=http://127.0.0.1:5001` (or similar) so the spawned agents know where to call back.
3. Join the lobby in a browser, click **Join Game**, then, as the host, select **Local AI agents**, pick the preset, and choose how many bots to spawn.
4. When you click **Start Game**, the Flask app launches `Bot/local_agent.py` in the background. Each bot polls `/gameState`, only speaks on its turn, and queries Ollama (or falls back to heuristics if Ollama isn’t running).
5. Optional environment variables:
   - `OLLAMA_URL` – change this if your Ollama server isn’t on `http://127.0.0.1:11434`.
   - `LOCAL_BOT_SERVER_URL` – point to the Flask instance when it runs behind Docker or a custom hostname.

Switching back to “Cloud API bots” immediately tears down the local processes so the original OpenAI/Mistral bots can keep working unchanged.

### Testing + dev tips

- Automated tests now cover the host selection flow. Run them with `python -m unittest test_app.py`.
- If you need to disable process spawning during automated runs, export `CAPSTONE_SKIP_BOT_MANAGER=1` before starting the app (the tests do this automatically).
