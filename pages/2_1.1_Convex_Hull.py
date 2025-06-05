import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import time
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches

def orientation(p, q, r):
    """計算三點的方向"""
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  # 共線
    return 1 if val > 0 else 2  # 順時針或逆時針

def distance(p1, p2):
    """計算兩點間距離"""
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def merge_hulls(left_hull, right_hull):
    """合併兩個凸包"""
    # 找到最右邊的左凸包點和最左邊的右凸包點
    left_rightmost = max(range(len(left_hull)), key=lambda i: left_hull[i][0])
    right_leftmost = min(range(len(right_hull)), key=lambda i: right_hull[i][0])
    
    # 找上切線
    upper_left = left_rightmost
    upper_right = right_leftmost
    
    while True:
        changed = False
        # 檢查左凸包
        next_left = (upper_left + 1) % len(left_hull)
        while orientation(right_hull[upper_right], left_hull[upper_left], left_hull[next_left]) != 2:
            upper_left = next_left
            next_left = (upper_left + 1) % len(left_hull)
            changed = True
        
        # 檢查右凸包
        prev_right = (upper_right - 1) % len(right_hull)
        while orientation(left_hull[upper_left], right_hull[upper_right], right_hull[prev_right]) != 1:
            upper_right = prev_right
            prev_right = (upper_right - 1) % len(right_hull)
            changed = True
            
        if not changed:
            break
    
    # 找下切線
    lower_left = left_rightmost
    lower_right = right_leftmost
    
    while True:
        changed = False
        # 檢查左凸包
        prev_left = (lower_left - 1) % len(left_hull)
        while orientation(right_hull[lower_right], left_hull[lower_left], left_hull[prev_left]) != 1:
            lower_left = prev_left
            prev_left = (lower_left - 1) % len(left_hull)
            changed = True
        
        # 檢查右凸包
        next_right = (lower_right + 1) % len(right_hull)
        while orientation(left_hull[lower_left], right_hull[lower_right], right_hull[next_right]) != 2:
            lower_right = next_right
            next_right = (lower_right + 1) % len(right_hull)
            changed = True
            
        if not changed:
            break
    
    # 構建合併後的凸包
    result = []
    
    # 從左凸包的上切線點開始，順時針到下切線點
    i = upper_left
    while True:
        result.append(left_hull[i])
        if i == lower_left:
            break
        i = (i + 1) % len(left_hull)
    
    # 從右凸包的下切線點開始，順時針到上切線點
    i = lower_right
    while True:
        result.append(right_hull[i])
        if i == upper_right:
            break
        i = (i + 1) % len(right_hull)
    
    return result

def convex_hull_divide_conquer(points, steps=None, level=0):
    """分治法求凸包"""
    if len(points) <= 3:
        # 基本情況：直接返回所有點構成的凸包
        if len(points) == 1:
            return points
        elif len(points) == 2:
            return points
        else:
            # 三個點的情況
            hull = []
            # 按逆時針順序排列
            center_x = sum(p[0] for p in points) / 3
            center_y = sum(p[1] for p in points) / 3
            points_with_angle = []
            for p in points:
                angle = np.arctan2(p[1] - center_y, p[0] - center_x)
                points_with_angle.append((p, angle))
            points_with_angle.sort(key=lambda x: x[1])
            return [p[0] for p in points_with_angle]
    
    # 按x座標排序
    sorted_points = sorted(points, key=lambda p: (p[0], p[1]))
    
    # 分割
    mid = len(sorted_points) // 2
    left_points = sorted_points[:mid]
    right_points = sorted_points[mid:]
    
    if steps is not None:
        steps.append({
            'type': 'divide',
            'left': left_points,
            'right': right_points,
            'all_points': points,
            'level': level
        })
    
    # 遞歸求解
    left_hull = convex_hull_divide_conquer(left_points, steps, level+1)
    right_hull = convex_hull_divide_conquer(right_points, steps, level+1)
    
    if steps is not None:
        # 收集當前所有已完成的凸包
        all_hulls = []
        for step in steps:
            if step['type'] == 'merge_after' and 'result' in step:
                all_hulls.append(step['result'])
        
        steps.append({
            'type': 'merge_before',
            'left_hull': left_hull,
            'right_hull': right_hull,
            'all_points': points,
            'level': level,
            'all_existing_hulls': all_hulls.copy()
        })
    
    # 合併
    result = merge_hulls(left_hull, right_hull)
    
    if steps is not None:
        # 收集當前所有已完成的凸包（包括剛合併的）
        all_hulls = []
        for step in steps:
            if step['type'] == 'merge_after' and 'result' in step:
                all_hulls.append(step['result'])
        
        steps.append({
            'type': 'merge_after',
            'result': result,
            'all_points': points,
            'level': level,
            'all_existing_hulls': all_hulls.copy()
        })
    
    return result

def plot_convex_hull_step(step, ax):
    """繪製單個步驟"""
    ax.clear()
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 110)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # 確保每個步驟都有層級信息
    level = step.get('level', 0)
    
    if step['type'] == 'divide':
        # 繪製所有點
        all_points = step['all_points']
        left_points = step['left']
        right_points = step['right']
        
        for point in all_points:
            ax.plot(point[0], point[1], 'ko', markersize=6)
        
        # 用不同顏色標記左右部分
        for point in left_points:
            ax.plot(point[0], point[1], 'bo', markersize=8)
        for point in right_points:
            ax.plot(point[0], point[1], 'ro', markersize=8)
            
        ax.set_title(f"分割階段 (層級 {level}): 藍色為左半部，紅色為右半部")
        
    elif step['type'] == 'merge_before':
        # 繪製兩個子凸包
        left_hull = step['left_hull']
        right_hull = step['right_hull']
        
        # 先繪製所有已存在的凸包（半透明灰色）
        if 'all_existing_hulls' in step:
            for existing_hull in step['all_existing_hulls']:
                if len(existing_hull) > 2:
                    existing_polygon = Polygon(existing_hull, fill=True, facecolor='gray', alpha=0.15, edgecolor='gray', linewidth=1)
                    ax.add_patch(existing_polygon)
        
        # 繪製所有點
        for point in step['all_points']:
            ax.plot(point[0], point[1], 'ko', markersize=4)
        
        # 繪製左凸包（帶半透明填充）
        if len(left_hull) > 2:
            left_polygon = Polygon(left_hull, fill=True, facecolor='blue', alpha=0.2, edgecolor='blue', linewidth=2)
            ax.add_patch(left_polygon)
        elif len(left_hull) == 2:
            ax.plot([left_hull[0][0], left_hull[1][0]], 
                   [left_hull[0][1], left_hull[1][1]], 'b-', linewidth=2)
        
        for point in left_hull:
            ax.plot(point[0], point[1], 'bo', markersize=8)
        
        # 繪製右凸包（帶半透明填充）
        if len(right_hull) > 2:
            right_polygon = Polygon(right_hull, fill=True, facecolor='red', alpha=0.2, edgecolor='red', linewidth=2)
            ax.add_patch(right_polygon)
        elif len(right_hull) == 2:
            ax.plot([right_hull[0][0], right_hull[1][0]], 
                   [right_hull[0][1], right_hull[1][1]], 'r-', linewidth=2)
        
        for point in right_hull:
            ax.plot(point[0], point[1], 'ro', markersize=8)
            
        ax.set_title(f"合併前 (層級 {level}): 左凸包（藍）和右凸包（紅），灰色為其他層級凸包")
        
    elif step['type'] == 'merge_after':
        # 繪製合併後的結果
        result = step['result']
        
        # 先繪製所有已存在的凸包（半透明灰色）
        if 'all_existing_hulls' in step:
            for existing_hull in step['all_existing_hulls']:
                if len(existing_hull) > 2:
                    existing_polygon = Polygon(existing_hull, fill=True, facecolor='gray', alpha=0.15, edgecolor='gray', linewidth=1)
                    ax.add_patch(existing_polygon)
        
        # 繪製所有點
        for point in step['all_points']:
            ax.plot(point[0], point[1], 'ko', markersize=4)
        
        # 繪製合併後的凸包（帶半透明填充）
        if len(result) > 2:
            result_polygon = Polygon(result, fill=True, facecolor='green', alpha=0.3, edgecolor='green', linewidth=3)
            ax.add_patch(result_polygon)
        elif len(result) == 2:
            ax.plot([result[0][0], result[1][0]], 
                   [result[0][1], result[1][1]], 'g-', linewidth=3)
        
        for point in result:
            ax.plot(point[0], point[1], 'go', markersize=8)
            
        ax.set_title(f"合併後 (層級 {level}): 新凸包（綠），灰色為其他層級凸包")

def main():
    st.title("分治法凸包演算法視覺化")
    st.markdown("---")
    
    # 側邊欄控制
    st.sidebar.title("控制面板")
    
    # 點數控制
    num_points = st.sidebar.slider("點的數量", 4, 20, 8)
    
    # 生成隨機點按鈕
    if st.sidebar.button("生成新的隨機點"):
        points = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(num_points)]
        st.session_state.points = points
        st.session_state.steps = []
        st.session_state.current_step = 0
    
    # 初始化點集
    if 'points' not in st.session_state:
        points = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(num_points)]
        st.session_state.points = points
        st.session_state.steps = []
        st.session_state.current_step = 0
    
    points = st.session_state.points
    
    # 計算凸包按鈕
    if st.sidebar.button("計算凸包"):
        steps = []
        result = convex_hull_divide_conquer(points.copy(), steps, 0)
        st.session_state.steps = steps
        st.session_state.result = result
        st.session_state.current_step = 0
    
    # 顯示點集信息
    st.sidebar.write(f"當前點集：{len(points)} 個點")
    
    st.write("### 演算法說明")
    st.write("""
    **分治法凸包演算法步驟：**
    
    1. **前處理**：將點集按x座標排序後分成兩半
    2. **Devide**：遞迴求解左右兩部分的凸包
    3. **Conquer**：找到兩個凸包的上下公切線，合併成最終凸包
    
    **時間複雜度：** O(n log n)
    """)
    

    if 'steps' in st.session_state and st.session_state.steps:
        # 步驟控制
        st.write("### 演算法步驟")
        current_step = st.slider("步驟", 0, len(st.session_state.steps)-1, st.session_state.current_step)
        st.session_state.current_step = current_step
        
        # 繪圖
        fig, ax = plt.subplots(figsize=(10, 8))
        if current_step < len(st.session_state.steps):
            plot_convex_hull_step(st.session_state.steps[current_step], ax)
        
        st.pyplot(fig)
        
        # 自動播放
        if st.button("自動播放"):
            placeholder = st.empty()
            for i in range(len(st.session_state.steps)):
                fig, ax = plt.subplots(figsize=(10, 8))
                plot_convex_hull_step(st.session_state.steps[i], ax)
                placeholder.pyplot(fig)
                time.sleep(1.5)
                plt.close(fig)
    else:
        # 顯示初始點集
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(-10, 110)
        ax.set_ylim(-10, 110)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        for point in points:
            ax.plot(point[0], point[1], 'ko', markersize=8)
        
        ax.set_title("初始點集")
        st.pyplot(fig)


    
    
    if 'result' in st.session_state:
        st.write("### 結果")
        st.write(f"凸包頂點數：{len(st.session_state.result)}")
        st.write("凸包頂點座標：")
        for i, point in enumerate(st.session_state.result):
            st.write(f"{i+1}. ({point[0]}, {point[1]})")
    
    # 圖例
    st.markdown("---")
    st.write("### 顏色說明")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("🔵 **藍色**：左半部分")
    with col2:
        st.markdown("🔴 **紅色**：右半部分")
    with col3:
        st.markdown("🟢 **綠色**：新合併凸包")
    with col4:
        st.markdown("⚫ **黑色**：所有點")
    with col5:
        st.markdown("⚪ **灰色**：其他層級凸包")

if __name__ == "__main__":
    main()
