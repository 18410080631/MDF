import json
import re
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score
def normalize_minmax(arr):
    arr = np.array(arr, dtype=float)
    min_val = arr.min()
    max_val = arr.max()
    if max_val - min_val < 1e-8:
        return arr.tolist()
    return ((arr - min_val) / (max_val - min_val)).tolist()
def normalize_zscore(arr):
    """
    Z-score标准化（均值为0，标准差为1）
    :param arr: 待标准化的列表/数组
    :return: 标准化后的列表，处理异常值（标准差为0时返回原数组）
    """
    # 转换为浮点型numpy数组，避免整数运算误差
    arr = np.array(arr, dtype=float)
    # 计算均值和标准差
    mean_val = arr.mean()
    std_val = arr.std()
    
    # 处理标准差为0的情况（所有元素相同），避免除以0
    if std_val < 1e-8:
        return arr.tolist()
    
    # 执行标准化计算并转回列表（保持和原函数一致的返回类型）
    normalized_arr = (arr - mean_val) / std_val
    return normalized_arr.tolist()
def train_logistic_regression(data, feature_names=None, C=1.0):
    """
    使用逻辑回归训练二分类模型。
    
    参数:
        data: List[List], 每个子列表为 [label, f1, f2, ..., fn]
        feature_names: 可选，特征名称列表（用于输出公式）
        C: 正则化强度（越小正则越强，默认 C=1.0）
    
    返回:
        dict 包含:
            - 'model': 训练好的 LogisticRegression 模型
            - 'scaler': StandardScaler 对象（用于 Python 环境 transform）
            - 'scaler_params': dict, {'mean': [...], 'scale': [...]}（可 JSON 保存）
            - 'weights': 特征权重（已还原到原始尺度）
            - 'intercept': 截距项
            - 'feature_names': 特征名
            - 'performance': {'accuracy': ..., 'f1': ...}
            - 'formula': 可读的线性判别公式字符串
            - 'train_predictions': 训练集预测标签
            - 'train_prediction_proba': 训练集预测概率
    """
    l = set()
    for d in data:
        l.add(d[0])
    if len(l)!=2:
        print(f"警告: 训练数据标签不唯一！标签集合: {l}，无法训练二分类模型。")
        return {
        'model': None,
        'scaler': None,
        'scaler_params': None,  # <-- 关键新增
        'weights': [],
        'intercept': 0.0,
        'feature_names': feature_names,
        'performance': {'accuracy': 1.0, 'f1': 1.0},
        'formula': "No model trained due to inconsistent labels.",
        'train_predictions': [],
        'train_prediction_proba': [],
        "feature_importance":[]
    }

    data = np.array(data)
    y = data[:, 0].astype(int)
    X_raw = data[:, 1:].astype(float)
    n_features = X_raw.shape[1]
    
    if feature_names is None:
        feature_names = [f'F{i}' for i in range(1, n_features + 1)]
    
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    # 训练逻辑回归
    model = LogisticRegression(C=C, solver='liblinear', random_state=42)
    model.fit(X_scaled, y)
    
    # 还原权重到原始尺度
    weights_original = weights_original = [float(w) for w in (model.coef_[0] / scaler.scale_)]
    intercept_original = model.intercept_[0] - np.sum(model.coef_[0] * scaler.mean_ / scaler.scale_)
    
    # 性能评估
    y_pred = model.predict(X_scaled)
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    # 构建可读公式
    terms = []
    for w, name in zip(weights_original, feature_names):
        if w >= 0:
            terms.append(f"+ {w:.3f} * {name}")
        else:
            terms.append(f"- {abs(w):.3f} * {name}")
    linear_part = " ".join(terms).lstrip("+ ")
    formula = f"Logit = {linear_part} {'+' if intercept_original >= 0 else '-'} {abs(intercept_original):.3f}"
    scaled_weights = [float(w) for w in model.coef_[0]]
    feature_importance = [
        {"feature": name, "abs_weight": abs(w)}
        for name, w in zip(feature_names, scaled_weights)
    ]
    # ✅ 新增：提取 scaler 的可序列化参数
    scaler_params = {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "n_features": int(n_features)
    }
    
    return {
        'model': model,
        'scaler': scaler,
        'scaler_params': scaler_params,  # <-- 关键新增
        'weights': weights_original,
        'intercept': intercept_original,
        'feature_names': feature_names,
        'performance': {'accuracy': acc, 'f1': f1},
        'formula': formula,
        'train_predictions': y_pred.tolist(),
        'train_prediction_proba': model.predict_proba(X_scaled).tolist(),
        "feature_importance":feature_importance
    }


with open('HARM/result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_res(scale_factor,b):
    train_data = []
    feature_names = None
    count = 0 
    for d in data.values():
        if "evidence_score" not in d or "scores" not in d or "refer_dimension" not in d:
            continue
        evidence_score = d["evidence_score"]
        scores = list(d["scores"]["harmful_scores"].values()) + list(d["scores"]["harmless_scores"].values())
        harmful_score_len = len(d["scores"]["harmful_scores"])
        # scores = normalize_minmax(scores)
        refer_dimension = d["refer_dimension"]
        #refer_dimension = normalize_minmax(refer_dimension)
        if len(evidence_score) != 8 or len(scores) != 16 or len(refer_dimension) != 16:
            continue
        harmful_evi_score = sum(evidence_score[:4])
        harmless_evi_score = sum(evidence_score[4:])
        #如果 harmful_evi_score > harmless_evi_score: s 中对应的 harmful_scores 全部加 0.1，否则全部加 -0.1
        scores = [s+harmful_evi_score for s in scores[:harmful_score_len]] + [s+harmless_evi_score for s in scores[harmful_score_len:]]
          # 改这个系数就能看到结果
        refer_dimension_scale = [s * scale_factor for s in refer_dimension]
        scores = [s + r for s, r in zip(scores, refer_dimension_scale)]
        feature_names = list(d["scores"]["harmful_scores"].keys()) + list(d["scores"]["harmless_scores"].keys())
        count += 1
        ground_truth = d["ground_truth"]
        features = [ground_truth] + scores
        train_data.append(features)
    res = train_logistic_regression(train_data, feature_names=feature_names)
    return res

from sklearn.metrics import accuracy_score, f1_score
import os
import json
import numpy as np
from tqdm import tqdm

def calculate_metrics(dataset_name, a, b, c, u):
    """计算指标，支持 4 个权重参数"""
    data_src = os.path.join(dataset_name, "result.json")
    origin_src = os.path.join(dataset_name, "id_scores.json")
    evi_src = os.path.join(dataset_name, "evi_score.json")
    
    with open(data_src, "r", encoding="utf-8") as f:
        result = json.load(f)
    with open(origin_src, "r", encoding="utf-8") as f:
        origin_scores = json.load(f)
    with open(evi_src, "r", encoding="utf-8") as f:
        evi_score_dict = json.load(f)  # 🔧 修复：避免变量名冲突
    
    scores = result[list(result.keys())[0]]["scores"]
    harmful_nums = len(scores['harmful_scores'])
    harmless_nums = len(scores['harmless_scores'])
    
    predictions = []
    ids = []
    
    for r in result.keys():
        res = result[r]
        if "scores" not in res or (len(res['scores']["harmful_scores"])+len(res['scores']["harmless_scores"])) != harmful_nums+harmless_nums:
            print(f"scores出错  {r}")
            continue
        if "refer_dimension" not in res or len(res["refer_dimension"]) != (harmful_nums+harmless_nums):
            print(f"refer_dimension出错   {r}")
            continue
        if "evidence_score" not in res or len(res["evidence_score"]) != 8:
            print(f"evidence_score出错  {r}")
            continue
        
        # 处理不同数据集的 ID 格式
        if dataset_name == "FHM":
            sid = str(int(r))
        elif dataset_name == "HARM":
            sid = r
        else:
            sid = r
            
        ori_score = origin_scores.get(sid, [])
        evi_scores = evi_score_dict.get(r, [0]*8)  # 🔧 修复：使用不同的变量名
        
        score = list(res['scores']["harmful_scores"].values()) + list(res['scores']["harmless_scores"].values())
        refer_dimension = res["refer_dimension"]
        
        if len(ori_score) != len(score) + 1:
            print(f"ori_score length mismatch for {r}")
            continue
            
        s = []
        for j in range(len(score)):
            # 🔧 融合公式：原始分 + a*辩论分 + b*维度分 + c*证据分
            fused = ori_score[j+1] + a*score[j] + b*refer_dimension[j] + c*evi_scores[j]
            s.append(fused)
        
        ids.append(r)
        pre1 = [res["ground_truth"]] + s
        predictions.append(pre1)
    
    if not predictions:
        return {"accuracy": 0.0, "macro_f1": 0.0}
    
    y_true = []
    y_pred = []
    
    for idx, d in enumerate(predictions):
        true_label = int(d[0])
        y_true.append(true_label)
        
        harmful_scores = d[1 : 1 + harmful_nums]
        harmless_scores = d[1 + harmful_nums : 1 + harmful_nums + harmless_nums]
        
        avg_harmful = sum(harmful_scores) / len(harmful_scores) if harmful_scores else 0
        avg_harmless = sum(harmless_scores) / len(harmless_scores) if harmless_scores else 0
        
        # 🔧 预测逻辑：u 是偏移阈值
        predict = 1 if avg_harmful > avg_harmless - u else 0
        y_pred.append(predict)
    
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    return {
        "accuracy": acc,
        "macro_f1": macro_f1
    }


# ================= 多目标参数搜索 =================
if __name__ == "__main__":
    
    # 🔧 参数搜索范围（根据实际需求调整步长）
    a_range = np.arange(0, 2.1, 0.2)      # 辩论 score 权重
    b_range = np.arange(0, 2.1, 0.2)      # refer_dimension 权重
    c_range = np.arange(0, 2.1, 0.2)      # 🔧 新增：evidence_score 权重
    u_range = np.arange(-1, 5.1, 0.5)     # 决策阈值偏移
    
    # 数据集权重（多目标优化）
    fhm_weight = 0.7
    harm_weight = 0.3
    
    best_total_score = -1.0
    best_results = {"FHM": {}, "HARM": {}}
    best_params = {"a": 0, "b": 0, "c": 0, "u": 0}
    
    # 计算总迭代次数（用于进度条）
    total_iterations = len(a_range) * len(b_range) * len(c_range) * len(u_range)
    print(f"[📊] 总搜索空间: {total_iterations} 次迭代 (a×b×c×u = {len(a_range)}×{len(b_range)}×{len(c_range)}×{len(u_range)})")
    
    with tqdm(total=total_iterations, desc="4D 参数网格搜索", unit="次") as pbar:
        for a in a_range:
            for b in b_range:
                for c in c_range:          # 🔧 新增 c 循环
                    for u in u_range:
                        try:
                            # 🔧 修复：调用时传入 4 个权重参数
                            resFHM = calculate_metrics("FHM", a, b, c, u)
                            resHARM = calculate_metrics("HARM", a, b, c, u)
                            
                            # 加权 F1 作为优化目标
                            current_score = (fhm_weight * resFHM['macro_f1']) + (harm_weight * resHARM['macro_f1'])
                            
                            if current_score > best_total_score:
                                best_total_score = current_score
                                best_params = {"a": a, "b": b, "c": c, "u": u}
                                
                                # 记录当前最优参数下的各自表现
                                best_results["FHM"] = {
                                    "f1": resFHM['macro_f1'], 
                                    "acc": resFHM['accuracy']
                                }
                                best_results["HARM"] = {
                                    "f1": resHARM['macro_f1'], 
                                    "acc": resHARM['accuracy']
                                }
                                
                                tqdm.write(f"\n[✨ NEW BEST] a={a:.1f}, b={b:.1f}, c={c:.1f}, u={u:.1f}")
                                tqdm.write(f"  → Weighted Score: {current_score:.4f}")
                                tqdm.write(f"  → FHM: F1={resFHM['macro_f1']:.4f}, Acc={resFHM['accuracy']:.4f}")
                                tqdm.write(f"  → HARM: F1={resHARM['macro_f1']:.4f}, Acc={resHARM['accuracy']:.4f}")
                            
                            pbar.set_postfix({
                                'Best': f'{best_total_score:.3f}',
                                'Cur': f'{current_score:.3f}'
                            })
                            
                        except Exception as e:
                            tqdm.write(f"[⚠️ Error] a={a},b={b},c={c},u={u}: {e}")
                            continue
                        finally:
                            pbar.update(1)
    
    # ================= 最终结果展示 =================
    print("\n" + "="*60)
    print("🏆 最优参数组合")
    print("="*60)
    print(f"  a (debate score):     {best_params['a']:.2f}")
    print(f"  b (refer dimension):  {best_params['b']:.2f}")
    print(f"  c (evidence score):   {best_params['c']:.2f}  🔧 新增")
    print(f"  u (threshold offset): {best_params['u']:.2f}")
    print()
    print("📈 数据集表现")
    print("-"*60)
    print(f"  FHM  → F1: {best_results['FHM']['f1']:.4f}  |  Acc: {best_results['FHM']['acc']:.4f}")
    print(f"  HARM → F1: {best_results['HARM']['f1']:.4f}  |  Acc: {best_results['HARM']['acc']:.4f}")
    print()
    print(f"🎯 加权总分: {best_total_score:.4f} (FHM×{fhm_weight} + HARM×{harm_weight})")
    print("="*60)
    
    # 💡 可选：保存最优参数
    import json
    with open("best_params.json", "w", encoding="utf-8") as f:
        json.dump({
            "params": best_params,
            "results": best_results,
            "weights": {"fhm": fhm_weight, "harm": harm_weight},
            "best_score": best_total_score
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 最优参数已保存至 best_params.json")
# for scale in np.arange(0.0, 4, 0.05):
#     # for b in np.arange(0.0, 1.0, 0.1):
#     res = get_res(scale,0.0)
#     if res['performance']['f1'] > best_f1:
#         best_f1 = res['performance']['f1']
#         best_acc = res['performance']['accuracy']
#         best_scale = scale
#         best_b = 0.0
# print(f"\n最佳 refer_dimension 权重系数: {best_scale:.1f}，最佳 b 系数: {best_b:.1f}，对应 F1 分数: {best_f1:.4f},准确率: {best_acc:.4f}")
# dataset_name,a,b,u  a代表辩论score权重 b代表refer_dimension权重 u代表

