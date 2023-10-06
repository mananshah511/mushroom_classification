import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
import yaml
import pandas as pd
import numpy as np
from collections import namedtuple
from sklearn.metrics import accuracy_score
import importlib



GRID_SEARCH_KEY = 'grid_search'
MODULE_KEY = 'module'
CLASS_KEY = 'class'
PARAM_KEY = 'params'
MODEL_SELECTION_KEY = 'model_selection'
SEARCH_PARAM_GRID_KEY = 'search_param_grid'

InitlizedModelDetails = namedtuple("InitlizedModelDetails", ["model_serial_number","model","params_grid_search","model_name"])

GridSearchedBestModel = namedtuple("GridSearchedBestModel",["model_serial_number","model",
                                                            "best_model",
                                                            "best_parameters",
                                                            "best_scores"])

MetricInfoArtifact = namedtuple("MetricInfoArtifact",["model_name","model_object",
                                                      "train_accuracy","test_accuracy","model_accuracy","index_number"])


def get_evulated_classification_model( model_list:list,X_train:np.ndarray,y_train:np.ndarray,X_test:np.ndarray,
                                      y_test:np.ndarray,base_accuracy:float=0.6 )->MetricInfoArtifact:
    try:
        logging.info(f"get evulated classification model function started")
        metric_info_artifact = None
        index_number = 0
        logging.info(f"model list : {model_list}")

        for model in model_list:

            logging.info(f"-----------------for model : {model}----------------------")

            model_name = str(model)

            y_train_predict = model.predict(X_train)
            y_test_predict = model.predict(X_test)

            train_accuracy = accuracy_score(y_train_predict,y_train)
            test_accuracy = accuracy_score(y_test_predict,y_test)

            logging.info(f"train accuracy : {train_accuracy}")
            logging.info(f"test accuracy : {test_accuracy}")

            model_accuracy = (2*(train_accuracy*test_accuracy))/(train_accuracy+test_accuracy)
            diff_train_test_accuracy = np.abs(train_accuracy-test_accuracy)

            logging.info(f"model accuracy : {model_accuracy}")
            logging.info(f"diff in train and test accuracy is : {diff_train_test_accuracy}")

            if model_accuracy>=base_accuracy and diff_train_test_accuracy<0.05:
                base_accuracy = model_accuracy

                metric_info_artifact = MetricInfoArtifact(model_name=model_name,
                                                          model_object=model,
                                                          train_accuracy=train_accuracy,
                                                          test_accuracy=test_accuracy,
                                                          model_accuracy=model_accuracy,
                                                          index_number=index_number)
                index_number+=1

        if metric_info_artifact is None:
            logging.info(f"no model matched base accuracy")

        return metric_info_artifact
    except Exception as e:
        raise MashroomException(sys,e) from e
    

class Modelfactory:



    def __init__(self, config_path:str=None) -> None:
        try:
            self.config : dict = Modelfactory.read_params(config_path=config_path)
            self.grid_search_cv_module:str = self.config[GRID_SEARCH_KEY][MODULE_KEY]
            self.grid_search_cv_class_module:str = self.config[GRID_SEARCH_KEY][CLASS_KEY]
            self.grid_search_cv_property_data:dict = dict(self.config[GRID_SEARCH_KEY][PARAM_KEY])
            self.model_intial_config:dict = dict(self.config[MODEL_SELECTION_KEY])

            self.intlized_model_list = None
            self.grid_searched_best_model_list = None
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    @staticmethod
    def read_params(config_path:str)->dict:
        try:
            with open(config_path) as yaml_files:
                config:dict = yaml.safe_load(yaml_files)
                return config
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    @staticmethod
    def class_for_name(class_name:str,module_name:str):
        try:
            module = importlib.import_module(module_name)
            class_ref = getattr(module,class_name)
            return class_ref
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    @staticmethod
    def update_property_class(insta_object:object,property_data:dict):
        try:
            for key,value in property_data.items():
                setattr(insta_object,key,value)
                return insta_object
        except Exception as e:
            raise MashroomException(sys,e) from e
        

    def get_intlized_model_list(self)->list[InitlizedModelDetails]:
        try:
            logging.info(f"get intlized model list function started")
            intlized_model_list = []

            for model_serial_number in self.model_intial_config.keys():
                model_config = self.model_intial_config[model_serial_number]

                model_object = Modelfactory.class_for_name(class_name=model_config[CLASS_KEY],
                                                    module_name=model_config[MODULE_KEY])
                
                model = model_object()

                if PARAM_KEY in model_config:
                    model_object_property_data = dict(model_config[PARAM_KEY])
                    model = Modelfactory.update_property_class(insta_object=model,
                                                               property_data=model_object_property_data)
                    
                params_grid_search = model_config[SEARCH_PARAM_GRID_KEY]

                modell_name = f"{model_config[MODULE_KEY]}.{model_config[CLASS_KEY]}"

                model_config = InitlizedModelDetails(model_serial_number=model_serial_number,
                                                     model=model,params_grid_search=params_grid_search,
                                                     model_name=modell_name)
                intlized_model_list.append(model_config)
                self.intlized_model_list = intlized_model_list
                logging.info(f"intlized model list : {intlized_model_list}")
            return self.intlized_model_list
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def initite_best_parameter_search_for_initlized_models(self,intlized_model_list:list[InitlizedModelDetails],
                                                           input_feature,output_feature)->list[GridSearchedBestModel]:
        try:
            logging.info(f"initite best parameter for models function started")
            self.grid_searched_best_model_list = []

            for intlized_model in intlized_model_list:
                logging.info(f"finding best model for : {intlized_model}")
                grid_searched_best_model = self.initite_best_parameter_search_for_initlized_model(
                    intlized_model_details=intlized_model,
                    input_feature=input_feature,
                    output_feature=output_feature
                )
                logging.info(f"best model is : {grid_searched_best_model}")

                self.grid_searched_best_model_list.append(grid_searched_best_model)

            return self.grid_searched_best_model_list
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def initite_best_parameter_search_for_initlized_model(self,intlized_model_details:InitlizedModelDetails,
                                                          input_feature,output_feature)->GridSearchedBestModel:
        try:
            logging.info(f"finding best parameters for each models")

            grid_search_ref = Modelfactory.class_for_name(class_name=self.grid_search_cv_class_module,
                                                          module_name=self.grid_search_cv_module)
            
            grid_search_cv = grid_search_ref(estimator = intlized_model_details.model,
                                             param_grid = intlized_model_details.params_grid_search)
            
            grid_search_cv = Modelfactory.update_property_class(insta_object=grid_search_cv,
                                                                property_data=self.grid_search_cv_property_data)
            
            grid_search_cv.fit(input_feature,output_feature)

            grid_searched_best_model = GridSearchedBestModel(model_serial_number=intlized_model_details.model_serial_number,
                                                             model=intlized_model_details.model,
                                                             best_parameters=grid_search_cv.best_params_,
                                                             best_model=grid_search_cv.best_estimator_,
                                                             best_scores=grid_search_cv.best_score_)
            return grid_searched_best_model
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    @staticmethod
    def get_best_model_from_grid_serached_best_model_list(grid_searched_best_model_list:list[GridSearchedBestModel],
                                                          base_accuracy:float=0.6):
        try:
            logging.info(f"get best model from grid searched best model")

            best_model = None
            for grid_searched_model in grid_searched_best_model_list:
                if base_accuracy < grid_searched_model.best_scores:
                    base_accuracy = grid_searched_model.best_scores
                    best_model = grid_searched_model.best_model

            if not best_model:
                raise Exception("None model has base accuracy")
            
            return best_model
        except Exception as e:
            raise MashroomException(sys,e) from e
        

    def get_best_model(self,X,y,base_accuracy=0.6):
        try:
            logging.info(f"get best model function started")
            intlized_model_list = self.get_intlized_model_list()
            logging.info(f"Final model list is:{intlized_model_list}")

            grid_searched_best_model_list = self.initite_best_parameter_search_for_initlized_models(
                intlized_model_list=intlized_model_list,
                input_feature=X,
                output_feature=y
            )
            logging.info(f"Best individual models with paramater is :{grid_searched_best_model_list}")

            return Modelfactory.get_best_model_from_grid_serached_best_model_list(grid_searched_best_model_list=grid_searched_best_model_list,
                                                                                  base_accuracy=base_accuracy)


        except Exception as e:
            raise MashroomException(sys,e) from e
