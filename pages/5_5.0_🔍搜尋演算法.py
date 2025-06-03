import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')

st.set_page_config(page_title="搜尋演算法", page_icon="🔍")
st.title("搜尋演算法")

st.markdown("""
## 什麼是搜尋演算法？

搜尋演算法是一種用於從資料集中尋找特定項目或特定條件的項目的方法。在圖論中，搜尋演算法通常用於探索圖形結構，尋找特定節點或路徑。

### 本分類包含的演算法：

1. **深度優先搜尋 (DFS)**
   - 使用堆疊(Stack)資料結構
   - 優先探索圖的深度
   - 適合遍歷所有可能路徑

2. **廣度優先搜尋 (BFS)**
   - 使用佇列(Queue)資料結構
   - 逐層探索圖形結構
   - 適合尋找最短路徑

### DFS 與 BFS 比較

兩種搜尋演算法各有特點，下面的圖形展示了它們在相同圖結構上的不同搜尋順序：
""")

# 創建比較圖
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# 樹結構
tree = nx.balanced_tree(2, 3)  # 創建一個平衡二叉樹
try:
    tree_pos = nx.nx_agraph.graphviz_layout(tree, prog="dot")
except ImportError:
    # 若 pygraphviz 無法使用，則用其他布局算法
    tree_pos = nx.spring_layout(tree, seed=42)

# DFS 訪問順序
dfs_order = list(nx.dfs_preorder_nodes(tree, 0))
dfs_colors = ['#FF9999' if node == 0 else 
              plt.cm.plasma(i/len(dfs_order)) for i, node in enumerate(dfs_order)]

node_colors = [dfs_colors[dfs_order.index(node)] for node in tree.nodes()]
nx.draw(tree, tree_pos, with_labels=True, node_color=node_colors, 
        node_size=700, ax=ax[0], font_weight='bold')
ax[0].set_title("DFS Search Order", fontsize=14)

# BFS 訪問順序
bfs_order = list(nx.bfs_tree(tree, 0).nodes())
bfs_colors = ['#FF9999' if node == 0 else 
              plt.cm.plasma(i/len(bfs_order)) for i, node in enumerate(bfs_order)]

node_colors = [bfs_colors[bfs_order.index(node)] for node in tree.nodes()]
nx.draw(tree, tree_pos, with_labels=True, node_color=node_colors, 
        node_size=700, ax=ax[1], font_weight='bold')
ax[1].set_title("BFS Search Order", fontsize=14)

plt.tight_layout()
st.pyplot(fig)

st.markdown("""
### 點擊左側導航欄中的具體演算法，可以查看更詳細的解釋和互動式示範。
""")

# 添加相關的演算法卡片
col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### 深度優先搜尋 (DFS)
    
    深入探索一條路徑，直到無法繼續前進才回溯。
    
    [查看詳情 →](DFS)
    """)

with col2:
    st.info("""
    ### 廣度優先搜尋 (BFS)
    
    逐層探索所有相鄰節點，適合尋找最短路徑。
    
    [查看詳情 →](BFS)
    """)
