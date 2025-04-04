import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""
基于pytorch的网络编写
实现一个网络完成一个简单nlp任务
判断文本中某个特定字符出现的位置
"""

class TorchModel(nn.Module):
    def __init__(self, vector_dim, sentence_length, vocab,hidden_dim=128):
        super(TorchModel, self).__init__()
        self.embedding = nn.Embedding(len(vocab), vector_dim, padding_idx=0)  #embedding层
        self.rnn = nn.RNN(vector_dim,hidden_dim,batch_first=True) #RNN层
        self.classify = nn.Linear(hidden_dim, len(vocab))     #线性层
        self.loss = nn.CrossEntropyLoss()  #交叉熵损失

    def forward(self, x, y=None):
        x = self.embedding(x)                      # (batch_size, sen_len) -> (batch_size, sen_len, vector_dim)
        rnnout,_ = self.rnn(x)                           # (batch_size, sen_len, hidden_dim)
        x = rnnout[:, -1, :]
        y_pred = self.classify(x)       # (batch_size, sen_len)
        if y is not None:
            return self.loss(y_pred, y)
        else:
            return y_pred                          # 输出预测结果

#字符集随便挑了一些字，实际上还可以扩充
#为每个字生成一个标号
#{"a":1, "b":2, "c":3...}
#abc -> [1,2,3]
def build_vocab():
    chars = "你我他defghijklmnopqrstuvwxyz"  #字符集
    vocab = {"pad":0}
    for index, char in enumerate(chars):
        vocab[char] = index+1   #每个字对应一个序号
    vocab['unk'] = len(vocab) #26
    return vocab

#随机生成一个样本
#从所有字中选取sentence_length个字
def build_sample(vocab, sentence_length, target_chars):
    # 随机选择剩余的字符填充到样本中
    x = [random.choice(list(vocab.keys())) for _ in range(sentence_length - len(target_chars))]

    # 将目标字符集插入到随机位置
    target_chars = list(target_chars)  # 转换为列表以便使用
    positions = random.sample(range(sentence_length), len(target_chars))  # 随机选择位置

    for i, target_char in zip(positions, target_chars):
        x.insert(i, target_char)  # 在随机位置插入目标字符

    # 将字符转换为索引
    x = [vocab.get(char, vocab['unk']) for char in x]
    for idx, char in enumerate(x):
        if char in target_chars:
            return x, idx+1  # 返回字符串和目标字符的出现位置
    return x, 0  # 如果目标字符不在字符串中，返回 None

#建立数据集
#输入需要的样本数量。需要多少生成多少
def build_dataset(sample_length, vocab, sentence_length, target_chars):
    dataset_x = []
    dataset_y = []
    for i in range(sample_length):
        x, y = build_sample(vocab, sentence_length, target_chars)
        dataset_x.append(x)
        dataset_y.append(y)
    return torch.LongTensor(dataset_x), torch.LongTensor(dataset_y)

#建立模型
def build_model(vocab, char_dim, sentence_length):
    model = TorchModel(char_dim, sentence_length, vocab)
    return model

#测试代码
#用来测试每轮模型的准确率
def evaluate(model, vocab, sample_length,sentence_length,target_chars):
    model.eval()
    x, y = build_dataset(sample_length, vocab, sentence_length, target_chars)   #建立200个用于测试的样本
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)      #模型预测
        for y_p, y_t in zip(y_pred, y):  #与真实标签进行对比
            pred_idx = torch.argmax(y_p, dim=-1).item()  # 获取预测的类别
            if pred_idx == int(y_t.item()):  # 判断是否正确
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f"%(correct, correct/(correct+wrong)))
    return correct/(correct+wrong)


def main():
    #配置参数
    epoch_num = 10        #训练轮数
    batch_size = 20       #每次训练样本个数
    train_sample = 500    #每轮训练总共训练的样本总数
    char_dim = 20         #每个字的维度
    sentence_length = 6   #样本文本长度
    learning_rate = 0.005 #学习率
    target_chars = set("你")  # 目标字符集
    # 建立字表
    vocab = build_vocab()
    # 建立模型
    model = build_model(vocab, char_dim, sentence_length)
    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch in range(int(train_sample / batch_size)):
            x, y = build_dataset(batch_size, vocab, sentence_length,target_chars) #构造一组训练样本
            optim.zero_grad()    #梯度归零
            loss = model(x, y)   #计算loss
            loss.backward()      #计算梯度
            optim.step()         #更新权重
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model, vocab, train_sample, sentence_length, target_chars)
        log.append([acc, np.mean(watch_loss)])
    #画图
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  #画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  #画loss曲线
    plt.legend()
    plt.show()
    #保存模型
    torch.save(model.state_dict(), "model.pth")
    # 保存词表
    writer = open("vocab.json", "w", encoding="utf8")
    writer.write(json.dumps(vocab, ensure_ascii=False, indent=2))
    writer.close()
    return

#使用训练好的模型做预测
def predict(model_path, vocab_path, input_strings):
    char_dim = 20  # 每个字的维度
    sentence_length = 6  # 样本文本长度
    vocab = json.load(open(vocab_path, "r", encoding="utf8")) #加载字符表
    model = build_model(vocab, char_dim, sentence_length)     #建立模型
    model.load_state_dict(torch.load(model_path))             #加载训练好的权重
    x = []
    for input_string in input_strings:
        x.append([vocab[char] for char in input_string])  #将输入序列化
    model.eval()   #测试模式
    with torch.no_grad():  #不计算梯度
        result = model.forward(torch.LongTensor(x))  #模型预测
    for i, input_string in enumerate(input_strings):
        pred_idx = torch.argmax(result[i]).item()
        print(f"输入：{input_string}, 预测位置：{pred_idx}")

if __name__ == "__main__":
    main()
    test_strings = ["fnv他ee", "wz你dfg", "你qwdeg", "n我kwww"]
    predict("model.pth", "vocab.json", test_strings)
