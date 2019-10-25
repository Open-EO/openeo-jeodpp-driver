import os
import re
from json import load
import requests
import sys
sys.path.append('/scratch2/openeo/openeo-pg-parser-python/src')
sys.path.append('/scratch2/openeo/openeo-pg-parser-python/src/openeo_pg_parser_python')
sys.path.append('/home/kempepi/openeo/back_end')

from openeo_pg_parser_python.translate_process_graph import translate_graph
from openeo_pg_parser_python.validate_process_graph import validate_graph
from jeodpp_backend import BackEnd

# Global variables for tests
PG_FOLDER = os.path.join(os.path.dirname(__file__), 'process_graphs')
PROCESSES_FOLDER_LOCAL = os.path.join(os.path.dirname(__file__), "processes")

def load_processes_local():
    #test
    # print("we are in load_processes_local")
    pattern = re.compile(".*.json$")
    filenames = [filename for filename in os.listdir(PROCESSES_FOLDER_LOCAL) if re.match(pattern, filename)]
    filepaths = [os.path.join(PROCESSES_FOLDER_LOCAL, filename) for filename in filenames]
    processes_list = []
    for filepath in filepaths:
        processes_list.append(load(open(filepath)))

    return processes_list


def validate_process_graph(pg_filepath, processes_url=None):
    """
    Validate a process graph according to the specified processes.

    """

    if not processes_url:
        processes_list = load_processes_local()
    else:
        r = requests.get(url=processes_url)
        data = r.json()
        processes_list = data['processes']


    validated = validate_graph(pg_filepath, processes_list)

    assert validated


def test_validate_process_graph_local():
    """
    Validate a process graph using processes defined on a backend
    """

    # Validate input file
    # validate_process_graph(os.path.join(PG_FOLDER, "use_case_1.json"))
    validate_process_graph(os.path.join(PG_FOLDER, "evi.json"))
    # Validate input dictionary
    # validate_process_graph(load(open(os.path.join(PG_FOLDER, "use_case_1.json"))))


def test_validate_process_graph_remote():
    """
    Validate a process graph using locally specified processes
    """

    validate_process_graph(os.path.join(PG_FOLDER, "test_1.json"),
                           processes_url="https://earthengine.openeo.org/v0.4/processes")


def test_translate_process_graph():
    """
    Translate pg from openEO syntax to python traversable object
    """

    graph = translate_graph(os.path.join(PG_FOLDER, "use_case_1.json"))

def test_evi():
    """
    test the evi process
    """
    graph = translate_graph(os.path.join(PG_FOLDER, "evi_jeodpp.json"))
    print(graph)

    graph.process()

def test_aggregate_polygon():
    """
    test the aggregate polygon process (use case 3)
    """
    graph = translate_graph(os.path.join(PG_FOLDER, "zonal_statistics.json"))
    print(graph)
    graph.process()

if __name__ == '__main__':
    # test_validate_process_graph_local()
    # test_validate_process_graph_remote()
    # test_translate_process_graph()
    # test_evi()
    jeodpp=BackEnd('jeodpp')
    graph = translate_graph(os.path.join(PG_FOLDER, "evi_jeodpp.json"))
    print(graph)
    jeodpp.process(graph)
