"""
认证相关的 Pydantic 模型
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str
    login_type: str = "username"  # username, wechat, alipay
    
    @validator('login_type')
    def validate_login_type(cls, v):
        if v not in ['username', 'wechat', 'alipay']:
            raise ValueError('登录类型必须是 username, wechat 或 alipay')
        return v


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20个字符之间')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6个字符')
        return v


class ThirdPartyLogin(BaseModel):
    """第三方登录请求"""
    login_type: str  # wechat, alipay
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    
    @validator('login_type')
    def validate_login_type(cls, v):
        if v not in ['wechat', 'alipay']:
            raise ValueError('登录类型必须是 wechat 或 alipay')
        return v


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class UserProfile(BaseModel):
    """用户资料"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    login_type: str
    is_active: bool
    is_verified: bool
    real_name: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateProfile(BaseModel):
    """更新用户资料请求"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ChangePassword(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度至少6个字符')
        return v


class ResetPassword(BaseModel):
    """重置密码请求"""
    username: str
    verification_code: str
    new_password: str