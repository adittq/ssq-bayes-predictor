#!/usr/bin/env python3
"""
端到端测试脚本
测试前后端集成功能
"""

import requests
import json
import time
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:5173"

class E2ETest:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        
    def test_backend_health(self):
        """测试后端健康检查"""
        print("🔍 测试后端健康检查...")
        try:
            response = requests.get(f"{BACKEND_URL}/../health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务正常")
                return True
            else:
                print(f"❌ 后端健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 后端连接失败: {e}")
            return False
    
    def test_frontend_health(self):
        """测试前端健康检查"""
        print("🔍 测试前端健康检查...")
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
                print("✅ 前端服务正常")
                return True
            else:
                print(f"❌ 前端健康检查失败: {response.status_code}, content-type: {response.headers.get('content-type', 'unknown')}")
                return False
        except Exception as e:
            print(f"❌ 前端连接失败: {e}")
            return False
    
    def test_user_workflow(self):
        """测试用户完整工作流程"""
        print("🔍 测试用户工作流程...")
        
        # 1. 用户登录
        login_data = {
            "username": "testuser6",
            "password": "123456"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.user_token = data.get("data", {}).get("access_token")
                    print("✅ 用户登录成功")
                    
                    # 设置认证头
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.user_token}"
                    })
                    
                    return True
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_lottery_features(self):
        """测试彩票功能"""
        print("🔍 测试彩票功能...")
        
        # 测试获取当前期号
        try:
            response = self.session.get(f"{BACKEND_URL}/lottery/current-period")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ 获取当前期号成功")
                else:
                    print(f"❌ 获取当前期号失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 获取当前期号请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取当前期号异常: {e}")
            return False
        
        # 测试机选号码
        try:
            response = self.session.post(f"{BACKEND_URL}/lottery/quick-pick?count=1")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    picks = data.get("data", {}).get("picks", [])
                    if picks:
                        print(f"✅ 机选号码成功: {picks[0]}")
                    else:
                        print("✅ 机选号码成功（无号码返回）")
                else:
                    print(f"❌ 机选号码失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 机选号码请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 机选号码异常: {e}")
            return False
        
        return True
    
    def test_analysis_features(self):
        """测试分析功能"""
        print("🔍 测试分析功能...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/analysis/recommendations?model_type=frequency&count=3")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    recommendations = data.get("data", {}).get("recommendations", [])
                    print(f"✅ 获取分析推荐成功: {len(recommendations)} 条推荐")
                else:
                    print(f"❌ 获取分析推荐失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 获取分析推荐请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取分析推荐异常: {e}")
            return False
        
        return True
    
    def run_all_tests(self):
        """运行所有端到端测试"""
        print("🚀 开始端到端测试...")
        print("=" * 50)
        
        tests = [
            ("后端健康检查", self.test_backend_health),
            ("前端健康检查", self.test_frontend_health),
            ("用户工作流程", self.test_user_workflow),
            ("彩票功能", self.test_lottery_features),
            ("分析功能", self.test_analysis_features),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}...")
            if test_func():
                passed += 1
            print("-" * 30)
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有端到端测试通过！")
            print("✅ 系统集成测试完成，前后端功能正常")
            return True
        else:
            print("⚠️ 部分测试失败，请检查相关功能")
            print("❌ 端到端测试发现问题，请检查系统集成")
            return False

def main():
    """主函数"""
    tester = E2ETest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 端到端测试总结:")
        print("• 前端服务器运行正常")
        print("• 后端API服务正常")
        print("• 用户认证功能正常")
        print("• 彩票核心功能正常")
        print("• 数据分析功能正常")
        print("• 前后端集成正常")
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())