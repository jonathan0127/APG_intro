import streamlit as st

st.set_page_config(page_title="演算法視覺化",page_icon="🧮",)

st.write("# 常用演算法說明區")

st.sidebar.success("Home")

# 創建下拉式選單
search_algorithms = st.sidebar.expander("🔍 搜尋演算法")
with search_algorithms:
    st.page_link("pages/1_1.2_BFS.py", label="廣度優先搜尋 (BFS)")
    st.page_link("pages/1_1.3_DFS.py", label="深度優先搜尋 (DFS)")

# 新增圖論演算法分類
graph_algorithms = st.sidebar.expander("🌐 圖論演算法")
with graph_algorithms:
    st.page_link("pages/1_1.0_Grapth_Algorithm.py", label="圖論介紹")
    st.page_link("pages/1_1.1_Transitive_Closure&Connectivity.py", label="圖的遞移性與連通性")
    st.page_link("pages/1_1.4_Minimum_Spanning_Trees.py", label="最小生成樹 (MST)")
    st.page_link("pages/1_1.5_Dijkstra's.py", label="Dijkstra最短路徑")
    

st.markdown(
    """
    ## 歡迎來到演算法視覺化學習平台！
    
    本網站提供常用演算法的詳細解說與視覺化呈現，幫助你更直觀地理解演算法的運作原理。
    
    
    
    ### 使用方式
    在左側欄選擇你想了解的演算法分類和具體演算法，每個頁面都包含：
    - 演算法基本介紹
    - 圖形化說明
    - 實際應用場景
    
    """
)