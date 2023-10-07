import os,sys
from mashroom.exception import MashroomException
from mashroom.logger import logging
from mashroom.entity.artifact_entity import ModelEvulationArtifact,ModelTrainerArtifact,DataTransformArtifact,DataValidationArtifact
from mashroom.entity.config_entity import ModelEvulationConfig
import numpy as np
import pandas as pd
from mashroom.util.util import read_yaml,write_yaml_file,load_object
from mashroom.entity.model_factory import get_evulated_classification_model
from mashroom.constant import *


class ModelEvulation:

    def __init__(self,model_evulation_config:ModelEvulationConfig,
                 data_transform_artifact:DataTransformArtifact,
                 model_trainer_artifact:ModelTrainerArtifact,
                 data_validation_artifact:DataValidationArtifact) -> None:
        try:
            logging.info(f"{'>>'*20}Model evulation log started.{'<<'*20} \n\n")
            self.model_evulation_config = model_evulation_config
            self.data_transform_artifact = data_transform_artifact
            self.model_trainer_artifact = model_trainer_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e

    def get_best_model(self):
        try:
            logging.info(f"get best model function started")
            model_evu_path = self.model_evulation_config.evulation_file_path
            logging.info(f"model evulation file path : {model_evu_path}")

            model = None

            if not os.path.exists(model_evu_path):
                write_yaml_file(file_path=model_evu_path)
                return model
            
            model_evu_file_content = read_yaml(model_evu_path)

            model_evu_file_content = dict() if model_evu_file_content is None else model_evu_file_content

            if BEST_MODEL_KEY not in model_evu_file_content:
                return model
            
            model = load_object(file_path=model_evu_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])

            return model
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_updated_evulation_report(self,model_evulation_artifact:ModelEvulationArtifact):
        try:
            logging.info(f"get updated evulation report function started")
            model_evu_path = self.model_evulation_config.evulation_file_path

            model_evu_file_content = read_yaml(model_evu_path)

            model_evu_file_content = dict() if model_evu_file_content is None else model_evu_file_content

            previous_best_model = None

            if BEST_MODEL_KEY in model_evu_file_content:
                previous_best_model = model_evu_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY]

            logging.info(f"previous evulation report : {model_evu_file_content}")

            eval_result = {BEST_MODEL_KEY:{MODEL_PATH_KEY:model_evulation_artifact.evulation_model_file_path}}

            if previous_best_model is not None:
                model_history = {self.model_evulation_config.time_stamp : previous_best_model}

                if HISTORY_KEY not in model_evu_file_content:
                    history = {HISTORY_KEY:model_history}
                    eval_result.update(history)
                
                else:
                    model_evu_file_content[BEST_MODEL_KEY].update(model_history)

            model_evu_file_content.update(eval_result)

            logging.info(f"updated evulation report : {model_evu_file_content}")

            write_yaml_file(file_path=model_evu_path,data=model_evu_file_content)

            logging.info(f"writting successfull")
            
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intiate_model_evulation(self):
        try:
            logging.info(f"intiate model evulation function started")

            transform_train_dir = self.data_transform_artifact.transform_train_dir
            transform_test_dir = self.data_transform_artifact.transform_test_dir

            logging.info(f"tranform train dir path : {transform_train_dir}")
            logging.info(f"transform test dir path : {transform_test_dir}")

            train_file = os.listdir(transform_train_dir)[0]
            test_file = os.listdir(transform_test_dir)[0]

            logging.info(f"train file is : {train_file}")
            logging.info(f"test file is : {test_file}")

            train_file_path = os.path.join(transform_train_dir,train_file)
            test_file_path = os.path.join(transform_test_dir,test_file)

            model_evulation_artifact = None
            model_obj = load_object(file_path=self.model_trainer_artifact.trained_model_path)

            logging.info(f"-----reading train data started------")
            train_df = pd.read_csv(train_file_path)
            logging.info(f"-----reading train data completed-----")
            logging.info(f"-----reading test data started-----")
            test_df = pd.read_csv(test_file_path)
            logging.info(f"-----reading test data completed-----")

            logging.info("splitting data into input and output feature")
            X_train,y_train,X_test,y_test = train_df.iloc[:,:-1],train_df.iloc[:,-1],test_df.iloc[:,:-1],test_df.iloc[:,-1]

            model = self.get_best_model()

            if model is None:
                logging.info(f"no model found hence accepting this model")

                model_evulation_artifact = ModelEvulationArtifact(is_model_accepted=True,evulation_model_file_path=self.model_trainer_artifact.trained_model_path)
                self.get_updated_evulation_report(model_evulation_artifact=model_evulation_artifact)
                return model_evulation_artifact
            
            model_list = [model,model_obj]

            base_accuracy = self.model_trainer_artifact.model_accuracy
            logging.info(f"base accuracy is : {base_accuracy}")

            metric_info_artifact = get_evulated_classification_model(X_train = np.array(X_train),
                                                                     y_train = np.array(y_train),
                                                                     X_test = np.array(X_test),
                                                                     y_test = np.array(y_test),
                                                                     base_accuracy=base_accuracy,
                                                                     model_list=model_list)
            if metric_info_artifact is None:
                model_evulation_artifact = ModelEvulationArtifact(is_model_accepted=False,evulation_model_file_path=self.model_trainer_artifact.trained_model_path)
                return model_evulation_artifact
            
            if metric_info_artifact.index_number==1:
                model_evulation_artifact = ModelEvulationArtifact(is_model_accepted=True,evulation_model_file_path=self.model_trainer_artifact.trained_model_path)
                
                self.get_updated_evulation_report(model_evulation_artifact=model_evulation_artifact)

                return model_evulation_artifact
            else:
                logging.info(f"trained model is not better than existing model hence not accepting it")

            model_evulation_artifact = ModelEvulationArtifact(is_model_accepted=False,evulation_model_file_path=self.model_trainer_artifact.trained_model_path)   

            return model_evulation_artifact

        except Exception as e:
            raise MashroomException(sys,e) from e

    def __del__(self):
        logging.info(f"{'>>'*20}Model evulation log completed.{'<<'*20} \n\n")