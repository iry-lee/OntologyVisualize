import random

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
print_file = open("dbpedia-triple-of-relation-type-most-" + str(N) + ".txt", "w")
for item in relation_dic.items():
    dic_value = relation_type_dic[item[0]]
    # 下面这句的作用是，如果一个关系，数据量不足N条，也不打印
    # if len(dic_value) < N: continue
    list = sorted(dic_value.items(), key=lambda x:x[1]["count"], reverse=True)
    print_file.write(str(item[0]) + "\n")
    for i in range(0, N):
        if i < len(list):
            print_file.write(str(list[i][1]) + "\n")
