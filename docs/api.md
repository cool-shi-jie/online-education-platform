# API 清单

默认前缀：`/api/`

## 认证

- `POST /auth/register/`：学生或教师注册。
- `POST /auth/login/`：登录并返回 JWT 和用户角色。
- `POST /auth/refresh/`：刷新 JWT。
- `GET /auth/me/`：获取当前用户。

## 课程

- `GET /courses/`：课程列表，支持分页、搜索、分类、语言和状态过滤。
- `POST /courses/`：教师创建课程。
- `GET /courses/{id}/`：课程详情。
- `POST /courses/{id}/enroll/`：学生报名课程。
- `POST /courses/{id}/complete_chapter/`：学生标记章节完成。
- `GET /courses/{id}/progress/`：学生查看个人进度，教师查看课程学生进度。
- `GET /courses/{id}/recommendations/`：获取同分类推荐课程。
- `POST /chapters/`：教师创建章节。
- `POST /materials/`：教师上传课件资料。
- `GET /enrollments/`：按角色返回报名记录。

## 考试

- `GET /exams/`：考试列表。
- `POST /exams/`：教师创建考试。
- `POST /questions/`：教师创建题目。
- `POST /choices/`：教师创建选项。
- `POST /submissions/`：学生提交答卷，后端自动评分并防重复提交。
- `GET /submissions/`：学生查看个人成绩，教师查看所授课程成绩。

## 论坛与证书

- `GET /forum/posts/`：论坛帖子列表，支持分页和课程过滤。
- `POST /forum/posts/`：发布帖子。
- `GET /forum/posts/{id}/replies/`：查看帖子回复。
- `POST /forum/replies/`：发布回复。
- `DELETE /forum/posts/{id}/`：作者或管理员软删除帖子。
- `GET /certificates/`：按角色查看证书记录。
