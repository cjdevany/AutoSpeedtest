import sys, datetime, time, speedtest, schedule, argparse

"""
TODO:
    -get a setup.py file ready for installation purposes
    -Introduce handling for the verbosity flag and the duration flag
"""

### Global Variables ###
VERBOSE = False
FREQUENCY = None
OUTPUT_FILE = ''
DURATION = -1

### Functions ###
def init(args):
    # init() takes parser.parse_args() and will populate the flags & global variables.
    global VERBOSE, FREQUENCY, OUTPUT_FILE, DURATION
    if args.verbose:
        VERBOSE = True
    FREQUENCY = args.frequency
    OUTPUT_FILE = args.filename
    DURATION = args.duration

    # create the output file if it doesn't already exist
    try:
        header = "Download, Upload, Ping, Timestamp"
        f = open(OUTPUT_FILE, 'x')
        f.write(f"{header}\n")
        f.close()
    except FileExistsError:
        sys.exit(f'A file with the name "{OUTPUT_FILE}" already exists.')


def get_test():
    """Runs a speedtest, then returns a dictionary of the result. Speeds are in bytes per second."""
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


def write_results(results):
    # writes results dictionary to the csv file
    with open(OUTPUT_FILE, 'a') as file:
        file.write(parse_results(results))


def run_and_record_test():
    # and here's the reason everything else was written!
    write_results(get_test())


def print_results(results):
    for key in results:
        print(f"{key} -> {results[key]}")


### Main ###
if __name__ == "__main__":
    ### Set up command line arguments ###
    parser = argparse.ArgumentParser()

    # mandatory positional arguments
    parser.add_argument("frequency", help="How often the speed test will run in minutes.", type=int, metavar="frequency")
    parser.add_argument("filename", help="The filename to output results into.", metavar="output_filename")

    # optional arguments
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-d", "--duration", help="Sets the number of tests to run before quitting.", action="store", type=int, metavar="numTests")

    init(parser.parse_args())    

    schedule.every(FREQUENCY).minutes.do(run_and_record_test)

    # If DURATION wasn't changed, loop permanently.
    if DURATION != -1:
        for i in range(DURATION):
            schedule.run_pending()
            time.sleep(1)

        sys.exit()
    else:
        while True:
                schedule.run_pending()
                time.sleep(1)