#!/usr/bin/env python3

import os
import numpy as np
import re
import os
from string import ascii_letters
import matplotlib.pyplot as plt
import json
import math

from NumpyDataTypes import getDataFields,getBGReading,getDeviceTime

def GetInputFiles(_args) :
    # We will process Medtronic csv files OR TidePool json files!
    _args.match_regexp = ['Tidepool_Export.*json','Annotations_.*json']

    inputfilenames = []
    for d in os.listdir(_args.datadir) :
        # _args.match_regexp should be a list of regexp tries
        # (e.g. ['CareLink_Export.*csv','Tidepool_Export.*json']
        matches = list( bool(re.match(matchstr,d)) for matchstr in _args.match_regexp)
        if (True in matches) :
            inputfilenames.append('%s/%s'%(_args.datadir,d))

    inputfilenames = sorted(inputfilenames,key=lambda a: a.lstrip(ascii_letters+'/_.'))
    return inputfilenames

def GetBGRollingAverageAndRMS(_data,nweeks=17,minweeks=4,step_days=2) :

    timerange = np.arange(_data['DeviceTime'][0]+np.timedelta64(minweeks,'W'),
                          _data['DeviceTime'][-1],
                          step=np.timedelta64(step_days,'D'),
                          dtype='datetime64[D]')
    bgAverage = []
    bgRMS = []

    for t_plot in timerange :

        bgsOfPreviousWeeks = []
        # print(t_plot)
        for data in _data :
            if data['BGReading'] < 0 :
                continue
            data_age = t_plot - data['DeviceTime']
            #print ('--',data['DeviceTime'],data_age)
            if data_age < np.timedelta64(0,'s') :
                break
            if data_age > np.timedelta64(nweeks,'W') :
                continue
            bgsOfPreviousWeeks.append(data['BGReading'])

        n = len(bgsOfPreviousWeeks)
        if not n :
            bgAverage.append(0)
        mean = sum(bgsOfPreviousWeeks)/n
        bgAverage.append(mean)
        rms = math.sqrt(sum(list(math.pow(a-mean,2) for a in bgsOfPreviousWeeks))/float(n))
        bgRMS.append(rms)

    avg = np.array(bgAverage)
    rms = np.array(bgRMS)
    return timerange,avg,rms


def main(args) :

    inputfiles = GetInputFiles(args)
    fields = getDataFields()

    # Populate this events list with tuples containing the event info
    events = []

    for inputfile in inputfiles :

        # print(inputfile)
        with open(inputfile,'r') as json_file :
            data = json.load(json_file)

            for i in data :
                if 'deviceTime' not in i.keys() :
                    continue
                #print(i)

                event = tuple()
                for field in fields :
                    try :
                        event += (field['fcn'](i),)
                    except KeyError :
                        print('Exception occurred with\n',i)

                #print('One tuple:',event)
                events.append(event)

    # Sort the events
    events.sort(key=lambda x: x[0])

    dtype = list((field['name'],field['type']) for field in fields)
    all_data = np.array(events,dtype=dtype)

    print('length of array:',len(all_data))

    #
    # Plot of all BG points
    #
    # Trick: make a list of booleans, which can then be used to select the indices
    # corresponding to True!
    BG_indices = all_data['BGReading'] > 0
    plt.scatter(all_data['DeviceTime'][BG_indices],all_data['BGReading'][BG_indices])
    # plt.show()

    #
    # Rolling average of BG points in time
    #
    # Solid "error bars" are achieved using fill_between function
    fig, ax = plt.subplots()
    ax.set(xlabel='time', ylabel='BG (mg/dL)',title='Seventeen-week average')

    timerange17,avg17,rms17 = GetBGRollingAverageAndRMS(all_data,17,4)
    ax.plot(timerange17,avg17)
    ax.fill_between(timerange17, avg17-rms17, avg17+rms17,
                     alpha=0.5, edgecolor='#1B2ACC', facecolor='#089FFF')

    timerange4,avg4,rms4 = GetBGRollingAverageAndRMS(all_data,4,4)
    ax.plot(timerange4,avg4)
    ax.fill_between(timerange4, avg4-rms4, avg4+rms4,
                     alpha=0.5, edgecolor='#ffa505', facecolor='#ffa500')

    timerange1,avg1,rms1 = GetBGRollingAverageAndRMS(all_data,1,1,step_days=7)
    ax.scatter(timerange1,avg1)

    plt.show()

    return

if __name__ == '__main__' :
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--summary' ,action='store_true',default=False,help='Make summary root file')
    parser.add_argument('--ndetailed',type=int,default=4,help='Number of weeks of detail (4)')
    parser.add_argument('--outname'  ,default='output.root',help='Output file name')
    parser.add_argument('--datadir'  ,default='data',help='Data directory')

    main(parser.parse_args())
