from flask import render_template,Flask,request
import os,sys
from mashroom.logger import logging
from mashroom.exception import MashroomException
from flask_cors import CORS,cross_origin


app = Flask(__name__)

@app.route('/',methods=['GET'])
def homepage():
    return render_template('index.html')


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():
    try:
        data = [str(x) for x in request.form.values()]
        logging.info(data)
        return data
    except Exception as e:
        raise MashroomException(sys,e) from e

@app.route('/train',methods=['POST'])
@cross_origin()
def train():
    pass


if __name__ == "__main__":
    app.run()