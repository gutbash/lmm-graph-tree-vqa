import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc, confusion_matrix
from sklearn.preprocessing import KBinsDiscretizer, OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.decomposition import PCA
from pathlib import Path
from joblib import dump
from joblib import load
import torch
import timm
from torchvision import transforms
from PIL import Image

def read_data(csv_path: Path):
    print(f"Reading data from {csv_path}")
    return pd.read_csv(csv_path)

def extract_image_features(image_paths, model_name='efficientvit_l3.r384_in1k', target_size=512, device='cuda', batch_size=32):
    """
    extract_image_features function will extract features from the images using a pre-trained model.
    """
    print("Starting to extract image features...")
    # model_name can be set to any model supported by timm. For ViT, consider 'vit_base_patch16_224' as a starting point.
    model = timm.create_model(model_name, pretrained=True, num_classes=0, global_pool='avg')
    model.eval()
    model.to(device)

    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        print(f"Model {model_name} loaded and moved to {device}", file=f)

    preprocess = transforms.Compose([
        transforms.Resize((target_size, target_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Identify and process unique images
    path_to_features = {}

    def preprocess_batch(image_batch_paths):
        images = [Image.open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / img_path).convert('RGB') for img_path in image_batch_paths]
        tensors = [preprocess(img) for img in images]
        print(f"Preprocessed {len(tensors)} images.")
        return torch.stack(tensors).to(device)

    print("Processing unique images...")
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        img_tensors = preprocess_batch(batch_paths)

        with torch.no_grad():
            batch_features = model(img_tensors)

        for path, features in zip(batch_paths, batch_features):
            path_to_features[path] = features.cpu().numpy()

    # Map extracted features back to the original dataset order
    features = np.array([path_to_features[path] for path in image_paths])

    print("Image feature extraction complete.")
    return features

def apply_pca(features, n_components='mle'):
    """
    Apply PCA to reduce dimensions of features.
    If n_components is 'mle', PCA will choose the number of components by 'mle' algorithm.
    If n_components is None, it will retain components explaining a certain variance ratio.
    """
    print("Applying PCA to reduce dimensions...")
    pca = PCA(n_components=n_components, svd_solver='full', random_state=42)
    pca_features = pca.fit_transform(features)
    dump(pca, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/pca_image_model.joblib'))
    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        print(f"Reduced dimensions: {pca_features.shape[1]}")
    return pca_features

def feature_engineering(df, image_paths, device='cuda'):
    # The feature engineering steps will go here.
    # This will include binning, encoding, interaction terms, and text processing.
    # The output will be an engineered feature matrix X and targets y_reg and y_class.
    # Function to convert hex node_color to RGB
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    
    # Construct feature names
    feature_names = []
    
    # One-hot Encode 'edge_width'
    edge_width_encoder = OneHotEncoder(categories='auto', drop=None, sparse=False)
    edge_width_encoded = edge_width_encoder.fit_transform(df[['edge_width']])
    edge_width_features = [f'edge_width_{int(category)}' for category in edge_width_encoder.categories_[0]]
    feature_names.extend(edge_width_features)

    # Extract image features from the 'image_prompt' column which contains the image paths
    unique_image_paths = list(set(image_paths))
    image_features = extract_image_features(unique_image_paths, device=device)
    # Apply PCA to the image features
    pca_image_features = apply_pca(image_features, n_components=50)
    original_to_pca_index_map = {path: index for index, path in enumerate(unique_image_paths)}
    # Create names for PCA features
    pca_feature_names = [f'image_pca_{i}' for i in range(pca_image_features.shape[1])]
    feature_names.extend(pca_feature_names)
    
    # Create a mapping from unique image paths to their PCA-transformed features
    path_to_pca_features = dict(zip(unique_image_paths, pca_image_features))
    
    # Map PCA-transformed features back to the original dataset order, including handling duplicates
    ordered_pca_features = np.array([path_to_pca_features[path] for path in image_paths])

    # One-hot Encode 'num_nodes'
    num_nodes_encoder = OneHotEncoder(categories='auto', drop=None, sparse=False)
    num_nodes_encoded = num_nodes_encoder.fit_transform(df[['num_nodes']])
    num_nodes_features = [f'num_nodes_{category}' for category in num_nodes_encoder.categories_[0]]
    feature_names.extend(num_nodes_features)

    # Convert 'node_color' to RGB and normalize
    node_colors_rgb = np.array(list(map(hex_to_rgb, df['node_color']))) / 255.0

    # For RGB components of 'node_color'
    feature_names.extend(['node_color_rgb_red', 'node_color_rgb_green', 'node_color_rgb_blue'])

    # 3. Create Interaction Feature: 'num_nodes' * 'edge_width'
    node_edge_interaction = df['num_nodes'].values.reshape(-1, 1) * df['edge_width'].values.reshape(-1, 1)
    # For interaction feature
    feature_names.extend(['num_nodes_edge_width_interaction'])

    # 4. One-hot Encode 'structure', 'task', 'variation_id', and 'generation_id'
    structure_encoder = OneHotEncoder()
    structure_encoded = structure_encoder.fit_transform(df[['structure']]).toarray()
    structure_features = [f'structure_{category}' for category in structure_encoder.categories_[0]]
    feature_names.extend(structure_features)

    task_encoder = OneHotEncoder()
    task_encoded = task_encoder.fit_transform(df[['task']]).toarray()
    task_features = [f'task_{category}' for category in task_encoder.categories_[0]]
    feature_names.extend(task_features)

    variation_id_encoder = OneHotEncoder()
    variation_id_encoded = variation_id_encoder.fit_transform(df[['variation_id']].astype(str)).toarray()
    variation_id_features = [f'variation_id_{category}' for category in variation_id_encoder.categories_[0]]
    feature_names.extend(variation_id_features)

    generation_id_encoder = OneHotEncoder()
    generation_id_encoded = generation_id_encoder.fit_transform(df[['generation_id']].astype(str)).toarray()
    generation_id_features = [f'generation_id_{category}' for category in generation_id_encoder.categories_[0]]
    feature_names.extend(generation_id_features)
    
    # one hot encode 'text_prompt'
    text_prompt_encoder = OneHotEncoder()
    text_prompt_encoded = text_prompt_encoder.fit_transform(df[['text_prompt']]).toarray()
    text_prompt_features = [f'text_prompt_{category}' for category in text_prompt_encoder.categories_[0]]
    feature_names.extend(text_prompt_features)

    # Advanced NLP on 'text_prompt': Using TF-IDF followed by SVD for dimensionality reduction
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    text_prompt_tfidf = tfidf_vectorizer.fit_transform(df['text_prompt'])
    svd = TruncatedSVD(n_components=20, random_state=42)
    text_prompt_tfidf_svd = svd.fit_transform(text_prompt_tfidf)
    
    # Instead of adding TF-IDF vectorizer feature names directly to feature_names, 
    # we create SVD component feature names for clarity
    text_prompt_svd_feature_names = [f'text_prompt_svd_{i}' for i in range(text_prompt_tfidf_svd.shape[1])]
    feature_names.extend(text_prompt_svd_feature_names)
    
    # Number of components to examine
    n_components_to_examine = 5  # Or whatever number makes sense for your analysis

    for i in range(n_components_to_examine):
        component_loadings = svd.components_[i]
        loading_scores = dict(zip(feature_names, component_loadings))
        sorted_loading_scores = sorted(loading_scores.items(), key=lambda x: x[1], reverse=True)
        
        with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'w') as f:
        
            print(f"\nTop contributing terms for text_prompt_svd_{i}:", file=f)
            for term, score in sorted_loading_scores[:10]:  # Top 10 terms
                print(f"{term}: {score}", file=f)

            print(f"\nBottom contributing terms for text_prompt_svd_{i}:", file=f)
            for term, score in sorted_loading_scores[-10:]:  # Bottom 10 terms
                print(f"{term}: {score}", file=f)

    # Combining all new features into a single feature matrix X
    X = np.hstack([
        edge_width_encoded,  # Assuming it's 2D
        ordered_pca_features, # 2D from PCA
        num_nodes_encoded,  # Assuming it's 2D
        node_colors_rgb,  # Reshaping just in case
        node_edge_interaction,  # Assuming it's 2D
        structure_encoded,  # 2D from OneHotEncoder
        task_encoded,  # 2D from OneHotEncoder
        variation_id_encoded,  # 2D from OneHotEncoder
        generation_id_encoded,  # 2D from OneHotEncoder
        text_prompt_encoded,  # 2D from OneHotEncoder
        text_prompt_tfidf_svd,  # 2D from SVD
    ])
    
    assert X.shape[1] == len(feature_names), f"Mismatch between features and feature names: {X.shape[1]} != {len(feature_names)}"

    # Target for regression (similarity) and classification (match)
    y_reg = df['similarity'] / 100.0
    y_class = df['match']
    
    dump(feature_names, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/feature_names.joblib'))
    dump(X, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/X.joblib'))
    dump(svd, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/svd.joblib'))
    dump(tfidf_vectorizer, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/tfidf_vectorizer.joblib'))
    dump(text_prompt_tfidf_svd, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/text_prompt_tfidf_svd.joblib'))
    dump(pca_image_features, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/pca_image_features.joblib'))
    dump(image_features, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/image_features.joblib'))
    dump(y_reg, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/y_reg.joblib'))
    dump(y_class, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/y_class.joblib'))
    dump(text_prompt_tfidf, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/text_prompt_tfidf.joblib'))
    dump(original_to_pca_index_map, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/original_to_pca_index_map.joblib'))

    return X, y_reg, y_class, feature_names

def train_models(X, y_reg, y_class):
    # The model training steps will go here.
    # This will include splitting the data, training regression and classification models,
    # and printing out performance metrics.
    # Split the data for the regression task
    print("Training models...")
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)

    pipeline_reg = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])
    pipeline_reg.fit(X_train_reg, y_train_reg)
    y_pred_reg = pipeline_reg.predict(X_test_reg)
    mse_reg = mean_squared_error(y_test_reg, y_pred_reg)
    r2_reg = r2_score(y_test_reg, y_pred_reg)
    metrics_reg = {'mse': mse_reg, 'r2': r2_reg, 'y_test': y_test_reg, 'y_pred': y_pred_reg}

    # Split the data for the classification task
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(X, y_class, test_size=0.2, random_state=42)
    pipeline_class = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    pipeline_class.fit(X_train_class, y_train_class)

    # Predictions and probabilities for evaluation
    y_pred_class = pipeline_class.predict(X_test_class)
    y_pred_prob_class = pipeline_class.predict_proba(X_test_class)[:, 1]

    # Calculate metrics (assuming y_test_class is defined)
    accuracy_class = accuracy_score(y_test_class, y_pred_class)
    precision_class = precision_score(y_test_class, y_pred_class)
    recall_class = recall_score(y_test_class, y_pred_class)
    f1_class = f1_score(y_test_class, y_pred_class)

    # Update the metrics dictionary accordingly
    metrics_class = {
        'accuracy': accuracy_class, 'precision': precision_class,
        'recall': recall_class, 'f1': f1_class, 'y_test': y_test_class,
        'y_pred': y_pred_class, 'y_pred_prob': y_pred_prob_class
    }

    # After fitting the regression model:
    y_train_pred_reg = pipeline_reg.predict(X_train_reg)
    mse_train_reg = mean_squared_error(y_train_reg, y_train_pred_reg)
    r2_train_reg = r2_score(y_train_reg, y_train_pred_reg)
    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        print("Training Regression Metrics:", {'mse': mse_train_reg, 'r2': r2_train_reg}, file=f)

    # Similarly, after fitting the classification model:
    y_train_pred_class = pipeline_class.predict(X_train_class)
    accuracy_train_class = accuracy_score(y_train_class, y_train_pred_class)
    precision_train_class = precision_score(y_train_class, y_train_pred_class)
    recall_train_class = recall_score(y_train_class, y_train_pred_class)
    f1_train_class = f1_score(y_train_class, y_train_pred_class)
    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        print("Training Classification Metrics:", {'accuracy': accuracy_train_class, 'precision': precision_train_class, 'recall': recall_train_class, 'f1': f1_train_class}, file=f)

    print("Model training complete.")

    dump(pipeline_reg, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/regression_model.joblib'))
    dump(pipeline_class, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/classification_model.joblib'))
    dump(metrics_reg, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/regression_metrics.joblib'))
    dump(metrics_class, Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path('results/classification_metrics.joblib'))

    return pipeline_reg, pipeline_class, metrics_reg, metrics_class

def print_feature_importance(pipeline_reg, pipeline_class, feature_names):
    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        # For Linear Regression (effect sizes)
        print("Feature importances for Linear Regression:", file=f)
        # Assuming reg_model is a LinearRegression model or a pipeline ending with it
        if hasattr(pipeline_reg, 'named_steps'):
            reg_coefs = pipeline_reg.named_steps['regressor'].coef_
        else:
            reg_coefs = pipeline_reg.coef_

        for feature, coef in zip(feature_names, reg_coefs):
            print(f"{feature}: {coef:.4f}", file=f)

        # For Logistic Regression (effect sizes)
        print("\nFeature importances for Logistic Regression:", file=f)
        # Access the 'classifier' step in the pipeline
        if hasattr(pipeline_class, 'named_steps'):
            class_coefs = np.abs(pipeline_class.named_steps['classifier'].coef_[0])
        else:
            class_coefs = np.abs(pipeline_class.coef_[0])

        sorted_indices = np.argsort(class_coefs)[::-1]  # Sorting them in descending order
        for idx in sorted_indices:
            print(f"{feature_names[idx]}: {class_coefs[idx]:.4f}", file=f)

def main(csv_path):
    # Read the data
    df = read_data(csv_path)

    image_paths = df['image_prompt'].tolist()  # Convert the column to a list

    # Perform feature engineering
    X, y_reg, y_class, feature_names = feature_engineering(df, image_paths)

    # Train the models and get metrics
    pipeline_reg, pipeline_class, metrics_reg, metrics_class = train_models(X, y_reg, y_class)

    print_feature_importance(pipeline_reg, pipeline_class, feature_names)

    print("Regression Metrics:", metrics_reg)
    print("Classification Metrics:", metrics_class)

    # Print out the metrics
    with open(Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / f'results/analysis.txt', 'a') as f:
        print("Regression Metrics:", metrics_reg, file=f)
        print("Classification Metrics:", metrics_class, file=f)

if __name__ == "__main__":
    print("Script execution started.")
    # Provide the path to your CSV file here
    CSV_PATH = Path('/content/drive/MyDrive/lmm-graph-tree-vqa') / Path("results/archive/large-course/deepmind-zero_shot-large_course.csv")
    main(CSV_PATH)
    print("Script execution completed.")