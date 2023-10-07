import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
from mashroom.entity.config_entity import DataValidationConfig
from mashroom.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
import pandas as pd
from mashroom.constant import COLUMN_KEY,CATEGORICAL_COLUMN_KEY,TARGET_COLUMN_KEY
from mashroom.util.util import read_yaml
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab

class DataValidation:

    def __init__(self,data_validation_config : DataValidationConfig,
                 data_ingestion_artifact : DataIngestionArtifact) -> None:
        try:
            logging.info(f"{'>>'*20}Data Validation log started.{'<<'*20} \n\n")
            self.data_validation_config  = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_train_test_dataframes(self):
        try:
            logging.info(f"get train test dataframe function started")

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            logging.info(f"reading train data from : {train_file_path}")
            train_df = pd.read_csv(train_file_path)
            logging.info(f"train file read successfull")

            logging.info(f"reading test data from : {test_file_path}")
            test_df = pd.read_csv(test_file_path)
            logging.info(f"test file read successfull")

            return train_df,test_df
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_train_test_dir_exits(self)->bool:
        try:
            logging.info("get train test dir exits function started")

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_flag = False
            test_flag = False

            if os.path.exists(train_file_path):
                logging.info(f"-----train dir is okk-----")
                train_flag = True

            if os.path.exists(test_file_path):
                logging.info(f"----test dir is okk-----")
                test_flag = True

            if train_flag == False:
                logging.info(f"train file path is not okk, please check")

            if test_flag == False:
                logging.info(f"test file path is not okk, please check")

                return train_flag and test_flag
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_column_count_validation(self)->bool:
        try:
            logging.info(f"get column count validation function started")
            schema_file_path = self.data_validation_config.schema_file_dir
            schema_file_content = read_yaml(schema_file_path)

            train_df,test_df = self.get_train_test_dataframes()
            
            schema_column_count = len(list(schema_file_content[COLUMN_KEY]))
            train_column_count = len(train_df.columns)
            test_column_count = len(test_df.columns)

            logging.info(f"column count in schema file is : {schema_column_count}")
            logging.info(f"column count in train file is : {train_column_count}")
            logging.info(f"column count in test file is : {test_column_count}")

            train_flag = False
            test_flag = False

            if schema_column_count == train_column_count:
                logging.info(f"column count in train dataframe is okky")
                train_flag = True
            if schema_column_count == test_column_count:
                logging.info(f"column count in test dataframe is okky")
                test_flag = True

            if train_flag == False:
                logging.info(f"column count in train dataframe is not correct")

            if test_flag == False:
                logging.info(f"column count in test dataframe is not correct")

            return train_flag and test_flag

        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_column_name_validation(self)->bool:
        try:
            logging.info(f"get column name validation function started")
            schema_file_path = self.data_validation_config.schema_file_dir
            schema_file_content = read_yaml(schema_file_path)

            train_df,test_df = self.get_train_test_dataframes()

            schema_columns = list(schema_file_content[CATEGORICAL_COLUMN_KEY])
            train_df_columns = list(train_df.columns)
            test_df_columns = list(test_df.columns)

            logging.info(f"schema column names are : {schema_columns}")
            logging.info(f"train dataframe column names are : {train_df_columns}")
            logging.info(f"test dataframe column anmes are : {test_df_columns}")

            train_flag = False
            test_flag = False

            if schema_columns == train_df_columns:
                logging.info(f"train dataframe column names are correct")
                train_flag = True

            if schema_columns == test_df_columns:
                logging.info(f"test dataframe column names are correct")
                test_flag = True

            if train_flag == False:
                logging.info(f"train dataframe column names are not correct")

            if test_flag == False:
                logging.info(f"test dataframe column names are not correct")

            return test_flag and train_flag
            
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_column_data_type_validation(self)->bool:
        try:
            logging.info(f"get column data type validation function started")
            schema_file_path = self.data_validation_config.schema_file_dir
            schema_file_content = read_yaml(schema_file_path)

            train_df,test_df = self.get_train_test_dataframes()
            
            schema_column_data = dict(schema_file_content[COLUMN_KEY])
            train_column_data = dict(train_df.dtypes)
            test_column_data = dict(test_df.dtypes)

            train_flag = False
            test_flag = False

            for column_name in schema_column_data.keys():
                if train_column_data[column_name]!=schema_column_data[column_name]:
                    logging.info(f"datatype of {column_name} in train data is not correct")
                    return train_flag
                if test_column_data[column_name]!=schema_column_data[column_name]:
                    logging.info(f"datatype of {column_name} in test data is not correct")
                    return test_flag

            train_flag = True
            test_flag = True

            return train_flag and test_flag
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_and_save_data_drift_report(self):
        try:
            logging.info("get and save data drift report function started")
            report_file_dir = self.data_validation_config.report_page_file_dir
            os.makedirs(report_file_dir,exist_ok=True)

            report_file_path = os.path.join(report_file_dir,self.data_validation_config.report_name)

            train_df,test_df = self.get_train_test_dataframes()

            dashboard = Dashboard(tabs=[DataDriftTab()])
            dashboard.calculate(train_df,test_df)
            dashboard.save(report_file_path)
            logging.info(f"report saved succesfully")
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intiate_data_validation(self)->DataValidationArtifact:
        try:
            validation3 = False
            validation1 = self.get_column_count_validation()
            if validation1:
                validation2 = self.get_column_name_validation()
            if validation2:
                validation3 = self.get_column_data_type_validation()
            
            self.get_and_save_data_drift_report()

            data_validation_artifact = DataValidationArtifact(is_validated=validation3,message="validation succesfull",
                                                              schema_file_path=self.data_validation_config.schema_file_dir,
                                                              reprot_file_path=self.data_validation_config.report_page_file_dir)
            
            return data_validation_artifact
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def __del__(self):
        logging.info(f"{'>>'*20}Data Validation log completed.{'<<'*20} \n\n")