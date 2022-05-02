import sys
from alerting.alert import Alerting
from stages.acquisition import Acquisition
from stages.filter import RequestFilter
from stages.typing import Typing

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

    alerting_observer = Alerting()

    # TODO: Create 2 other pipeline stages, pass every successor
    # STAGE: Typing
    stage_typing = Typing(None)
    # STAGE: Filter
    stage_filter = RequestFilter(stage_typing)
    stage_filter.attach(alerting_observer)
    # STAGE: Acquisition
    stage_acquisition = Acquisition(stage_filter, host)
    
    # Start Pipeline
    stage_acquisition.run(None)


if __name__ == '__main__':
    init_pipeline()
