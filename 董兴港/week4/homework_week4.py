#week3作业

#词典；每个词后方存储的是其词频，词频仅为示例，不会用到，也可自行修改
Dict = {"经常":0.1,
        "经":0.05,
        "有":0.1,
        "常":0.001,
        "有意见":0.1,
        "歧":0.001,
        "意见":0.2,
        "分歧":0.2,
        "见":0.05,
        "意":0.05,
        "见分歧":0.05,
        "分":0.1}

#待切分文本
sentence = "经常有意见分歧"

#实现全切分函数，输出根据字典能够切分出的所有的切分方式
def all_cut(sentence, Dict):
    n = len(sentence)
    # dp[i]存储从开始到第i个字符的所有可能切分方式
    dp = [[] for _ in range(n + 1)]
    dp[0] = [[]]  # 空字符串的切分方式为空列表
    
    # 遍历每个位置作为结束位置
    for i in range(1, n + 1):
        current_cuts = set()
        
        # 遍历所有可能的起始位置
        for j in range(i):
            word = sentence[j:i]
            # 如果当前子串在字典中
            if word in Dict:
                if j == 0:
                    current_cuts.add(tuple([word]))
                # 将当前子串添加到j位置的所有切分方式中
                for prev_cut in dp[j]:
                    current_cuts.add(tuple(prev_cut + [word]))
        
        # 将set中的切分方式转回list添加到dp数组中
        dp[i] = [list(cut) for cut in current_cuts]
    
    return dp[n]

#目标输出;顺序不重要
target = [
    ['经常', '有意见', '分歧'],
    ['经常', '有意见', '分', '歧'],
    ['经常', '有', '意见', '分歧'],
    ['经常', '有', '意见', '分', '歧'],
    ['经常', '有', '意', '见分歧'],
    ['经常', '有', '意', '见', '分歧'],
    ['经常', '有', '意', '见', '分', '歧'],
    ['经', '常', '有意见', '分歧'],
    ['经', '常', '有意见', '分', '歧'],
    ['经', '常', '有', '意见', '分歧'],
    ['经', '常', '有', '意见', '分', '歧'],
    ['经', '常', '有', '意', '见分歧'],
    ['经', '常', '有', '意', '见', '分歧'],
    ['经', '常', '有', '意', '见', '分', '歧']
]

print(all_cut(sentence, Dict))
print(len(target))
