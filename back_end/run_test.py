import sys
sys.path.append('/scratch2/openeo/openeo-pg-parser-python/src/openeo_pg_parser_python')

from openeo_pg_parser_python.translate_process_graph import translate_graph
from openeo_pg_parser_python.validate_process_graph import validate_graph
from jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp')
graph = translate_graph("tests/process_graphs/zonal_statistics_timeseries.json")
graph = translate_graph("tests/process_graphs/zonal_statistics_test.json")
graph = translate_graph("tests/process_graphs/zonal_statistics.json")
graph = translate_graph("tests/process_graphs/min_evi_1_jeodpp.json")

print(graph)
jeodpp.process(graph)
