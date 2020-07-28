from pyecharts import options as opts
from pyecharts.charts import Graph

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

# 开始画图
# nodes = []
# for item in type_dic.items():
#     nodes.append({"name": item[0]})

recorder = {}
nodes = []
links = []
# 先放一个relation进来试试
for item in relation_dic.items():
    dic_value = relation_type_dic[item[0]]
    for val in dic_value.values():
        # 因为改成了生成关系图，所以就把这里注释掉了，这里是为桑基图设计的
        # links.append({"source": val["head"], "target": val["tail"], "value": val["count"]})
        links.append({"source": val["head"], "target": val["tail"]})
        if val["head"] not in recorder:
            recorder[val["head"]] = 1
            nodes.append({"name": val["head"]})
        if val["tail"] not in recorder:
            recorder[val["tail"]] = 1
            nodes.append({"name": val["tail"]})
    break

c = (
    Graph(init_opts=opts.InitOpts(width="1600px", height="800px"))
    .add("", nodes, links,
         repulsion=8000,
         layout="force",
         linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7),
         )
    .set_global_opts(title_opts=opts.TitleOpts(title="Graph"))
    .render("relation.html")
)