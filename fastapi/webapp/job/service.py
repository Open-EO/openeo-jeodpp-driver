import json
import logging
import uuid

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


_JOBS_DATA = {"jobs": []}


def get_output_formats_all():
    return _OUTPUT_FORMATS_OPEN_EO_SAMPLE_DICT


def get_jobs_all():
    return _JOBS_DATA


def get_job_by_id(job_id):
    matching_job = None
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                matching_job = job
            else:
                continue
    return matching_job


def create_job(job_payload_data):
    insert_job_record = job_payload_data.dict()
    insert_job_record["job_id"] = str(uuid.uuid4())
    _JOBS_DATA.get("jobs").append(insert_job_record)
    return _JOBS_DATA


def update_job(job_id, job_payload_data):
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                updated_job_record = job_payload_data.dict()
                updated_job_record["job_id"] = str(job_id)
                job.update(updated_job_record)
            else:
                continue
    return job_id


def delete_job(job_id):
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                _JOBS_DATA.get("jobs").remove(job)
            else:
                continue
    return job_id
