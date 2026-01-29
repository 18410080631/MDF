from debate_graph import DebateGraph
from pathlib import Path
import time
from config import TEMPERATURE,MODEL_NAME

def main():
    """主入口函数"""
    # 配置辩论参数
    meme_text = "its their character not their color that matters"
    meme_src = "C:/Users/77366/Desktop/模因检测/few-shot模因检测/基于多智能体对抗辩论的零样本有害模因检测/code/Debate-to-Detect/img/42953.png"
    news_path = Path("sample_news.txt")
    
    print("🤖 初始化辩论系统...")
    print(f"📊 模因文本: {meme_text}")
    print(f"🖼️  模因图片: {meme_src}")

    # 创建辩论图
    debate_graph = DebateGraph(
        model_name=MODEL_NAME,
        temperature=TEMPERATURE
    )
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行辩论
    try:
        final_state = debate_graph.run_debate(
            meme_text=meme_text,
            meme_src=meme_src,
            news_path=news_path
        )
        
        # 总耗时
        total_time = time.time() - start_time
        print(f"\n⏱️  总执行时间: {total_time:.2f} 秒")
        
        # 显示关键结果
        print("\n" + "="*60)
        print("🎯 关键结果摘要")
        print("="*60)
        print(f"✅ 领域检测: {final_state['domain']}")
        print(f"✅ 证据收集: {'已启用' if final_state['evidence_enabled'] else '已禁用'}")
        print(f"✅ 总发言数: {len(final_state['transcript'])}")
        print(f"✅ 最终判决: {final_state['verdict']}")
        print(f"✅ 保存路径: Results/ 目录")
        
    except Exception as e:
        print(f"\n❌ 执行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()