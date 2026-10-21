import random , os , json , joblib
import numpy as np
from src.pathes import *
from typing import List, Any , Optional
model , scaler , dataset , features , target = "model" , "scaler" , "dataset" , "features" , "terget"


# class ModelPredictor:
#     def __init__(self, model_path: str, scaler_path: Optional[str] = None):
#         self.model = joblib.load(model_path)
#         self.scaler = joblib.load(scaler_path) if scaler_path else None

#     def predict(self, features: Any) -> np.ndarray:
#         """
#         پیش‌بینی برای یک نمونه.
#         features: لیست/آرایه ویژگی‌ها با طول n_features.
#         """
#         x = np.asarray(features, dtype=float).reshape(1, -1)

#         # اعتبارسنجی تعداد ویژگی‌ها (اگه مدل پشتیبانی کنه)
#         n_expected = getattr(self.model, "n_features_in_", None)
#         if n_expected is not None and x.shape[1] != n_expected:
#             raise ValueError(
#                 f"انتظار {n_expected} ویژگی بود، دریافت شد {x.shape[1]}"
#             )

#         if self.scaler is not None:
#             x = self.scaler.transform(x)

#         return self.model.predict(x)

import pandas as pd

class ModelPredictor:
    def __init__(self, model_path: str, scaler_path: Optional[str] = None):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path) if scaler_path else None

        # گرفتن نام ویژگی‌ها از scaler یا model
        self.feature_names = None
        if self.scaler is not None and hasattr(self.scaler, "feature_names_in_"):
            self.feature_names = list(self.scaler.feature_names_in_)
        elif hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)

    def predict(self, features: Any) -> np.ndarray:
        x = np.asarray(features, dtype=float).reshape(1, -1)

        n_expected = getattr(self.model, "n_features_in_", None)
        if n_expected is not None and x.shape[1] != n_expected:
            raise ValueError(
                f"انتظار {n_expected} ویژگی بود، دریافت شد {x.shape[1]}"
            )

        # اگر نام ویژگی‌ها را داریم، DataFrame بساز تا هشدار حذف شود
        if self.feature_names is not None:
            x = pd.DataFrame(x, columns=self.feature_names)

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
    
    def multiple_screening(self , *multi_data):
        results = {}
        for data in multi_data:
            try :
                screening_result = self.Screening(data["disease_name"] , **data["patients_data"])
                results.update({
                    self.__Create_unique_name(data["__name__"] , results) : {
                        "disease_name" : data["disease_name"] ,
                        "result" : screening_result[0] ,
                        "msg" : screening_result[1]["msg"] ,
                        "result_value" : screening_result[1]["value"]
                        }
                    })
            except ValueError as v :
                results.update({
                    data["__name__"] : {
                        "disease_name" : data["disease_name"] ,
                        "result" : "Feature Error" ,
                        "msg" : f"There was a problem retrieving some features. {v}" ,
                        "result_value" : None
                        }
                    })
            except NameError as n :
                name = data["disease_name"]
                results.update({
                    data["__name__"] : {
                        "disease_name" : name ,
                        "result" : "Disease_name Error" ,
                        "msg" : f"{name} is not supported.\n{n}" ,
                        "result_value" : None
                    }
                })
            except RuntimeError as r:
                results.update({
                        data["__name__"] : {
                        "disease_name" : data["disease_name"] ,
                        "result" : None ,
                        "msg" : str(r) ,
                        "result_value" : None
                    }
                })
            except Exception as e:
                results.update({
                    data["__name__"] : {
                        "disease_name" : data["disease_name"] ,
                        "result" : "Unknown error" ,
                        "msg" : str(e) ,
                        "result_value" : None
                    }
                })
        return results

    def __Create_unique_name(self , name , dic):
        counter = 1
        uniq_name = name
        while(uniq_name in list(dic.keys())):
            counter += 1
            uniq_name = f"{name}({counter})"
        return uniq_name


    def show_result(self , msg):
        print(msg)
    
    def __show_result(self , results , result):
        for target in results:
            if result[0] != target["value"] : continue
            self.show_result(target["msg"])
            return [target["output"] , target]
        raise RuntimeError(f"The model has made an unexpected prediction : '{result}'")
    
    def __open_models_json(self , model_name):
        if model_name in list(self.current_models.keys()):
            with open(self.current_models[model_name] , "r" , encoding = "utf-8") as file:
                return json.load(file)
        else :
            return None

def shuffle_list(input_list):
    # ایجاد یک کپی برای جلوگیری از تغییر لیست اصلی
    temp_list = list(input_list)
    random.shuffle(temp_list)
    return temp_list

def test_model_heart_disease():
    t = Disease_diagnosis()

    patient_1 = {
        "age": 63,
        "sex": 1,
        "cp": 4,
        "trestbps": 130,
        "chol": 254,
        "fbs": 0,
        "restecg": 2,
        "thalach": 147,
        "exang": 0,
        "oldpeak": 1.4,
        "slope": 2,
        "ca": 1.0,
        "thal": 7.0
    } # نتیجه انتظاری: بیمار (target = 1)
    healthy_1 = {
        "age": 57,
        "sex": 1,
        "cp": 4,
        "trestbps": 140,
        "chol": 192,
        "fbs": 0,
        "restecg": 0,
        "thalach": 148,
        "exang": 0,
        "oldpeak": 0.4,
        "slope": 2,
        "ca": 0.0,
        "thal": 6.0
    } # نتیجه انتظاری: سالم (target = 0)

    high_risk_patient = {
        "age": 67,
        "sex": 1,
        "cp": 4,
        "trestbps": 160,
        "chol": 286,
        "fbs": 0,
        "restecg": 2,
        "thalach": 108,
        "exang": 1,
        "oldpeak": 1.5,
        "slope": 2,
        "ca": 3.0,
        "thal": 3.0
    }# نکات: سن بالا، فشار خون بالا، کلسترول بالا، حداکثر ضربان پایین، آنژین ورزشی
    # نتیجه انتظاری: بیمار (target = 1)
    young_healthy = {
        "age": 37,
        "sex": 1,
        "cp": 3,
        "trestbps": 130,
        "chol": 250,
        "fbs": 0,
        "restecg": 0,
        "thalach": 187,
        "exang": 0,
        "oldpeak": 3.5,
        "slope": 3,
        "ca": 0.0,
        "thal": 3.0
    }# نکات: سن پایین، ضربان حداکثر بالا (187)، بدون آنژین
    # نتیجه انتظاری: سالم (target = 0)

    high_chol_patient = {
        "age": 67,
        "sex": 0,
        "cp": 3,
        "trestbps": 115,
        "chol": 564,
        "fbs": 0,
        "restecg": 2,
        "thalach": 160,
        "exang": 0,
        "oldpeak": 1.6,
        "slope": 2,
        "ca": 0.0,
        "thal": 7.0
    }# کلسترول 564 (بسیار بالا)، thal=7.0
    # نتیجه انتظاری: سالم طبق دیتاست (target = 0) — نمونه جالب برای تست!
    
    female_patient = {
        "age": 62,
        "sex": 0,
        "cp": 4,
        "trestbps": 150,
        "chol": 244,
        "fbs": 0,
        "restecg": 0,
        "thalach": 154,
        "exang": 1,
        "oldpeak": 1.4,
        "slope": 2,
        "ca": 0.0,
        "thal": 3.0
    }# زن، آنژین ورزشی، thal=3.0
    # نتیجه انتظاری: بیمار (target = 1)

    midage_patient = {
        "age": 58,
        "sex": 1,
        "cp": 4,
        "trestbps": 128,
        "chol": 259,
        "fbs": 0,
        "restecg": 2,
        "thalach": 130,
        "exang": 1,
        "oldpeak": 3.0,
        "slope": 2,
        "ca": 2.0,
        "thal": 7.0
    }# آنژین ورزشی، oldpeak بالا (3.0)، ca=2.0
    # نتیجه انتظاری: بیمار (target = 1)

    tricky_healthy = {
        "age": 60,
        "sex": 0,
        "cp": 3,
        "trestbps": 120,
        "chol": 178,
        "fbs": 1,
        "restecg": 0,
        "thalach": 96,
        "exang": 0,
        "oldpeak": 0.0,
        "slope": 1,
        "ca": 0.0,
        "thal": 3.0
    }
    # ضربان حداکثر پایین (96) ولی در دیتاست سالم است!
    # نتیجه انتظاری: سالم (target = 0) — تست خوب برای بررسی overfitting
    test_cases = {
        "patient_1 (بیمار)":              patient_1,
        "healthy_1 (سالم)":               healthy_1,
        "high_risk_patient (بیمار شدید)": high_risk_patient,
        "young_healthy (سالم جوان)":      young_healthy,
        "high_chol_patient (سالم)":       high_chol_patient,
        "female_patient (بیمار زن)":      female_patient,
        "midage_patient (بیمار)":         midage_patient,
        "tricky_healthy (سالم)":          tricky_healthy,
    }
    sample_data = [
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : patient_1} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : healthy_1} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : high_risk_patient} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : young_healthy} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : high_chol_patient} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : female_patient} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : midage_patient} ,
        {"__name__" : "Ali" , "disease_name" : 'Heart disease' , "patients_data" : tricky_healthy}
    ]
    
    result = t.multiple_screening(*sample_data)
    print(json.dumps(result , ensure_ascii=False , indent=3))

    # for name, data in test_cases.items():
    #     print(f"\n{'='*50}")
    #     print(f"تست: {name}")
    #     try:
    #         result = t.Screening(disease_name='Heart disease', **data)
    #         print(f"خروجی مدل: {result}")
    #     except Exception as e:
    #         print(f"خطا: {e}")
    #     finally:
    #         print(f"{'='*50}\n")

def test_model_breast_cancer():
    malignant_1 = {
        "radius1": 17.99, "texture1": 10.38, "perimeter1": 122.8, "area1": 1001.0,
        "smoothness1": 0.1184, "compactness1": 0.2776, "concavity1": 0.3001,
        "concave_points1": 0.1471, "symmetry1": 0.2419, "fractal_dimension1": 0.07871,
        "radius2": 1.095, "texture2": 0.9053, "perimeter2": 8.589, "area2": 153.4,
        "smoothness2": 0.006399, "compactness2": 0.04904, "concavity2": 0.05373,
        "concave_points2": 0.01587, "symmetry2": 0.03003, "fractal_dimension2": 0.006193,
        "radius3": 25.38, "texture3": 17.33, "perimeter3": 184.6, "area3": 2019.0,
        "smoothness3": 0.1622, "compactness3": 0.6656, "concavity3": 0.7119,
        "concave_points3": 0.2654, "symmetry3": 0.4601, "fractal_dimension3": 0.1189,
    }# نتیجه انتظاری: بدخیم (target = 1)

    benign_1 = {
        "radius1": 13.54, "texture1": 14.36, "perimeter1": 87.46, "area1": 566.3,
        "smoothness1": 0.09779, "compactness1": 0.08129, "concavity1": 0.06664,
        "concave_points1": 0.04781, "symmetry1": 0.1885, "fractal_dimension1": 0.05766,
        "radius2": 0.2699, "texture2": 0.7886, "perimeter2": 2.058, "area2": 23.56,
        "smoothness2": 0.008462, "compactness2": 0.0146, "concavity2": 0.02387,
        "concave_points2": 0.01315, "symmetry2": 0.0198, "fractal_dimension2": 0.0023,
        "radius3": 15.11, "texture3": 19.26, "perimeter3": 99.7, "area3": 711.2,
        "smoothness3": 0.144, "compactness3": 0.1773, "concavity3": 0.239,
        "concave_points3": 0.1288, "symmetry3": 0.2977, "fractal_dimension3": 0.07259,
    }# نتیجه انتظاری: سالم (target = 0)

    large_malignant = {
        "radius1": 20.57, "texture1": 17.77, "perimeter1": 132.9, "area1": 1326.0,
        "smoothness1": 0.08474, "compactness1": 0.07864, "concavity1": 0.0869,
        "concave_points1": 0.07017, "symmetry1": 0.1812, "fractal_dimension1": 0.05667,
        "radius2": 0.5435, "texture2": 0.7339, "perimeter2": 3.398, "area2": 74.08,
        "smoothness2": 0.005225, "compactness2": 0.01308, "concavity2": 0.0186,
        "concave_points2": 0.0134, "symmetry2": 0.01389, "fractal_dimension2": 0.003532,
        "radius3": 24.99, "texture3": 23.41, "perimeter3": 158.8, "area3": 1956.0,
        "smoothness3": 0.1238, "compactness3": 0.1866, "concavity3": 0.2416,
        "concave_points3": 0.186, "symmetry3": 0.275, "fractal_dimension3": 0.08902,
    }
    # area1 = 1326، radius3 = 24.99 (بسیار بزرگ)
    # نتیجه انتظاری: بدخیم (target = 1)

    small_benign = {
        "radius1": 9.504, "texture1": 12.44, "perimeter1": 60.34, "area1": 273.9,
        "smoothness1": 0.1024, "compactness1": 0.06492, "concavity1": 0.02956,
        "concave_points1": 0.02076, "symmetry1": 0.1815, "fractal_dimension1": 0.06905,
        "radius2": 0.2773, "texture2": 0.9768, "perimeter2": 1.909, "area2": 15.7,
        "smoothness2": 0.009606, "compactness2": 0.01432, "concavity2": 0.01985,
        "concave_points2": 0.01421, "symmetry2": 0.02027, "fractal_dimension2": 0.002968,
        "radius3": 10.23, "texture3": 15.66, "perimeter3": 65.13, "area3": 314.9,
        "smoothness3": 0.1324, "compactness3": 0.1148, "concavity3": 0.08867,
        "concave_points3": 0.06227, "symmetry3": 0.245, "fractal_dimension3": 0.07773,
    }
    # تومور کوچک، احتمالاً خوش‌خیم
    # نتیجه انتظاری: سالم (target = 0)

    high_concavity_malignant = {
        "radius1": 14.25, "texture1": 22.15, "perimeter1": 96.42, "area1": 645.7,
        "smoothness1": 0.1049, "compactness1": 0.2008, "concavity1": 0.2135,
        "concave_points1": 0.08653, "symmetry1": 0.1949, "fractal_dimension1": 0.07292,
        "radius2": 0.7036, "texture2": 1.268, "perimeter2": 5.373, "area2": 60.78,
        "smoothness2": 0.009407, "compactness2": 0.07056, "concavity2": 0.06899,
        "concave_points2": 0.01848, "symmetry2": 0.017, "fractal_dimension2": 0.006113,
        "radius3": 17.67, "texture3": 29.51, "perimeter3": 119.1, "area3": 959.5,
        "smoothness3": 0.164, "compactness3": 0.6247, "concavity3": 0.6922,
        "concave_points3": 0.1785, "symmetry3": 0.2844, "fractal_dimension3": 0.1132,
    }
    # concavity1 = 0.2135 و compactness3 = 0.6247 (بالا)
    # نتیجه انتظاری: بدخیم (target = 1)

    borderline_benign = {
        "radius1": 12.86, "texture1": 18.0, "perimeter1": 83.19, "area1": 506.3,
        "smoothness1": 0.09934, "compactness1": 0.09546, "concavity1": 0.03889,
        "concave_points1": 0.02315, "symmetry1": 0.1718, "fractal_dimension1": 0.05997,
        "radius2": 0.2655, "texture2": 1.095, "perimeter2": 1.778, "area2": 20.35,
        "smoothness2": 0.005293, "compactness2": 0.01661, "concavity2": 0.02071,
        "concave_points2": 0.008179, "symmetry2": 0.01748, "fractal_dimension2": 0.002848,
        "radius3": 14.24, "texture3": 24.82, "perimeter3": 91.88, "area3": 622.1,
        "smoothness3": 0.1289, "compactness3": 0.2141, "concavity3": 0.1731,
        "concave_points3": 0.07926, "symmetry3": 0.2779, "fractal_dimension3": 0.07918,
    }
    # ویژگی‌های متوسط، تست خوب برای بررسی مرز تصمیم‌گیری
    # نتیجه انتظاری: سالم (target = 0)

    high_fractal_malignant = {
        "radius1": 19.17, "texture1": 24.8, "perimeter1": 132.4, "area1": 1123.0,
        "smoothness1": 0.0974, "compactness1": 0.2458, "concavity1": 0.2065,
        "concave_points1": 0.1118, "symmetry1": 0.2397, "fractal_dimension1": 0.078,
        "radius2": 0.9555, "texture2": 3.568, "perimeter2": 11.07, "area2": 116.2,
        "smoothness2": 0.003139, "compactness2": 0.08297, "concavity2": 0.0889,
        "concave_points2": 0.0409, "symmetry2": 0.04484, "fractal_dimension2": 0.01284,
        "radius3": 20.96, "texture3": 29.94, "perimeter3": 151.7, "area3": 1332.0,
        "smoothness3": 0.1037, "compactness3": 0.3903, "concavity3": 0.3639,
        "concave_points3": 0.1767, "symmetry3": 0.3176, "fractal_dimension3": 0.1023,
    }
    # texture2 = 3.568 (بسیار بالا نسبت به میانگین)
    # نتیجه انتظاری: بدخیم (target = 1)

    smooth_benign = {
        "radius1": 11.42, "texture1": 20.38, "perimeter1": 77.58, "area1": 386.1,
        "smoothness1": 0.1425, "compactness1": 0.2839, "concavity1": 0.2414,
        "concave_points1": 0.1052, "symmetry1": 0.2597, "fractal_dimension1": 0.09744,
        "radius2": 0.4956, "texture2": 1.156, "perimeter2": 3.445, "area2": 27.23,
        "smoothness2": 0.00911, "compactness2": 0.07458, "concavity2": 0.05661,
        "concave_points2": 0.01867, "symmetry2": 0.05963, "fractal_dimension2": 0.009208,
        "radius3": 14.91, "texture3": 26.5, "perimeter3": 98.87, "area3": 567.7,
        "smoothness3": 0.2098, "compactness3": 0.8663, "concavity3": 0.6869,
        "concave_points3": 0.2575, "symmetry3": 0.6638, "fractal_dimension3": 0.173,
    }
    # نکته مهم: این نمونه در دیتاست با target=1 (بدخیم) است!
    # ولی featureهایش شبیه موارد خوش‌خیم است — تست عالی برای false negative
    # نتیجه واقعی: بدخیم (target = 1) — اگر مدل سالم تشخیص داد، ضعف دارد

    t = Disease_diagnosis()

    test_cases = {
        "malignant_1 (بدخیم)":             malignant_1,
        "benign_1 (سالم)":                 benign_1,
        "large_malignant (بدخیم بزرگ)":    large_malignant,
        "small_benign (سالم کوچک)":        small_benign,
        "high_concavity_malignant (بدخیم)": high_concavity_malignant,
        "borderline_benign (سالم مرزی)":   borderline_benign,
        "high_fractal_malignant (بدخیم)":  high_fractal_malignant,
        "smooth_benign (بدخیم پنهان)":     smooth_benign,
    }

    expected = {
        "malignant_1 (بدخیم)":             "بدخیم",
        "benign_1 (سالم)":                 "سالم",
        "large_malignant (بدخیم بزرگ)":    "بدخیم",
        "small_benign (سالم کوچک)":        "سالم",
        "high_concavity_malignant (بدخیم)": "بدخیم",
        "borderline_benign (سالم مرزی)":   "سالم",
        "high_fractal_malignant (بدخیم)":  "بدخیم",
        "smooth_benign (بدخیم پنهان)":     "بدخیم",  # ← مهم!
    }

    for name, data in test_cases.items():
        print(f"\n{'='*60}")
        print(f"تست: {name}")
        print(f"انتظار: {expected[name]}")
        try:
            result = t.Screening(disease_name='Breast cancer', **data)
            print(f"خروجی مدل: {result}")
        except Exception as e:
            print(f"خطا: {e}")
        finally:
            print(f"{'='*60}")

def test_model_diabet_type2():
    diabetic_1 = {
    "Pregnancies": 6,
    "Glucose": 148,
    "BloodPressure": 72,
    "SkinThickness": 35,
    "Insulin": 0,
    "BMI": 33.6,
    "DiabetesPedigreeFunction": 0.627,
    "Age": 50
    }# نتیجه انتظاری: دیابتی (Outcome = 1)

    healthy_1 = {
        "Pregnancies": 1,
        "Glucose": 85,
        "BloodPressure": 66,
        "SkinThickness": 29,
        "Insulin": 0,
        "BMI": 26.6,
        "DiabetesPedigreeFunction": 0.351,
        "Age": 31
    }# نتیجه انتظاری: سالم (Outcome = 0)

    high_glucose_diabetic = {
        "Pregnancies": 2,
        "Glucose": 197,
        "BloodPressure": 70,
        "SkinThickness": 45,
        "Insulin": 543,
        "BMI": 30.5,
        "DiabetesPedigreeFunction": 0.158,
        "Age": 53
    }
    # گلوکز 197 (بالا)، انسولین 543 (بسیار بالا)
    # نتیجه انتظاری: دیابتی (Outcome = 1)

    obese_healthy = {
        "Pregnancies": 0,
        "Glucose": 100,
        "BloodPressure": 88,
        "SkinThickness": 60,
        "Insulin": 110,
        "BMI": 46.8,
        "DiabetesPedigreeFunction": 0.962,
        "Age": 31
    }# BMI = 46.8 (چاقی شدید) ولی در دیتاست سالم است!
    # نتیجه انتظاری: سالم (Outcome = 0) — تست عالی برای بررسی تعصب مدل به BMI

    high_pedigree_diabetic = {
        "Pregnancies": 0,
        "Glucose": 137,
        "BloodPressure": 40,
        "SkinThickness": 35,
        "Insulin": 168,
        "BMI": 43.1,
        "DiabetesPedigreeFunction": 2.288,
        "Age": 33
    }# DiabetesPedigreeFunction = 2.288 (بسیار بالا = سابقه خانوادگی قوی)
    # نتیجه انتظاری: دیابتی (Outcome = 1)

    young_healthy = {
        "Pregnancies": 1,
        "Glucose": 89,
        "BloodPressure": 66,
        "SkinThickness": 23,
        "Insulin": 94,
        "BMI": 28.1,
        "DiabetesPedigreeFunction": 0.167,
        "Age": 21
    }# سن جوان، گلوکز 89، BMI نرمال
    # نتیجه انتظاری: سالم (Outcome = 0)

    older_multipara_diabetic = {
        "Pregnancies": 17,
        "Glucose": 163,
        "BloodPressure": 72,
        "SkinThickness": 41,
        "Insulin": 114,
        "BMI": 40.9,
        "DiabetesPedigreeFunction": 0.817,
        "Age": 47
    }# ۱۷ بارداری، سن ۴۷، BMI 40.9
    # نتیجه انتظاری: دیابتی (Outcome = 1)

    high_insulin_healthy = {
        "Pregnancies": 7,
        "Glucose": 158,
        "BloodPressure": 70,
        "SkinThickness": 0,
        "Insulin": 0,
        "BMI": 29.8,
        "DiabetesPedigreeFunction": 0.207,
        "Age": 63
    }# انسولین 0 (گمشده)، BMI 29.8، گلوکز 158 — ظاهراً مرزی
    # نتیجه انتظاری: سالم (Outcome = 0) — تست رفتار مدل با داده گمشده

    borderline_glucose_diabetic = {
        "Pregnancies": 10,
        "Glucose": 139,
        "BloodPressure": 80,
        "SkinThickness": 0,
        "Insulin": 0,
        "BMI": 27.1,
        "DiabetesPedigreeFunction": 1.441,
        "Age": 57
    }# گلوکز 139 (مرزی)، pedigree بالا (1.441)
    # نتیجه انتظاری: دیابتی (Outcome = 1) — در دیتاست 0 است ولی با 139 معمولاً مرزی تلقی می‌شود
    # ⚠️ نکته: در دیتاست اصلی این نمونه Outcome=0 است! (تست false positive)

    extremely_obese_diabetic = {
        "Pregnancies": 0,
        "Glucose": 129,
        "BloodPressure": 110,
        "SkinThickness": 46,
        "Insulin": 130,
        "BMI": 67.1,
        "DiabetesPedigreeFunction": 0.319,
        "Age": 26
    }# BMI = 67.1 (چاقی مفرط)، فشار خون 110
    # نتیجه انتظاری: دیابتی (Outcome = 1)

    tricky_healthy = {
        "Pregnancies": 4,
        "Glucose": 197,
        "BloodPressure": 70,
        "SkinThickness": 39,
        "Insulin": 744,
        "BMI": 36.7,
        "DiabetesPedigreeFunction": 2.329,
        "Age": 31
    }
    # گلوکز 197، انسولین 744، pedigree 2.329 — همه بالا!
    # ولی در دیتاست سالم است!
    # نتیجه انتظاری: سالم (Outcome = 0) — تست عالی برای بررسی overfitting

    young_high_pedigree_diabetic = {
        "Pregnancies": 1,
        "Glucose": 128,
        "BloodPressure": 98,
        "SkinThickness": 41,
        "Insulin": 58,
        "BMI": 32.0,
        "DiabetesPedigreeFunction": 1.321,
        "Age": 33
    }
    # سن جوان (33) ولی pedigree بالا (1.321)
    # نتیجه انتظاری: دیابتی (Outcome = 1)

    t = Disease_diagnosis()

    test_cases = {
        "diabetic_1 (دیابتی)":                 diabetic_1,
        "healthy_1 (سالم)":                    healthy_1,
        "high_glucose_diabetic (دیابتی شدید)": high_glucose_diabetic,
        "obese_healthy (سالم چاق)":            obese_healthy,
        "high_pedigree_diabetic (دیابتی)":     high_pedigree_diabetic,
        "young_healthy (سالم جوان)":           young_healthy,
        "older_multipara_diabetic (دیابتی)":   older_multipara_diabetic,
        "high_insulin_healthy (سالم)":         high_insulin_healthy,
        "borderline_glucose_diabetic (سالم!)": borderline_glucose_diabetic,
        "extremely_obese_diabetic (دیابتی)":   extremely_obese_diabetic,
        "tricky_healthy (سالم!)":              tricky_healthy,
        "young_high_pedigree_diabetic (دیابتی)": young_high_pedigree_diabetic,
    }

    expected = {
        "diabetic_1 (دیابتی)":                 "دیابتی",
        "healthy_1 (سالم)":                    "سالم",
        "high_glucose_diabetic (دیابتی شدید)": "دیابتی",
        "obese_healthy (سالم چاق)":            "سالم",
        "high_pedigree_diabetic (دیابتی)":     "دیابتی",
        "young_healthy (سالم جوان)":           "سالم",
        "older_multipara_diabetic (دیابتی)":   "دیابتی",
        "high_insulin_healthy (سالم)":         "سالم",
        "borderline_glucose_diabetic (سالم!)": "سالم",
        "extremely_obese_diabetic (دیابتی)":   "دیابتی",
        "tricky_healthy (سالم!)":              "سالم",
        "young_high_pedigree_diabetic (دیابتی)": "دیابتی",
    }

    for name, data in test_cases.items():
        print(f"\n{'='*60}")
        print(f"تست: {name}")
        print(f"انتظار: {expected[name]}")
        try:
            result = t.Screening(disease_name='Diabet type2', **data)
            print(f"خروجی مدل: {result}")
        except Exception as e:
            print(f"خطا: {e}")
        finally:
            print(f"{'='*60}")

if __name__ == "__main__":
    test_model_heart_disease()
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
    