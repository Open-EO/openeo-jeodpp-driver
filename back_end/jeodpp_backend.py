from datetime import time, timedelta, datetime
import os
import graph
from jeolib import Collection
import pyjeo as pj

class BackEnd:
    def __init__(self, name=None):
        self.name = name

    def processNode(self, graph, nodeid, jim):
        verbose=True
        node=graph.nodes[nodeid]
        if node.graph['process_id'] == 'save_result':
            if node.graph['arguments']['data']['from_node'] not in jim:
                print("cannot save result yet")
                jim[node.id]=None
                return jim[node.id]
            if jim[node.graph['arguments']['data']['from_node']]:
                print("saving result")
                jim[node.id]=jim[node.graph['arguments']['data']['from_node']]
                if isinstance(jim[node.id],pj.Jim):
                    pathname=os.path.join('/tmp',node.id+'.tif')
                    jim[node.id].io.write(pathname,co=['COMPRESS=LZW','TILED=YES'])
                elif isinstance(jim[node.id],pj.JimVect):
                    pathname=os.path.join('/tmp',node.id+'.sqlite')
                    jim[node.id].io.write(pathname)
                else:
                    raise TypeError("Error: {} type not supported for writing".format(type(jim[node.id])))
                return jim[node.id]
            else:
                print("cannot save result yet")
                jim[node.id]=None
                return jim[node.id]
        elif node.graph['process_id'] == 'load_collection':
            if verbose:
                print("load_collection")
            coll=Collection()
            coll.filterOn('productType',node.graph['arguments']['id'])
            properties={}
            #test
            # properties['cloudCoverPercentage']='<10'
            # if 'properties' in node.graph['arguments']:
            #     if 'eo:cloud_cover' in 
            #filter on bounding box (defined in lat/lon)
            spatial_extent={}
            spatial_extent['west']=node.graph['arguments']['spatial_extent']['west']
            spatial_extent['east']=node.graph['arguments']['spatial_extent']['east']
            spatial_extent['north']=node.graph['arguments']['spatial_extent']['north']
            spatial_extent['south']=node.graph['arguments']['spatial_extent']['south']
            if 'crs' in node.graph['arguments']['spatial_extent']:
                spatial_extent['crs']=node.graph['arguments']['spatial_extent']['crs']
            if verbose:
                print(spatial_extent)
            # coll.filter_bbox(west=node.graph['arguments']['spatial_extent']['west'],
            #                  east=node.graph['arguments']['spatial_extent']['east'],
            #                  north=node.graph['arguments']['spatial_extent']['north'],
            #                  south=node.graph['arguments']['spatial_extent']['south'])
            #filter on dates:

            print("temporal_extent: {}".format(node.graph['arguments']['temporal_extent']))
            # daterange = [datetime.strptime(d, '%Y-%m-%dT%H:%M:%S') for d in node.graph['arguments']['temporal_extent']]
            daterange = [datetime.strptime(d,"%Y-%m-%dT%H:%M:%S.%fZ") for d in node.graph['arguments']['temporal_extent']]
            print("daterange: {}".format(daterange))
            # self.filter_daterange(dateString)
            # daterange = [datetime.strptime(d, '%Y-%m-%d') for d in node.graph['arguments']['temporal_extent']]
            # dateString=[single_date.strftime('%Y-%m-%dT%H:%M:%S') for single_date in daterange]
            # coll.filter_daterange(dateString)
            #make sure the following filters are called after filtering dates and bounding box)
            #filter spectral bands
            bands=None
            if 'bands' in node.graph['arguments']:
                bands=node.graph['arguments']['bands']
                # print("filter bands: {}".format(node.graph['arguments']['bands']))
                # coll.filter_bands(node.graph['arguments']['bands'])
            #define spatial and temporal resolution to load collection as data cube.
            resolution={}
            #todo: define spatial resolution
            resolution.update({'spatial':[10,10]})
            resolution.update({'temporal':timedelta(1)})
            #todo: define projection t_srs?
            #todo: define appropriate output data type?
            print("daterange is {}".format(daterange))
            # jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands,resolution=resolution,t_srs=3857,otype='GDT_Float32',rule='overwrite', nodata=0)
            #todo: support empty projection t_srs to keep original?
            jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands, properties=properties,resolution=resolution,t_srs=32632,otype='GDT_Float32',rule='overwrite', nodata=0)
            #test
            print("return Jim {}".format(jim[node.id]))
            return jim[node.id]
        elif node.graph['process_id'] == 'array_element':
            if 'index' in node.graph['arguments']:
                if verbose:
                    print("array_element with index {}".format(node.graph['arguments']['index']))
                if jim[node.graph['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return jim[node.id]
                else:
                    #todo: support other type of indexing
                    # result=Cube(jim[node.graph['arguments']['data']['from_node']])
                    jim[node.id]=pj.geometry.cropBand(jim[node.graph['arguments']['data']['from_node']],node.graph['arguments']['index'])
                    if jim[node.id].properties.nrOfBand() > 1:
                        raise AttributeError("Error: number of bands is {}".format(jim[node.id].properties.nrOfBand()))
                    return jim[node.id]
            else:
                raise AttributeError("Error: only index is supported for array_element")
        elif node.graph['process_id'] in ['sum','subtract','product','divide']:
            if verbose:
                print("arithmetic {}".format(node.graph['process_id']))
            jim[node.id]=None
            for data in node.graph['arguments']['data']:
                print("data is: {}".format(data))
                if isinstance(data,dict):
                    if verbose:
                        print("type of jim is {}".format(type(jim[data['from_node']])))
                    if jim[data['from_node']] is None:
                        jim[node.id]=None
                        return jim[node.id]
                    else:
                        value=jim[data['from_node']]
                else:
                    value=data
                if jim[node.id] is None:
                    jim[node.id]=value
                else:
                    if node.graph['process_id'] == 'sum':
                        jim[node.id]+=value
                    if node.graph['process_id'] == 'subtract':
                        jim[node.id]-=value
                    if node.graph['process_id'] == 'product':
                        #test
                        print(jim[node.id])
                        print(value)
                        jim[node.id]*=value
                    if node.graph['process_id'] == 'divide':
                        jim[node.id]/=value
            return jim[node.id]
        elif node.graph['process_id'] == 'reduce':
            if verbose:
                print("reducing {}".format(node.graph['arguments']['dimension']))
            if 'spectral' in node.graph['arguments']['dimension']:
            # if node.graph['arguments']['dimension'] == 'spectral' or node.graph['arguments']['dimension'] == 'spectral_bands':
                if jim[node.graph['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                if jim[node.graph['arguments']['reducer']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                else:
                    jim[node.id]=jim[node.graph['arguments']['reducer']['from_node']]
                    return jim[node.id]
            elif node.graph['arguments']['dimension'] == 'temporal':
                if jim[node.graph['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                reducer_node=graph.nodes[node.graph['arguments']['reducer']['from_node']]
                if verbose:
                    print("node is: {}".format(node.graph))
                    print("reducer node is: {}".format(reducer_node))
                if jim[node.graph['arguments']['reducer']['from_node']] is None:
                    rule=reducer_node.graph['process_id']
                    if verbose:
                        print("reducer graph is: {}".format(reducer_node.graph))
                        print("rule: {}".format(rule))
                    jim[reducer_node.id]=pj.Jim(jim[node.graph['arguments']['data']['from_node']])
                    jim[reducer_node.id].geometry.reducePlane(rule)
                    if jim[reducer_node.id] is not None:
                        jim[node.id]=jim[reducer_node.id]
                        return jim[node.id]
                    else:
                        raise ValueError("Error: jim_reduced is False")
                else:
                    jim[node.id]=jim[node.graph['arguments']['data']['from_node']]
                    return jim[node.id]
        elif node.graph['process_id'] == 'aggregate_polygon':
            if verbose:
                print("aggregating polygon")
            if jim[node.graph['arguments']['data']['from_node']] is None:
                return None
            reducer_node=graph.nodes[node.graph['arguments']['reducer']['from_node']]
            if verbose:
                print("node is: {}".format(node.graph))
                print("reducer node is: {}".format(reducer_node))
            if jim[node.graph['arguments']['reducer']['from_node']] is None:
                rule=reducer_node.graph['process_id']
                if verbose:
                    print("reducer graph is: {}".format(reducer_node.graph))
                    print("rule: {}".format(rule))

                for points in node.graph['arguments']['polygons']['coordinates']:
                    wktstring=node.graph['arguments']['polygons']['type']
                    wktstring+=' (('
                    wktstring+=",".join(" ".join(str(coordinate) for coordinate in point) for point in points)
                    wktstring+='))'
                    invect=pj.JimVect(wkt=wktstring,output=os.path.join('/vsimem/invect.sqlite'))
                #todo: support multiple invect
                outvect=os.path.join('/vsimem',node.id+'.sqlite')
                jim[reducer_node.id]=jim[node.graph['arguments']['data']['from_node']].geometry.aggregate_vector(invect,rule,outvect,co=['OVERWRITE=TRUE'])

                if jim[reducer_node.id] is not None:
                    jim[node.id]=jim[reducer_node.id]
                    return jim[node.id]
                else:
                    raise ValueError("Error: could not aggregate polygon")
            else:
                # jim[node['arguments']['data']['from_node']].dimension['temporal']=node.name
                return jim[node.graph['arguments']['data']['from_node']]
        elif node.graph['process_id'] in ['min', 'max', 'mean', 'median', 'stdev', 'centroid']:#callback function
            if verbose:
                print("we are in callback function with {}".format(node.graph['process_id']))
            return None

    def process(self, graph):
        verbose=True
        jim={}
        if verbose:
            print("initialize")

        for node in graph.nodes.values():
            jim[node.id]=None
        finished=False
        if verbose:
            print("starting process")
        while not finished:
            if verbose:
                print("finished is: {}".format(finished))
            finished=True
            for node in graph.nodes.values():
                print("processing node {}".format(node.id))
                if jim[node.id] is not None:
                    if verbose:
                        print("skipping node {} that was already calculated".format(node.id))
                    continue
                else:
                    self.processNode(graph, node.id, jim)
                if jim[node.id] is not None:
                    if verbose:
                        print("calculated result for {}".format(node.id))
                        print("type of jim returned: {}".format(type(jim[node.id])))
                    if isinstance(jim[node.id],pj.Jim):
                        if verbose:
                            print("number of planes returned: {}".format(jim[node.id].properties.nrOfPlane()))
                            print("number of bands returned: {}".format(jim[node.id].properties.nrOfBand()))
                    elif isinstance(jim[node.id],pj.JimVect):
                        if verbose:
                            print("number of features calculated: {}".format(jim[node.id].properties.getFeatureCount()))
                    else:
                        raise TypeError("Error: result should either be Jim or JimVect")
                else:
                    if verbose:
                        print("could not calculate result for node {}".format(node.id))
                    continue

            ntodo=0;
            for node in graph.nodes.values():
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

        #todo: garbage collect jim (delete all Jim instances for without references from_node

