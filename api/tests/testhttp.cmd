curl.exe -X POST -H "Content-Type: application/json" -d "{\"channel\":\"B\",\"mode\":\"0\",\"short_time\":"10"}" http://localhost:8088/api/v1/properties
curl.exe -X POST -H "Content-Type: application/json" -d "{\"channel\":\"B\",\"time\":120}" http://localhost:8088/api/v1/state
pause
curl.exe -X GET -H "Content-Type: application/json" http://localhost:8088/api/v1/state
