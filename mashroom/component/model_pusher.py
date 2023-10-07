import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
from mashroom.entity.config_entity import ModelPusherConfig
from mashroom.entity.artifact_entity import ModelPusherArtifact,ModelEvulationArtifact
import shutil

class ModelPusher:

    def __init__(self,model_pusher_config:ModelPusherConfig,
                model_evulation_artifact:ModelEvulationArtifact):
        try:
            logging.info(f"{'>>'*20}Model Pusher log started.{'<<'*20} \n\n")
            self.model_pusher_config = model_pusher_config
            self.model_evulation_artifact = model_evulation_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def export_model_dir(self):
        try:
            logging.info(f"export model dir function started")
            export_model_dir = self.model_pusher_config.export_dir_path
            logging.info(f"export model dir is : {export_model_dir}")
            os.makedirs(export_model_dir,exist_ok=True)

            trained_model_file = self.model_evulation_artifact.evulation_model_file_path
            shutil.copy(src = trained_model_file,dst=export_model_dir)

            logging.info(f"model export completed")
            model_pusher_artifact = ModelPusherArtifact(export_dir_path=export_model_dir)
            return model_pusher_artifact
        

        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intiate_model_pusher(self):
        try:
            logging.info(f"intiate model pusher function started")
            return self.export_model_dir()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def __del__(self):
        logging.info(f"{'>>'*20}Model Pusher log completed.{'<<'*20} \n\n")
