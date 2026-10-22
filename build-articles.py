#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Obsidian 库里的「产品创意案例知识库」编译成站点栏目 /articles/（文章页里的拆解系列）。

用法:
    python3 build-articles.py

源目录默认指向本机 Obsidian 库（可用环境变量 VAULT_DIR 覆盖）。
新增案例的流程: 在库里加一个「编号 标题.md」→ 重跑本脚本 → 提交。

脚本只读取笔记，不改动 Obsidian 库里的任何文件。
"""

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
VAULT = Path(
    os.environ.get(
        "VAULT_DIR",
        "/Users/Admin/Downloads/Downloads/呆胶布/呆胶布/产品创意案例知识库",
    )
)
OUT = SITE / "articles"
ASSETS_OUT = OUT / "assets"
ASSETS_SRC = VAULT / "_assets"

# 手写 slug，比自动音译稳定，也方便分享链接
SLUGS = {
    "01": "dog-cup",
    "02": "silicone-stand",
    "03": "beach-umbrella",
    "04": "dissolvable-wash",
    "05": "poop-scooper",
    "06": "blush-glasses",
    "07": "pot-lid",
    "08": "cat-paw-sunscreen",
    "09": "v-teacup",
    "10": "van-gogh-cup",
    "11": "paper-sakura",
    "12": "nose-sweet-cup",
    "13": "flower-clip",
    "14": "lego-tile",
    "15": "dragonball-light",
    "16": "rainbow-bath-bomb",
    "17": "ar-menu",
}

# 字段归一化：笔记里同一栏有几种写法
FIELDS = [
    ("用户", "user"),
    ("场景", "scene"),
    ("当前方案痛点", "pain"),
    ("痛点", "pain"),
    ("创意方案", "idea"),
    ("核心价值", "value"),
    ("方案短板 & 边界", "limit"),
    ("方案短板与边界", "limit"),
    ("方案短板&边界", "limit"),
    ("底层设计思想", "principle"),
    ("底层范式", "principle"),
    ("同思想延伸案例", "analogy"),
    ("同范式延伸案例", "analogy"),
    ("标签", "tags"),
    ("AI 机会迁移", "ai"),
    ("AI机会迁移", "ai"),
    ("产品图片", "image"),
]
FIELD_MAP = dict(FIELDS)

LABELS = {
    "user": "用户",
    "scene": "场景",
    "pain": "当前方案痛点",
    "idea": "创意方案",
    "value": "核心价值",
    "limit": "方案短板与边界",
    "principle": "底层设计思想",
    "analogy": "同思想延伸案例",
    "ai": "AI 机会迁移",
}

ORDER = ["user", "scene", "pain", "idea", "value", "limit", "principle", "analogy", "ai"]

COSMOS = """  <div class="cosmos" aria-hidden="true">
    <div class="nebula nebula-a" data-depth="0.08"></div>
    <div class="nebula nebula-b" data-depth="0.14"></div>
    <div class="stars stars-a" data-depth="0.22"></div>
    <div class="stars stars-b" data-depth="0.34"></div>
    <div class="stars stars-c" data-depth="0.48"></div>
    <div class="meteor-shower">
      <span class="shoot shoot-1"></span>
      <span class="shoot shoot-2"></span>
      <span class="shoot shoot-3"></span>
      <span class="shoot shoot-4"></span>
      <span class="shoot shoot-5"></span>
      <span class="shoot shoot-6"></span>
      <span class="shoot shoot-7"></span>
      <span class="shoot shoot-8"></span>
      <span class="shoot shoot-9"></span>
      <span class="shoot shoot-10"></span>
      <span class="shoot shoot-11"></span>
      <span class="shoot shoot-12"></span>
    </div>
  </div>"""

NAV = """  <header class="nav">
    <a class="nav-brand" href="../index.html">Dingjun</a>
    <nav class="nav-links" aria-label="主导航">
      <a href="../projects.html">项目</a>
      <a class="is-active" href="index.html">文章</a>
      <a href="../thoughts.html">思考</a>
      <a href="../about.html">关于</a>
    </nav>
  </header>"""


def shell(title, desc, body, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{desc}" />
  <title>{title} · Dingjun</title>
  <link rel="stylesheet" href="../styles.css" />
  <link rel="stylesheet" href="notes.css" />{extra_css}
</head>
<body>
{COSMOS}

{NAV}

{body}

  <footer class="foot">
    <span>&copy; <span id="year"></span> Dingjun</span>
    <a href="../index.html">回到首页</a>
  </footer>

  <script src="../script.js"></script>
</body>
</html>
"""


def inline(text):
    """转义 + 还原笔记里的轻标记。"""
    s = html.escape(text.strip())
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"==(.+?)==", r"<mark>\1</mark>", s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    return s


def blocks(text):
    """段落 + 列表混排。"""
    items, buf, out = [], [], []

    def flush_para():
        if buf:
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
            buf.clear()

    def flush_list():
        if items:
            lis = "".join(f"<li>{inline(i)}</li>" for i in items)
            out.append(f"<ul>{lis}</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip().lstrip("\t").strip()
        if not line or line in ("-", "*"):
            flush_para()
            flush_list()
            continue
        m = re.match(r"^(?:[-*]|\d+[.、])\s*(.+)$", line)
        if m:
            flush_para()
            items.append(m.group(1))
        else:
            flush_list()
            buf.append(line)
    flush_para()
    flush_list()
    return "\n        ".join(out)


def parse(path):
    text = path.read_text(encoding="utf-8")
    # ## 用户 / ### 产品图片 这类 markdown 小标题统一折成【用户】
    text = re.sub(r"(?m)^#{2,4}\s*(.+?)\s*$", r"【\1】", text)

    images = []

    def take_image(m):
        images.append(m.group(1).strip())
        return ""

    text = re.sub(r"!\[\[([^\]]+)\]\]", take_image, text)

    parts = re.split(r"【([^】]{1,20})】", text)
    data = {}
    for i in range(1, len(parts) - 1, 2):
        key = FIELD_MAP.get(parts[i].strip())
        if key and key not in data:
            data[key] = parts[i + 1]

    tags = []
    for t in re.split(r"[#\s]+", data.get("tags", "")):
        t = t.strip()
        if t:
            tags.append(t)
    data["tags"] = tags
    data["images"] = [re.sub(r"\|.*$", "", n) for n in images]
    return data


def optimize(src_name, out_stem, index):
    src = ASSETS_SRC / src_name
    if not src.exists():
        print(f"  ! 缺图: {src_name}")
        return None
    ext = ".png" if src.suffix.lower() == ".png" and src.stat().st_size < 120_000 else ".jpg"
    dst = ASSETS_OUT / f"{out_stem}-{index}{ext}"
    if ext == ".jpg":
        subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
             "-Z", "1400", str(src), "--out", str(dst)],
            check=True, capture_output=True,
        )
    else:
        shutil.copyfile(src, dst)
    return dst.name


def build_case(num, title, slug, data, prev_case, next_case):
    figs = []
    for i, name in enumerate(data["images"], 1):
        out = optimize(name, slug, i)
        if out:
            figs.append(f'<img src="assets/{out}" alt="{html.escape(title)} 的产品图" loading="lazy" />')

    head_img = f'\n      <figure class="td-figure">{"".join(figs[:1])}</figure>' if figs else ""
    tail_img = (
        f'\n      <figure class="td-figure td-figure--sm">{"".join(figs[1:])}</figure>'
        if len(figs) > 1
        else ""
    )

    tag_html = ""
    if data["tags"]:
        chips = "".join(f"<li>{html.escape(t)}</li>" for t in data["tags"])
        tag_html = f'\n      <ul class="tags td-tags">{chips}</ul>'

    body = []
    for key in ORDER:
        if key not in data:
            continue
        content = blocks(data[key])
        if not content:
            continue
        cls = "td-field"
        if key == "principle":
            cls += " td-field--key"
        elif key == "ai":
            cls += " td-field--key td-field--ai"
        body.append(
            f'      <section class="{cls}">\n'
            f'        <h2>{LABELS[key]}</h2>\n'
            f'        {content}\n'
            f"      </section>"
        )
        if key == "analogy" and tail_img:
            body.append(tail_img.strip())

    pager = []
    if prev_case:
        pager.append(
            f'<a class="td-pager-prev" href="{prev_case[2]}.html">'
            f'<span>上一件</span>{html.escape(prev_case[1])}</a>'
        )
    if next_case:
        pager.append(
            f'<a class="td-pager-next" href="{next_case[2]}.html">'
            f'<span>下一件</span>{html.escape(next_case[1])}</a>'
        )
    pager_html = f'\n    <nav class="td-pager">{"".join(pager)}</nav>' if pager else ""

    main = f"""  <main class="page page-narrow">
    <p class="td-crumb"><a href="ideas.html">&larr; 产品创意拆解</a></p>

    <header class="article-head">
      <p class="eyebrow">Teardown {num}</p>
      <h1>{html.escape(title)}</h1>{tag_html}
    </header>{head_img}

    <div class="td-body">
{chr(10).join(body)}
    </div>{pager_html}
  </main>"""

    value = re.sub(r"\s+", "", data.get("value", ""))[:70]
    return shell(title, html.escape(value or title), main)


SYSTEMS = [
    ("01", "检索", "hybrid-retrieval.html", "为什么我给 BM25 留了 35%",
     "向量负责语义，BM25 负责型号和数值。两路分数怎么合、为什么没选 RRF、为什么还没上 Rerank。",
     ["NutriFit", "混合检索", "取舍"]),
    ("02", "记忆", "memory-routing.html", "记忆最难的不是存，是决定什么时候别读",
     "七种意图对应七套开关。分诊时强制关掉记忆，传了新报告时让记忆退到对照位。",
     ["医路通", "意图路由", "证据优先级"]),
    ("03", "合规", "triage-rules.html", "合规不写进提示词，写进后处理",
     "「不能说确诊」放在提示词里等于没有约束。真正拦住它的，是跑在模型输出之后的一层确定性代码。",
     ["医路通", "输出护栏", "风险分层"]),
]


def build_index(cases):
    """文章总入口：只放两个系列，不铺开全部文章。"""
    n = len(cases)
    main = f"""  <main class="page">
    <header class="page-head">
      <p class="eyebrow">Writing</p>
      <h1>文章</h1>
      <p class="page-desc">两个系列，各写各的。一个拆自己做的系统，一个拆别人的产品。</p>
    </header>

    <div class="folders">
      <a class="folder" href="systems.html">
        <span class="folder-no">系列 01</span>
        <h2>系统拆解</h2>
        <p class="folder-desc">自己项目里的设计决定：为什么这么选、踩到了什么、哪笔账还没还。只写能对着代码核实的部分。</p>
        <p class="folder-pick">先看：为什么我给 BM25 留了 35%</p>
        <span class="folder-go">{len(SYSTEMS)} 篇 &rarr;</span>
      </a>

      <a class="folder" href="ideas.html">
        <span class="folder-no">系列 02</span>
        <h2>产品创意拆解</h2>
        <p class="folder-desc">从日常小产品里抽出一条能搬到别处的思路，再看它长到 AI 产品上会变成什么机会。</p>
        <p class="folder-pick">先看：狗狗的随行杯</p>
        <span class="folder-go">{n} 篇 &rarr;</span>
      </a>
    </div>
  </main>"""

    return shell("文章", "两个系列：系统拆解与产品创意拆解。", main)


def build_series_systems():
    rows = "".join(
        f"""      <article class="list-item">
        <div class="list-meta">
          <span>{num}</span>
          <span class="cat">{cat}</span>
        </div>
        <h2><a href="../systems/{slug}">{title}</a></h2>
        <p>{desc}</p>
        <ul class="tags">{''.join(f'<li>{t}</li>' for t in tags)}</ul>
      </article>
"""
        for num, cat, slug, title, desc, tags in SYSTEMS
    )

    main = f"""  <main class="page">
    <p class="td-crumb"><a href="index.html">&larr; 文章</a></p>

    <header class="page-head">
      <p class="eyebrow">系列 01</p>
      <h1>系统拆解</h1>
      <p class="page-desc">不写教程，只写当时为什么这么决定、事后发现哪里没想清楚。</p>
    </header>

    <div class="list">
{rows}    </div>
  </main>"""

    return shell("系统拆解", "自己项目里的设计决定、取舍和踩到的坑。", main)


def build_series_ideas(cases):
    n = len(cases)
    rows = []
    for num, title, slug, data in cases:
        cat = data["tags"][-1] if data["tags"] else "案例"
        value = re.sub(r"\s+", " ", data.get("value", "")).strip()
        chips = "".join(f"<li>{html.escape(t)}</li>" for t in data["tags"])
        rows.append(
            f"""      <article class="list-item">
        <div class="list-meta">
          <span>{num}</span>
          <span class="cat">{html.escape(cat)}</span>
        </div>
        <h2><a href="{slug}.html">{html.escape(title)}</a></h2>
        <p>{inline(value)}</p>
        <ul class="tags">{chips}</ul>
      </article>"""
        )

    main = f"""  <main class="page">
    <p class="td-crumb"><a href="index.html">&larr; 文章</a></p>

    <header class="page-head">
      <p class="eyebrow">系列 02</p>
      <h1>产品创意拆解</h1>
      <p class="page-desc">同一张表拆 {n} 件小产品：它替谁省掉了什么成本，抽掉实体之后还剩哪条可复用的思路。</p>
      <p class="td-method-link"><a href="method.html">先看我是怎么拆的 &rarr;</a></p>
    </header>

    <div class="list">
{chr(10).join(rows)}
    </div>
  </main>"""

    return shell("产品创意拆解", f"{n} 件小产品，同一套可迁移的分析框架。", main)


METHOD_STEPS = [
    ("用户", "是谁？精准人群，描述人群特征与诉求，不要写「所有人」。"),
    ("场景", "用户正在做什么任务？限定时间与环境，不要宽泛。"),
    ("当前方案痛点", "现在用户怎么解决？有哪些约束、麻烦、别扭的地方？"),
    ("创意方案", "核心设计是什么？把哪些组件或能力做了重组、集成？"),
    ("核心价值", "帮用户减少了哪一类成本：携带、切换、时间、浪费？"),
    ("方案短板与边界", "什么场景下这个创意不好用？副作用是什么？"),
    ("底层设计思想", "抽掉产品实体，提炼一句可跨行业复用的通用模型。"),
    ("同思想延伸案例", "在完全不同的品类里，找到同一条范式已经成立的产品。"),
    ("AI 机会迁移", "把这条范式搬到 AI 产品上，可以是什么机会？"),
]


def build_method(cases_count):
    steps = []
    for i, (name, hint) in enumerate(METHOD_STEPS, 1):
        steps.append(
            f"""      <li class="td-step">
        <span class="td-step-no">{i:02d}</span>
        <div>
          <h2>{name}</h2>
          <p>{hint}</p>
        </div>
      </li>"""
        )

    main = f"""  <main class="page page-narrow">
    <p class="td-crumb"><a href="ideas.html">&larr; 产品创意拆解</a></p>

    <header class="article-head">
      <p class="eyebrow">Method</p>
      <h1>我是怎么拆的</h1>
      <p class="page-desc">一件产品值不值得学，不在于它多新奇，而在于把实体抽掉之后，还剩不剩一句能搬到别处用的话。这张表就是为了逼出那句话。</p>
    </header>

    <div class="prose td-method">
      <p>前九栏是同一个问题被问了九次：它替谁、在什么时刻、省掉了哪一种成本，代价又是什么。最后两栏才是这套笔记真正的目的——先在不同品类里验证这条思路成立，再把它搬到 AI 产品上。</p>
    </div>

    <ol class="td-steps">
{chr(10).join(steps)}
    </ol>

    <p class="td-method-link"><a href="ideas.html">看 {cases_count} 个案例 -&gt;</a></p>
  </main>"""

    return shell("我是怎么拆的", "一套用于拆解产品创意的九栏框架，以及把它迁移到 AI 产品的方法。", main)


def main():
    if not VAULT.exists():
        sys.exit(f"找不到笔记库: {VAULT}")

    for d in (OUT, ASSETS_OUT):
        if not d.is_dir():
            d.mkdir(parents=True)

    files = sorted(p for p in VAULT.glob("*.md") if re.match(r"^\d{2}\s", p.stem))
    cases = []
    for p in files:
        m = re.match(r"^(\d{2})\s+(.+)$", p.stem)
        num, title = m.group(1), m.group(2)
        if num == "00":
            continue
        slug = SLUGS.get(num)
        if not slug:
            print(f"  ! 没有配 slug，跳过: {p.name}")
            continue
        cases.append((num, title, slug, parse(p)))

    cases.sort(key=lambda c: c[0])
    print(f"解析到 {len(cases)} 个案例")

    for i, (num, title, slug, data) in enumerate(cases):
        prev_case = cases[i - 1] if i > 0 else None
        next_case = cases[i + 1] if i < len(cases) - 1 else None
        (OUT / f"{slug}.html").write_text(
            build_case(num, title, slug, data, prev_case, next_case), encoding="utf-8"
        )
        print(f"  {num} {title} -> {slug}.html")

    (OUT / "index.html").write_text(build_index(cases), encoding="utf-8")
    (OUT / "systems.html").write_text(build_series_systems(), encoding="utf-8")
    (OUT / "ideas.html").write_text(build_series_ideas(cases), encoding="utf-8")
    (OUT / "method.html").write_text(build_method(len(cases)), encoding="utf-8")
    print(
        "完成: articles/index.html（两个系列入口）、systems.html、ideas.html、"
        f"method.html 及 {len(cases)} 个详情页"
    )


if __name__ == "__main__":
    main()
