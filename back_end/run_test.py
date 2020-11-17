from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph

from openeo_pg_parser import graph

from openeo_jeodpp_backend import BackEnd

jeodpp=BackEnd('jeodpp',user='kempepi')
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_test.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_test.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_geometry.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_mgrs.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_file.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_file.json")
#graph = translate_process_graph("tests/process_graphs/ndvi_masked_timeseries.json")
#graph = translate_process_graph("tests/process_graphs/ndvi_masked_timeseries_udf.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_file_mask.json")
#graph = translate_process_graph("tests/process_graphs/zonal_statistics_timeseries_ndvi_udf.json")
#graph = translate_process_graph("tests/process_graphs/jrc_usecase5_noudf.json")
#graph = translate_process_graph("tests/process_graphs/jrc_uc1_pol.json")
#graph = translate_process_graph("tests/process_graphs/jrc_uc1_temp.json")
#graph = translate_process_graph("tests/process_graphs/jrc_usecase5_udf.json")
#graph = translate_process_graph("tests/process_graphs/jrc_usecase5_noudf.json")
#graph = translate_process_graph("tests/process_graphs/JRC_job.json")
# graph = translate_process_graph("tests/process_graphs/jrc_d22_evi.json")
# graph = translate_process_graph("tests/process_graphs/evi_eodc_1.json")
# graph = translate_process_graph("tests/process_graphs/s2_max_ndvi.json")
# graph = translate_process_graph("tests/process_graphs/evi_eodc.json")
# graph = translate_process_graph("tests/process_graphs/min_evi_jeodpp.json")
graph = translate_process_graph("tests/process_graphs/evi_jeodpp.json")


print(graph.sort())
jeodpp.processGraph(graph.sort(), tileindex=None, tiletotal=None)
