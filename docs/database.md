# 数据库设计摘要

## 用户与权限

- `accounts_user`：用户账号，包含 `role` 字段，取值为 `student`、`teacher`、`admin`。

## 课程学习

- `courses_course`：课程基础信息、分类、语言、封面、状态、合格分数。
- `courses_chapter`：课程章节、视频、排序、是否必修。
- `courses_coursematerial`：课程资料，可关联课程或章节。
- `courses_enrollment`：学生报名记录，限制同一学生同一课程只能报名一次。
- `courses_chapterprogress`：章节学习状态，限制同一报名记录同一章节只有一条进度。

## 考试成绩

- `exams_exam`：课程考试。
- `exams_question`：考试题目，支持单选和多选。
- `exams_choice`：题目选项和正确答案。
- `exams_examsubmission`：学生答卷和分数，限制同一学生同一考试只能提交一次。

## 论坛证书

- `forum_forumpost`：课程论坛帖子，支持软删除。
- `forum_forumreply`：帖子回复，支持软删除。
- `certificates_certificate`：证书记录，限制同一学生同一课程只能获得一张证书。
