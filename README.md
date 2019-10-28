# openEO JEODPP web service and back-end

## openEO JEODPP back-end

### dependencies
[openeo_pg_parser_python](https://github.com/Open-EO/openeo-pg-parser-python)
from openEO

[secrets](https://docs.python.org/3/library/secrets.html)
to generate random node id names

### usage
Create [process graph](https://open-eo.github.io/openeo-api/processgraphs/)
as json file

for instance: evi_jeodpp.json

Python3:
```
jeodpp=BackEnd('jeodpp')
graph = translate_graph("evi_jeodpp.json")
jeodpp.process(graph)
```

