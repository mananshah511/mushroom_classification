import os,sys
from mashroom.exception import MashroomException
from mashroom.logger import logging
from mashroom.entity.artifact_entity import DataIngestionArtifact
from mashroom.entity.config_entity import DataIngestionConfig
from six.moves import urllib
from zipfile import ZipFile
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from mashroom.constant import COLUMNS

class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig) -> None:
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20} ")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def download_mashroom_data(self):
        try:
            logging.info(f"download mashroom data function started")
            dataset_url = self.data_ingestion_config.dataset_download_url
            zip_data_dir = self.data_ingestion_config.zip_data_dir
            logging.info(f"downlaodind data from {dataset_url} in the {zip_data_dir} folder")

            os.makedirs(zip_data_dir,exist_ok=True)
            
            filename = os.path.basename(dataset_url)
            zip_data_path = os.path.join(zip_data_dir,filename)

            logging.info(f"-----data download started-----")
            urllib.request.urlretrieve(dataset_url,zip_data_path)
            logging.info(f"-----data download completed-----")

            return zip_data_path


        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_extract_data(self,zip_file_path:str):
        try:
            logging.info(f"get extracted data function started")
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            os.makedirs(raw_data_dir,exist_ok=True)
            logging.info(f"extracting data from {zip_file_path} into {raw_data_dir} folder")

            with ZipFile(zip_file_path,'r') as zip:
                zip.extractall(raw_data_dir)
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def get_train_test_split_data(self):
        try:
            logging.info(f"get train test split function started")
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            data_file_name = os.listdir(raw_data_dir)[0]
            logging.info(f"data file name : {data_file_name}")

            file_path = os.path.join(raw_data_dir,data_file_name)

            logging.info(f"-----data reading started-----")
            mashroom_df = pd.read_csv(file_path,sep=',',names=COLUMNS)
            #logging.info(f"{mashroom_df}")
            logging.info(f"-----data reading completed-----")

            logging.info(f"-----splitting data started-----")
            X_train,X_test,y_train,y_test = train_test_split(mashroom_df.iloc[:,1:],mashroom_df.iloc[:,0],test_size=0.2, random_state=42)
            logging.info(f"-----splitting data completed-----")

            data_file_name = data_file_name.replace('data','csv')

            train_df = None
            test_df = None

            

            logging.info(f"combining input and output features")
            train_df = pd.concat([X_train,y_train],axis=1)
            test_df = pd.concat([X_test,y_test],axis=1)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,data_file_name)
            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,data_file_name)

            if train_df is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"saving train data as csv")
                train_df.to_csv(train_file_path,index=False)

            if test_df is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir,exist_ok=True)
                logging.info(f"saving test data as csv")
                train_df.to_csv(test_file_path,index=False)

            data_ingestion_config = DataIngestionArtifact(is_ingested=True,message="Data Ingested",
                                                          train_file_path=train_file_path,test_file_path=test_file_path)
            
            return data_ingestion_config

        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def intiate_data_ingestion(self)->DataIngestionArtifact:
        try:
            logging.info(f"intitate data ingestion function started")
            zip_file_path = self.download_mashroom_data()
            self.get_extract_data(zip_file_path=zip_file_path)
            return self.get_train_test_split_data()
        except Exception as e:
            raise MashroomException(sys,e) from e
        
    def __del__(self):
        logging.info(f"{'>>'*20}Data Ingestion log completed.{'<<'*20} \n\n")