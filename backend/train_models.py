import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from app.ml.deep_model import DiseaseTreatmentModel, EffectEvaluationModel, VideoAnalysisModel

class DiseaseDataset(Dataset):
    def __init__(self, data: List[Dict], transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        features = self._encode_features(item)
        treatment_label = item.get('treatment_type', 0)
        severity_label = item.get('severity_level', 1)
        return features, treatment_label, severity_label

    def _encode_features(self, item: Dict) -> torch.Tensor:
        disease_map = {
            "叶斑病": [1, 0, 0, 0, 0, 0],
            "锈病": [0, 1, 0, 0, 0, 0],
            "白粉病": [0, 0, 1, 0, 0, 0],
            "早疫病": [0, 0, 0, 1, 0, 0],
            "晚疫病": [0, 0, 0, 0, 1, 0],
            "健康": [0, 0, 0, 0, 0, 1]
        }

        severity_map = {
            "light": [1, 0, 0],
            "medium": [0, 1, 0],
            "severe": [0, 0, 1]
        }

        crop_map = {
            "番茄": [1, 0, 0],
            "黄瓜": [0, 1, 0],
            "其他": [0, 0, 1]
        }

        disease_vec = disease_map.get(item.get('disease', '健康'), [0, 0, 0, 0, 0, 1])
        severity_vec = severity_map.get(item.get('severity', 'medium'), [0, 1, 0])
        crop_vec = crop_map.get(item.get('crop_type', '其他'), [0, 0, 1])

        weather = item.get('weather', {})
        weather_temp = weather.get('temperature', 25) / 40.0
        weather_humidity = weather.get('humidity', 60) / 100.0

        env = item.get('env_conditions', {})
        env_ph = env.get('ph', 7.0) / 14.0
        env_moisture = env.get('soil_moisture', 50) / 100.0

        features = disease_vec + severity_vec + crop_vec + [weather_temp, weather_humidity, env_ph, env_moisture]
        return torch.tensor(features, dtype=torch.float32)

class EffectEvaluationDataset(Dataset):
    def __init__(self, data: List[Dict]):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        features = self._encode_features(item)
        effectiveness = item.get('effectiveness_score', 0.5)
        return features, torch.tensor([effectiveness], dtype=torch.float32)

    def _encode_features(self, item: Dict) -> torch.Tensor:
        before_count = item.get('before_count', 0) / 100.0
        after_count = item.get('after_count', 0) / 100.0
        reduction_rate = item.get('reduction_rate', 0) / 100.0
        severity = item.get('severity', 1) / 3.0
        treatment_type = item.get('treatment_type', 0) / 3.0
        time_interval = item.get('time_interval', 7) / 30.0
        confidence = item.get('confidence', 0.8)
        environmental_factor = item.get('environmental_factor', 0.5)

        features = [before_count, after_count, reduction_rate, severity, 
                   treatment_type, time_interval, confidence, environmental_factor]
        return torch.tensor(features, dtype=torch.float32)

def generate_synthetic_training_data(num_samples: int = 1000) -> Tuple[List[Dict], List[Dict]]:
    diseases = ["叶斑病", "锈病", "白粉病", "早疫病", "晚疫病", "健康"]
    severities = ["light", "medium", "severe"]
    crops = ["番茄", "黄瓜", "其他"]

    disease_data = []
    for _ in range(num_samples):
        disease_data.append({
            'disease': np.random.choice(diseases),
            'severity': np.random.choice(severities),
            'crop_type': np.random.choice(crops),
            'weather': {
                'temperature': np.random.uniform(15, 35),
                'humidity': np.random.uniform(40, 90)
            },
            'env_conditions': {
                'ph': np.random.uniform(5.5, 8.5),
                'soil_moisture': np.random.uniform(30, 80)
            },
            'treatment_type': np.random.randint(0, 6),
            'severity_level': np.random.randint(0, 3)
        })

    evaluation_data = []
    for _ in range(num_samples // 2):
        before_count = np.random.randint(10, 100)
        effectiveness = np.random.uniform(0, 1)
        after_count = int(before_count * (1 - effectiveness * 0.8))
        reduction_rate = ((before_count - after_count) / before_count * 100) if before_count > 0 else 0

        evaluation_data.append({
            'before_count': before_count,
            'after_count': after_count,
            'reduction_rate': reduction_rate,
            'severity': np.random.randint(0, 3),
            'treatment_type': np.random.randint(0, 4),
            'time_interval': np.random.randint(3, 21),
            'confidence': np.random.uniform(0.6, 0.95),
            'environmental_factor': np.random.uniform(0, 1),
            'effectiveness_score': effectiveness
        })

    return disease_data, evaluation_data

def train_treatment_model(model: DiseaseTreatmentModel, train_loader: DataLoader, 
                          val_loader: DataLoader, epochs: int = 50, 
                          learning_rate: float = 0.001) -> Dict[str, List[float]]:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    criterion_treatment = nn.CrossEntropyLoss()
    criterion_severity = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)

    history = {
        'train_loss': [],
        'val_loss': [],
        'train_accuracy': [],
        'val_accuracy': []
    }

    best_val_loss = float('inf')
    patience_counter = 0
    max_patience = 10

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for features, treatment_labels, severity_labels in train_loader:
            features, treatment_labels, severity_labels = \
                features.to(device), treatment_labels.to(device), severity_labels.to(device)

            optimizer.zero_grad()
            treatment_output, severity_output = model(features)

            loss_treatment = criterion_treatment(treatment_output, treatment_labels)
            loss_severity = criterion_severity(severity_output, severity_labels)
            loss = loss_treatment + 0.5 * loss_severity

            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(treatment_output.data, 1)
            train_total += treatment_labels.size(0)
            train_correct += (predicted == treatment_labels).sum().item()

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for features, treatment_labels, severity_labels in val_loader:
                features, treatment_labels, severity_labels = \
                    features.to(device), treatment_labels.to(device), severity_labels.to(device)

                treatment_output, severity_output = model(features)
                loss_treatment = criterion_treatment(treatment_output, treatment_labels)
                loss_severity = criterion_severity(severity_output, severity_labels)
                loss = loss_treatment + 0.5 * loss_severity

                val_loss += loss.item()
                _, predicted = torch.max(treatment_output.data, 1)
                val_total += treatment_labels.size(0)
                val_correct += (predicted == treatment_labels).sum().item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        train_accuracy = 100 * train_correct / train_total
        val_accuracy = 100 * val_correct / val_total

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_accuracy'].append(train_accuracy)
        history['val_accuracy'].append(val_accuracy)

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), 'best_treatment_model.pth')
        else:
            patience_counter += 1

        if patience_counter >= max_patience:
            print(f'Early stopping at epoch {epoch+1}')
            break

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, '
                  f'Train Acc: {train_accuracy:.2f}%, Val Acc: {val_accuracy:.2f}%')

    return history

def train_evaluation_model(model: EffectEvaluationModel, train_loader: DataLoader,
                           val_loader: DataLoader, epochs: int = 50,
                           learning_rate: float = 0.001) -> Dict[str, List[float]]:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)

    history = {
        'train_loss': [],
        'val_loss': [],
        'train_mae': [],
        'val_mae': []
    }

    best_val_loss = float('inf')
    patience_counter = 0
    max_patience = 10

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_mae = 0.0

        for features, targets in train_loader:
            features, targets = features.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_mae += torch.mean(torch.abs(outputs - targets)).item()

        model.eval()
        val_loss = 0.0
        val_mae = 0.0

        with torch.no_grad():
            for features, targets in val_loader:
                features, targets = features.to(device), targets.to(device)
                outputs = model(features)
                loss = criterion(outputs, targets)
                val_loss += loss.item()
                val_mae += torch.mean(torch.abs(outputs - targets)).item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        train_mae /= len(train_loader)
        val_mae /= len(val_loader)

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_mae'].append(train_mae)
        history['val_mae'].append(val_mae)

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), 'best_evaluation_model.pth')
        else:
            patience_counter += 1

        if patience_counter >= max_patience:
            print(f'Early stopping at epoch {epoch+1}')
            break

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, '
                  f'Train MAE: {train_mae:.4f}, Val MAE: {val_mae:.4f}')

    return history

def plot_training_history(history: Dict[str, List[float]], model_name: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(history['train_loss'], label='Train Loss', marker='o')
    axes[0].plot(history['val_loss'], label='Validation Loss', marker='s')
    axes[0].set_title(f'{model_name} - Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True)

    if 'train_accuracy' in history:
        axes[1].plot(history['train_accuracy'], label='Train Accuracy', marker='o')
        axes[1].plot(history['val_accuracy'], label='Validation Accuracy', marker='s')
        axes[1].set_title(f'{model_name} - Accuracy')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy (%)')
    else:
        axes[1].plot(history['train_mae'], label='Train MAE', marker='o')
        axes[1].plot(history['val_mae'], label='Validation MAE', marker='s')
        axes[1].set_title(f'{model_name} - MAE')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('MAE')

    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    filename = f'{model_name.lower()}_training_history.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Training history plot saved as {filename}')
    plt.close()

def evaluate_model(model: nn.Module, test_loader: DataLoader, model_type: str = 'classification') -> Dict[str, Any]:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    all_predictions = []
    all_targets = []
    total_loss = 0.0

    with torch.no_grad():
        if model_type == 'classification':
            criterion = nn.CrossEntropyLoss()
            for features, treatment_labels, severity_labels in test_loader:
                features, treatment_labels = features.to(device), treatment_labels.to(device)
                treatment_output, _ = model(features)
                loss = criterion(treatment_output, treatment_labels)
                total_loss += loss.item()

                _, predicted = torch.max(treatment_output.data, 1)
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(treatment_labels.cpu().numpy())
        else:
            criterion = nn.MSELoss()
            for features, targets in test_loader:
                features, targets = features.to(device), targets.to(device)
                outputs = model(features)
                loss = criterion(outputs, targets)
                total_loss += loss.item()

                all_predictions.extend(outputs.cpu().numpy().flatten())
                all_targets.extend(targets.cpu().numpy().flatten())

    avg_loss = total_loss / len(test_loader)

    if model_type == 'classification':
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

        accuracy = accuracy_score(all_targets, all_predictions)
        precision = precision_score(all_targets, all_predictions, average='weighted', zero_division=0)
        recall = recall_score(all_targets, all_predictions, average='weighted', zero_division=0)
        f1 = f1_score(all_targets, all_predictions, average='weighted', zero_division=0)

        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': classification_report(all_targets, all_predictions, zero_division=0)
        }
    else:
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

        mse = mean_squared_error(all_targets, all_predictions)
        mae = mean_absolute_error(all_targets, all_predictions)
        r2 = r2_score(all_targets, all_predictions)

        return {
            'loss': avg_loss,
            'mse': mse,
            'mae': mae,
            'r2_score': r2
        }

def main():
    print("=" * 60)
    print("深度学习模型训练开始")
    print("=" * 60)

    print("\n生成合成训练数据...")
    disease_data, evaluation_data = generate_synthetic_training_data(num_samples=1000)
    print(f"生成 {len(disease_data)} 条病害防治数据")
    print(f"生成 {len(evaluation_data)} 条效果评估数据")

    train_split = int(0.8 * len(disease_data))
    train_disease_data = disease_data[:train_split]
    val_disease_data = disease_data[train_split:]

    train_split = int(0.8 * len(evaluation_data))
    train_eval_data = evaluation_data[:train_split]
    val_eval_data = evaluation_data[train_split:]

    train_disease_dataset = DiseaseDataset(train_disease_data)
    val_disease_dataset = DiseaseDataset(val_disease_data)
    train_eval_dataset = EffectEvaluationDataset(train_eval_data)
    val_eval_dataset = EffectEvaluationDataset(val_eval_data)

    train_disease_loader = DataLoader(train_disease_dataset, batch_size=32, shuffle=True)
    val_disease_loader = DataLoader(val_disease_dataset, batch_size=32, shuffle=False)
    train_eval_loader = DataLoader(train_eval_dataset, batch_size=32, shuffle=True)
    val_eval_loader = DataLoader(val_eval_dataset, batch_size=32, shuffle=False)

    print("\n" + "=" * 60)
    print("训练病害防治模型")
    print("=" * 60)
    treatment_model = DiseaseTreatmentModel()
    treatment_history = train_treatment_model(
        treatment_model, train_disease_loader, val_disease_loader, 
        epochs=50, learning_rate=0.001
    )
    plot_training_history(treatment_history, 'Treatment Model')

    treatment_results = evaluate_model(treatment_model, val_disease_loader, 'classification')
    print("\n病害防治模型评估结果:")
    print(f"Loss: {treatment_results['loss']:.4f}")
    print(f"Accuracy: {treatment_results['accuracy']:.4f}")
    print(f"Precision: {treatment_results['precision']:.4f}")
    print(f"Recall: {treatment_results['recall']:.4f}")
    print(f"F1 Score: {treatment_results['f1_score']:.4f}")

    print("\n" + "=" * 60)
    print("训练效果评估模型")
    print("=" * 60)
    evaluation_model = EffectEvaluationModel()
    evaluation_history = train_evaluation_model(
        evaluation_model, train_eval_loader, val_eval_loader,
        epochs=50, learning_rate=0.001
    )
    plot_training_history(evaluation_history, 'Evaluation Model')

    evaluation_results = evaluate_model(evaluation_model, val_eval_loader, 'regression')
    print("\n效果评估模型评估结果:")
    print(f"Loss: {evaluation_results['loss']:.4f}")
    print(f"MSE: {evaluation_results['mse']:.4f}")
    print(f"MAE: {evaluation_results['mae']:.4f}")
    print(f"R² Score: {evaluation_results['r2_score']:.4f}")

    print("\n" + "=" * 60)
    print("模型训练完成")
    print("=" * 60)
    print("\n模型文件已保存:")
    print("- best_treatment_model.pth (病害防治模型)")
    print("- best_evaluation_model.pth (效果评估模型)")
    print("\n训练历史图表已保存:")
    print("- treatment_model_training_history.png")
    print("- evaluation_model_training_history.png")

if __name__ == "__main__":
    main()