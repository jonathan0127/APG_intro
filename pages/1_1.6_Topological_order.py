import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib
import pandas as pd
from collections import deque

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')
st.set_page_config(page_title="拓撲排序", page_icon="📊")
st.title("拓撲排序 (Topological Sort)")

st.markdown("""
## 演算法定義
拓撲排序是對**有向無環圖 (DAG, Directed Acyclic Graph)** 中的節點進行線性排序，使得對於圖中的每一條有向邊 (u, v)，
節點 u 在排序中都出現在節點 v 之前。

### 拓撲排序特性
- **僅適用於有向無環圖**：如果圖中存在環，則不存在拓撲排序
- **排序結果可能不唯一**：一個DAG可能有多種有效的拓撲排序
- **廣泛應用於依賴關係分析**：如課程安排、任務排程、編譯順序等

### 拓撲排序流程
1. **初始化階段**：
   - 計算每個節點的入度 (in-degree)
   - 找出所有入度為 0 的節點並加入佇列

2. **主要處理過程**：
   - 從佇列中取出一個入度為 0 的節點，加入結果序列
   - 移除該節點及其所有出邊
   - 更新相鄰節點的入度，若有節點入度變為 0，則加入佇列

3. **重複步驟 2**：直到佇列為空

4. **環檢測**：
   - 如果處理的節點數等於圖中總節點數，則排序成功
   - 否則圖中存在環，無法進行拓撲排序

### 時間複雜度與空間複雜度
- 時間複雜度：O(V + E)，其中 V 是節點數，E 是邊數
- 空間複雜度：O(V)，用於存儲入度表和佇列
""")

# 視覺化示範
st.header("拓撲排序視覺化展示")

# 創建示範圖
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("控制面板")
    graph_type = st.selectbox("選擇圖例", [
        "課程依賴關係", 
        "任務排程", 
        "自定義DAG"
    ], index=0)
    speed = st.slider("動畫速度", 0.5, 3.0, 1.0, 0.1)
    run_topo = st.button("執行拓撲排序")

with col1:
    # 根據選擇創建不同的圖
    if graph_type == "課程依賴關係":
        G = nx.DiGraph()
        edges = [
            ('數學', '物理'), ('數學', '化學'),
            ('物理', '電子學'), ('化學', '生物'),
            ('電子學', '計算機'), ('生物', '生化'),
            ('計算機', '人工智慧')
        ]
        G.add_edges_from(edges)
        pos = {
            '數學': (0.5, 1),
            '物理': (0.2, 0.7), '化學': (0.8, 0.7),
            '電子學': (0.2, 0.4), '生物': (0.8, 0.4),
            '計算機': (0.2, 0.1), '生化': (0.8, 0.1),
            '人工智慧': (0.5, -0.2)
        }
    elif graph_type == "任務排程":
        G = nx.DiGraph()
        edges = [
            ('A', 'C'), ('B', 'C'), ('B', 'D'),
            ('C', 'E'), ('D', 'E'), ('E', 'F')
        ]
        G.add_edges_from(edges)
        pos = {
            'A': (0.2, 0.8), 'B': (0.8, 0.8),
            'C': (0.3, 0.5), 'D': (0.7, 0.5),
            'E': (0.5, 0.2), 'F': (0.5, -0.1)
        }
    else:  # 自定義DAG
        G = nx.DiGraph()
        edges = [
            ('1', '2'), ('1', '3'), ('2', '4'),
            ('3', '4'), ('3', '5'), ('4', '6'),
            ('5', '6')
        ]
        G.add_edges_from(edges)
        pos = {
            '1': (0.5, 1),
            '2': (0.2, 0.6), '3': (0.8, 0.6),
            '4': (0.3, 0.2), '5': (0.7, 0.2),
            '6': (0.5, -0.2)
        }
    
    # 創建顯示元素
    graph_placeholder = st.empty()
    table_placeholder = st.empty()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def draw_graph(in_degrees, queue, processed, current_node=None, removed_edges=None):
        ax.clear()
        
        # 設置節點顏色
        node_colors = []
        for node in G.nodes():
            if node == current_node:
                node_colors.append('red')  # 當前處理的節點
            elif node in processed:
                node_colors.append('green')  # 已處理的節點
            elif node in queue:
                node_colors.append('orange')  # 待處理的節點（入度為0）
            else:
                node_colors.append('lightblue')  # 其他節點
        
        # 設置邊的顏色
        edge_colors = []
        edge_widths = []
        for u, v in G.edges():
            if removed_edges and (u, v) in removed_edges:
                edge_colors.append('lightgray')  # 已移除的邊
                edge_widths.append(1)
            else:
                edge_colors.append('black')  # 正常的邊
                edge_widths.append(2)
        
        # 繪製邊
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, 
                              width=edge_widths, arrows=True, arrowsize=20)
        
        # 繪製節點
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1000)
        
        # 繪製節點標籤（顯示節點名稱和入度）
        labels = {}
        for node in G.nodes():
            degree = in_degrees.get(node, 0)
            labels[node] = f"{node}\n({degree})"
        
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=10, font_weight='bold')
        
        # 添加圖例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=12, label='當前處理'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=12, label='已處理'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=12, label='入度為0'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=12, label='待處理')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        # 顯示狀態信息
        queue_text = f"佇列: {list(queue)}"
        processed_text = f"排序結果: {' → '.join(processed)}"
        
        # 添加信息面板背景
        info_panel = plt.Rectangle((0.03, -0.15), 0.94, 0.12, 
                                  fill=True, color='white', alpha=0.9, 
                                  transform=ax.transAxes, zorder=1)
        ax.add_patch(info_panel)
        
        # 在底色上添加文字
        ax.text(0.05, -0.08, queue_text, transform=ax.transAxes, fontsize=11, zorder=2)
        ax.text(0.05, -0.12, processed_text, transform=ax.transAxes, fontsize=11, zorder=2)
        
        ax.set_title(f"拓撲排序執行過程 ({graph_type})", fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    def display_table(steps_info):
        if not steps_info:
            return pd.DataFrame()
        
        headers = ["步驟", "處理節點", "移除邊", "更新入度", "新加入佇列", "當前排序"]
        data = []
        
        for i, info in enumerate(steps_info, 1):
            current = info.get('current', "")
            removed = info.get('removed_edges', "")
            updated = info.get('updated_degrees', "")
            new_queue = info.get('new_in_queue', "")
            current_order = info.get('current_order', "")
            
            data.append([i, current, removed, updated, new_queue, current_order])
        
        return pd.DataFrame(data, columns=headers)
    
    # 計算初始入度
    initial_in_degrees = {node: G.in_degree(node) for node in G.nodes()}
    initial_queue = [node for node in G.nodes() if initial_in_degrees[node] == 0]
    
    # 初始顯示
    graph_placeholder.pyplot(draw_graph(initial_in_degrees, initial_queue, []))
    
    # 結果顯示區
    result_placeholder = st.empty()
    
    if run_topo:
        # 拓撲排序實現 (Kahn's Algorithm)
        in_degrees = {node: G.in_degree(node) for node in G.nodes()}
        queue = deque([node for node in G.nodes() if in_degrees[node] == 0])
        topo_order = []
        removed_edges = set()
        steps_info = []
        
        while queue:
            # 取出一個入度為0的節點
            current_node = queue.popleft()
            topo_order.append(current_node)
            
            # 顯示當前狀態
            graph_placeholder.pyplot(draw_graph(in_degrees, queue, topo_order, current_node, removed_edges))
            time.sleep(1/speed)
            
            # 記錄移除的邊和更新的入度
            edges_to_remove = []
            updated_nodes = []
            new_zero_degree = []
            
            # 移除該節點的所有出邊
            for neighbor in G.successors(current_node):
                edge = (current_node, neighbor)
                edges_to_remove.append(edge)
                removed_edges.add(edge)
                
                # 減少鄰居的入度
                in_degrees[neighbor] -= 1
                updated_nodes.append(f"{neighbor}:{in_degrees[neighbor]}")
                
                # 如果鄰居的入度變為0，加入佇列
                if in_degrees[neighbor] == 0:
                    queue.append(neighbor)
                    new_zero_degree.append(neighbor)
            
            # 記錄步驟信息
            step_info = {
                'current': current_node,
                'removed_edges': ', '.join([f"{u}→{v}" for u, v in edges_to_remove]),
                'updated_degrees': ', '.join(updated_nodes),
                'new_in_queue': ', '.join(new_zero_degree),
                'current_order': ' → '.join(topo_order)
            }
            steps_info.append(step_info)
            
            # 更新表格
            table_placeholder.dataframe(display_table(steps_info), use_container_width=True)
            
            # 更新顯示
            graph_placeholder.pyplot(draw_graph(in_degrees, queue, topo_order, None, removed_edges))
            time.sleep(1/speed)
        
        # 檢查是否成功完成拓撲排序
        if len(topo_order) == len(G.nodes()):
            result_placeholder.success(
                f"拓撲排序完成！\n排序結果: {' → '.join(topo_order)}"
            )
        else:
            result_placeholder.error("圖中存在環，無法進行拓撲排序！")

# 拓撲排序實作程式碼
st.header("Python 實作程式碼")

st.subheader("Kahn's Algorithm (使用佇列)")
kahn_code = '''
from collections import deque

def topological_sort_kahn(graph):
    # 計算每個節點的入度
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1
    
    # 找出所有入度為0的節點
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    topo_order = []
    
    while queue:
        # 取出一個入度為0的節點
        current = queue.popleft()
        topo_order.append(current)
        
        # 移除該節點的所有出邊
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            # 如果鄰居的入度變為0，加入佇列
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # 檢查是否所有節點都被處理（即是否存在環）
    if len(topo_order) != len(graph):
        return None  # 圖中存在環
    
    return topo_order

# 範例使用
graph = {
    'A': ['C'],
    'B': ['C', 'D'],
    'C': ['E'],
    'D': ['E'],
    'E': ['F'],
    'F': []
}

result = topological_sort_kahn(graph)
if result:
    print("拓撲排序結果:", result)
else:
    print("圖中存在環，無法進行拓撲排序")
'''

st.code(kahn_code, language="python")

st.subheader("DFS Based Algorithm (基於深度優先搜尋)")
dfs_code = '''
def topological_sort_dfs(graph):
    visited = set()
    temp_visited = set()  # 用於檢測環
    topo_order = []
    
    def dfs(node):
        if node in temp_visited:
            return False  # 發現環
        if node in visited:
            return True
        
        temp_visited.add(node)
        
        # 訪問所有鄰居
        for neighbor in graph.get(node, []):
            if not dfs(neighbor):
                return False
        
        temp_visited.remove(node)
        visited.add(node)
        topo_order.append(node)  # 後序添加
        return True
    
    # 對所有未訪問的節點執行DFS
    for node in graph:
        if node not in visited:
            if not dfs(node):
                return None  # 圖中存在環
    
    # 反轉結果（因為是後序添加）
    return topo_order[::-1]

# 範例使用
result = topological_sort_dfs(graph)
if result:
    print("拓撲排序結果:", result)
else:
    print("圖中存在環，無法進行拓撲排序")
'''

st.code(dfs_code, language="python")

# 應用場景
st.header("拓撲排序應用場景")
st.markdown("""
### 實際應用
1. **課程排課系統**：根據先修課程要求安排課程順序
2. **項目管理**：確定任務執行的先後順序
3. **編譯系統**：決定源文件的編譯順序
4. **依賴管理**：軟體包管理器中的依賴解析
5. **工作流程設計**：業務流程中步驟的執行順序

### 演算法比較
- **Kahn's Algorithm**：
  - 使用佇列實現，容易理解
  - 可以輕鬆檢測環的存在
  - 適合需要逐步處理的場景

- **DFS Based**：
  - 使用遞迴實現，程式碼簡潔
  - 在檢測環的同時完成排序
  - 適合遞迴深度不會太大的情況

### 注意事項
- 拓撲排序僅適用於**有向無環圖 (DAG)**
- 一個DAG可能有**多種有效的拓撲排序**
- 如果圖中存在環，則**不存在拓撲排序**
""")
