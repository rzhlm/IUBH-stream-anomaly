# IU: Stream anomaly detection
Task 1, in DLBDSMTP01: Project: from Model to Production

## What this project does:
- (simulated) sensors in a factory send their data
- goes to API server, server calculates "anomaly score" and returns it
- monitoring is done on a HTTP dashboard

## How to run:
a) clone the project from this git repo
```
git clone URL
```

b) run
- if using Docker compose:
```
# docker-compose v1:
docker-compose up --build

# or docker compose v2:
docker compose up --build
```

- if running natively:
this project was built using 'uv' for package management, python version management, venv, etc.
uv is not required as common standards are used: pip, poetry or other tools should work fine.

    * start api server:
    ```
    uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
    ```

   * start data sender (sensor simulator)
    ```
    uv run python ./src/sim/sim.py
    ```

   * start monitoring dashboard
    ```
    uv run streamlit run ./src/dash/dash_live.py
    ```


## current endpoints:
GET /status

GET /recent_scores

POST /score (JSON)


## diagrams (Mermaid):
 links:
- [architecture](./documentation/architecture.mermaid)
- [sequence](./documentation/sequence.mermaid)
