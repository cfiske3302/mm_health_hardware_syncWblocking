# file for postprocessing. Extracts values from data as a sanity check. 
import os
import imageio
import numpy as np
from config import *

video_ids = ["nir", "thermal", "polarized", "rgb_", "rgbd"]
health_ids = ["ppg.txt"]
mic_ids = ["mic", "webcam"]

def check_data_folder(dir_path):
    file_list = os.listdir(dir_path)
    sensors_dict = {}

    for file in file_list:
        #check video files
        for video in video_ids:
            if video in file:
                if ".tiff" in file:
                    # print("video {} stats:".format(video))
                    data = get_data(os.path.join(dir_path, file))
                    sensors_dict.update({video: data})

        #check audio files
        for mic in mic_ids:
            if mic in file:
                if ".wave" in file:
                    print("audio", file)
        #check mx800 files
        for health in health_ids:
            if health in file:
                print("health", file)

    print("Comparing against config parameters:")
    compare_config(sensors_dict)
    # print("Comparing sensor start and end times:")
    # compare_sensor_times(sensors_dict)

def get_data(video_path):
    imarray = imageio.volread(video_path)
    #sample 20 frames
    num_frames = imarray.shape[0]
    random_idxs = np.random.choice(num_frames, size = 20, replace=False)
    imarray = imarray[random_idxs]
    #load timestamps
    time_stamp_file = os.path.splitext(video_path)[0] + ".txt"
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
    for sensor_type in sensors_dict:
        [avg_pixel, std_pixel, start_time, end_time, fps, fps_jitter] = sensors_dict[sensor_type]
        data_dict = {"start_time" : start_time, "end_time" : end_time, "fps" : fps, "fps_jitter" : fps_jitter, "avg_pixel" : avg_pixel, "std_pixel" : std_pixel}

        for data_key in data_dict:
            if (data_key == "start_time" or "end_time" or "fps" or "fps_jitter"):
                config_tag = "mmhealth"
            else:
                config_tag = sensor_type
            data_value = data_dict[data_key]
            if(data_key == "start_time"):
                lower_bound = 0
                upper_bound = config.getint(config_tag, data_key + "_delta")
            else:
                lower_bound = config.getint(config_tag, data_key) - config.getint(config_tag, data_key + "_delta")
                upper_bound = config.getint(config_tag, data_key) + config.getint(config_tag, data_key + "_delta")

            if data_value not in range(lower_bound, upper_bound):
                print("WARNING: {} {} value: {} not in expected/requested range", sensor_type, data_key, data_value)
                print("Lower Bound: {}", lower_bound )
                print("Upper Bound: {}", upper_bound )

def check_distance(sensors_dict): #TODO use rgbd data to confirm range measurement from rf
    pass

if __name__ == '__main__':
    check_data_folder(r"C:\Temp\mmhealth_data\99_1")