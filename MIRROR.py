from Data_Pro_new import getasp_word_adjset, getasp_opinion_tonum
from Data_Pro_new import clusternoun
from Phrase import Phrase
from Aspect import Aspect
import time
import os

global_maxscoresum = 0
global_setsum = 0
global_property = 0
global_experiment_count = 0
global_time = 0

global_maxlist_list = []
global_maxscore = 0


def readdata_new(file_raw, word_adj_topnum, phrasenum_to_asp):
    fraw = open(file_raw, 'r')
    phrase_review_raw = {}
    phrase_review = {}
    asp_review_raw = {}
    asp_review = {}
    asp_to_phrasenumlist = {}
    review_count = -1
    for line in fraw:
        line = line.strip('\r\n')
        if line.count('\n') == len(line):
            continue
        review_count += 1
        opinions = line.strip('@@').split('@@')
        for opinion in opinions:
            opinion = opinion.split('##')
            word = opinion[0]
            adj = opinion[1]
            if word in word_adj_topnum.keys() and \
                    adj in word_adj_topnum[word].keys():
                pnum = word_adj_topnum[word][adj]
                if pnum not in phrase_review_raw:
                    phrase_review_raw[pnum] = []
                phrase_review_raw[pnum].append(review_count)
                asp = phrasenum_to_asp[pnum]
                if asp not in asp_review_raw.keys():
                    asp_review_raw[asp] = []
                asp_review_raw[asp].append(review_count)
                if asp not in asp_to_phrasenumlist.keys():
                    asp_to_phrasenumlist[asp] = []
                asp_to_phrasenumlist[asp].append(pnum)
    for asp in asp_review_raw.keys():
        review_items = list(set(asp_review_raw[asp]))
        asp_review[asp] = list.copy(review_items)

    for pnum in phrase_review_raw.keys():
        review_items = list(set(phrase_review_raw[pnum]))
        phrase_review[pnum] = list.copy(review_items)

    return phrase_review, asp_review, asp_to_phrasenumlist

'''
FUNC:getshared_pnum_eachasp 得到两个评论集每个asp共享phrase
INPUT: asp_phrasenum0,asp_phrasenum1
OUTPUT:
shared_asp_phrasenum_list
'''


def getshared_pnum_eachasp(asp_to_phrasenumlist0, asp_to_phrasenumlist1):
    shared_asp_phrasenum_list = {}
    total_asp_phrasenum_list = {}
    shared_aspn_list = list(set(asp_to_phrasenumlist1.keys()).intersection
                            (set(asp_to_phrasenumlist0.keys())))
    for asp in shared_aspn_list:
        shared_asp_phrasenum_list[asp] = list(set(asp_to_phrasenumlist0[asp]).intersection
                                              (set(asp_to_phrasenumlist1[asp])))
    for asp in shared_aspn_list:
        total_asp_phrasenum_list[asp] = list(set(asp_to_phrasenumlist0[asp]).union(set(asp_to_phrasenumlist1[asp])))
    if len(total_asp_phrasenum_list) == 0:
        total_aspn_length = 0
    else:
        total_aspn_length = 0
        for i in total_asp_phrasenum_list:
            if len(total_asp_phrasenum_list[i]) > total_aspn_length:
                total_aspn_length = len(total_asp_phrasenum_list[i])
    return shared_asp_phrasenum_list, shared_aspn_list, total_aspn_length


'''
FUNC: getsup 得到每一个key的支持度
INPUT: phrase_review, asp_review, phrasenum_to_asp
OUTPUT:phrase_sup,asp_review_count
'''


def getsup(phrase_review, asp_review, phrasenum_to_asp):
    phrase_sup = {}
    asp_review_count = {}
    for a in asp_review.keys():
        asp_review_count[a] = len(asp_review[a])
    for p in phrase_review.keys():
        phrase_sup[p] = len(phrase_review[p]) / asp_review_count[phrasenum_to_asp[p]]
    return phrase_sup

'''
FUNC: shared_pnum_to_Phrase
INPUT: shared_asp_phrasenum_list,phrase_sup0,phrase_sup1
OUTPUT: shared_asp_Phrase_list
'''


def shared_pnum_to_Phrase(shared_asp_phrasenum_list, phrase_sup0, phrase_sup1, phrase_review0, phrase_review1):
    shared_asp_Phrase_list = {}
    for asp in shared_asp_phrasenum_list.keys():
        shared_asp_Phrase_list[asp] = []
        for spnum in shared_asp_phrasenum_list[asp]:
            p = Phrase()
            p.p_num = spnum
            p.sup_0 = phrase_sup0[spnum]
            p.sup_1 = phrase_sup1[spnum]
            p.sup_avg = (p.sup_1 + p.sup_0) / 2
            p.asp = asp
            p.review_list0 = phrase_review0[spnum]
            p.review_list1 = phrase_review1[spnum]
            shared_asp_Phrase_list[asp].append(p)
        shared_asp_Phrase_list[asp] = sorted(shared_asp_Phrase_list[asp], key=lambda t: t.sup_avg, reverse=True)
    return shared_asp_Phrase_list


'''
FUNC:avg_sup_PhraseSet
INPUT:list_Phrase
OUTPUT:avg_sup
'''


def avg_sup_PhraseSet(list_Phrase, total_aspn_length, review_count0, review_count1):
    le = len(list_Phrase)
    if le != 0:
        sup_sum = 0
        for p in list_Phrase:
            sup_sum = sup_sum + p.sup_avg
        avg_sup = sup_sum / (review_count0 + review_count1)
        # if total_aspn_length == 0:
        #     avg_sup = 0
        # else:
            # avg_sup = sup_sum / total_aspn_length
    else:
        avg_sup = 0
    return avg_sup


'''
FUNC:asp_to_ASP
INPUT:asp_num,asp_to_phrasenumlist0,asp_to_phrasenumlist1,phrase_review0,phrase_review1,shared_asp_Phrase_list
OUTPUT:ASP_list
'''


def asp_to_ASP(shared_aspn_list, total_aspn_length, shared_asp_Phrase_list,
               asp_review0, asp_review1, review_count0, review_count1):
    ASP_list = []
    for anum in shared_aspn_list:
        a = Aspect()
        a.num = anum
        a.review_cover0 = []
        a.review_cover1 = []
        a.review_cover0 = list(set(asp_review0[anum]))
        a.review_cover1 = list(set(asp_review1[anum]))
        a.avg_sup = avg_sup_PhraseSet(shared_asp_Phrase_list[anum], total_aspn_length, review_count0, review_count1)
        a.comac = (len(a.review_cover0) / review_count0 + len(a.review_cover1) / review_count1) / 2
        if a.avg_sup == 0 or a.comac == 0:
            a.sim = 0
        else:
            a.sim = 2 / (1 / a.avg_sup + 1 / a.comac)
        ASP_list.append(a)
    ASP_list = list.copy(sorted(ASP_list, key=lambda t: t.avg_sup, reverse=True))
    # print("ASP_LIST is:", end=' ')
    # for a in ASP_list:
    #     print(a.num, end=',')
    # print()
    return ASP_list


'''
FUNC:score_ASPSet
INPUT:list_ASP,shared_asp_Phrase_list,review_count0,review_count1
OUTPUT:score
'''


def score_ASPSet(list_ASP, review_count0, review_count1, nextsup):
    AS = 0
    ReviewCover0 = []
    ReviewCover1 = []
    upperbound = 0
    for asp in list_ASP:
        AS = AS + asp.avg_sup
        ReviewCover0.extend(asp.review_cover0)
        ReviewCover1.extend(asp.review_cover1)
    AvgAS = AS / len(list_ASP)
    left = (len(list(set(ReviewCover0)))) / review_count0
    right = (len(list(set(ReviewCover1)))) / review_count1
    ComAC = (left + right) / 2
    if AvgAS == 0 or ComAC == 0:
        score = 0
    else:
        score = 2 / (1 / AvgAS + 1 / ComAC)
    if (AS + nextsup) != 0:
        upperbound = 2 / (1 + 1 / ((AS + nextsup) / (len(list_ASP) + 1)))
    return score, upperbound


def findallset(item_set, stack, review_count0, review_count1):
    global global_maxscore
    global global_maxlist_list
    n = len(item_set)
    if n == 0:
        return
    for i in range(0, n):
        item_set_n = item_set[i + 1:]
        stack.append(item_set[i])
        if i != n - 1:
            nextsup = item_set[i + 1].avg_sup
        else:
            nextsup = 0
        score, upperbound = score_ASPSet(stack, review_count0, review_count1, nextsup)  # 计算分数，并更新最大值

        if score > global_maxscore:
            global_maxscore = score
            global_maxlist_list = []
            maxlist = list.copy(stack)
            global_maxlist_list.append(maxlist)
        elif score == global_maxscore:
            global_maxlist_list.append(list.copy(stack))

        findallset(item_set_n, stack, review_count0, review_count1)
        stack.pop()


def printstack(stack):
    for ASP in stack:
        print(ASP.num, end=',')
    print()


def findallset_purn(item_set, stack, review_count0, review_count1):
    global global_maxscore
    global global_maxlist_list
    n = len(item_set)
    if n == 0:
        return
    for i in range(0, n):
        item_set_n = item_set[i + 1:]
        stack.append(item_set[i])
        if i != n - 1:
            nextsup = item_set[i + 1].avg_sup
        else:
            nextsup = 0
        score, upperbound = score_ASPSet(stack, review_count0, review_count1, nextsup)  # 计算分数，并更新最大值

        if score > global_maxscore:
            global_maxscore = score
            global_maxlist_list = []
            maxlist = list.copy(stack)
            global_maxlist_list.append(maxlist)
        elif score == global_maxscore:
            global_maxlist_list.append(list.copy(stack))

        if upperbound < global_maxscore:
            stack.pop()
            continue
        else:
            findallset_purn(item_set_n, stack, review_count0, review_count1)
            stack.pop()


def getreviewcount(file_raw):
    fraw = open(file_raw, 'r')
    review_count = -1
    for line in fraw:
        line = line.strip('\r\n')
        if line.count('\n') == len(line):
            continue
        review_count += 1
    review_count += 1
    return review_count


def func_cal (data0, data1, cluster_pro, min_oc, base_path0, base_path1, asp_keylist, purn, base_path_merge):
    time_start = time.time()
    global global_maxscoresum
    global global_setsum
    global global_experiment_count
    global global_time
    global global_property
    global global_maxlist_list
    global global_maxscore
    global_maxscore = 0
    global_maxlist_list = []
    file_of_noun0 = base_path0 + str(data0) + "/NoumMap.txt"
    file_of_noun1 = base_path1 + str(data1) + "/NoumMap.txt"

    file0 = base_path0 + str(data0) + "/Phrase1.txt"
    file1 = base_path1 + str(data1) + "/Phrase1.txt"

    adj_file_homepath0 = base_path0 + str(data0)
    adj_file_homepath1 = base_path1 + str(data1)

    review_count0 = getreviewcount(file0)
    review_count1 = getreviewcount(file1)
    least_occur_time0 = min_oc * review_count0
    least_occur_time1 = min_oc * review_count1
    nounlist_0, nounlist_1, asp_key_adjset, interaput = \
        getasp_word_adjset(asp_keylist, file_of_noun0, adj_file_homepath0,
                           least_occur_time0, file_of_noun1, adj_file_homepath1, least_occur_time1)
    if purn:
        file_result = base_path_merge + "result_" + str(data0) + ".txt"
    else:
        file_result = base_path_merge + "result_" + str(data0) + "_baseline.txt"
    if interaput:
        global_experiment_count += 1;
        word_adj_topnum, pnum_to_meaning, asp_ocount, phrasenum_to_asp = getasp_opinion_tonum(asp_key_adjset)
        phrase_review0, asp_review0, asp_to_phrasenumlist0 = readdata_new(file0, word_adj_topnum, phrasenum_to_asp)
        phrase_review1, asp_review1, asp_to_phrasenumlist1 = readdata_new(file1, word_adj_topnum, phrasenum_to_asp)
        shared_asp_phrasenum_list, shared_aspn_list, total_aspn_length = \
            getshared_pnum_eachasp(asp_to_phrasenumlist0, asp_to_phrasenumlist1)
        phrase_sup0 = getsup(phrase_review0, asp_review0, phrasenum_to_asp)
        phrase_sup1 = getsup(phrase_review1, asp_review1, phrasenum_to_asp)
        shared_asp_Phrase_list = shared_pnum_to_Phrase(shared_asp_phrasenum_list,
                                                       phrase_sup0, phrase_sup1, phrase_review0, phrase_review1)
        ASP_list = asp_to_ASP(shared_aspn_list, total_aspn_length,
                              shared_asp_Phrase_list, asp_review0, asp_review1, review_count0, review_count1)
        if purn:
            findallset_purn(ASP_list, [], review_count0, review_count1)
        else:
            findallset(ASP_list, [], review_count0, review_count1)

        time_end = time.time()
        global_time += time_end-time_start
        f_result = open(file_result, 'a')
        # f_time = open(fto_writetimeinfo, 'w')
        f_result.write('Info of %d_%d : min_oc: %f ; cluster_pro: %f ; time:%f ; score is: %f\n' % (data0, data1, min_oc, cluster_pro, time_end - time_start, global_maxscore))
        string = str(data0) + '_' + str(data1) + ' sim_score_is: ' + str(global_maxscore)
        global_maxscoresum = global_maxscoresum + global_maxscore
        # print("score is %f" % global_maxscore)
        f_result.write('Total number of sets are:%d\n' % len(global_maxlist_list))
        global_setsum = global_setsum + len(global_maxlist_list)
        for ASP_list in global_maxlist_list:
            global_property = global_property + len(ASP_list)
            f_result.write('\nNext set:\n')
            for ASP in ASP_list:
                # f_result.write("\nASP_NUM: %s\nkeywords are:" % str(ASP.num))
                # for key in asp_keylist[ASP.num]:
                #     f_result.write("%s," % str(key))
                # f_result.write('\n')
                f_result.write("Properties:\n")
                shared_asp_Phrase_list[ASP.num] = list.copy(sorted(shared_asp_Phrase_list[ASP.num],
                                                                    key=lambda t: t.sup_avg, reverse=True))
                for Phra in shared_asp_Phrase_list[ASP.num]:
                    f_result.write("%s: sup0: %f sup1: %f sup_avg: %f\n" % (str(pnum_to_meaning[Phra.p_num]),
                                                                                 Phra.sup_0, Phra.sup_1, Phra.sup_avg))
        f_result.flush()
        f_result.close()
        string = string + " aspnum_is: " + str(len(ASP_list)) + ' runtime_is: ' + str(time_end - time_start)
    else:
        string = 'no shared asp'
    return string




def func_main(min_oc, cluster_pro, city0, city1, data_list_0, data_list_1, leng, needclusting, purn, base):
    global global_maxscoresum
    global global_setsum
    global global_experiment_count
    global global_time
    global global_property
    global global_maxlist_list
    global global_maxscore
    base_path0 = base + city0 + "/"
    base_path1 = base + city1 + "/"
    base_path_merge = base + "/oc_" + str(min_oc) + "_clusterpro_" + str(cluster_pro) +"/"
    isExists = os.path.exists(base_path_merge)
    if not isExists:
        os.makedirs(base_path_merge)
    file_vec0 = base_path0 + str(min_oc) + "_wordvec.txt"
    file_vec1 = base_path1 + str(min_oc) + "_wordvec.txt"
    file_nounlist0 = base_path0 + str(min_oc) + "_nounlist.txt"
    file_nounlist1 = base_path1 + str(min_oc) + "_nounlist.txt"
    file_to_keycluster = base_path_merge + "cluster.txt"

    if needclusting:
        # 对整个城市的名词进行聚类
        asp_keylist, key_to_asp, center_word_list = clusternoun(file_vec0, file_vec1,
                                                                file_to_keycluster, cluster_pro, file_nounlist0, file_nounlist1)
    else:
        # 若不需要聚类，则读取文件得到asp_keylist 和 key_to_asp
        file_open_cluster = open(file_to_keycluster, 'r')
        asp_keylist = {}
        key_to_asp = {}
        count = 0
        for line in file_open_cluster.readlines():
            asp_keylist[count] = []
            words = line.strip().split(": ")[1].split(',')
            words.pop()
            for word in words:
                asp_keylist[count].append(word)
                key_to_asp[word] = count
            count += 1
    if purn:
        file_sum = base_path_merge + "sum.txt"
    else:
        file_sum = base_path_merge + "sum_baseline.txt"
    f = open(file_sum, 'w')
    list1 = []
    for i in range(0, leng):
        data0 = int(data_list_0[i])
        data1 = int(data_list_1[i])
        string = func_cal(data0, data1, cluster_pro, min_oc, base_path0, base_path1, asp_keylist, purn, base_path_merge)
        list1.append(string)
        print("oc: " + str(min_oc) + " cp: " + str(cluster_pro) + " " + str(data0) + '_' + str(data1))
        print("global_maxscore: %f" % global_maxscore)
    value1 = global_maxscoresum / global_experiment_count
    value2 = global_setsum / global_experiment_count
    value3 = global_property / global_setsum
    value4 = global_time / global_experiment_count
    f.writelines("AVG.similarity: " + str(value1))
    f.writelines("\nAVG.#shared pro sets: " + str(value2))
    f.writelines("\nAVG.size of pro sets: " + str(value3))
    f.writelines("\nAVG.time: " + str(value4))
    f.writelines("\nExperiment count: " + str(global_experiment_count) + "\n")
    global_setsum = 1
    global_property = 1
    global_maxscoresum = 0
    global_time = 0
    global_experiment_count = 0
    for i in list1:
        f.writelines(i + '\n')
    f.flush()
    f.close()

# α 实验 剪枝
if __name__ == '__main__':
    min_oc = 0.05
    cluster_pro = 0.05
    needclusting = True
    purn = True  # False不剪枝


    for type in ["yelp"]:
        if type == "booking":
            city0 = "london"
            len0 = 482
            city1 = "amsterdam"
            len1 = 526
            # city0 = "london"
            # len0 = 2
            # city1 = "london2"
            # len1 = 2
        elif type == "yelp":
            city0 = "LasVegas"
            len0 = 1524
            city1 = "NorthYork"
            len1 = 1186

        # base = "G:/DASFAA/data/" + type + "/"
        base = "/home/hadoop/xiaohui/data/" + type + "/"
        data_path = base + "term_1000.txt"
        data_list_0 = []
        data_list_1 = []
        data_file = open(data_path, 'r')
        for datapair in data_file.readlines():
            datapair = datapair.strip('\n')
            datapair = datapair.split(',')
            data0 = datapair[0]
            data1 = datapair[1]
            data_list_0.append(data0)
            data_list_1.append(data1)
        data_file.close()
        leng = len(data_list_0)
        func_main(min_oc, cluster_pro, city0, city1, data_list_0, data_list_1, leng, needclusting, purn, base)
