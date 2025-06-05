import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import time
import matplotlib

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')
st.set_page_config(page_title="廣度優先搜尋 (BFS)", page_icon="🌊")
st.title("廣度優先搜尋 (Breadth-First Search, BFS)")

st.markdown("""
## 演算法簡介
廣度優先搜尋 (BFS) 是一種圖形搜尋演算法，它從起始節點開始，先走訪所有相鄰節點，再繼續走訪下一層節點。
這種搜尋方式類似於水面上的波紋擴散，從中心向四周均勻擴散。

### BFS 特性
- 使用**queue (Queue)** 資料結構
- 找到的路徑是從起點到終點的最短路徑
- 適用於最短路徑問題、網路爬蟲、社交網路分析等

### 時間複雜度與空間複雜度
- 時間複雜度：O(V + E)，其中 V 是節點數，E 是邊數
- 空間複雜度：O(V)，需要存儲所有節點
""")

# 視覺化示範
st.header("BFS 視覺化展示")

# 將控制面板移到左側邊欄
st.sidebar.header("控制面板")
start_node = st.sidebar.selectbox("選擇起始節點", ["A", "B", "C", "D", "E", "F", "G"], index=0)
speed = st.sidebar.slider("動畫速度", 0.5, 3.0, 1.0, 0.1)
run_bfs = st.sidebar.button("執行 BFS 演算法")

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

def draw_graph(visited=[], queue=[], current=None):
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
        elif node in queue and node != current:
            node_colors.append('orange')  # 在queue中的節點
        else:
            node_colors.append('lightblue')  # 未訪問節點
    
    # 繪製節點
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=700)
    
    # 繪製標籤
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold')
      # 為顯示queue和已訪問節點添加圖例 - 調整位置避免重疊
    # 創建一個長方形底色來讓文字更清晰
    visited_text = f"Visit Order: {' -> '.join(visited) if visited else 'None'}"
    queue_text = f"Queue Status: {list(queue) if queue else 'Empty'}"
    
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
    ax.text(0.05, -0.10, queue_text, transform=ax.transAxes, fontsize=10, zorder=2)
    
    ax.axis('off')
    
    # 調整圖形布局，確保所有內容可見
    plt.tight_layout()
    
    # 返回圖形但不直接顯示
    return fig

# 初始顯示
graph_placeholder.pyplot(draw_graph())

# 結果顯示區
result_placeholder = st.empty()

if run_bfs:
    # BFS 實現
    visited = []
    queue = deque([start_node])
    visited_order = []
    
    while queue:
        # 顯示當前狀態
        current = queue[0]
        graph_placeholder.pyplot(draw_graph(visited, queue, current))
        time.sleep(1/speed)  # 控制動畫速度
        
        # 出queue
        node = queue.popleft()
        if node not in visited:
            visited.append(node)
            visited_order.append(node)
            
            # 將相鄰節點加入queue
            for neighbor in G[node]:
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)
            
            # 更新顯示
            graph_placeholder.pyplot(draw_graph(visited, queue))
            time.sleep(1/speed)
    
    result_placeholder.success(f"BFS Complete! Visit Order: {' -> '.join(visited_order)}")

# BFS 實作程式碼
st.header("Python 實作程式碼")

code = '''
from collections import deque

def bfs(graph, start):
    # 初始化已訪問集合和queue
    visited = set()
    queue = deque([start])
    result = []
    
    # 當queue不為空時繼續執行
    while queue:
        # 從queue的前端取出一個節點
        vertex = queue.popleft()
        
        # 如果該節點尚未被訪問
        if vertex not in visited:
            # 將節點加入已訪問集合
            visited.add(vertex)
            result.append(vertex)
            
            # 將所有未訪問的相鄰節點加入queue
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    queue.append(neighbor)
    
    return result

# 範例使用
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F', 'G'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E'],
    'G': ['C']
}

bfs_result = bfs(graph, 'A')
print("BFS 訪問順序:", bfs_result)
'''

st.code(code, language="python")

