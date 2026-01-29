import json

def load_jsonl(filepath):
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                data[obj['id']] = obj
    return data

def main():
    # 加载两个文件
    memes = load_jsonl('data/HARM/test_with_description_copy.jsonl')
    searches = load_jsonl('data/HARM/test_with_search_results.jsonl')

    # 合并：将 search_results 添加到 memes 中
    merged = []
    for id_key in memes:
        if id_key in searches:
            # 合并字段
            merged_obj = memes[id_key]
            merged_obj['search_results'] = searches[id_key]['search_results']
            merged.append(merged_obj)
        else:
            # 如果没有对应的 search_results，可选择跳过或保留原样
            # 这里选择保留原样（不加 search_results）
            merged.append(memes[id_key])

    # 写入输出文件（保持原始顺序：按 memes 的遍历顺序）
    with open('data/HARM/merged.jsonl', 'w', encoding='utf-8') as f:
        for obj in merged:
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"合并完成，共处理 {len(merged)} 条记录。")

if __name__ == '__main__':
    main()