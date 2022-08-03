from time import sleep
from typing import Dict
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, TypingExtractionDTO, ExtractionModelDTO
import sys
from type import Type
import os
import importlib
from database import DatabaseHandler


class ExtractionPluginInterface:
    """
    This class defines the default method that must be implemented in all extraction plugins.

    Methods
    ----------
    extract_features(message, type)
        Extracts and returns the features for the following ML-algorithm based on the type.
    """

    def extract_features(self, message: IDSHTTPMessage, type: Type, mode: str, db_handler: DatabaseHandler) -> Dict:
        """
        This method extracts and returns the features for the following ML-algorithm based on the type.

        Parameters
        ----------
        message: IDSHTTPMessage
            The HTTP message from which the features should be extracted.
        type: Type
            The type of the HTTP message.
        mode: str
            The mode of the pipeline.
        db_handler: DatabaseHandler
            The database handler.

        Returns
        ----------
        list
            The list of the extracted features.
        """
        pass


class Extraction(Stage):
    """
    This class represents the fourth stage of the ML-IDS pipeline.
    This stage extracts the features from a HTTP request for the following ML model.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
    mode: str
        The mode of the pipeline ("train" or "test")
    logging: bool
        The logging mode
    db_handler: DatabaseHandler
        The handler for the database connection.

    Methods
    ----------
    run(dto)
        The method that gets called by the previous stage.
    """

    def __init__(self, successor: 'Stage', mode: str, logging: bool, db_handler: DatabaseHandler):
        """
        Parameters
        ----------
        successor: Stage
            The stage that follows this stage in the pipeline.
        mode: str
            The mode of the pipeline ("train" or "test")
        logging: bool
            The logging mode
        db_handler: DatabaseHandler
            The handler for the database connection.
        """

        self.successor = successor
        if len(os.listdir('./stages/extraction/plugins')) == 0:
            sys.exit("No extraction plugin detected. Please place default extraction plugin in the extraction plugin directory.")
        sys.path.append('./stages/extraction/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin(db_handler)
            for f in next(os.walk('stages/extraction/plugins'))[2]
        ]
        self.mode = mode
        self.logging = logging
        self.db_handler = db_handler
        #Workaround labeling
        self.label = 1


    def run(self, dto: DTO) -> None:
        """
        The method that gets called by the previous stage.

        Parameters
        ----------
        dto: DTO
            The data transfer object that is received from the previous stage.
        """
        
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        features = {}
        for plugin in self.plugins:
            temp_features = plugin.extract_features(dto.message, dto.type, self.mode, self.db_handler, self.label)
            features.update(temp_features)
        
        if self.mode == "train":
            # Save everything in the db so the ML model can use the data for training
            data = {
                "features": features,
                "message": dto.message,
                "type": dto.type,
                "label": self.label
            }
            self.db_handler.set_strategy(self.db_handler.data_strategy)
            self.db_handler.write(data, "data")
            self.db_handler.set_strategy(None)

        new_dto = ExtractionModelDTO(features=features, type=dto.type)
        self.successor.run(new_dto)
