import os , json , joblib
import numpy as np
from src.pathes import *
from typing import List, Any , Optional
model , scaler , dataset , features , target = "model" , "scaler" , "dataset" , "features" , "terget"


class ModelPredictor:
    def __init__(self, model_path: str, scaler_path: Optional[str] = None):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path) if scaler_path else None

    def predict(self, features: Any) -> np.ndarray:
        """
        پیش‌بینی برای یک نمونه.
        features: لیست/آرایه ویژگی‌ها با طول n_features.
        """
        x = np.asarray(features, dtype=float).reshape(1, -1)

        # اعتبارسنجی تعداد ویژگی‌ها (اگه مدل پشتیبانی کنه)
        n_expected = getattr(self.model, "n_features_in_", None)
        if n_expected is not None and x.shape[1] != n_expected:
            raise ValueError(
                f"انتظار {n_expected} ویژگی بود، دریافت شد {x.shape[1]}"
            )

        if self.scaler is not None:
            x = self.scaler.transform(x)

        return self.model.predict(x)

class Disease_diagnosis:
    def __init__(self):
        self._models = {}
        self.current_models = self.models

    @property
    def models(self):
        for model in os.listdir(models_json_path):
            item = Path(models_json_path).joinpath(model).as_posix()
            if os.path.exists(item):
                self._models.update({Path(model).stem : item})
            else :
                print(f"'{model}' is not exists!!")
        return self._models
    
    def use_models(self ,features ,  model_path = "" , scaler_path = ""):
        prediction = ModelPredictor(
            model_path = model_path ,
            scaler_path = scaler_path)
        return prediction.predict(features = features)
    
    def sort_patient_data(self , disease_name , **data):
        if not disease_name in list(self.current_models.keys()):
            print(f"The '{disease_name}' model doesn't exist")
            return None
        sorted_data = {}
        unavailable_data = []
        load_model_json = {}
        with open(self.current_models[disease_name] , "r" , encoding="utf-8") as file:
            load_model_json = json.load(file)
        for feature in load_model_json[features]:
            if feature in list(data.keys()):
                sorted_data.update({feature : data[feature]})
            else :
                unavailable_data.append(feature)
        return {
            "data" : sorted_data ,
            "lost_data" : unavailable_data
        }

    def Screening(self , disease_name , **patients_data):
        if not disease_name in list(self.current_models.keys()):
            print(f"The '{disease_name}' model doesn't exist")
            return None
        sorted_data = self.sort_patient_data(disease_name = disease_name , **patients_data)
        if len(sorted_data["lost_data"]) > 0:
            raise ValueError(f"Some features haven't been entered correctly :" , *sorted_data["lost_data"])

        model_details = self.__open_models_json(disease_name)
        if model_details is None:
            raise NameError(f"The '{disease_name}' model doesn't exist")
        path_model = model_details[model]
        path_scaler = model_details[scaler]
        
        screening = self.use_models(
            features = list(sorted_data["data"].values()) ,
            model_path = path_model ,
            scaler_path = path_scaler
        )
        return self.__show_result(
            results = model_details["terget"] ,
            result = screening
        )

    def __show_result(self , results , result):
        for target in results:
            if result[0] != target["value"] : continue
            print(target["msg"])
            return target["output"]
        raise RuntimeError(f"The model has made an unexpected prediction : '{result}'")
    def __open_models_json(self , model_name):
        if model_name in list(self.current_models.keys()):
            with open(self.current_models[model_name] , "r" , encoding = "utf-8") as file:
                return json.load(file)
        else :
            return None
import random

def shuffle_list(input_list):
    # ایجاد یک کپی برای جلوگیری از تغییر لیست اصلی
    temp_list = list(input_list)
    random.shuffle(temp_list)
    return temp_list

if __name__ == "__main__":
    t = Disease_diagnosis()
    # print(t.models)
    # data = shuffle_list(["age", "sex", "cp", 
    #             "trestbps", "chol", "fbs", 
    #             "restecg", "thalach", "exang", 
    #             "oldpeak", "slope", "ca"])
    # print(f"Data : \n{data}")
    # creat_data = {}
    # for f in data:
    #     creat_data.update({f : 1})

    # sorted_data = t.sort_patient_data("Heart disease" , **creat_data)
    # print(f"sorted data : \n{sorted_data}")
    s1 = {
        "age" : 63,
        "sex" : 1,
        "cp" : 1,
        "trestbps" : 145,
        "chol" : 233,
        "fbs" : 1,
        "restecg" : 2,
        "thalach" : 150,
        "exang" : 0,
        "oldpeak" : 2.3,
        "slope" : 3,
        "ca" : 0.0,
        "thal" : 6.0
        }
    
    t.Screening(disease_name = 'Heart disease' ,
                **s1)
    