from pyecharts.charts import Graph
import pyecharts.options as opts

# 数据读入
# 在这里修改输入文件的文件名
filename = "db_onto_small_mini.txt"
# filename = "yago_ontonet.txt"

file = open("data/" + filename, "r")
triple = []
while True:
    line = file.readline()
    if not line:
        break
    if(filename[:2] == "db"):
        triple.append(line.split("\n")[0].split("\t"))
    elif(filename[:4] == "yago"):
        temp = line.split("\n")[0].split("\t")
        temp[0] = temp[0].split("_")[1]
        temp[2] = temp[2].split("_")[1]
        triple.append(temp)

file.close()

ct = 0
node_dir = {}
node_value = {}
for tri in triple:
    if tri[0] not in node_dir:
        node_dir[tri[0]] = ct
        node_value[tri[0]] = 10
        ct = ct + 1
    else:
        node_value[tri[0]] = node_value[tri[0]] + 2
    if tri[2] not in node_dir:
        node_dir[tri[2]] = ct
        node_value[tri[2]] = 10
        ct = ct + 1
    else:
        node_value[tri[2]] = node_value[tri[2]] + 2

nodes = []
for node in node_dir.items():
    nodes.append({
        "id": node[1],
        "name": node[0],
        "symbolSize": node_value[node[0]],
        "label": {"fontSize": 17, "color": "black"}
    })


edges = []
for tri in triple:
    # 不展示指向自己的关系
    # 以及可以选定某一种关系进行展示 "if tri[2] == 'isa':"
    if tri[0] != tri[2]:
        edges.append({
            "source": node_dir.get(tri[0]),
            "label": {"formatter":tri[1], "show": True, "color": "gray", "position":"middle"},
            "symbol": ["", "arrow"],
            "target": node_dir.get(tri[2]),
        })

c = (
    Graph(init_opts=opts.InitOpts(width="1600px", height="800px"))
    .add("", nodes, edges, repulsion=8000, linestyle_opts=opts.LineStyleOpts(width=0.5, curve=0.3, opacity=0.7))
    .set_global_opts(title_opts=opts.TitleOpts(title="Ontology-Graph"))
    .render(filename + ".html")
)