import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def display_graph(adj_matrix, title="Graph"):
    """根據鄰接矩陣繪製有向圖"""
    plt.figure(figsize=(5, 5))
    G = nx.DiGraph()
    
    n = len(adj_matrix)
    for i in range(n):
        G.add_node(i)
    
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] == 1:
                G.add_edge(i, j)
    
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=500, arrowsize=20, font_size=15)
    plt.title(title)
    return plt

def matrix_power(A, n):
    """計算矩陣A的n次方"""
    result = A.copy()
    for _ in range(n-1):
        result = np.matmul(result, A)
    return result

def compute_transitive_closure(A):
    """計算Transitive Closure (Warshall's Algorithm)"""
    n = len(A)
    R = A.copy()
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                R[i][j] = R[i][j] or (R[i][k] and R[k][j])
    
    return R

def is_strongly_connected(adj_matrix):
    """檢查有向圖是否強連通"""
    tc = compute_transitive_closure(adj_matrix)
    n = len(adj_matrix)
    
    # 對於強連通圖，任意兩點之間都存在路徑
    for i in range(n):
        for j in range(n):
            if i != j and tc[i][j] == 0:
                return False
    
    return True

def find_connected_components(adj_matrix):
    """找出有向圖的強連通分量"""
    n = len(adj_matrix)
    G = nx.DiGraph()
    
    for i in range(n):
        G.add_node(i)
    
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] == 1:
                G.add_edge(i, j)
    
    # 使用Tarjan算法找出強連通分量
    return list(nx.strongly_connected_components(G))

def display_components(adj_matrix, components):
    """以不同顏色顯示強連通分量"""
    plt.figure(figsize=(5, 5))
    G = nx.DiGraph()
    
    n = len(adj_matrix)
    for i in range(n):
        G.add_node(i)
    
    for i in range(n):
        for j in range(n):
            if adj_matrix[i][j] == 1:
                G.add_edge(i, j)
    
    pos = nx.spring_layout(G, seed=42)
    
    # 為每個強連通分量指定不同顏色
    colors = plt.cm.rainbow(np.linspace(0, 1, len(components)))
    
    for idx, component in enumerate(components):
        nx.draw_networkx_nodes(G, pos, nodelist=list(component), 
                               node_color=[colors[idx]]*len(component), 
                               node_size=500)
    
    nx.draw_networkx_edges(G, pos, arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=15)
    
    plt.title("強連通分量 (Strongly Connected Components)")
    return plt

def display_matrix(matrix, title="Matrix"):
    """顯示矩陣"""
    fig, ax = plt.subplots(figsize=(5, 5))
    cmap = ListedColormap(['white', 'lightblue'])
    ax.matshow(matrix, cmap=cmap)
    
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            ax.text(j, i, str(matrix[i][j]), va='center', ha='center', fontsize=15)
    
    plt.title(title)
    return plt

def main():
    st.title("Transitive Closure & Connectivity")
    
    st.header("1. Transitive Closure的定義")
    st.write("""
    對於一個有向圖 G，其Transitive Closure是一個新的有向圖 G+，滿足以下條件：
    - G+ 包含 G 中的所有頂點
    - 對於 G 中的每一條邊 (u, v)，G+ 中也存在邊 (u, v)
    - 如果在 G 中存在一條從 u 到 v 的路徑，那麼在 G+ 中就存在一條從 u 到 v 的邊
    
    簡單來說，Transitive Closure表示了圖中所有可達性關係。如果在原圖中可以從頂點 i 通過多個邊到達頂點 j，
    那麼在Transitive Closure中，就會有一條直接從 i 到 j 的邊。
    """)
    
    st.header("2. 圖與鄰接矩陣舉例")
    
    # 原始有向圖的鄰接矩陣
    A = np.array([
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ])
    
    st.subheader("原始有向圖")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(display_graph(A, "原始有向圖 G"))
    with col2:
        st.pyplot(display_matrix(A, "鄰接矩陣 A"))
    
    st.write("""
    在上面的例子中，我們有一個有向圖 G 和它對應的鄰接矩陣 A。
    - 矩陣中的 1 表示存在從行索引到列索引的邊
    - 矩陣中的 0 表示不存在邊
    
    例如，A[0][1] = 1 表示從頂點 0 到頂點 1 有一條邊。
    """)
    
    # 計算Transitive Closure
    transitive_closure = compute_transitive_closure(A)
    
    st.subheader("Transitive Closure")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(display_graph(transitive_closure, "Transitive Closure G+"))
    with col2:
        st.pyplot(display_matrix(transitive_closure, "Transitive Closure矩陣 A+"))
    
    st.write("""
    Transitive Closure G+ 顯示了所有可達性關係。例如，在原圖中，從頂點 0 到頂點 3 沒有直接的邊，
    但可以通過路徑 0→1→2→3 到達，因此在Transitive Closure中，增加了從 0 到 3 的直接邊。
    """)
    
    st.header("3. 矩陣乘法與Transitive Closure的關係")
    
    A2 = np.matmul(A, A)
    A3 = np.matmul(A, A2)
    
    st.subheader("A² = A × A (矩陣的平方)")
    st.pyplot(display_matrix(A2, "A² 矩陣"))
    
    st.write("""
    A² 的第 i 行第 j 列表示從頂點 i 到頂點 j 有沒有長度為 2 的路徑。
    例如，A²[0][2] = 1 表示從頂點 0 到頂點 2 存在長度為 2 的路徑 (0→1→2)。
    """)
    
    st.subheader("A³ = A × A² (矩陣的立方)")
    st.pyplot(display_matrix(A3, "A³ 矩陣"))
    
    st.write("""
    A³ 的第 i 行第 j 列表示從頂點 i 到頂點 j 有沒有長度為 3 的路徑。
    例如，A³[0][3] = 1 表示從頂點 0 到頂點 3 存在長度為 3 的路徑 (0→1→2→3)。
    """)
    
    st.subheader("Transitive Closure與矩陣次方的關係")
    
    st.write("""
    Transitive Closure可以用矩陣次方來表示：A+ = A + A² + A³ + ... + Aⁿ
    
    其中 n 是圖中的頂點數，A+ 表示Transitive Closure矩陣。
    
    這個加法表示邏輯 OR 操作。所以如果兩個頂點之間有任意長度的路徑，
    Transitive Closure矩陣的對應位置就會是 1。
    
    這個性質說明：
    - A 表示長度為 1 的路徑
    - A² 表示長度為 2 的路徑
    - A³ 表示長度為 3 的路徑
    ...
    
    所以Transitive Closure實際上表示了任意長度的路徑的存在性。
    """)
    
    st.header("4. 圖的連通性 (Connectivity)")
    
    st.write("""
    圖的連通性是指圖中各頂點之間的連接關係。
    
    **強連通 (Strongly Connected)**: 有向圖中，若對於任意兩個不同的頂點 u 和 v，都同時存在從 u 到 v 和從 v 到 u 的路徑，則稱該圖是強連通的。
    
    **強連通分量 (Strongly Connected Component, SCC)**: 有向圖中的極大強連通子圖。
    """)
    
    # 新的例子 - 矩陣B
    B = np.array([
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0]
    ])
    
    st.subheader("連通性範例")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(display_graph(B, "有向圖範例"))
    with col2:
        st.pyplot(display_matrix(B, "鄰接矩陣 B"))
    
    st.write("""
    在此範例中：
    - 頂點0, 1, 2形成一個強連通分量 (可互相到達)
    - 頂點3和4形成另一個強連通分量 (可互相到達)
    - 從第一個分量可以到達第二個分量，但無法反向
    """)
    
    components = find_connected_components(B)
    
    

if __name__ == "__main__":
    main()
