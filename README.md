# Dingjun · dingjunn.com

个人网站：项目、文章、思考。不是简历，是长期更新的个人空间。

## 本地预览

```bash
python3 -m http.server 4173
```

打开 http://127.0.0.1:4173/

## 结构

```
index.html            首页（六屏滑动：首屏 / 精选 / 项目 / 文章 / 思考 / 关于）
projects.html         项目列表（四条入口）
projects/             项目详情（四页）+ detail.css
articles/index.html   文章总入口（两个系列文件夹）
articles/systems.html 系列 01 · 系统拆解
articles/ideas.html   系列 02 · 产品创意拆解
articles/*.html       产品创意拆解单篇（脚本生成）
systems/*.html        系统拆解单篇（手写）
articles/method.html  拆解方法页
posts/                思考类单篇
thoughts.html         思考列表
about.html            关于
assets/projects/      项目截图（三项目共 17 张）
```

## 文章栏目

`articles/` 下除 `systems.html` 外，页面都由 `build-articles.py` 生成；源文件是本机 Obsidian 库里的
`产品创意案例知识库/`（每个「编号 标题.md」是一个案例）。

```bash
python3 build-articles.py                          # 重新编译全部案例与配图
VAULT_DIR=/别的/路径 python3 build-articles.py      # 换笔记库位置
```

新增案例：在 Obsidian 里加一篇 `18 xxx.md` → 在脚本 `SLUGS` 里补 `"18": "xxx"` → 重跑脚本。
配图会自动从 `_assets/` 压缩到 1400px 宽并复制进 `articles/assets/`。脚本只读笔记库，不改动 Obsidian 文件。

系统拆解三篇是手写的，索引条目在 `build-articles.py` 的 `SYSTEMS` 列表里，改标题/摘要要改那里再重跑。

## 事实边界（改文案时请守住）

- 项目截图里的数字都是演示数据，不写「准确率」「提升多少」这类没验证过的结论
- NutriFit 的热量识别是估算；医路通是技术演示，不替代诊断
- mac-checkup：移进废纸篓 ≠ 释放空间；充电上限只做提醒，不能自动设置
- 三篇数学论文是「完成写作」，不是「已发表」

## 部署

推到 GitHub `main` 即由 Vercel（`vercel[bot]` Git 集成）自动生产部署，无需手动 CLI。
`vercel.json` 已开 `cleanUrls`：`/projects/medix` 等价于 `projects/medix.html`。

## 已知欠账

- 没有 favicon、没有 `og:image`，分享到微信只有一行文字
- 项目截图是 1280×577 的固定尺寸，窄屏下细节偏小
