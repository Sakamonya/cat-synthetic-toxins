#!/usr/bin/env python3
"""生成兼容旧内核（QQ/微信内置浏览器）的单文件速查表。

约束：不依赖 CSS 变量 / flex / grid / 媒体查询 / 模板字符串 / async-await。
全部样式内联或使用最基础的 CSS 属性，布局靠块级元素纵向堆叠。
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "synthetic-compounds.yaml"
QUAR = ROOT / "quarantine" / "observations.yaml"
SPEC = ROOT / "docs" / "agent-task.md"
OUT = ROOT / "docs" / "index.html"

COLORS = {
    "极高": ("#b42318", "#fdecea"),
    "高": ("#9a3412", "#fff4e5"),
    "中": ("#7a5c00", "#fffbe6"),
}

BASE_CSS = """
body{margin:0;padding:14px 12px 40px;background:#f4f5f7;color:#1a1d21;
font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
font-size:15px;line-height:1.6;-webkit-text-size-adjust:100%}
h1{font-size:19px;margin:0 0 4px;line-height:1.35}
.sub{color:#6b7280;font-size:12.5px;margin:0 0 12px}
.bar{background:#eaf3ff;border:1px solid #cfe3ff;color:#0b4a8f;font-size:13px;
padding:10px 12px;border-radius:8px;margin:0 0 10px}
.warn{background:#fdecea;border:1px solid #f5c2c0;color:#7a271a;font-size:12.5px;
padding:10px 12px;border-radius:8px;margin:0 0 12px}
input[type=search]{display:block;width:100%;padding:10px;font-size:15px;
border:1px solid #ccd2da;border-radius:8px;margin:0 0 10px;background:#fff}
.fbtn{display:inline-block;padding:7px 11px;margin:0 6px 6px 0;font-size:12.5px;
border:1px solid #ccd2da;border-radius:14px;background:#fff;color:#344054;cursor:pointer}
.fbtn.on{background:#1a1d21;color:#fff;border-color:#1a1d21}
.count{color:#6b7280;font-size:12.5px;margin:2px 0 10px}
.card{background:#fff;border:1px solid #e0e3e8;border-radius:10px;padding:12px;margin:0 0 10px}
.card h2{font-size:16px;margin:0 0 6px;font-weight:600}
.badge{display:inline-block;font-size:11.5px;padding:1px 7px;border-radius:10px;
margin-left:6px;font-weight:600;vertical-align:middle}
.kv{font-size:12px;color:#6b7280;margin:0 0 6px}
.kv span{display:inline-block;background:#f2f4f7;border-radius:5px;padding:1px 6px;margin:0 5px 5px 0}
.ali{font-size:12px;color:#6b7280;margin:0 0 8px;word-wrap:break-word}
.dose{font-size:13px;background:#eaf3ff;border:1px solid #cfe3ff;color:#0b4a8f;
border-radius:6px;padding:7px 9px;margin:0 0 8px;word-wrap:break-word}
.dose.none{background:#f6f7f9;border-color:#e0e3e8;color:#6b7280}
.sum{font-size:13.5px;margin:0 0 8px;word-wrap:break-word}
.src{border-top:1px dashed #e0e3e8;padding-top:6px;font-size:12px}
.src a{display:block;color:#175cd3;text-decoration:none;margin:2px 0;word-wrap:break-word}
table.q{width:100%;border-collapse:collapse;background:#fff;font-size:12.5px;
border:1px solid #e0e3e8}
table.q th,table.q td{border-bottom:1px solid #eef0f3;padding:7px 8px;text-align:left;
vertical-align:top}
table.q th{background:#f7f8fa;font-weight:600}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
footer{margin:22px 0 0;padding-top:12px;border-top:1px solid #e0e3e8;
color:#6b7280;font-size:11.5px}
.btn{display:inline-block;padding:9px 14px;border:1px solid #175cd3;border-radius:8px;
background:#175cd3;color:#fff;font-size:14px;cursor:pointer;margin:0 8px 8px 0}
.btn2{display:inline-block;padding:9px 14px;border:1px solid #ccd2da;border-radius:8px;
background:#fff;color:#344054;font-size:14px;cursor:pointer;margin:0 8px 8px 0}
.mask{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(16,24,40,.5);
padding:12px;z-index:99}
.mask.show{display:block}
.dlg{background:#fff;border-radius:10px;padding:16px;max-width:640px;margin:0 auto;
max-height:88%;overflow:auto}
.dlg h3{font-size:16px;margin:0 0 8px}
.dlg p{font-size:13px;color:#344054;margin:0 0 8px}
.dlg textarea{width:100%;height:120px;font-size:12.5px;padding:8px;
border:1px solid #ccd2da;border-radius:6px;margin:0 0 8px;
font-family:Consolas,monospace;box-sizing:border-box}
pre{background:#f7f8fa;border:1px solid #e0e3e8;border-radius:6px;padding:10px;
font-size:11.5px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;
max-height:40%;overflow:auto;margin:0}
.toast{font-size:12.5px;color:#027a48;margin-left:4px}
"""

JS = r"""
function esc(s){
  return String(s == null ? '' : s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function colors(level){
  if (level === '极高') return ['#b42318','#fdecea'];
  if (level === '高') return ['#9a3412','#fff4e5'];
  return ['#7a5c00','#fffbe6'];
}
var state = { q: '', danger: '', common: '' };

function render(){
  var rows = [];
  for (var i = 0; i < DATA.length; i++){
    var e = DATA[i];
    if (state.danger && e.danger_level !== state.danger) continue;
    if (state.common && e.commonness !== state.common) continue;
    if (state.q){
      var hay = (e.compound + ' ' + (e.aliases || []).join(' ') + ' ' +
                 e.cat_toxicity_summary + ' ' + (e.cat_dose_note || '')).toLowerCase();
      if (hay.indexOf(state.q.toLowerCase()) < 0) continue;
    }
    rows.push(e);
  }

  var html = '';
  for (var j = 0; j < rows.length; j++){
    var x = rows[j];
    var c = colors(x.danger_level);
    var dose;
    if (x.cat_lethal_dose && x.cat_lethal_dose !== '无可靠数值'){
      dose = '<div class="dose"><b>剂量：</b>' + esc(x.cat_lethal_dose) + '</div>';
    } else if (x.cat_dose_note){
      dose = '<div class="dose"><b>危险剂量：</b>' + esc(x.cat_dose_note) + '</div>';
    } else {
      dose = '<div class="dose none"><b>剂量：</b>无可靠数值（公开来源未给出猫的数值）</div>';
    }
    var srcs = '';
    for (var k = 0; k < (x.sources || []).length; k++){
      var s = x.sources[k];
      srcs += '<a href="' + esc(s.url) + '" target="_blank">' + esc(s.library) +
              ' · ' + esc(s.title) + '</a>';
    }
    var routes = '';
    for (var r = 0; r < (x.exposure_routes || []).length; r++){
      routes += '<span>' + esc(x.exposure_routes[r]) + '</span>';
    }
    html += '<div class="card">' +
      '<h2>' + esc(x.compound) +
        '<span class="badge" style="color:' + c[0] + ';background:' + c[1] + '">危险 ' + esc(x.danger_level) + '</span>' +
      '</h2>' +
      '<div class="kv"><span>' + esc(x.category) + '</span><span>' + esc(x.physical_form) +
        '</span><span>常见 ' + esc(x.commonness) + '</span><span>毒性 ' + esc(x.toxicity_level) + '</span></div>' +
      '<div class="ali">' + esc((x.aliases || []).join(' / ')) + '</div>' +
      dose +
      '<p class="sum">' + esc(x.cat_toxicity_summary) + '</p>' +
      '<div class="kv">' + routes + '</div>' +
      '<div class="src">' + srcs + '</div>' +
    '</div>';
  }
  document.getElementById('grid').innerHTML = html ||
    '<p style="color:#6b7280">没有匹配的条目</p>';
  document.getElementById('count').innerHTML = '显示 ' + rows.length + ' / ' + DATA.length + ' 条';
}

function bindFilters(){
  var btns = document.getElementsByTagName('button');
  for (var i = 0; i < btns.length; i++){
    var b = btns[i];
    if (!b.getAttribute('data-field')) continue;
    b.onclick = (function(el){
      return function(){
        var f = el.getAttribute('data-field');
        var v = el.getAttribute('data-value');
        state[f] = (state[f] === v) ? '' : v;
        var all = document.querySelectorAll('button[data-field="' + f + '"]');
        for (var j = 0; j < all.length; j++){
          all[j].className = (all[j].getAttribute('data-value') === state[f]) ? 'fbtn on' : 'fbtn';
        }
        render();
      };
    })(b);
  }
}

function copyText(text, cb){
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  var ok = false;
  try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
  document.body.removeChild(ta);
  cb(ok);
}

function show(id){ document.getElementById(id).className = 'mask show'; }
function hide(id){ document.getElementById(id).className = 'mask'; }

document.getElementById('q').oninput = function(){
  state.q = this.value;
  render();
};

document.getElementById('opensub').onclick = function(){ show('submask'); };
document.getElementById('closesub').onclick = function(){ hide('submask'); };
document.getElementById('openspec').onclick = function(){ show('specmask'); };
document.getElementById('closespec').onclick = function(){ hide('specmask'); };

document.getElementById('sendmail').onclick = function(){
  var v = document.getElementById('payload').value;
  if (!v.replace(/\s/g, '')){ document.getElementById('toast').innerHTML = '先把 YAML 粘贴进来'; return; }
  copyText('收件人：1449262435@qq.com\n\n' + v, function(ok){
    document.getElementById('toast').innerHTML = ok ? '已复制，粘贴到邮件正文' : '复制失败，请长按手动复制';
  });
  window.open('https://mail.qq.com', '_blank');
};

document.getElementById('copyyaml').onclick = function(){
  var v = document.getElementById('payload').value;
  copyText(v, function(ok){
    document.getElementById('toast').innerHTML = ok ? '已复制' : '复制失败，请长按手动复制';
  });
};

document.getElementById('copyspec').onclick = function(){
  copyText(SPEC, function(ok){
    document.getElementById('spectoast').innerHTML = ok ? '已复制，粘给 AI 即可' : '复制失败，请长按手动复制';
  });
};

bindFilters();
render();
document.getElementById('vw').innerHTML =
  '视口 ' + window.innerWidth + '×' + window.innerHeight + ' · 设备像素比 ' + (window.devicePixelRatio || 1);
"""


def build() -> None:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    entries = data["entries"]
    quar = (yaml.safe_load(QUAR.read_text(encoding="utf-8")) or {}).get("entries", [])
    spec_md = SPEC.read_text(encoding="utf-8")

    payload = [
        {
            "compound": e["compound"],
            "aliases": e.get("aliases", []),
            "category": e["category"],
            "physical_form": e["physical_form"],
            "danger_level": e["danger_level"],
            "toxicity_level": e["toxicity_level"],
            "commonness": e["commonness"],
            "exposure_routes": e.get("exposure_routes", []),
            "cat_lethal_dose": e.get("cat_lethal_dose", ""),
            "cat_dose_note": e.get("cat_dose_note", ""),
            "cat_toxicity_summary": e.get("cat_toxicity_summary", ""),
            "sources": e.get("sources", []),
        }
        for e in entries
    ]

    def fbtns(field, values):
        return "".join(
            '<button class="fbtn" data-field="' + field + '" data-value="' + v + '">' + v + "</button>"
            for v in values
        )

    qrows = "".join(
        "<tr><td>" + q["compound"] + "</td><td>" + q["category_guess"] + "</td><td>" +
        q["why_quarantined"] + "</td></tr>"
        for q in quar
    )

    spec_escaped = (
        spec_md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )

    html = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<meta http-equiv="Cache-Control" content="no-store,no-cache,must-revalidate">\n'
        '<meta http-equiv="Pragma" content="no-cache">\n'
        '<title>养猫家庭 · 人工合成化合物速查</title>\n'
        '<style>' + BASE_CSS + '</style>\n</head>\n<body>\n'
        '<h1>养猫家庭 · 人工合成化合物速查</h1>\n'
        '<p class="sub">只收录已确认对猫有毒的人工合成化合物 · 共 ' + str(len(entries)) +
        ' 条 · 最后复核 2026-10-24</p>\n'

        '<div class="bar">你在用 AI 助手？把这个网页交给它 —— 它会按同一套规则查证，'
        '输出一段可直接收录的 YAML，并把结果提交上来共享给其他人。'
        '<a href="javascript:void(0)" id="openspec" style="color:#175cd3;font-weight:600">查看工作说明书</a></div>\n'

        '<div class="warn"><b>⚠ 不替代兽医诊断。</b>怀疑中毒请立即联系兽医或宠物中毒热线，带上产品包装。'
        '本页为建议性参考，不担保完整或最新；剂量与结论均标注来源，请以来源原文为准。'
        '<b>查不到数值 ≠ 安全</b>——标「无可靠数值」的条目同样需要避开。<br>'
        '危险程度规则：非固体 + 常见或一般 + 剧毒 才为「极高」；固体或「少见」一律封顶「高」。</div>\n'

        '<input id="q" type="search" placeholder="搜索化合物、别名、成分名…（如 布洛芬 / permethrin / 滴露）">\n'
        '<div>' + fbtns("danger", ["极高", "高", "中"]) + '</div>\n'
        '<div>' + fbtns("common", ["常见", "一般", "少见"]) + '</div>\n'
        '<p class="count" id="count"></p>\n'
        '<div id="grid"></div>\n'

        '<h2 style="font-size:15px;margin:22px 0 6px">候审区：待确认，默认避免</h2>\n'
        '<p class="sub" style="margin:0 0 8px">证据不足，未进主库；处理原则与高危物质相同。</p>\n'
        '<div class="scroll"><table class="q"><tr><th>物质</th><th>推测类别</th>'
        '<th>为什么不进主库</th></tr>' + qrows + '</table></div>\n'

        '<footer>数据源：ASPCA · Pet Poison Helpline · Plumb\'s · Merck Vet Manual · '
        'VCA · ACVP · ICAT ｜ <b>build-es5-2026</b><br>'
        '仓库：github.com/Sakamonya/cat-synthetic-toxins ｜ 由 scripts/build_site.py 生成<br>'
        '<span id="vw"></span></footer>\n'

        '<div class="mask" id="submask"><div class="dlg">'
        '<h3>提交收录</h3>'
        '<p>把工作说明书和你的问题一起交给能上网的 AI 助手，它会输出一段 YAML。'
        '把结果贴到下面，点按钮复制并打开 QQ 邮箱。</p>'
        '<p style="color:#6b7280">收件人：<b>1449262435@qq.com</b></p>'
        '<textarea id="payload" placeholder="在这里粘贴 AI 生成的 YAML…"></textarea>'
        '<div><button class="btn" id="sendmail">复制并打开 QQ 邮箱</button>'
        '<button class="btn2" id="copyyaml">只复制</button>'
        '<span class="toast" id="toast"></span></div>'
        '<div style="margin-top:10px"><button class="btn2" id="closesub">关闭</button></div>'
        '</div></div>\n'

        '<div class="mask" id="specmask"><div class="dlg">'
        '<h3>给 AI 助手的工作说明书</h3>'
        '<p>复制全部内容，连同问题一起交给能上网的 AI 助手。</p>'
        '<div><button class="btn" id="copyspec">复制说明书</button>'
        '<span class="toast" id="spectoast"></span></div>'
        '<pre>' + spec_escaped + '</pre>'
        '<div style="margin-top:10px"><button class="btn2" id="closespec">关闭</button></div>'
        '</div></div>\n'

        '<script>var DATA = ' + json.dumps(payload, ensure_ascii=False) + ';var SPEC = ' +
        json.dumps(spec_md, ensure_ascii=False) + ';</script>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"built {OUT} ({len(html)} chars, {len(entries)} entries)")


if __name__ == "__main__":
    build()
