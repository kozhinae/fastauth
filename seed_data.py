from app.database import SessionLocal, Base, engine
from app import models, crud

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin_role = models.Role(name="admin", description="Администратор")
editor_role = models.Role(name="editor", description="Может читать и создавать статьи")
viewer_role = models.Role(name="viewer", description="Только чтение")

db.add_all([admin_role, editor_role, viewer_role])
db.commit()

article_res = models.Resource(name="article", description="Статьи")
db.add(article_res)
db.commit()

perm_read = models.Permission(action="read", description="Чтение")
perm_create = models.Permission(action="create", description="Создание")
perm_update = models.Permission(action="update", description="Обновление")
perm_delete = models.Permission(action="delete", description="Удаление")
db.add_all([perm_read, perm_create, perm_update, perm_delete])
db.commit()

db.add(models.RolePermission(role_id=admin_role.id, resource_id=article_res.id, permission_id=perm_read.id))
db.add(models.RolePermission(role_id=admin_role.id, resource_id=article_res.id, permission_id=perm_create.id))
db.add(models.RolePermission(role_id=admin_role.id, resource_id=article_res.id, permission_id=perm_update.id))
db.add(models.RolePermission(role_id=admin_role.id, resource_id=article_res.id, permission_id=perm_delete.id))

db.add(models.RolePermission(role_id=editor_role.id, resource_id=article_res.id, permission_id=perm_read.id))
db.add(models.RolePermission(role_id=editor_role.id, resource_id=article_res.id, permission_id=perm_create.id))

db.add(models.RolePermission(role_id=viewer_role.id, resource_id=article_res.id, permission_id=perm_read.id))

db.commit()

admin_user = crud.create_user(db, email="admin@example.com", password="adminpass", first_name="Admin", last_name="Root")
admin_user.is_staff = True
db.add(admin_user)
db.commit()
db.refresh(admin_user)

db.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
db.commit()
