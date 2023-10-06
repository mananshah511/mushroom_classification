import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
import pandas as pd
import numpy as np
import dill
from mashroom.entity.artifact_entity import ModelTrainerArtifact,DataTransformArtifact
from mashroom.entity.config_entity import ModelTrainerConfig
from mashroom.entity.model_factory import Modelfactory
from mashroom.entity.model_factory import GridSearchedBestModel,MetricInfoArtifact,get_evulated_classification_model

class ModelTrainer:

    def __init__(self,model_trainer_config:ModelTrainerConfig,
                 data_transform_artifact:DataTransformArtifact) -> None:
        try:
            logging.info(f"{'>>'*20}Model Trainer log started.{'<<'*20} ")
            self.model_trainer_config = model_trainer_config
            self.data_transform_artifact = data_transform_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intitate_model_trainer(self):
        try:
            logging.info(f"intiate model trainer function started")

            transform_train_file_dir = self.data_transform_artifact.transform_train_dir
            transform_test_file_dir = self.data_transform_artifact.transform_test_dir

            transform_train_file = os.listdir(transform_train_file_dir)[0]
            transform_test_file = os.listdir(transform_test_file_dir)[0]

            train_df = pd.read_csv(os.path.join(transform_train_file_dir,transform_train_file))
            test_df = pd.read_csv(os.path.join(transform_test_file_dir,transform_test_file))

            model_trainer_artifact = None
            X_train,y_train,X_test,y_test = train_df.iloc[:,:-1],train_df.iloc[:,-1],test_df.iloc[:,:-1],test_df.iloc[:,-1]

            model_config_file_path = self.model_trainer_config.model_config_file_path

            model_factory = Modelfactory(config_path=model_config_file_path)

            base_accuracy = self.model_trainer_config.base_accuracy

            best_model = model_factory.get_best_model(X=np.array(X_train),y=np.array(y_train),base_accuracy=base_accuracy)

            logging.info(f"best model on trained data is : {best_model}")

            grid_searched_best_model_list:list[GridSearchedBestModel] = model_factory.grid_searched_best_model_list

            model_list = [model.best_model for model in grid_searched_best_model_list]

            metric_info:MetricInfoArtifact = get_evulated_classification_model(X_train=np.array(X_train),
                                                                               X_test=np.array(X_test),
                                                                               y_train=np.array(y_train),
                                                                               y_test=np.array(y_test),
                                                                               base_accuracy=base_accuracy,
                                                                               model_list=model_list)
            
            model_trainer_artifact = ModelTrainerArtifact(is_trained=True,
                                                          message='yes',
                                                          trained_model_path=self.model_trainer_config.trained_model_file_path,
                                                          train_accuracy=metric_info.train_accuracy,
                                                          test_accuracy=metric_info.test_accuracy,
                                                          model_accuracy=metric_info.model_accuracy)
            return model_trainer_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def __del__(self):
        logging.info(f"{'>>'*20}Model trainer log completed.{'<<'*20} \n\n")