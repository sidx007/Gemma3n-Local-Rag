import json
from classify import classify_query_by_similarity
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
# Read JSON file and convert to Python list
def json_file_to_list(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data




def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    
    return dot_product / (norm_vec1 * norm_vec2)


def predict(query: str, embeddings: HuggingFaceEmbeddings, positive_embeddings: np.ndarray, threshold: float=0.026198) -> bool:
    query_embedding = embeddings.embed_query(query)
    
    positive_similarities = []
    for pos_emb in positive_embeddings:
        sim = cosine_similarity(query_embedding, pos_emb)
        positive_similarities.append(sim)
    
    avg_positive_similarity = np.mean(positive_similarities)
    
    similarity = avg_positive_similarity
    print(similarity)
    return similarity < threshold

def prepare_training_data(positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings):
    """Prepare training data with similarity scores and labels"""
    X = []  # Similarity scores
    y = []  # Labels (1 for positive class, 0 for negative class)
    
    # Calculate similarities for positive samples
    for i, sample in enumerate(positive_samples):
        query_embedding = embeddings.embed_query(sample)
        
        # Calculate average similarity to positive embeddings
        pos_similarities = []
        for pos_emb in positive_embeddings:
            sim = cosine_similarity(query_embedding, pos_emb)
            pos_similarities.append(sim)
        
        avg_pos_similarity = np.mean(pos_similarities)
        
        X.append([avg_pos_similarity])  # Feature: average similarity to positive class
        y.append(1)  # Label: positive class
    
    # Calculate similarities for negative samples
    for i, sample in enumerate(negative_samples):
        query_embedding = embeddings.embed_query(sample)
        
        # Calculate average similarity to positive embeddings
        pos_similarities = []
        for pos_emb in positive_embeddings:
            sim = cosine_similarity(query_embedding, pos_emb)
            pos_similarities.append(sim)
        
        avg_pos_similarity = np.mean(pos_similarities)
        
        X.append([avg_pos_similarity])  # Feature: average similarity to positive class
        y.append(0)  # Label: negative class
    
    return np.array(X), np.array(y)

def find_optimal_threshold_linear_regression(positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings):
    """Find optimal threshold using linear regression approach"""
    
    # Prepare training data
    X, y = prepare_training_data(positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings)
    
    # Split data into train and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Fit linear regression model
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    
    # The optimal threshold is where the linear regression predicts 0.5 (decision boundary)
    # For linear regression: y = mx + b, solve for x when y = 0.5
    # 0.5 = m*x + b  =>  x = (0.5 - b) / m
    optimal_threshold = (0.5 - lr_model.intercept_) / lr_model.coef_[0]
    
    print(f"Linear Regression Model:")
    print(f"Coefficient (slope): {lr_model.coef_[0]:.6f}")
    print(f"Intercept: {lr_model.intercept_:.6f}")
    print(f"Optimal threshold (decision boundary): {optimal_threshold:.6f}")
    
    # Validate the threshold
    val_predictions = [predict(positive_samples[i] if i < len(positive_samples) else negative_samples[i - len(positive_samples)], 
                              embeddings, positive_embeddings, negative_embeddings, optimal_threshold) 
                      for i in range(len(X_val))]
    
    val_accuracy = accuracy_score(y_val, val_predictions)
    print(f"Validation accuracy with optimal threshold: {val_accuracy:.4f}")
    
    return optimal_threshold, lr_model, val_accuracy

def grid_search_threshold(positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings, 
                         threshold_range=None, cv_folds=5):
    """Alternative: Grid search approach to find optimal threshold"""
    
    if threshold_range is None:
        # Create threshold range based on similarity distribution
        all_similarities = []
        
        # Calculate similarities for all samples
        for sample in positive_samples + negative_samples:
            query_embedding = embeddings.embed_query(sample)
            pos_similarities = []
            for pos_emb in positive_embeddings:
                sim = cosine_similarity(query_embedding, pos_emb)
                pos_similarities.append(sim)
            avg_sim = np.mean(pos_similarities)
            all_similarities.append(avg_sim)
        
        min_sim = min(all_similarities)
        max_sim = max(all_similarities)
        threshold_range = np.linspace(min_sim, max_sim, 100)
    
    # Prepare full dataset
    X, y = prepare_training_data(positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings)
    
    best_threshold = 0.5
    best_accuracy = 0.0
    threshold_accuracies = []
    
    print("Grid search for optimal threshold...")
    
    for threshold in threshold_range:
        # Cross-validation
        fold_accuracies = []
        
        for fold in range(cv_folds):
            # Split data for this fold
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=fold, stratify=y)
            
            # Make predictions with current threshold
            val_predictions = []
            for i, similarity_score in enumerate(X_val):
                prediction = 1 if similarity_score[0] > threshold else 0
                val_predictions.append(prediction)
            
            fold_accuracy = accuracy_score(y_val, val_predictions)
            fold_accuracies.append(fold_accuracy)
        
        avg_accuracy = np.mean(fold_accuracies)
        threshold_accuracies.append((threshold, avg_accuracy))
        
        if avg_accuracy > best_accuracy:
            best_accuracy = avg_accuracy
            best_threshold = threshold
    
    print(f"Best threshold from grid search: {best_threshold:.6f}")
    print(f"Best cross-validation accuracy: {best_accuracy:.4f}")
    
    return best_threshold, best_accuracy, threshold_accuracies

def evaluate_threshold(threshold, positive_samples, negative_samples, embeddings, positive_embeddings, negative_embeddings):
    """Evaluate a specific threshold on the dataset"""
    
    all_samples = positive_samples + negative_samples
    true_labels = [1] * len(positive_samples) + [0] * len(negative_samples)
    
    predictions = []
    for sample in all_samples:
        prediction = predict(sample, embeddings, positive_embeddings, negative_embeddings, threshold)
        predictions.append(int(prediction))
    
    accuracy = accuracy_score(true_labels, predictions)
    report = classification_report(true_labels, predictions, target_names=['Negative', 'Positive'])
    
    print(f"\nEvaluation Results for threshold = {threshold:.6f}")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)
    
    return accuracy, predictions

def plot_threshold_analysis(threshold_accuracies):
    """Plot threshold vs accuracy curve"""
    try:
        thresholds = [x[0] for x in threshold_accuracies]
        accuracies = [x[1] for x in threshold_accuracies]
        
        plt.figure(figsize=(10, 6))
        plt.plot(thresholds, accuracies, 'b-', linewidth=2)
        plt.xlabel('Threshold')
        plt.ylabel('Accuracy')
        plt.title('Threshold vs Accuracy')
        plt.grid(True)
        
        # Mark the best threshold
        best_idx = np.argmax(accuracies)
        plt.plot(thresholds[best_idx], accuracies[best_idx], 'ro', markersize=10, label=f'Best: {thresholds[best_idx]:.4f}')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("Matplotlib not available. Cannot plot threshold analysis.")

def main_threshold_optimization():
    """Main function to run threshold optimization"""
    
    print("Starting threshold optimization...")
    
    # Method 1: Linear Regression Approach
    print("\n" + "="*50)
    print("METHOD 1: Linear Regression Approach")
    print("="*50)
    
    try:
        optimal_threshold_lr, lr_model, lr_accuracy = find_optimal_threshold_linear_regression(
            positive, negative, embeddings, positive_embeddings, negative_embeddings
        )
    except Exception as e:
        print(f"Linear regression approach failed: {e}")
        optimal_threshold_lr = 0.5
    
    # Method 2: Grid Search Approach
    print("\n" + "="*50)
    print("METHOD 2: Grid Search Approach")
    print("="*50)
    
    optimal_threshold_grid, grid_accuracy, threshold_accuracies = grid_search_threshold(
        positive, negative, embeddings, positive_embeddings, negative_embeddings
    )
    
    # Compare both methods
    print("\n" + "="*50)
    print("COMPARISON OF METHODS")
    print("="*50)
    
    print(f"Linear Regression Threshold: {optimal_threshold_lr:.6f} (Accuracy: {lr_accuracy:.4f})")
    print(f"Grid Search Threshold: {optimal_threshold_grid:.6f} (Accuracy: {grid_accuracy:.4f})")
    
    # Use the better performing method
    if grid_accuracy >= lr_accuracy:
        best_threshold = optimal_threshold_grid
        print(f"\nUsing Grid Search threshold: {best_threshold:.6f}")
    else:
        best_threshold = optimal_threshold_lr
        print(f"\nUsing Linear Regression threshold: {best_threshold:.6f}")
    
    # Final evaluation
    print("\n" + "="*50)
    print("FINAL EVALUATION")
    print("="*50)
    
    final_accuracy, predictions = evaluate_threshold(
        best_threshold, positive, negative, embeddings, positive_embeddings, negative_embeddings
    )
    
    # Plot analysis (if matplotlib is available)
    plot_threshold_analysis(threshold_accuracies)
    
    return best_threshold, final_accuracy

# Run the optimization
if __name__ == "__main__":
    positive = json_file_to_list('data/oos_test.json') + json_file_to_list('data/oos_train.json')
    positive = [item[0] for item in positive]  # Extract 'text' field from each item
    embeddings = HuggingFaceEmbeddings(model_name="C:\\models\\static-mrl")
    positive_embeddings = np.array(embeddings.embed_documents(positive))
    print(predict("Who is the president of france", embeddings, positive_embeddings))
    print(predict("Hello there", embeddings, positive_embeddings))
    print(predict("What is the amex hackathon about", embeddings, positive_embeddings))
    print(predict("What is the capital of France?", embeddings, positive_embeddings))
    print(predict("What is the capital of ", embeddings, positive_embeddings))
