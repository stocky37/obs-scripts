import obspython as obs
import time
import os

WAIT_TIME = "dev.stocky37.props.waitTime"
waitTime = 10

def script_update(settings):
    global waitTime
    obs.obs_data_set_default_int(settings, WAIT_TIME, waitTime)
    waitTime = obs.obs_data_get_int(settings, WAIT_TIME)


def script_load(settings):
    print("Loaded")
    obs.obs_hotkey_register_frontend("dev.stocky37.split", "Split & discard recording", split_and_delete_callback)

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_int(props, WAIT_TIME, "Maximum wait time (s).", 1, 60, 1)
    return props

def get_new_recording_file(old_file):
    global waitTime
    attempts = 0

    new_file = obs.obs_frontend_get_last_recording()
    while new_file == old_file and attempts < waitTime:
        attempts += 1
        print("Attempt {} of {}".format(attempts, waitTime))
        time.sleep(1)
        new_file = obs.obs_frontend_get_last_recording()

    if(attempts == waitTime):
        raise Exception("Split took to long.")

    return new_file


def is_file_ready(path):
    try:
        os.rename(path, path)
    except PermissionError:
        return False
    else:
        return True

def delete_file(path):
    print("Attempting to delete file {}".format(path))
    if os.path.exists(path):
        os.remove(path)

def split_and_delete():
    global waitTime
    old_file = obs.obs_frontend_get_last_recording()
    print("File to delete: {}".format(old_file))
    if obs.obs_frontend_recording_split_file():
        print("Successfully asked to split file.")
        new_file = get_new_recording_file(old_file)
        delete_file(old_file)
        print("New recording file: {}".format(new_file))

def split_and_delete_callback(pressed):
    if(pressed):
        split_and_delete()
