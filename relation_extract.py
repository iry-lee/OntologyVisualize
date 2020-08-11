# 使用的环境是pytorch35.yml
import random
from scipy.spatial.distance import cosine


insNet = open("data/db_insnet.txt", "r", encoding="utf8")
insType = open("data/db_InsType_mini.txt", "r", encoding="utf8")

type_ct = 0
type_dic = {}
entity_type_dic = {}
# 对于属于多个类的实体，先考虑第一个遇到的类型
for line in insType.readlines():
    entity, type = line.split()[0], line.split()[2]
    if entity not in entity_type_dic:
        entity_type_dic[entity] = type
    if type not in type_dic:
        type_dic[type] = type_ct
        type_ct = type_ct + 1

relation_dic = {}
relation_type_dic = {}
# relation_type_dic = {key : value}
# ---- key(string): relation_name
# ---- value(dic): {key : value}
# --------- key(int): entity_type_dic[head]*(type_ct+1) + entity_type_dic[tail]     ( by using hash code
# --------- value(dic): {"head": head_name, "tail": tail_name, "count": number}
for line in insNet.readlines():
    head, relation, tail = line.split()[0], line.split()[1], line.split()[2]
    if head == tail: continue
    head_type, tail_type = entity_type_dic[head], entity_type_dic[tail]
    if relation not in relation_dic:
        relation_dic[relation] = relation
    if relation in relation_type_dic:
        dic_key = type_dic[head_type]*(type_ct+1) + type_dic[tail_type]
        if dic_key not in relation_type_dic[relation]:
            relation_type_dic[relation][dic_key] = {"head": head_type, "tail": tail_type, "count": 1}
        else:
            dic_value = relation_type_dic[relation][dic_key]
            relation_type_dic[relation][dic_key] = {"head": head_type, "tail": tail_type, "count": dic_value["count"] + 1}
    else:
        dic_value = {}
        dic_value[type_dic[head_type]*(type_ct+1) + type_dic[tail_type]] \
            = {"head": head_type, "tail": tail_type, "count": 1}
        relation_type_dic[relation] = dic_value

insNet.close()
insType.close()

# 【如果直接打印的话】
# 不然就改为输出每个关系的前 N 个(C1, r, C2)
# 先设 N=10
N = 10
# 用来保存concept，用于后续生成concept的编码
concept_dic = {}
# concept_dic = {key: value}
# ---- key(string): concept_name
# ---- value(int): numbering
concept_dic_ct = 0
# 对于每个关系，保存前N个concept relation实例
relation_type_dic_most_N = {} 
# relation_type_dic = {key : value}
# ---- key(string): relation_name
# ---- value(list): [[head_type_name, tail_type_name],[],....]
print_file = open("dbpedia-triple-of-relation-type-most-" + str(N) + ".txt", "w")
for item in relation_dic.items():
    dic_value = relation_type_dic[item[0]]
    # 下面这句的作用是，如果一个关系，数据量不足N条，也不打印
    # if len(dic_value) < N: continue
    list_temp = sorted(dic_value.items(), key=lambda x:x[1]["count"], reverse=True)
    print_file.write(str(item[0]) + "\n")
    relation_type_dic_most_N[item[0]] = []
    for i in range(0, N):
        if i < len(list_temp):
            print_file.write(str(list_temp[i][1]) + "\n")
            htype = list_temp[i][1]["head"]
            ttype = list_temp[i][1]["tail"]
            relation_type_dic_most_N[item[0]].append([htype, ttype])
            if htype not in concept_dic:
                concept_dic[htype] = concept_dic_ct
                concept_dic_ct = concept_dic_ct + 1
            if ttype not in concept_dic:
                concept_dic[ttype] = concept_dic_ct
                concept_dic_ct = concept_dic_ct + 1


# 开始做关系类型的分类，等价关系？逆关系？自环关系？包含关系？
# 1.等价关系、逆关系
relation_vector = []  # 用来保存relation的头concept集合向量表示和尾concept集合向量表示
# relation_vector = [head_vector, tail_vector]
# head_vector = []
# tail_vector = []
equivalence_relation_file = open("equivalence-relation-most-" + str(N) + ".txt", "w")
inverse_relation_file = open("inverse-relation-most-" + str(N) + ".txt", "w")
selfloop_relation_file = open("selfloop-relation-most-" + str(N) + ".txt", "w")

for item in relation_dic.items():
    value = relation_type_dic_most_N[item[0]]
    head_vector = []
    tail_vector = []
    for i in range(0, concept_dic_ct):
        head_vector.append(0)
        tail_vector.append(0)
    for one in value:
        # one 的格式:
        # one[0]: (string)head_type_name
        # one[1]: (string)tail_type_name
        head_vector[concept_dic[one[0]]] = 1
        tail_vector[concept_dic[one[1]]] = 1
    relation_vector.append([head_vector, tail_vector])

# 现在关系的头尾向量表示就都在relation_vector中了

threshold = 0.2001
for i in range(0, len(relation_vector)):
    relation_list = list(relation_dic.keys())
    head_vector = relation_vector[i][0]
    tail_vector = relation_vector[i][1]
    for j in range(i+1, len(relation_vector)):
        if j == i: continue
        _head_vector = relation_vector[j][0]
        _tail_vector = relation_vector[j][1]
        c1 = cosine(_head_vector, head_vector)
        c2 = cosine(_tail_vector, tail_vector)
        c3 = cosine(_head_vector, tail_vector)
        c4 = cosine(_tail_vector, head_vector)
        if c1 < threshold and c2 < threshold and c3 < threshold and c4 < threshold:
            selfloop_relation_file.write(relation_list[i])
            selfloop_relation_file.write(" >>> " + relation_list[j] + "(cosine: " + str(c1) + "," + str(c2) + ")")
            selfloop_relation_file.write("\n")
            continue

        if c1 < threshold and c2 < threshold:
            equivalence_relation_file.write(relation_list[i])
            equivalence_relation_file.write(" >>> " + relation_list[j] + "(cosine: " + str(c1) + "," + str(c2) + ")")
            equivalence_relation_file.write("\n")

        if c3 < threshold and c4 < threshold:
            inverse_relation_file.write(relation_list[i])
            inverse_relation_file.write(" >>> " + relation_list[j] + "(cosine: " + str(c3) + "," + str(c4) + ")")
            inverse_relation_file.write("\n")


equivalence_relation_file.close()
inverse_relation_file.close()

'''
【后续的改进之处】：
concept向量的生成，现在采用的是凡是出现在头/尾concept集合中，就将向量中该位置为1，
其实无法很好地体现不同的concept在集合中所占比的关系，其实还要根据各个concept出现的次数
也纳入到向量中，最后做一个正则化，这样应该会好一些。
'''