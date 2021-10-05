import configparser
import os
import sys

config = configparser.ConfigParser()
config.read( r"C:\Users\111\Desktop\mmhealth_2\sensors\configs\sensors_config.ini")
sys.path.insert(0, r"C:\Users\111\Desktop\mmhealth_2\sensors")

if __name__ == '__main__':

    for section in config.sections():
        print(section)
        section_dict = dict(config[section])
        for key in section_dict:
            print("  {} = {}".format(key,section_dict[key]))
        print()

    print(config.getint('rgb', 'fps'))
    print(config.get("mmhealth", "data_path").encode('unicode_escape'))
    print(os.listdir(config.get("mmhealth", "data_path").encode('unicode_escape')))
    