from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class NoteGenerationOptions(BaseModel):
    """AI 笔记生成选项"""
    include_weak_points: bool = Field(default=True, description="包含薄弱知识点分析")
    include_study_plan: bool = Field(default=True, description="包含学习计划")
    include_interview_tips: bool = Field(default=True, description="包含面试技巧")
    custom_requirements: Optional[str] = Field(default=None, description="用户自定义要求")


class NoteGenerationRequest(BaseModel):
    """AI 笔记生成请求"""
    source_type: Literal["mistakes", "interview", "learning_path"] = Field(
        ..., 
        description="数据源类型：mistakes-错题，interview-面试题，learning_path-学习路径"
    )
    source_id: int = Field(..., description="数据源ID（learning_path_id）")
    options: NoteGenerationOptions = Field(default_factory=NoteGenerationOptions)


class NoteDraftMetadata(BaseModel):
    """笔记草稿元数据"""
    source: str = Field(..., description="数据来源")
    learning_path_id: int = Field(..., description="学习路径ID")
    position: str = Field(..., description="职业名称")
    mistakes_count: Optional[int] = Field(default=0, description="错题数量")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")


class NoteDraftResponse(BaseModel):
    """AI 笔记草稿响应"""
    title: str = Field(..., description="笔记标题")
    content: str = Field(..., description="笔记内容（Markdown格式）")
    suggested_notebook: str = Field(..., description="建议保存的笔记本名称")
    metadata: NoteDraftMetadata = Field(..., description="元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python开发工程师 - 错题总结笔记",
                "content": "## 错题分析\n\n...",
                "suggested_notebook": "错题本",
                "metadata": {
                    "source": "mistakes",
                    "learning_path_id": 1,
                    "position": "Python开发工程师",
                    "mistakes_count": 5,
                    "generated_at": "2024-01-01T00:00:00"
                }
            }
        }

