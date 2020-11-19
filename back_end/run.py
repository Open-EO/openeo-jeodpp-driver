import os
import argparse
from openeo_pg_parser.translate import translate_process_graph
from openeo_pg_parser.validate import validate_process_graph
from openeo_pg_parser import graph
from openeo_jeodpp_backend import BackEnd

import json, urllib.request, ast
import getpass
from uuid import UUID
# from sqlalchemy.orm import Session
# from openeo.web_service.fastapi.webapp.job.manager import get_job_process_graph
# from openeo.web_service.fastapi.webapp.job.manager import update_job_status
# from openeo.web_service.fastapi.webapp.models.job import ProcessStatus


def run_job_id(endPoint: str, job_id: UUID, user: str = None, path: str = None, tileindex: int = None, tiletotal: int = None):
    # endPoint='https://jeodpp.jrc.ec.europa.eu/openeo/jobs'
    try:
        httpGet = endPoint + '/' + job_id
        sendRequest = requests.get(httpGet)
        sendRequest.raise_for_status()
        if sendRequest:
            job_metadata = sendRequest.json()
        else:
            raise urllib.error.ContentTooShortError
        process_graph = job_metadata["process"]
        # process_graph = get_job_process_graph(db_session, job_id)
        #todo: cannot use db here, as long as we are not in the docker-compose scope
        # update_job_status(db_session, job_id, models.job.ProcessStatus.running)
        jeodpp=BackEnd('jeodpp',user=user, path = path)
        graph = translate_process_graph(process_graph)
        jeodpp.processGraph(graph.sort(), tileindex,tiletotal)
        #todo: cannot use db here, as long as we are not in the docker-compose scope
        # update_job_status(db_session, job_id, models.job.ProcessStatus.finished)
        return "finished"
    except:
        print("Erorr: job {} did not process, error returned".format(job_id))
        #todo: cannot use db here, as long as we are not in the docker-compose scope
        # update_job_status(db_session, job_id, models.job.ProcessStatus.error)
        return "error"

def run_job_graph(process_graph: dict, user: str = None, path: str = None, tileindex: int = None, tiletotal: int = None):
    try:
        jeodpp=BackEnd('jeodpp',user=user, path = path)
        translated_graph = translate_process_graph(process_graph)
        jeodpp.processGraph(translated_graph.sort(), tileindex,tiletotal)
        return "finished"
    except:
        return "error"

def main():
    parser=argparse.ArgumentParser()

    parser.add_argument("-process_graph","--process_graph",help="process_graph",dest="process_graph",required=False,type=str)
    parser.add_argument("-job_id","--job_id",help="job id (UUID)",dest="job_id",required=False,type=UUID)
    parser.add_argument("-user","--user",help="user id",dest="user",required=False,type=str, default=None)
    parser.add_argument("-path","--path",help="path to save output",dest="path",required=False,type=str, default=None)
    parser.add_argument("-tileindex","--tileindex",help="tileindex to split input",dest="tileindex",required=False,type=int,default=None)
    parser.add_argument("-tiletotal","--tiletotal",help="total to split input",dest="tiletotal",required=False,type=int,default=None)

    args = parser.parse_args()
    if args.path is not None:
        path = os.path.join(args.path,job_id)
        try:
            os.mkdir(path)
        except OSError:
            print("The creation of the directory {} has failed".format(path))
    else:
        path = None

    if args.process_graph is not None:
        jeodpp=BackEnd('jeodpp',user=args.user, path = path)
        graph = translate_process_graph(process_graph)
        jeodpp.processGraph(graph.sort(), tileindex,tiletotal)
        run_job_graph(args.process_graph, args.user, args.path, args.tileindex, args.tiletotal)
    elif args.job_id is not None:
        run_job_id(args.job_id, args.user, args.path, args.tileindex, args.tiletotal)
    else:
        print("Erorr: either process_graph or a db_session with job_id must be provided")

if __name__ == "__main__":
    main()
