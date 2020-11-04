from datetime import time, timedelta, datetime
import dateutil.parser
import os
import numpy as np
import inspect
from openeo_pg_parser import graph
import pyjeo as pj
from jeolib.collection import Collection
from jeolib.cube import Cube

def min(agraph, nodeid, jim):
    node = agraph[nodeid]
    return jim[node.id]

def max(agraph, nodeid, jim):
    node = agraph[nodeid]
    return jim[node.id]

def mean(agraph, nodeid, jim):
    node = agraph[nodeid]
    return jim[node.id]

def median(agraph, nodeid, jim):
    node = agraph[nodeid]
    return jim[node.id]

def between(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    properties={}

    spatiallyfiltered = False
    mgrs = None
    arguments=node.content.get('arguments')
    if arguments is None:
        raise AttributeError("Error: no arguments found")

    minValue = arguments.get('min')
    maxValue = arguments.get('max')
    if maxValue < minValue:
        jim[node.id]=False
        return jim[node.id]
    x = arguments.get('x')
    if x is not None:
        if isinstance(x,dict):
            if verbose:
                print("type of jim is {}".format(type(jim[x['from_node']])))
            if jim[x['from_node']] is None:
                jim[node.id]=None
                return jim[node.id]
            else:
                value=jim[x['from_node']]
        else:
            value=x
        if value < minValue:
            jim[node.id]=False
            return jim[node.id]
        else:
            exclude_max = arguments.get('exclude_max', False)
            if exclude_max:
                if value >= maxValue:
                    jim[node.id]=False
                    return jim[node.id]
                else:
                    jim[node.id]=True
                    return jim[node.id]
            elif value > maxValue:
                jim[node.id]=False
                return jim[node.id]
            else:
                jim[node.id]=True
                return jim[node.id]
    return jim[node.id]

def load_collection(agraph, nodeid, jim, tileindex=None, tiletotal=None, virtual=False):
    verbose = True
    node = agraph[nodeid]
    collectionId = node.content['arguments']['id'].split('.')
    if verbose:
        print("load_collection")
    coll=Collection(collectionId[0])
    if len(collectionId) > 1:
        coll.filterOn('productType',collectionId[1])
    properties={}

    spatiallyfiltered = False
    mgrs = None
    properties=node.content['arguments'].get('properties')
    if properties is not None:
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

    features = None
    crs = None
    if spatial_extent is not None:
        west = spatial_extent.get('west')
        east = spatial_extent.get('east')
        north = spatial_extent.get('north')
        south = spatial_extent.get('south')
        crs = spatial_extent.get('crs')
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
        if bands is not None:
            print("filter bands: {}".format(node.content['arguments']['bands']))
            coll.filter_bands(node.content['arguments']['bands'])
    #define spatial and temporal resolution to load collection as data cube.
    resolution={}
    #todo: define spatial resolution
    dx = 10
    dy = 10
    resolution.update({'spatial':[dx,dy]})
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
        jim[node.id]=coll.load_collection(t_srs=crs,resolution=resolution,bands=bands, otype='GDT_Float32',rule='overwrite', nodata=0)
    # jim[node.id]=coll.load_collection(spatial_extent,temporal_extent=daterange,bands=bands, properties=properties,resolution=resolution,t_srs=None,otype='GDT_Float32',rule='overwrite', nodata=0)
    #test
    if verbose:
        print("return Jim {}".format(jim[node.id]))
        print("temporal dimension: {}".format(jim[node.id].getDimension('temporal')))
        print("band dimension: {}".format(jim[node.id].getDimension('band')))
    return jim[node.id]

def save_result(agraph, nodeid, jim, pathname):
    verbose = True
    node = agraph[nodeid]
    if node.content['arguments']['data']['from_node'] not in jim:
        print("cannot save result yet")
        jim[node.id]=None
        return jim[node.id]
    if jim[node.content['arguments']['data']['from_node']]:
        print("saving result")
        jim[node.id]=jim[node.content['arguments']['data']['from_node']]
        if isinstance(jim[node.id],pj.Jim):
            #to save as multi-spectral GeoTIFF, 1 file per acquisition time
            print("jim has {} planes".format(jim[node.id].properties.nrOfPlane()))
            plane2band=False
            if jim[node.id].properties.nrOfPlane() > 1:
                if jim[node.id].properties.nrOfBand() > 1:
                    for iplane, theDate in enumerate(jim[node.id].dimension['temporal']):
                        print("cropPlane {}".format(iplane))
                        jimplane=Cube(pj.geometry.cropPlane(jim[node.id],iplane))
                        jimplane.properties.setNoDataVals(0)
                        jimplane.io.write(os.path.join(pathname,theDate.strftime('%Y%m%d')+'.tif'),co=['COMPRESS=LZW','TILED=YES'])
                    return jim[node.id]
                else:
                    plane2band=True
                    jim[node.id].geometry.plane2band()
            jim[node.id].io.write(pathname+'.tif',co=['COMPRESS=LZW','TILED=YES'])
            if plane2band:
                jim[node.id].geometry.band2plane()
            return jim[node.id]
        elif isinstance(jim[node.id],pj.JimVect):
            # print("saved result: {}".format(jim[node.id].np()))
            jim[node.id].io.write(pathname+'.sqlite')
        elif isinstance(jim[node.id],Collection):
            raise TypeError("Error: {} virtual cube not implemented yet".format(type(jim[node.id])))
        else:
            raise TypeError("Error: {} type not supported for writing".format(type(jim[node.id])))
    else:
        print("cannot save result yet")
        jim[node.id]=None
        return jim[node.id]

def filter_bands(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    bandindexes=[]
    if 'bands' in node.content['arguments']:
        bandnames = node.content['arguments'].get('bands')
        for bandname in bandnames:
            bandindex=jim[node.content['arguments']['data']['from_node']].dimension['band'].index(bandname)
            if verbose:
                print("array_element with label {}".format(bandname))
                print("array_element with index {}".format(bandindex))
            bandindexes.append(bandindex)
    if jim[node.content['arguments']['data']['from_node']] is None:
        jim[node.id]=None
    elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.Jim):
        jim[node.id]=Cube(pj.geometry.cropBand(jim[node.content['arguments']['data']['from_node']],bandindexes))
        jim[node.id].dimension['band']=bandnames
        return jim[node.id]
    elif isinstance(jim[node.content['arguments']['data']['from_node']],pj.JimVect):
        raise TypeError("Error: {} array_element not implemented for JimVect".format(type(jim[node.id])))
    elif isinstance(jim[node.content['arguments']['data']['from_node']],Collection):
        raise TypeError("Error: {} array element not implemented for Collection".format(type(jim[node.id])))
    else:
        raise AttributeError("Error: only bands is supported for filter_bands")

def filter_temporal(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    extent = node.content['arguments'].get('extent')
    data = jim[node.content['arguments']['data']['from_node']]
    if data is None:
        jim[node.id] = None
        return jim[node.id]
    if not isinstance(data,Cube):
        raise TypeError("Error: filter_temporal only implemented for Cube, not {}".format(type(jim[node.content['arguments']['data']['from_node']])))
    print("times in data: {}".format(data.getDimension('temporal')))
    jim[node.id] = Cube(data)
    #todo: should be solved in __init__ of Cube
    jim[node.id].setDimension('temporal',data.getDimension('temporal'))
    jim[node.id].setDimension('band',data.getDimension('band'))
    jim[node.id].setResolution('temporal',data.getResolution('temporal'))
    jim[node.id].setResolution('spatial',data.getResolution('spatial'))
    if len(extent) == 0:
        raise ValueError("extent should contain at least one date element, but got empty list: " + extent)
    dateFrom = extent[0]
    if len(extent) > 1:
        dateTo = extent[1]
    else:
        dateTo = None
    #todo: support datetime resolution finer than day
    if not isinstance(dateFrom,datetime):
        dateFrom=datetime.strptime(dateFrom, '%Y-%m-%d')
    if dateTo:
        if not isinstance(dateTo,datetime):
            dateTo=datetime.strptime(dateTo, '%Y-%m-%d')
    else:
        dateTo = dateFrom + jim[node.id].resolution['temporal']

    print("dateFrom: {}".format(dateFrom))
    print("dateTo: {}".format(dateTo))
    print("times in cube: {}".format(jim[node.id].getDimension('temporal')))
    filtered_temporal=[d for d in jim[node.id].getDimension('temporal') if d >= dateFrom and d < dateTo]
    print("filtered times: {}".format(filtered_temporal))
    planeindices=[jim[node.id].getDimension('temporal').index(d) for d in filtered_temporal]
    if len(planeindices) < 1:
        raise ValueError("Error: filter temporal found no match")
    # planeindices=[self.dimension['temporal'].index(d) for d in self.dimension['temporal'] if d >= dateFrom and d < dateTo]
    jim[node.id] = Cube(pj.geometry.cropPlane(jim[node.id], plane=planeindices))
    jim[node.id].setDimension('temporal',filtered_temporal)
    return jim[node.id]

    # jim[node.id] = Cube(jim[node.content['arguments']['data']['from_node']])
    # jim[node.id].filter_temporal(extent)
    # return jim[node.id]

    # jim[node.id]=Cube(pj.geometry.cropPlane(data, temporalindexes))
    # if len(extent) != 2:
    #     raise TypeError("Error: extent should be tuple with 2 elements (start, end), got {}".format(extent))
    # data = jim[node.content['arguments']['data']['from_node']]
    # if data is None:
    #     jim[node.id] = None
    #     return jim[node.id]
    # if not isinstance(jim[node.content['arguments']['data']['from_node']],Cube):
    #     raise TypeError("Error: filter_temporal only implemented for Cube, not {}".format(type(jim[node.content['arguments']['data']['from_node']])))
    # timeStrings = data.getDimension('temporal')
    # times = [datetime.strptime(ds,"%Y-%m-%dT%H:%M:%S") for ds in timeStrings]

    # startTime=datetime.strptime(extent[0],"%Y-%m-%dT%H:%M:%S")
    # endTime=datetime.strptime(extent[1].split('.')[0],"%Y-%m-%dT%H:%M:%S")
    # selected = [dt for dt in times if dt >= startTime and dt < endTime]
    # temporalindexes = [times.index(atime) for atime in selected]
    # jim[node.id]=Cube(pj.geometry.cropPlane(data, temporalindexes))
    # jim[node.id].dimension['temporal']=selected
    # return jim[node.id]

def ndvi(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    data = jim[node.content['arguments']['data']['from_node']]
    nir = node.content['arguments']['nir']
    red = node.content['arguments']['red']
    if nir is None:
        jim[node.id]=None
        return[node.id]
    red = jim[node.content['arguments']['y']['from_node']]
    if nir is None:
        jim[node.id]=None
        return[node.id]
    jim[node.id] = Cube(pj.pixops.convert(nir,'GDT_Float32'))
    nirnp=jim2np(jim[node.id], nir).astype(np.float)
    rednp=jim2np(jim[node.id], red).astype(np.float)
    ndvi=(nirnp-rednp)/(nirnp+rednp)
    ndvi[np.isnan(ndvi)]=0
    jim[node.id].np()[:]=ndvi
    jim[node.id].dimension['band']=['nd']
    jim[node.id].dimension['temporal']=nir.dimension['temporal']
    return jim[node.id]

def normalized_difference(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    nir = jim[node.content['arguments']['x']['from_node']]
    if nir is None:
        jim[node.id]=None
        return[node.id]
    red = jim[node.content['arguments']['y']['from_node']]
    if nir is None:
        jim[node.id]=None
        return[node.id]
    jim[node.id] = Cube(pj.pixops.convert(nir,'GDT_Float32'))
    nirnp=nir.np().astype(np.float)
    rednp=red.np().astype(np.float)
    ndvi=(nirnp-rednp)/(nirnp+rednp)
    ndvi[np.isnan(ndvi)]=0
    jim[node.id].np()[:]=ndvi
    jim[node.id].dimension['band']=['nd']
    jim[node.id].dimension['temporal']=nir.dimension['temporal']
    return jim[node.id]

def array_element(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    parent_node=node.parent_process.content
    data = jim[parent_node['arguments']['data']['from_node']]
    if 'index' in node.content['arguments']:
        bandindex=node.content['arguments']['index']
        bandname=data.dimension['band'][bandindex]
    elif 'label' in node.content['arguments']:
        bandname=node.content['arguments']['label']
        if verbose:
            print("array_element with label {}".format(bandname))
        bandindex=data.dimension['band'].index(bandname)
    else:
        raise AttributeError("Error: only index or label is supported for array_element")
    if verbose:
        print("array_element with index {}".format(bandindex))
    if data is None:
        jim[node.id]=None
    elif isinstance(data,pj.Jim):
        result=Cube(pj.geometry.cropBand(data,bandindex))
        result.dimension['band']=[bandname]
        jim[node.id]=result
    elif isinstance(data,pj.JimVect):
        raise TypeError("Error: {} array_element not implemented for JimVect".format(type(jim[node.id])))
    elif isinstance(data,Collection):
        raise TypeError("Error: {} array element not implemented for Collection".format(type(jim[node.id])))
    return jim[node.id]

def apply_unary(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
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
        else:
            raise TypeError("Error: {} not implemented for process apply".format(process_node.content['process_id']))
    jim[node.id]=jim[process_node.id]
    return jim[node.id]

def sum(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    if verbose:
        print(node)

    jim[node.id]=None
    arguments = [item for sublist in node.content['arguments'].values() for item in sublist]
    for argument in arguments:
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
            if node.content['process_id'] == 'sum':
                jim[node.id]+=value
            else:
                raise TypeError("Error: arithmetic {} not implemented".format(node.content['process_id']))
    return jim[node.id]

def product(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    if verbose:
        print(node)

    jim[node.id]=None
    arguments = [item for sublist in node.content['arguments'].values() for item in sublist]
    for argument in arguments:
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
            if node.content['process_id'] == 'product':
                jim[node.id]*=value
            else:
                raise TypeError("Error: arithmetic {} not implemented".format(node.content['process_id']))
    return jim[node.id]


def apply_binary(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    if verbose:
        print(node)
        print("eq {}".format(node.content.get('description')))

    jim[node.id]=None
    # arguments = [item for sublist in node.content['arguments'].values() for item in sublist]
    arguments = node.content['arguments']
    x = arguments['x']
    y = arguments['y']
    if isinstance(x,dict):
        if verbose:
            print("type of jim is {}".format(type(jim[x['from_node']])))
        if jim[x['from_node']] is None:
            jim[node.id]=None
            return jim[node.id]
        else:
            jim[node.id]=jim[x['from_node']]
    else:
        jim[node.id]=x
    value=0
    if isinstance(y,dict):
        if verbose:
            print("type of jim is {}".format(type(jim[y['from_node']])))
        if jim[y['from_node']] is None:
            jim[node.id]=None
            return jim[node.id]
        else:
            value=jim[y['from_node']]
    else:
        value=y
    if node.content['process_id'] == 'add':
        jim[node.id]+=value
    elif node.content['process_id'] == 'divide':
        jim[node.id]/=value
    elif node.content['process_id'] == 'eq':
        jim[node.id]=Cube(jim[node.id]==value)
    elif node.content['process_id'] == 'gt':
        jim[node.id]=Cube(jim[node.id]>value)
    elif node.content['process_id'] == 'gte':
        jim[node.id]=Cube(jim[node.id]>=value)
    elif node.content['process_id'] == 'lt':
        jim[node.id]=Cube(jim[node.id]<value)
    elif node.content['process_id'] == 'lte':
        jim[node.id]=Cube(jim[node.id]<=value)
    elif node.content['process_id'] == 'multiply':
        jim[node.id]*=value
    elif node.content['process_id'] == 'neq':
        jim[node.id]=Cube(jim[node.id]!=value)
    elif node.content['process_id'] == 'subtract':
        jim[node.id]-=value
    else:
        raise TypeError("Error: arithmetic {} not implemented".format(node.content['process_id']))
    return jim[node.id]

def mask(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    if verbose:
        print(node)
        print("eq {}".format(node.content.get('description')))

    jim[node.id]=None
    data = node.content['arguments'].get('data')
    mask = node.content['arguments'].get('mask')
    replacement = node.content['arguments'].get('replacement')
    if isinstance(mask,dict):
        if verbose:
            print("type of mask is {}".format(type(jim[mask['from_node']])))
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

def reduce_dimension(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    parent_node=node.parent_process.content
    data = jim[parent_node['arguments']['data']['from_node']]
    if verbose:
        print(node)
        print("reducing {}".format(node.content['arguments']['dimension']))
    if data is None:
        jim[node.id]=None
        return[node.id]
    reducer_node=agraph[node.content['arguments']['reducer']['from_node']]
    if verbose:
        print("node is: {}".format(node.content))
        print("reducer node is: {}".format(reducer_node))
    if jim[reducer_node.id] is None:
        if node.content['arguments']['dimension'] in ['temporal', 'time', 't']:
            jim[reducer_node.id]=Cube(data)
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
            jim[reducer_node.id].setDimension('temporal',[])
            jim[reducer_node.id].setDimension('band',data.getDimension('band'))
        elif node.content['arguments']['dimension'] in ['spectral', 'bands', 'b']:
            if reducer_node.content['process_id'] == 'first':
                jim[reducer_node.id]=Cube(data)
                # cube=jim[reducer_node.content['arguments']['data']['from_node']]
                if jim[reducer_node.id] is None:
                    jim[node.id]=None
                    return[node.id]
                elif isinstance(cube,pj.JimVect):
                    raise TypeError("Error: reduce not implemented for JimVect")
                elif isinstance(cube,Collection):
                    raise TypeError("Error: reduce not implemented for Collection")
                jim[reducer_node.id].geometry.cropBand(0)
                jim[reducer_node.id].setDimension('band',jim[reducer_node.id].getDimension('band')[0:1])
            elif reducer_node.content['process_id'] == 'last':
                jim[reducer_node.id].geometry.cropBand(-1)
                jim[reducer_node.id].setDimension('band',jim[reducer_node.id].getDimension('band')[-1:])
    jim[node.id]=jim[reducer_node.id]
    return jim[node.id]

def aggregate_temporal(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
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

def merge_cubes(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    if verbose:
        print(node)
    cube1 = jim[node.content['arguments']['cube1'].get('from_node')]
    cube2 = jim[node.content['arguments']['cube2'].get('from_node')]
    if verbose:
        print("cube1 is: {}".format(cube1))
        print("cube2 is: {}".format(cube2))
    if cube1 is None or cube2 is None:
        jim[node.id]=None
        return jim[node.id]
    overlap_resolver = node.content['arguments'].get('overlap_resolver')
    if overlap_resolver is not None:
        overlap_resolver_node=agraph[overlap_resolver]
        x = jim[overlap_resolver_node.content['arguments']['x']['from_node']]
        y = jim[overlap_resolver_node.content['arguments']['y']['from_node']]
        if x is None or y is None:
            jim[node.id]=None
            return jim[node.id]
    else:
        if cube1.properties.nrOfCol() == cube2.properties.nrOfCol():
            if cube1.properties.nrOfRow() == cube2.properties.nrOfRow():
                if cube1.getDimension('temporal') == cube1.getDimension('temporal'):
                    if cube1.properties.nrOfPlane() != cube2.properties.nrOfPlane():
                        raise ValueError('Error: mismatch in temporal dimension ')
                    bandname1=cube1.getDimension('band')
                    bandname2=cube2.getDimension('band')
                    temporalOverlap = not set(bandname1).isdisjoint(bandname2)
                    bandnames = [band for band in bandname1 + bandname2 if band not in list(set(bandname1) & set(bandname2))]
                    bandOverlap = not set(bandname1).isdisjoint(bandname2)
                    if bandOverlap:
                        if overlap_resolver is None:
                            raise ValueError('Error: no overlap resolver defined in merge_cube')
                        else:
                            #todo: reduce
                            raise ValueError('Error: band overlap not yet supported in merge_cube')
                    else:
                        jim[node.id]=Cube(pj.geometry.stackBand(cube1,cube2))
                        jim[node.id].setDimension('band', bandnames)
                elif cube1.getDimension('band') == cube1.getDimension('band'):
                    if cube1.properties.nrOfBand() != cube2.properties.nrOfBand():
                        raise ValueError('Error: mismatch in band dimension ')
                    dimension1=cube1.getDimension('temporal')
                    dimension2=cube2.getDimension('temporal')
                    temporalOverlap = not set(dimension1).isdisjoint(dimension2)
                    dimension = [dim for dim in dimension1 + dimension2 if dim not in list(set(dimension1) & set(dimension2))]
                    if temporalOverlap:
                        if overlap_resolver is None:
                            raise ValueError('Error: no overlap resolver defined in merge_cube')
                        else:
                            #todo: reduce
                            raise ValueError('Error: temporal overlap not yet supported in merge_cube')
                    else:
                        jim[node.id]=Cube(pj.geometry.stackPlane(cube1,cube2))
                        jim[node.id].setDimension('temporal', dimension)
            else:
                raise ValueError('Error: merge_cube not supported if number of rows do not match')
        else:
            raise ValueError('Error: merge_cube not supported if number of cols do not match')
    return jim[node.id]

def add_dimension(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    jim[node.id]=jim[node.content['arguments']['data']['from_node']]
    if jim[node.id] is None:
        return jim[node.id]
    dimension = node.content['arguments'].get('name')
    label = node.content['arguments'].get('label')
    jim[node.id].addDimension(dimension, label)
    return jim[node.id]

def drop_dimension(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    jim[node.id]=jim[node.content['arguments']['data']['from_node']]
    if jim[node.id] is None:
        return jim[node.id]
    dimension = node.content['arguments'].get('name')
    label = node.content['arguments'].get('label')
    jim[node.id].dropDimension(dimension, label)
    return jim[node.id]

def rename_labels(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    jim[node.id]=jim[node.content['arguments']['data']['from_node']]
    if jim[node.id] is None:
        return jim[node.id]
    dimension = node.content['arguments'].get('dimension')
    values = node.content['arguments'].get('target')
    if not isinstance(values, list):
        raise TypeError('Error: {} is not a list'.format(values))
    jim[node.id].setDimension(dimension, values)
    return jim[node.id]

def resample_cube_spatial(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
    target=jim[node.content['arguments']['target']['from_node']]
    if target is None:
        jim[node.id]=None
        return jim[node.id]
    elif not isinstance(target,pj.Jim):
        raise TypeError("Error: target must be of Jim type, not {}".format( type(target)))
    jim[node.id]=jim[node.content['arguments']['data']['from_node']]
    if jim[node.id] is None:
        return jim[node.id]
    if not isinstance(jim[node.id],pj.Jim):
        raise TypeError("Error: {} not implemented for {}".format(node.content['process_id'], type(jim[node.id])))
    jim[node.id].geometry.crop(dx = target.properties.getDeltaX(), dy = target.properties.getDeltaY())
    jim[node.id].resolution['spatial'] = [jim[node.id].properties.getDeltaX(), jim[node.id].properties.getDeltaY()]
    return jim[node.id]

def run_udf(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
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

        if 'array' in imgname:
            jim[node.id]=eval(udf_name)(jim[node.content['arguments']['data']['from_node']].np())
        elif 'jim' in imgname:
            jim[node.id]=eval(udf_name)(jim[node.content['arguments']['data']['from_node']])
        else:
            raise TypeError("Error: name of first parameter should either be jim (for pyjeo Jim) or array (for Numpy array)".format(type(jim[node.id])))
        if not isinstance(jim[node.id],Cube) or not isinstance(jim[node.id],pj.JimVect):
            if isinstance(jim[node.id],pj.Jim):
                jim[node.id]=Cube(jim[node.id])
                jim[node.id].dimension=jim[node.content['arguments']['data']['from_node']].dimension
            elif isinstance(jim[node.id],np.ndarray):
                aCube = Cube(jim[node.content['arguments']['data']['from_node']])
                aCube.np()[:]=jim[node.id]
                jim[node.id]=aCube
            else:
                raise TypeError("Error: udf returns {}, must be of type Jim/Cube, numpy.ndarray, or JimVect".format(type(jim[node.id])))

def aggregate_spatial(agraph, nodeid, jim):
    verbose = True
    node = agraph[nodeid]
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
                # print(invect.np().shape)
                # print(invect.np())
                # ds=gdal.OpenEx(geojson)
                # lyr = ds.GetLayer()
            elif geometryType == 'file':
                invect=pj.JimVect(geometries['path'])
                # print(invect.np().shape)
                # print(invect.np())
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
            if not planename:
                planename=['t'+str(t) for t in range(0,jim[node.content['arguments']['data']['from_node']].properties.nrOfPlane())]

            bandname=jim[node.content['arguments']['data']['from_node']].dimension['band']
            if not bandname:
                bandname=['b'+str(b) for b in range(0,jim[node.content['arguments']['data']['from_node']].properties.nrOfBand())]
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
            # print('extracted vector: {}'.format(jim[node.id].np()))
            jim[node.id].io.write()
            return jim[node.id]
        else:
            raise ValueError("Error: could not aggregate polygon")
    else:
        jim[node.id]=jim[reducer_node.id]
        return jim[node.id]
