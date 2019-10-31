import os

def create_dir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    except:
        raise Exception("Unknown error occured")

def is_dir_empty(dirname):
    num_files = len(os.listdir(dirname))
    if num_files == 0:
        return True
    return False
