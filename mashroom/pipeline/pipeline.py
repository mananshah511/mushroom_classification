import os,sys
from mashroom.exception import MashroomException
from mashroom.logger import logging
from mashroom.config.configuration import Configuration
from mashroom.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformArtifact,ModelTrainerArtifact,ModelEvulationArtifact,ModelPusherArtifact
from mashroom.component.data_ingestion import DataIngestion
from mashroom.component.data_validation import DataValidation
from mashroom.component.data_transform import DataTransform
from mashroom.component.model_trainer import ModelTrainer
from mashroom.component.model_evulation import ModelEvulation
from mashroom.component.model_pusher import ModelPusher

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

    def start_data_transform(self,data_ingestion_artifact:DataIngestionArtifact,
                             data_validation_artifact:DataValidationArtifact)->DataTransformArtifact:
        try:
            data_tranform = DataTransform(data_ingestion_artifact=data_ingestion_artifact,
                                          data_validation_artifact=data_validation_artifact,
                                          data_transform_config=self.cofig.get_data_transform_config())
            return data_tranform.intiate_data_transform()
            
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def start_model_trainer(self,data_transform_artifact:DataTransformArtifact)->ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(data_transform_artifact=data_transform_artifact,
                                         model_trainer_config=self.cofig.get_model_trainer_config())
            return model_trainer.intitate_model_trainer()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def start_model_evulation(self,data_transform_artifact:DataTransformArtifact,
                              data_validation_artifact:DataValidationArtifact,
                              model_trainer_artifact:ModelTrainerArtifact)->ModelEvulationArtifact:
        try:
            model_evulation = ModelEvulation(data_transform_artifact=data_transform_artifact,
                                             model_trainer_artifact=model_trainer_artifact,
                                             data_validation_artifact=data_validation_artifact,
                                             model_evulation_config=self.cofig.get_model_evualtion_config())
            return model_evulation.intiate_model_evulation()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def start_model_pusher(self,model_evulation_artifact:ModelEvulationArtifact)->ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(model_evulation_artifact=model_evulation_artifact,
                                       model_pusher_config=self.cofig.get_model_pusher_config())
            return model_pusher.intiate_model_pusher()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transform_artifact = self.start_data_transform(data_ingestion_artifact=data_ingestion_artifact,
                                        data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transform_artifact=data_transform_artifact)
            model_evulation_artifact = self.start_model_evulation(data_transform_artifact=data_transform_artifact,
                                                                  data_validation_artifact=data_validation_artifact,
                                                                  model_trainer_artifact=model_trainer_artifact)
            model_pusher_artifact = self.start_model_pusher(model_evulation_artifact=model_evulation_artifact)
        except Exception as e:
            raise MashroomException(sys,e) from e