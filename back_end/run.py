from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph
from openeo_pg_parser import graph
from openeo_jeodpp_backend import BackEnd

def job_run(job_id: int, user: str = None, path: str = None):
    job_result = {}
    try:
        #todo: get process_graph from job_id
        #todo: update job_id in db as "started"
        jeodpp=BackEnd('jeodpp',user=user, path = path)
        graph = translate_process_graph(process_graph)
        print(graph.sort())
        jeodpp.processGraph(graph.sort(), tileindex=None, tiletotal=None)
        #todo: update job_result with meaningful data
        #todo: update job_id in db as "finished"
    except:
        print("Erorr: job {} did not process, error returned".format(job_id))
        #todo: update job_id in db as "error"
    return job_result
