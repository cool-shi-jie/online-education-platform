# 在线教育平台

前后端分离的在线教育平台 MVP，面向学生、教师和管理员，覆盖课程发布、学习进度、在线考试、论坛互动和证书记录。

## 技术栈

- 后端：Python、Django、Django REST Framework、MySQL、JWT
- 前端：Vue 3、Vite、Element Plus、Pinia、Vue Router、Axios

## 目录

- `backend/`：后端 API 服务
- `frontend/`：前端页面
- `docs/`：数据库、接口和部署说明

## 快速启动

后端：

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

前端：

```bash
cd frontend
npm install
npm run dev
```

默认后端地址为 `http://127.0.0.1:8000/api`。
