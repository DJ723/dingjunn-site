# Dingjun · dingjunn.com

个人网站：项目、文章、思考。

## 本地预览

```bash
python3 -m http.server 4173
```

打开 http://127.0.0.1:4173/

## 结构

- `index.html` 首页（五屏滑动）
- `projects.html` 项目（三项目 + 一个开源 Skill）
- `articles/` 文章（产品创意拆解系列，由 Obsidian 笔记生成，勿手改）
- `systems/` 系统拆解（手写，拆自己项目的设计取舍；索引条目在 `build-articles.py` 的 `systems` 列表里）
- `thoughts.html` 思考列表
- `posts/` 单篇（思考类文章）
- `about.html` 关于
- `assets/projects/` 项目页截图

## 文章栏目

`articles/` 下的 19 个页面全部由 `build-articles.py` 生成，源文件是本机 Obsidian 库里的
`产品创意案例知识库/`（每个「编号 标题.md」是一个案例）。

```bash
python3 build-articles.py                          # 重新编译全部案例与配图
VAULT_DIR=/别的/路径 python3 build-articles.py      # 换笔记库位置
```

新增案例的流程：在 Obsidian 里加一篇 `18 xxx.md` → 在脚本的 `SLUGS` 里补一行 `"18": "xxx"` → 重跑脚本。
配图会自动从 `_assets/` 压缩到 1400px 宽并复制进 `articles/assets/`。
脚本只读笔记库，不会改动 Obsidian 里的文件。

`articles/index.html` 是文章总览页；`articles/method.html` 是拆解方法页；其余为单篇详情。

## 待补

关于页「论文」一节只写了状态（3 篇基础数学，在投审稿中），没有列题目——这是刻意的：
没录用、没预印本的情况下写「已发表」是不诚实的。等录用或挂上 arXiv 后，把题目与链接补进
`about.html` 的「论文」段，同时更新 `index.html` 首屏的「3 篇论文在投」。


## 部署

本目录直接部署到 Vercel（`vercel.json` 已开 cleanUrls），把 `dingjunn.com` 解析过去即可。
