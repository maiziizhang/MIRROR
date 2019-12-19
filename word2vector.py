from nltk.corpus import wordnet as wn
import nltk


def phr_sim(word1, word2):
    w_sim = 0.0
    for synset1 in wn.synsets(word1):
        for synset2 in wn.synsets(word2):
            s_sim = synset1.path_similarity(synset2)
            if not s_sim is None:
                if s_sim > w_sim:
                    w_sim = s_sim
    return w_sim

'''
def loadData(fileName0,fileName1):
    f0 = open(fileName0,"r")
    f1=open(fileName1,"r")
    wordlist=[]
    for line in f0.readlines():
        if line.count('\n')==len(line):
            continue
        wordlist.append(line.strip().replace('\n','').split(':')[1])
    f0.close()

    for line in f1.readlines():
        if line.count('\n')==len(line):
            continue
        wordlist.append(line.strip().replace('\n','').split(':')[1])

    f1.close()
    
    
    return wordlist 
'''


def loadData(fileName0, fileName1,min_oc,f0_len,f1_len):
    f0 = open(fileName0, "r",encoding='utf-8')
    f1 = open(fileName1, "r",encoding='utf-8')
    ex0=0
    ex1=0
    wordlist0 = {}
    wordlist1 = {}
    wordlist=[]
    for line in f0.readlines():
        if line.count('\n') == len(line):
            continue
        line=line.strip('\r\n').split('!!')
        l0=line[1]
        l0=l0.split('@')
        wordlist0[l0[0]]=int(l0[1])
    f0.close()

    for line in f1.readlines():
        if line.count('\n') == len(line):
            continue
        line = line.strip('\r\n').split('!!')
        l1=line[1]
        l1=l1.split('@')
        wordlist1[l1[0]] = int(l1[1])
    f1.close()
    k0=f0_len*min_oc
    k1=f1_len*min_oc
    print("k0: %f\n" % k0)
    print("k1: %f\n" % k1)

    wordlist0_sort = sorted(wordlist0.items(), key=lambda x: x[1], reverse=True)
    wordlist1_sort = sorted(wordlist1.items(), key=lambda x: x[1], reverse=True)

    for t in wordlist0_sort:
        if t[1]>=k0:
            wordlist.append(t[0])
            ex0=ex0+1
        else:
            break
    for t in wordlist1_sort:
        if t[1]>=k1:
            wordlist.append(t[0])
            ex1=ex1+1
        else:
            break
    print(ex0)
    print(ex1)
    print("keyword num:%d"%len(set(wordlist)))

    return list(set(wordlist)),k0,k1


def word2vec(wordlist):
    length = len(wordlist)
    fvectors = [[0.0 for col in range(length)] for row in range(length)]
    for i in range(length):
        fvectors[i][i] = 1.0
        for j in range(i+1, length):
            print("i: %d j:%d"%(i,j))
            psim = phr_sim(wordlist[i],wordlist[j])
            fvectors[i][j] = psim
            fvectors[j][i] = psim
    return fvectors


def write(fvectors,file_to_writevec,file_townounlist,wordlist):
    file1 = open(file_to_writevec,"w")
    for i in range(len(fvectors)):
        for j in range(len(fvectors[i])):
            file1.writelines(str(fvectors[i][j]))
            if j != len(fvectors[i])-1:
                file1.writelines(",")
        file1.write("\n")
    file1.flush()
    file1.close()
    fnounlist=open(file_townounlist,'w')
    for word in wordlist:
        fnounlist.write(word)
        fnounlist.write('\n')
    fnounlist.flush()
    fnounlist.close()

def word2vec_interface(file_of_noun0,file_of_noun1,file_to_writevec,min_oc,file_townounlist,f0_len,f1_len):
    nltk.download('wordnet')

    wordlist,k0,k1 = loadData(file_of_noun0,file_of_noun1,min_oc,f0_len,f1_len)
    fvectors = word2vec(wordlist)
    write(fvectors,file_to_writevec,file_townounlist,wordlist)
