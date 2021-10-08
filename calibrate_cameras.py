import multiprocessing as mp
import time
from progressbar import progressbar
import cv2
import matplotlib.pyplot as plt
import numpy as np

from sensors.config import *
from sensors.nir_sensor import *
from sensors.polarized_sensor import *
from sensors.rgb_sensor import *
from sensors.rgbd_sensor import *
from sensors.uv_sensor import *
from sensors.thermal_sensor import *
import sensors.sensor
from postproc.data_interpolation import *
from postproc.tiff_to_avi import *

def nir_main(acquisition_time, folder_name, synchronizer, verbose=False):
    nir_cam = NIR_Sensor(filename="nir_1", foldername=folder_name)
    print("Ready nir")
    synchronizer.wait()
    nir_cam.acquire(acquisition_time = acquisition_time)
    if(verbose):
        nir_cam.print_stats()

def polarized_main(acquisition_time, folder_name, synchronizer):
    polarized_cam = Polarized_Sensor(filename="polarized_1", foldername=folder_name)
    print("Ready polarized cam")
    synchronizer.wait()
    polarized_cam.acquire(acquisition_time = acquisition_time)

def rgb_main(acquisition_time, folder_name, synchronizer):
    rgb_cam = RGB_Sensor(filename="rgb_1", foldername=folder_name)
    print("Ready rgb cam")
    synchronizer.wait()
    rgb_cam.acquire(acquisition_time = acquisition_time)

def rgbd_main(acquisition_time, folder_name, synchronizer):
    rgbd_cam = RGBD_Sensor(filename="rgbd_1", foldername=folder_name)
    print("Ready rgbd cam")
    synchronizer.wait()
    rgbd_cam.acquire(acquisition_time = acquisition_time)

def uv_main(acquisition_time, folder_name, synchronizer):
    uv_cam = UV_Sensor(filename="uv_1", foldername=folder_name)
    print("Ready uv cam")
    synchronizer.wait()
    uv_cam.acquire(acquisition_time = acquisition_time)

def thermal_main(acquisition_time, folder_name, synchronizer):
    thermal_cam = Thermal_Sensor(filename="thermal_output_1", foldername=folder_name)
    print("Ready thermal cam")
    synchronizer.wait()
    thermal_cam.acquire(acquisition_time = acquisition_time)

def progress_main(acquistion_time, folder_name, synchronizer):
    synchronizer.wait()
    print("\nProgress:")
    for i in progressbar(range(acquistion_time)):
        time.sleep(1)
    print("\n")


if __name__ == '__main__':

    #Start
    start = time.time()
    #-------------------- Sensor Config ---------------------------
    # sensors = [rgb_main, nir_main, polarized_main, mic_main, webcam_main, mx800_main]
    # sensors = [rgb_main, nir_main, polarized_main, mic_main, webcam_main] #thermal_main, polarized_main
    # sensors_list = [rgbd_main, nir_main, polarized_main, progress_main]  
    sensors_list = [rgbd_main, nir_main, polarized_main, thermal_main, progress_main]
    jobs = []
    num_sensors = len(sensors_list) #RGBD, NIR, Polarized, Thermal
    time_acquire = config.getint("mmhealth", "acquire_time") #seconds to give 1 frame
    sync_barrior = mp.Barrier(num_sensors)
    #-------------------- Folder Config ---------------------------
    folder_name = "calibration"
    data_folder_name = os.path.join(config.get("mmhealth", "data_path"), folder_name)
    os.makedirs(data_folder_name)
    #-------------------- Start Sensors ----------------------------
    for sensor in sensors_list:
        proc = mp.Process(target=sensor, args= (time_acquire,folder_name,sync_barrior))
        jobs.append(proc)
        proc.start()

    for job in jobs:
        job.join() 

    end = time.time()
    print("Time taken: {}".format(end-start))
    
    #--------------------- Post-Processing ---------------------------
    
    # find all tiff files, store their paths in a list
    file_list = os.listdir(data_folder_name)
    #for loop, iterate through each filepath and do the conversion
    for file in file_list:
        filename_ext = os.path.basename(file)
        ext = os.path.splitext(filename_ext)[1]
        if (ext == ".tiff"):
            tiff_to_avi(os.path.join(data_folder_name, file)) # change to tiff_to_jpeg? and display

    im_dict = {}
    for file in file_list:
        filename_ext = os.path.basename(file)
        filename, ext = os.path.splitext(filename_ext)
        if (ext == ".jpeg"):
            img = cv2.imread(file)
            im_dict.update({filename: img})

    num_imgs = num_sensors - 1
    rows = round(num_imgs/2)
    cols = 2
    axes = []
    fig = plt.figure()

    counter = 0
    for key in range(im_dict):
        image = im_dict[key]
        axes.append( fig.add_subplot(rows, cols, counter+1) )
        subplot_title=(key)
        axes[-1].set_title(subplot_title)  
        plt.imshow(image)
        counter += 1
    fig.tight_layout()
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()    
    plt.show()
    #accept user key stroke after all images displayed to either leave saved or to delete (both tiff and jpeg)
