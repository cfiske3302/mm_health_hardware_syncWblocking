import numpy as np
import os
import scipy
from scipy import interpolate
import matplotlib.pyplot as plt

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
        # print(time_obj.timestamp())
    
    return np.array(ts)

def extract_data(input_filepath):
    file = open(input_filepath, 'r', encoding='utf-8-sig')
    csvreader = csv.reader(file)
    stamp_list = []
    idx =3
    
    path = os.path.dirname(input_filepath)
    filename_ext = os.path.basename(input_filepath)
    filename = os.path.splitext(filename_ext)[0]

    if(filename == "MPDataExport"):
        # This skips the first row of the CSV file.
        next(csvreader)
        idx = 13
    
    for i in csvreader:
        stamp_list.append(i)

    mx_stamps = []
    sys_stamps = []
    data = []

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

        data.append(int(stamp_list[j][idx]))

        # print(stamp_mx, stamp_sys)

    return mx_stamps, sys_stamps, data
        
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

def interpolate_timestamp(sensor, vital_sign, path):
    if (sensor == "rgbd" or sensor == "rgb" or sensor == "nir" or sensor == "polarized" or sensor == "thermal" or sensor == "uv" ): # or "audio"
        filepath_vid = os.path.join(path, sensor + "_local.txt")

        if (vital_sign == "ppg"):
            filepath_vs = os.path.join(path, "NOM_PLETHWaveExport.csv")
        else: # hr_ppg (#TODO: hr_ECG, Blood Pressure, etc..)
            filepath_vs = os.path.join(path, "MPDataExport.csv")

        print("Interpolating {} signal using {} timestamps".format(vital_sign, sensor) )

        #constucting arrays for the data
        mx_stamps, sys_stamps, data = extract_data(input_filepath=filepath_vs)
        # print("mx_stamps: {}".format(mx_stamps) )
        # print("sys_stamps: {}".format(sys_stamps) )
        # print("data: {}".format(data) )

        delta_array = find_deltas2(sys_stamps, mx_stamps)
        sys_mx_time_delta = np.mean(delta_array)
        # mx_unrolled = unroll_stamps2(mx_stamps)
        ts_data = apply_delta(mx_stamps, sys_mx_time_delta)
        # print("delta_array: {}".format(delta_array) )
        # print(sys_mx_time_delta)
        # # print(mx_unrolled)    
        # print("ts_data: {}".format(ts_data) )

        #loading the time stamp files
        ts_vid = extract_timestamps(filepath_vid)

        # print(ts_data.shape, ts_vid.shape)
        # print(ts_data[0])
        # print(ts_vid[0])

        ##CHECK FOR Data AND TS LENGTHS AND CORRECT
        l1 = len(ts_data)
        l2 = len(data)
        if l1<l2:
            data = data[0:l1]
        elif l2<l1:
            ts_data = ts_data[0:l2]
        # ts_data = ts_data[0:-1]

        ts_data_sec = ts_data 
        ts_vid_sec = ts_vid

        #interpolation function
        f = interpolate.interp1d(ts_data_sec,data,kind='linear')

        reinterp_data = []

        for t_temp in ts_vid_sec:
            if t_temp<ts_data_sec[0]:
                reinterp_data.append(data[0])
            elif t_temp>ts_data_sec[-1]:
                reinterp_data.append(data[-1])
            else:
                reinterp_data.append(f(t_temp))

        #write to csv files

        output = np.array(reinterp_data)
        # filepath_output = os.path.join(path, vital_sign + ".csv")
        # np.savetxt(filepath_output, reinterp_data, delimiter=",")

        plt.plot(reinterp_data)
        plt.show()
        return output

def vital_matrix(sensors_list, vital_sign_list, path): # TODO MAYBE data point number mismatch between cameras (900) and audio (1291)
    num_sensors = len(sensors_list)
    num_vitals = len(vital_sign_list)
    num_datapoints = 900

    vital_matrix = np.empty((num_sensors, num_datapoints, num_vitals))

    v_counter = 0
    s_counter = 0
    for vital in vital_sign_list:
        print(str(vital))
        v_idx = vital_sign_list.index(vital)
        for sensor in sensors_list:
            print(str(sensor))
            s_idx = sensors_list.index(sensor)
            vital_list = interpolate_timestamp(sensor, vital, path)
            vital_arr = np.array(vital_list)
            vital_matrix[s_idx,:,v_idx] = vital_arr
            s_counter += 1
        v_counter += 1

    #save numpy vital matrix
    filepath_output = os.path.join(path, "vital_matrix.npy")
    np.save(filepath_output, vital_matrix)

if __name__ == '__main__':
 
    datafolder_path = r"E:\mmhealth_data\1_3"
    sensors_list = ["rgbd", "nir", "polarized", "thermal"] # "audio" , "rgb", "uv" 
    vital_sign_list = ["ppg", "hr_ppg"]

    vital_matrix(sensors_list, vital_sign_list, datafolder_path)