import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
from mashroom.entity.artifact_entity import DataIngestionArtifact,DataTransformArtifact,DataValidationArtifact
from mashroom.entity.config_entity import DataTransformConfig
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import pandas as pd
from mashroom.util.util import read_yaml
from sklearn.base import BaseEstimator,TransformerMixin
from mashroom.constant import TARGET_COLUMN_KEY
import numpy as np
import dill

class trans(BaseEstimator,TransformerMixin):
  def __init(self):
    pass

  def fit(self,X,y=None):
    return self

  def transform(self,X,y=None):
    X=pd.DataFrame(X)
    X=pd.get_dummies(X,drop_first=True,dtype='int64')
    global column_trans
    column_trans = X.columns
    return X

class DataTransform:

    def __init__(self,data_transform_config:DataTransformConfig,
                data_ingestion_artifact:DataIngestionArtifact,
                data_validation_artifact:DataValidationArtifact) -> None:
        try:
            logging.info(f"{'>>'*20}Data Transformation log started.{'<<'*20} ")
            self.data_transform_config = data_transform_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
    
    def get_preprocessing_object(self)->Pipeline:
        try:
            logging.info(f"get preprocessing object function staretd")

            logging.info(f"-----pipeline esamble started-----")
            pipeline = Pipeline(steps=[('impute',SimpleImputer(strategy='most_frequent')),
                                       ('dumies',trans())
                                       ])
            logging.info(f"-----pipeline esamble completed-----")
            return pipeline
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_perfrom_preprocessing(self,preprocessed_obj:Pipeline,is_test_data:bool=False):
        try:
            logging.info(f"get perfrom preprocessing function started")
            schme_file_path = self.data_validation_artifact.schema_file_path
            schema_file_content = read_yaml(file_path=schme_file_path)
            target_coulmn_name = schema_file_content[TARGET_COLUMN_KEY]
            
            if is_test_data == False:

                train_file_path = self.data_ingestion_artifact.train_file_path

                logging.info(f"-----reading train data started-----")
                train_df = pd.read_csv(train_file_path)
                logging.info(f"------reading train data completed-----")

                target_df = train_df.iloc[:,-1]
                logging.info(f"dropping target column from dataframe")
                train_df.drop(target_coulmn_name,inplace=True,axis=1)

                columns = train_df.columns
                logging.info(f"columns names after dropping target column : {columns}")

                logging.info(f"-----preprocessing on train data started-----")
                train_df = preprocessed_obj.fit_transform(train_df)
                logging.info(f"-----preprocessing on train data completed-----")

                              
                logging.info(f"one hot encoding on target data")
                target_df = pd.get_dummies(target_df.values,drop_first=True,dtype='int64')

                train_df = pd.concat([train_df,target_df],axis=1)
                logging.info(f"combining input and output dataframes")

                return train_df,preprocessed_obj
            else:

                test_file_path = self.data_ingestion_artifact.test_file_path

                logging.info(f"-----reading test data started-----")
                test_df = pd.read_csv(test_file_path)
                logging.info(f"------reading train data completed-----")

                target_df = test_df.iloc[:,-1]
                logging.info(f"dropping target column from dataframe")
                test_df.drop(target_coulmn_name,inplace=True,axis=1)

                columns = test_df.columns
                logging.info(f"columns names after dropping target column : {columns}")

                logging.info(f"-----preprocessing on test data started-----")
                test_df = preprocessed_obj.transform(test_df)
                logging.info(f"-----preprocessing on test data completed-----")

                
                logging.info(f"one hot encoding on target data")
                target_df = pd.get_dummies(target_df.values,drop_first=True,dtype='int64')

                test_df = pd.concat([test_df,target_df],axis=1)
                logging.info(f"combining input and output dataframes")

                return test_df
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def save_transformed_train_test_data(self,train_df:pd.DataFrame,test_df:pd.DataFrame):
        try:
            logging.info(f"save transformed train test data function started")

            tansform_train_dir = self.data_transform_config.transform_train_dir
            logging.info(f"saving transformed train file in : {tansform_train_dir}")
            os.makedirs(tansform_train_dir,exist_ok=True)
            transform_train_file_path = os.path.join(tansform_train_dir,"train.csv")
            if train_df is not None:
                train_df.to_csv(transform_train_file_path,index=False)
            logging.info(f"saving transformed train file succesfull")

            tansform_test_dir = self.data_transform_config.transform_test_dir
            logging.info(f"saving transformed test file in : {tansform_test_dir}")
            os.makedirs(tansform_test_dir,exist_ok=True)
            transform_test_file_path = os.path.join(tansform_test_dir,"test.csv")
            if test_df is not None:
                test_df.to_csv(transform_test_file_path,index=False)
            logging.info(f"saving transformed test file succesfull")
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intiate_data_transform(self)->DataTransformArtifact:
        try:
            logging.info(f"intiate data transform function started")
            preprocessed_object = self.get_preprocessing_object()

            train_df,preprocessed_object = self.get_perfrom_preprocessing(preprocessed_obj=preprocessed_object)
            test_df = self.get_perfrom_preprocessing(preprocessed_obj=preprocessed_object,is_test_data=True)

            preprocessed_file_path = self.data_transform_config.preprocessed_file_path
            preprocessed_file_dir = os.path.dirname(preprocessed_file_path)
            os.makedirs(preprocessed_file_dir,exist_ok=True)

            with open(preprocessed_file_path,'wb') as objfile:
                dill.dump(preprocessed_object,objfile)
            
            self.save_transformed_train_test_data(train_df=train_df,test_df=test_df)

            data_transform_artifact = DataTransformArtifact(is_transform=True,message="Data Transform suceessfull",
                                                            transform_train_dir=self.data_transform_config.transform_train_dir,
                                                            transform_test_dir=self.data_transform_config.transform_test_dir,
                                                            preprocessed_dir=self.data_transform_config.preprocessed_file_path)
            
            return data_transform_artifact


        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def __del__(self):
        logging.info(f"{'>>'*20}Data Transformation log completed.{'<<'*20} \n\n")