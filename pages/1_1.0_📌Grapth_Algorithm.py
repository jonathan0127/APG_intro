import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import numpy as np
from collections import deque

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')


st.set_page_config(page_title="Graph Algorithm", page_icon="📌")
st.title("Graph Algorithm")

st.markdown("""
## 圖的定義
### Graph G = (V, E)
- V: 節點集合
- E: 邊集合

## 圖的類型
1. **有向圖**: 邊有方向性，表示從一個節點指向另一個節點。
2. **無向圖**: 邊沒有方向性，表示兩個節點之間的關係是雙向的。
"""
)

# 添加更多圖論基礎知識
st.markdown("""
## 圖的表示方法
1. **鄰接矩陣 (Adjacency Matrix)**: 用二維矩陣表示節點間的連接關係
2. **鄰接表 (Adjacency List)**: 每個節點存儲其相鄰節點的列表
""")
# 添加圖像與表格化說明
st.markdown("### 鄰接矩陣與鄰接表的視覺化比較")

# 創建示例圖
def create_sample_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0,1), (0,2), (1,2), (2,0), (2,3)])
    return G

G = create_sample_graph()

# 繪製圖形
fig, ax = plt.subplots(figsize=(4, 3))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=500, arrowsize=20, ax=ax, font_size=14)
st.pyplot(fig)

# 生成並顯示鄰接矩陣
st.subheader("鄰接矩陣表示")
adj_matrix = nx.to_numpy_array(G, dtype=int)
st.markdown("鄰接矩陣是一個 n×n 的方陣，其中 n 是圖中節點的數量。如果節點 i 和節點 j 之間有邊，則矩陣中對應位置的值為 1（或權重值），否則為 0。")


# 視覺化鄰接矩陣
fig, ax = plt.subplots(figsize=(7, 6))
cax = ax.matshow(adj_matrix, cmap='YlOrBr')
for i in range(adj_matrix.shape[0]):
    for j in range(adj_matrix.shape[1]):
        ax.text(j, i, str(adj_matrix[i, j]), va='center', ha='center', fontsize=15)
ax.set_xticks(range(adj_matrix.shape[0]))
ax.set_yticks(range(adj_matrix.shape[0]))
ax.set_xticklabels(range(adj_matrix.shape[0]))
ax.set_yticklabels(range(adj_matrix.shape[0]))
ax.set_xlabel('目標節點')
ax.set_ylabel('來源節點')
ax.set_title('鄰接矩陣視覺化')
st.pyplot(fig)

# 生成並顯示鄰接表
st.subheader("鄰接表表示")
st.markdown("鄰接表為每個節點產生一個陣列，陣列中包含與該節點相鄰的所有節點。")

# 視覺化鄰接表
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(G.nodes())*1.5)
ax.axis('off')

for i, node in enumerate(sorted(G.nodes())):
    ax.text(0.5, len(G.nodes())*1.2 - i*1.2, f"節點 {node}", fontsize=14, ha='left')
    ax.text(2, len(G.nodes())*1.2 - i*1.2, "→", fontsize=14)
    neighbors = list(G.neighbors(node))
    if neighbors:
        for j, neighbor in enumerate(neighbors):
            ax.text(3 + j*1.5, len(G.nodes())*1.2 - i*1.2, str(neighbor), fontsize=14, 
                    bbox=dict(facecolor='lightblue', alpha=0.5, boxstyle='circle'))
            if j < len(neighbors) - 1:
                ax.text(3 + j*1.5 + 0.8, len(G.nodes())*1.2 - i*1.2, "→", fontsize=14)

ax.set_title('鄰接表視覺化', fontsize=16)
st.pyplot(fig)

# 比較表格
st.subheader("鄰接矩陣與鄰接表比較")
comparison_data = {
    "特性": ["空間複雜度", "查找兩節點是否相鄰", "查找節點的所有鄰居", "添加節點", "添加邊", "刪除節點", "刪除邊", "適用場景"],
    "鄰接矩陣": ["O(n²)", "O(1)", "O(n)", "O(n²)", "O(1)", "O(n²)", "O(1)", "稠密圖，頻繁查詢兩節點是否相鄰"],
    "鄰接表": ["O(n+e)，其中e為邊數", "O(degree)", "O(degree)", "O(1)", "O(1)", "O(n+e)", "O(degree)", "稀疏圖，需要頻繁遍歷鄰居"]
}

st.table(comparison_data)

st.markdown("""
## 圖的重要性質
- **路徑 (Path)**: 連接兩個節點的邊序列
- **環 (Cycle)**: 首尾相連的路徑
- **連通圖 (Connected Graph)**: 任意兩節點間存在路徑的圖
- **樹 (Tree)**: 無環連通圖
- **權重圖 (Weighted Graph)**: 邊帶有權重的圖
- **節點的degree**: 表示與該節點相連的邊的數量(degree = in-degree + out-degree)
  - **Degree**: 節點的度數，表示與該節點相連的邊的數量
  - **In-Degree**: 指向該節點的邊的數量
  - **Out-Degree**: 從該節點指向其他節點的邊的數量
""")

