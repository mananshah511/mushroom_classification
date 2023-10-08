from flask import render_template,Flask,request
import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
from flask_cors import CORS,cross_origin
from mashroom.pipeline.pipeline import Pipeline
import json
from mashroom.entity.artifact_entity import FinalArtifact
import pandas as pd
import numpy as np
from mashroom.util.util import load_object


app = Flask(__name__)

@app.route('/',methods=['GET'])
def homepage():
    return render_template('index.html')


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():
    try:
        data = [str(x) for x in request.form.values()]
        
        if not os.path.exists('data.json'):
            return render_template('index.html',output_text = "No model is trained, please start training")
        with open('data.json', 'r') as json_file:
            dict_data = json.loads(json_file.read())
        
        final_artifact = FinalArtifact(**dict_data)
        logging.info(f"final artifact : {final_artifact}")

        train_df = pd.read_csv(final_artifact.ingested_train_file_dir)
        train_df = train_df.iloc[:,:-1]
        logging.info(f"{train_df.head(5)}")
        df = pd.DataFrame(np.array(data)).T
        df.columns = train_df.columns
        df = pd.concat([df,train_df])
        

        preprocessed_obj = load_object(file_path=final_artifact.preproceesed_model_dir)
        df = preprocessed_obj.transform(df)

        model_dir = final_artifact.trained_model_dir
        model_file = os.listdir(model_dir)[0]
        model_file_path = os.path.join(model_dir,model_file)
        model_obj = load_object(file_path=model_file_path)

        
        df = (np.array(df.iloc[0])).reshape(1,-1)
        output = model_obj.predict(df)
      
        if output[0] == True:
            return render_template('index.html',output_text = "Mashroom is poisonous")
        else:
            return render_template('index.html',output_text = "Mashroom is edible")
    except Exception as e:
        raise MashroomException(sys,e) from e

@app.route('/train',methods=['POST'])
@cross_origin()
def train():
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
        return render_template('index.html',prediction_text = "Model training completed")
    except Exception as e:
        raise MashroomException(sys,e) from e


if __name__ == "__main__":
    app.run()