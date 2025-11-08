@echo FETCHING
curl -s http://localhost:8000/status
@echo 
curl -s -X POST http://localhost:8000/score ^
 -H "Content-Type: application/json" ^
 -d "{\"temperature_c\": 28, \"humidity\": 61, \"sound\": 55}"

