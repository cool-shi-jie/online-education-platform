# 部署说明

## 开发环境

1. 创建 MySQL 数据库：

```sql
CREATE DATABASE online_education DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 后端配置：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. 前端配置：

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## 生产部署建议

- 使用 `gunicorn` 或 `uwsgi` 运行 Django。
- 使用 Nginx 反向代理后端接口和前端静态文件。
- 将 `DEBUG` 设置为 `False`，配置强随机 `SECRET_KEY`。
- 配置 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS` 为实际域名。
- 将 `media/` 目录映射为受控静态资源目录，生产环境可迁移到对象存储。
- MySQL 使用独立账号并授予最小权限。
