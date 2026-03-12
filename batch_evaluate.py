import requests
import pandas as pd
import time
import os

# 配置区
BASE_URL = "https://intelliknow-kms-api-9e88.onrender.com"
API_URL = f"{BASE_URL}/api/query"
INPUT_CSV = "sample_docs/testSet.xlsx"
OUTPUT_CSV = "rag_evaluation_results.csv"

def run_evaluation():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ 找不到测试集文件: {INPUT_CSV}")
        return

    # 1. 读取测试集
    print(f"📂 正在加载测试集: {INPUT_CSV}...")
    df_test = pd.read_excel(INPUT_CSV)
    total_queries = len(df_test)
    print(f"🚀 开始批量测试，共 {total_queries} 个问题...\n")

    results = []

    # 2. 遍历测试集
    for index, row in df_test.iterrows():
        # 提取原表字段
        query = str(row.get("query", "")).strip()
        expected_intent = str(row.get("intent", "")).strip()
        expected_answer = str(row.get("answer", "")).strip()
        source_text = str(row.get("sourcetext", "")).strip()
        
        print(f"[{index+1}/{total_queries}] 正在测试: {query[:40]}...")
        
        payload = {
            "query": query,
            "source": "batch_evaluation",
            "user_id": "evaluator"
        }
        
        # 准备记录的基础数据（保留原表所有重要字段）
        record = {
            "Query": query,
            "Expected Intent": expected_intent,
            "Expected Answer": expected_answer,
            "Source Text": source_text
        }
        
        try:
            # 请求后端 API
            response = requests.post(API_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            predicted_intent = str(data.get("intent", "")).strip()
            
            # 自动比对意图是否一致 (忽略大小写)
            intent_match = (predicted_intent.lower() == expected_intent.lower())
            
            # 记录大模型返回的结果
            record.update({
                "Predicted Intent": predicted_intent,
                "Intent Match": "✅ Yes" if intent_match else "❌ No",
                "Confidence": round(data.get("confidence", 0), 2),
                "Latency(ms)": data.get("response_time_ms"),
                "Actual Response": data.get("response", ""),
                "API Status": "Success"
            })
            
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            record.update({
                "Predicted Intent": "N/A",
                "Intent Match": "⚠️ Error",
                "Confidence": 0,
                "Latency(ms)": 0,
                "Actual Response": f"Error: {str(e)}",
                "API Status": "Failed"
            })
            
        results.append(record)
        
        # 停顿 1.5 秒，防止打满 Render 单核 CPU 或触发大模型 API 并发限制
        time.sleep(1.5)

    # 3. 保存结果到新的 CSV
    df_results = pd.DataFrame(results)
    # 使用 utf-8-sig 编码，确保 Excel 打开不乱码
    df_results.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    print(f"\n✅ 批量测试完成！结果已保存至 {OUTPUT_CSV}")

    # 4. 打印自动化评估报告
    success_df = df_results[df_results['API Status'] == 'Success']
    if not success_df.empty:
        # 计算意图准确率
        correct_intents = len(success_df[success_df['Intent Match'] == '✅ Yes'])
        intent_accuracy = (correct_intents / len(success_df)) * 100
        
        # 计算平均延迟
        avg_latency = success_df['Latency(ms)'].mean()
        
        print("\n" + "="*40)
        print("📊 RAG 系统自动化评估报告")
        print("="*40)
        print(f"总测试用例: {total_queries}")
        print(f"API 成功率: {(len(success_df) / total_queries) * 100:.1f}%")
        print(f"意图分类准确率 (Intent Accuracy): {intent_accuracy:.1f}% ({correct_intents}/{len(success_df)})")
        print(f"平均响应延迟: {avg_latency:.0f}ms")
        print("="*40)
        print("提示: 问答准确率 (Answer Accuracy) 可在生成的 CSV 中，通过对比 [Expected Answer] 和 [Actual Response] 进行人工或大模型打分评估。")

if __name__ == "__main__":
    run_evaluation()