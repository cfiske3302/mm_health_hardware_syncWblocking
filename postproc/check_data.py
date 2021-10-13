# file for postprocessing. Extracts values from data as a sanity check. 
import os
import imageio
import numpy as np

import sys
sys.path.insert(0, r"C:\Users\111\Desktop\mmhealth_2\sensors")
from config import *

video_ids = ["nir", "thermal", "polarized", "rgbd"] # "rgb", "uv"
health_ids = ["ppg.csv"]
mic_ids = ["mic", "webcam"]

def get_data(video_path):
    imarray = imageio.volread(video_path)
    #sample 20 frames
    num_frames = imarray.shape[0]
    random_idxs = np.random.choice(num_frames, size = 20, replace=False)
    imarray = imarray[random_idxs]
    #load timestamps
    # print(video_path)
    path = os.path.dirname(video_path)
    filename_ext = os.path.basename(video_path)
    filename = os.path.splitext(filename_ext)[0]
    if( (filename == "rgbd_depth") or (filename == "rgbd_rgb") ):
        time_stamp_file = os.path.join(path, "rgbd_local.txt")
    else:
        time_stamp_file = os.path.splitext(video_path)[0] + "_local.txt"
    # print(time_stamp_file)
    time_stamps = np.genfromtxt(time_stamp_file, delimiter='\n')
    fps = num_frames / (time_stamps[-1] - time_stamps[0])
    fps_jitter = np.std(np.diff(time_stamps))

    avg_pixel = np.mean(imarray, axis=(0,1,2))
    std_pixel = np.std(imarray, axis = (0,1,2))

    # print('Average Pixel :', avg_pixel)
    # print('STD pixel :', std_pixel)
    # print('(start time , end time) : ({} , {})'.format(time_stamps[0], time_stamps[-1]))
    # print('FPS : ', fps)
    # print('FPS jitter : ', fps_jitter)

    data = [avg_pixel, std_pixel, time_stamps[0], time_stamps[-1], fps, fps_jitter]
    return data

def compare_config(sensors_dict): # compare against input config (avg_pixel_delta, std_pixel_delta [establish empirically], spatial&temporal_resolution/fps or fps_delta, NUM_FRAMES, unit8 vs uint16)
    print_counter = 0
    for sensor_type in sensors_dict:
        [avg_pixel, std_pixel, start_time, end_time, fps, fps_jitter] = sensors_dict[sensor_type]
        data_dict = {"start_time" : start_time, "end_time" : end_time, "fps" : fps, "fps_jitter" : fps_jitter, "avg_pixel" : avg_pixel, "std_pixel" : std_pixel}

        for data_key in data_dict:
            if (data_key == "fps" or data_key == "fps_jitter"):
                config_tag = "mmhealth"
                lower_bound = config.getint(config_tag, data_key) - config.getint(config_tag, data_key + "_delta")
                upper_bound = config.getint(config_tag, data_key) + config.getint(config_tag, data_key + "_delta")
            elif(data_key == "start_time"):
                config_tag = "mmhealth"
                lower_bound = 0
                upper_bound = config.getint(config_tag, data_key + "_delta")
            elif(data_key == "end_time"):
                config_tag = "mmhealth"
                data_key = "acquire_time"
                lower_bound = config.getint(config_tag, data_key) - config.getint(config_tag, data_key + "_delta")
                upper_bound = config.getint(config_tag, data_key) + config.getint(config_tag, data_key + "_delta")
                data_key = "end_time"
            else:
                config_tag = sensor_type
                lower_bound = config.getint(config_tag, data_key) - config.getint(config_tag, data_key + "_delta")
                upper_bound = config.getint(config_tag, data_key) + config.getint(config_tag, data_key + "_delta")

            data_value = data_dict[data_key]
            if (sensor_type == "rgbd" or sensor_type == "rgb" or sensor_type == "uv"):
                data_value = np.mean(data_value)
            if (np.isnan(data_value)):
                data_value = 0
            data_value = int(data_value)
            if data_value not in range(lower_bound, upper_bound):
                print("WARNING: {} {} value: {} not in expected/requested range".format(  sensor_type, data_key, data_value) )
                print("Lower Bound: {}".format( lower_bound ) )
                print("Upper Bound: {}".format(  upper_bound ) )
                print_counter += 1
        
    if (print_counter == 0):
        print("No Warnings Detected!")


def check_distance(sensors_dict): #TODO use rgbd data to confirm range measurement from rf
    pass

def check_data_folder(dir_path):
    file_list = os.listdir(dir_path)
    sensors_dict = {}

    for file in file_list:
        #check video files
        for video in video_ids:
            if video in file:
                if ".tiff" in file:
                    # print(file)
                    # print("video {} stats:".format(video))
                    data = get_data(os.path.join(dir_path, file))
                    sensors_dict.update({video: data})

        #check audio files
        for mic in mic_ids:
            if mic in file:
                if ".wave" in file:
                    pass
                    # print("audio", file)
        #check mx800 files
        for health in health_ids:
            if health in file:
                pass
                # print("health", file)

    print("Comparing against config parameters:")
    compare_config(sensors_dict)
    # print("Comparing sensor start and end times:")
    # compare_sensor_times(sensors_dict)

if __name__ == '__main__':
    check_data_folder(r"E:\mmhealth_data\1_3")