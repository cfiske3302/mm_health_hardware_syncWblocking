import multiprocessing as mp
import time
from progressbar import progressbar

from sensors.config import *
from sensors.nir_sensor import *
from sensors.polarized_sensor import *
from sensors.rgb_sensor import *
from sensors.rgbd_sensor import *
from sensors.uv_sensor import *
from sensors.thermal_sensor import *
from sensors.audio_sensor import *
from sensors.mx800_sensor import *
from sensors.rf_sensor import *
import sensors.sensor
from postproc.data_interpolation import *
from postproc.tiff_to_avi import *

def cleanup_mx800(folder_name):
    file_list = ['MPrawoutput.txt','NOM_ECG_ELEC_POTL_IIWaveExport.csv','NOM_PLETHWaveExport.csv', 'MPDataExport.csv']
    for file in file_list:
        shutil.move(file, os.path.join(folder_name, file)) #os.replace cannot copy files across drives
        # os.remove(file)

wait_time = 3 #MX800 wait time to ensure that it begins recording before any sensor does.
calibrate_mode = config.getint("mmhealth", "calibration_mode") 

def mic_main(acquisition_time, folder_name, synchronizer):
    mic = Audio_Sensor(filename="audio", foldername=folder_name)
    print("Ready mic")
    synchronizer.wait()
    time.sleep(wait_time)
    mic.acquire(acquisition_time = acquisition_time)

def webcam_main(acquisition_time, folder_name, synchronizer):
    webcam = Audio_Sensor(filename="webcam_audio", foldername=folder_name)
    print("Ready webcam")
    synchronizer.wait()
    time.sleep(wait_time)
    webcam.acquire(acquisition_time = acquisition_time)

def nir_main(acquisition_time, folder_name, synchronizer, verbose=False):
    nir_cam = NIR_Sensor(filename="nir", foldername=folder_name)
    print("Ready nir")
    synchronizer.wait()
    time.sleep(wait_time)
    nir_cam.acquire(acquisition_time = acquisition_time)
    if(verbose):
        nir_cam.print_stats()

def polarized_main(acquisition_time, folder_name, synchronizer):
    polarized_cam = Polarized_Sensor(filename="polarized", foldername=folder_name)
    print("Ready polarized cam")
    synchronizer.wait()
    time.sleep(wait_time)
    polarized_cam.acquire(acquisition_time = acquisition_time)

def rgb_main(acquisition_time, folder_name, synchronizer):
    rgb_cam = RGB_Sensor(filename="rgb", foldername=folder_name)
    print("Ready rgb cam")
    synchronizer.wait()
    time.sleep(wait_time)
    rgb_cam.acquire(acquisition_time = acquisition_time)

def rgbd_main(acquisition_time, folder_name, synchronizer):
    rgbd_cam = RGBD_Sensor(filename="rgbd", foldername=folder_name)
    print("Ready rgbd cam")
    synchronizer.wait()
    time.sleep(wait_time)
    rgbd_cam.acquire(acquisition_time = acquisition_time)

def uv_main(acquisition_time, folder_name, synchronizer):
    uv_cam = UV_Sensor(filename="uv", foldername=folder_name)
    print("Ready uv cam")
    synchronizer.wait()
    time.sleep(wait_time)
    uv_cam.acquire(acquisition_time = acquisition_time)

def thermal_main(acquisition_time, folder_name, synchronizer):
    thermal_cam = Thermal_Sensor(filename="thermal", foldername=folder_name)
    print("Ready thermal cam")
    synchronizer.wait()
    time.sleep(wait_time)
    thermal_cam.acquire(acquisition_time = acquisition_time)

def rf_main(acquisition_time, folder_name, synchronizer, sensor_on=True):
    rf_s = RF_Sensor(filename="rf", foldername=folder_name, sensor_on=sensor_on)
    if(not sensor_on):
        time.sleep(120) #two minutes warm up time of the RF
    print("Ready rf device")
    synchronizer.wait()
    time.sleep(wait_time)
    rf_s.acquire(acquisition_time = acquisition_time)

def mx800_main(acquisition_time, folder_name, synchronizer):
    mx800_instance = MX800_Sensor(filename="mx800", foldername=folder_name)
    print("Ready mx800 device")
    synchronizer.wait()
    mx800_instance.acquire(acquisition_time = acquisition_time+wait_time + 2)

def progress_main(acquistion_time, folder_name, synchronizer):
    synchronizer.wait()
    time.sleep(wait_time)
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
    # sensors_list = [rgbd_main, nir_main, polarized_main, thermal_main, rf_main, mic_main, mx800_main, progress_main]
    
    if(calibrate_mode == 1):
        sensors_list = [rgbd_main, nir_main, polarized_main, thermal_main]
    else:
        sensors_list = [nir_main, progress_main]
    jobs = []
    num_sensors = len(sensors_list) #RGB, NIR, Polarized, Webcam Audio, Mic Audio
    time_acquire = config.getint("mmhealth", "acquire_time") #seconds
    sync_barrior = mp.Barrier(num_sensors)
    #-------------------- Folder Config ---------------------------
    folder_name = "1"
    folder_name += "_"
    start_num = 1
    data_folder_name = os.path.join(config.get("mmhealth", "data_path"), folder_name)

    while(os.path.exists(data_folder_name + str(start_num))):
        start_num += 1
    data_folder_name += str(start_num)
    folder_name += str(start_num)
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
            tiff_to_avi(os.path.join(data_folder_name, file))
    
    if(sensors_list.count(mx800_main) != 0):
        cleanup_mx800(data_folder_name)
        interpolate_ppg_timestamp(sensor_file_name="rgbd_local.txt", file_dir_mx800=data_folder_name)
