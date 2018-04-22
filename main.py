import pandas as pd
import numpy as np
import time

def loadDataSet():
    return [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]

# 生成初始候选频繁项集C1
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if [item] not in C1:
                C1.append([item])
    C1.sort()
    return list(map(frozenset, C1))

def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                ssCnt[can] = ssCnt.get(can, 0) + 1
    numItems = len(D)
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.append(key)
            supportData[key] = support
    return retList, supportData

def has_infrequent_subset(c, Lk):
    for item in c:
        c_copy = c.copy()
        c_copy.remove(item)
        if c_copy not in Lk:
            return True
    return False

def aprioriGen(Lk, k):
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk):
            L1 = list(Lk[i]) ; L2 = list(Lk[j])
            L1.sort() ; L2.sort()
            if L1[:k-2] == L2[:k-2]:
                c = Lk[i] | Lk[j]
                if has_infrequent_subset(set(c), Lk): continue
                else: retList.append(c)
    return retList

def apriori(dataSet, minSupport=0.5):
    C1 = createC1(dataSet)
    D = list(map(set, dataSet))
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while len(L[k-2]) > 0:
        Ck = aprioriGen(L[k-2], k)
        Lk, supK = scanD(D, Ck, minSupport)
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData

def generateRules(L, supportData, minConf=0.7):
    bigRuleList = []
    for i in range(1, len(L)):
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if i > 1:
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList

def calcConf(freqSet, H, supportData, br1, minConf=0.7):
    prunedH = []
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet-conseq]
        lift = conf / suppData[conseq]
        if conf >= minConf:
            print(freqSet-conseq, '-->', conseq, 'conf:', conf, 'lift:', lift)
            br1.append((freqSet-conseq, conseq, conf, lift))
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, br1, minConf=0.7):
    Hmp1 = calcConf(freqSet, H, supportData, br1, minConf)
    if Hmp1 and len(freqSet) > (len(Hmp1[0]) + 1):
        Hmp1 = aprioriGen(Hmp1, len(Hmp1[0]) + 1)
        rulesFromConseq(freqSet, Hmp1, supportData, br1, minConf)

def add_prefix(row):
    for index in row.index:
        row[index] = index + '_' + str(row[index])
    return row

df = pd.read_csv('NFL Play by Play 2009-2017 (v4).csv', dtype=str)
for col in df:
    df_counts = df[col].value_counts()
    num = df_counts.max()
    name = df_counts.idxmax()
    if pd.isnull(name) or name == 'None' or num < len(df)/2  or num > len(df)*0.95:
        df.drop(col, axis=1, inplace=True)
df.fillna(method='ffill')
df = df.apply(add_prefix,axis=1)
L, suppData = apriori(np.array(df).tolist() ,minSupport=0.5)
rules = generateRules(L, suppData, minConf=0.7)

with open('ruls.txt', 'w') as fw:
    for rule in rules:
        fw.write('{} --> {} conf: {}   lift: {}\n'.format(rule[0], rule[1], rule[2], rule[3]))
