from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME
import time
import json
import os
from tqdm import tqdm
def get_description_of_meme(meme_text: str,meme_src:str) -> str:
    """获取对meme的客观描述"""
    system_prompt = """
You are a precision Image-to-Text Transcriber. Your goal is to provide objective, high-density visual data for accessibility indexing. 
### GUIDELINES:
1. **Objectivity**: Describe physical attributes (colors, shapes, textures) and identify public figures only if they are clearly recognizable for indexing purposes.
2. **Neutrality**: Treat all elements as graphical data. Focus on the spatial arrangement of text and subjects.
3. **Format**: Use a technical, inventory-style tone. Avoid any evaluative adjectives or socio-political analysis.
"""
    evidence_judge_template = (
"""
Generate a Concise Visual Data Audit. Start directly with "Visual Audit Summary:".
1. **Subjects**: List individuals (Left to Right). Briefly state their physical appearance and clothing.
2. **Text**: Transcribe all visible text verbatim. Note its position (e.g., "Bold white text at bottom").
3. **Setting**: 1-sentence description of the background environment.
4. **Graphic Overlays**: Identify any added symbols, logos, or digital edits.
5. **Image Medium**: Define the format (e.g., "Photograph with digital text overlay").
**Constraint**: Keep the entire response under 800 words. No warnings or preambles."""
    )
    llm_tool = LLMTool(model_name=MODEL_NAME, temperature=1.0)
    fact_judge_response = llm_tool.call_llm(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": evidence_judge_template}],
        meme_src=meme_src,
        temperature=TEMPERATURE,
        max_tokens=4096
    )
    print(f"✅ 模因描述: {fact_judge_response}")
    return fact_judge_response
if DATASET_NAME=="FHM":
    data_src = 'data/FHM/data/dev.jsonl'
    img_src = 'data/FHM/data'
elif DATASET_NAME=="MAMI":
    data_src = 'data/MAMI/data/test.tsv'
    img_src = 'data/MAMI/data/test_images'
elif DATASET_NAME=="HARM":
    data_src = 'data/HARM/test.jsonl'
    img_src = 'data/HARM/images'
else:
    raise ValueError("Unsupported DATASET_NAME. Choose either 'FHM' or 'MAMI'.")
if DATASET_NAME == 'FHM':
    output_path = data_src.replace('.jsonl', '_with_description.jsonl')
    temp_path = output_path + '.tmp'  # 临时文件
    # 步骤1: 读取并过滤，保留 description >= 70 的数据
    valid_imgs = set()
    kept_count = 0
    removed_count = 0
    try:
        with open(output_path, 'r', encoding='utf-8') as f_in, \
             open(temp_path, 'w', encoding='utf-8') as f_out:
            for line in tqdm(f_in, desc="清理无效description"):
                try:
                    sample = json.loads(line.strip())
                    description = sample.get('description', '')
                    if len(description) >= 110:
                        # 保留有效数据
                        f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')
                        valid_imgs.add(sample['img'])
                        kept_count += 1
                    else:
                        # 跳过无效数据（相当于删除）
                        removed_count += 1
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️ 跳过无效行: {e}")
                    continue
        # 步骤2: 用临时文件替换原文件
        os.replace(temp_path, output_path)
        print(f"✅ 清理完成！保留 {kept_count} 条，删除 {removed_count} 条 description < 110 的数据")
    except FileNotFoundError:
        print(f"ℹ️  {output_path} 不存在，无需清理")
    # 步骤3: 继续增量处理新数据
    
    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'a', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        skipped_count = 0
        processed_count = 0
        for idx, line in tqdm(enumerate(lines), total=len(lines), desc="增量处理"):
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            img_name = sample['img']
            # 如果这个 img 已经在有效数据中，跳过
            if img_name in valid_imgs:
                skipped_count += 1
                continue
            # 处理新的样本
            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['img']}"
            description = get_description_of_meme(meme_text, meme_src)
            if not description or len(description) < 110:
                print(img_name)
                print(f"⚠️ 描述过短，跳过 (行 {idx + 1})")
                continue
            sample['description'] = description
            # 追加写入
            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')
            processed_count += 1
            
        print(f"✅ 完成！新增处理 {processed_count} 条，跳过 {skipped_count} 条已存在的记录")
        
elif DATASET_NAME == 'MAMI':
    import pandas as pd
    import os
    from tqdm import tqdm
    with open("data/MAMI/data/supplement.json", 'r', encoding='utf-8') as f:
        supplement = json.load(f)
    # 路径定义
    img_src = 'data/MAMI/data/test_images'
    output_path = data_src.replace('.tsv', '_with_description.tsv')
    LENGTH_THRESHOLD = 110  # MAMI 描述相对较短，可根据需求调整阈值
    processed_files = set()
    # --- 步骤 1: 检查已处理的数据 (断点续传) ---
    if os.path.exists(output_path):
        # 读取已生成的部分结果
        existing_df = pd.read_csv(output_path, sep='\t')
        # 只有 description 字段不为空且长度达标的才算处理过
        valid_mask = existing_df['description'].fillna('').str.len() >= LENGTH_THRESHOLD
        processed_files = set(existing_df.loc[valid_mask, 'file_name'].tolist())
        print(f"✅ [MAMI] 发现历史数据：已跳过 {len(processed_files)} 条有效记录")


    # --- 步骤 2: 增量处理 ---
    # 读取原始输入文件
    raw_data = pd.read_csv(data_src, sep='\t')
    
    skipped_count = 0
    processed_count = 0
    failed_count = 0

    # 检查输出文件是否存在，若不存在则需要写入表头
    write_header = not os.path.exists(output_path)

    # 使用 'a' 模式打开文件进行逐行追加
    with open(output_path, 'a', encoding='utf-8') as f_out:
        for idx, row in tqdm(raw_data.iterrows(), total=len(raw_data), desc="[MAMI] 增量生成描述"):
            file_name = row['file_name']
            # 检查是否已处理过
            if file_name in processed_files:
                skipped_count += 1
                continue
            meme_text = row['text']
            file_name = row['file_name']
            meme_src_path = f"{img_src}/{file_name}"
            # 检查图片是否存在
            if not os.path.exists(meme_src_path):
                print(f"❌ [MAMI] 图片不存在: {meme_src_path}")
                failed_count += 1
                continue
            try:
                # 调用 LLM 获取描述
                if file_name in supplement:
                    description = supplement[file_name]
                else:
                    description = get_description_of_meme(meme_text, meme_src_path)
                # 质量校验
                if len(description) < LENGTH_THRESHOLD:
                    print(f"⚠️ [MAMI] 描述过短或无效，跳过 ({file_name})")
                    failed_count += 1
                    continue
                # 构造当前行数据
                current_row = row.copy()
                current_row['description'] = description
                # 转换为 DataFrame 以方便利用 pandas 的解析能力写入单行
                df_row = pd.DataFrame([current_row])
                df_row.to_csv(f_out, sep='\t', index=False, header=write_header, encoding='utf-8')
                f_out.flush() 
                os.fsync(f_out.fileno())
                # 写入一次表头后，后续行不再写入
                write_header = False 
                processed_files.add(file_name)
                processed_count += 1
            except Exception as e:
                print(f"❌ [MAMI] 处理异常 ({file_name}): {e}")
                failed_count += 1
                continue

    print(f"✨ [MAMI] 处理结束！新增: {processed_count} 条, 跳过: {skipped_count} 条, 失败: {failed_count} 条")
    

elif DATASET_NAME == 'HARM':
    import json
    import os
    from tqdm import tqdm
    # 路径定义
    output_path = data_src.replace('.jsonl', '_with_description.jsonl')
    temp_path = output_path + '.tmp'
    LENGTH_THRESHOLD = 110  # 统一长度阈值
    valid_imgs = set()
    kept_count = 0
    removed_count = 0
    # --- 步骤 1: 清理并加载已有的有效数据 ---
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f_in, \
                 open(temp_path, 'w', encoding='utf-8') as f_out:
                for line in tqdm(f_in, desc="[HARM] 清理无效描述"):
                    try:
                        sample = json.loads(line.strip())
                        description = sample.get('description', '')
                        # 只有长度达标的才保留
                        if len(description) >= LENGTH_THRESHOLD:
                            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')
                            valid_imgs.add(sample['image']) # 注意 HARM 使用 'image' 字段
                            kept_count += 1
                        else:
                            removed_count += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
            # 用清理后的临时文件替换原输出文件
            os.replace(temp_path, output_path)
            print(f"✅ [HARM] 历史数据清理完成：保留 {kept_count} 条，删除 {removed_count} 条无效数据")
        except Exception as e:
            print(f"⚠️ [HARM] 清理过程出错: {e}")
    else:
        print(f"ℹ️ [HARM] {output_path} 不存在，将开始全新处理")
    # --- 步骤 2: 增量处理新数据 ---
    # 使用 'a' 模式追加写入
    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'a', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        skipped_count = 0
        processed_count = 0
        for idx, line in tqdm(enumerate(lines), total=len(lines), desc="[HARM] 增量生成描述"):
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            img_id = sample['image'] # HARM 字段
            # 检查是否已处理过且有效
            if img_id in valid_imgs:
                skipped_count += 1
                continue
            # 调用 LLM 获取描述
            meme_text = sample['text']
            meme_src_path = f"{img_src}/{img_id}"
            failed_count = 0
            try:
                description = get_description_of_meme(meme_text, meme_src_path)
                # 长度校验
                if len(description) < LENGTH_THRESHOLD:
                    # 如果模型返回了拒答（如 "I'm sorry..."），长度通常很短，会被这里拦截
                    print(f"⚠️ [HARM] 描述过短或无效，跳过 (行 {idx + 1})")
                    failed_count += 1
                    continue
                sample['description'] = description
                # 实时写入，防止崩溃导致数据丢失
                f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')
                valid_imgs.add(img_id) # 防止原数据集中有重复的 image ID
                processed_count += 1
            except Exception as e:
                print(f"❌ [HARM] 调用异常 (行 {idx + 1}): {e}")
                failed_count += 1
                continue

    print(f"✨ [HARM] 处理结束！新增: {processed_count} 条, 跳过: {skipped_count} 条, 失败/拦截: {failed_count} 条")