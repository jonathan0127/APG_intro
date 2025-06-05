import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')
st.set_page_config(page_title="深度優先搜尋 (DFS)", page_icon="🧭")
st.title("深度優先搜尋 (Depth-First Search, DFS)")

st.markdown("""
## 演算法簡介
深度優先搜尋 (DFS) 是一種圖形搜尋演算法，從起始點開始，盡可能深入探索一條路徑，直到無法繼續前進才回溯。
這種搜尋方式類似於走迷宮時，優先選擇一條路走到底，遇到死路才回頭嘗試其他路徑。

### DFS 特性
- 使用**堆疊 (Stack)** 資料結構（或遞迴實現）
- 深入優先，不一定找到最短路徑
- 適用於遍歷所有可能路徑、拓撲排序、連通元件分析等

### 時間複雜度與空間複雜度
- 時間複雜度：O(V + E)，其中 V 是節點數，E 是邊數
- 空間複雜度：O(V)，需要存儲訪問狀態和遞迴堆疊
""")

# 視覺化示範
st.header("DFS 視覺化展示")

# 將控制面板移到左側邊欄
st.sidebar.header("控制面板")
start_node = st.sidebar.selectbox("選擇起始節點", ["A", "B", "C", "D", "E", "F", "G"], index=0)
speed = st.sidebar.slider("動畫速度", 0.5, 3.0, 1.0, 0.1)
run_dfs = st.sidebar.button("執行 DFS 演算法")

# 創建一個圖
G = nx.Graph()
G.add_edges_from([
    ('A', 'B'), ('A', 'C'), 
    ('B', 'D'), ('B', 'E'),
    ('C', 'F'), ('C', 'G'),
    ('E', 'F')
])

# 設置節點位置
pos = {
    'A': (0.5, 1), 
    'B': (0.3, 0.7), 'C': (0.7, 0.7),
    'D': (0.1, 0.4), 'E': (0.4, 0.4), 'F': (0.6, 0.4), 'G': (0.9, 0.4)
}

# 創建一個用於顯示圖形的佔位元素
graph_placeholder = st.empty()

fig, ax = plt.subplots(figsize=(8, 6))

def draw_graph(visited=[], stack=[], current=None):
    ax.clear()
    
    # 繪製邊
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray')
    
    # 節點顏色
    node_colors = []
    for node in G.nodes():
        if node == current:
            node_colors.append('red')  # 當前節點
        elif node in visited and node != current:
            node_colors.append('green')  # 已訪問節點
        elif node in stack and node != current:
            node_colors.append('orange')  # 在堆疊中的節點
        else:
            node_colors.append('lightblue')  # 未訪問節點
    
    # 繪製節點
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=700)
    
    # 繪製標籤
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold')
      # 為顯示堆疊和已訪問節點添加圖例 - 調整位置避免重疊
    # 創建一個長方形底色來讓文字更清晰
    visited_text = f"Visit Order: {' -> '.join(visited) if visited else 'None'}"
    stack_text = f"Stack Status: {list(reversed(stack)) if stack else 'Empty'}"
    
    # 正確方式清除現有的圖形元素，而不是直接設置 patches 屬性
    for patch in ax.patches[:]:
        patch.remove()
    
    # 添加信息面板背景
    info_panel = plt.Rectangle((0.03, -0.05), 0.94, 0.15, 
                              fill=True, color='white', alpha=0.8, 
                              transform=ax.transAxes, zorder=1)
    ax.add_patch(info_panel)
    
    # 在底色上添加文字
    ax.text(0.05, -0.05, visited_text, transform=ax.transAxes, fontsize=10, zorder=2)
    ax.text(0.05, -0.1, stack_text, transform=ax.transAxes, fontsize=10, zorder=2)
    
    ax.axis('off')
    
    # 調整圖形布局，確保所有內容可見
    plt.tight_layout()
    
    return fig

# 初始顯示
graph_placeholder.pyplot(draw_graph())

# 結果顯示區
result_placeholder = st.empty()

if run_dfs:
    # DFS 實現
    visited = []
    stack = [start_node]
    visited_order = []
    
    while stack:
        # 顯示當前狀態
        current = stack[-1]
        graph_placeholder.pyplot(draw_graph(visited, stack, current))
        time.sleep(1/speed)  # 控制動畫速度
        
        # 彈出堆疊
        node = stack.pop()
        if node not in visited:
            visited.append(node)
            visited_order.append(node)
            
            # 尋找所有未訪問的相鄰節點
            neighbors = list(G[node])
            neighbors.sort(reverse=True)  # 為了讓DFS按字母順序訪問，需要反轉
            
            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in stack:
                    stack.append(neighbor)
            
            # 更新顯示
            graph_placeholder.pyplot(draw_graph(visited, stack))
            time.sleep(1/speed)
    
    result_placeholder.success(f"DFS Complete! Visit Order: {' -> '.join(visited_order)}")


# 應用場景
st.header("DFS 應用場景")
st.markdown("""

### DFS vs BFS 比較圖

以下圖片說明了 DFS 和 BFS 的搜尋方式差異：
""")

# 創建比較圖
comp_fig, comp_ax = plt.subplots(1, 2, figsize=(12, 5))

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
        node_size=700, ax=comp_ax[0], font_weight='bold')
comp_ax[0].set_title("DFS Search Order", fontsize=14)

# BFS 訪問順序
bfs_order = list(nx.bfs_tree(tree, 0).nodes())
bfs_colors = ['#FF9999' if node == 0 else 
              plt.cm.plasma(i/len(bfs_order)) for i, node in enumerate(bfs_order)]

node_colors = [bfs_colors[bfs_order.index(node)] for node in tree.nodes()]
nx.draw(tree, tree_pos, with_labels=True, node_color=node_colors, 
        node_size=700, ax=comp_ax[1], font_weight='bold')
comp_ax[1].set_title("BFS Search Order", fontsize=14)

plt.tight_layout()
st.pyplot(comp_fig)
