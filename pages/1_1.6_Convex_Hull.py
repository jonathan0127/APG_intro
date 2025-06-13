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
            'all_existing_hulls': all_hulls.copy(),
            'final_hull_this_level': True  # 標記這是這個層級的最終凸包
        })
    
    return result

def graham_scan(points, steps=None):
    """Graham's scan 演算法求凸包"""
    if len(points) < 3:
        return points
    
    # 找到最下方的點（y最小，若相同則x最小）
    start_point = min(points, key=lambda p: (p[1], p[0]))
    
    if steps is not None:
        steps.append({
            'type': 'find_start',
            'start_point': start_point,
            'all_points': points
        })
    
    # 計算其他點相對於起始點的極角
    def polar_angle(p):
        dx = p[0] - start_point[0]
        dy = p[1] - start_point[1]
        return np.arctan2(dy, dx)
    
    # 按極角排序（相同極角時距離近的在前）
    other_points = [p for p in points if p != start_point]
    sorted_points = sorted(other_points, key=lambda p: (polar_angle(p), distance(start_point, p)))
    
    if steps is not None:
        steps.append({
            'type': 'sort_by_angle',
            'start_point': start_point,
            'sorted_points': sorted_points,
            'all_points': points
        })
    
    # Graham scan 主要過程
    hull = [start_point]
    
    for point in sorted_points:
        # 移除形成右轉的點
        while len(hull) > 1 and orientation(hull[-2], hull[-1], point) != 2:
            removed = hull.pop()
            if steps is not None:
                steps.append({
                    'type': 'remove_point',
                    'hull': hull.copy(),
                    'removed_point': removed,
                    'current_point': point,
                    'all_points': points
                })
        
        hull.append(point)
        if steps is not None:
            steps.append({
                'type': 'add_point',
                'hull': hull.copy(),
                'added_point': point,
                'all_points': points
            })
    
    return hull

def plot_convex_hull_step(step, ax):
    """繪製單個步驟"""
    ax.clear()
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 110)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # 確保每個步驟都有層級信息
    level = step.get('level', 0)
    
    # 添加遞迴層級指示器
    ax.text(5, 105, f"Recursion Level: {level}", fontsize=12, 
            bbox=dict(facecolor='yellow', alpha=0.3))
    
    if step['type'] == 'divide':
        # 繪製所有點 - 先劃分當前處理的點和非當前處理的點
        all_points = step['all_points']
        left_points = step['left']
        right_points = step['right']
        
        # 取得所有點，包括不在當前步驟中的點
        # 首先取得原始完整點集
        original_points = []
        if 'original_points' in st.session_state:
            original_points = st.session_state.original_points
        else:
            # 如果找不到原始點集，嘗試從第一個步驟獲取
            for original_step in st.session_state.steps:
                if original_step['type'] == 'divide' and original_step['level'] == 0:
                    original_points = original_step['all_points']
                    break
        
        # 將當前處理的點轉換為集合，便於快速查找
        current_points_set = set()
        for p in all_points:
            current_points_set.add(tuple(p))
        
        # 先繪製所有非當前處理的點（淺灰色，小尺寸）
        for point in original_points:
            if tuple(point) not in current_points_set:
                ax.plot(point[0], point[1], 'o', color='lightgray', alpha=0.3, markersize=3)
        
        # 取得當前遞迴層級中不被直接處理的點
        current_processing_points = left_points + right_points
        other_points_in_current = [p for p in all_points if p not in current_processing_points]
        
        # 繪製當前層級但不在直接處理範圍的點（灰色，較小）
        for point in other_points_in_current:
            ax.plot(point[0], point[1], 'o', color='gray', alpha=0.5, markersize=4)
        
        # 然後繪製當前正在處理的所有點（黑色，較大）
        for point in current_processing_points:
            ax.plot(point[0], point[1], 'ko', markersize=6, alpha=0.7)
        
        # 用不同顏色標記左右部分
        for point in left_points:
            ax.plot(point[0], point[1], 'bo', markersize=8)
        for point in right_points:
            ax.plot(point[0], point[1], 'ro', markersize=8)
        
        # 添加邊框標示當前處理範圍
        if len(current_processing_points) > 2:
            # 找出當前處理範圍的邊界
            min_x = min(p[0] for p in current_processing_points)
            max_x = max(p[0] for p in current_processing_points)
            min_y = min(p[1] for p in current_processing_points)
            max_y = max(p[1] for p in current_processing_points)
            
            # 添加虛線框
            padding = 5
            ax.plot([min_x-padding, max_x+padding, max_x+padding, min_x-padding, min_x-padding],
                    [min_y-padding, min_y-padding, max_y+padding, max_y+padding, min_y-padding],
                    'k--', alpha=0.5, linewidth=1)
            
        ax.set_title(f"Division Phase (Level {level}): Recursing Down", fontsize=14)
        
        # 添加說明
        ax.text(5, 95, "Recursion Down: Breaking problem into smaller subproblems", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        ax.text(5, 90, "Light gray points: Points from other recursion levels", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        # 添加圖例說明
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgray', alpha=0.3, markersize=6, label='Other level points'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', alpha=0.5, markersize=6, label='Current level non-processed'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Left half'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Right half')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
    elif step['type'] == 'merge_before':
        # 繪製兩個子凸包
        left_hull = step['left_hull']
        right_hull = step['right_hull']
        all_points = step['all_points']
        
        # 確保繪製所有點，包括不在當前處理範圍的點
        # 首先取得原始點集
        original_points = []
        for original_step in st.session_state.steps:
            if original_step['type'] == 'divide' and original_step['level'] == 0:
                original_points = original_step['all_points']
                break
        
        # 取得當前正在處理的點和其他點
        current_hull_points = set()
        for p in left_hull + right_hull:
            current_hull_points.add(tuple(p))  # 將點轉為元組以便使用set
        
        # 繪製非當前處理的點（灰色，較小）
        for point in original_points:
            if tuple(point) not in current_hull_points and point not in all_points:
                ax.plot(point[0], point[1], 'o', color='lightgray', alpha=0.4, markersize=3)
        
        # 繪製遞迴層級結構
        recursion_levels = {}
        if 'all_existing_hulls' in step:
            for i, existing_hull in enumerate(step['all_existing_hulls']):
                # 根據大小猜測遞迴層級
                hull_size = len(existing_hull)
                if hull_size not in recursion_levels:
                    recursion_levels[hull_size] = []
                recursion_levels[hull_size].append(existing_hull)
        
        # 先繪製所有已存在的凸包（半透明灰色）
        if 'all_existing_hulls' in step:
            for i, existing_hull in enumerate(step['all_existing_hulls']):
                if len(existing_hull) > 2:
                    alpha_value = 0.1 + 0.05 * (i % 3)  # 不同透明度
                    existing_polygon = Polygon(existing_hull, fill=True, 
                                              facecolor='gray', alpha=alpha_value, 
                                              edgecolor='gray', linewidth=1)
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
            
        ax.set_title(f"Before Merge (Level {level}): Preparing to Process Subproblem Results", fontsize=14)
        
        # 添加解釋說明
        ax.text(5, 95, "Results from subproblems: Preparing to merge left and right hulls", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        ax.text(5, 90, "Gray outlines: Hulls from other recursion levels", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
    elif step['type'] == 'merge_after':
        # 繪製合併後的結果
        result = step['result']
        all_points = step['all_points']
        
        # 確保繪製所有點，包括不在當前處理範圍的點
        # 首先取得原始點集
        original_points = []
        for original_step in st.session_state.steps:
            if original_step['type'] == 'divide' and original_step['level'] == 0:
                original_points = original_step['all_points']
                break
        
        # 取得當前正在處理的點和其他點
        current_hull_points = set(tuple(p) for p in result)
        
        # 繪製非當前處理的點（灰色，較小）
        for point in original_points:
            if tuple(point) not in current_hull_points and point not in all_points:
                ax.plot(point[0], point[1], 'o', color='lightgray', alpha=0.4, markersize=3)
        
        # 添加遞迴層級視覺化
        max_hulls = 5  # 最多顯示的其他凸包數量
        
        # 保存當前步驟的索引，用於查找之前完成的凸包
        current_step_index = -1
        for i, s in enumerate(st.session_state.steps):
            if s == step:
                current_step_index = i
                break
        
        # 查找之前所有已完成的凸包，按層級和完成順序排序
        previous_hulls = []
        if current_step_index >= 0:
            for i in range(current_step_index):
                prev_step = st.session_state.steps[i]
                if prev_step['type'] == 'merge_after' and 'result' in prev_step:
                    # 不同層級的凸包用不同顏色顯示
                    previous_hulls.append({
                        'hull': prev_step['result'],
                        'level': prev_step.get('level', 0),
                        'final': prev_step.get('final_hull_this_level', False)
                    })
        
        # 先繪製所有已存在的凸包（半透明灰色）
        if 'all_existing_hulls' in step:
            existing_hulls = step['all_existing_hulls']
            # 限制顯示數量，避免過多
            if len(existing_hulls) > max_hulls:
                existing_hulls = existing_hulls[-max_hulls:]
                
            for i, existing_hull in enumerate(existing_hulls):
                if len(existing_hull) > 2:
                    # 根據大小設置不同顏色和透明度，暗示不同的遞迴層級
                    hull_size = len(existing_hull)
                    alpha_value = 0.1 + 0.05 * (i % 3)
                    existing_polygon = Polygon(existing_hull, fill=True, 
                                              facecolor='gray', alpha=alpha_value, 
                                              edgecolor='gray', linewidth=1)
                    ax.add_patch(existing_polygon)
        
        # 繪製之前完成的凸包，特別是較高層級的最終結果
        for prev_hull_info in previous_hulls:
            prev_hull = prev_hull_info['hull']
            prev_level = prev_hull_info['level']
            is_final = prev_hull_info['final']
            
            # 只顯示較高層級的最終結果
            if prev_level < level and is_final and len(prev_hull) > 2:
                alpha_value = 0.2
                # 使用淺綠色標記之前層級的最終結果
                prev_polygon = Polygon(prev_hull, fill=True, 
                                      facecolor='lightgreen', alpha=alpha_value, 
                                      edgecolor='lightgreen', linewidth=1.5)
                ax.add_patch(prev_polygon)
        
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
            
        # 添加回朔標記，表示從子問題返回
        if level > 0:  # 只有非根層級才顯示回朔標記
            ax.text(50, 50, "↑", fontsize=30, color='purple', alpha=0.7,
                   ha='center', va='center')
            
        ax.set_title(f"After Merge (Level {level}): Backtracking to Upper Level", fontsize=14)
        
        # 添加解釋說明
        if level == 0:
            ax.text(5, 95, "Recursion Base: All backtracking complete, final hull obtained", 
                    fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        else:
            ax.text(5, 95, f"Backtracking: Result will return to level {level-1}", 
                    fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        ax.text(5, 90, "Green: Current level merged result  Gray: Other level hulls", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        # 簡單的遞迴層級指示圖
        recursion_indicator = "→" * level + "●" + "←" * level
        ax.text(50, 85, recursion_indicator, fontsize=12, ha='center',
               bbox=dict(facecolor='lightyellow', alpha=0.5))

def plot_graham_scan_step(step, ax):
    """繪製 Graham scan 步驟"""
    ax.clear()
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 110)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    all_points = step['all_points']
    
    if step['type'] == 'find_start':
        # 顯示找到的起始點
        start_point = step['start_point']
        
        for point in all_points:
            if point == start_point:
                ax.plot(point[0], point[1], 'ro', markersize=12, label='Start Point')
            else:
                ax.plot(point[0], point[1], 'ko', markersize=8)
        
        ax.set_title("Graham Scan: Finding the Starting Point (Lowest Point)")
        ax.legend()
        
    elif step['type'] == 'sort_by_angle':
        # 顯示按極角排序後的結果
        start_point = step['start_point']
        sorted_points = step['sorted_points']
        
        # 繪製起始點
        ax.plot(start_point[0], start_point[1], 'ro', markersize=12, label='Start Point')
        
        # 繪製排序後的點並標上順序
        for i, point in enumerate(sorted_points):
            ax.plot(point[0], point[1], 'bo', markersize=8)
            ax.annotate(str(i+1), (point[0], point[1]), xytext=(5, 5), 
                       textcoords='offset points', fontsize=10, color='blue')
        
        # 繪製從起始點到各點的射線
        for point in sorted_points:
            ax.plot([start_point[0], point[0]], [start_point[1], point[1]], 
                   'b--', alpha=0.5, linewidth=1)
        
        ax.set_title("Graham Scan: Sorting Points by Polar Angle (Blue Numbers Show Order)")
        ax.legend()
        
    elif step['type'] == 'remove_point':
        # 顯示移除點的過程
        hull = step['hull']
        removed_point = step['removed_point']
        current_point = step['current_point']
        
        # 繪製所有點
        for point in all_points:
            if point in hull:
                ax.plot(point[0], point[1], 'go', markersize=8)
            elif point == removed_point:
                ax.plot(point[0], point[1], 'rx', markersize=12, markeredgewidth=3, label='Removed')
            elif point == current_point:
                ax.plot(point[0], point[1], 'bo', markersize=10, label='Current')
            else:
                ax.plot(point[0], point[1], 'ko', markersize=6)
        
        # 繪製當前凸包
        if len(hull) > 1:
            hull_polygon = Polygon(hull + [current_point], fill=False, edgecolor='red', 
                                 linewidth=2, linestyle='--', alpha=0.7)
            ax.add_patch(hull_polygon)
        
        ax.set_title(f"Graham Scan: Removing Point {removed_point} (Forms Right Turn)")
        ax.legend()
        
    elif step['type'] == 'add_point':
        # 顯示添加點的過程
        hull = step['hull']
        added_point = step['added_point']
        
        # 繪製所有點
        for point in all_points:
            if point in hull:
                if point == added_point:
                    ax.plot(point[0], point[1], 'go', markersize=12, label='Just Added')
                else:
                    ax.plot(point[0], point[1], 'go', markersize=8)
            else:
                ax.plot(point[0], point[1], 'ko', markersize=6)
        
        # 繪製當前凸包
        if len(hull) > 2:
            hull_polygon = Polygon(hull, fill=True, facecolor='green', alpha=0.3, 
                                 edgecolor='green', linewidth=2)
            ax.add_patch(hull_polygon)
        elif len(hull) == 2:
            ax.plot([hull[0][0], hull[1][0]], [hull[0][1], hull[1][1]], 
                   'g-', linewidth=2)
        
        ax.set_title(f"Graham Scan: Adding Point {added_point} to Hull")
        ax.legend()

def main():
    st.title("凸包演算法視覺化")
    st.markdown("---")
    
    # 側邊欄控制
    st.sidebar.title("控制面板")
    
    # 演算法選擇
    algorithm = st.sidebar.selectbox("選擇演算法", ["分治法 (Divide & Conquer)", "Graham's Scan"], index=0)
    
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
        if algorithm == "分治法 (Divide & Conquer)":
            # 儲存原始點集到session_state，確保所有步驟都能訪問
            st.session_state.original_points = points.copy()
            result = convex_hull_divide_conquer(points.copy(), steps, 0)
        else:  # Graham's Scan
            st.session_state.original_points = points.copy()
            result = graham_scan(points.copy(), steps)
        
        st.session_state.steps = steps
        st.session_state.result = result
        st.session_state.current_step = 0
        st.session_state.algorithm = algorithm
    
    # 顯示點集信息
    st.sidebar.write(f"當前點集：{len(points)} 個點")
    st.sidebar.write(f"選擇的演算法：{algorithm}")
    
    # 演算法說明
    if algorithm == "分治法 (Divide & Conquer)":
        st.write("### 分治法凸包演算法說明")
        st.write("""
        **分治法凸包演算法步驟：**
        
        1. **前處理**：將點集按x座標排序後分成兩半
        2. **Divide**：遞迴求解左右兩部分的凸包
        3. **Conquer**：找到兩個凸包的上下公切線，合併成最終凸包
        
        **時間複雜度：** O(n log n)
        
        **遞迴與回朔的概念：**
        - **遞迴向下**：問題不斷被分解為更小的子問題，直到基本情況（點數≤3）
        - **回朔向上**：從基本情況開始，逐步合併子問題的解，最終得到完整解
        - **層級結構**：每個遞迴層級處理特定大小的子問題，灰色輪廓顯示其他層級
        """)
    else:
        st.write("### Graham's Scan 演算法說明")
        st.write("""
        **Graham's Scan 演算法步驟：**
        
        1. **找起始點**：找到y座標最小的點（若有多個則選x座標最小的）
        2. **極角排序**：將其他點按相對於起始點的極角排序
        3. **掃描過程**：依序處理每個點：
           - 如果當前點與凸包形成左轉，加入凸包
           - 如果形成右轉，移除凸包頂部的點直到形成左轉
        
        **時間複雜度：** O(n log n)（主要來自排序）
        """)

    if 'steps' in st.session_state and st.session_state.steps:
        # 步驟控制
        st.write("### 演算法步驟")
        current_step = st.slider("步驟", 0, len(st.session_state.steps)-1, st.session_state.current_step)
        st.session_state.current_step = current_step
        
        # 繪圖
        fig, ax = plt.subplots(figsize=(10, 8))
        if current_step < len(st.session_state.steps):
            if st.session_state.get('algorithm', '').startswith("Graham"):
                plot_graham_scan_step(st.session_state.steps[current_step], ax)
            else:
                plot_convex_hull_step(st.session_state.steps[current_step], ax)
        
        st.pyplot(fig)
        
        # 自動播放
        if st.button("自動播放"):
            placeholder = st.empty()
            for i in range(len(st.session_state.steps)):
                fig, ax = plt.subplots(figsize=(10, 8))
                if st.session_state.get('algorithm', '').startswith("Graham"):
                    plot_graham_scan_step(st.session_state.steps[i], ax)
                else:
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
    if algorithm == "分治法 (Divide & Conquer)":
        st.write("### Color Legend (Divide & Conquer)")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown("🔵 **Blue**: Left half")
        with col2:
            st.markdown("🔴 **Red**: Right half")
        with col3:
            st.markdown("🟢 **Green**: Newly merged hull")
        with col4:
            st.markdown("⚫ **Black**: All points")
        with col5:
            st.markdown("⚪ **Gray**: Other level hulls")
            
        # 添加遞迴與回朔說明
        st.write("### Recursion & Backtracking Indicators")
        st.markdown("""
        - **Yellow box**: Shows current recursion level (level 0 is top level)
        - **Purple arrow**: Indicates backtracking, returning from subproblems to parent
        - **Text descriptions**: Each step provides explanations of recursion and backtracking
        - **Level indicator**: Bottom "→●←" shows position in recursion tree
        """)
    else:
        st.write("### Color Legend (Graham's Scan)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🔴 **Red**: Starting point")
        with col2:
            st.markdown("🔵 **Blue**: Current processing point")
        with col3:
            st.markdown("🟢 **Green**: Points in hull")
        with col4:
            st.markdown("❌ **Red X**: Removed points")


if __name__ == "__main__":
    main()
