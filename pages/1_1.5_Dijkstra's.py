import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib
import pandas as pd
import heapq

matplotlib.rc('font', family='Microsoft JhengHei')
st.set_page_config(page_title="Dijkstra最短路徑", page_icon="🛤️")
st.title("Dijkstra最短路徑演算法 (Dijkstra's Shortest Path Algorithm)")

st.markdown("""
## 演算法簡介
Dijkstra演算法是一種用於尋找加權圖中單點到任一點最短路徑的貪婪演算法，能夠找到從起始點到圖中所有其他點的最短路徑。

### Dijkstra 流程
1. **初始化階段**：
   - 將起始節點的距離設為 0，其他所有節點的距離設為無限大
   - 建立priority queue，將起始節點加入其中
   - 初始化已處理節點集合為空

2. **主要迭代過程**：
   - 從priority queue中取出距離最小的未處理節點作為當前節點
   - 將當前節點標記為已處理
   - 對當前節點的所有鄰居進行**鬆弛操作**：
     * 計算經由當前節點到鄰居的新距離
     * 如果新距離小於原本記錄的距離，則更新距離並加入priority queue

3. **終止條件**：
   - 當priority queue為空時，演算法結束
   - 此時已找到從起始點到所有可達節點的最短路徑

4. **路徑重建**：
   - 使用前驅節點記錄，從目標節點回溯到起始節點
   - 將路徑反轉得到完整的最短路徑

""")

# 視覺化示範
st.header("Dijkstra 視覺化展示")

# 創建示範圖
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("控制面板")
    start_node = st.selectbox("選擇起始節點", ["A", "B", "C", "D", "E", "F"], index=0)
    target_node = st.selectbox("選擇目標節點", ["A", "B", "C", "D", "E", "F"], index=5)
    speed = st.slider("動畫速度", 0.5, 3.0, 1.0, 0.1)
    run_dijkstra = st.button("執行 Dijkstra 演算法")

with col1:
    # 創建一個帶權重的有向圖
    G = nx.DiGraph()
    
    # 添加帶權重的邊
    edges_with_weights = [
        ('A', 'B', 4), ('A', 'C', 2),
        ('B', 'C', 1), ('B', 'D', 5),
        ('C', 'D', 8), ('C', 'E', 10),
        ('D', 'E', 2), ('D', 'F', 6),
        ('E', 'F', 3)
    ]
    
    G.add_weighted_edges_from(edges_with_weights)
    
    # 設置節點位置
    pos = {
        'A': (0, 0.5),
        'B': (0.3, 0.8),
        'C': (0.3, 0.2),
        'D': (0.6, 0.8),
        'E': (0.6, 0.2),
        'F': (1, 0.5)
    }
    
    # 創建顯示元素
    graph_placeholder = st.empty()
    table_placeholder = st.empty()
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    def draw_graph(distances, processed, current_node=None, current_path=None):
        ax.clear()
        
        # 設置節點顏色
        node_colors = []
        for node in G.nodes():
            if node == current_node:
                node_colors.append('red')  # 當前處理的節點
            elif node in processed:
                node_colors.append('green')  # 已處理的節點
            elif distances[node] != float('inf'):
                node_colors.append('orange')  # 已發現但未處理的節點
            else:
                node_colors.append('lightgray')  # 未發現的節點
        
        # 繪製邊
        edge_colors = ['lightblue' for _ in G.edges()]
        edge_widths = [1 for _ in G.edges()]
        
        # 高亮最短路徑
        if current_path:
            for i, (u, v, _) in enumerate(G.edges(data=True)):
                for j in range(len(current_path) - 1):
                    if (current_path[j] == u and current_path[j+1] == v):
                        edge_colors[i] = 'red'
                        edge_widths[i] = 3
        
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, 
                              width=edge_widths, arrows=True, arrowsize=20)
        
        # 繪製節點 - 增大節點大小
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1200)
        
        # 繪製節點標籤（顯示節點名稱和距離）- 增大字體
        labels = {}
        for node in G.nodes():
            dist_text = f"∞" if distances[node] == float('inf') else str(distances[node])
            labels[node] = f"{node}\n({dist_text})"
        
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=12, font_weight='bold')
        
        # 繪製邊權重標籤 - 增大字體
        edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        # 添加圖例 - 增大圖例標記
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=12, label='當前節點'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=12, label='已處理'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=12, label='待處理'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgray', markersize=12, label='未發現')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    def display_table(steps_info):
        if not steps_info:
            return pd.DataFrame()
        
        headers = ["步驟", "當前節點", "鄰居", "舊距離", "新距離", "是否更新", "priority queue"]
        data = []
        
        for i, info in enumerate(steps_info, 1):
            current = info.get('current', "")
            neighbor = info.get('neighbor', "")
            old_dist = info.get('old_distance', "")
            new_dist = info.get('new_distance', "")
            updated = "✓" if info.get('updated', False) else "✗"
            queue = info.get('queue', "")
            
            data.append([i, current, neighbor, old_dist, new_dist, updated, queue])
        
        return pd.DataFrame(data, columns=headers)
    
    # 初始顯示
    initial_distances = {node: float('inf') for node in G.nodes()}
    initial_distances[start_node] = 0
    graph_placeholder.pyplot(draw_graph(initial_distances, set()))
    
    # 結果顯示區
    result_placeholder = st.empty()
    
    if run_dijkstra:
        # Dijkstra演算法實現
        distances = {node: float('inf') for node in G.nodes()}
        distances[start_node] = 0
        previous = {node: None for node in G.nodes()}
        processed = set()
        priority_queue = [(0, start_node)]
        steps_info = []
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # 如果節點已經被處理過，跳過
            if current_node in processed:
                continue
            
            # 標記為已處理
            processed.add(current_node)
            
            # 更新顯示
            graph_placeholder.pyplot(draw_graph(distances, processed, current_node))
            time.sleep(1/speed)
            
            # 檢查所有鄰居
            for neighbor in G.neighbors(current_node):
                if neighbor not in processed:
                    weight = G[current_node][neighbor]['weight']
                    new_distance = distances[current_node] + weight
                    old_distance = distances[neighbor]
                    
                    # 記錄步驟信息
                    queue_str = str([(d, n) for d, n in priority_queue])
                    step_info = {
                        'current': current_node,
                        'neighbor': neighbor,
                        'old_distance': old_distance if old_distance != float('inf') else "∞",
                        'new_distance': new_distance,
                        'updated': False,
                        'queue': queue_str
                    }
                    
                    # 鬆弛操作
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_node
                        heapq.heappush(priority_queue, (new_distance, neighbor))
                        step_info['updated'] = True
                    
                    steps_info.append(step_info)
                    # 更新表格
                    table_placeholder.dataframe(display_table(steps_info), use_container_width=True)
                    
                    # 更新顯示
                    graph_placeholder.pyplot(draw_graph(distances, processed, current_node))
                    time.sleep(1/speed)
        
        # 構建最短路徑
        if distances[target_node] != float('inf'):
            path = []
            current = target_node
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
            
            # 顯示最終結果
            graph_placeholder.pyplot(draw_graph(distances, processed, None, path))
            
            result_placeholder.success(
                f"從 {start_node} 到 {target_node} 的最短距離: {distances[target_node]}\n"
                f"最短路徑: {' → '.join(path)}"
            )
        else:
            result_placeholder.error(f"從 {start_node} 到 {target_node} 無法到達！")

