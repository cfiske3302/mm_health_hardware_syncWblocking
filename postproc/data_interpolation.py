import numpy as np
import os
import scipy
from scipy import interpolate

import sys
import os
import time
import csv
from datetime import datetime

def extract_timestamps(filename):
    file = open(filename, 'r')
    data = file.readlines()

    ts = []
    for i in data:
        # print(i.rstrip() + "s")
        time_obj = datetime.strptime(i.rstrip(), '%Y-%m-%d %H:%M:%S.%f')
        ts.append(time_obj.timestamp())
        print(time_obj.timestamp())
    
    return np.array(ts)

def extract_data(filename):
    file = open(filename, 'r', encoding='utf-8-sig')
    csvreader = csv.reader(file)
    stamp_list = []
    for i in csvreader:
        stamp_list.append(i)

    mx_stamps = []
    sys_stamps = []
    pleth = []

    print(stamp_list[0])

    for j in range(len(stamp_list)):
        # print(stamp_list[j])
        time_obj_mx = datetime.strptime(stamp_list[j][0], '%d-%m-%Y %H:%M:%S.%f')
        # stamp_mx = 60*time_obj_mx.minute + time_obj_mx.second + time_obj_mx.microsecond / 1e6
        stamp_mx = time_obj_mx.timestamp()
        mx_stamps.append(stamp_mx)

        time_obj_sys = datetime.strptime(stamp_list[j][2], '%d-%m-%Y %H:%M:%S.%f')
        # stamp_sys = 60*time_obj_sys.minute + time_obj_sys.second + time_obj_sys.microsecond / 1e6
        stamp_sys = time_obj_sys.timestamp()
        sys_stamps.append(stamp_sys)

        pleth.append(int(stamp_list[j][3]))

        # print(stamp_mx, stamp_sys)

    return mx_stamps, sys_stamps, pleth

def find_deltas(sys_stamps, mx_stamps):
    const_num = sys_stamps[0]
    deltas = []
    for i, stamp in enumerate(sys_stamps):
        if(stamp != const_num):
            const_num = stamp
            delta = sys_stamps[i-1] - mx_stamps[i-1]
            if(sys_stamps[i] - sys_stamps[i-1] > 0.3): # comparison for blips
                deltas.append(delta)
    return np.array(deltas)

def find_deltas2(sys_stamps, mx_stamps):
    sys_stamps = sys_stamps[0:200*32]
    mx_stamps  = mx_stamps[0:200*32]

    const_num = sys_stamps[0]
    deltas = []
    for i, stamp in enumerate(sys_stamps):
        if(stamp != const_num):
            const_num = stamp
            delta = sys_stamps[i-1] - mx_stamps[i-1]
            if(sys_stamps[i] - sys_stamps[i-1] > 0.3): # comparison for blips
                deltas.append(delta)
    return np.array(deltas)

def unroll_stamps(mx_stamps, batch_size = int(32), time_diff = 0.256):

    unrolled_stamps = []

    for i in range(int(len(mx_stamps)/batch_size)):
        current_stamp = mx_stamps[i * batch_size]
        # print(current_stamp)
        for j in range(batch_size):
            unrolled_val = current_stamp - time_diff + time_diff*(j+1)/batch_size
            # print(unrolled_val)
            unrolled_stamps.append(unrolled_val)
    
    return np.array(unrolled_stamps)

def unroll_stamps2(mx_stamps, batch_size = int(32), time_diff = 0.256):

    unrolled_stamps = []

    current_stamp = mx_stamps[0] - time_diff
    for i in range(int(len(mx_stamps)/batch_size)):
        current_stamp += time_diff
        # print(current_stamp)
        for j in range(batch_size):
            unrolled_val = current_stamp - time_diff + time_diff*(j+1)/batch_size
            # print(unrolled_val)
            unrolled_stamps.append(unrolled_val)
    
    return np.array(unrolled_stamps)


def apply_delta(mx_stamps, sys_mx_time_delta):
    return mx_stamps + sys_mx_time_delta

def timestamp_process(ts):
        f = ((float(ts)/1e6)-int(float(ts)/1e6))*1e6

        ts = int(float(ts)/1e6)
        s = ((float(ts)/1e2)-int(float(ts)/1e2))*1e2
        ts = int(float(ts)/1e2)
        m = ((float(ts)/1e2)-int(float(ts)/1e2))*1e2
        ts = int(float(ts)/1e2)
        h = ((float(ts)/1e2)-int(float(ts)/1e2))*1e2


        temp = (3600*h)+(60*m)+s+(f*1e-6)
        temp = float(int(temp*1e6))/1e6

        return temp

def interpolate_ppg_timestamp(sensor_file_name, file_dir_mx800):
    file_dir_rgb =  file_dir_mx800
    file_dir_mx800 =  file_dir_mx800

    #constucting arrays for the data
    filename = file_dir_mx800 + r"\NOM_PLETHWaveExport.csv"
    mx_stamps, sys_stamps, ppg = extract_data(filename=filename)

    delta_array = find_deltas2(sys_stamps, mx_stamps)
    sys_mx_time_delta = np.mean(delta_array)
    mx_unrolled = unroll_stamps2(mx_stamps)
    ts_ppg = apply_delta(mx_unrolled, sys_mx_time_delta)

    #loading the time stamp files
    filename2 =  os.path.join(file_dir_rgb, sensor_file_name)
    ts_vid = extract_timestamps(filename2)

    print(ts_ppg.shape, ts_vid.shape)
    print(ts_ppg[0])
    print(ts_vid[0])

    ##CHECK FOR PPG AND TS LENGTHS AND CORRECT
    l1 = len(ts_ppg)
    l2 = len(ppg)
    if l1<l2:
        ppg = ppg[0:l1]
    elif l2<l1:
        ts_ppg = ts_ppg[0:l2]
    # ts_ppg = ts_ppg[0:-1]

    ts_ppg_sec = ts_ppg 
    ts_vid_sec = ts_vid

    #interpolation function
    f = interpolate.interp1d(ts_ppg_sec,ppg,kind='linear')

    reinterp_ppg = []

    for t_temp in ts_vid_sec:
        if t_temp<ts_ppg_sec[0]:
            reinterp_ppg.append(ppg[0])
        elif t_temp>ts_ppg_sec[-1]:
            reinterp_ppg.append(ppg[-1])
        else:
            reinterp_ppg.append(f(t_temp))

    #write to csv files

    a = np.array(reinterp_ppg)
    np.savetxt(file_dir_mx800+'/'+"ppg.csv", reinterp_ppg, delimiter=",")

    import matplotlib.pyplot as plt

    plt.plot(reinterp_ppg)
    plt.show()

if __name__ == '__main__':

    num = sys.argv[1]
    #Paths and directories
    file_dir_rgb =  r"F:\IRB data\91\91_5"#"C:\Temp\mmhealth_data\testing4"
    file_dir_mx800 =  r"F:\IRB data\91\91_5"

    #constucting arrays for the data
    filename = file_dir_mx800 + r"\NOM_PLETHWaveExport.csv"
    mx_stamps, sys_stamps, ppg = extract_data(filename=filename)

    delta_array = find_deltas2(sys_stamps, mx_stamps)
    sys_mx_time_delta = np.mean(delta_array)
    mx_unrolled = unroll_stamps2(mx_stamps)
    ts_ppg = apply_delta(mx_unrolled, sys_mx_time_delta)

    #loading the time stamp files
    filename2 =  file_dir_rgb + r"\91_5_local.txt"
    ts_vid = extract_timestamps(filename2)

    # print(ts_ppg)
    # print(ts_vid)
    print(ts_ppg.shape, ts_vid.shape)

    print(ts_ppg[0])
    print(ts_vid[0])

    ##CHECK FOR PPG AND TS LENGTHS AND CORRECT
    l1 = len(ts_ppg)
    l2 = len(ppg)
    if l1<l2:
        ppg = ppg[0:l1]
    elif l2<l1:
        ts_ppg = ts_ppg[0:l2]
    # ts_ppg = ts_ppg[0:-1]

    ts_ppg_sec = ts_ppg 
    ts_vid_sec = ts_vid

    #process the time stamps to return

    

    # ts_ppg_sec = []
    # for t_temp in ts_ppg:
    #     ts_ppg_sec.append(timestamp_process(t_temp))

    # ts_vid_sec = []
    # for t_temp in ts_vid:
    #     ts_vid_sec.append(timestamp_process(t_temp))


    #interpolation function
    f = interpolate.interp1d(ts_ppg_sec,ppg,kind='linear')

    reinterp_ppg = []

    for t_temp in ts_vid_sec:
        if t_temp<ts_ppg_sec[0]:
            reinterp_ppg.append(ppg[0])
        elif t_temp>ts_ppg_sec[-1]:
            reinterp_ppg.append(ppg[-1])
        else:
            reinterp_ppg.append(f(t_temp))

    #write to csv files

    a = np.array(reinterp_ppg)
    np.savetxt(file_dir_mx800+'/'+"ppg.csv", reinterp_ppg, delimiter=",")

    import matplotlib.pyplot as plt

    plt.plot(reinterp_ppg)
    plt.show()
