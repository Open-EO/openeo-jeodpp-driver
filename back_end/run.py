from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph
from openeo_pg_parser import graph
from openeo_jeodpp_backend import BackEnd

def job_run(process_graph: dict, user: str = None, path: str = None):
    job_result = {}
    try:
        jeodpp=BackEnd('jeodpp',user=user, path = path)
        graph = translate_process_graph(process_graph)
        print(graph.sort())
        jeodpp.processGraph(graph.sort(), tileindex=None, tiletotal=None)
        #todo: update job_result
    except:
        print("Erorr: job did not process, error returned")
        #todo: update job as error
    #todo: update job as finished
    return job_result
