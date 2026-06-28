"""
领域异常定义
文档 5.3: 失败策略
"""


class DomainException(Exception):
    """领域基础异常"""

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        super().__init__(message)


class PermissionDeniedException(DomainException):
    """
    权限拒绝 - 不可重试
    文档 5.3: 权限失败 -> 立即终止，不重试
    """

    pass


class ResourceNotFoundException(DomainException):
    """
    资源不存在
    文档 5.3: RESOURCE_NOT_FOUND -> 返回信息不足，不能继续生成退款结论
    """

    pass


class BudgetExceededException(DomainException):
    """
    Token 超预算
    文档 5.3: Token 超预算 -> 停止新增模型调用并降级
    """

    pass


class TaskTimeoutException(DomainException):
    """
    任务总超时
    文档 5.3: 任务总超时 -> 保存检查点，标记失败或转人工
    """

    pass


class RuleConflictException(DomainException):
    """
    规则冲突
    文档 5.3: 规则冲突 -> 人工审批
    """

    pass


class DependencyTimeoutException(DomainException):
    """
    依赖超时（Java API 等）
    文档 5.3: Java API 瞬时超时 -> 指数退避重试，最多两次
    """

    pass


class DependencyUnavailableException(DomainException):
    """
    依赖不可用
    """

    pass
