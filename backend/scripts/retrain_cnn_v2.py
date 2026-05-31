"""
Retrain CNN v2 on re-balanced dataset with strong augmentation
"""
import sys, io, json, time, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
import numpy as np
import torch, torch.nn as nn, torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'datasets' / 'balanced_dataset'
MODELS = BASE / 'models'
REPORTS = BASE / 'training_reports'
MODELS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)


class PlantDiseaseCNN(nn.Module):
    def __init__(self, num_classes=6):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True), nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True), nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Sequential(nn.Dropout(0.4), nn.Linear(256, num_classes))

    def forward(self, x):
        return self.classifier(self.features(x).view(x.size(0), -1))


class ImgDS(Dataset):
    def __init__(self, root, tfm=None):
        self.samples = []
        self.class_names = sorted([d.name for d in Path(root).iterdir() if d.is_dir()])
        self.c2i = {n: i for i, n in enumerate(self.class_names)}
        for d in Path(root).iterdir():
            if not d.is_dir():
                continue
            ci = self.c2i[d.name]
            for f in d.iterdir():
                if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    self.samples.append((str(f), ci))
        self.tfm = tfm

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        p, l = self.samples[idx]
        try:
            img = Image.open(p).convert('RGB')
            return self.tfm(img) if self.tfm else img, l
        except:
            return torch.zeros(3, 224, 224), l


def main():
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(0.5),
        transforms.RandomVerticalFlip(0.2),
        transforms.RandomRotation(20),
        transforms.ColorJitter(0.3, 0.3, 0.2, 0.1),
        transforms.RandomAffine(0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_ds = ImgDS(DATA / 'train', train_tf)
    val_ds = ImgDS(DATA / 'val', val_tf)
    test_ds = ImgDS(DATA / 'test', val_tf)
    class_names = train_ds.class_names

    print(f'Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}')
    print(f'Classes: {class_names}')

    train_ldr = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=0)
    val_ldr = DataLoader(val_ds, batch_size=32, shuffle=False, num_workers=0)
    test_ldr = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=0)

    device = torch.device('cpu')
    model = PlantDiseaseCNN(num_classes=len(class_names)).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f'Params: {n_params:,}')

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=7, factor=0.5)

    best_va = 0.0
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    EPOCHS = 20

    print(f'\n{"="*60}')
    print(f'Training {EPOCHS} epochs with strong augmentation...')
    print(f'{"="*60}')
    t0 = time.time()

    for ep in range(EPOCHS):
        model.train()
        tl, tc = 0.0, 0
        for imgs, lbls in train_ldr:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), lbls)
            loss.backward()
            optimizer.step()
            tl += loss.item() * imgs.size(0)
            tc += (model(imgs).argmax(1) == lbls).sum().item()

        model.eval()
        vl, vc = 0.0, 0
        with torch.no_grad():
            for imgs, lbls in val_ldr:
                imgs, lbls = imgs.to(device), lbls.to(device)
                out = model(imgs)
                vl += criterion(out, lbls).item() * imgs.size(0)
                vc += (out.argmax(1) == lbls).sum().item()

        tl /= len(train_ldr.dataset)
        vl /= len(val_ldr.dataset)
        ta = 100 * tc / len(train_ldr.dataset)
        va = 100 * vc / len(val_ldr.dataset)

        history['train_loss'].append(round(tl, 6))
        history['val_loss'].append(round(vl, 6))
        history['train_acc'].append(round(ta, 2))
        history['val_acc'].append(round(va, 2))

        scheduler.step(vl)
        if va > best_va:
            best_va = va
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'val_acc': va,
                'n_params': n_params,
            }, str(MODELS / 'best_cnn_v2.pth'))

        if (ep + 1) % 5 == 0 or ep == 0:
            print(f'  Epoch {ep+1:3d}/{EPOCHS} | '
                  f'T Loss: {tl:.4f} V Loss: {vl:.4f} | '
                  f'T Acc: {ta:.1f}% V Acc: {va:.1f}%')

    train_time = time.time() - t0
    print(f'\nDone in {train_time/60:.1f} min | Best Val Acc: {best_va:.1f}%')

    # Load best model
    ckpt = torch.load(str(MODELS / 'best_cnn_v2.pth'), map_location='cpu')
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    # ── Validation ──
    ap, al = [], []
    for imgs, lbls in val_ldr:
        ap.extend(model(imgs).argmax(1).cpu().numpy())
        al.extend(lbls.numpy())

    cm = confusion_matrix(al, ap)
    cr = classification_report(al, ap, target_names=class_names, output_dict=True, zero_division=0)
    va2 = np.mean(np.array(ap) == np.array(al))

    print(f'\n{"="*70}')
    print(f'  VALIDATION SET ({len(val_ds)} images) — Accuracy: {va2*100:.1f}%')
    print(f'{"="*70}')

    hdr = f'{"":>25s}' + ''.join(f'{n[:8]:>10s}' for n in class_names)
    print(f'\n{hdr}')
    for i, n in enumerate(class_names):
        print(f'{n:>25s}' + ''.join(f'{cm[i][j]:>10d}' for j in range(len(class_names))))

    print(f'\n{"Class":<25s} {"Prec":>8s} {"Rec":>8s} {"F1":>8s} {"Supp":>6s}')
    print('-' * 62)
    for n in class_names:
        r = cr[n]
        print(f'{n:<25s} {r["precision"]:>8.4f} {r["recall"]:>8.4f} {r["f1-score"]:>8.4f} {int(r["support"]):>6d}')
    for a in ['macro avg', 'weighted avg']:
        r = cr[a]
        print(f'{a:<25s} {r["precision"]:>8.4f} {r["recall"]:>8.4f} {r["f1-score"]:>8.4f} {int(r["support"]):>6d}')

    # ── Test ──
    tp, tl = [], []
    for imgs, lbls in test_ldr:
        tp.extend(model(imgs).argmax(1).cpu().numpy())
        tl.extend(lbls.numpy())
    ta2 = np.mean(np.array(tp) == np.array(tl))
    tcm = confusion_matrix(tl, tp)

    print(f'\n{"="*70}')
    print(f'  TEST SET ({len(test_ds)} images) — Accuracy: {ta2*100:.1f}%')
    print(f'{"="*70}')
    print(f'\n{hdr}')
    for i, n in enumerate(class_names):
        print(f'{n:>25s}' + ''.join(f'{tcm[i][j]:>10d}' for j in range(len(class_names))))

    # ── Plots ──
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names, ax=axes[0])
    axes[0].set_title(f'CNN v2 — Val Confusion Matrix (Acc: {va2*100:.1f}%)', fontweight='bold')
    cmn = cm.astype('float') / (cm.sum(axis=1, keepdims=True) + 1e-9)
    sns.heatmap(cmn, annot=True, fmt='.2f', cmap='YlOrRd', xticklabels=class_names, yticklabels=class_names, ax=axes[1])
    axes[1].set_title('CNN v2 — Normalized', fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(REPORTS / 'cnn_v2_val_cm.png'), dpi=150)
    plt.close()

    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.heatmap(tcm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names, ax=ax2)
    ax2.set_title(f'CNN v2 — Test Confusion Matrix (Acc: {ta2*100:.1f}%)', fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(REPORTS / 'cnn_v2_test_cm.png'), dpi=150)
    plt.close()

    fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
    axes3[0].plot(history['train_loss'], 'o-', label='Train', markersize=3)
    axes3[0].plot(history['val_loss'], 's-', label='Val', markersize=3)
    axes3[0].set_title('CNN v2 — Loss')
    axes3[0].legend()
    axes3[0].grid(alpha=0.3)
    axes3[1].plot(history['train_acc'], 'o-', label='Train', markersize=3)
    axes3[1].plot(history['val_acc'], 's-', label='Val', markersize=3)
    axes3[1].set_title('CNN v2 — Accuracy')
    axes3[1].legend()
    axes3[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(REPORTS / 'cnn_v2_curves.png'), dpi=150)
    plt.close()

    # ── JSON Report ──
    report = {
        'model': 'PlantDiseaseCNN_v2',
        'architecture': '4-Conv CNN + BatchNorm + Dropout',
        'n_params': n_params,
        'dataset': str(DATA),
        'train_samples': len(train_ds),
        'val_samples': len(val_ds),
        'test_samples': len(test_ds),
        'epochs': EPOCHS,
        'augmentation': 'Flip+Rotate+ColorJitter+Affine',
        'train_time_minutes': round(train_time / 60, 1),
        'val_accuracy': round(va2 * 100, 2),
        'test_accuracy': round(ta2 * 100, 2),
        'classes': class_names,
        'confusion_matrix_val': cm.tolist(),
        'confusion_matrix_test': tcm.tolist(),
        'classification_report': cr,
        'training_history': history,
    }
    with open(str(REPORTS / 'cnn_v2_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f'\n{"="*70}')
    print(f'  Reports saved to {REPORTS}/')
    print(f'  Model saved to {MODELS}/best_cnn_v2.pth')
    print(f'{"="*70}')


if __name__ == '__main__':
    main()
