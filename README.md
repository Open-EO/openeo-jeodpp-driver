# openEO JEODPP web service and back-end

## openEO JEODPP web service

## openEO JEODPP back-end

### Installing in JEO-DESK

1. Create and activate virtual environment (venv)

```bash
mkdir /home/klimeto/openeo-backend && cd /home/klimeto/openeo-backend
virtualenv --system-site-packages --python /usr/bin/python3 venv3
source venv3/bin/activate
```

2. Clone repositories

```bash
git clone https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo
git clone https://github.com/Open-EO/openeo-pg-parser-python
```

3. Install libraries

```bash
pip install ./openeo-pg-parser-python/
pip install python2-secrets
```

4. CD to back_end directory

```bash
cd openeo/back_end
```

5. Create a python executable file `run_test.py` with the following content:

```python
from openeo_pg_parser_python.translate_process_graph import translate_graph
from openeo_pg_parser_python.validate_process_graph import validate_graph
from jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp')
graph = translate_graph("tests/process_graphs/evi_jeodpp.json")
jeodpp.process(graph)

```

6. Execute the created file:

```bash
python run_test.py
```

7. Open calculated file in QGIS:

```bash
qgis /tmp/save_9c0040089af34900.tif
```








