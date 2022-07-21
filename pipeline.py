import sys
from alerting.alert import Alerting
from stages.acquisition import Acquisition
from stages.extraction import Extraction
from stages.filter import RequestFilter
from stages.model import Model
from stages.typing import Typing
import argparse
from database import DatabaseHandler


class Pipeline:
    """
    This class represents the Inversion of Control Container of the Pipeline structure.
    It creates all instances of the stages and passes all the references.

    Methods
    ----------
    init_pipeline()
        Initializes the pipeline. This method is called on startup.
    """

    def init_pipeline(self):
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
        database_handler = DatabaseHandler()

        # STAGE: Model
        stage_model = Model(None, args.mode, database_handler)
        stage_model.attach(alerting_observer)
        # STAGE: Extraction
        stage_extraction = Extraction(stage_model, args.mode, args.logging, database_handler)
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
    pipeline = Pipeline()
    pipeline.init_pipeline()
