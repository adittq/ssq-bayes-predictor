"""
用户认证相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import UserRegister, UpdateProfile, ChangePassword
from app.utils.response import success_response, error_response

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@router.post("/login", summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    用户登录接口
    支持微信和支付宝登录模拟
    """
    try:
        auth_service = AuthService(db)
        
        # 验证用户凭据
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成访问令牌
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # 生成刷新令牌
        refresh_token = auth_service.create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "login_type": user.login_type,
                    "avatar": user.avatar
                }
            },
            message="登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"登录失败: {str(e)}")


@router.post("/token", summary="OAuth2 获取令牌")
async def issue_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    OAuth2 标准令牌端点
    - 输入: 表单 `username` 和 `password`
    - 输出: 标准OAuth2响应，仅包含 `access_token` 与 `token_type`
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", summary="用户注册")
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    用户注册接口
    """
    try:
        auth_service = AuthService(db)
        
        # 检查用户是否已存在
        if auth_service.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 创建新用户
        user = auth_service.create_user(
            username=user_data.username,
            password=user_data.password,
            nickname=user_data.nickname or user_data.username,
            login_type="username"  # 默认使用用户名登录
        )
        
        return success_response(
            data={
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "login_type": user.login_type
                }
            },
            message="注册成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"注册失败: {str(e)}")


@router.post("/wechat-login", summary="微信登录")
async def wechat_login(
    code: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    微信登录模拟接口
    """
    try:
        auth_service = AuthService(db)
        
        # 模拟微信登录逻辑
        # 在实际项目中，这里会调用微信API获取用户信息
        mock_wechat_user = {
            "openid": f"wx_{code}",
            "nickname": f"微信用户_{code[:6]}",
            "avatar": "https://example.com/avatar.jpg"
        }
        
        # 查找或创建用户
        user = auth_service.get_user_by_username(mock_wechat_user["openid"])
        if not user:
            user = auth_service.create_user(
                username=mock_wechat_user["openid"],
                password="",  # 第三方登录不需要密码
                nickname=mock_wechat_user["nickname"],
                login_type="wechat",
                avatar=mock_wechat_user["avatar"]
            )
        
        # 生成令牌
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "login_type": user.login_type,
                    "avatar": user.avatar
                }
            },
            message="微信登录成功"
        )
        
    except Exception as e:
        return error_response(message=f"微信登录失败: {str(e)}")


@router.post("/alipay-login", summary="支付宝登录")
async def alipay_login(
    auth_code: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    支付宝登录模拟接口
    """
    try:
        auth_service = AuthService(db)
        
        # 模拟支付宝登录逻辑
        mock_alipay_user = {
            "user_id": f"alipay_{auth_code}",
            "nick_name": f"支付宝用户_{auth_code[:6]}",
            "avatar": "https://example.com/avatar.jpg"
        }
        
        # 查找或创建用户
        user = auth_service.get_user_by_username(mock_alipay_user["user_id"])
        if not user:
            user = auth_service.create_user(
                username=mock_alipay_user["user_id"],
                password="",  # 第三方登录不需要密码
                nickname=mock_alipay_user["nick_name"],
                login_type="alipay",
                avatar=mock_alipay_user["avatar"]
            )
        
        # 生成令牌
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "login_type": user.login_type,
                    "avatar": user.avatar
                }
            },
            message="支付宝登录成功"
        )
        
    except Exception as e:
        return error_response(message=f"支付宝登录失败: {str(e)}")


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    刷新访问令牌
    """
    try:
        auth_service = AuthService(db)
        
        # 验证刷新令牌
        payload = auth_service.verify_token(refresh_token)
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 获取用户信息
        user = auth_service.get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        # 生成新的访问令牌
        new_access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return success_response(
            data={
                "access_token": new_access_token,
                "token_type": "bearer"
            },
            message="令牌刷新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"令牌刷新失败: {str(e)}")


@router.get("/profile", summary="获取用户信息")
async def get_profile(
    current_user: User = Depends(AuthService.get_current_user)
) -> Dict[str, Any]:
    """
    获取当前用户信息
    """
    try:
        return success_response(
            data={
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "nickname": current_user.nickname,
                    "login_type": current_user.login_type,
                    "avatar": current_user.avatar,
                    "created_at": current_user.created_at.isoformat(),
                    "last_login": current_user.last_login.isoformat() if current_user.last_login else None
                }
            },
            message="获取用户信息成功"
        )
        
    except Exception as e:
        return error_response(message=f"获取用户信息失败: {str(e)}")


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(AuthService.get_current_user)
) -> Dict[str, Any]:
    """
    用户登出接口
    """
    try:
        # 在实际项目中，这里可以将token加入黑名单
        return success_response(message="登出成功")
        
    except Exception as e:
        return error_response(message=f"登出失败: {str(e)}")


@router.put("/profile", summary="更新用户资料")
async def update_profile(
    profile_data: UpdateProfile,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    更新用户资料接口
    """
    try:
        auth_service = AuthService(db)
        
        # 更新用户资料
        updated_user = auth_service.update_user_profile(
            user_id=current_user.id,
            profile_data=profile_data.dict(exclude_unset=True)
        )
        
        return success_response(
            data={
                "user": {
                    "id": updated_user.id,
                    "username": updated_user.username,
                    "nickname": updated_user.nickname,
                    "avatar": updated_user.avatar,
                    "phone": updated_user.phone,
                    "email": updated_user.email,
                    "login_type": updated_user.login_type
                }
            },
            message="用户资料更新成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"用户资料更新失败: {str(e)}")


@router.put("/password", summary="修改密码")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    修改密码接口
    """
    try:
        auth_service = AuthService(db)
        
        # 修改密码
        auth_service.change_password(
            user_id=current_user.id,
            old_password=password_data.old_password,
            new_password=password_data.new_password
        )
        
        return success_response(message="密码修改成功")
        
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"密码修改失败: {str(e)}")