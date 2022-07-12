import sys
from alerting.alert import Alerting
from stages import Stage
from stages.acquisition import Acquisition
from stages.extraction import Extraction
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

    # TODO: Create 1 other pipeline stage, pass successor
    # STAGE: Extraction
    stage_extraction = Extraction(None)
    # STAGE: Typing
    stage_typing = Typing(stage_extraction)
    stage_typing.attach(alerting_observer)
    # STAGE: Filter
    stage_filter = RequestFilter(stage_typing)
    stage_filter.attach(alerting_observer)
    # STAGE: Acquisition
    stage_acquisition = Acquisition(stage_filter, host)

    # start pipeline maintenance jobs
    maintenance_jobs(stage_typing)

    # Start Pipeline
    stage_acquisition.run(None)


def maintenance_jobs(typing_stage: Stage) -> None:
    """
    This methode contains all maintenance jobs for the data pipeline
    """
    # Start the aggregation task for the typing stage
    typing_stage.aggregate()


if __name__ == '__main__':
    init_pipeline()
