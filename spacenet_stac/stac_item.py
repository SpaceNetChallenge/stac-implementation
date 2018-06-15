import xml.etree.ElementTree as ET
import json
import rasterio
from rasterio import features


def iterate_OverXML(root, recursionTagList=[], metaDataStruct={}):
    
    for child in root:
        if child.tag in recursionTagList:
            metaDataStruct = iterate_OverXML(child, recursionTagList, metaDataStruct)
        else:
            metaDataStruct[child.tag] = child.text
    
    return metaDataStruct
            

class spacenetStacItem:
    
    def __init__(self, rasterPath, provider, license, idStr, assetDict, imdPath=[], links=[]):
    
        self.rasterPath = rasterPath
        self.provider   = provider
        self.license    = license
        self.id         = idStr
        self.stac_item   = {"id": idStr,
                            "type": "Feature",
                            "geometry": self.calcGeometry()  
                           }
        
        if imdPath:
            self.stac_item['properties']=self.createProperties_EO(imdPath)
            
        self.stac_item['assets']=assetDict
        self.stac_item['links'] = links
            
        
        
        
        
        
    def calcGeometry(self):
        
        with rasterio.open(self.rasterPath) as dataset:
            profile = dataset.profile
                # Read the dataset's valid data mask as a ndarray.
            mask = dataset.dataset_mask()
            # Extract feature shapes and values from the array.
            for geom, val in features.shapes(
                    mask, transform=dataset.transform):

                # Transform shapes from the dataset's own coordinate
                # reference system to CRS84 (EPSG:4326).
                geom = rasterio.warp.transform_geom(
                    dataset.crs, 'EPSG:4326', geom, precision=6)

                # Print GeoJSON shapes to stdout.
                print(geom)
        
        self.geometry=geom
        
        return geom
        
    
    def createAssetList(self):
        pass
    
    
    def createProperties_EO(self, imdPath):
        eo_prop_dict = {}
        tree = ET.parse(imdPath)
        root = tree.getroot()
        self.metaDataStruct = iterate_OverXML(root, recursionTagList=['IMD', 'IMAGE'])
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
            "provider": provider,
            "license": license
            }

        return eoDict
        
    def write_toJSON(self, filename):
        
        with open(filename, 'w') as fp:
            json.dump(self.stac_item, fp, indent=2)