# openEO JEODPP web service and back-end

## openEO JEODPP back-end

### Dependencies
[openeo_pg_parser_python](https://github.com/Open-EO/openeo-pg-parser-python)
from openEO

[pyjeo](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/JIPlib/pyJEO) (open source license in progress)
JRC image processing library (see [publication](https://doi.org/10.3390/ijgi8100461))

[jeolib](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp-services/jeo-libraries/blob/master/README.md)

### Usage
Create [process graph](https://open-eo.github.io/openeo-api/processgraphs/)
as json file
 
Check available [examples](https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/openeo/tree/master/back_end/tests/process_graphs)

for instance: evi_jeodpp.json

```json
{
    "process_graph":
    {
        "dc": {
            "process_id": "load_collection",
            "description": "Loading the data; The order of the specified bands is important for the following reduce operation.",
            "arguments": {
                "id": "S2MSI2A",
                "temporal_extent": [
                    "2019-01-01T00:00:00.000Z",
                    "2020-01-01T00:00:00.000Z"
                ],
                "bands": ["B4","B8","SCL"],
                "properties": {
                    "eo:cloud_cover": {
                        "process_graph": {
                            "cc": {
                                "process_id": "between",
                                "arguments": {
                                    "x": {
                                        "from_parameter": "value"
                                    },
                                    "min": 0,
                                    "max": 80
                                },
                                "result": true
                            }
                        }
                    },
                    "eo:mgrs": {
                        "process_graph": {
                            "mgrs": {
                                "process_id": "eq",
                                "arguments": {
                                    "x": {
                                        "from_parameter":"value"
                                    },
                                    "y": "31UFT"
                                },
                            	"result": true
                            }
                        }
                    }
                }
            }
        },
        "ndvi": {
            "process_id": "reduce_dimension",
            "arguments": {
                "data": {
                    "from_node": "dc"
                },
                "reducer": {
                    "process_graph": {
                        "red": {
                            "process_id": "array_element",
                            "arguments": {
                                "data": {
                                    "from_parameter": "data"
                                },
                                "label": "B4"
                            }
                        },
                        "nir": {
                            "process_id": "array_element",
                            "arguments": {
                                "data": {
                                    "from_parameter": "data"
                                },
                                "label": "B8"
                            }
                        },
                        "ndvi": {
                            "process_id": "normalized_difference",
                            "arguments": {
                                "x": {
                                    "from_node": "nir"
                                },
                                "y": {
                                    "from_node": "red"
                                }
                            },
                            "result": true
                        }
                    }
                },
                "dimension": "bands"
            },
        "description": "Compute the NDVI: (NIR - RED) / (NIR + RED)"
        },
        "cloudMask": {
            "process_id": "reduce_dimension",
            "arguments": {
                "data": {
                    "from_node": "dc"
                },
                "dimension": "bands",
                "reducer": {
                    "process_graph": {
                        "scl": {
                            "process_id": "array_element",
                            "arguments": {
                                "data": {
                                    "from_parameter": "data"
                                },
                                "label": "SCL"
                            }
                        },
                        "eq1": {
                            "process_id": "neq",
                            "arguments": {
                                "x": {
                                    "from_node": "scl"
                                },
                                "y": 4
                            },
                            "result": true
                        }
                    }
                }
            },
            "description": "Scene classification mask"
        },
        "maskedNdvi": {
            "process_id": "mask",
            "arguments": {
                "data": {
                    "from_node": "ndvi"
                },
                "mask": {
                    "from_node": "cloudMask"
                },
                "replacement": 0
            },
            "result": true
        },
        "savgolay": {
            "process_id": "run_udf",
            "arguments": {
                "data": {"from_node": "maskedNdvi"},
                "runtime": "Python",
                "version": "latest",
                "udf": "def savgolay(jim):\n  jim.ngbops.smoothNoData1d(0,interp='linear')\n  nplane=jim.properties.nrOfPlane()\n  nl=min(7,(nplane-1)/2)\n  nr=min(7,(nplane-1)/2)\n  savgol=Cube(pj.ngbops.savgolay(jim, nl=nl, nr=nr, m=2, pad='replicate'))\n  print(jim.properties.getDataType())\n  print(savgol.properties.getDataType())\n  for loop in range(0,4):\n    savgol.pixops.convert(otype=jim.properties.getDataType())\n    print('iteration {}'.format(loop))\n    savgol[savgol<jim]=jim\n    nl=min(4,(nplane-1)/2)\n    nr=min(4,(nplane-1)/2)\n    m=min(6,nl+nr-1)\n    print('nl: {}'.format(nl))\n    print('nr: {}'.format(nr))\n    print('m: {}'.format(m))\n    savgol=Cube(pj.ngbops.savgolay(savgol, nl=nl, nr=nr, m=m, pad='replicate'))\n  savgol.dimension=jim.dimension\n  return Cube(savgol)"
            },
            "result": true
        },
        "aggreg1": {
            "process_id": "aggregate_spatial",
            "description": "aggregate spatial using mean value",
            "arguments": {
                "data": {"from_node": "savgolay"},
                "geometries": {
                    "type": "file",
                    "path": "/eos/jeodpp/data/base/Landuse/COUNTRIES/NL/Agriculture/Parcels/VER2017/Data/FileGDB/BRP_Gewaspercelen_2017.gdb"
                },
                "context": {
                    "buffer": -10,
                    "srcnodata": 0
                },
                "reducer": {
                    "process_graph": {
                        "mean": {
                            "process_id": "mean",
                            "arguments": {
                                "data": {"from_parameter": "data"}
                            },
                            "result": true
                        }
                    }
                }
            }
        },
        "save": {
            "process_id": "save_result",
            "arguments": {
                "data": {"from_node": "aggreg1"},
                "format": "JSON"
            },
            "result": true
        }
    }
}

```

Python3:

```python
from openeo_pg_parser_python.translate_process_graph import translate_graph
from openeo_pg_parser_python.validate_process_graph import validate_graph
from openeo_pg_parser import graph
from openeo-jeodpp-backend import BackEnd

jeodpp=BackEnd('jeodpp',user='kempepi')
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_udf.json")
print(graph.sort())
jeodpp.process(graph.sort(), tileindex=36, tiletotal=64)
```

