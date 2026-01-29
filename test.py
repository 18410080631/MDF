import json

def load_jsonl(filepath):
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                data[obj['id']] = obj
    return data

if __name__ == '__main__':
    # 加载两个文件
    id = 8291
    memes = load_jsonl('data/FHM/data/dev_with_description copy.jsonl')
    title = memes[id]['search_results']['results'][0]['title']
    content = memes[id]['search_results']['results'][0]['content']
    print("Title:", title)
    print("Content:", content)