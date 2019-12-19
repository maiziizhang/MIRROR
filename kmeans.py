from sklearn.cluster import KMeans
import numpy as np


def initcluster(fileName, dataMat):
    f1 = open(fileName, "r")
    wordlist = []
    for line in f1.readlines():
        if line.count('\n') == len(line):
            continue
        lineTemp = line.strip().replace('\n', '').split(':')
        lineTemp[2] = int(lineTemp[2])
        wordlist.append(lineTemp)
    f1.close()
    sortedWordlist = sorted(wordlist, key=lambda x: x[2], reverse=True)
    list1 = []
    initcluster = []
    for i in range(20):
        list1.append(sortedWordlist[0])
    for i in list1:
        initcluster.append(dataMat[int(i[0]) - 1])

    return np.array(initcluster)

def loadData(data0, data1):
    dataMat = []
    fr0 = open(data0, 'r')
    for line in fr0.readlines():
        curLine = line.strip().split(',')
        curLine.pop()
        fltLine = list(map(float, curLine))
        dataMat.append(fltLine)
    fr0.close()
    fr1 = open(data1, 'r')
    for line in fr1.readlines():
        curLine = line.strip().split(',')
        curLine.pop()
        fltLine = list(map(float, curLine))
        dataMat.append(fltLine)
    fr1.close()
    return np.array(dataMat)


def write(outputName, lable_pred, dataMat, cluster_num, file_nounlist0, file_nounlist1, centroids):
    fnoun0 = open(file_nounlist0,'r')
    fnoun1 = open(file_nounlist1,'r')
    nounlist=[]
    for line in fnoun0:
        nounlist.append(line.strip('\n'))
    for line in fnoun1:
        nounlist.append(line.strip('\n'))
    asp_keylist={}
    key_to_asp={}
    for i in range(cluster_num):
        asp_keylist[i]=[]
    for i in range(len(dataMat)):
        asp_keylist[lable_pred[i]].append(nounlist[i])
        key_to_asp[nounlist[i]]=lable_pred[i]
    center_word_list=[]
    for i in range(cluster_num):
        dist = 10000000
        lable = 0
        for j in range(len(lable_pred)):
            if int(lable_pred[j]) == i:
                Dtemp = np.sqrt(np.sum(np.square(dataMat[j]-centroids[i])))
                if dist > Dtemp:
                    dist = Dtemp
                    lable = j
        center_word_list.append(lable)
    file_towritekeycluster=open(outputName,'w')
    for i in range(cluster_num):
        file_towritekeycluster.writelines(str(nounlist[center_word_list[i]])+': ')
        for key in asp_keylist[i]:
            file_towritekeycluster.write(key)
            file_towritekeycluster.write(',')
        file_towritekeycluster.write('\n')
    file_towritekeycluster.flush()
    file_towritekeycluster.close()
    return asp_keylist,key_to_asp,center_word_list

def kmeans(dataMat,n_clusters):
    # a=initcluster(fileName, dataMat)
    # estimator = KMeans(n_clusters=n_clusters,init=a).fit(dataMat) |a|=n_cluster
    estimator = KMeans(n_clusters=n_clusters,max_iter=1000000000).fit(dataMat)
    lable_pred = estimator.labels_
    centroids = estimator.cluster_centers_
    # print(lable_pred)
    # print(centroids)
    return lable_pred,centroids

# if __name__ == "__main__":
#     fileName='word2vec.txt'
#     wordList='NounMap.txt'
#     outputName='kmeans.txt'
#     n_clusters=100
#     dataMat = loadData(fileName)
#     wordLength = len(dataMat)
#     lable_pred = kmeans(dataMat,n_clusters)
#     write(wordList,outputName,lable_pred,wordLength,n_clusters)
