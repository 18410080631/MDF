import os
import json
from config import DATASET_NAME
from sklearn.metrics import accuracy_score, f1_score

if DATASET_NAME == 'FHM':
    data_src = 'data/FHM/data/dev_with_description_copy.jsonl'
    res = []
    y_true = []
    y_pred = []

    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            sample = json.loads(line.strip())
            labels[sample['id']] = sample['label']

    for filename in os.listdir('resultsFHM'):
        if not filename.endswith('.json'):
            continue
        with open(os.path.join('resultsFHM', filename), 'r', encoding='utf-8') as f:
            result = json.load(f)
            id = int(filename.split('.')[0])
            label = labels[id]
            pre = result['verdict']
            pred_label = 1 if pre == 'HARMFUL' else 0

            y_true.append(label)
            y_pred.append(pred_label)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    print(f'Accuracy: {acc:.4f}')
    print(f'F1-score: {f1:.4f}')

elif DATASET_NAME == "HARM":
    data_src = 'data/HARM/test_with_description_copy.jsonl'
    y_true = []
    y_pred = []

    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            sample = json.loads(line.strip())
            labels[sample['id']] = 0 if 'not harmful' in sample['labels'] else 1

    for filename in os.listdir('resultsHARM'):
        if not filename.endswith('.json'):
            continue
        with open(os.path.join('resultsHARM', filename), 'r', encoding='utf-8') as f:
            result = json.load(f)
            id = filename.split('.')[0]
            label = labels[id]
            pre = result['verdict']
            pred_label = 1 if pre == 'HARMFUL' else 0

            y_true.append(label)
            y_pred.append(pred_label)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    print(f'Accuracy: {acc:.4f}')
    print(f'F1-score: {f1:.4f}')