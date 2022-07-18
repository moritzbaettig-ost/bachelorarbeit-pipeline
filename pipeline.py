import sys
from alerting.alert import Alerting
from stages import Stage
from stages.acquisition import Acquisition
from stages.extraction import Extraction
from stages.filter import RequestFilter
from stages.model import Model
from stages.typing import Typing
import argparse


def init_pipeline():
    print("Initializing Pipeline")
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=None)
    parser.add_argument('--mode', choices=['train', 'test'], default='test')
    parser.add_argument('--logging', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    if len(sys.argv) > 4 or len(sys.argv) < 3:
        sys.exit("Illegal amount of arguments")

    print(f"Running pipeline with host {args.host} and mode {args.mode}")
    if args.logging:
        print("Logging activated")

    alerting_observer = Alerting()

    # STAGE: Model
    stage_model = Model(args.mode)
    # STAGE: Extraction
    stage_extraction = Extraction(stage_model, args.mode, args.logging)
    # STAGE: Typing
    stage_typing = Typing(stage_extraction)
    stage_typing.attach(alerting_observer)
    # STAGE: Filter
    stage_filter = RequestFilter(stage_typing)
    stage_filter.attach(alerting_observer)
    # STAGE: Acquisition
    stage_acquisition = Acquisition(stage_filter, args.host)
    
    # Start Pipeline
    stage_acquisition.run(None)


if __name__ == '__main__':
    init_pipeline()
