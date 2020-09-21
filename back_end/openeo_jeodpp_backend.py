from datetime import time, timedelta, datetime
import dateutil.parser
import os
import json
from openeo_pg_parser import graph
import gc
import inspect
import numpy as np
from jeolib.collection import Collection
from jeolib.cube import Cube
import pyjeo as pj

from process import load_collection, save_result, filter_bands, array_element, apply_unary, apply_binary, mask, reduce_dimension, aggregate_temporal, merge_cubes, add_dimension, drop_dimension, rename_labels, resample_cube_spatial, run_udf, aggregate_spatial

verbose=True

class BackEnd:
    def __init__(self, name=None, user=None, path=None, gc=True):
        self.name = name
        self.user = user
        self.path = path
        self.gc = gc

    def processNode(self, agraph, nodeid, jim, tileindex=None, tiletotal=None, virtual=False):
        print('agraph.nodes: {}'.format(agraph.nodes))
        #node=graph.nodes[nodeid]
        node=agraph[nodeid]
        if node.content['process_id'] == 'save_result':
            return save_result(agraph, nodeid, jim, tileindex, tiletotal)
        elif node.content['process_id'] == 'load_collection':
            return load_collection(agraph, nodeid, jim, tileindex, tiletotal, virtual)
        elif node.content['process_id'] == 'filter_bands':
            return filter_bands(agraph, nodeid, jim)
        elif node.content['process_id'] == 'array_element':
            return array_element(agraph, nodeid, jim)
        elif node.content['process_id'] == 'apply':
            return apply_unary(agraph, nodeid, jim)
        elif node.content['process_id'] in ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'sum', 'subtract', 'product', 'divide']:
            return apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == "mask":
            return mask(agraph, nodeid, jim)
        elif node.content['process_id'] == 'reduce_dimension':
            return reduce_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'aggregate_temporal':
            return aggregate_temporal(agraph, nodeid, jim)
        elif node.content['process_id'] == 'merge_cubes':
            return merge_cubes(agraph, nodeid, jim)
        elif node.content['process_id'] == 'add_dimension':
            return add_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'drop_dimension':
            return drop_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'rename_labels':
            return rename_labels(agraph, nodeid, jim)
        elif node.content['process_id'] == 'resample_cube_spatial':
            return resample_cube_spatial(agraph, nodeid, jim)
        elif node.content['process_id'] == 'run_udf':
            return run_udf(agraph, nodeid, jim)
        elif node.content['process_id'] == 'aggregate_spatial':
            return aggregate_spatial(agraph, nodeid, jim)

    def processGraph(self, agraph, tileindex=None, tiletotal=None, virtual=False):
        jim={}
        if verbose:
            print("initialize")

        print("agraph.nodes: {}".format(agraph.nodes))
        #for node in agraph.nodes.values():
        for node in agraph.nodes:
            jim[node.id]=None
        finished=False
        if verbose:
            print("starting process")
        while not finished:
            if verbose:
                print("finished is: {}".format(finished))
            finished=True
            #for node in agraph.nodes.values():
            for node in agraph.nodes:
                print("processing node {}".format(node.id))
                if jim[node.id] is not None:
                    if verbose:
                        print("skipping node {} that was already calculated".format(node.id))
                    continue
                else:
                    self.processNode(agraph, node.id, jim, tileindex, tiletotal, virtual)
                if jim[node.id] is not None:
                    if verbose:
                        print("calculated result for {}".format(node.id))
                        print("type of jim returned: {}".format(type(jim[node.id])))
                    if isinstance(jim[node.id],Cube):
                        if verbose:
                            print("number of planes returned: {}".format(jim[node.id].properties.nrOfPlane()))
                            print("number of bands returned: {}".format(jim[node.id].properties.nrOfBand()))
                    elif isinstance(jim[node.id],pj.JimVect):
                        if verbose:
                            print("number of features calculated: {}".format(jim[node.id].properties.getFeatureCount()))
                    elif isinstance(jim[node.id],Collection):
                        if verbose:
                            print("Node is collection not loaded in memory")
                    elif isinstance(jim[node.id],bool):
                        if verbose:
                            print("Node is intermediate result")
                    else:
                        raise TypeError("Error: result should either be Jim or JimVect")
                    for ancestor in node.ancestors().nodes:
                        collectGarbage = self.gc
                        for descendant in ancestor.descendants().nodes:
                            if jim[descendant.id] is None:
                                collectGarbage = False
                                print("cannot collect garbage for ancestor node {} yet, found descendant {}".format(ancestor.id, descendant.id))
                                break
                        if collectGarbage and not isinstance(jim[ancestor.id],bool):
                            print("collecting garbage for node {}".format(ancestor.id))
                            jim[ancestor.id] = True
                            gc.collect()
                else:
                    if verbose:
                        print("could not calculate result for node {}".format(node.id))
                    continue

            ntodo=0;
            #for node in agraph.nodes.values():
            for node in agraph.nodes:
                if jim[node.id] is None:
                    if not ntodo:
                        if verbose:
                            print("nodes to do:")
                    if verbose:
                        print(node.id)
                    ntodo+=1

            if ntodo:
                finished=False
            elif verbose:
                print("All nodes processed")
