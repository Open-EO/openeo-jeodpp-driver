from datetime import time, timedelta, datetime
import os
import json
from openeo_pg_parser import graph
#import graph
from jeolib import Collection
import pyjeo as pj

verbose=True

class BackEnd:
    def __init__(self, name=None):
        self.name = name

    # def processCube(self, cube, agraph):
    #     for node in agraph.nodes:
    #         if not isinstance(node,graph.Node):
    #             print("convert node of type {}".format(type(node)))
    #             node = graph.Node(node)
    #             print("to {}".format(type(node)))
    #         if verbose:
    #             # print("processing node {}".format(node.id))
    #             print("node: {}".format(node))
    #             print(node.content['arguments']['data'])
    #         if isinstance(cube,pj.Jim):
    #             print("type of cube is: {}".format(type(cube)))
    #         elif isinstance(cube,pj.JimVect):
    #             raise TypeError("Error: {} array_element not implemented for JimVect")
    #         elif isinstance(cube,Collection):
    #             raise TypeError("Error: {} array element not implemented for Collection")
    #         if cube is None:
    #             print("Error: cube is None")
    #             return None
    #         if node.content['process_id'] == 'array_element':
    #             if 'index' in node.content['arguments']:
    #                 print("crop band {}".format(node.content['arguments']['index']))
    #                 return pj.geometry.cropBand(cube,node.content['arguments']['index'])
    #             else:
    #                 raise AttributeError("Error: only index is supported for array_element")
    #         elif node.content['process_id'] in ['all', 'any', 'count', 'first', 'last', 'max', 'mean', 'median', 'min', 'product', 'sd', 'sum', 'variance']:
    #             if node.content['process_id'] in ['max', 'mean', 'median', 'min']:
    #                 return pj.geometry.reducePlane(cube,rule=node.content['process_id'])
    #             elif node.content['process_id'] == 'first':
    #                 return pj.geometry.cropPlane(cube,0)
    #             elif node.content['process_id'] == 'last':
    #                 return pj.geometry.cropPlane(cube,-1)
    #             else:
    #                 raise ValueError("Error: reduction rule {} not implemented yet".format(node.content['process_id']))
    #         elif node.content['process_id'] in ['sum', 'subtract', 'product', 'divide']:
    #             for data in node.content['arguments']['data']:
    #             value=jim[data['from_node']]
    #             else:
    #                 value=data
    #             #value should be of type pj.Jim

    #             if isinstance(value,pj.Jim):
    #                 if jim[node.id] is None:
    #                     jim[node.id]=value
    #                 else:
    #                     if node.content['process_id'] == 'sum':
    #                         jim[node.id]+=value
    #                     if node.content['process_id'] == 'subtract':
    #                         jim[node.id]-=value
    #                     if node.content['process_id'] == 'product':
    #                         #test
    #                         print(jim[node.id])
    #                         print(value)
    #                         jim[node.id]*=value
    #                     if node.content['process_id'] == 'divide':
    #                         jim[node.id]/=value
    #             elif isinstance(value,pj.JimVect):
    #                 raise TypeError("Error: arithmetic not implemented for JimVect")
    #             elif isinstance(value,Collection):
    #                 raise TypeError("Error: arithmetic not implemented for Collection")
    #         else:
    #             raise ValueError("Error: reduction {} not supported".format(node['process_id']))

    def processNode(self, agraph, nodeid, jim, virtual=False):
        print('agraph.nodes: {}'.format(agraph.nodes))
        #node=graph.nodes[nodeid]
        node=agraph[nodeid]
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
            west = node.content['arguments']['spatial_extent'].get('west')
            east = node.content['arguments']['spatial_extent'].get('east')
            north = node.content['arguments']['spatial_extent'].get('north')
            south = node.content['arguments']['spatial_extent'].get('south')
            crs = node.content['arguments']['spatial_extent'].get('crs')
            features = node.content['arguments']['spatial_extent'].get('features')
            if features is not None:
                features=json.dumps(features),
            coll.filter_bbox(west=west,
                             east=east,
                             north=north,
                             south=south,
                             regions=features,
                             crs=crs)
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
                bandname=node.content['arguments']['index']
                #todo: get bandindex from bandname in bands
                bandindex=jim[node.content['arguments']['data']['from_node']].dimension['band'].index(bandname)
                if verbose:
                    print("array_element with name {}".format(bandname))
                    print("array_element with index {}".format(bandindex))
                if jim[node.content['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.Jim):
                    result=Cube(pj.geometry.cropBand(jim[node.content['arguments']['data']['from_node']],bandindex))
                    result.dimension['band']=bandname
                    jim[node.id]=result
                elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.JimVect):
                    raise TypeError("Error: {} array_element not implemented for JimVect".format(type(jim[node.id])))
                elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
                    raise TypeError("Error: {} array element not implemented for Collection".format(type(jim[node.id])))
                return jim[node.id]
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
                print(node)
                print("reducing {}".format(node.content['arguments']['dimension']))
                print("reducer: {}".format(node.content['arguments']['reducer']['process_graph']))
            if jim[node.content['arguments']['data']['from_node']] is None:
                jim[node.id]=None
                return[node.id]
            reducer_node=agraph[node.content['arguments']['reducer']['from_node']]
            if verbose:
                print("node is: {}".format(node.content))
                print("reducer node is: {}".format(reducer_node))
            if jim[reducer_node.id] is None:
                if node.content['arguments']['dimension'] in ['temporal', 'time', 't']:
                    cube=jim[reducer_node.contents['arguments']['data']['from_node']]
                    if cube is None:
                        jim[node.id]=None
                        return[node.id]
                    if reducer_node.content['process_id'] in ['max', 'mean', 'median', 'min']:
                        jim[reducer_node.id] = pj.geometry.reducePlane(cube,rule=node.content['process_id'])
                    elif reducer_node.content['process_id'] == 'first':
                        jim[reducer_node.id]=pj.geometry.cropPlane(cube,0)
                    elif reducer_node.content['process_id'] == 'last':
                        jim[reducer_node.id]=pj.geometry.cropPlane(cube,-1)
                    else:
                        raise ValueError("Error: temporal reduction rule not implemented")
                elif node.content['arguments']['dimension'] in ['spectral', 'bands', 'b']:
                    if reducer_node.content['process_id'] in ['ndvi', 'normalized_difference']:
                        nir = jim[['arguments']['x']['from_node']]
                        if nir is None:
                            jim[node.id]=None
                            return[node.id]
                        red = jim[['arguments']['y']['from_node']]
                        if nir is None:
                            jim[node.id]=None
                            return[node.id]
                        jim[reducer_node.id] = pj.pixops.convert(nir,'GDT_Float32')
                        nirnp=nir.np().astype(np.float)
                        rednp=red.np().astype(np.float)
                        ndvi=(nirnp-rednp)/(nirnp+rednp)
                        ndvi[np.isnan(ndvi)]=0
                        jim[reducer_node.id].np()[:]=ndvi
                    elif reducer_node.content['process_id'] == 'first':
                        cube=jim[reducer_node.contents['arguments']['data']['from_node']]
                        if cube is None:
                            jim[node.id]=None
                            return[node.id]
                        elif isinstance(cube,pj.JimVect):
                            raise TypeError("Error: reduce not implemented for JimVect")
                        elif isinstance(cube,Collection):
                            raise TypeError("Error: reduce not implemented for Collection")
                        jim[reducer_node.id]=pj.geometry.cropBand(cube,0)
                    elif reducer_node.content['process_id'] == 'last':
                        cube=jim[reducer_node.contents['arguments']['data']['from_node']]
                        if cube is None:
                            jim[reducer_node.id]=None
                        elif isinstance(cube,pj.JimVect):
                            raise TypeError("Error: reduce not implemented for JimVect")
                        elif isinstance(cube,Collection):
                            raise TypeError("Error: reduce not implemented for Collection")
                        if cube is None:
                            jim[reducer_node.id]=None
                        jim[reducer_node.id]=pj.geometry.cropBand(cube,-1)
                    else:
                        raise ValueError("Error: band reduction rule not implemented")
            jim[node.id]=jim[reducer_node.id]
            return jim[node.id]
        elif node.content['process_id'] == 'aggregate_temporal':
            #todo: not tested yet in openeo API v1.0
            if node.content['arguments']['dimension'] == 'temporal':
                if jim[node.content['arguments']['data']['from_node']] is None:
                    jim[node.id]=None
                    return[node.id]
                reducer_node=agraph[node.content['arguments']['reducer']['from_node']]
                if verbose:
                    print("node is: {}".format(node.content))
                    print("reducer node is: {}".format(reducer_node))
                if jim[reducer_node.id] is None:
                    rule=reducer_node.content['process_id']
                    if verbose:
                        print("reducer graph is: {}".format(reducer_node))
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
                    #test
                    jim[node.id]=jim[reducer_node.id]
                    #jim[node.id]=jim[node.content['arguments']['data']['from_node']]
                    return jim[node.id]
            else:
                raise TypeError("Error: reduce not implemented for dimension different than temporal")
        elif node.content['process_id'] == 'aggregate_spatial':
            if verbose:
                print("aggregating spatial")
            if jim[node.content['arguments']['data']['from_node']] is None:
                return None
            reducer_node=agraph[node.content['arguments']['reducer']['from_node']]
            if verbose:
                print("node is: {}".format(node.content))
                print("reducer node is: {}".format(reducer_node))
            # if jim[node.content['arguments']['reducer']['from_node']] is None:
            #test
            if jim[reducer_node.id] is None:
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

                if isinstance(jim[reducer_node.id],pj.Jim):
                    times=jim[node.content['arguments']['data']['from_node']].dimension['temporal']
                    planename=[t.strftime('%Y%m%d') for t in times]
                    bandname=jim[node.content['arguments']['data']['from_node']].dimension['band']
                    jim[reducer_node.id]=pj.geometry.extract(invect, jim[node.content['arguments']['data']['from_node']], outvect, rule, bandname=bandname, planename=planename, co=['OVERWRITE=TRUE'])
                elif isinstance(jim[reducer_node.id],Collection):
                    print("rule is: {}".format(rule))
                    jim[reducer_node.id]=jim[node.content['arguments']['data']['from_node']].aggregate_spatial(invect, rule, outvect)
                elif isinstance(jim[reducer_node.id],pj.JimVect):
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
                #test
                jim[node.id]=jim[reducer_node.id]
                return jim[node.id]
                #return jim[node.content['arguments']['data']['from_node']]
        # elif node.content['process_id'] in ['min', 'max', 'mean', 'median', 'stdev', 'centroid']:#callback function
        #     if verbose:
        #         print("we are in callback function with {}".format(node.content['process_id']))
        #     return None

    def process(self, agraph, virtual=False):
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
                    self.processNode(agraph, node.id, jim, virtual)
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

        #todo: garbage collect jim (delete all Jim instances for without references from_node

