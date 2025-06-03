import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib
import pandas as pd  # 添加pandas用於表格顯示

# 設置matplotlib支援中文字體
matplotlib.rc('font', family='Microsoft JhengHei')
st.set_page_config(page_title="最小生成樹 (MST)", page_icon="🌳")
st.title("最小生成樹 (Minimum Spanning Tree, MST)")

st.markdown("""
## 最小生成樹的定義
最小生成樹是一個帶權重無向圖中的一個子圖，它是一棵包含圖中所有頂點的樹，且權重總和最小。

### 重要特性
- 它是一棵樹且不包含環路
- 它包含原圖中所有的點
- 它的邊的權重總和在所有可能的生成樹中是最小的
- 若圖中有 n 個頂點，則最小生成樹恰好有 n-1 條邊

### 常見的MST演算法
1. **Kruskal演算法**：從最小權重的邊開始，逐步加入不形成環路的邊
2. **Prim演算法**：從一個頂點開始，逐步擴展到所有頂點
""")

# MST視覺化示範
st.header("最小生成樹視覺化展示")

# 創建示範圖
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("控制面板")
    algorithm = st.selectbox("選擇演算法", ["Kruskal", "Prim"], index=0)
    speed = st.slider("動畫速度", 0.5, 3.0, 1.0, 0.1)
    run_mst = st.button("執行MST演算法")

with col1:
    # 創建一個帶權重的無向圖
    G = nx.Graph()
    
    # 添加帶權重的邊
    edges_with_weights = [
        ('A', 'B', 4), ('A', 'C', 3), 
        ('B', 'C', 2), ('B', 'D', 5),
        ('C', 'D', 1), 
        # ('C', 'E', 6), 已移除CE邊
        ('D', 'E', 7), ('D', 'F', 9),
        ('E', 'F', 8)
    ]
    
    G.add_weighted_edges_from(edges_with_weights)
    
    # 設置節點位置
    pos = {
        'A': (0, 0.8), 
        'B': (0.3, 0.5),
        'C': (0.3, 0.1),
        'D': (0.6, 0.5),
        'E': (0.6, 0.1),
        'F': (1, 0.3)
    }
    
    # 創建一個用於顯示圖形的佔位元素
    graph_placeholder = st.empty()
    
    # 增加一個用於顯示表格的佔位元素
    table_placeholder = st.empty()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    def draw_graph(mst_edges=[], processing_edge=None, processed_edges=None):
        ax.clear()
        
        # 所有邊的顏色設為灰色
        edge_colors = ['gray' for _ in G.edges()]
        
        # 設置邊的寬度
        edge_width = [1 for _ in G.edges()]
        
        # 按優先順序設置邊的顏色：從低到高優先順序為 灰色 -> 橙色 -> 紅色 -> 綠色
        
        # 標記處理過的邊為橙色
        if processed_edges:
            for i, (u, v, _) in enumerate(G.edges(data=True)):
                if (u, v) in processed_edges or (v, u) in processed_edges:
                    edge_colors[i] = 'orange'
                    edge_width[i] = 2
        
        # 標記當前處理的邊為紅色
        if processing_edge:
            for i, (u, v, _) in enumerate(G.edges(data=True)):
                if (u, v) == processing_edge or (v, u) == processing_edge:
                    edge_colors[i] = 'red'
                    edge_width[i] = 2.5
        
        # 標記MST中的邊為綠色 (最高優先順序)
        for i, (u, v, _) in enumerate(G.edges(data=True)):
            if (u, v) in mst_edges or (v, u) in mst_edges:
                edge_colors[i] = 'green'
                edge_width[i] = 3
        
        # 繪製邊 - 添加alpha=1.0確保所有邊都是完全不透明的
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_width, alpha=1.0)
        
        # 繪製節點
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue', node_size=500)
        
        # 繪製節點標籤
        nx.draw_networkx_labels(G, pos, ax=ax, font_weight='bold')
        
        # 繪製邊權重標籤
        edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        if mst_edges:
            total_weight = sum(G[u][v]['weight'] for u, v in mst_edges)
            mst_text = f"最小生成樹總權重: {total_weight}"
            
            # 添加信息面板背景
            info_panel = plt.Rectangle((0.03, -0.05), 0.94, 0.15, 
                                     fill=True, color='white', alpha=0.8, 
                                     transform=ax.transAxes, zorder=1)
            ax.add_patch(info_panel)
            
            # 在底色上添加文字
            ax.text(0.05, -0.03, mst_text, transform=ax.transAxes, fontsize=12, zorder=2)
        
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    # 函數：生成和顯示分析表格
    def display_table(steps_info):
        if not steps_info:
            return
        
        # 建立表格資料
        headers = ["步驟", "考慮的邊", "權重", "是否加入MST", "目前MST總權重"]
        data = []
        
        for i, info in enumerate(steps_info, 1):
            edge = info.get('edge', "")
            weight = info.get('weight', "")
            added = "✓" if info.get('added', False) else "✗"
            total_weight = info.get('total_weight', 0)
            
            data.append([i, edge, weight, added, total_weight])
        
        # 使用Streamlit的表格顯示
        df = pd.DataFrame(data, columns=headers)
        return df
    
    # 初始顯示
    graph_placeholder.pyplot(draw_graph())
    
    # 結果顯示區
    result_placeholder = st.empty()
    
    if run_mst:
        # 初始化步驟資訊列表
        steps_info = []
        
        # 邊的列表，用於Kruskal算法
        edges = list(G.edges(data=True))
        edges.sort(key=lambda x: x[2]['weight'])
        
        if algorithm == "Kruskal":
            # Kruskal算法實現
            mst_edges = []
            processed_edges = []
            total_weight = 0
            
            # 用於檢測環路的並查集
            parent = {node: node for node in G.nodes()}
            
            def find(node):
                if parent[node] != node:
                    parent[node] = find(parent[node])
                return parent[node]
            
            def union(u, v):
                parent[find(u)] = find(v)
            
            for u, v, data in edges:
                processing_edge = (u, v)
                processed_edges.append(processing_edge)
                
                # 更新顯示
                graph_placeholder.pyplot(draw_graph(mst_edges, processing_edge, processed_edges))
                
                # 檢查是否加入MST
                weight = data['weight']
                will_add = find(u) != find(v)
                
                # 準備步驟資訊
                step_info = {
                    'edge': f'{u}-{v}',
                    'weight': weight,
                    'added': will_add,
                    'total_weight': total_weight
                }
                
                if will_add:  # 確保不會形成環路
                    union(u, v)
                    mst_edges.append((u, v))
                    total_weight += weight
                    step_info['total_weight'] = total_weight
                
                # 添加步驟資訊
                steps_info.append(step_info)
                
                # 更新表格
                table_placeholder.dataframe(display_table(steps_info), use_container_width=True)
                
                time.sleep(1/speed)
                
                if will_add:
                    # 更新顯示
                    graph_placeholder.pyplot(draw_graph(mst_edges, None, processed_edges))
                    time.sleep(1/speed)
            
            result_placeholder.success(f"Kruskal演算法完成！MST總權重: {total_weight}")
        
        else:  # Prim算法
            # Prim算法實現
            mst_edges = []
            processed_edges = []
            total_weight = 0
            
            # 從第一個節點開始
            nodes = list(G.nodes())
            included = {nodes[0]}
            
            while len(included) < len(nodes):
                min_edge = None
                min_weight = float('inf')
                
                all_candidate_edges = []
                
                # 尋找最小權重的邊，該邊連接已包含和未包含的節點
                for u in included:
                    for v in G.neighbors(u):
                        if v not in included:
                            processing_edge = (u, v)
                            weight = G[u][v]['weight']
                            processed_edges.append(processing_edge)
                            all_candidate_edges.append((u, v, weight))
                            
                            # 更新顯示
                            graph_placeholder.pyplot(draw_graph(mst_edges, processing_edge, processed_edges))
                            
                            # 準備步驟資訊
                            step_info = {
                                'edge': f'{u}-{v}',
                                'weight': weight,
                                'added': False,  # 先設為False，等確定是最小邊時再更新
                                'total_weight': total_weight
                            }
                            steps_info.append(step_info)
                            
                            # 更新表格
                            table_placeholder.dataframe(display_table(steps_info), use_container_width=True)
                            
                            time.sleep(1/speed)
                            
                            if weight < min_weight:
                                min_edge = (u, v)
                                min_weight = weight
                
                if min_edge:
                    u, v = min_edge
                    mst_edges.append((u, v))
                    included.add(v)
                    total_weight += min_weight
                    
                    # 更新最後加入的邊的狀態
                    for i in range(len(steps_info)-len(all_candidate_edges), len(steps_info)):
                        if steps_info[i]['edge'] == f'{u}-{v}':
                            steps_info[i]['added'] = True
                            steps_info[i]['total_weight'] = total_weight
                    
                    # 更新表格
                    table_placeholder.dataframe(display_table(steps_info), use_container_width=True)
                    
                    # 更新顯示
                    graph_placeholder.pyplot(draw_graph(mst_edges, None, processed_edges))
                    time.sleep(1/speed)
            
            result_placeholder.success(f"Prim演算法完成！MST總權重: {total_weight}")

# 提供MST演算法的偽代碼
st.header("MST演算法流程")

st.subheader("Kruskal演算法")
st.markdown("""
**Kruskal演算法**是一種貪婪演算法，按照邊的權重從小到大依次考慮每條邊。

**流程說明：**
1. **初始化階段**：
   * 為圖中的每個頂點建立一個單獨的集合（每個頂點自成一棵樹）
   * 將所有邊按照權重從小到大排序

2. **建立MST階段**：
   * 依次檢查已排序的邊
   * 如果當前邊連接兩個不同的集合（不會形成環），則：
     - 將這條邊加入MST
     - 合併這條邊連接的兩個集合（使用並查集實現）
   * 如果當前邊會導致環，則丟棄這條邊

3. **終止條件**：
   * 當MST中的邊數達到頂點數減1時停止
   * 或者當所有邊都被考慮過時停止

Kruskal演算法特別適合處理稀疏圖（邊數相對較少的圖）。
""")

st.subheader("Prim演算法")
st.markdown("""
**Prim演算法**也是一種貪婪演算法，但與Kruskal不同，它是從一個起始點開始，逐步擴展樹。

**流程說明：**
1. **初始化階段**：
   * 選擇任意一個頂點作為起點，加入MST
   * 初始化一個集合，用於追蹤已經加入MST的頂點

2. **建立MST階段**：
   * 重複以下步驟，直到所有頂點都已加入MST：
     - 找出所有連接「已在MST中的頂點」和「未在MST中的頂點」的邊
     - 從中選擇權重最小的邊
     - 將這條邊和它連接的新頂點加入MST

3. **終止條件**：
   * 當所有頂點都已加入MST時停止

Prim演算法特別適合處理稠密圖（邊數相對較多的圖）。
""")
