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

import exceptions

import process

class BackEnd:
    def __init__(self, name = None, user = None, path = None, gc = True):
        self.name = name
        self.user = user
        self.path = path
        self.gc = gc

    def processNode(self, agraph, nodeid, jim, tileindex = None,
                    tiletotal = None, virtual = False):
        print("agraph.nodes: {}".format(agraph.nodes))
        #node=graph.nodes[nodeid]
        node=agraph[nodeid]
        if node.content['process_id'] == 'absolute':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'add_dimension':
            return process.add_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'add':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'aggregate_spatial_binary':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'aggregate_spatial':
            return process.aggregate_spatial(agraph, nodeid, jim)
        elif node.content['process_id'] == 'aggregate_temporal':
            return process.aggregate_temporal(agraph, nodeid, jim)
        elif node.content['process_id'] == 'aggregate_temporal_period':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'all':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'and':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'anomaly':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'any':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'apply_dimension':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'apply':
            return process.apply_unary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'apply_kernel':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'apply_neighborhood':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arccos':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arcosh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arcsin':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arctan2':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arctan':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'array_apply':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'array_contains':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'array_element':
            return process.array_element(agraph, nodeid, jim)
        elif node.content['process_id'] == 'array_filter':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'array_find':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'array_labels':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'arsinh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'artanh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'between':
            return process.between(agraph, nodeid, jim)
        elif node.content['process_id'] == 'ceil':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'climatological_normal':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'clip':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'constant':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cosh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cos':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'count':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'create_raster_cube':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cummax':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cummin':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cumproduct':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'cumsum':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'debug':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'dimension_labels':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'divide':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'drop_dimension':
            return process.drop_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'e':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'eq':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'exp':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'extrema':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'filter_bands':
            return process.filter_bands(agraph, nodeid, jim)
        elif node.content['process_id'] == 'filter_bbox':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'filter_labels':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'filter_spatial':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'filter_temporal':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'first':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'floor':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'gte':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'gt':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'if':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'int':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'is_nan':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'is_nodata':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'is_valid':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'last':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'linear_scale_range':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'ln':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'load_collection':
            return process.load_collection(agraph, nodeid, jim, tileindex, tiletotal,
                                   virtual)
        elif node.content['process_id'] == 'load_result':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'load_uploaded_files':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'log':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'lte':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'lt':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'mask':
            return process.mask(agraph, nodeid, jim)
        elif node.content['process_id'] == 'mask_polygon':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'max':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'mean':
            return process.mean(agraph, nodeid, jim)
        elif node.content['process_id'] == 'median':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'merge_cubes':
            return process.merge_cubes(agraph, nodeid, jim)
        elif node.content['process_id'] == 'min':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'mod':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'multiply':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'ndvi':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'neq':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'normalized_difference':
            return process.normalized_difference(agraph, nodeid, jim)
        elif node.content['process_id'] == 'not':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'order':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'or':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'pi':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'power':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'product':
            return process.product(agraph, nodeid, jim)
        elif node.content['process_id'] == 'quantiles':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'rearrange':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'reduce_dimension_binary':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'reduce_dimension':
            return process.reduce_dimension(agraph, nodeid, jim)
        elif node.content['process_id'] == 'rename_dimension':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'rename_labels':
            return process.rename_labels(agraph, nodeid, jim)
        elif node.content['process_id'] == 'resample_cube_spatial':
            return process.resample_cube_spatial(agraph, nodeid, jim)
        elif node.content['process_id'] == 'resample_cube_temporal':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'resample_spatial':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'round':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'run_udf_externally':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'run_udf':
            return process.run_udf(agraph, nodeid, jim)
        elif node.content['process_id'] == 'save_result':
            if self.path is not None:
                pathname=os.path.join(self.path,node.id)
            elif self.user is not None:
                pathname=os.path.join('/home',self.user,node.id)
            else:
                pathname=os.path.join('/tmp',node.id)
            if tileindex is not None and tiletotal is not None:
                pathname += '_'+str(tileindex)+'_'+str(tiletotal)
            return process.save_result(agraph, nodeid, jim, pathname)
        elif node.content['process_id'] == 'sd':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'sgn':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'sinh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'sin':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'sort':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'sqrt':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'subtract':
            return process.apply_binary(agraph, nodeid, jim)
        elif node.content['process_id'] == 'sum':
            return process.sum(agraph, nodeid, jim)
        elif node.content['process_id'] == 'tanh':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'tan':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'text_begins':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'text_contains':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'text_ends':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'text_merge':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'trim_cube':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'variance':
            raise exceptions.NoSuchProcess("process not implemented yet")
        elif node.content['process_id'] == 'xor':
            raise exceptions.NoSuchProcess("process not implemented yet")
        else:
            raise exceptions.NoSuchProcess("process {process} not implemented yet".format(process=node.content['process_id']))

    def processGraph(self, agraph, tileindex = None, tiletotal = None,
                     virtual = False):
        jim={}
        verbose = True
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
                        print("skipping node {} that was already "
                              "calculated".format(node.id))
                    continue
                else:
                    self.processNode(agraph, node.id, jim, tileindex,
                                     tiletotal, virtual)
                if jim[node.id] is not None:
                    if verbose:
                        print("calculated result for {}".format(node.id))
                        print("type of jim returned: {}".format(
                            type(jim[node.id])))
                    if isinstance(jim[node.id],Cube):
                        if verbose:
                            print("number of planes returned: {}".format(
                                jim[node.id].properties.nrOfPlane()))
                            print("number of bands returned: {}".format(
                                jim[node.id].properties.nrOfBand()))
                    elif isinstance(jim[node.id],pj.JimVect):
                        if verbose:
                            print("number of features calculated: {}".format(
                                jim[node.id].properties.getFeatureCount()))
                    elif isinstance(jim[node.id],Collection):
                        if verbose:
                            print("Node is collection not loaded in memory")
                    elif isinstance(jim[node.id],bool):
                        if verbose:
                            print("Node is intermediate result")
                    elif isinstance(jim[node.id],Jim):
                        if verbose:
                            print("Node is a Jim, converting to Cube")
                        jim[node.id].__class__ = Cube
                    else:
                        raise TypeError("Error: result should either be Jim or "
                                        "JimVect")
                    for ancestor in node.ancestors().nodes:
                        collectGarbage = self.gc
                        for descendant in ancestor.descendants().nodes:
                            if jim[descendant.id] is None:
                                collectGarbage = False
                                print("cannot collect garbage for ancestor node "
                                      "{} yet, found descendant {}".format(
                                          ancestor.id,
                                          descendant.id))
                                break
                        if collectGarbage and not isinstance(jim[ancestor.id],
                                                             bool):
                            print("collecting garbage for node {}".format(
                                ancestor.id))
                            jim[ancestor.id] = True
                            gc.collect()
                else:
                    if verbose:
                        print("could not calculate result for node {}".format(
                            node.id))
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
