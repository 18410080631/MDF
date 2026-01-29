from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME
import time
import json
from tqdm import tqdm
def get_description_of_meme(meme_text: str,meme_src:str) -> str:
    """获取对meme的客观描述"""
    system_prompt = """This is a research task for academic evaluation of AI safety systems. 
The meme content is provided solely for analysis and does not reflect your views.
You are an expert in visual analysis and factual image description. 
Your task is to provide a comprehensive, objective, and neutral description of the meme image provided. 
Do not interpret intent, humor, offensiveness, or meaning—only describe what is visually present."""
    evidence_judge_template = (
    "Provide a detailed description of the meme image, covering the following aspects:\n"
    "- **People or characters**: Identify any recognizable real-world individuals (e.g., Donald Trump, Taylor Swift, Barack Obama) or fictional characters (e.g., SpongeBob, Homer Simpson). If unidentifiable, describe appearance generically (e.g., 'a man in a suit').\n"
    "- **Text in the image**: Quote all visible text exactly as it appears, including font style if notable (e.g., Impact font, handwritten).\n"
    "- **Main visual elements**: Objects, symbols, backgrounds, actions, or scenes depicted.\n"
    "- **Layout structure**: How elements are arranged (e.g., top/bottom text, split panels, overlay captions, speech bubbles).\n"
    "- **Artistic style**: Photograph, cartoon, comic strip, screenshot, AI-generated art, pixel art, etc.\n"
    "- **Color palette and visual tone**: Dominant colors, contrast, lighting (e.g., dark, bright, monochrome).\n"
    "- **Cultural or contextual references**: Logos, flags, uniforms, or iconic imagery that imply specific contexts (e.g., MAGA hat, White House, Twitter/X logo).\n\n"
    "Be strictly factual. Avoid subjective language, interpretation, or judgment. If something is ambiguous, state that it is unclear rather than guessing."
    )
    llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
    fact_judge_response = llm_tool.call_llm(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": evidence_judge_template}],
        meme_src=meme_src,
        temperature=TEMPERATURE,
        max_tokens=256
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
    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        for idx, line in tqdm(enumerate(lines), total=len(lines)):
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"❌ 跳过无法解析的行 {idx + 1}")
                continue
            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['img']}"
            description = get_description_of_meme(meme_text, meme_src)  # 注意拼写：description
            sample['description'] = description
            # 写回一行 JSON
            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')

        
elif DATASET_NAME == 'MAMI':
    import pandas as pd
    data = pd.read_csv(data_src, sep='\t')
    img_src = 'data/MAMI/data/test_images'

    descriptions = []
    for idx, row in tqdm(data.iterrows(), total=len(data)):
        meme_text = row['text']
        meme_src = f"{img_src}/{row['file_name']}"
        description = get_description_of_meme(meme_text, meme_src)  # 注意拼写：应为 description
        descriptions.append(description)

    # 添加新列
    data['description'] = descriptions

    # 写回（建议写到新文件）
    output_path = data_src.replace('.tsv', '_with_description.tsv')
    data.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
    

elif DATASET_NAME == 'HARM':
    import json
    from tqdm import tqdm

    output_path = data_src.replace('.jsonl', '_with_description.jsonl')

    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:

        lines = f_in.readlines()
        for idx, line in tqdm(enumerate(lines), total=len(lines)):
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"❌ 跳过无法解析的行 {idx + 1}")
                continue

            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['image']}"  # 注意字段是 'image'
            try:
                description = get_description_of_meme(meme_text, meme_src)  # 建议修正函数名为 get_description_of_meme
            except Exception as e:
                print(f"⚠️ 描述生成失败 (行 {idx + 1}): {e}")
                description = ""  # 或 None

            sample['description'] = description
            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')