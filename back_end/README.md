# openEO JEODPP web service and back-end

## openEO JEODPP back-end

### Dependencies
[openeo_pg_parser_python](https://github.com/Open-EO/openeo-pg-parser-python)
from openEO

[secrets](https://docs.python.org/3/library/secrets.html)
to generate random node id names

[pyjeo](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/JIPlib/pyJEO) (open source license in progress)
JRC image processing library (see [publication](https://doi.org/10.3390/ijgi8100461))

[jeo-library](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp-services/jeo-libraries/blob/master/README.md)

### Usage
Create [process graph](https://open-eo.github.io/openeo-api/processgraphs/)
as json file
 
Check available [examples](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo/tree/master/back_end/tests/process_graphs)

```json
for instance: evi_jeodpp.json (in tests/process_graphs))
{
  "dc": {
    "process_id": "load_collection",
    "description": "Loading the data; The order of the specified bands is important for the following reduce operation.",
    "parameters": {
      "id": "S2MSI2A",
      "spatial_extent": {
        "west": 16.1,
        "east": 16.6,
        "north": 48.6,
        "south": 47.2
      },
      "temporal_extent": ["2018-05-01", "2018-05-30"],
      "bands": ["B8", "B4", "B2"]
    }
  },
  "evi": {
    "process_id": "reduce",
    "description": "Compute the EVI. Formula: 2.5 * (NIR - RED) / (1 + NIR + 6*RED + -7.5*BLUE)",
    "parameters": {
      "data": {"from_node": "dc"},
      "dimension": "spectral",
      "reducer": {
        "callback": {
          "nir": {
            "process_id": "array_element",
            "parameters": {
              "data": {"from_argument": "data"},
              "index": 0
            }
          },
          "red": {
            "process_id": "array_element",
            "parameters": {
              "data": {"from_argument": "data"},
              "index": 1
            }
          },
          "blue": {
            "process_id": "array_element",
            "parameters": {
              "data": {"from_argument": "data"},
              "index": 2
            }
          },
          "sub": {
            "process_id": "subtract",
            "parameters": {
              "data": [{"from_node": "nir"}, {"from_node": "red"}]
            }
          },
          "p1": {
            "process_id": "product",
            "parameters": {
              "data": [6, {"from_node": "red"}]
            }
          },
          "p2": {
            "process_id": "product",
            "parameters": {
              "data": [-7.5, {"from_node": "blue"}]
            }
          },
          "sum": {
            "process_id": "sum",
            "parameters": {
              "data": [1, {"from_node": "nir"}, {"from_node": "p1"}, {"from_node": "p2"}]
            }
          },
          "div": {
            "process_id": "divide",
            "parameters": {
              "data": [{"from_node": "sub"}, {"from_node": "sum"}]
            }
          },
          "p3": {
            "process_id": "product",
            "parameters": {
              "data": [2.5, {"from_node": "div"}]
            },
            "result": true
          }
        }
      }
    }
  },
  "mintime": {
    "process_id": "reduce",
    "description": "Compute a minimum time composite by reducing the temporal dimension",
    "parameters": {
      "data": {"from_node": "evi"},
      "dimension": "temporal",
      "reducer": {
        "callback": {
          "min": {
            "process_id": "max",
            "parameters": {
              "data": {"from_argument": "data"}
            },
            "result": true
          }
        }
      }
    }
  },
  "save": {
    "process_id": "save_result",
    "parameters": {
      "data": {"from_node": "mintime"},
      "format": "GTiff"
    },
    "result": true
  }
}
```

Python3:

```python
jeodpp=BackEnd('jeodpp')
graph = translate_graph("evi_jeodpp.json")
jeodpp.process(graph)
```

