import json
import logging

logger = logging.getLogger(__name__)


_PROCESS_OPEN_EO_SAMPLE_DICT = json.loads(
    """
{
	"processes": [{
			"name": "get_collection_example",
			"summary": "Selects a collection.",
			"description": "Filters and selects a single collection provided by the back-end. The back-end provider decides which of the potential collections is the most relevant one to be selected. Example - do not use, it's not an official process description!",
			"min_parameters": 1,
			"parameters": {
				"name": {
					"description": "Filter by collection name",
					"schema": {
						"type": "string",
						"examples": [
							"Sentinel2A-L1C"
						]
					}
				},
				"spatial_extent": {
					"description": "Filter by spatial extent, may include a vertical axis (height or depth).",
					"schema": {
						"type": "object",
						"format": "spatial_extent"
					}
				},
				"temporal_extent": {
					"description": "Filter by time",
					"schema": {
						"type": "array",
						"format": "temporal_extent"
					}
				},
				"bands": {
					"description": "Filter by band IDs",
					"schema": {
						"type": "array",
						"items": {
							"type": "string"
						}
					}
				}
			},
			"returns": {
				"description": "Processed EO data.",
				"schema": {
					"type": "object",
					"format": "eodata"
				}
			}
		},
		{
			"name": "filter_bands_example",
			"summary": "Filter an image collection by bands.",
			"description": "Allows to extract one or multiple bands of multi-band raster image collection. Bands can be chosen either by band id, band name or by wavelength. imagery and at least one of the other arguments is required to be specified. Example - do not use, it's not an official process description!",
			"min_parameters": 2,
			"parameters": {
				"imagery": {
					"description": "EO data to process.",
					"required": true,
					"schema": {
						"type": "object",
						"format": "eodata"
					}
				},
				"bands": {
					"description": "string or array of strings containing band ids.",
					"schema": {
						"type": [
							"string",
							"array"
						],
						"items": {
							"type": "string"
						}
					}
				},
				"names": {
					"description": "string or array of strings containing band names.",
					"schema": {
						"type": [
							"string",
							"array"
						],
						"items": {
							"type": "string"
						}
					}
				},
				"wavelengths": {
					"description": "number or two-element array of numbers containing a wavelength or a minimum and maximum wavelength respectively.",
					"schema": {
						"type": [
							"number",
							"array"
						],
						"minItems": 2,
						"maxItems": 2,
						"items": {
							"type": "number"
						}
					}
				}
			},
			"returns": {
				"description": "Processed EO data.",
				"schema": {
					"type": "object",
					"format": "eodata"
				}
			}
		},
		{
			"name": "filter_daterange_example",
			"summary": "Filter an image collection by temporal extent.",
			"description": "Example - do not use, it's not an official process description!",
			"min_parameters": 1,
			"parameters": {
				"imagery": {
					"description": "EO data to process.",
					"required": true,
					"schema": {
						"type": "object",
						"format": "eodata"
					}
				},
				"extent": {
					"type": "array",
					"description": "Temporal extent specified by a start and an end time, each formatted as a [RFC 3339](https://www.ietf.org/rfc/rfc3339) date-time. Open date ranges are supported and can be specified by setting one of the times to null. Setting both entries to null is not allowed.",
					"example": [
						"2016-01-01T00:00:00Z",
						"2017-10-01T00:00:00Z"
					],
					"items": {
						"type": [
							"string",
							"null"
						],
						"format": "date-time",
						"minItems": 2,
						"maxItems": 2
					}
				}
			},
			"returns": {
				"description": "Processed EO data.",
				"schema": {
					"type": "object",
					"format": "eodata"
				}
			}
		},
		{
			"name": "process_graph_example",
			"description": "Loads another process graph and applies it to the specified imagery. This can be an externally hosted process graph. Example - do not use, it's not an official process description!",
			"parameters": {
				"imagery": {
					"description": "EO data to process.",
					"required": true,
					"schema": {
						"type": "object",
						"format": "eodata"
					}
				},
				"url": {
					"description": "An URL to a process graph.",
					"required": true,
					"schema": {
						"type": "string",
						"format": "url",
						"examples": [
							"http://otherhost.org/api/v1/users/12345/process_graphs/abcdef"
						]
					}
				}
			},
			"returns": {
				"description": "Processed EO data.",
				"schema": {
					"type": "object",
					"format": "eodata"
				}
			},
			"exceptions": {
				"NotFound": {
					"code": 404,
					"description": "Process graph doesn't exist."
				}
			}
		}
	],
	"links": [{
		"rel": "alternate",
		"href": "https://openeo.org/processes",
		"type": "text/html",
		"title": "HTML version of the processes"
	}]
}
"""
)


def get_process_all():
    return _PROCESS_OPEN_EO_SAMPLE_DICT


def get_process_by_id(process_name: str):
    process = [
        process
        for process in _PROCESS_OPEN_EO_SAMPLE_DICT.get("processes")
        if process.get("name") == process_name
    ]
    return process
