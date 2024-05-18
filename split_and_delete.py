import obspython as obs
import time
import os

class Hotkey:
    _prefix = "dev.stocky37.hk"
    def __init__(self, id, description, callback, obs_settings):
        self.obs_data = obs_settings
        self.hotkey_id = obs.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self._id = id
        self.description = description
        self.callback = callback

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def id(self):
        return "{}.{}".format(self._prefix, self._id)

    def register_hotkey(self):
        self.hotkey_id = obs.obs_hotkey_register_frontend(self.id(), self.description, self.callback)
        obs.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        self.hotkey_saved_key = obs.obs_data_get_array(self.obs_data, self.id())
        obs.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        self.hotkey_saved_key = obs.obs_hotkey_save(self.hotkey_id)
        obs.obs_data_set_array(self.obs_data, self.id(), self.hotkey_saved_key)
        obs.obs_data_array_release(self.hotkey_saved_key)


WAIT_TIME = "dev.stocky37.props.waitTime"
waitTime = 10
hotkey = None

def script_update(settings):
    global waitTime
    obs.obs_data_set_default_int(settings, WAIT_TIME, waitTime)
    waitTime = obs.obs_data_get_int(settings, WAIT_TIME)

def script_load(settings):
    print("Loaded.")
    global hotkey
    hotkey = Hotkey("split_delete", "Split & Discard Recording", split_and_delete_callback, settings)

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_int(props, WAIT_TIME, "Maximum wait time (s).", 1, 60, 1)
    return props

def script_save(_):
    hotkey.save_hotkey()

def split_and_delete_callback(pressed):
    if(pressed):
        split_and_delete()


def split_and_delete():
    old_file = obs.obs_frontend_get_last_recording()
    print("File to delete: {}".format(old_file))
    if obs.obs_frontend_recording_split_file():
        print("Successfully asked to split file.")
        new_file = get_new_recording_file(old_file)
        delete_file(old_file)
        print("New recording file: {}".format(new_file))

def get_new_recording_file(old_file):
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
