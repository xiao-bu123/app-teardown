# -*- coding: utf-8 -*-
"""Renderer for App page-tree research reports.

Consumes a *data module* (see report_data.example.py) and emits:
  * <slug>.html          single-file report, screenshots embedded as base64 JPEG
  * <slug>.md            Markdown backup, images referenced from ./shots
  * feishu_<slug>.md     same content but with @./shots/... image paths (lark-cli)

Data module contract (module-level names):
  SLUG        str            file stem, e.g. "waixingzai"
  TITLE       str
  SUB         str
  META        [(label, value_html)]
  CONCLUSIONS [(headline, paragraph)]
  TREE        str            ASCII page tree (will be escaped)
  SECTIONS    [{id,num,title,intro,pages:[PAGE]}]
  PAGE        {code,name,path,kind,img,desc,points[],next,limit}
  CLEAN       [row]          first row is the header (页面路径/类型/...)
  TECH        [(dimension, conclusion)]
  OBSERVE     [(title, paragraph)]
  METHOD      [str]
"""
import base64
import html as H
import io
import json
import os

_cache = {}


def _b64(root, img_dir, name, maxw=0, quality=84):
    key = (root, img_dir, name, maxw, quality)
    if key not in _cache:
        path = os.path.join(root, img_dir, name + ".jpg")
        if maxw:
            try:
                from PIL import Image
                im = Image.open(path).convert("RGB")
                if im.width > maxw:
                    im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=quality, optimize=True)
                _cache[key] = base64.b64encode(buf.getvalue()).decode()
            except Exception:
                with open(path, "rb") as f:
                    _cache[key] = base64.b64encode(f.read()).decode()
        else:
            with open(path, "rb") as f:
                _cache[key] = base64.b64encode(f.read()).decode()
    return _cache[key]


def _esc(s):
    return H.escape(str(s), quote=False)


def _img(root, img_dir, name, alt, cls="shot", maxw=0, quality=84):
    return (f'<img class="{cls}" loading="lazy" src="data:image/jpeg;base64,'
            f'{_b64(root, img_dir, name, maxw, quality)}" alt="{_esc(alt)}">')


HTML_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --bg:#0b0b10; --panel:#14141c; --panel2:#1b1b26; --line:#2a2a3a; --txt:#e8e8f2; --dim:#9a9ab0;
    --accent:#a06bff; --accent2:#7c4dff; --red:#ff5c5c; --green:#3ddc97; --amber:#ffb020;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:radial-gradient(1200px 600px at 70% -10%, #241a3d 0%, var(--bg) 55%) no-repeat, var(--bg);
         color:var(--txt); font:15px/1.7 "PingFang SC","Microsoft YaHei",system-ui,-apple-system,sans-serif; }}
  a {{ color:var(--accent); text-decoration:none; }}
  .wrap {{ display:flex; }}
  aside {{ position:sticky; top:0; align-self:flex-start; width:280px; height:100vh; overflow:auto;
           padding:22px 14px 40px; border-right:1px solid var(--line); background:rgba(10,10,16,.85); backdrop-filter:blur(8px); }}
  aside .brand {{ font-weight:700; font-size:15px; margin:0 8px 4px; }}
  aside .brand small {{ display:block; color:var(--dim); font-weight:400; font-size:12px; margin-top:4px; }}
  .nav-sec {{ display:block; margin:16px 8px 4px; font-size:13px; color:var(--amber); font-weight:600; }}
  .nav-page {{ display:block; margin:1px 8px; padding:3px 8px; font-size:12.5px; color:var(--dim); border-radius:6px; }}
  .nav-page:hover {{ background:var(--panel2); color:var(--txt); }}
  main {{ flex:1; min-width:0; padding:40px 48px 100px; max-width:1180px; }}
  header.hero h1 {{ font-size:30px; line-height:1.35; margin:0 0 8px; letter-spacing:.5px; }}
  header.hero .sub {{ color:var(--dim); font-size:14px; }}
  .stats {{ display:flex; gap:14px; margin:26px 0 6px; flex-wrap:wrap; }}
  .stat {{ flex:1; min-width:130px; background:linear-gradient(160deg,#1d1630,#14141c); border:1px solid var(--line);
           border-radius:14px; padding:14px 16px; }}
  .stat b {{ display:block; font-size:26px; color:var(--accent); }}
  .stat span {{ color:var(--dim); font-size:12.5px; }}
  h2 {{ font-size:21px; margin:0; }}
  .sec {{ margin-top:56px; scroll-margin-top:20px; }}
  .sec-head {{ display:flex; align-items:center; gap:12px; border-bottom:1px solid var(--line); padding-bottom:10px; }}
  .sec-num {{ display:inline-flex; width:32px; height:32px; align-items:center; justify-content:center; border-radius:9px;
             background:linear-gradient(160deg,var(--accent),var(--accent2)); font-weight:700; }}
  .intro {{ color:var(--dim); margin:14px 0 22px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:20px; }}
  .card {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:16px; scroll-margin-top:20px;
           transition:border-color .2s; }}
  .card:hover {{ border-color:#3d3260; }}
  .card-head {{ display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; }}
  .card-head h3 {{ margin:0; font-size:15.5px; }}
  .code {{ font:600 11px/1 ui-monospace,Consolas,monospace; color:#0b0b10; background:var(--accent);
           padding:4px 6px; border-radius:5px; }}
  .kind {{ font-size:11.5px; color:var(--amber); border:1px solid #3a2f16; background:#1c1709; padding:2px 6px; border-radius:5px; }}
  .path {{ color:var(--dim); font-size:12px; margin:6px 0 12px; }}
  figure {{ margin:0 0 12px; }}
  .shot {{ width:100%; height:auto; border-radius:10px; border:1px solid #26263a; cursor:zoom-in; display:block; }}
  figcaption {{ color:#6f6f88; font-size:11.5px; margin-top:6px; text-align:center; }}
  .desc {{ margin:0 0 10px; font-size:14px; color:#d6d6e6; }}
  .pts {{ margin:0 0 12px; padding-left:18px; color:#c9c9dc; font-size:13.4px; }}
  .pts li {{ margin:5px 0; }}
  .io {{ font-size:12.6px; color:var(--dim); border-top:1px dashed #262637; padding-top:7px; margin-top:7px; }}
  .io .lbl {{ display:inline-block; color:var(--txt); background:#23233a; border-radius:4px; padding:0 6px; margin-right:8px; font-size:11.5px; }}
  .concl-wrap {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:16px; margin-top:18px; }}
  .concl {{ background:linear-gradient(160deg,#1a1428,#111119); border:1px solid #2f2745; border-radius:14px; padding:14px 16px; }}
  .concl h3 {{ margin:0 0 6px; font-size:14.5px; color:#cbb6ff; }}
  .concl p {{ margin:0; font-size:13.4px; color:#c6c6d8; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:14px; }}
  th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
  thead th {{ background:#1c1c2a; color:#cfc4ff; font-weight:600; }}
  tbody tr:nth-child(even) {{ background:#111119; }}
  table.meta th {{ width:96px; color:var(--dim); font-weight:500; background:#14141e; }}
  pre.tree {{ background:#0f0f16; border:1px solid var(--line); border-radius:14px; padding:18px; overflow:auto;
              font:12.6px/1.75 ui-monospace,Consolas,"Cascadia Mono",monospace; color:#cfd0e6; }}
  .note {{ border-left:3px solid var(--accent); background:#151222; padding:12px 16px; border-radius:0 10px 10px 0; color:#cfc8e6; font-size:13.5px; }}
  footer {{ margin-top:60px; color:#5f5f78; font-size:12px; border-top:1px solid var(--line); padding-top:18px; }}
  #lb {{ position:fixed; inset:0; background:rgba(0,0,0,.92); display:none; align-items:center; justify-content:center; z-index:99; cursor:zoom-out; }}
  #lb img {{ max-width:92vw; max-height:92vh; border-radius:10px; }}
  /* structure map */
  .win {{ border:1px solid #2f2745; border-radius:16px; background:linear-gradient(160deg,#151024,#0f0f17); padding:14px; margin-top:8px; }}
  .win-bar {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; padding:6px 8px 12px; border-bottom:1px dashed #2c2c40; }}
  .tabpill {{ border:1px solid #3a2f5c; background:#1c1730; color:#d9ccff; border-radius:999px; padding:5px 12px; font-size:12.5px; }}
  .lanes {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; margin-top:14px; }}
  .lane {{ background:#12121b; border:1px solid #262638; border-radius:14px; padding:10px; }}
  .lane-head {{ font-size:12.5px; color:#cfc4ff; font-weight:600; padding:4px 4px 8px; border-bottom:1px solid #262638; margin-bottom:4px; }}
  .chain {{ padding-left:12px; border-left:1px dashed #33334c; margin-left:4px; }}
  .node {{ position:relative; display:block; margin:9px 0; padding:7px 9px; border-radius:10px; background:#181822; border:1px solid #2a2a3a; color:inherit; text-decoration:none; transition:.15s; }}
  .node:hover {{ background:#201a33; border-color:#4b3a7a; }}
  .node::before {{ content:""; position:absolute; left:-14px; top:17px; width:10px; height:1px; background:#3a3a55; }}
  .node b {{ display:block; font-size:12.4px; font-weight:600; color:#e6e0ff; }}
  .node span {{ display:block; font-size:11px; color:#8f8fa8; line-height:1.45; margin-top:2px; }}
  .k-func {{ border-left:3px solid var(--accent); }}
  .k-content {{ border-left:3px solid var(--green); }}
  .k-pay {{ border-left:3px solid var(--amber); }}
  .k-sys {{ border-left:3px solid #5c9dff; }}
  .rowlabel {{ margin:18px 2px 6px; font-size:12.5px; color:var(--dim); }}
  .flat {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(215px,1fr)); gap:10px; }}
  .flat .node::before {{ display:none; }}
  .legend {{ display:flex; gap:16px; flex-wrap:wrap; margin:14px 2px 2px; font-size:12px; color:var(--dim); }}
  .legend i {{ display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:6px; vertical-align:middle; }}
  @media (max-width:900px) {{ aside {{ display:none; }} main {{ padding:24px 16px 80px; }} .grid {{ grid-template-columns:1fr; }} }}
  @media print {{
    aside, #lb {{ display:none !important; }}
    body {{ background:#fff; color:#111; }}
    .card, .concl, .stat {{ break-inside:avoid; background:#fff; border-color:#ddd; }}
    .shot {{ max-width:60%; }}
  }}
</style>
</head>
<body>
<div class="wrap">
<aside>
  <div class="brand">{brand}<small>{brand_sub}</small></div>
  <a class="nav-sec" href="#top">概览与结论</a>
  <a class="nav-page" href="#tree">页面层级树（全图）</a>
  <a class="nav-page" href="#index">页面索引表</a>
  {nav}
  <a class="nav-sec" href="#clean">功能清单表</a>
  <a class="nav-sec" href="#tech">技术观察</a>
  <a class="nav-sec" href="#observe">产品判断</a>
  <a class="nav-sec" href="#method">方法与边界</a>
</aside>
<main id="top">
  <header class="hero">
    <h1>{title}</h1>
    <div class="sub">{sub}</div>
    <div class="stats">{stats}</div>
  </header>

  <section class="sec" id="meta">
    <div class="sec-head"><span class="sec-num">i</span><h2>调研对象与基本盘</h2></div>
    <table class="meta">{meta_rows}</table>
  </section>

  <section class="sec" id="concl">
    <div class="sec-head"><span class="sec-num">✳</span><h2>先看结论</h2></div>
    <div class="concl-wrap">{concl}</div>
  </section>

  {map_sec}

  <section class="sec" id="tree">
    <div class="sec-head"><span class="sec-num">⌘</span><h2>页面层级树（全图）</h2></div>
    <p class="intro">括号内为层级（L0 一级 / L1 二级 / L2 三级）；箭头表示点击后的跳转。</p>
    <pre class="tree">{tree}</pre>
  </section>

  <section class="sec" id="index">
    <div class="sec-head"><span class="sec-num">≡</span><h2>页面索引（{page_count} 个页面/状态）</h2></div>
    <table>
      <thead><tr><th>编号</th><th>页面</th><th>路径</th><th>类型</th><th>一句话</th></tr></thead>
      <tbody>{index_rows}</tbody>
    </table>
  </section>
  {sections}

  <section class="sec" id="clean">
    <div class="sec-head"><span class="sec-num">▤</span><h2>功能清单表</h2></div>
    <table>
      <thead><tr>{clean_head}</tr></thead>
      <tbody>{clean_rows}</tbody>
    </table>
  </section>

  <section class="sec" id="tech">
    <div class="sec-head"><span class="sec-num">⚙</span><h2>技术观察</h2></div>
    <table class="meta">{tech_rows}</table>
  </section>
  {extra_tables}

  <section class="sec" id="observe">
    <div class="sec-head"><span class="sec-num">◎</span><h2>产品判断</h2></div>
    <div class="concl-wrap">{observe}</div>
  </section>

  <section class="sec" id="method">
    <div class="sec-head"><span class="sec-num">✓</span><h2>调研方法与安全边界</h2></div>
    <ul class="pts">{method}</ul>
    <p class="note">{note}</p>
  </section>

  <footer>{footer}</footer>
</main>
</div>
<div id="lb"><img alt=""></div>
<script>
  const lb = document.getElementById('lb'), lbImg = lb.querySelector('img');
  document.querySelectorAll('.shot').forEach(el => el.addEventListener('click', () => {{
    lbImg.src = el.src; lb.style.display = 'flex';
  }}));
  lb.addEventListener('click', () => {{ lb.style.display = 'none'; }});
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') lb.style.display = 'none'; }});
</script>
</body>
</html>"""


def _map_html(data):
    """Optional visual structure map. Data may provide LANES / ROWS / TABS / MAP_INTRO."""
    lanes = getattr(data, "LANES", None)
    if not lanes:
        return ""

    def node(n):
        label, sub, kind, goto = (list(n) + ["", "", "func", ""])[:4]
        cls = "k-" + str(kind or "func")
        if goto:
            return (f'<a class="node {cls}" href="#{_esc(goto)}">'
                    f'<b>{_esc(label)}</b><span>{_esc(sub)}</span></a>')
        return f'<div class="node {cls}"><b>{_esc(label)}</b><span>{_esc(sub)}</span></div>'

    lane_html = "".join(
        f'<div class="lane"><div class="lane-head">{_esc(l["title"])}</div>'
        f'<div class="chain">{"".join(node(n) for n in l.get("nodes", []))}</div></div>'
        for l in lanes)
    rows = "".join(
        f'<div class="rowlabel">{_esc(r["label"])}</div>'
        f'<div class="flat">{"".join(node(n) for n in r.get("nodes", []))}</div>'
        for r in getattr(data, "ROWS", []))
    tabs = "".join(f'<span class="tabpill">{_esc(t)}</span>' for t in getattr(data, "TABS", []))
    intro = getattr(data, "MAP_INTRO", "一个窗口，多条并列主线；下方是弹窗层与隐藏层。颜色区分内容/功能/付费/系统。")
    return f"""<section class="sec" id="map">
    <div class="sec-head"><span class="sec-num">⌗</span><h2>页面结构图（点节点跳到对应卡片）</h2></div>
    <p class="intro">{_esc(intro)}</p>
    <div class="win"><div class="win-bar">{tabs}</div><div class="lanes">{lane_html}</div>{rows}</div>
    <div class="legend"><span><i style="background:#a06bff"></i>功能 / 交互</span>
      <span><i style="background:#3ddc97"></i>内容 / 列表</span>
      <span><i style="background:#ffb020"></i>付费 / 变现</span>
      <span><i style="background:#5c9dff"></i>系统 / 内核</span></div>
  </section>"""


def _meta_rows(data):
    return "".join(f"<tr><th>{_esc(k)}</th><td>{v}</td></tr>" for k, v in data.META)


def _concl(pairs):
    return "".join(f'<div class="concl"><h3>{_esc(c)}</h3><p>{_esc(t)}</p></div>' for c, t in pairs)


def _index_rows(pages):
    return "".join(
        f'<tr><td><a href="#{p["code"]}">{p["code"]}</a></td><td>{_esc(p["name"])}</td>'
        f'<td>{_esc(p["path"])}</td><td>{_esc(p["kind"])}</td><td>{_esc(p["desc"][:46])}…</td></tr>'
        for p in pages)


def _index_cards(pages):
    return "".join(
        f'<div class="mi"><a class="mi-code" href="#{p["code"]}">{p["code"]}</a>'
        f'<div class="mi-body"><b>{_esc(p["name"])}</b>'
        f'<span>{_esc(p["path"])} · {_esc(p["kind"])}</span></div></div>'
        for p in pages)


def _sections_html(data, root, img_dir, maxw=0, quality=84, card_cls="card"):
    out = []
    for s in data.SECTIONS:
        cards = []
        for p in s["pages"]:
            pts = "".join(f"<li>{_esc(x)}</li>" for x in p["points"])
            cards.append(f"""
      <article class="{card_cls}" id="{p['code']}">
        <div class="card-head">
          <span class="code">{p['code']}</span>
          <h3>{_esc(p['name'])}</h3>
          <span class="kind">{_esc(p['kind'])}</span>
        </div>
        <div class="path">{_esc(p['path'])}</div>
        <figure>{_img(root, img_dir, p['img'], p['name'], maxw=maxw, quality=quality)}
        <figcaption>{_esc(p['name'])} · 实机截图</figcaption></figure>
        <p class="desc">{_esc(p['desc'])}</p>
        <ul class="pts">{pts}</ul>
        <div class="io"><span class="lbl">跳转</span>{_esc(p['next'])}</div>
        <div class="io"><span class="lbl">限制</span>{_esc(p['limit'])}</div>
      </article>""")
        out.append(f"""
    <section class="sec" id="{s['id']}">
      <div class="sec-head"><span class="sec-num">{s['num']}</span><h2>{_esc(s['title'])}</h2></div>
      <p class="intro">{_esc(s['intro'])}</p>
      <div class="grid">{''.join(cards)}</div>
    </section>""")
    return "".join(out)


def _clean_table(data):
    head = "".join(f"<th>{_esc(c)}</th>" for c in data.CLEAN[0])
    rows = "".join("<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>" for row in data.CLEAN[1:])
    return head, rows


def _extra_tables_html(data, minw=0):
    out = []
    for t in getattr(data, "EXTRA_TABLES", []):
        head = "".join(f"<th>{_esc(c)}</th>" for c in t["head"])
        rows = "".join("<tr>" + "".join(f"<td>{_esc(c)}</td>" for c in row) + "</tr>" for row in t["rows"])
        style = f' style="min-width:{minw}px"' if minw else ""
        out.append(f"""
  <section class="sec" id="tbl-{_esc(t.get('id', ''))}">
    <div class="sec-head"><span class="sec-num">▦</span><h2>{_esc(t['title'])}</h2></div>
    <table{style}><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>
  </section>""")
    return "".join(out)


def _tech_rows(data):
    return "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in data.TECH)


def _observe(data):
    return "".join(f'<div class="concl"><h3>{_esc(t)}</h3><p>{_esc(d)}</p></div>' for t, d in data.OBSERVE)


def _method(data):
    return "".join(f"<li>{_esc(m)}</li>" for m in data.METHOD)


def build_html(data, root):
    img_dir = getattr(data, "IMG_DIR", "shots")
    pages = [p for s in data.SECTIONS for p in s["pages"]]

    nav = []
    if getattr(data, "LANES", None):
        nav.append('<a class="nav-page" href="#map">页面结构图</a>')
    for s in data.SECTIONS:
        nav.append(f'<a class="nav-sec" href="#{s["id"]}">{s["num"]}. {_esc(s["title"])}</a>')
        for p in s["pages"]:
            nav.append(f'<a class="nav-page" href="#{p["code"]}">{p["code"]} {_esc(p["name"])}</a>')

    stats = getattr(data, "HERO_STATS", None)
    if not stats:
        tabs = getattr(data, "TAB_COUNT", "")
        stats = [(str(len(pages)), "页面 / 状态"), (tabs, "底部 Tab"), (str(len(pages)), "张真机截图")]

    clean_head, clean_rows = _clean_table(data)

    html = HTML_SHELL.format(
        title=_esc(data.TITLE), sub=_esc(data.SUB), brand=_esc(getattr(data, "BRAND", data.TITLE[:12])),
        brand_sub=_esc(getattr(data, "BRAND_SUB", "")),
        stats="".join(f'<div class="stat"><b>{_esc(v)}</b><span>{_esc(k)}</span></div>' for v, k in stats),
        meta_rows=_meta_rows(data), concl=_concl(data.CONCLUSIONS), tree=_esc(data.TREE), nav="".join(nav),
        map_sec=_map_html(data),
        page_count=len(pages), index_rows=_index_rows(pages),
        sections=_sections_html(data, root, img_dir),
        clean_head=clean_head, clean_rows=clean_rows, tech_rows=_tech_rows(data),
        extra_tables=_extra_tables_html(data),
        observe=_observe(data), method=_method(data),
        note=_esc(getattr(data, "NOTE", "")),
        footer=_esc(getattr(data, "FOOTER", "")),
    )

    out = os.path.join(root, data.SLUG + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


MOBILE_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0b10">
<title>{title}</title>
<style>
  :root {{ --bg:#0b0b10; --panel:#14141c; --line:#2a2a3a; --txt:#e8e8f2; --dim:#9a9ab0;
           --accent:#a06bff; --green:#3ddc97; --amber:#ffb020; }}
  * {{ box-sizing:border-box; -webkit-tap-highlight-color:transparent; }}
  body {{ margin:0; background:var(--bg); color:var(--txt);
          font:16px/1.78 "PingFang SC","Microsoft YaHei",system-ui,sans-serif;
          padding-bottom:64px; }}
  a {{ color:var(--accent); text-decoration:none; }}
  .m-top {{ padding:18px 16px 12px; background:linear-gradient(160deg,#241a3d,#0b0b10); }}
  .m-top h1 {{ margin:0 0 6px; font-size:21px; line-height:1.4; }}
  .m-top .sub {{ color:var(--dim); font-size:13px; }}
  .m-stats {{ display:flex; gap:10px; margin-top:14px; overflow-x:auto; padding-bottom:4px; }}
  .m-stat {{ flex:0 0 auto; background:#181822; border:1px solid var(--line); border-radius:12px; padding:8px 12px; }}
  .m-stat b {{ color:var(--accent); font-size:18px; margin-right:6px; }}
  .m-stat span {{ color:var(--dim); font-size:12px; }}
  nav.m-jump {{ position:sticky; top:0; z-index:20; display:flex; gap:8px; overflow-x:auto;
                padding:10px 12px; background:rgba(11,11,16,.94); backdrop-filter:blur(8px);
                border-bottom:1px solid var(--line); }}
  nav.m-jump a {{ flex:0 0 auto; font-size:13px; color:#d9ccff; border:1px solid #3a2f5c;
                  background:#1c1730; border-radius:999px; padding:6px 12px; }}
  main {{ padding:16px 14px 40px; }}
  section {{ margin:26px 0; scroll-margin-top:64px; }}
  h2 {{ font-size:18px; margin:0 0 12px; padding-left:10px; border-left:4px solid var(--accent); }}
  h3 {{ font-size:16px; }}
  .m-card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:12px; margin:14px 0; scroll-margin-top:70px; }}
  .m-card .code {{ font:600 11px/1 ui-monospace,Consolas,monospace; color:#0b0b10; background:var(--accent);
                   padding:4px 6px; border-radius:5px; margin-right:6px; }}
  .m-card .kind {{ font-size:11.5px; color:var(--amber); }}
  .m-card h3 {{ display:inline; margin:0; font-size:15.5px; }}
  .m-card .path {{ color:var(--dim); font-size:12.5px; margin:6px 0 10px; }}
  .m-card img {{ width:100%; border-radius:10px; display:block; border:1px solid #26263a; }}
  .m-card figcaption {{ color:#6f6f88; font-size:11.5px; text-align:center; margin:6px 0 8px; }}
  .m-card p, .m-card li, .cl p, .m-top h1 {{ overflow-wrap:anywhere; word-break:break-word; }}\n  .m-card p {{ font-size:14.5px; color:#d6d6e6; margin:8px 0; }}
  .m-card ul {{ padding-left:20px; margin:8px 0; color:#c9c9dc; font-size:14px; }}
  .m-card li {{ margin:6px 0; }}
  .m-card .io {{ font-size:13px; color:var(--dim); border-top:1px dashed #262637; padding-top:8px; margin-top:8px; }}
  .m-card .io .lbl {{ display:inline-block; color:var(--txt); background:#23233a; border-radius:4px; padding:0 6px; margin-right:6px; font-size:12px; }}
  .kv {{ width:100%; border-collapse:collapse; font-size:14px; table-layout:fixed; }}
  .kv th, .kv td {{ border-bottom:1px solid var(--line); padding:9px 8px; text-align:left; vertical-align:top; overflow-wrap:anywhere; word-break:break-word; }}
  .kv th {{ color:var(--dim); font-weight:500; width:34%; }}
  .mi {{ display:flex; gap:10px; align-items:flex-start; padding:10px 2px; border-bottom:1px solid var(--line); }}
  .mi-code {{ flex:0 0 auto; font:600 11px/1.6 ui-monospace,Consolas,monospace; color:#0b0b10; background:var(--accent);
             border-radius:5px; padding:3px 6px; margin-top:2px; }}
  .mi-body b {{ display:block; font-size:15px; }}
  .mi-body span {{ display:block; color:var(--dim); font-size:12.5px; margin-top:2px; }}
  .tbl {{ overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid var(--line); border-radius:12px; }}
  .tbl table {{ border-collapse:collapse; font-size:13px; min-width:560px; }}
  .tbl th, .tbl td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
  .tbl th {{ background:#1c1c2a; color:#cfc4ff; position:sticky; top:0; }}
  .cl {{ background:linear-gradient(160deg,#1a1428,#111119); border:1px solid #2f2745; border-radius:14px; padding:12px 14px; margin:12px 0; }}
  .cl h3 {{ margin:0 0 6px; font-size:15px; color:#cbb6ff; }}
  .cl p {{ margin:0; font-size:14px; color:#c6c6d8; }}
  details {{ background:#101018; border:1px solid var(--line); border-radius:12px; padding:10px 12px; }}
  details summary {{ cursor:pointer; color:#cfc4ff; font-size:14px; }}
  pre {{ white-space:pre; overflow-x:auto; font:12.5px/1.7 ui-monospace,Consolas,monospace; color:#cfd0e6; margin:10px 0 0; }}
  .lane {{ background:#12121b; border:1px solid #262638; border-radius:12px; padding:10px; margin:12px 0; }}
  .lane-head {{ color:#cfc4ff; font-weight:600; font-size:14px; margin-bottom:8px; }}
  .node {{ display:block; border-left:3px solid var(--accent); background:#181822; border-radius:9px;
           padding:8px 10px; margin:8px 0; color:inherit; }}
  .node b {{ display:block; font-size:14px; }}
  .node span {{ display:block; font-size:12.5px; color:#8f8fa8; }}
  .k-content {{ border-left-color:var(--green); }}
  .k-pay {{ border-left-color:var(--amber); }}
  .k-sys {{ border-left-color:#5c9dff; }}
  .rowlabel {{ color:var(--dim); font-size:13px; margin:16px 0 8px; }}
  .legend {{ display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:var(--dim); margin-top:10px; }}
  .legend i {{ display:inline-block; width:9px; height:9px; border-radius:3px; margin-right:5px; }}
  .top {{ position:fixed; right:14px; bottom:18px; width:46px; height:46px; border-radius:50%;
          background:#241a3d; border:1px solid #4b3a7a; color:#d9ccff; display:flex; align-items:center;
          justify-content:center; font-size:18px; z-index:30; }}
  #lb {{ position:fixed; inset:0; background:rgba(0,0,0,.95); display:none; align-items:center;
         justify-content:center; z-index:99; }}
  #lb img {{ max-width:100vw; max-height:100vh; }}
  footer {{ color:#5f5f78; font-size:12px; border-top:1px solid var(--line); padding-top:14px; margin-top:24px; }}
</style>
</head>
<body>
<header class="m-top">
  <h1>{title}</h1>
  <div class="sub">{sub}</div>
  <div class="m-stats">{stats}</div>
</header>
<nav class="m-jump">
  <a href="#meta">基本盘</a><a href="#concl">结论</a>{map_link}<a href="#tree">层级树</a>
  <a href="#index">索引</a><a href="#pages">逐页</a><a href="#clean">功能</a>
  <a href="#tech">技术</a><a href="#observe">判断</a><a href="#method">方法</a>
</nav>
<main>
  <section id="meta"><h2>调研对象与基本盘</h2><table class="kv">{meta_rows}</table></section>
  <section id="concl"><h2>结论</h2>{concl}</section>
  {map_sec}
  <section id="tree"><h2>页面层级树</h2><details><summary>展开文本树</summary><pre>{tree}</pre></details></section>
  <section id="index"><h2>页面索引（{page_count}）</h2>{index_cards}</section>
  <section id="pages"><h2>逐页拆解</h2>{sections}</section>
  <section id="clean"><h2>功能清单</h2><div class="tbl"><table style="min-width:640px">
    <thead><tr>{clean_head}</tr></thead><tbody>{clean_rows}</tbody></table></div></section>
  <section id="tech"><h2>技术观察</h2><table class="kv">{tech_rows}</table></section>
  {extra_tables}
  <section id="observe"><h2>产品判断</h2>{observe}</section>
  <section id="method"><h2>方法与边界</h2><ul>{method}</ul><p class="note">{note}</p></section>
  <footer>{footer}</footer>
</main>
<a class="top" href="#top" aria-label="回到顶部">↑</a>
<div id="lb"><img alt=""></div>
<script>
  var lb = document.getElementById('lb'), lbImg = lb.querySelector('img');
  document.addEventListener('click', function (e) {{
    if (e.target.tagName === 'IMG' && e.target.closest('.m-card')) {{
      lbImg.src = e.target.src; lb.style.display = 'flex'; e.preventDefault();
    }}
    if (e.target === lb) lb.style.display = 'none';
  }});
</script>
</body>
</html>"""


def _map_html_mobile(data):
    lanes = getattr(data, "LANES", None)
    if not lanes:
        return ""
    def node(n):
        label, sub, kind, goto = (list(n) + ["", "", "func", ""])[:4]
        inner = f'<b>{_esc(label)}</b><span>{_esc(sub)}</span>'
        if goto:
            return f'<a class="node k-{kind}" href="#{_esc(goto)}">{inner}</a>'
        return f'<div class="node k-{kind}">{inner}</div>'
    blocks = "".join(
        f'<div class="lane"><div class="lane-head">{_esc(l["title"])}</div>'
        f'{"".join(node(n) for n in l.get("nodes", []))}</div>' for l in lanes)
    rows = "".join(
        f'<div class="rowlabel">{_esc(r["label"])}</div>'
        f'{"".join(node(n) for n in r.get("nodes", []))}' for r in getattr(data, "ROWS", []))
    return (f'<section id="map"><h2>页面结构图</h2>'
            f'<p style="color:#9a9ab0;font-size:13.5px">{_esc(getattr(data, "MAP_INTRO", ""))}</p>'
            f'{blocks}{rows}'
            '<div class="legend"><span><i style="background:#a06bff"></i>功能</span>'
            '<span><i style="background:#3ddc97"></i>内容</span>'
            '<span><i style="background:#ffb020"></i>付费</span>'
            '<span><i style="background:#5c9dff"></i>系统</span></div></section>')


def build_mobile(data, root):
    img_dir = getattr(data, "IMG_DIR", "shots")
    pages = [p for s in data.SECTIONS for p in s["pages"]]
    stats = getattr(data, "HERO_STATS", None)
    if not stats:
        stats = [(str(len(pages)), "页面"), (getattr(data, "TAB_COUNT", ""), "Tab")]
    clean_head, clean_rows = _clean_table(data)
    map_sec = _map_html_mobile(data)
    html = MOBILE_SHELL.format(
        title=_esc(data.TITLE), sub=_esc(data.SUB),
        stats="".join(f'<div class="m-stat"><b>{_esc(v)}</b><span>{_esc(k)}</span></div>' for v, k in stats),
        map_link='<a href="#map">结构图</a>' if map_sec else "",
        meta_rows=_meta_rows(data), concl=_concl(data.CONCLUSIONS), map_sec=map_sec,
        tree=_esc(data.TREE), page_count=len(pages),
        index_cards=_index_cards(pages),
        sections=_sections_html(data, root, img_dir, maxw=760, quality=72, card_cls="m-card"),
        clean_head=clean_head, clean_rows=clean_rows, tech_rows=_tech_rows(data),
        extra_tables=_extra_tables_html(data),
        observe=_observe(data), method=_method(data),
        note=_esc(getattr(data, "NOTE", "")), footer=_esc(getattr(data, "FOOTER", "")),
    )
    out = os.path.join(root, data.SLUG + "_mobile.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


def build_md(data, root, prefix, out_name, inline=False):
    import re
    plain = lambda s: re.sub(r"<[^>]+>", "", str(s))
    img_dir = getattr(data, "IMG_DIR", "shots")
    pages = [p for s in data.SECTIONS for p in s["pages"]]
    L = []
    A = L.append
    A(f"# {data.TITLE}")
    A("")
    A(f"> {data.SUB}")
    A("")
    if getattr(data, "HTML_NAME", ""):
        A(f"> 桌面版结构图：`{data.HTML_NAME}`　手机版：`{getattr(data, 'MOBILE_NAME', '')}`")
        A("")
    A("## 一、调研对象与基本盘")
    A("")
    A("| 项目 | 内容 |")
    A("|---|---|")
    for k, v in data.META:
        A(f"| {k} | {plain(v)} |")
    A("")
    A("## 二、先看结论")
    A("")
    for c, t in data.CONCLUSIONS:
        A(f"**{c}**")
        A("")
        A(t)
        A("")
    A("## 三、页面层级树（全图）")
    A("")
    A("```text")
    A(data.TREE)
    A("```")
    A("")
    A(f"## 四、页面索引（{len(pages)} 个页面/状态）")
    A("")
    A("| 编号 | 页面 | 路径 | 类型 | 一句话 |")
    A("|---|---|---|---|---|")
    for p in pages:
        A(f"| {p['code']} | {p['name']} | {p['path']} | {p['kind']} | {p['desc'].replace('|', chr(92)+'|')} |")
    A("")
    A("## 五、逐页拆解")
    A("")
    for s in data.SECTIONS:
        A(f"### {s['num']}. {s['title']}")
        A("")
        A(s["intro"])
        A("")
        for p in s["pages"]:
            A(f"#### {p['code']} · {p['name']}")
            A("")
            A(f"- **路径**：{p['path']}")
            A(f"- **类型**：{p['kind']}")
            A("")
            if inline:
                A(f'<img alt="{p["name"]}" src="data:image/jpeg;base64,{_b64(root, img_dir, p["img"], 900, 76)}" style="max-width:100%">')
            else:
                A(f"![{p['name']}]({prefix}{img_dir}/{p['img']}.jpg)")
            A("")
            A(f"*{p['name']} · 实机截图*")
            A("")
            A(f"**页面说明**：{p['desc']}")
            A("")
            A("**要点**：")
            A("")
            for x in p["points"]:
                A(f"- {x}")
            A("")
            A(f"**跳转**：{p['next']}　　**限制**：{p['limit']}")
            A("")
    A("## 六、功能清单表")
    A("")
    A("| " + " | ".join(data.CLEAN[0]) + " |")
    A("|" + "---|" * len(data.CLEAN[0]))
    for row in data.CLEAN[1:]:
        A("| " + " | ".join(c.replace("|", "\\|") for c in row) + " |")
    A("")
    A("## 七、技术观察")
    A("")
    A("| 维度 | 结论 |")
    A("|---|---|")
    for k, v in data.TECH:
        A(f"| {k} | {v.replace('|', chr(92)+'|')} |")
    A("")
    for t in getattr(data, "EXTRA_TABLES", []):
        A(f"## {t['title']}")
        A("")
        A("| " + " | ".join(t["head"]) + " |")
        A("|" + "---|" * len(t["head"]))
        for row in t["rows"]:
            A("| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |")
        A("")
    A("## 八、产品判断")
    A("")
    for t, d in data.OBSERVE:
        A(f"### {t}")
        A("")
        A(d)
        A("")
    A("## 九、调研方法与安全边界")
    A("")
    for m in data.METHOD:
        A(f"- {m}")
    A("")
    A(f"> {getattr(data, 'NOTE', '')}")
    A("")
    A("---")
    A(getattr(data, "FOOTER", ""))

    out = os.path.join(root, out_name)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return out


def build(data, root="."):
    """Emit five files: desktop html, mobile html, md (+shots), single-file md, feishu md."""
    root = os.path.abspath(root)
    outs = [
        build_html(data, root),
        build_mobile(data, root),
        build_md(data, root, "", data.SLUG + ".md"),
        build_md(data, root, "", data.SLUG + "_single.md", inline=True),
        build_md(data, root, "@./", "feishu_doc.md"),
    ]
    for p in outs:
        print(f"{os.path.basename(p):32s} {os.path.getsize(p)/1048576:6.2f} MB")
    return outs
