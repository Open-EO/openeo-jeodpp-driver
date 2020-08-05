#import sys
#sys.path.append('../../Open-EO-openeo-pg-parser-python/src')

from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph

from openeo_pg_parser import graph

from jeodpp_backend import BackEnd

def memory_usage():
    """Memory usage of the current process in kilobytes."""
    status = None
    result = {'peak': 0, 'rss': 0}
    try:
        # This will only work on systems with a /proc file system
        # (like Linux).
        status = open('/proc/self/status')
        for line in status:
            parts = line.split()
            key = parts[0][2:-1].lower()
            if key in result:
                result[key] = int(parts[1])
    finally:
        if status is not None:
            status.close()
    return result['peak']/1024.0/1024.0

jeodpp=BackEnd('jeodpp',user='kempepi')
graph = translate_process_graph("tests/process_graphs/evi_eodc_1.json")
graph = translate_process_graph("tests/process_graphs/s2_max_ndvi.json")
graph = translate_process_graph("tests/process_graphs/evi_eodc.json")
#graph = translate_process_graph("tests/process_graphs/evi_eodc_test.json")
graph = translate_process_graph("tests/process_graphs/min_evi_jeodpp.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_test.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_test.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_geometry.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_mgrs.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_file.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_file.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_file_mask.json")
#graph = translate_process_graph("tests/process_graphs/ndvi_masked_timeseries.json")
#graph = translate_process_graph("tests/process_graphs/ndvi_masked_timeseries_udf.json")

#print(graph)
print(graph.sort())
print("memory before process (in GB): {}".format(memory_usage()))
jeodpp.process(graph.sort(), tileindex=36, tiletotal=64)
#jeodpp.process(graph.sort())
#jeodpp.process(graph.sort(),virtual=True)
print("memory after process (in GB): {}".format(memory_usage()))
