import json
import logging

logger = logging.getLogger(__name__)



_COLLECTION_OPEN_EO_SAMPLE_DICT = json.loads("""
{
  "collections": [
    {
      "name": "Sentinel-2A",
      "title": "Sentinel-2A MSI L1C",
      "description": "Sentinel-2A is a wide-swath, high-resolution, multi-spectral imaging mission supporting Copernicus Land Monitoring studies, including the monitoring of vegetation, soil and water cover, as well as observation of inland waterways and coastal areas.",
      "license": "proprietary",
      "extent": {
        "spatial": [
          180,
          -56,
          -180,
          83
        ],
        "temporal": [
          "2015-06-23T00:00:00Z",
          null
        ]
      },
      "links": [
        {
          "rel": "self",
          "href": "https://openeo.org/api/collections/Sentinel-2A"
        },
        {
          "rel": "license",
          "href": "https://scihub.copernicus.eu/twiki/pub/SciHubWebPortal/TermsConditions/Sentinel_Data_Terms_and_Conditions.pdf"
        }
      ]
    },
    {
      "name": "MOD09Q1",
      "title": "MODIS/Terra Surface Reflectance 8-Day L3 Global 250m SIN Grid V006",
      "description": "The MOD09Q1 Version 6 product provides an estimate of the surface spectral reflectance of Terra MODIS Bands 1-2 corrected for atmospheric conditions such as gasses, aerosols, and Rayleigh scattering. Provided along with the two 250 m MODIS bands is one additional layer, the Surface Reflectance QC 250 m band. For each pixel, a value is selected from all the acquisitions within the 8-day composite period. The criteria for the pixel choice include cloud and solar zenith. When several acquisitions meet the criteria the pixel with the minimum channel 3 (blue) value is used. Validation at stage 3 has been achieved for all MODIS Surface Reflectance products.",
      "license": "proprietary",
      "extent": {
        "spatial": [
          180,
          -90,
          -180,
          90
        ],
        "temporal": [
          "2000-02-01T00:00:00Z",
          null
        ]
      },
      "links": [
        {
          "rel": "self",
          "href": "https://openeo.org/api/collections/MOD09Q1"
        },
        {
          "rel": "license",
          "href": "https://openeo.org/api/collections/MOD09Q1/license"
        }
      ]
    }
  ],
  "links": [
    {
      "rel": "self",
      "href": "https://openeo.org/api/collections"
    },
    {
      "rel": "alternate",
      "href": "https://openeo.org/csw",
      "title": "openEO catalog (OGC Catalogue Services 3.0)"
    }
  ]
}
""")


def get_collection_all():
    return _COLLECTION_OPEN_EO_SAMPLE_DICT


def get_collection_by_id(collection_name: str):
    collection = [ collection for collection in _COLLECTION_OPEN_EO_SAMPLE_DICT.get("collections") if collection.get("name") == collection_name]
    return collection

