"""创建管理员账号的脚本"""
import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # 检查admin用户是否已存在
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("管理员账号已存在")
            return
        
        # 创建管理员账号
        admin_user = User(
            username="admin",
            email="admin@zhitu.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("✓ 管理员账号创建成功")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@zhitu.com")
    except Exception as e:
        print(f"✗ 创建管理员账号失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

