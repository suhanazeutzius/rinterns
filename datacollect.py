def datacollect(filename=None, scriptpath=None):
    """Run 2 channel data collection
    
    @param filename -- optional string filename
    @param scriptpath -- optional path to script
    @return status code of script
    """
    import subprocess
    import time

    if filename is None:
        t = time.ctime(time.time())
        t = t.replace(' ', '_')
        t = t.replace(':', '_')

        filename = "./data/sample_" + t

    if scriptpath is None:
        scriptpath = "./datacollect.sh"

    ret_code = (subprocess.run(["bash", scriptpath, filename])).returncode
    if ret_code:
        print("Script failed: returned " + str(ret_code))
    
    return ret_code


if __name__ == "__main__":
    datacollect()
