#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新文件创建功能的脚本
"""

import os
import sys
from ssq_data_updater import SSQDataUpdater

def test_new_file_creation():
    """测试文件不存在时创建新文件的功能"""
    
    # 使用一个测试文件名
    test_file = 'ssq_data_test.csv'
    
    print(f"测试文件: {test_file}")
    
    # 确保测试文件不存在
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"已删除现有的测试文件: {test_file}")
    
    # 创建更新器实例
    updater = SSQDataUpdater(target_file=test_file)
    
    print("开始测试新文件创建功能...")
    
    # 执行更新
    success = updater.update_data()
    
    if success:
        print("✅ 测试成功！新文件创建功能正常工作")
        
        # 检查文件是否存在
        if os.path.exists(test_file):
            print(f"✅ 文件 {test_file} 已成功创建")
            
            # 显示文件大小
            file_size = os.path.getsize(test_file)
            print(f"文件大小: {file_size} 字节")
            
            # 读取前几行查看内容
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"文件总行数: {len(lines)}")
                    print("前5行内容:")
                    for i, line in enumerate(lines[:5]):
                        print(f"  {i+1}: {line.strip()}")
            except Exception as e:
                print(f"读取文件内容时出错: {e}")
        else:
            print(f"❌ 文件 {test_file} 未创建")
    else:
        print("❌ 测试失败！新文件创建功能存在问题")
    
    # 清理测试文件
    if os.path.exists(test_file):
        try:
            os.remove(test_file)
            print(f"已清理测试文件: {test_file}")
        except Exception as e:
            print(f"清理测试文件时出错: {e}")

if __name__ == "__main__":
    test_new_file_creation()