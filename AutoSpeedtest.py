import sys, datetime, time, speedtest, schedule, argparse

"""
TODO:
    -get a setup.py file ready for installation purposes
    -Introduce handling for the verbosity flag
"""

### Global Variables ###
VERBOSE = False
FREQUENCY = None
APPEND = False
OUTPUT_FILE_NAME = ''
DURATION = -1
NUM_TESTS_PERFORMED = 0

### Functions ###
def init(args):
    # init() takes parser.parse_args() and will populate the flags & global variables.
    global VERBOSE, FREQUENCY, OUTPUT_FILE_NAME, DURATION
    if args.verbose:
        VERBOSE = True
    FREQUENCY = args.frequency
    OUTPUT_FILE_NAME = args.filename
    DURATION = args.duration
    APPEND = args.append

    # create the output file if it doesn't already exist    
    if not APPEND:
        try:
            header = "Download, Upload, Ping, Timestamp"
            f = open(OUTPUT_FILE_NAME, 'x')
            f.write(f"{header}\n")
            f.close()
        except FileExistsError:
            sys.exit(f'A file with the name "{OUTPUT_FILE_NAME}" already exists.')


def get_test():
    """Runs a speedtest, then returns a dictionary of the result. Speeds are in bytes per second."""
    global NUM_TESTS_PERFORMED
    NUM_TESTS_PERFORMED += 1
    current_time = datetime.datetime.now()
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download()
        s.upload()
        results = s.results.dict()
        return {
            "download"  : results["download"],
            "upload"    : results["upload"],
            "ping"      : results["ping"],
            "timestamp" : current_time
        }
    except speedtest.ConfigRetrievalError:
        return {
            "download"  : 0,
            "upload"    : 0,
            "ping"      : -1,
            "timestamp" : current_time
        }


def scale_bps(bps):
    # Takes a value in bytes per second
    # Returns a string with the value converted (if necessary) to a more appropriate unit.
    if bps > 1000000:       # convert to Mbps
        return str(round(bps / 1000000, 2)) + " Mbps"
    elif bps > 1000:        # convert to Kbps
        return str(round(bps / 1000, 2)) + " Kbps"
    else:                   # leave at Bps
        return str(bps) + " Bps"


def parse_results(results):
    # Takes the results dictionary and returns a comma separated line
    return f"{scale_bps(results['download'])}, {scale_bps(results['upload'])}, {str(round(results['ping'], 1))} ms, {results['timestamp']}\n"


def run_and_record_test():
    with open(OUTPUT_FILE_NAME, 'a') as file:
        test = get_test()
        file.write(parse_results(test))


### Main ###
if __name__ == "__main__":
    ### Set up command line arguments ###
    parser = argparse.ArgumentParser()

    # mandatory positional arguments
    parser.add_argument("frequency", help="How often the speed test will run in minutes.", type=int, metavar="frequency")
    parser.add_argument("duration", help="How many tests to run before quitting. 0 = loop indefinitely.", type=int, metavar="duration")
    parser.add_argument("filename", help="The filename to output results into.", metavar="output_filename")

    # optional arguments
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-a", "--append", help="Open an existing log file and append rather than creating a new file.", action="store_true")

    init(parser.parse_args())    

    schedule.every(FREQUENCY).minutes.do(run_and_record_test)

    while True:
        schedule.run_pending()
        time.sleep(1)
        if NUM_TESTS_PERFORMED == DURATION:
            sys.exit()