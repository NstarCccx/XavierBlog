"""站点设置 DTO。"""

from pydantic import BaseModel, Field


class SiteInfo(BaseModel):
    """前台站点信息。"""

    site_name: str = "XavierBlog"
    site_description: str = ""
    about_content: str = ""
    footer: str = ""
    # 备案信息：ICP 备案号及其查询链接
    icp_number: str = ""
    icp_link: str = ""
    # 公安备案：号码与查询链接，未下发时为空串，前台据此隐藏
    police_number: str = ""
    police_link: str = ""


class SiteConfigUpdate(BaseModel):
    """后台批量保存设置。"""

    data: dict[str, str] = Field(min_length=1)


class PostViewsItem(BaseModel):
    """单篇文章浏览量（仪表盘图表用）。"""

    id: int
    title: str
    views: int


class DashboardStats(BaseModel):
    """后台仪表盘统计。"""

    post_count: int
    published_count: int
    draft_count: int
    category_count: int
    tag_count: int
    comment_count: int
    pending_comment_count: int
    total_views: int
    top_views: list[PostViewsItem] = []
