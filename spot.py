import os
import datetime
import numpy as np
import xml.dom.minidom
import rasterio as rio
# import matplotlib.pyplot as plt
# from rasterio.control import GroundControlPoint

#%%
class SPOT_SENSOR(object):
    
    def __init__(self):
        pass
            
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def band_key(self):
        band_key = dict()
        
        band_key["reflectance"]  = ['B0', 'B1', 'B2', 'B3']
        band_key["panchromatic"] = ['P']
        
        return band_key
    
    @property
    def band_nick_name(self):
        band_nick_name = {'BLUE':  'B0',
                          'GREEN': 'B1',
                          'RED':   'B2',
                          'NIR':   'B3',
                          'PAN':   'P',
                          '0':     'B0',
                          '1':     'B1',
                          '2':     'B2',
                          '3':     'B3'}
        
        band_key = self.band_key
        
        for key in band_key["reflectance"]:
            band_nick_name[key] = key
        
        for key in band_key["panchromatic"]:
            band_nick_name[key] = key
        
        return band_nick_name
        

#%%
class SPOT(SPOT_SENSOR):
    
    def __init__(self, filepath):
        
        self.filepath = filepath
    
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def filepath(self):
        return self._filepath
    
    # *************************************************************************
    # PROPERTIES - SETTERS
    # *************************************************************************
    
    @filepath.setter
    def filepath(self, src):
        path = dict()
        path["MAIN"] = src
        path["PROD"] = [os.path.join(path["MAIN"],x) for x in os.listdir(path["MAIN"]) if ( os.path.isdir(os.path.join(path["MAIN"],x)) and (x.startswith("PROD_SPOT")) )][0]
        path["VOL"]  = [os.path.join(path["PROD"],x) for x in os.listdir(path["PROD"]) if ( os.path.isdir(os.path.join(path["PROD"],x)) and (x.startswith("VOL_SPOT"))  )][0]
        
        MS = [os.path.join(path["VOL"] ,x) for x in os.listdir(path["VOL"] ) if ( os.path.isdir(os.path.join(path["VOL"] ,x)) and (x.count("_MS_")>0))][0]
        P  = [os.path.join(path["VOL"] ,x) for x in os.listdir(path["VOL"] ) if ( os.path.isdir(os.path.join(path["VOL"] ,x)) and (x.count("_P_") >0))][0]
        
        path["MS"] = dict()
        path["P"]  = dict()
        
        path["MS"]["IMG"] = [os.path.join(MS ,x) for x in os.listdir(MS ) if ( (x.startswith("IMG_SPOT")) and (x.count("_MS_")>0) and (x.endswith(".TIF")) )][0]
        path["MS"]["DIM"] = [os.path.join(MS ,x) for x in os.listdir(MS ) if ( (x.startswith("DIM_SPOT")) and (x.count("_MS_")>0) and (x.endswith(".XML")) )][0]
        path["MS"]["RPC"] = [os.path.join(MS ,x) for x in os.listdir(MS ) if ( (x.startswith("RPC_SPOT")) and (x.count("_MS_")>0) and (x.endswith(".XML")) )][0]
        
        path["P"]["IMG"]  = [os.path.join(P ,x)  for x in os.listdir(P )  if ( (x.startswith("IMG_SPOT")) and (x.count("_P_")>0)  and (x.endswith(".TIF")) )][0]
        path["P"]["DIM"]  = [os.path.join(P ,x)  for x in os.listdir(P )  if ( (x.startswith("DIM_SPOT")) and (x.count("_P_")>0)  and (x.endswith(".XML")) )][0]
        path["P"]["RPC"]  = [os.path.join(P ,x)  for x in os.listdir(P )  if ( (x.startswith("RPC_SPOT")) and (x.count("_P_")>0)  and (x.endswith(".XML")) )][0]
    
        self._filepath = path

    # *************************************************************************
    # METHODS
    # *************************************************************************
    
    def metadata(self, key="PAN"):
        
        filepath = self.filepath
        band_key = self.band_key
        band_nick_name = self.band_nick_name
        
        if (filepath is None):
            raise ValueError("ERROR: No SPOT filepath available")
            
        if not(key in band_nick_name.keys()):
            raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
        else:
            
            key = band_nick_name[key]
            
            if (key in band_key["reflectance"]):
                dim  = xml.dom.minidom.parse(filepath["MS"]["DIM"])
                rpc  = xml.dom.minidom.parse(filepath["MS"]["RPC"])
            elif (key in band_key["panchromatic"]):
                dim  = xml.dom.minidom.parse(filepath["P"]["DIM"])
                rpc  = xml.dom.minidom.parse(filepath["P"]["RPC"])
            else:
                raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
        
        meta = dict()
        
        # ---------------------------------------------------------------------
        # INDEX        
        for elmt in dim.getElementsByTagName("Raster_Index_List")[0].getElementsByTagName("Raster_Index"):
            
            key   = elmt.getElementsByTagName("BAND_ID")[0].lastChild.data
            index = elmt.getElementsByTagName("BAND_INDEX")[0].lastChild.data
            
            meta[key]          = dict()
            meta[key]["INDEX"] = int(index)
        
        # ---------------------------------------------------------------------
        # GAIN, BIAS            
        for elmt in dim.getElementsByTagName("Band_Measurement_List")[0].getElementsByTagName("Band_Radiance"):
            
            key  = elmt.getElementsByTagName("BAND_ID")[0].lastChild.data
            gain = elmt.getElementsByTagName("GAIN")[0].lastChild.data
            bias = elmt.getElementsByTagName("BIAS")[0].lastChild.data
            
            meta[key]["GAIN"] = float(gain)
            meta[key]["BIAS"] = float(bias)
        
        # ---------------------------------------------------------------------
        # ESUN
        for elmt in dim.getElementsByTagName("Band_Measurement_List")[0].getElementsByTagName("Band_Solar_Irradiance"):
            
            key  = elmt.getElementsByTagName("BAND_ID")[0].lastChild.data
            esun = elmt.getElementsByTagName("VALUE")[0].lastChild.data
            
            meta[key]["ESUN"] = float(esun)
                    
        # ---------------------------------------------------------------------
        # BBOX
        meta["BBOX"] = dict()
        
        for i,elmt in enumerate(dim.getElementsByTagName("Dataset_Extent")[0].getElementsByTagName("Vertex")):
            
            meta["BBOX"][i] = dict()
            
            lon  = float(elmt.getElementsByTagName("LON")[0].lastChild.data)
            lat  = float(elmt.getElementsByTagName("LAT")[0].lastChild.data)
            row  = int(  elmt.getElementsByTagName("ROW")[0].lastChild.data)
            col  = int(  elmt.getElementsByTagName("COL")[0].lastChild.data)
            
            meta["BBOX"][i]["LON"] = lon
            meta["BBOX"][i]["LAT"] = lat
            meta["BBOX"][i]["ROW"] = row
            meta["BBOX"][i]["COL"] = col
            
        i+=1
        elmt = dim.getElementsByTagName("Dataset_Extent")[0].getElementsByTagName("Center")[0]
        
        meta["BBOX"][i] = dict()
            
        lon  = float(elmt.getElementsByTagName("LON")[0].lastChild.data)
        lat  = float(elmt.getElementsByTagName("LAT")[0].lastChild.data)
        row  = int(  elmt.getElementsByTagName("ROW")[0].lastChild.data)
        col  = int(  elmt.getElementsByTagName("COL")[0].lastChild.data)
        
        meta["BBOX"][i]["LON"] = lon
        meta["BBOX"][i]["LAT"] = lat
        meta["BBOX"][i]["ROW"] = row
        meta["BBOX"][i]["COL"] = col
        
        # ---------------------------------------------------------------------
        # WIDTH, HEIGHT, COUNT
        elmt = dim.getElementsByTagName("Raster_Data")[0].getElementsByTagName("Raster_Dimensions")[0]
        
        height = int(elmt.getElementsByTagName("NROWS")[0].lastChild.data)
        width  = int(elmt.getElementsByTagName("NCOLS")[0].lastChild.data)
        count  = int(elmt.getElementsByTagName("NBANDS")[0].lastChild.data)
        
        meta["HEIGHT"] = height
        meta["WIDTH"]  = width
        meta["COUNT"]  = count
        
        # ---------------------------------------------------------------------
        # CRS
        elmt = dim.getElementsByTagName("Coordinate_Reference_System")[0].getElementsByTagName("Geodetic_CRS")[0].getElementsByTagName("GEODETIC_CRS_CODE")[0].lastChild.data
        crs  = elmt.split("::")[0].split(":")[-1] + ":" + elmt.split("::")[1]
        
        meta["CRS"] = rio.crs.CRS.from_string(crs)
        
        # # ---------------------------------------------------------------------
        # # TRANSFORM
        # gcps = list()
        # for BBOX in meta["BBOX"].values():
        #     gcp = GroundControlPoint(col=BBOX["COL"]-1, row=BBOX["ROW"]-1, x=BBOX["LON"], y=BBOX["LAT"], z=0.0)
        #     gcps.append(gcp)
        
        # meta["TRANSFORM"] = rio.transform.from_gcps(gcps)
        
        # BBOX   = meta["BBOX"]
        # left   = min(BBOX[0]["LON"], BBOX[1]["LON"], BBOX[2]["LON"], BBOX[3]["LON"])
        # bottom = min(BBOX[0]["LAT"], BBOX[1]["LAT"], BBOX[2]["LAT"], BBOX[3]["LAT"])
        # right  = max(BBOX[0]["LON"], BBOX[1]["LON"], BBOX[2]["LON"], BBOX[3]["LON"])
        # top    = max(BBOX[0]["LAT"], BBOX[1]["LAT"], BBOX[2]["LAT"], BBOX[3]["LAT"])
        
        elmt = rpc.getElementsByTagName("Rational_Function_Model")[0].getElementsByTagName("Global_RFM")[0].getElementsByTagName("RFM_Validity")[0].getElementsByTagName("Inverse_Model_Validity_Domain")[0]
        
        left   = float(elmt.getElementsByTagName("FIRST_LON")[0].lastChild.data)
        bottom = float(elmt.getElementsByTagName("FIRST_LAT")[0].lastChild.data)
        right  = float(elmt.getElementsByTagName("LAST_LON" )[0].lastChild.data)
        top    = float(elmt.getElementsByTagName("LAST_LAT" )[0].lastChild.data)
                
        meta["TRANSFORM"] = rio.transform.from_bounds(left, bottom, right, top, meta["WIDTH"], meta["HEIGHT"])
        
                
        # ---------------------------------------------------------------------
        # YYYY, MM, DD, DOY        
        data = dim.getElementsByTagName("Use_Area")[0].getElementsByTagName("TIME")[0].lastChild.data
        data = data.split("T")[0]
        data = data.split("-")
        
        meta["ACQUISITION_DATE"] = dict()
        
        meta["ACQUISITION_DATE"]["YYYY"] = int(data[0])
        meta["ACQUISITION_DATE"]["MM"]   = int(data[1])
        meta["ACQUISITION_DATE"]["DD"]   = int(data[2])
        
        today = datetime.datetime(meta["ACQUISITION_DATE"]["YYYY"],\
                                  meta["ACQUISITION_DATE"]["MM"],\
                                  meta["ACQUISITION_DATE"]["DD"])
            
        meta["ACQUISITION_DATE"]["DOY"]  = (today - datetime.datetime(today.year, 1, 1)).days + 1
        
        # ---------------------------------------------------------------------
        # SUN_ELEVATION, SUN_EARTH_DISTANCE
        elmts = dim.getElementsByTagName("Use_Area")[0].getElementsByTagName("SUN_ELEVATION")    
        meta["SUN_ELEVATION"] = 0.
        
        for elmt in elmts:
            meta["SUN_ELEVATION"] += float(elmt.lastChild.data)
        
        meta["SUN_ELEVATION"] = meta["SUN_ELEVATION"]/len(elmts)
        
        meta["SUN_EARTH_DISTANCE"] = self._sun_earth_distance(meta["ACQUISITION_DATE"]["DOY"])
        
        return meta
    
    def reflectance(self, key):
        
        filepath = self.filepath
        band_key = self.band_key
        band_nick_name = self.band_nick_name
        
        if (filepath is None):
            raise ValueError("ERROR: No SPOT filepath available")
            
        if not(key in band_nick_name.keys()):
            raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
            
        else:
            key = band_nick_name[key]
            meta = self.metadata(key=key)
            
            if (key in band_key["reflectance"]):
                src  = filepath["MS"]["IMG"]                
            elif (key in band_key["panchromatic"]):
                src  = filepath["P"]["IMG"]
            else:
                raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
                
        INDEX = meta[key]["INDEX"]
        GAIN  = meta[key]["GAIN"]
        BIAS  = meta[key]["BIAS"]
        ESUN  = meta[key]["ESUN"]
        
        SUN_ELEV = meta["SUN_ELEVATION"]
        SUN_DIST = meta["SUN_EARTH_DISTANCE"]
        
        with rio.open(src) as dst:
            img  = dst.read(INDEX)
        
        band = ( np.pi * (img/GAIN+BIAS) * SUN_DIST**2 )/( ESUN * np.sin(SUN_ELEV*np.pi/180.) )
        
        band[band>1.] = 1.
        band[band<0.] = 0.
        
        return band
        
    def save_band(self, key, src):
        
        filepath = self.filepath
        band_nick_name = self.band_nick_name
        
        if (filepath is None):
            raise ValueError("ERROR: No SPOT filepath available")
        if not(key in band_nick_name.keys()):
            raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
        else:
            key = band_nick_name[key]
            
        profile = self.profile(key)
        
        img = (255*self.reflectance(key)).astype("uint8")
        img = (np.ma.array(img, mask=img==0))
        
        with rio.open(src, "w", **profile) as dst:
            dst.write(img, indexes=1)
    
    def profile(self, key):
        
        filepath = self.filepath
        band_nick_name = self.band_nick_name
        
        if (filepath is None):
            raise ValueError("ERROR: No SPOT filepath available")
        if not(key in band_nick_name.keys()):
            raise ValueError("ERROR: Invalid Parameter 'key' = {}".format(key))
        else:
            key = band_nick_name[key]
            meta = self.metadata(key=key)
            
        profile = {"crs": meta["CRS"],\
                   "width": meta["WIDTH"],\
                   "height": meta["HEIGHT"],\
                   "transform": meta["TRANSFORM"],\
                   "count": 1,\
                   "nodata": 0,\
                   "dtype": "uint8",\
                   "driver": "GTiff",
                   "compress":"deflate"}
        
        return profile
        
    # *************************************************************************
    # HIDDEN METHODS
    # *************************************************************************
    
    def _sun_earth_distance(self, DOY):
        d = {1: 0.98331,
             2: 0.9833,
             3: 0.9833,
             4: 0.9833,
             5: 0.9833,
             6: 0.98332,
             7: 0.98333,
             8: 0.98335,
             9: 0.98338,
             10: 0.98341,
             11: 0.98345,
             12: 0.98349,
             13: 0.98354,
             14: 0.98359,
             15: 0.98365,
             16: 0.98371,
             17: 0.98378,
             18: 0.98385,
             19: 0.98393,
             20: 0.98401,
             21: 0.9841,
             22: 0.98419,
             23: 0.98428,
             24: 0.98439,
             25: 0.98449,
             26: 0.9846,
             27: 0.98472,
             28: 0.98484,
             29: 0.98496,
             30: 0.98509,
             31: 0.98523,
             32: 0.98536,
             33: 0.98551,
             34: 0.98565,
             35: 0.9858,
             36: 0.98596,
             37: 0.98612,
             38: 0.98628,
             39: 0.98645,
             40: 0.98662,
             41: 0.9868,
             42: 0.98698,
             43: 0.98717,
             44: 0.98735,
             45: 0.98755,
             46: 0.98774,
             47: 0.98794,
             48: 0.98814,
             49: 0.98835,
             50: 0.98856,
             51: 0.98877,
             52: 0.98899,
             53: 0.98921,
             54: 0.98944,
             55: 0.98966,
             56: 0.98989,
             57: 0.99012,
             58: 0.99036,
             59: 0.9906,
             60: 0.99084,
             61: 0.99108,
             62: 0.99133,
             63: 0.99158,
             64: 0.99183,
             65: 0.99208,
             66: 0.99234,
             67: 0.9926,
             68: 0.99286,
             69: 0.99312,
             70: 0.99339,
             71: 0.99365,
             72: 0.99392,
             73: 0.99419,
             74: 0.99446,
             75: 0.99474,
             76: 0.99501,
             77: 0.99529,
             78: 0.99556,
             79: 0.99584,
             80: 0.99612,
             81: 0.9964,
             82: 0.99669,
             83: 0.99697,
             84: 0.99725,
             85: 0.99754,
             86: 0.99782,
             87: 0.99811,
             88: 0.9984,
             89: 0.99868,
             90: 0.99897,
             91: 0.99926,
             92: 0.99954,
             93: 0.99983,
             94: 1.00012,
             95: 1.00041,
             96: 1.00069,
             97: 1.00098,
             98: 1.00127,
             99: 1.00155,
             100: 1.00184,
             101: 1.00212,
             102: 1.0024,
             103: 1.00269,
             104: 1.00297,
             105: 1.00325,
             106: 1.00353,
             107: 1.00381,
             108: 1.00409,
             109: 1.00437,
             110: 1.00464,
             111: 1.00492,
             112: 1.00519,
             113: 1.00546,
             114: 1.00573,
             115: 1.006,
             116: 1.00626,
             117: 1.00653,
             118: 1.00679,
             119: 1.00705,
             120: 1.00731,
             121: 1.00756,
             122: 1.00781,
             123: 1.00806,
             124: 1.00831,
             125: 1.00856,
             126: 1.0088,
             127: 1.00904,
             128: 1.00928,
             129: 1.00952,
             130: 1.00975,
             131: 1.00998,
             132: 1.0102,
             133: 1.01043,
             134: 1.01065,
             135: 1.01087,
             136: 1.01108,
             137: 1.01129,
             138: 1.0115,
             139: 1.0117,
             140: 1.01191,
             141: 1.0121,
             142: 1.0123,
             143: 1.01249,
             144: 1.01267,
             145: 1.01286,
             146: 1.01304,
             147: 1.01321,
             148: 1.01338,
             149: 1.01355,
             150: 1.01371,
             151: 1.01387,
             152: 1.01403,
             153: 1.01418,
             154: 1.01433,
             155: 1.01447,
             156: 1.01461,
             157: 1.01475,
             158: 1.01488,
             159: 1.015,
             160: 1.01513,
             161: 1.01524,
             162: 1.01536,
             163: 1.01547,
             164: 1.01557,
             165: 1.01567,
             166: 1.01577,
             167: 1.01586,
             168: 1.01595,
             169: 1.01603,
             170: 1.0161,
             171: 1.01618,
             172: 1.01625,
             173: 1.01631,
             174: 1.01637,
             175: 1.01642,
             176: 1.01647,
             177: 1.01652,
             178: 1.01656,
             179: 1.01659,
             180: 1.01662,
             181: 1.01665,
             182: 1.01667,
             183: 1.01668,
             184: 1.0167,
             185: 1.0167,
             186: 1.0167,
             187: 1.0167,
             188: 1.01669,
             189: 1.01668,
             190: 1.01666,
             191: 1.01664,
             192: 1.01661,
             193: 1.01658,
             194: 1.01655,
             195: 1.0165,
             196: 1.01646,
             197: 1.01641,
             198: 1.01635,
             199: 1.01629,
             200: 1.01623,
             201: 1.01616,
             202: 1.01609,
             203: 1.01601,
             204: 1.01592,
             205: 1.01584,
             206: 1.01575,
             207: 1.01565,
             208: 1.01555,
             209: 1.01544,
             210: 1.01533,
             211: 1.01522,
             212: 1.0151,
             213: 1.01497,
             214: 1.01485,
             215: 1.01471,
             216: 1.01458,
             217: 1.01444,
             218: 1.01429,
             219: 1.01414,
             220: 1.01399,
             221: 1.01383,
             222: 1.01367,
             223: 1.01351,
             224: 1.01334,
             225: 1.01317,
             226: 1.01299,
             227: 1.01281,
             228: 1.01263,
             229: 1.01244,
             230: 1.01225,
             231: 1.01205,
             232: 1.01186,
             233: 1.01165,
             234: 1.01145,
             235: 1.01124,
             236: 1.01103,
             237: 1.01081,
             238: 1.0106,
             239: 1.01037,
             240: 1.01015,
             241: 1.00992,
             242: 1.00969,
             243: 1.00946,
             244: 1.00922,
             245: 1.00898,
             246: 1.00874,
             247: 1.0085,
             248: 1.00825,
             249: 1.008,
             250: 1.00775,
             251: 1.0075,
             252: 1.00724,
             253: 1.00698,
             254: 1.00672,
             255: 1.00646,
             256: 1.0062,
             257: 1.00593,
             258: 1.00566,
             259: 1.00539,
             260: 1.00512,
             261: 1.00485,
             262: 1.00457,
             263: 1.0043,
             264: 1.00402,
             265: 1.00374,
             266: 1.00346,
             267: 1.00318,
             268: 1.0029,
             269: 1.00262,
             270: 1.00234,
             271: 1.00205,
             272: 1.00177,
             273: 1.00148,
             274: 1.00119,
             275: 1.00091,
             276: 1.00062,
             277: 1.00033,
             278: 1.00005,
             279: 0.99976,
             280: 0.99947,
             281: 0.99918,
             282: 0.9989,
             283: 0.99861,
             284: 0.99832,
             285: 0.99804,
             286: 0.99775,
             287: 0.99747,
             288: 0.99718,
             289: 0.9969,
             290: 0.99662,
             291: 0.99634,
             292: 0.99605,
             293: 0.99577,
             294: 0.9955,
             295: 0.99522,
             296: 0.99494,
             297: 0.99467,
             298: 0.9944,
             299: 0.99412,
             300: 0.99385,
             301: 0.99359,
             302: 0.99332,
             303: 0.99306,
             304: 0.99279,
             305: 0.99253,
             306: 0.99228,
             307: 0.99202,
             308: 0.99177,
             309: 0.99152,
             310: 0.99127,
             311: 0.99102,
             312: 0.99078,
             313: 0.99054,
             314: 0.9903,
             315: 0.99007,
             316: 0.98983,
             317: 0.98961,
             318: 0.98938,
             319: 0.98916,
             320: 0.98894,
             321: 0.98872,
             322: 0.98851,
             323: 0.9883,
             324: 0.98809,
             325: 0.98789,
             326: 0.98769,
             327: 0.9875,
             328: 0.98731,
             329: 0.98712,
             330: 0.98694,
             331: 0.98676,
             332: 0.98658,
             333: 0.98641,
             334: 0.98624,
             335: 0.98608,
             336: 0.98592,
             337: 0.98577,
             338: 0.98562,
             339: 0.98547,
             340: 0.98533,
             341: 0.98519,
             342: 0.98506,
             343: 0.98493,
             344: 0.98481,
             345: 0.98469,
             346: 0.98457,
             347: 0.98446,
             348: 0.98436,
             349: 0.98426,
             350: 0.98416,
             351: 0.98407,
             352: 0.98399,
             353: 0.98391,
             354: 0.98383,
             355: 0.98376,
             356: 0.9837,
             357: 0.98363,
             358: 0.98358,
             359: 0.98353,
             360: 0.98348,
             361: 0.98344,
             362: 0.9834,
             363: 0.98337,
             364: 0.98335,
             365: 0.98333,
             366: 0.98331}
    
        return d[DOY]
