from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app.permissions import require_permission
from app import crud  # используем crud, чтобы показать реальные обращения к БД (роль пользователя)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["business"])

# Мок-данные (фейковые статьи)
_fake_articles = [
    {"id": 1, "title": "Article 1", "content": "Content 1"},
    {"id": 2, "title": "Article 2", "content": "Content 2"},
]


@router.get("/")
def list_articles(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    perm=Depends(require_permission("article", "read")),
):
    """
    Возвращает список mock-статей.
    Требуется право: article:read

    Параметры-зависимости используются явно:
    - db: для получения списка ролей пользователя (демонстрация использования)
    - current_user: id пользователя включён в метаданные ответа
    - perm: результат зависимости (обычно True) — проверка уже выполнена
    """
    # Используем db + crud, чтобы показать, какие роли у пользователя:
    try:
        role_ids = crud.get_user_role_ids(db, current_user.id) or []
    except Exception as e:
        # если что-то пошло не так с БД — логируем и возвращаем 500
        logger.exception("Failed to fetch user roles: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")

    # Формируем ответ: статьи + метаданные (показываем, что зависимости реально используются)
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "roles": role_ids,
        "permission_checked": bool(perm),
        "articles": _fake_articles,
    }


@router.post("/{article_id}/update")
def update_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    perm=Depends(require_permission("article", "update")),
):
    """
    Mock-обновление статьи.
    Требуется право: article:update

    В теле явно используем db/current_user/perm:
    - проверяем наличия статьи,
    - логируем кто выполнил обновление,
    - возвращаем информацию о пользователе и изменении.
    """
    # проверка существования "статьи" в мок-списке
    article = next((a for a in _fake_articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # демонстрация использования db: получить роли пользователя (для логирования)
    role_ids = crud.get_user_role_ids(db, current_user.id) or []

    # логируем фактическое действие (в реальном приложении здесь бы было обновление в БД)
    logger.info("User %s (roles=%s) updated article %s", current_user.email, role_ids, article_id)

    return {
        "detail": f"Article {article_id} updated (mock).",
        "user": {"id": current_user.id, "email": current_user.email},
        "roles": role_ids,
        "permission_checked": bool(perm),
    }