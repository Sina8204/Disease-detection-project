from pathlib import Path

root_path = Path(__file__).resolve().parents[1]

models ={
    "breast_cancer" : {
        "model" : fr"{root_path}\models\Breast_cancer\best_breast_cancer_model.pkl" ,
        "scaler" : fr"{root_path}\models\Breast_cancer\breast_cancer_scaler.pkl" ,
        "dataset" : fr"{root_path}\models\Breast_cancer\breast_cancer.csv" ,
        "features" : ['radius1', 'texture1', 'perimeter1', 
                    'area1', 'smoothness1', 'compactness1', 
                    'concavity1', 'concave_points1', 'symmetry1', 
                    'fractal_dimension1', 'radius2', 'texture2', 
                    'perimeter2', 'area2', 'smoothness2', 
                    'compactness2', 'concavity2', 'concave_points2', 
                    'symmetry2', 'fractal_dimension2', 'radius3', 
                    'texture3', 'perimeter3', 'area3', 
                    'smoothness3', 'compactness3', 'concavity3', 
                    'concave_points3', 'symmetry3', 'fractal_dimension3']
    } ,

    "diabet_type2" : {
            "model" : fr"{root_path}\models\Diabet_type2\best_diabete_model.pkl" ,
            "scaler" : fr"{root_path}\models\Diabet_type2\diabete_scaler.pkl" ,
            "dataset" : fr"{root_path}\models\Diabet_type2\pima-diabetes-diagnostic-dataset_en.csv" ,
            "features" : ['Pregnancies', 'Glucose', 'BloodPressure', 
                        'SkinThickness', 'Insulin', 'BMI', 
                        'DiabetesPedigreeFunction', 'Age']
    } ,

    "heart_disease" : {
            "model" : fr"{root_path}\models\Heart_disease\best_heart_disease_model.pkl" ,
            "scaler" : fr"{root_path}\models\Heart_disease\heart_disease_scaler.pkl" ,
            "dataset" : fr"{root_path}\models\Heart_disease\heart_disease.csv" ,
            "features" : ['age', 'sex', 'cp', 
                        'trestbps', 'chol', 'fbs', 
                        'restecg', 'thalach', 'exang', 
                        'oldpeak', 'slope', 'ca', 'thal']
    }
}

if __name__ == "__main__":
    print(root_path)