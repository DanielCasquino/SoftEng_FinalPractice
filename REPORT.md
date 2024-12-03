# 1st Part

- [x] Base de datos

Usamos postgres :)


- [x] Api swagger

http://localhost:8080/redoc


- [x] Code coverage 90%

coverage run -m pytest

coverage report --show-missing

Tenemos 91% :)


- [x] Endpoint con happy path latency < 1000ms

Endpoints tienen < 10ms


- [x] 400 y 500 documented

http://localhost:8080/redoc


- [] Integration test con base


- [x] Availability 95%

Archivos CSV en jmeter/availability/

Entre los 3 endpoints, hicimos 80k requests, y tuvimos errores en 5k.

(80k / 5k) * 100 = 93.75% de availability :(


- [x] Reliability 95%

Archivos CSV en jmeter/reliability/

Los report summaries demuestran una tasa de error del 0% para usuarios individuales, por lo que el api hace lo que se espera

# 2nd Part

