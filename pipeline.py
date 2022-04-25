import sys
from stages.acquisition import Acquisition
from stages.filter import RequestFilter

host = ''
mode = ''


def init_pipeline():
    print("Initializing Pipeline")

    if len(sys.argv) != 3:
        sys.exit("Illegal amount of arguments")

    global host
    host = sys.argv[1]
    global mode
    mode = sys.argv[2]

    print(f"Running pipeline with host {host} and mode {mode}")

    # TODO: Create 3 other pipeline stages, pass every successor
    stage_filter = RequestFilter(None, None)
    acquisition = Acquisition(stage_filter, host)
    
    # Start Pipeline
    acquisition.run(None)


if __name__ == '__main__':
    init_pipeline()
