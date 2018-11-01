import xml.etree.ElementTree as ET
import json
from shapely import geometry 
from urllib.parse import urlparse
import boto3
import rasterio
from rasterio import features
from datetime import datetime

CM_PER_INCH = 2.54


def iterate_OverXML(root, recursionTagList=[], metaDataStruct={}):
    
    for child in root:
        if child.tag in recursionTagList:
            metaDataStruct = iterate_OverXML(child, recursionTagList, metaDataStruct)
        else:
            metaDataStruct[child.tag] = child.text
    
    return metaDataStruct
            

class spacenetStacItem:
    
    def __init__(self, rasterPath, title, provider, license, idStr, assetDict, 
                 imdPath=[], 
                 vrtPath=[], 
                 links=[],
                collection_base=''):
    
        self.rasterPath = rasterPath
        self.provider   = provider
        self.id         = idStr
        self.title      = title
        
        if collection_base !='':
            with open(collection_base) as f:
                self.stac_item = json.load(f)
        else:
            self.stac_item = {
                'properties': []
            }
        
        self.stac_item.update(
            {"id": idStr,
             "type": "Feature",
             "geometry": self.calcGeometry(),
             "title": self.title
            }
                             )
        
        
        
        
        
        self.stac_item['properties'].update(
                        self.createProperties_EO(imdPath=imdPath, vrtPath=vrtPath)
        )
                                            
            
        
        
            
        self.stac_item['assets']=assetDict
        self.stac_item['links'] = links
            
        
        
        
        
        
    def calcGeometry(self):
        
        with rasterio.open(self.rasterPath) as dataset:
            profile = dataset.profile
                # Read the dataset's valid data mask as a ndarray.
            geom = geometry.box(*dataset.bounds)
        
        self.geometry=json.loads(json.dumps(geometry.mapping(geom)))
        
        return json.loads(json.dumps(geometry.mapping(geom)))
        
    
    def createAssetList(self):
        pass
    
    
    def createProperties_EO(self, imdPath=[], vrtPath=[]):
        eo_prop_dict = {}
        
        if imdPath:
            o = urlparse(imdPath)
            if o.scheme == 's3':
                s3 = boto3.resource("s3")
                bucket = o.netloc
                key = o.path.lstrip('/')
                obj = s3.Object(bucket, key)
                body = obj.get()['Body'].read()
                root = ET.fromstring(body)

            else:

                tree = ET.parse(imdPath)
                root = tree.getroot()

            self.metaDataStruct = iterate_OverXML(root, recursionTagList=['IMD', 'IMAGE'])
        elif vrtPath:
            with rasterio.open(vrtPath) as src:
                self.metaDataStruct = process_nitf_tags(src.tags())
        
        else:
            print("no Data Specified")
        self.eoDict = self.processMetaData_To_Properties(self.metaDataStruct, self.provider, self.license)
        
        return self.eoDict
        

    def processMetaData_To_Properties(self, metaDataStruct, provider, license):
        eoDict = {
            "eo:sun_azimuth": metaDataStruct['MEANSUNAZ'],
            "eo:cloud_cover": metaDataStruct['CLOUDCOVER'],
            "eo:off_nadir": metaDataStruct['MEANOFFNADIRVIEWANGLE'],
            "eo:azimuth": metaDataStruct['MEANSATAZ'],
            "eo:platform": metaDataStruct['SATID'],
            "eo:sun_elevation": metaDataStruct['MEANSUNEL'],
            "eo:gsd": metaDataStruct['MEANCOLLECTEDGSD'],
            "eo:crs": '',
            "dg:catalog_id": metaDataStruct['CATID'],
            "dg:platform": metaDataStruct['SATID'],
            "dg:product_level": metaDataStruct['PRODUCTLEVEL'],
            "datetime": metaDataStruct['FIRSTLINETIME'],
            }

        return eoDict
        
    def write_toJSON(self, filename):
        
        with open(filename, 'w') as fp:
            json.dump(self.stac_item, fp, indent=2)
            
            
            
    
    
def process_nitf_tags(tags):
    
    metaDataStruct = {}
    metaDataStruct.update({'MEANSUNAZ': tags['NITF_USE00A_SUN_AZ']})
    
    metaDataStruct.update({'CLOUDCOVER': tags['NITF_PIAIMC_CLOUDCVR']})
    metaDataStruct.update({'MEANOFFNADIRVIEWANGLE': tags['NITF_USE00A_OBL_ANG']})
    metaDataStruct.update({'MEANSATAZ': tags['NITF_USE00A_ANGLE_TO_NORTH']})
    metaDataStruct.update({'SATID': tags['NITF_PIAIMC_SENSNAME']})
    metaDataStruct.update({'MEANSUNEL': tags['NITF_USE00A_SUN_EL']})
    metaDataStruct.update({'MEANCOLLECTEDGSD': float(tags['NITF_CSEXRA_GEO_MEAN_GSD'])*CM_PER_INCH})
    metaDataStruct.update({'CATID': tags['NITF_IDATIM']})
    metaDataStruct.update({'SATID': tags['NITF_PIAIMC_SENSNAME']})
    metaDataStruct.update({'FIRSTLINETIME': datetime.strptime(tags['NITF_STDIDC_ACQUISITION_DATE'], "%Y%m%d%H%M%S").isoformat('T')})
    metaDataStruct.update({'PRODUCTLEVEL': "LV1B"})
    
    
    return metaDataStruct
                        

    
    
    



    
    