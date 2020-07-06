import sys
sys.path.append('../../Open-EO-openeo-pg-parser-python/src')


from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph

from openeo_pg_parser import graph

from jeodpp_backend import BackEnd

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

#print(graph)
print(graph.sort())
#jeodpp.process(graph)
jeodpp.process(graph.sort(),virtual=True)
