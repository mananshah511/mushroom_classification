import os,sys
from mashroom.exception import MashroomException
from mashroom.logger import logging
from mashroom.config.configuration import Configuration
from mashroom.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from mashroom.component.data_ingestion import DataIngestion
from mashroom.component.data_validation import DataValidation


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
        
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact)->DataValidationArtifact:
        try:
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=self.cofig.get_data_validation_config())
            return data_validation.intiate_data_validation()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
        except Exception as e:
            raise MashroomException(sys,e) from e