from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Dict, Any
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.learning_path import LearningPath
from ..schemas.learning_path import (
    LearningPathCreate,
    LearningPathResponse,
    LearningPathList,
    ContentGenerationRequest
)
from ..services.n8n_client import n8n_client
from ..services.resource_matcher import resource_matcher
from ..services.dynamic_resource_service import dynamic_resource_service
import re

router = APIRouter(prefix="/api/learning-paths", tags=["学习路线"])


def extract_keywords_from_learning_path(learning_path: LearningPath) -> List[str]:
    """
    从学习路线中提取关键词用于搜索
    
    Args:
        learning_path: 学习路线对象
        
    Returns:
        关键词列表
    """
    keywords = []
    
    # 1. 职位名称
    keywords.append(learning_path.position)
    
    # 2. 从generated_content中提取技术关键词
    generated_content = learning_path.generated_content or {}
    output = generated_content.get('output', '')
    
    # 3. 从Markdown内容中提取加粗的技术名词（**xxx**）
    if output:
        # 提取Markdown加粗文本
        bold_keywords = re.findall(r'\*\*([^\*]+)\*\*', output)
        keywords.extend(bold_keywords[:10])  # 最多10个
        
        # 提取常见技术关键词
        tech_pattern = r'\b(Java|Python|JavaScript|React|Vue|Angular|Node\.js|Spring|Django|Flask|MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes|AWS|Azure|Git|Linux|HTTP|TCP|SQL|NoSQL|RESTful|GraphQL|微服务|前端|后端|全栈)\b'
        tech_keywords = re.findall(tech_pattern, output, re.IGNORECASE)
        keywords.extend(list(set(tech_keywords))[:5])  # 去重后最多5个
    
    # 4. 去重并限制数量
    unique_keywords = []
    seen = set()
    for kw in keywords:
        kw_clean = kw.strip()
        if kw_clean and kw_clean.lower() not in seen:
            unique_keywords.append(kw_clean)
            seen.add(kw_clean.lower())
    
    return unique_keywords[:5]  # 返回最多5个关键词


@router.post("/generate", response_model=LearningPathResponse)
async def generate_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成学习路线（调用n8n工作流）"""
    # 调用n8n工作流，传递content_types
    result = await n8n_client.generate_learning_path(
        user_id=str(current_user.id),
        position=path_data.position,
        job_description=path_data.job_description,
        content_types=path_data.content_types
    )
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "学习路线生成失败")
        )
    
    # 构建generated_content，只标记实际生成的内容类型
    generated_data = result.get("data", {})
    
    # 只有mindmap是首次生成时一定有的，其他内容需要单独生成
    actually_generated_types = []
    if generated_data.get("output"):
        actually_generated_types.append("mindmap")
    
    generated_content = {
        "output": generated_data.get("output", ""),
        "generated_types": actually_generated_types,
        "metadata": {
            "position": path_data.position,
            "timestamp": generated_data.get("timestamp")
        }
    }
    
    # 保存到数据库
    learning_path = LearningPath(
        user_id=current_user.id,
        position=path_data.position,
        job_description=path_data.job_description,
        generated_content=generated_content
    )
    db.add(learning_path)
    db.commit()
    db.refresh(learning_path)
    
    return LearningPathResponse.model_validate(learning_path)


@router.get("", response_model=LearningPathList)
async def list_learning_paths(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的学习路线列表"""
    query = db.query(LearningPath).filter(
        LearningPath.user_id == current_user.id
    ).order_by(LearningPath.created_at.desc())
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return LearningPathList(
        total=total,
        items=[LearningPathResponse.model_validate(item) for item in items]
    )


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个学习路线详情"""
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    return LearningPathResponse.model_validate(learning_path)


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除学习路线"""
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    db.delete(learning_path)
    db.commit()


@router.post("/{path_id}/generate-content")
async def generate_specific_content(
    path_id: int,
    content_request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """按需生成特定类型的内容"""
    # 获取学习路线
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    content_type = content_request.content_type
    generated_content = learning_path.generated_content or {}
    generated_types = generated_content.get("generated_types", [])
    
    # 资源推荐类型（courses, books, certifications）允许多次生成（加载更多）
    # 其他类型（knowledge, interview）检查缓存
    if content_type not in ["courses", "books", "certifications"]:
        # 检查是否已生成该类型内容（并且内容不为空）
        if content_type in generated_types and generated_content.get(content_type):
            return {
                "success": True,
                "message": "内容已存在",
                "content": generated_content.get(content_type),
                "from_cache": True
            }
    
    # 处理资源推荐类型 (courses, books, certifications)
    if content_type in ["courses", "books", "certifications"]:
        # 从学习路线中提取关键词
        keywords = extract_keywords_from_learning_path(learning_path)
        
        # 获取现有资源并计算页码
        existing_resources = generated_content.get(content_type, [])
        # 每次生成就增加页码，而不是等满一页
        # 这样可以确保每次都获取不同的结果
        generation_count = generated_content.get(f"{content_type}_generation_count", 0)
        page = generation_count + 1
        generated_content[f"{content_type}_generation_count"] = page
        
        print(f"[DEBUG] 提取的关键词: {keywords}")
        print(f"[DEBUG] 当前已有 {len(existing_resources)} 个资源，将搜索第 {page} 页")
        
        # 使用DynamicResourceService动态搜索资源
        try:
            if content_type == "courses":
                matched_resources = dynamic_resource_service.search_courses(
                    keywords=keywords,
                    platforms=['bilibili', 'imooc', 'geekbang'],
                    page=page
                )
            elif content_type == "books":
                matched_resources = dynamic_resource_service.search_books(
                    keywords=keywords,
                    page=page
                )
            else:  # certifications
                matched_resources = dynamic_resource_service.search_certifications(
                    keywords=keywords,
                    page=page
                )
            
            print(f"[DEBUG] 搜索到 {len(matched_resources)} 个{content_type}资源")
        except Exception as e:
            print(f"[ERROR] 资源搜索失败: {e}")
            # 失败时使用旧的静态资源匹配作为备选
            if content_type == "courses":
                matched_resources = resource_matcher.match_courses(keywords)
            elif content_type == "books":
                matched_resources = resource_matcher.match_books(keywords)
            else:
                matched_resources = resource_matcher.match_certifications(keywords)
        
        # 追加新资源（而不是覆盖）
        # existing_resources 已在上面定义
        
        # 使用URL去重
        existing_urls = {res.get('url') for res in existing_resources if isinstance(res, dict) and res.get('url')}
        
        # 只添加新资源
        new_resources = []
        for resource in matched_resources:
            if isinstance(resource, dict) and resource.get('url') not in existing_urls:
                new_resources.append(resource)
                existing_urls.add(resource.get('url'))
        
        print(f"[DEBUG] 已有 {len(existing_resources)} 个资源，新增 {len(new_resources)} 个")
        
        # 检查是否有新资源
        if len(new_resources) == 0:
            # 没有新资源可推荐
            content_type_names = {
                "courses": "课程",
                "books": "书籍",
                "certifications": "证书"
            }
            type_name = content_type_names.get(content_type, "资源")
            
            return {
                "success": False,
                "message": f"暂无更多{type_name}推荐，已展示所有相关{type_name}",
                "content": existing_resources,  # 返回现有资源
                "from_cache": True,
                "no_more_resources": True  # 标记：没有更多资源
            }
        
        # 合并资源列表
        all_resources = existing_resources + new_resources
        generated_content[content_type] = all_resources
        
        if content_type not in generated_types:
            generated_types.append(content_type)
        generated_content["generated_types"] = generated_types
        
        learning_path.generated_content = generated_content
        # 标记JSON字段已修改
        flag_modified(learning_path, "generated_content")
        db.commit()
        db.refresh(learning_path)
        
        print(f"[DEBUG] 总计 {len(all_resources)} 个资源")
        
        return {
            "success": True,
            "message": f"成功新增 {len(new_resources)} 个{content_type}推荐",
            "content": all_resources,  # 返回所有资源
            "from_cache": False
        }
    
    # 处理AI生成类型 (knowledge, interview)
    # 根据content_type构建具体的prompt
    content_type_prompts = {
        "knowledge": f"请为'{learning_path.position}'职位生成详细的知识点详解，包括：\n1. 核心概念说明\n2. 技术要点分析\n3. 学习路径建议\n4. 实践应用指导\n\n要求：使用Markdown格式，内容专业且易懂。",
        "interview": f"请为'{learning_path.position}'职位生成面试题库，包括：\n1. 常见面试问题及答案\n2. 技术难点剖析\n3. 项目经验问题\n4. 面试技巧建议\n\n要求：使用Markdown格式，每题包含问题、参考答案、考察点。"
    }
    
    # 构建job_description，包含具体的生成要求
    job_description = content_type_prompts.get(content_type, f"生成{content_type}相关内容")
    
    # 调用n8n工作流生成内容
    result = await n8n_client.generate_learning_path(
        user_id=str(current_user.id),
        position=learning_path.position,
        job_description=job_description,
        content_types=["mindmap"]  # 使用mindmap类型，但内容是定制的
    )
    
    # 添加调试日志
    print(f"[DEBUG] n8n返回结果: {result}")
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", f"{content_type}内容生成失败")
        )
    
    # 更新数据库
    result_data = result.get("data", {})
    print(f"[DEBUG] result_data: {result_data}")
    
    # 提取AI生成的内容
    ai_output = result_data.get("output", "")
    print(f"[DEBUG] AI输出长度: {len(ai_output)}")
    
    if not ai_output:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI生成的内容为空"
        )
    
    generated_content[content_type] = ai_output
    if content_type not in generated_types:
        generated_types.append(content_type)
    generated_content["generated_types"] = generated_types
    
    learning_path.generated_content = generated_content
    # 标记JSON字段已修改，否则SQLAlchemy不会更新
    flag_modified(learning_path, "generated_content")
    db.commit()
    db.refresh(learning_path)
    
    return {
        "success": True,
        "message": f"{content_type}内容生成成功",
        "content": ai_output,
        "from_cache": False
    }

