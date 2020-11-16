# openEO JEODPP web service and back-end

## openEO JEODPP web service

## openEO JEODPP back-end

### Installing in JEO-DESK

1. Create and activate virtual environment (venv)

```bash
mkdir ~/openeo-backend && cd ~/openeo-backend
virtualenv --system-site-packages --python /usr/bin/python3 venv3
source venv3/bin/activate
```

2. Clone current repository and process graph parser:

```bash
git clone https://github.com/Open-EO/openeo-pg-parser-python
```

3. Install libraries

```bash
pip install ./openeo-pg-parser-python/
pip install python2-secrets
```

4. Create a python executable file `run_test.py` with the following content:

```python
from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph
from openeo_pg_parser import graph
from openeo_jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp')
graph = translate_graph("tests/process_graphs/evi_jeodpp.json")
jeodpp.process(graph)
```

5. Execute the created file:

```bash
python run_test.py
