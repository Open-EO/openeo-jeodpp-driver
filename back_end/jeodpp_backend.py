from datetime import time, timedelta, datetime
from osgeo import gdal
import os
import json
#import graph
from jeolib import Collection
import pyjeo as pj

class BackEnd:
    def __init__(self, name=None):
        self.name = name

    def processNode(self, graph, nodeid, jim, virtual=False):
        verbose=True
        print('graph.nodes: {}'.format(graph.nodes))
        #node=graph.nodes[nodeid]
        node=graph[nodeid]
        if node.content['process_id'] == 'save_result':
            if node.content['arguments']['data']['from_node'] not in jim:
                print("cannot save result yet")
                jim[node.id]=None
                return jim[node.id]
            if jim[node.content['arguments']['data']['from_node']]:
                print("saving result")
                jim[node.id]=jim[node.content['arguments']['data']['from_node']]
                pathname=os.path.join('/tmp',node.id)
                if isinstance(jim[node.id],pj.Jim):
                    # Create target Directory if don't exist
                    if not os.path.exists(pathname):
                        os.mkdir(pathname)
                        print("Directory {} created".format(pathname))
                    else:
                        print("Directory {} already exists".format(pathname))
                    #to save as multi-spectral GeoTIFF, 1 file per acquisition time
                    print("jim has {} planes".format(jim[node.id].properties.nrOfPlane()))
                    if jim[node.id].properties.nrOfPlane() > 1:
                        if jim[node.id].properties.nrOfBand() > 1:
                            for iplane, theDate in enumerate(jim[node.id].dimension['temporal']):
                                print("cropPlane {}".format(iplane))
                                jimplane=pj.geometry.cropPlane(jim[node.id],iplane)
                                jimplane.properties.setNoDataVals(0)
                                jimplane.io.write(os.path.join(pathname,theDate.strftime('%Y%m%d')+'.tif'),co=['COMPRESS=LZW','TILED=YES'])
                            return jim[node.id]
                        else:
                            jim[node.id].geometry.plane2band()
                    jim[node.id].io.write(pathname+'.tif',co=['COMPRESS=LZW','TILED=YES'])
                    return jim[node.id]
                elif isinstance(jim[node.id],pj.JimVect):
                    print("saved result: {}".format(jim[node.id].np()))
                    jim[node.id].io.write(pathname+'.sqlite')
                elif isinstance(jim[node.id],Collection):
                    raise TypeError("Error: {} virtual cube not implemented yet".format(type(jim[node.id])))
                else:
                    raise TypeError("Error: {} type not supported for writing".format(type(jim[node.id])))
            else:
                print("cannot save result yet")
                jim[node.id]=None
                return jim[node.id]
        elif node.content['process_id'] == 'load_collection':
            if verbose:
                print("load_collection")
            coll=Collection()
            coll.filterOn('productType',node.content['arguments']['id'])
            properties={}
            #test
            # properties['cloudCoverPercentage']='<10'
            # if 'properties' in node.content['arguments']:
            #     if 'eo:cloud_cover' in
            #filter on bounding box (defined in lat/lon)
            spatial_extent={}
            spatial_extent['west']=node.content['arguments']['spatial_extent']['west']
            spatial_extent['east']=node.content['arguments']['spatial_extent']['east']
            spatial_extent['north']=node.content['arguments']['spatial_extent']['north']
            spatial_extent['south']=node.content['arguments']['spatial_extent']['south']
            if 'crs' in node.content['arguments']['spatial_extent']:
                spatial_extent['crs']=node.content['arguments']['spatial_extent']['crs']
            if verbose:
                print(spatial_extent)
            coll.filter_bbox(west=node.content['arguments']['spatial_extent']['west'],
                             east=node.content['arguments']['spatial_extent']['east'],
                             north=node.content['arguments']['spatial_extent']['north'],
                             south=node.content['arguments']['spatial_extent']['south'])
            #filter on dates:

            print("temporal_extent: {}".format(node.content['arguments']['temporal_extent']))
            # daterange = [datetime.strptime(d, '%Y-%m-%dT%H:%M:%S') for d in node.content['arguments']['temporal_extent']]
            try:
                daterange = [datetime.strptime(d,"%Y-%m-%dT%H:%M:%S.%fZ") for d in node.content['arguments']['temporal_extent']]
            except ValueError:
                daterange = [datetime.strptime(d+"T00:00:00.000Z","%Y-%m-%dT%H:%M:%S.%fZ") for d in node.content['arguments']['temporal_extent']]
            print("daterange: {}".format(daterange))
            # self.filter_daterange(dateString)
            #daterange = [datetime.strptime(d, '%Y-%m-%d') for d in node.content['arguments']['temporal_extent']]
            dateString=[single_date.strftime('%Y-%m-%dT%H:%M:%S') for single_date in daterange]
            print('dateString: {}'.format(dateString))
            coll.filter_daterange(dateString)
            #make sure the following filters are called after filtering dates and bounding box)
            #filter spectral bands
            bands=None
            if 'bands' in node.content['arguments']:
                bands=node.content['arguments']['bands']
                print("filter bands: {}".format(node.content['arguments']['bands']))
                coll.filter_bands(node.content['arguments']['bands'])
            #define spatial and temporal resolution to load collection as data cube.
            resolution={}
            #todo: define spatial resolution
            #test
            resolution.update({'spatial':[10,10]})
            resolution.update({'temporal':timedelta(1)})
            #todo: define projection t_srs?
            #todo: define appropriate output data type?
            print("daterange is {}".format(daterange))
            # jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands,resolution=resolution,t_srs=3857,otype='GDT_Float32',rule='overwrite', nodata=0)
            #todo: support empty projection t_srs to keep original?
            #test
            #jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands, properties=properties,resolution=resolution,t_srs=32632,otype='GDT_Float32',rule='overwrite', nodata=0)
            if virtual:
                jim[node.id]=coll
            else:
                jim[node.id]=coll.load_collection(t_srs=None,resolution=resolution,bands=bands, otype='GDT_Float32',rule='overwrite', nodata=0)
            # jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands, properties=properties,resolution=resolution,t_srs=None,otype='GDT_Float32',rule='overwrite', nodata=0)
            #test
            if verbose:
                print("return Jim {}".format(jim[node.id]))
            return jim[node.id]
        elif node.content['process_id'] == 'array_element':
            if 'index' in node.content['arguments']:
                if verbose:
                    print("array_element with index {}".format(node.content['arguments']['index']))
                if jim[node.content['arguments']['data']['from_parameter']] is None:
                    jim[node.id]=None
                    return jim[node.id]
                else:
                    if isinstance(jim[node.content['arguments']['data']['from_parameter']],pj.Jim):
                        #todo: support other type of indexing
                        # result=Cube(jim[node.content['arguments']['data']['from_node']])
                        jim[node.id]=pj.geometry.cropBand(jim[node.content['arguments']['data']['from_node']],node.content['arguments']['index'])
                        if jim[node.id].properties.nrOfBand() > 1:
                            raise AttributeError("Error: number of bands is {}".format(jim[node.id].properties.nrOfBand()))
                        return jim[node.id]
                    elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.JimVect):
                        raise TypeError("Error: {} array_element not implemented for JimVect".format(type(jim[node.id])))
                    elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
                        raise TypeError("Error: {} array element not implemented for Collection".format(type(jim[node.id])))
            else:
                raise AttributeError("Error: only index is supported for array_element")
        elif node.content['process_id'] in ['sum','subtract','product','divide']:
            if verbose:
                print("arithmetic {}".format(node.content['process_id']))
            jim[node.id]=None
            for data in node.content['arguments']['data']:
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
                #value should be of type pj.Jim

                if isinstance(value,pj.Jim):
                    if jim[node.id] is None:
                        jim[node.id]=value
                    else:
                        if node.content['process_id'] == 'sum':
                            jim[node.id]+=value
                        if node.content['process_id'] == 'subtract':
                            jim[node.id]-=value
                        if node.content['process_id'] == 'product':
                            #test
                            print(jim[node.id])
                            print(value)
                            jim[node.id]*=value
                        if node.content['process_id'] == 'divide':
                            jim[node.id]/=value
                elif isinstance(value,pj.JimVect):
                    raise TypeError("Error: arithmetic not implemented for JimVect")
                elif isinstance(value,Collection):
                    raise TypeError("Error: arithmetic not implemented for Collection")
            return jim[node.id]
        elif node.content['process_id'] == 'reduce_dimension':
            if verbose:
                print("reducing {}".format(node.content['arguments']['dimension']))
            if 'spectral' in node.content['arguments']['dimension']:
            # if node.content['arguments']['dimension'] == 'spectral' or node.content['arguments']['dimension'] == 'spectral_bands':
                if jim[node.content['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                if jim[node.content['arguments']['reducer']] is None:
                    jim[node.id]=None
                    return[node.id]
                else:
                    jim[node.id]=jim[node.content['arguments']['reducer']]
                    return jim[node.id]
        elif node.content['process_id'] == 'aggregate_temporal':
            #todo: not tested yet in openeo API v1.0
            if node.content['arguments']['dimension'] == 'temporal':
                if jim[node.content['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                reducer_node=graph[node.content['arguments']['reducer']]
                if verbose:
                    print("node is: {}".format(node.content))
                    print("reducer node is: {}".format(reducer_node))
                if jim[node.content['arguments']['reducer']] is None:
                    rule=reducer_node.content['process_id']
                    if verbose:
                        print("reducer graph is: {}".format(reducer_node.content))
                        print("rule: {}".format(rule))
                    if isinstance(jim[node.content['arguments']['data']['from_node']],pj.Jim):
                        jim[reducer_node.id]=pj.Jim(jim[node.content['arguments']['data']['from_node']])
                        jim[reducer_node.id].geometry.reducePlane(rule)
                        if jim[reducer_node.id] is not None:
                            jim[node.id]=jim[reducer_node.id]
                            return jim[node.id]
                        else:
                            raise ValueError("Error: jim_reduced is False")
                    elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.JimVect):
                        raise TypeError("Error: reduce not implemented for JimVect")
                    elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
                        raise TypeError("Error: reduce not implemented for Collection")
                else:
                    jim[node.id]=jim[node.content['arguments']['data']['from_node']]
                    return jim[node.id]
            else:
                raise TypeError("Error: reduce not implemented for dimension different than temporal")
        elif node.content['process_id'] == 'aggregate_spatial':
            if verbose:
                print("aggregating spatial")
            if jim[node.content['arguments']['data']['from_node']] is None:
                return None
            reducer_node=graph[node.content['arguments']['reducer']['from_node']]
            if verbose:
                print("node is: {}".format(node.content))
                print("reducer node is: {}".format(reducer_node))
            if jim[node.content['arguments']['reducer']['from_node']] is None:
                rule=reducer_node.content['process_id']
                if verbose:
                    print("reducer graph is: {}".format(reducer_node.content))
                    print("rule: {}".format(rule))
                if 'geometries' in node.content['arguments']:
                    geojson=node.content['arguments']['geometries']
                    print(json.dumps(geojson))
                    print(geojson)
                    invect=pj.JimVect(json.dumps(geojson),verbose=1)
                    print(invect.np().shape)
                    print(invect.np())
                    # ds=gdal.OpenEx(geojson)
                    # lyr = ds.GetLayer()
                else:
                    raise ValueError("Error: only polygons supported in geojson format")
                # for points in node.content['arguments']['polygons']['coordinates']:
                #     wktstring=node.content['arguments']['polygons']['type']
                #     wktstring+=' (('
                #     wktstring+=",".join(" ".join(str(coordinate) for coordinate in point) for point in points)
                #     wktstring+='))'
                # invect=pj.JimVect(wkt=wktstring,output=os.path.join('/vsimem/invect.sqlite'))
                #todo: support multiple invect
                outvect=os.path.join('/vsimem',node.id+'.sqlite')

                if isinstance(jim[node.content['arguments']['data']['from_node']],pj.Jim):
                    times=jim[node.content['arguments']['data']['from_node']].dimension['temporal']
                    planename=[t.strftime('%Y%m%d') for t in times]
                    bandname=jim[node.content['arguments']['data']['from_node']].dimension['band']
                    jim[reducer_node.id]=pj.geometry.extract(invect, jim[node.content['arguments']['data']['from_node']], outvect, rule, bandname=bandname, planename=planename, co=['OVERWRITE=TRUE'])
                elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
                    jim[reducer_node.id]=jim[node.content['arguments']['data']['from_node']].aggregate_spatial(invect, rule, outvect)
                elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.JimVect):
                    raise TypeError("Error: aggretate_spatial not implemented for JimVect")

                if jim[reducer_node.id] is not None:
                    jim[node.id]=jim[reducer_node.id]
                    print("output vector has {} features".format(jim[node.id].properties.getFeatureCount()))
                    print("output vector has fields: {}".format(jim[node.id].properties.getFieldNames()))
                    print('extracted vector: {}'.format(jim[node.id].np()))
                    jim[node.id].io.write()
                    return jim[node.id]
                else:
                    raise ValueError("Error: could not aggregate polygon")
            else:
                # jim[node['arguments']['data']['from_node']].dimension['temporal']=node.name
                return jim[node.content['arguments']['data']['from_node']]
        elif node.content['process_id'] in ['min', 'max', 'mean', 'median', 'stdev', 'centroid']:#callback function
            if verbose:
                print("we are in callback function with {}".format(node.content['process_id']))
            return None

    def process(self, graph, virtual=False):
        verbose=True
        jim={}
        if verbose:
            print("initialize")

        print("graph.nodes: {}".format(graph.nodes))
        #for node in graph.nodes.values():
        for node in graph.nodes:
            jim[node.id]=None
        finished=False
        if verbose:
            print("starting process")
        while not finished:
            if verbose:
                print("finished is: {}".format(finished))
            finished=True
            #for node in graph.nodes.values():
            for node in graph.nodes:
                print("processing node {}".format(node.id))
                if jim[node.id] is not None:
                    if verbose:
                        print("skipping node {} that was already calculated".format(node.id))
                    continue
                else:
                    self.processNode(graph, node.id, jim, virtual)
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
                    elif isinstance(jim[node.id],Collection):
                        if verbose:
                            print("Node is collection not loaded in memory")
                    else:
                        raise TypeError("Error: result should either be Jim or JimVect")
                else:
                    if verbose:
                        print("could not calculate result for node {}".format(node.id))
                    continue

            ntodo=0;
            #for node in graph.nodes.values():
            for node in graph.nodes:
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

