from pathlib import Path

root_path = Path(__file__).resolve().parents[1]

models ={
    "breast_cancer" : {
        "model" : fr"{root_path}\models\Breast_cancer\best_breast_cancer_model.pkl" ,
        "scaler" : fr"{root_path}\models\Breast_cancer\breast_cancer_scaler.pkl" ,
        "dataset" : fr"{root_path}\models\Breast_cancer\breast_cancer.csv"
    } ,

    "diabet_type2" : {
            "model" : fr"{root_path}\models\Diabet_type2\best_diabete_model.pkl" ,
            "scaler" : fr"{root_path}\models\Diabet_type2\diabete_scaler.pkl" ,
            "dataset" : fr"{root_path}\models\Diabet_type2\pima-diabetes-diagnostic-dataset_en.csv"
    } ,

    "heart_disease" : {
            "model" : fr"{root_path}\models\Heart_disease\best_heart_disease_model.pkl" ,
            "scaler" : fr"{root_path}\models\Heart_disease\heart_disease_scaler.pkl" ,
            "dataset" : fr"{root_path}\models\Heart_disease\heart_disease.csv"
    }
}

if __name__ == "__main__":
    print(root_path)