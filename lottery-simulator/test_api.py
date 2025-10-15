#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 验证后端API功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "password": "123456",
    "nickname": "测试用户"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        try:
            response = self.session.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ 健康检查通过")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_register(self):
        """测试用户注册"""
        print("🔍 测试用户注册...")
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                params={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"],
                    "nickname": TEST_USER["nickname"]
                }
            )
            if response.status_code in [200, 201]:
                print("✅ 用户注册成功")
                return True
            elif response.status_code == 400:
                data = response.json()
                if "已存在" in data.get("detail", ""):
                    print("ℹ️ 用户已存在，跳过注册")
                    return True
                else:
                    print(f"❌ 注册失败: {data}")
                    return False
            else:
                print(f"❌ 注册失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 注册异常: {e}")
            return False
    
    def test_login(self):
        """测试用户登录"""
        print("🔍 测试用户登录...")
        try:
            # 使用表单数据而不是JSON
            login_data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data["data"]["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    print("✅ 用户登录成功")
                    return True
            
            print(f"❌ 登录失败: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   错误详情: {error_data}")
                except:
                    print(f"   响应内容: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_get_profile(self):
        """测试获取用户信息"""
        print("🔍 测试获取用户信息...")
        try:
            response = self.session.get(f"{BASE_URL}/auth/profile")
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id")
                print(f"✅ 获取用户信息成功: {data.get('username')}")
                return True
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return False
    
    def test_account_balance(self):
        """测试获取账户余额"""
        print("🔍 测试获取账户余额...")
        try:
            response = self.session.get(f"{BASE_URL}/account/balance")
            if response.status_code == 200:
                data = response.json()
                balance = data.get("balance", 0)
                print(f"✅ 获取账户余额成功: ¥{balance}")
                return True
            else:
                print(f"❌ 获取账户余额失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取账户余额异常: {e}")
            return False
    
    def test_lottery_results(self):
        """测试获取开奖结果"""
        print("🔍 测试获取开奖结果...")
        try:
            response = self.session.get(f"{BASE_URL}/lottery/history?page=1&size=5")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    history_data = data.get("data", {})
                    results = history_data.get("items", [])
                    print(f"✅ 获取开奖结果成功: {len(results)} 条记录")
                    return True
                else:
                    print(f"❌ 获取开奖结果失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 获取开奖结果失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取开奖结果异常: {e}")
            return False
    
    def test_purchase_history(self):
        """测试获取购买历史"""
        print("🔍 测试获取购买历史...")
        try:
            response = self.session.get(f"{BASE_URL}/lottery/my-purchases?page=1&size=10")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    purchase_data = data.get("data", {})
                    purchases = purchase_data.get("items", [])
                    print(f"✅ 获取购买历史成功: {len(purchases)} 条记录")
                    return True
                else:
                    print(f"❌ 获取购买历史失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 获取购买历史失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取购买历史异常: {e}")
            return False
    
    def test_analysis_recommendations(self):
        """测试获取分析推荐"""
        print("🔍 测试获取分析推荐...")
        try:
            response = self.session.get(f"{BASE_URL}/analysis/recommendations?model_type=frequency&count=5")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    rec_data = data.get("data", {})
                    recommendations = rec_data.get("recommendations", [])
                    print(f"✅ 获取分析推荐成功: {len(recommendations)} 条推荐")
                    return True
                else:
                    print(f"❌ 获取分析推荐失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 获取分析推荐失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取分析推荐异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始API测试...")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_register,
            self.test_login,
            self.test_get_profile,
            self.test_account_balance,
            self.test_lottery_results,
            self.test_purchase_history,
            self.test_analysis_recommendations,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print("-" * 30)
        
        print("=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查相关功能")
        
        return passed == total

def main():
    """主函数"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ API测试完成，所有功能正常")
    else:
        print("\n❌ API测试发现问题，请检查后端服务")

if __name__ == "__main__":
    main()