from kmeans import loadData
from kmeans import kmeans
from kmeans import write


'''
输入：file_of_noun0, file_of_noun1, file_to_writevec, file_to_write_keycluster, cluster_num
功能：clusternoun将名词聚类
输出：asp_keylist,key_to_asp
'''


def clusternoun(file_vec0, file_vec1, file_to_keycluster, cluster_pro, file_nounlist0, file_nounlist1):
    # wordlist=read_file_townounlist
    # top_count_word=gettopwords np.array
    dataMat = loadData(file_vec0, file_vec1)
    wordLength = len(dataMat)
    interaput = True
    if wordLength == 0:
        interaput = False
        asp_keylist, key_to_asp, cluster_num = 1, 1, 1
    # kmeans( , ,top_count_word)
    if interaput:
        cluster_num = int(wordLength * cluster_pro)
        if cluster_num < 1:
            cluster_num = 1
        lable_pred, centroids = kmeans(dataMat, cluster_num)
        asp_keylist, key_to_asp, center_word_list = write(file_to_keycluster, lable_pred, dataMat,
                                                          cluster_num, file_nounlist0, file_nounlist1, centroids)
    return asp_keylist, key_to_asp, center_word_list


'''
输入：file_of_noun,asp_keylist,adj_file_homepath
功能：getasp_adjlist
输出：asp_adjlist
'''


def getkey_adjlist(least_occur_time, file_of_noun, adj_file_homepath):
    word_adjlist = {}
    f_of_noun = open(file_of_noun, 'r')
    adjslist = []
    nounlist = []
    adj_path = adj_file_homepath + '/adj.txt'
    count = -1
    f = open(adj_path, 'r')

    for line in f.readlines():
        if line.count('\n') == len(line):
            continue
        line = line.strip('[')
        line = line.strip('\r\n')
        line = line.strip(']')
        adj_list_r = line.split(',')
        adj_list = []
        for adj in adj_list_r:
            adjn = adj.replace(" ", "")
            adj_list.append(adjn)
        adj_list = list(set(adj_list))
        adjslist.append(adj_list)

    for line in f_of_noun:
        if line.count('\n') == len(line):
            continue
            line = line.strip('\r\n')
        count += 1
        line = line.split('@')
        times = line[1]
        if int(times) > least_occur_time:
            word = line[0].split('!!')[1]
            nounlist.append(word)
            word_adjlist[word] = adjslist[count]
    return nounlist, word_adjlist


'''
输入：asp_keylist,file_of_noun0,adj_file_homepath0,file_of_noun1,adj_file_homepath1
功能：getasp_adjset
输出：asp_adjsetlist
'''


def getasp_word_adjset(asp_keylist, file_of_noun0, adj_file_homepath0, least_occur_time0,
                       file_of_noun1, adj_file_homepath1, least_occur_time1):
    asp_key_adjset = {}
    nounlist_0, word_adjlist0 = getkey_adjlist(least_occur_time0, file_of_noun0, adj_file_homepath0)
    nounlist_1, word_adjlist1 = getkey_adjlist(least_occur_time1, file_of_noun1, adj_file_homepath1)
    for asp in asp_keylist.keys():
        asp_key_adjset[asp] = {}
        for key in asp_keylist[asp]:
            adjlist0 = []
            adjlist1 = []
            flag_key = False
            if key in word_adjlist0.keys():
                adjlist0 = word_adjlist0[key]
                flag_key = True
            if key in word_adjlist1.keys():
                adjlist1 = word_adjlist1[key]
                flag_key = True
            if flag_key:
                adjlist = list.copy(adjlist0)
                adjlist.extend(list.copy(adjlist1))
                adjlist = list(set(adjlist))
                asp_key_adjset[asp][key] = adjlist
    interaput = len(nounlist_0) > 0 and len(nounlist_1) > 0
    return nounlist_0, nounlist_1, asp_key_adjset, interaput


def getasp_opinion_tonum(asp_key_adjset):
    phrasenum_to_asp = {}
    word_adj_topnum = {}
    pnum_to_meaning = {}
    asp_ocount = []
    count = -1
    for asp in asp_key_adjset.keys():
        for word in asp_key_adjset[asp].keys():
            word_adj_topnum[word] = {}
            for adj in asp_key_adjset[asp][word]:
                count += 1
                opinion = '%s %s' % (word, adj)
                pnum_to_meaning[count] = opinion
                word_adj_topnum[word][adj] = count
                phrasenum_to_asp[count] = asp
        asp_ocount.append(count)
    return word_adj_topnum, pnum_to_meaning, asp_ocount, phrasenum_to_asp