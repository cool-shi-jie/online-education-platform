from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from urllib.parse import quote, urlparse

from apps.courses.models import Chapter, Course
from apps.forum.models import LearningResource


COURSES = [
    {
        "teacher": "teacher_ai",
        "title": "Python 数据分析入门",
        "category": "人工智能与数据",
        "description": "从 Python 基础、数据清洗到可视化分析，建立完整的数据分析工作流。",
        "chapters": ["Python 与数据环境", "表格数据读取", "数据清洗方法", "可视化图表", "综合分析案例"],
    },
    {
        "teacher": "teacher_ai",
        "title": "机器学习基础与实践",
        "category": "人工智能与数据",
        "description": "理解监督学习、模型评估和常见算法，并完成一个可运行的预测项目。",
        "chapters": ["机器学习问题定义", "特征工程", "分类与回归", "模型评估", "项目实战"],
    },
    {
        "teacher": "teacher_cs",
        "title": "Web 前端开发基础",
        "category": "计算机与互联网",
        "description": "系统学习 HTML、CSS、JavaScript 和组件化开发，完成一个响应式页面。",
        "chapters": ["HTML 结构", "CSS 布局", "JavaScript 交互", "组件化思想", "项目发布"],
    },
    {
        "teacher": "teacher_cs",
        "title": "Django 后端开发实战",
        "category": "计算机与互联网",
        "description": "围绕 Django、REST API、权限和数据建模构建可维护的后端服务。",
        "chapters": ["Django 项目结构", "模型与迁移", "REST API", "认证与权限", "部署检查"],
    },
    {
        "teacher": "teacher_cs",
        "title": "数据库设计与 SQL",
        "category": "计算机与互联网",
        "description": "掌握关系型数据库建模、查询优化和常用 SQL 分析技巧。",
        "chapters": ["关系模型", "基础查询", "多表连接", "索引与优化", "数据建模案例"],
    },
    {
        "teacher": "teacher_business",
        "title": "管理学原理",
        "category": "经济管理",
        "description": "从组织、计划、领导和控制四个角度理解现代管理的基础框架。",
        "chapters": ["管理者角色", "组织设计", "计划制定", "领导沟通", "控制与改进"],
    },
    {
        "teacher": "teacher_business",
        "title": "财务报表阅读",
        "category": "经济管理",
        "description": "用通俗案例理解资产负债表、利润表和现金流量表的核心信息。",
        "chapters": ["财务三张表", "盈利能力", "现金流分析", "偿债能力", "综合案例"],
    },
    {
        "teacher": "teacher_language",
        "title": "大学英语写作提升",
        "category": "语言学习",
        "description": "训练段落结构、论证表达和学术写作常用句式，提高英文写作质量。",
        "chapters": ["句子准确性", "段落组织", "论证展开", "学术表达", "作文修改"],
    },
    {
        "teacher": "teacher_language",
        "title": "日语五十音与入门会话",
        "category": "语言学习",
        "description": "从五十音开始，学习常见问候、校园和旅行场景表达。",
        "chapters": ["五十音图", "基础发音", "日常问候", "校园会话", "旅行表达"],
    },
    {
        "teacher": "teacher_foundation",
        "title": "高等数学基础",
        "category": "学科基础",
        "description": "围绕极限、导数、积分和应用题建立大学数学基础能力。",
        "chapters": ["函数与极限", "导数计算", "微分应用", "积分方法", "综合练习"],
    },
    {
        "teacher": "teacher_foundation",
        "title": "线性代数核心概念",
        "category": "学科基础",
        "description": "理解矩阵、向量空间、特征值和线性变换的直观意义。",
        "chapters": ["矩阵运算", "行列式", "向量空间", "特征值", "线性变换"],
    },
    {
        "teacher": "teacher_social",
        "title": "中国传统文化导论",
        "category": "人文社科",
        "description": "从思想、制度、文学和艺术角度理解传统文化的基本脉络。",
        "chapters": ["先秦思想", "制度演变", "古典文学", "传统艺术", "现代转化"],
    },
    {
        "teacher": "teacher_social",
        "title": "社会心理学入门",
        "category": "人文社科",
        "description": "学习态度、群体、从众和社会认知等常见心理现象。",
        "chapters": ["社会认知", "态度形成", "群体影响", "人际关系", "应用案例"],
    },
    {
        "teacher": "teacher_science",
        "title": "普通物理思维训练",
        "category": "自然科学与工程",
        "description": "通过力学、电磁学和能量守恒问题训练科学建模思维。",
        "chapters": ["运动描述", "牛顿定律", "能量守恒", "电场磁场", "实验思维"],
    },
    {
        "teacher": "teacher_science",
        "title": "工程制图基础",
        "category": "自然科学与工程",
        "description": "掌握投影、视图、尺寸标注和工程图阅读的基础技能。",
        "chapters": ["投影基础", "三视图", "剖视图", "尺寸标注", "图纸阅读"],
    },
    {
        "teacher": "teacher_health",
        "title": "健康管理与营养基础",
        "category": "医学与健康",
        "description": "了解营养结构、运动习惯和健康风险管理的基础知识。",
        "chapters": ["营养素基础", "膳食结构", "运动计划", "睡眠管理", "风险识别"],
    },
    {
        "teacher": "teacher_law",
        "title": "民法基础与生活案例",
        "category": "法律与公共事务",
        "description": "结合合同、侵权、人格权等生活案例理解民法基础规则。",
        "chapters": ["民法总则", "合同基础", "侵权责任", "人格权", "案例分析"],
    },
    {
        "teacher": "teacher_career",
        "title": "职业规划与简历表达",
        "category": "职业发展",
        "description": "帮助学生梳理职业方向、优化简历结构并准备面试表达。",
        "chapters": ["职业探索", "能力盘点", "简历结构", "面试表达", "行动计划"],
    },
    {
        "teacher": "teacher_art",
        "title": "摄影构图与后期入门",
        "category": "设计与创意",
        "description": "学习摄影构图、光线观察和基础后期，让作品更有表达力。",
        "chapters": ["构图基础", "光线观察", "色彩表达", "后期流程", "作品点评"],
    },
    {
        "teacher": "teacher_hobby",
        "title": "时间管理与自我提升",
        "category": "兴趣拓展",
        "description": "用目标拆解、任务排序和复盘方法提升学习与生活效率。",
        "chapters": ["目标设定", "任务拆解", "时间记录", "复盘方法", "习惯养成"],
    },
]


WEB_RESOURCES = [
    ("Python 官方教程", "人工智能与数据", "https://docs.python.org/zh-cn/3/tutorial/", "系统学习 Python 语言基础与标准库。", "Python Docs"),
    ("Pandas 用户指南", "人工智能与数据", "https://pandas.pydata.org/docs/user_guide/index.html", "适合数据清洗和表格分析的官方指南。", "Pandas"),
    ("Scikit-learn 入门", "人工智能与数据", "https://scikit-learn.org/stable/getting_started.html", "机器学习实践的常用工具文档。", "Scikit-learn"),
    ("MDN Web 入门", "计算机与互联网", "https://developer.mozilla.org/zh-CN/docs/Learn", "前端开发学习路径和基础教程。", "MDN"),
    ("Vue 官方教程", "计算机与互联网", "https://cn.vuejs.org/tutorial/", "交互式学习 Vue 组件和响应式开发。", "Vue"),
    ("Django 官方文档", "计算机与互联网", "https://docs.djangoproject.com/zh-hans/", "Django 后端开发的权威参考。", "Django"),
    ("MySQL 文档", "计算机与互联网", "https://dev.mysql.com/doc/", "数据库管理、查询和优化参考。", "MySQL"),
    ("Khan Academy 经济学", "经济管理", "https://www.khanacademy.org/economics-finance-domain", "经济学和金融基础的开放课程。", "Khan Academy"),
    ("Harvard Business Review", "经济管理", "https://hbr.org/", "管理案例、组织战略和领导力文章。", "HBR"),
    ("Cambridge English Learning", "语言学习", "https://www.cambridgeenglish.org/learning-english/", "英语学习资料、练习和考试准备。", "Cambridge English"),
    ("NHK Easy Japanese", "语言学习", "https://www.nhk.or.jp/lesson/", "日语入门发音和场景会话。", "NHK"),
    ("Paul's Online Math Notes", "学科基础", "https://tutorial.math.lamar.edu/", "高等数学、微积分和代数笔记。", "Paul's Notes"),
    ("MIT OpenCourseWare", "自然科学与工程", "https://ocw.mit.edu/", "工程、科学和数学开放课程资源。", "MIT OCW"),
    ("Coursera Learning How to Learn", "职业发展", "https://www.coursera.org/learn/learning-how-to-learn", "学习方法和自我提升经典课程。", "Coursera"),
    ("WHO Health Topics", "医学与健康", "https://www.who.int/health-topics", "健康主题、疾病预防和公共卫生资料。", "WHO"),
    ("中国法律服务网", "法律与公共事务", "https://www.12348.gov.cn/", "生活法律服务与公共法律知识。", "中国法律服务网"),
    ("Google Arts & Culture", "人文社科", "https://artsandculture.google.com/", "艺术、历史和文化专题资源。", "Google Arts & Culture"),
    ("Canva Design School", "设计与创意", "https://www.canva.com/learn/design-school/", "设计基础、排版和视觉表达学习资源。", "Canva"),
    ("NumPy 官方学习资料", "人工智能与数据", "https://numpy.org/learn/", "面向科学计算和数据处理的 NumPy 入门资源。", "NumPy"),
    ("Kaggle Learn", "人工智能与数据", "https://www.kaggle.com/learn", "数据分析、机器学习和可视化的实践型微课程。", "Kaggle"),
    ("Google Machine Learning Crash Course", "人工智能与数据", "https://developers.google.com/machine-learning/crash-course", "机器学习核心概念和练习的快速课程。", "Google Developers"),
    ("Jupyter Notebook 文档", "人工智能与数据", "https://docs.jupyter.org/en/latest/", "交互式数据分析和实验记录工具文档。", "Jupyter"),
    ("FreeCodeCamp", "计算机与互联网", "https://www.freecodecamp.org/learn/", "编程、前端、后端和数据分析的开放学习路径。", "freeCodeCamp"),
    ("JavaScript.info", "计算机与互联网", "https://javascript.info/", "系统讲解 JavaScript 语言和浏览器开发知识。", "JavaScript.info"),
    ("React 官方学习", "计算机与互联网", "https://react.dev/learn", "组件、状态和交互式界面开发的官方教程。", "React"),
    ("PostgreSQL 文档", "计算机与互联网", "https://www.postgresql.org/docs/", "数据库 SQL、索引和管理知识的权威资料。", "PostgreSQL"),
    ("Investopedia", "经济管理", "https://www.investopedia.com/", "金融、投资和商业概念的百科式学习资料。", "Investopedia"),
    ("Corporate Finance Institute", "经济管理", "https://corporatefinanceinstitute.com/resources/", "财务分析、估值和商业金融相关资源。", "CFI"),
    ("MindTools 管理技能", "经济管理", "https://www.mindtools.com/", "管理沟通、领导力和职场协作工具库。", "MindTools"),
    ("BBC Learning English", "语言学习", "https://www.bbc.co.uk/learningenglish", "英语听力、词汇、语法和新闻英语学习资源。", "BBC Learning English"),
    ("Duolingo Stories", "语言学习", "https://www.duolingo.com/stories", "通过短故事练习语言阅读和理解能力。", "Duolingo"),
    ("Tae Kim 日语语法指南", "语言学习", "https://guidetojapanese.org/learn/", "日语语法入门和进阶学习指南。", "Tae Kim"),
    ("Khan Academy Math", "学科基础", "https://www.khanacademy.org/math", "数学基础、代数、微积分和统计学习资源。", "Khan Academy Math"),
    ("3Blue1Brown", "学科基础", "https://www.3blue1brown.com/", "用可视化方式理解数学和线性代数概念。", "3Blue1Brown"),
    ("OpenStax Textbooks", "学科基础", "https://openstax.org/subjects", "数学、物理、经济和社会科学开放教材。", "OpenStax"),
    ("Stanford Encyclopedia of Philosophy", "人文社科", "https://plato.stanford.edu/", "哲学、人文和思想史主题的权威百科。", "Stanford Encyclopedia"),
    ("Internet History Sourcebooks", "人文社科", "https://sourcebooks.fordham.edu/", "历史文献、文化研究和社会科学材料合集。", "Fordham Sourcebooks"),
    ("Our World in Data", "人文社科", "https://ourworldindata.org/", "用数据理解社会、健康、教育和全球发展问题。", "Our World in Data"),
    ("NASA Science", "自然科学与工程", "https://science.nasa.gov/", "天文、地球科学和空间探索主题资料。", "NASA Science"),
    ("PhET Interactive Simulations", "自然科学与工程", "https://phet.colorado.edu/zh_CN/", "物理、化学、数学交互式仿真实验。", "PhET"),
    ("Engineering Toolbox", "自然科学与工程", "https://www.engineeringtoolbox.com/", "工程计算、材料属性和常用公式参考。", "Engineering Toolbox"),
    ("Mayo Clinic Health Library", "医学与健康", "https://www.mayoclinic.org/diseases-conditions", "疾病、症状和健康管理知识库。", "Mayo Clinic"),
    ("MedlinePlus", "医学与健康", "https://medlineplus.gov/", "面向公众的医学健康知识和药物信息。", "MedlinePlus"),
    ("Verywell Health", "医学与健康", "https://www.verywellhealth.com/", "健康生活、疾病科普和护理知识资料。", "Verywell Health"),
    ("中华人民共和国最高人民法院", "法律与公共事务", "https://www.court.gov.cn/", "司法解释、案例资讯和法治公开信息。", "最高人民法院"),
    ("中国人大网法律法规库", "法律与公共事务", "http://www.npc.gov.cn/npc/c2/c30834/", "国家法律法规查询和学习资源。", "中国人大网"),
    ("UN Sustainable Development Goals", "法律与公共事务", "https://sdgs.un.org/goals", "公共事务、全球治理和可持续发展目标资料。", "UN SDGs"),
    ("LinkedIn Learning Blog", "职业发展", "https://www.linkedin.com/business/learning/blog", "职场学习、技能发展和职业成长文章。", "LinkedIn Learning"),
    ("Indeed Career Guide", "职业发展", "https://www.indeed.com/career-advice", "求职、简历、面试和职业规划建议。", "Indeed Career Guide"),
    ("Google Career Certificates", "职业发展", "https://grow.google/certificates/", "数字技能、数据分析和项目管理职业证书路径。", "Google Career Certificates"),
    ("Adobe Design Basics", "设计与创意", "https://www.adobe.com/creativecloud/design/discover.html", "设计概念、创意工具和视觉表达基础。", "Adobe"),
    ("Interaction Design Foundation", "设计与创意", "https://www.interaction-design.org/literature", "用户体验、交互设计和产品设计文献资料。", "IxDF"),
    ("Smashing Magazine", "设计与创意", "https://www.smashingmagazine.com/", "前端设计、用户体验和网页视觉实践文章。", "Smashing Magazine"),
    ("TED-Ed", "兴趣拓展", "https://ed.ted.com/", "跨学科短视频课程和趣味学习主题。", "TED-Ed"),
    ("Lifehack", "兴趣拓展", "https://www.lifehack.org/", "时间管理、习惯养成和个人成长文章。", "Lifehack"),
    ("Wikibooks", "兴趣拓展", "https://www.wikibooks.org/", "开放教材、兴趣学习和自学资源集合。", "Wikibooks"),
    ("Purdue OWL", "语言学习", "https://owl.purdue.edu/", "英语写作、引用格式和学术表达指南。", "Purdue OWL"),
    ("MySQL 8.0 Reference Manual", "数据库", "https://dev.mysql.com/doc/refman/8.0/en/", "MySQL 8.0 数据库查询、管理和优化参考手册。", "MySQL"),
]


FILE_RESOURCES = [
    ("Python 数据分析速查表", "人工智能与数据", "pdf", "常用数据分析语法、函数和处理流程速查。"),
    ("机器学习术语表", "人工智能与数据", "docx", "监督学习、模型评估、特征工程等关键词解释。"),
    ("前端布局练习包", "计算机与互联网", "zip", "包含 Flex、Grid 和响应式布局练习说明。"),
    ("SQL 查询练习题", "计算机与互联网", "pdf", "从基础查询到多表连接的分层练习题。"),
    ("管理学案例阅读材料", "经济管理", "pdf", "组织管理、沟通和决策相关课堂案例。"),
    ("英语写作句型模板", "语言学习", "docx", "议论文、说明文和学术写作常用表达模板。"),
    ("高等数学公式清单", "学科基础", "pdf", "极限、导数、积分和级数基础公式整理。"),
    ("线性代数练习讲义", "学科基础", "pdf", "矩阵、行列式和特征值专题训练。"),
    ("传统文化阅读书单", "人文社科", "docx", "传统思想、文学和艺术入门阅读清单。"),
    ("物理实验记录模板", "自然科学与工程", "docx", "实验目的、步骤、数据和结论记录模板。"),
    ("健康饮食计划表", "医学与健康", "pdf", "一周膳食计划和营养结构记录表。"),
    ("简历优化清单", "职业发展", "pdf", "简历结构、项目表达和常见问题检查表。"),
    ("摄影构图练习卡", "设计与创意", "pdf", "三分法、引导线和色彩练习任务卡。"),
    ("时间管理复盘表", "兴趣拓展", "docx", "每日计划、时间记录和周复盘模板。"),
]


class Command(BaseCommand):
    help = "Seed rich demo courses, chapters, and community learning resources."

    def add_arguments(self, parser):
        parser.add_argument("--skip-preview", action="store_true", help="Skip writing static preview image URLs for web resources.")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        teachers = self._ensure_teachers(User)
        courses_created, chapters_created = self._seed_courses(teachers)
        resources_created = self._seed_resources(teachers["teacher_cs"], skip_preview=options["skip_preview"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {courses_created} courses, {chapters_created} chapters, and {resources_created} learning resources."
            )
        )

    def _ensure_teachers(self, User):
        teacher_names = sorted({course["teacher"] for course in COURSES})
        teachers = {}
        for username in teacher_names:
            teacher, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": User.Role.TEACHER,
                    "first_name": "水木",
                    "last_name": "讲师",
                },
            )
            if created:
                teacher.set_password("demo123456")
            teacher.role = User.Role.TEACHER
            teacher.email = teacher.email or f"{username}@example.com"
            teacher.save()
            teachers[username] = teacher
        return teachers

    def _seed_courses(self, teachers):
        course_count = 0
        chapter_count = 0
        for item in COURSES:
            course, course_created = Course.objects.update_or_create(
                title=item["title"],
                defaults={
                    "teacher": teachers[item["teacher"]],
                    "description": item["description"],
                    "category": item["category"],
                    "language": "zh-CN",
                    "status": Course.Status.PUBLISHED,
                    "pass_score": 60,
                },
            )
            course_count += int(course_created)
            for index, title in enumerate(item["chapters"], start=1):
                _, chapter_created = Chapter.objects.update_or_create(
                    course=course,
                    order=index,
                    defaults={
                        "title": title,
                        "description": f"{item['title']}的第 {index} 个学习主题：{title}。",
                        "duration_seconds": 0,
                        "is_required": True,
                    },
                )
                chapter_count += int(chapter_created)
        return course_count, chapter_count

    def _seed_resources(self, publisher, skip_preview=False):
        resource_count = 0
        for title, category, url, summary, site_name in WEB_RESOURCES:
            defaults = {
                "publisher": publisher,
                "summary": summary,
                "url": url,
                "category": category,
                "is_published": True,
                "preview_site_name": site_name,
            }
            if not skip_preview:
                defaults["preview_image_url"] = self._preview_image(url)
            _, created = LearningResource.objects.update_or_create(title=title, defaults=defaults)
            resource_count += int(created)

        for title, category, extension, summary in FILE_RESOURCES:
            resource, created = LearningResource.objects.update_or_create(
                title=title,
                defaults={
                    "publisher": publisher,
                    "summary": summary,
                    "url": "",
                    "category": category,
                    "is_published": True,
                    "preview_image_url": "",
                    "preview_site_name": "",
                },
            )
            if not resource.attachment:
                content = ContentFile(
                    f"{title}\n\n这是一份用于在线教育平台演示的学习资料占位文件。\n".encode("utf-8")
                )
                resource.attachment.save(f"{self._slug(title)}.{extension}", content, save=True)
            resource_count += int(created)
        return resource_count

    def _preview_image(self, url):
        domain = urlparse(url).netloc
        return f"https://www.google.com/s2/favicons?domain={quote(domain)}&sz=256"

    def _slug(self, value):
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in value)[:60].strip("_") or "resource"
