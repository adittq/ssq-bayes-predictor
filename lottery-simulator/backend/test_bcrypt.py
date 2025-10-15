#!/usr/bin/env python3
"""测试bcrypt密码哈希"""

from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_hash():
    """测试密码哈希功能"""
    test_passwords = ["123456", "test", "a", "password"]
    
    for password in test_passwords:
        print(f"Testing password: '{password}' (length: {len(password)} chars, {len(password.encode('utf-8'))} bytes)")
        try:
            # 尝试哈希密码
            hashed = pwd_context.hash(password)
            print(f"  Hash successful: {hashed[:50]}...")
            
            # 验证密码
            verified = pwd_context.verify(password, hashed)
            print(f"  Verification: {verified}")
            
        except Exception as e:
            print(f"  Error: {e}")
        print()

if __name__ == "__main__":
    test_password_hash()