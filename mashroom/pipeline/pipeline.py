import os,sys
from mashroom.exception import MashroomException
from mashroom.logger import logging
from mashroom.config.configuration import Configuration
from mashroom.entity.artifact_entity import DataIngestionArtifact
from mashroom.component.data_ingestion import DataIngestion

class Pipeline:

    def __init__(self,config:Configuration=Configuration()) -> None:
        try:
            self.cofig = config
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.cofig.get_data_ingestion_config())
            return data_ingestion.intiate_data_ingestion()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
        except Exception as e:
            raise MashroomException(sys,e) from e