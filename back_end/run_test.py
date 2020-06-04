#import sys
#sys.path.append('/scratch2/openeo/openeo-pg-parser-python/src/openeo_pg_parser_python')

#from openeo_pg_parser_python.translate_process_graph import translate_graph
#from openeo_pg_parser_python.validate import validate_graph
from openeo_pg_parser_python.translate import translate_process_graph
from openeo_pg_parser_python.validate import validate_process_graph

from openeo_pg_parser_python import graph

from jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp')
graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics_test.json")
graph = translate_process_graph("tests/process_graphs/min_evi_jeodpp.json")
graph = translate_process_graph("tests/process_graphs/zonal_statistics.json")

print(graph)
jeodpp.process(graph)
