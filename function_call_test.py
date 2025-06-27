from agents.deepseek_agent import DeepseekAgent

def main():
    agent = DeepseekAgent(
        api_key="",
        model_type="deepseek-chat"
    )
    
    user_query = "我有12、15、9这三个数，这三个数经过魔法算子计算后的结果是什么？"
    print(f"用户输入：{user_query}")
    
    response = agent.give_final_answer(user_query)
    print(response)

if __name__ == "__main__":
    main()
