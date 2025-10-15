#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球模拟购买系统
使用PyQt5构建的双色球彩票模拟购买和开奖系统
"""

import sys
import random
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QTextEdit, QTabWidget,
    QGroupBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon


class DoubleColorBallSimulator(QMainWindow):
    """双色球模拟购买系统主窗口"""
    
    def __init__(self):
        super().__init__()
        self.selected_red_balls = set()
        self.selected_blue_ball = None
        self.purchase_history = []
        self.statistics = {
            'total_purchases': 0,
            'total_spent': 0,
            'total_winnings': 0,
            'red_ball_frequency': {i: 0 for i in range(1, 34)},
            'blue_ball_frequency': {i: 0 for i in range(1, 17)}
        }
        self.red_ball_buttons = {}
        self.blue_ball_buttons = {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("双色球模拟购买系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # 创建中央部件和标签页
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_lottery_tab()
        self.create_history_tab()
        self.create_statistics_tab()

    def create_lottery_tab(self):
        """创建选号购买标签页"""
        lottery_widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("双色球选号购买")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #007acc; margin: 10px;")
        layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 选号区域
        self.create_red_ball_selection(scroll_layout)
        self.create_blue_ball_selection(scroll_layout)
        
        # 当前选择显示
        self.selection_display = QLabel("请选择6个红球和1个蓝球")
        self.selection_display.setAlignment(Qt.AlignCenter)
        self.selection_display.setFont(QFont("Arial", 12, QFont.Bold))
        self.selection_display.setStyleSheet("""
            QLabel {
                background-color: #f0f8ff;
                border: 2px solid #007acc;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
        """)
        scroll_layout.addWidget(self.selection_display)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        random_btn = QPushButton("机选")
        random_btn.clicked.connect(self.random_select)
        button_layout.addWidget(random_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_selection)
        button_layout.addWidget(clear_btn)
        
        purchase_btn = QPushButton("购买彩票")
        purchase_btn.clicked.connect(self.purchase_ticket)
        button_layout.addWidget(purchase_btn)
        
        scroll_layout.addLayout(button_layout)
        
        # 开奖模拟区域
        self.create_lottery_simulation(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        lottery_widget.setLayout(layout)
        self.tab_widget.addTab(lottery_widget, "选号购买")

    def create_red_ball_selection(self, parent_layout):
        """创建红球选择区域"""
        red_group = QGroupBox("红球区 (选择6个，范围1-33)")
        red_layout = QGridLayout()
        
        for i in range(1, 34):
            btn = QPushButton(str(i))
            btn.setCheckable(True)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border: 2px solid #ff5252;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #d32f2f;
                    border: 2px solid #b71c1c;
                }
                QPushButton:hover {
                    background-color: #f44336;
                }
            """)
            btn.clicked.connect(lambda checked, num=i: self.select_red_ball(num, checked))
            self.red_ball_buttons[i] = btn
            
            row = (i - 1) // 11
            col = (i - 1) % 11
            red_layout.addWidget(btn, row, col)
        
        red_group.setLayout(red_layout)
        parent_layout.addWidget(red_group)

    def create_blue_ball_selection(self, parent_layout):
        """创建蓝球选择区域"""
        blue_group = QGroupBox("蓝球区 (选择1个，范围1-16)")
        blue_layout = QGridLayout()
        
        for i in range(1, 17):
            btn = QPushButton(str(i))
            btn.setCheckable(True)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: 2px solid #1976d2;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #1565c0;
                    border: 2px solid #0d47a1;
                }
                QPushButton:hover {
                    background-color: #1e88e5;
                }
            """)
            btn.clicked.connect(lambda checked, num=i: self.select_blue_ball(num, checked))
            self.blue_ball_buttons[i] = btn
            
            row = (i - 1) // 8
            col = (i - 1) % 8
            blue_layout.addWidget(btn, row, col)
        
        blue_group.setLayout(blue_layout)
        parent_layout.addWidget(blue_group)

    def create_lottery_simulation(self, parent_layout):
        """创建开奖模拟区域"""
        simulation_group = QGroupBox("开奖模拟")
        simulation_layout = QVBoxLayout()
        
        self.draw_btn = QPushButton("模拟开奖")
        self.draw_btn.setFixedHeight(50)
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.draw_btn.clicked.connect(self.simulate_draw)
        simulation_layout.addWidget(self.draw_btn)
        
        self.draw_result_label = QLabel("点击上方按钮进行模拟开奖")
        self.draw_result_label.setAlignment(Qt.AlignCenter)
        self.draw_result_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.draw_result_label.setStyleSheet("""
            QLabel {
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        simulation_layout.addWidget(self.draw_result_label)
        
        simulation_group.setLayout(simulation_layout)
        parent_layout.addWidget(simulation_group)

    def create_history_tab(self):
        """创建历史记录标签页"""
        history_widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("购买历史记录")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007acc; margin: 10px;")
        layout.addWidget(title_label)
        
        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "购买时间", "选择号码", "开奖号码", "中奖等级", "奖金", "投注金额"
        ])
        
        # 设置表格样式
        self.history_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #007acc;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        # 清空历史按钮
        clear_history_btn = QPushButton("清空历史记录")
        clear_history_btn.clicked.connect(self.clear_history)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        layout.addWidget(clear_history_btn)
        
        history_widget.setLayout(layout)
        self.tab_widget.addTab(history_widget, "历史记录")

    def create_statistics_tab(self):
        """创建统计分析标签页"""
        stats_widget = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("统计分析")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #007acc; margin: 10px;")
        layout.addWidget(title_label)
        
        # 统计信息显示
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        layout.addWidget(self.stats_display)
        
        # 刷新统计按钮
        refresh_stats_btn = QPushButton("刷新统计")
        refresh_stats_btn.clicked.connect(self.update_statistics)
        layout.addWidget(refresh_stats_btn)
        
        stats_widget.setLayout(layout)
        self.tab_widget.addTab(stats_widget, "统计分析")

    def select_red_ball(self, number: int, checked: bool):
        """选择红球"""
        if checked:
            if len(self.selected_red_balls) >= 6:
                # 如果已经选择了6个红球，取消选择
                self.red_ball_buttons[number].setChecked(False)
                QMessageBox.warning(self, "提示", "最多只能选择6个红球！")
                return
            self.selected_red_balls.add(number)
        else:
            self.selected_red_balls.discard(number)
            
        self.update_selection_display()

    def select_blue_ball(self, number: int, checked: bool):
        """选择蓝球"""
        if checked:
            # 取消之前选择的蓝球
            if self.selected_blue_ball:
                self.blue_ball_buttons[self.selected_blue_ball].setChecked(False)
            self.selected_blue_ball = number
        else:
            if self.selected_blue_ball == number:
                self.selected_blue_ball = None
                
        self.update_selection_display()

    def update_selection_display(self):
        """更新选择显示"""
        red_balls = sorted(list(self.selected_red_balls))
        blue_ball = self.selected_blue_ball
        
        if len(red_balls) == 6 and blue_ball:
            red_str = " ".join([f"{num:02d}" for num in red_balls])
            blue_str = f"{blue_ball:02d}"
            self.selection_display.setText(f"红球: {red_str} | 蓝球: {blue_str}")
            self.selection_display.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 2px solid #4caf50;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 10px;
                    color: #2e7d32;
                }
            """)
        else:
            needed_red = 6 - len(red_balls)
            needed_blue = 1 if not blue_ball else 0
            self.selection_display.setText(f"还需选择: {needed_red}个红球, {needed_blue}个蓝球")
            self.selection_display.setStyleSheet("""
                QLabel {
                    background-color: #fff3e0;
                    border: 2px solid #ff9800;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 10px;
                    color: #f57c00;
                }
            """)

    def random_select(self):
        """随机选号（机选）"""
        # 清空当前选择
        self.clear_selection()
        
        # 随机选择6个红球
        red_balls = random.sample(range(1, 34), 6)
        for ball in red_balls:
            self.red_ball_buttons[ball].setChecked(True)
            self.selected_red_balls.add(ball)
        
        # 随机选择1个蓝球
        blue_ball = random.randint(1, 16)
        self.blue_ball_buttons[blue_ball].setChecked(True)
        self.selected_blue_ball = blue_ball
        
        self.update_selection_display()

    def clear_selection(self):
        """清空选择"""
        # 清空红球选择
        for ball in list(self.selected_red_balls):
            self.red_ball_buttons[ball].setChecked(False)
        self.selected_red_balls.clear()
        
        # 清空蓝球选择
        if self.selected_blue_ball:
            self.blue_ball_buttons[self.selected_blue_ball].setChecked(False)
            self.selected_blue_ball = None
            
        self.update_selection_display()

    def purchase_ticket(self):
        """购买彩票"""
        if len(self.selected_red_balls) != 6 or not self.selected_blue_ball:
            QMessageBox.warning(self, "提示", "请选择6个红球和1个蓝球！")
            return
        
        # 记录购买信息
        purchase_info = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'red_balls': sorted(list(self.selected_red_balls)),
            'blue_ball': self.selected_blue_ball,
            'amount': 2.0,  # 每注2元
            'draw_numbers': None,
            'prize_level': None,
            'winnings': 0
        }
        
        self.purchase_history.append(purchase_info)
        self.statistics['total_purchases'] += 1
        self.statistics['total_spent'] += 2.0
        
        # 更新号码频率统计
        for ball in self.selected_red_balls:
            self.statistics['red_ball_frequency'][ball] += 1
        self.statistics['blue_ball_frequency'][self.selected_blue_ball] += 1
        
        # 更新历史记录表格
        self.update_history_table()
        
        # 保存数据
        self.save_data()
        
        QMessageBox.information(self, "购买成功", "彩票购买成功！请到开奖模拟区进行开奖。")
        
        # 清空选择
        self.clear_selection()

    def simulate_draw(self):
        """模拟开奖"""
        if not self.purchase_history:
            QMessageBox.warning(self, "提示", "请先购买彩票！")
            return
        
        # 生成开奖号码
        draw_red_balls = sorted(random.sample(range(1, 34), 6))
        draw_blue_ball = random.randint(1, 16)
        
        # 显示开奖结果
        red_str = " ".join([f"{num:02d}" for num in draw_red_balls])
        blue_str = f"{draw_blue_ball:02d}"
        self.draw_result_label.setText(f"开奖号码 - 红球: {red_str} | 蓝球: {blue_str}")
        
        # 检查所有未开奖的购买记录
        total_winnings = 0
        for purchase in self.purchase_history:
            if purchase['draw_numbers'] is None:  # 未开奖的记录
                purchase['draw_numbers'] = {
                    'red_balls': draw_red_balls,
                    'blue_ball': draw_blue_ball
                }
                
                # 检查中奖情况
                red_matches = len(set(purchase['red_balls']) & set(draw_red_balls))
                blue_matches = 1 if purchase['blue_ball'] == draw_blue_ball else 0
                
                prize_level, winnings = self.check_winning(red_matches, blue_matches)
                purchase['prize_level'] = prize_level
                purchase['winnings'] = winnings
                
                if winnings > 0:
                    total_winnings += winnings
                    self.statistics['total_winnings'] += winnings
        
        # 更新历史记录表格
        self.update_history_table()
        
        # 保存数据
        self.save_data()
        
        if total_winnings > 0:
            QMessageBox.information(self, "中奖了！", f"恭喜中奖！本次中奖金额: {total_winnings:.2f}元")
        else:
            QMessageBox.information(self, "开奖结果", "很遗憾，本次未中奖。")

    def check_winning(self, red_matches: int, blue_matches: int) -> Tuple[str, float]:
        """检查中奖情况"""
        if red_matches == 6 and blue_matches == 1:
            return "一等奖", 5000000.0
        elif red_matches == 6 and blue_matches == 0:
            return "二等奖", 100000.0
        elif red_matches == 5 and blue_matches == 1:
            return "三等奖", 3000.0
        elif (red_matches == 5 and blue_matches == 0) or (red_matches == 4 and blue_matches == 1):
            return "四等奖", 200.0
        elif (red_matches == 4 and blue_matches == 0) or (red_matches == 3 and blue_matches == 1):
            return "五等奖", 10.0
        elif (red_matches == 2 and blue_matches == 1) or (red_matches == 1 and blue_matches == 1) or (red_matches == 0 and blue_matches == 1):
            return "六等奖", 5.0
        else:
            return "未中奖", 0.0

    def update_history_table(self):
        """更新历史记录表格"""
        self.history_table.setRowCount(len(self.purchase_history))
        
        for i, purchase in enumerate(self.purchase_history):
            # 购买时间
            self.history_table.setItem(i, 0, QTableWidgetItem(purchase['time']))
            
            # 选择号码
            red_str = " ".join([f"{num:02d}" for num in purchase['red_balls']])
            blue_str = f"{purchase['blue_ball']:02d}"
            selected_numbers = f"红: {red_str} 蓝: {blue_str}"
            self.history_table.setItem(i, 1, QTableWidgetItem(selected_numbers))
            
            # 开奖号码
            if purchase['draw_numbers']:
                draw_red_str = " ".join([f"{num:02d}" for num in purchase['draw_numbers']['red_balls']])
                draw_blue_str = f"{purchase['draw_numbers']['blue_ball']:02d}"
                draw_numbers = f"红: {draw_red_str} 蓝: {draw_blue_str}"
            else:
                draw_numbers = "未开奖"
            self.history_table.setItem(i, 2, QTableWidgetItem(draw_numbers))
            
            # 中奖等级
            prize_level = purchase['prize_level'] if purchase['prize_level'] else "未开奖"
            self.history_table.setItem(i, 3, QTableWidgetItem(prize_level))
            
            # 奖金
            winnings = f"{purchase['winnings']:.2f}元" if purchase['winnings'] > 0 else "0.00元"
            self.history_table.setItem(i, 4, QTableWidgetItem(winnings))
            
            # 投注金额
            self.history_table.setItem(i, 5, QTableWidgetItem(f"{purchase['amount']:.2f}元"))

    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(self, "确认", "确定要清空所有历史记录吗？", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.purchase_history.clear()
            self.statistics = {
                'total_purchases': 0,
                'total_spent': 0,
                'total_winnings': 0,
                'red_ball_frequency': {i: 0 for i in range(1, 34)},
                'blue_ball_frequency': {i: 0 for i in range(1, 17)}
            }
            self.update_history_table()
            self.update_statistics()
            self.save_data()
            QMessageBox.information(self, "提示", "历史记录已清空！")

    def update_statistics(self):
        """更新统计信息"""
        if not self.purchase_history:
            self.stats_display.setText("暂无购买记录，无法生成统计信息。")
            return
        
        # 计算基本统计
        total_purchases = self.statistics['total_purchases']
        total_spent = self.statistics['total_spent']
        total_winnings = self.statistics['total_winnings']
        net_result = total_winnings - total_spent
        
        stats_text = f"""
=== 购买统计 ===
总购买次数: {total_purchases} 次
总投入金额: {total_spent:.2f} 元
总中奖金额: {total_winnings:.2f} 元
盈亏情况: {net_result:+.2f} 元

=== 红球出现频率 TOP 10 ===
"""
        
        # 红球频率统计
        red_freq = sorted(self.statistics['red_ball_frequency'].items(), 
                         key=lambda x: x[1], reverse=True)[:10]
        for ball, freq in red_freq:
            percentage = (freq / total_purchases * 100) if total_purchases > 0 else 0
            stats_text += f"红球 {ball:02d}: {freq} 次 ({percentage:.1f}%)\n"
        
        stats_text += f"""
=== 蓝球出现频率 TOP 5 ===
"""
        
        # 蓝球频率统计
        blue_freq = sorted(self.statistics['blue_ball_frequency'].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        for ball, freq in blue_freq:
            percentage = (freq / total_purchases * 100) if total_purchases > 0 else 0
            stats_text += f"蓝球 {ball:02d}: {freq} 次 ({percentage:.1f}%)\n"
        
        self.stats_display.setText(stats_text)

    def save_data(self):
        """保存数据到文件"""
        data = {
            'purchase_history': self.purchase_history,
            'statistics': self.statistics
        }
        
        try:
            with open('lottery_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"数据保存失败: {str(e)}")

    def load_data(self):
        """从文件加载数据"""
        try:
            if os.path.exists('lottery_data.json'):
                with open('lottery_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.purchase_history = data.get('purchase_history', [])
                    
                    # 兼容旧数据格式
                    for purchase in self.purchase_history:
                        # 转换旧的字段名
                        if 'winning_numbers' in purchase and 'draw_numbers' not in purchase:
                            purchase['draw_numbers'] = purchase.pop('winning_numbers')
                        if 'cost' in purchase and 'amount' not in purchase:
                            purchase['amount'] = purchase.pop('cost')
                        if 'prize_amount' in purchase and 'winnings' not in purchase:
                            purchase['winnings'] = purchase.pop('prize_amount')
                    
                    # 加载或初始化统计数据
                    if 'statistics' in data:
                        self.statistics = data['statistics']
                    else:
                        # 从旧数据格式转换统计信息
                        self.statistics = {
                            'total_purchases': len(self.purchase_history),
                            'total_spent': data.get('total_spent', 0),
                            'total_winnings': data.get('total_won', 0),
                            'red_ball_frequency': {i: 0 for i in range(1, 34)},
                            'blue_ball_frequency': {i: 0 for i in range(1, 17)}
                        }
                        
                        # 重新计算号码频率
                        for purchase in self.purchase_history:
                            for ball in purchase.get('red_balls', []):
                                if ball in self.statistics['red_ball_frequency']:
                                    self.statistics['red_ball_frequency'][ball] += 1
                            blue_ball = purchase.get('blue_ball')
                            if blue_ball and blue_ball in self.statistics['blue_ball_frequency']:
                                self.statistics['blue_ball_frequency'][blue_ball] += 1
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"数据加载失败: {str(e)}")

    def showEvent(self, event):
        """窗口显示时更新数据"""
        super().showEvent(event)
        self.update_history_table()
        self.update_statistics()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序图标和名称
    app.setApplicationName("双色球模拟购买系统")
    app.setApplicationVersion("1.0")
    
    # 创建主窗口
    window = DoubleColorBallSimulator()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()