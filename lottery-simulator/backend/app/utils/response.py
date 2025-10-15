"""
响应工具模块
提供统一的API响应格式
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> JSONResponse:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
    
    Returns:
        JSONResponse: 统一格式的成功响应
    """
    return JSONResponse(
        status_code=code,
        content={
            "success": True,
            "code": code,
            "message": message,
            "data": data
        }
    )


def error_response(
    message: str = "操作失败",
    code: int = 400,
    data: Optional[Any] = None
) -> JSONResponse:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        data: 错误详情数据
    
    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=code,
        content={
            "success": False,
            "code": code,
            "message": message,
            "data": data
        }
    )


def validation_error_response(errors: list) -> JSONResponse:
    """
    验证错误响应
    
    Args:
        errors: 验证错误列表
    
    Returns:
        JSONResponse: 验证错误响应
    """
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "code": 422,
            "message": "数据验证失败",
            "data": {
                "errors": errors
            }
        }
    )