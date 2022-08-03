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

    Attributes
    ----------
    host: str
            The hostname of the service to be secured
    mode: str
        The mode of the pipeline (train or test)
    logging: bool
        States if file logging should be enabled
    stage_model: Model
        The model stage
    stage_extraction: Extraction
        The extraction stage
    stage_typing: Typing
        The typing stage
    stage_filter: RequestFilter
        The filter stage
    stage_acquisition: Acquisition
        The acquisition stage
        
    Methods
    ----------
    init_pipeline()
        Initializes the pipeline. This method is called on startup.
    """

    def __init__(self, host: str, mode: str, logging: bool) -> None:
        """
        Parameters
        ----------¨
        host: str
            The hostname of the service to be secured
        mode: str
            The mode of the pipeline (train or test)
        logging: bool
            States if file logging should be enabled
        """

        self.host = host
        self.mode = mode
        self.logging = logging


    def init_pipeline(self):
        print(f"Running pipeline with host {self.host} and mode {self.mode}")
        if self.logging:
            print("Logging activated")

        alerting_observer = Alerting(self.logging)
        self.database_handler = DatabaseHandler()

        # STAGE: Model
        self.stage_model = Model(None, self.mode, self.database_handler)
        self.stage_model.attach(alerting_observer)
        # STAGE: Extraction
        self.stage_extraction = Extraction(self.stage_model, self.mode, self.logging, self.database_handler)
        # STAGE: Typing
        self.stage_typing = Typing(self.stage_extraction)
        self.stage_typing.attach(alerting_observer)
        # STAGE: Filter
        self.stage_filter = RequestFilter(self.stage_typing)
        self.stage_filter.attach(alerting_observer)
        # STAGE: Acquisition
        self.stage_acquisition = Acquisition(self.stage_filter, self.host)
        
        # Start Pipeline
        self.stage_acquisition.run(None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=None)
    parser.add_argument('--mode', choices=['train', 'test'], default='test')
    parser.add_argument('--logging', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    if len(sys.argv) > 4 or len(sys.argv) < 3:
        sys.exit("Illegal amount of arguments")
    
    pipeline = Pipeline(args.host, args.mode, args.logging)
    pipeline.init_pipeline()
