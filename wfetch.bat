@echo FETCHING
curl -s http://localhost:8000/status
@echo 
curl -s -X POST http://localhost:8000/score ^
 -H "Content-Type: application/json" ^
 -d "{\"temperature_c\": 28, \"humidity_pct\": 61, \"sound_db\": 55}"

