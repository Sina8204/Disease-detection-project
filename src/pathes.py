from pathlib import Path
root_path = Path(__file__).resolve().parents[1]

models_json_path = "models"

if __name__ == "__main__":
    p = root_path.joinpath("Model_assets/Breast_cancer/best_breast_cancer_model.pkl")
    print(p)