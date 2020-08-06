from datetime import time, timedelta, datetime
import dateutil.parser
import os
import json
from openeo_pg_parser import graph
import gc
import inspect
import numpy as np
#import graph
from jeolib.collection import Collection
from jeolib.cube import Cube
import pyjeo as pj

verbose=True

class BackEnd:
    def __init__(self, name=None, user=None):
        self.name = name
        self.user = user

    def processNode(self, agraph, nodeid, jim, tileindex=None, tiletotal=None, virtual=False):
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
                if self.user is not None:
                    #pathname=os.path.join('/eos/jeodpp/home/users/',self.user,node.id)
                    pathname=os.path.join('/home',self.user,node.id)
                else:
                    pathname=os.path.join('/tmp',node.id)
                if tileindex is not None and tiletotal is not None:
                    pathname += str(tileindex)+'_'+str(tiletotal)
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
                                jimplane=Cube(pj.geometry.cropPlane(jim[node.id],iplane))
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
            properties=node.content['arguments'].get('properties')

            spatiallyfiltered = False
            mgrs = None
            for property in properties:
                if node.content['arguments']['properties'][property].get('from_node') is not None:
                    property_node=agraph[node.content['arguments']['properties'][property]['from_node']]
                else:
                    property_node=None
                if 'cloud_cover' in property:
                    minCloud = property_node.content['arguments'].get('min',0)
                    maxCloud = property_node.content['arguments'].get('max',100)
                    coll.filterOn('cloudCoverPercentage','<'+str(maxCloud))
                    coll.filterOn('cloudCoverPercentage','>'+str(minCloud))
                if 'mgrs' in property:
                    mgrs = property_node.content['arguments'].get('y')
                    if mgrs is not None:
                        if property_node.content['process_id'] == 'eq':
                            coll.filterOn('mgrs',str(mgrs))
                        elif property_node.content['process_id'] == 'neq':
                            coll.filterOn('mgrs','<>'+str(mgrs))
                        else:
                            raise AttributeError("Error: process_id {} not supported for property {}".format(property_node.content['process_id'],property))
                    spatiallyFiltered=True
                if 'platform' in property:
                    platform = property_node.content['arguments'].get('y')
                    if platform is not None:
                        if property_node.content['process_id'] == 'eq':
                            coll.filterOn('platform','='+str(platform))
                        elif property_node.content['process_id'] == 'neq':
                            coll.filterOn('platform','<>'+str(platform))
                        else:
                            raise AttributeError("Error: process_id {} not supported for property {}".format(property_node.content['process_id'],property))
                if property_node is not None:
                    jim[property_node.id]=True

            #filter on bounding box (defined in lat/lon)
            west = None
            east = None
            north = None
            south = None
            spatial_extent = node.content['arguments'].get('spatial_extent')
            crs = None

            features = None
            if spatial_extent is not None:
              west = spatial_extent.get('west')
              east = spatial_extent.get('east')
              north = spatial_extent.get('north')
              south = nodeial_extent.get('south')
              #crs = spatial_extent'get('crs')
              geometries = node.content['arguments'].get('spatial_extent').get('geometries')
              if geometries is not None:
                  features = node.content['arguments'].get('spatial_extent')
                  print('features {}'.format(features))
                  features=json.dumps(features)
                  print('features {}'.format(features))
                  v1 = pj.JimVect(features)
                  print(v1.properties.getFeatureCount())

            if mgrs is not None and tileindex is not None and tiletotal is not None:
                attribute="Name="+'\''+str(mgrs)+'\''
                print("attribute: {}".format(attribute))
                fn='/eos/jeodpp/data/base/GeographicalGridSystems/GLOBAL/MGRS/S2/LATEST/Data/Shapefile/S2grid2D.shp'
                v1=pj.JimVect(pj.JimVect(fn,attributeFilter=attribute),output='/vsimem/v1',co=['OVERWRITE=YES'])
                v1.io.write()
                bbox = v1.properties.getBBox()
                west = bbox[0]
                north = bbox[1]
                east = bbox[2]
                south = bbox[3]

            if west is not None and east is not None and north is not None and south is not None:
                coll.filter_bbox(west=west,
                                 east=east,
                                 north=north,
                                 south=south,
                                 regions=features,
                                 crs=crs,
                                 tileindex=tileindex,
                                 tiletotal=tiletotal)
                spatiallyFiltered = True
            if not spatiallyFiltered:
                raise AttributeError("Error: {} bounding box or mgrs must be defined to filter collection".format(type(jim[node.id])))

            #filter on dates:

            print("temporal_extent: {}".format(node.content['arguments']['temporal_extent']))
            daterange = [dateutil.parser.parse(d) for d in node.content['arguments']['temporal_extent']]
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
                bandindex=node.content['arguments']['index']
                bandname=jim[node.content['arguments']['data']['from_node']].dimension['band'][bandindex]
            elif 'label' in node.content['arguments']:
                bandname=node.content['arguments']['label']
                if verbose:
                    print("array_element with label {}".format(bandname))
                bandindex=jim[node.content['arguments']['data']['from_node']].dimension['band'].index(bandname)
            else:
                raise AttributeError("Error: only index or label is supported for array_element")
            if verbose:
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
        elif node.content['process_id'] == 'apply':
            if verbose:
                print(node)
                print("apply {}".format(node.content['description']))
            if jim[node.content['arguments']['data']['from_node']] is None:
                jim[node.id]=None
                return[node.id]
            process_node=agraph[node.content['arguments']['process']['from_node']]
            if verbose:
                print("node is: {}".format(node.content))
                print("process node is: {}".format(process_node))
            if jim[process_node.id] is None:
                if process_node.content['process_id'] == 'linear_scale_range':
                    inputMin=process_node.content['arguments'].get('inputMin',0)
                    inputMax=process_node.content['arguments'].get('inputMax')
                    if inputMax is None:
                        raise ValueError("Error: inputMax not set")
                    outputMin=process_node.content['arguments'].get('outputMin',0)
                    outputMax=process_node.content['arguments'].get('outputMax',255)
                    #todo: handle data types
                    if jim[process_node.content['arguments']['x']['from_node']] is None:
                        jim[node.id]=None
                        return[node.id]
                    jim[process_node.id] = Cube(jim[process_node.content['arguments']['x']['from_node']])
                    jim[process_node.id]-=inputMin
                    jim[process_node.id]/=(inputMax-inputMin)
                    jim[process_node.id]*=(outputMax-outputMin)
                    jim[process_node.id]+=outputMin
                elif process_node.content['process_id'] == 'abs':
                    if jim[process_node.content['arguments']['x']['from_node']] is None:
                        jim[node.id]=None
                        return[node.id]
                    jim[process_node.id] = Cube(abs(jim[process_node.content['arguments']['x']['from_node']]))
            jim[node.id]=jim[process_node.id]
            return jim[node.id]
        elif node.content['process_id'] in ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'sum', 'subtract', 'product', 'divide']:
            if verbose:
                print(node)
                print("eq {}".format(node.content.get('description')))

            jim[node.id]=None
            for argument in node.content['arguments'].values():
                if isinstance(argument,dict):
                    if verbose:
                        print("type of jim is {}".format(type(jim[argument['from_node']])))
                    if jim[argument['from_node']] is None:
                        jim[node.id]=None
                        return jim[node.id]
                    else:
                        value=jim[argument['from_node']]
                else:
                    value=argument
                #test
                print("argument is {}".format(type(argument),argument))
                print("value is of type {}, {}".format(type(value),value))
                if jim[node.id] is None:
                    jim[node.id]=value
                else:
                    if node.content['process_id'] == 'eq':
                        jim[node.id]=(jim[node.id]==value)
                    elif node.content['process_id'] == 'neq':
                        jim[node.id]=(jim[node.id]!=value)
                    elif node.content['process_id'] == 'gt':
                        jim[node.id]=(jim[node.id]>value)
                    elif node.content['process_id'] == 'gte':
                        jim[node.id]=(jim[node.id]>=value)
                    elif node.content['process_id'] == 'lt':
                        jim[node.id]=(jim[node.id]<value)
                    elif node.content['process_id'] == 'lte':
                        jim[node.id]=(jim[node.id]<=value)
                    elif node.content['process_id'] == 'sum':
                        jim[node.id]+=value
                    elif node.content['process_id'] == 'subtract':
                        jim[node.id]-=value
                    elif node.content['process_id'] == 'product':
                        jim[node.id]*=value
                    elif node.content['process_id'] == 'divide':
                        #test
                        print(jim[node.id].np())
                        print(value)
                        jim[node.id]/=value
                    else:
                        raise TypeError("Error: arithmetic {} not implemented".format(node.content['process_id']))
            return jim[node.id]
        elif node.content['process_id'] == "mask":
            if verbose:
                print(node)
                print("eq {}".format(node.content.get('description')))

            jim[node.id]=None
            data = node.content['arguments'].get('data')
            mask = node.content['arguments'].get('mask')
            replacement = node.content['arguments'].get('replacement')
            if isinstance(mask,dict):
                if verbose:
                    print("type of data is {}".format(type(jim[mask['from_node']])))
                    if jim[mask['from_node']] is None:
                        jim[node.id]=None
                        return jim[node.id]
                    else:
                        mask=jim[mask['from_node']]
            if isinstance(data,dict):
                if verbose:
                    print("type of data is {}".format(type(jim[data['from_node']])))
                    if jim[data['from_node']] is None:
                        jim[node.id]=None
                        return jim[node.id]
                    else:
                        jim[node.id]=jim[data['from_node']]
            if replacement is not None:
                jim[node.id][mask]=replacement
            else:
                jim[node.id][mask]=0
            return jim[node.id]
        # elif node.content['process_id'] in ['sum','subtract','product','divide']:
        #     if verbose:
        #         print("arithmetic {}".format(node.content['process_id']))
        #     jim[node.id]=None
        #     for data in node.content['arguments']['data']:
        #         print("data is: {}".format(data))
        #         if isinstance(data,dict):
        #             if verbose:
        #                 print("type of jim is {}".format(type(jim[data['from_node']])))
        #             if jim[data['from_node']] is None:
        #                 jim[node.id]=None
        #                 return jim[node.id]
        #             else:
        #                 value=jim[data['from_node']]
        #         else:
        #             value=data
        #         #value should be of type pj.Jim

        #         print("value is of type {}".format(type(value)))
        #         if jim[node.id] is None:
        #             jim[node.id]=value
        #         else:
        #             if node.content['process_id'] == 'sum':
        #                 jim[node.id]+=value
        #             elif node.content['process_id'] == 'subtract':
        #                 jim[node.id]-=value
        #             elif node.content['process_id'] == 'product':
        #                 jim[node.id]*=value
        #             elif node.content['process_id'] == 'divide':
        #                 #test
        #                 print(jim[node.id].np())
        #                 print(value)
        #                 jim[node.id]/=value
        #             else:
        #                 raise TypeError("Error: arithmetic {} not implemented".format(node.content['process_id']))
        #     return jim[node.id]
        elif node.content['process_id'] == 'reduce_dimension':
            if verbose:
                print(node)
                print("reducing {}".format(node.content['arguments']['dimension']))
            if jim[node.content['arguments']['data']['from_node']] is None:
                jim[node.id]=None
                return[node.id]
            reducer_node=agraph[node.content['arguments']['reducer']['from_node']]
            if verbose:
                print("node is: {}".format(node.content))
                print("reducer node is: {}".format(reducer_node))
            if jim[reducer_node.id] is None:
                if node.content['arguments']['dimension'] in ['temporal', 'time', 't']:
                    # cube=Cube(jim[reducer_node.content['arguments']['data']['from_node']])
                    jim[reducer_node.id]=Cube(jim[reducer_node.content['arguments']['data']['from_node']])
                    if jim[reducer_node.id] is None:
                        jim[node.id]=jim[reducer_node.id]
                        return[node.id]
                    rule=reducer_node.content['process_id']
                    if rule in ['max', 'mean', 'median', 'min']:
                        # jim[reducer_node.id] = pj.geometry.reducePlane(cube,rule=reducer_node.content['process_id'])
                        # jim[reducer_node.id]=Cube(jim[node.content['arguments']['data']['from_node']])
                        jim[reducer_node.id].geometry.reducePlane(rule=rule)
                    elif reducer_node.content['process_id'] == 'first':
                        jim[reducer_node.id].geometry.cropPlane(0)
                    elif reducer_node.content['process_id'] == 'last':
                        jim[reducer_node.id].geometry.cropPlane(-1)
                elif node.content['arguments']['dimension'] in ['spectral', 'bands', 'b']:
                    if reducer_node.content['process_id'] in ['ndvi', 'normalized_difference']:
                        nir = jim[reducer_node.content['arguments']['x']['from_node']]
                        if nir is None:
                            jim[node.id]=None
                            return[node.id]
                        red = jim[reducer_node.content['arguments']['y']['from_node']]
                        if nir is None:
                            jim[node.id]=None
                            return[node.id]
                        jim[reducer_node.id] = Cube(pj.pixops.convert(nir,'GDT_Float32'))
                        nirnp=nir.np().astype(np.float)
                        rednp=red.np().astype(np.float)
                        ndvi=(nirnp-rednp)/(nirnp+rednp)
                        ndvi[np.isnan(ndvi)]=0
                        jim[reducer_node.id].np()[:]=ndvi
                        jim[reducer_node.id].dimension['band']=['nd']
                        jim[reducer_node.id].dimension['temporal']=nir.dimension['temporal']
                    elif reducer_node.content['process_id'] == 'first':
                        jim[reducer_node.id]=Cube(reducer_node.content['arguments']['data']['from_node'])
                        # cube=jim[reducer_node.content['arguments']['data']['from_node']]
                        if jim[reducer_node.id] is None:
                            jim[node.id]=None
                            return[node.id]
                        elif isinstance(cube,pj.JimVect):
                            raise TypeError("Error: reduce not implemented for JimVect")
                        elif isinstance(cube,Collection):
                            raise TypeError("Error: reduce not implemented for Collection")
                        jim[reducer_node.id].geometry.cropBand(0)
                    elif reducer_node.content['process_id'] == 'last':
                        # cube=jim[reducer_node.content['arguments']['data']['from_node']]
                        jim[reducer_node.id].geometry.cropBand(-1)
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
                        jim[reducer_node.id]=Cube(jim[node.content['arguments']['data']['from_node']])
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
        if node.content['process_id'] == 'run_udf':
            if node.content['arguments']['data']['from_node'] not in jim:
                print("cannot run udf yet")
                jim[node.id]=None
                return jim[node.id]
            if jim[node.content['arguments']['data']['from_node']] is None:
                print("cannot run udf yet")
                jim[node.id]=None
                return jim[node.id]
            else:
                print("running udf")

                #find function name
                udfDefinition = node.content['arguments']['udf']
                udf_name = udfDefinition[udfDefinition.index('def ')+4:udfDefinition.index('(')].strip()
                print("udf_name is {}".format(udf_name))
                exec(udfDefinition)
                sig = inspect.signature(eval(udf_name))
                if len(sig.parameters) != 1:
                    raise TypeError("Error: udf definition must have single parameter")
                for key in sig.parameters:
                    imgname = key
                params = sig.parameters.keys()
                if 'import' in udfDefinition:
                    raise TypeError("Error: No import allowed in server-side execution functions")

                if 'os.path' in udfDefinition or 'os.system' in udfDefinition or 'os.popen' in udfDefinition:
                    raise TypeError("No os module functions allowed in server-side execution functions!")

                if 'sys' in udfDefinition:
                    raise TypeError("No sys module functions allowed in server-side execution functions!")

                if 'subprocess' in udfDefinition:
                    raise TypeError("No subprocess call allowed in server-side execution functions!")

                if 'eval' in udfDefinition:
                    raise TypeError("No eval call allowed in server-side execution functions!")

                if 'exec' in udfDefinition or 'execfile' in udfDefinition:
                    raise TypeError("No exec call allowed in server-side execution functions!")

                jim[node.id]=eval(udf_name)(jim[node.content['arguments']['data']['from_node']])
                if not isinstance(jim[node.id],pj.Jim):
                    raise TypeError("Error: udf returns {}, must be of type Jim".format(type(jim[node.id])))
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
                    geometries = node.content['arguments']['geometries']
                    geometryType = geometries['type']
                    if geometryType == 'FeatureCollection':
                        print(json.dumps(geometries))
                        print(geometries)
                        invect=pj.JimVect(json.dumps(geometries),verbose=1)
                        print(invect.np().shape)
                        print(invect.np())
                        # ds=gdal.OpenEx(geojson)
                        # lyr = ds.GetLayer()
                    elif geometryType == 'file':
                        invect=pj.JimVect(geometries['path'])
                        print(invect.np().shape)
                        print(invect.np())
                elif 'file' in node.content['arguments']:
                    raise ValueError("Error: not implemented yet")
                    #todo: handle vector files...
                else:
                    raise ValueError("Error: only polygons supported in geojson format")
                if 'context' in node.content['arguments']:
                    buffer = node.content['arguments']['context'].get('buffer')
                    srcnodata = node.content['arguments']['context'].get('srcnodata')
                if srcnodata is None:
                    srcnodata = 0
                # for points in node.content['arguments']['polygons']['coordinates']:
                #     wktstring=node.content['arguments']['polygons']['type']
                #     wktstring+=' (('
                #     wktstring+=",".join(" ".join(str(coordinate) for coordinate in point) for point in points)
                #     wktstring+='))'
                # invect=pj.JimVect(wkt=wktstring,output=os.path.join('/vsimem/invect.sqlite'))
                #todo: support multiple invect
                outvect=os.path.join('/vsimem',node.id+'.sqlite')

                if isinstance(jim[node.content['arguments']['data']['from_node']],pj.Jim):
                    print("we have a Jim")
                    times=jim[node.content['arguments']['data']['from_node']].dimension['temporal']
                    planename=[t.strftime('%Y%m%d') for t in times]
                    bandname=jim[node.content['arguments']['data']['from_node']].dimension['band']
                    #test
                    #jim[node.content['arguments']['data']['from_node']].io.write('/tmp/test.tif')
                    #invect.io.write('/tmp/test.sqlite',co=['OVERWRITE=TRUE'])

                    if buffer is not None:
                        jim[reducer_node.id]=pj.geometry.extract(invect, jim[node.content['arguments']['data']['from_node']], outvect, rule, bandname=bandname, planename=planename, co=['OVERWRITE=TRUE'], srcnodata=srcnodata, buffer=buffer)
                    else:
                        jim[reducer_node.id]=pj.geometry.extract(invect, jim[node.content['arguments']['data']['from_node']], outvect, rule, bandname=bandname, planename=planename, co=['OVERWRITE=TRUE'], srcnodata=srcnodata)
                elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
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

    def process(self, agraph, tileindex=None, tiletotal=None, virtual=False):
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
                    elif isinstance(jim[node.id],bool):
                        if verbose:
                            print("Node is intermediate result")
                    else:
                        raise TypeError("Error: result should either be Jim or JimVect")
                    for ancestor in node.ancestors().nodes:
                        collectGarbage = True
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
