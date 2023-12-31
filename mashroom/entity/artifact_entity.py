from collections import namedtuple

DataIngestionArtifact = namedtuple("DataIngestionArtifact",["is_ingested","message","train_file_path","test_file_path"])

DataValidationArtifact = namedtuple("DataValidationArtifact",
                                    ["is_validated","message","schema_file_path","reprot_file_path"])
                                    

DataTransformArtifact = namedtuple("DataTransformArtifact",
                                   ["is_transform","message","transform_train_dir","transform_test_dir",
                                    "preprocessed_dir"])

ModelTrainerArtifact = namedtuple("ModelArtifactConfig",
                                ["is_trained","message","trained_model_path","train_accuracy","test_accuracy",
                                 "model_accuracy"])

ModelEvulationArtifact = namedtuple("ModelEvulationConfig",
                                  ["is_model_accepted","evulation_model_file_path"])

ModelPusherArtifact = namedtuple("ModelPusherArtifact",["export_dir_path"])

FinalArtifact = namedtuple("FinalArtifact",["ingested_train_file_dir","preproceesed_model_dir","trained_model_dir"])
