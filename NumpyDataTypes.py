
import numpy as np
import datetime

def getBGReading(i) :
    cfactor = 1
    if i.get('units',None) == 'mmol/L' or i.get('units',{}).get('bg',None) == 'mmol/L' :
        cfactor = 18.01559
    return i.get('value')*cfactor if i['type'] == 'smbg' else -1

def getDeviceTime(i) :
    try :
        return np.datetime64(i['deviceTime'])
    except ValueError :
        tmp = datetime.datetime.strptime(i['deviceTime'],'%m/%d/%y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        return np.datetime64(tmp)

def getDataFields() :
    from collections import OrderedDict
    fields = [{'name':'DeviceTime','fcn':getDeviceTime,'type':'datetime64[s]'},
              {'name':'BGReading' ,'fcn':getBGReading ,'type':np.int16},
             ]
    return fields
