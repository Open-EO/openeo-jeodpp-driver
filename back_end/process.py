from datetime import time, timedelta, datetime
import dateutil.parser
from openeo_pg_parser import graph
from jeolib.collection import Collection
from jeolib.cube import Cube

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
    crs = None

    features = None
    if spatial_extent is not None:
        west = spatial_extent.get('west')
        east = spatial_extent.get('east')
        north = spatial_extent.get('north')
        south = spatial_extent.get('south')
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
        if bands is not None:
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
