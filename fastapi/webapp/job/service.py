import json
import logging

logger = logging.getLogger(__name__)


_OUTPUT_FORMATS_OPEN_EO_SAMPLE_DICT = json.loads(
    """
{
  "default": "GTiff",
  "formats": {
    "GTiff": {
      "gis_data_types": [
        "raster"
      ],
      "parameters": {
        "tiled": {
          "type": "boolean",
          "description": "This option can be used to force creation of tiled TIFF files [true]. By default [false] stripped TIFF files are created.",
          "default": false
        },
        "compress": {
          "type": "string",
          "description": "Set the compression to use.",
          "default": "none",
          "enum": [
            "JPEG",
            "LZW",
            "DEFLATE",
            "NONE"
          ]
        },
        "photometric": {
          "type": "string",
          "description": "Set the photometric interpretation tag.",
          "enum": [
            "MINISBLACK",
            "MINISWHIT",
            "RGB",
            "CMYK",
            "YCBCR",
            "CIELAB",
            "ICCLAB",
            "ITULAB"
          ],
          "default": "RGB"
        },
        "jpeg_quality": {
          "type": "integer",
          "description": "Set the JPEG quality when using JPEG.",
          "minimum": 1,
          "maximum": 100,
          "default": 75
        }
      }
    },
    "GeoPackage": {
      "gis_data_types": [
        "raster",
        "vector"
      ],
      "parameters": {
        "gis_data_type": {
          "type": "string",
          "enum": [
            "raster",
            "vector"
          ],
          "required": true
        },
        "version": {
          "type": "string",
          "description": "Set GeoPackage version. In AUTO mode, this will be equivalent to 1.2 starting with GDAL 2.3.",
          "enum": [
            "auto",
            1,
            1.1,
            1.2
          ],
          "default": "auto"
        },
        "geometry_name": {
          "type": "string",
          "description": "**VECTOR ONLY.** Column to use for the geometry column.",
          "default": "geom"
        },
        "table": {
          "type": "string",
          "description": "**RASTER ONLY.** Name of the table containing the tiles. If the GeoPackage dataset only contains one table, this option is not necessary. Otherwise, it is required."
        }
      }
    },
    "JSON": {
      "gis_data_types": [
        "other"
      ]
    }
  }
}
"""
)


_OUTPUT_JOBS_OPEN_EO_SAMPLE_DICT = json.loads(
"""
{
  "jobs": [
    {
      "job_id": "a3cca2b2aa1e3b5b",
      "title": "NDVI based on Sentinel 2",
      "description": "Deriving minimum NDVI measurements over pixel time series of Sentinel 2 imagery.",
      "status": "running",
      "submitted": "2017-01-01T09:32:12Z",
      "updated": "2017-01-01T09:36:18Z",
      "plan": "free",
      "costs": 12.98,
      "budget": 100
    }
  ],
  "links": [
    {
      "rel": "related",
      "href": "http://www.openeo.org",
      "type": "text/html",
      "title": "openEO"
    }
  ]
}
"""
)

def get_output_formats_all():
    return _OUTPUT_FORMATS_OPEN_EO_SAMPLE_DICT


def get_jobs_all():
    return _OUTPUT_JOBS_OPEN_EO_SAMPLE_DICT


def get_job_by_id(job_id: str):
    job = [
        job
        for job in _OUTPUT_JOBS_OPEN_EO_SAMPLE_DICT.get("jobs")
        if job.get("job_id") == job_id
    ]
    return job
