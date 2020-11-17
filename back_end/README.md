# openEO JEODPP back-end

## Dependencies
[openeo_pg_parser_python](https://github.com/Open-EO/openeo-pg-parser-python)
from openEO

[pyjeo](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/JIPlib/pyJEO) (open source license in progress)
JRC image processing library (see [publication](https://doi.org/10.3390/ijgi8100461))

[jeolib](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp-services/jeo-libraries/blob/master/README.md)


## Installing in JEO-DESK

### Create and activate virtual environment (venv)

```bash
mkdir ~/openeo-backend && cd ~/openeo-backend
virtualenv --system-site-packages --python /usr/bin/python3 venv3
source venv3/bin/activate
```

### Clone current repository and process graph parser:

```bash
git clone https://github.com/Open-EO/openeo-pg-parser-python
```

###. Install libraries

```bash
pip install ./openeo-pg-parser-python/
pip install python2-secrets
```

## Usage

### Create a python executable file `run_test.py` with the following content:

```python
from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph
from openeo_pg_parser import graph
from openeo_jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp')
graph = translate_graph("path/to/process_graph.json")
jeodpp.process(graph)
```

### Execute the created file:

```bash
python3 run_test.py
```

