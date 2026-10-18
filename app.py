
from src.pathes import *
model , scaler , dataset , features = "model" , "scaler" , "dataset" , "features"

class Disease_diagnosis:
    def __init__(self):
        self.dic_features = {
            "breast_cancer" : models.breast_cancer[features] , 
            "diabet_type2" : models.diabet_type2[features] , 
            "heart_disease" : models.heart_disease[features]
        }

    def check_disease(self , features_list : list):
        disease = None
        for disease_name , features in list(self.dic_features.items()):
            for feature in features_list :
                if not feature in features:
                    disease = None
                    break
                disease = disease_name
            if disease is None:
                continue
            else :
                break
        return disease

import random

def shuffle_list(input_list):
    # ایجاد یک کپی برای جلوگیری از تغییر لیست اصلی
    temp_list = list(input_list)
    random.shuffle(temp_list)
    return temp_list

if __name__ == "__main__":
    test_class = Disease_diagnosis()
    t_list = models.heart_disease[features]
    t_list.append("ttt")
    test_list = shuffle_list(t_list)
    print(test_list)
    print(test_class.check_disease(test_list))