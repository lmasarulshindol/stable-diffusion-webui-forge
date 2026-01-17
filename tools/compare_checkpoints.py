"""
Forge (A1111系) REST API を使って、複数チェックポイントで同条件生成し、比較しやすい形で保存するツール。

できること:
- /sdapi/v1/sd-models からモデル一覧取得
- /sdapi/v1/options で sd_model_checkpoint を切替
- /sdapi/v1/txt2img で各モデル1枚ずつ生成してPNG保存
- 画像と設定を並べた compare.html を自動生成（依存ライブラリ不要）

実行例:
  python tools/compare_checkpoints.py ^
    --prompt "1girl, anime, detailed" ^
    --seed 12345 --width 1024 --height 1024 ^
    --checkpoint "animagineXLV31_v31" ^
    --checkpoint "illustriousXL_v01" ^
    --outdir .\\compare-out

API認証がある場合:
  python tools/compare_checkpoints.py --api-user user --api-pass pass ...

ディレクトリ内のモデルを全対象（例: models/Stable-diffusion 配下）:
  python tools/compare_checkpoints.py ^
    --all-models --models-under "models/Stable-diffusion" --limit 20 ^
    --prompt "..." --outdir .\\compare-out
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import html
import json
import os
import time
from typing import Any

import requests


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _norm_pathish(s: str) -> str:
    return str(s).replace("\\", "/").lower()


def _decode_base64_image(b64: str) -> bytes:
    if "," in b64 and b64.lstrip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


def _safe_json_loads(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s


def _api_get(base_url: str, path: str, *, auth, timeout: float) -> Any:
    url = f"{base_url}{path}"
    r = requests.get(url, auth=auth, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _api_post(base_url: str, path: str, payload: dict[str, Any], *, auth, timeout: float) -> Any:
    url = f"{base_url}{path}"
    r = requests.post(url, json=payload, auth=auth, timeout=timeout)
    if r.status_code == 404:
        raise RuntimeError(
            f"404 Not Found: {path} が見つかりません。\n"
            "- Forgeを `--api` 付きで起動してください\n"
            "- `--subpath` を使っている場合は `--base-url http://127.0.0.1:7860/<subpath>` を指定してください\n"
            f"- URL: {url}\n"
        )
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {}


def _pick_checkpoint_title(models: list[dict[str, Any]], query: str) -> str:
    q = query.strip().lower()
    if not q:
        raise ValueError("checkpoint名が空です")

    # title 完全一致（大小無視）
    for m in models:
        title = str(m.get("title", ""))
        if title.lower() == q:
            return title

    # 末尾一致（ファイル名指定を許容）
    suffix_matches: list[str] = []
    for m in models:
        title = str(m.get("title", ""))
        if title.lower().endswith(q):
            suffix_matches.append(title)
    if len(suffix_matches) == 1:
        return suffix_matches[0]

    # 部分一致（候補1つなら採用）
    contains_matches: list[str] = []
    for m in models:
        title = str(m.get("title", ""))
        if q in title.lower():
            contains_matches.append(title)
    if len(contains_matches) == 1:
        return contains_matches[0]

    candidates = suffix_matches or contains_matches
    if not candidates:
        raise RuntimeError(f"checkpoint '{query}' が見つかりません。--list-models で一覧を確認してください。")
    preview = "\n".join(f"- {c}" for c in candidates[:40])
    raise RuntimeError(f"checkpoint '{query}' の候補が複数あります（より具体的に指定してください）:\n{preview}")


def _sanitize_filename(s: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        s = s.replace(ch, "_")
    return s.strip().strip(".")


@dataclasses.dataclass
class Result:
    query: str
    title: str
    png_path: str
    info_path: str
    meta: dict[str, Any]


def _write_compare_html(outdir: str, results: list[Result], *, header: dict[str, Any]) -> str:
    rows = []
    for r in results:
        rel_png = os.path.relpath(r.png_path, outdir).replace("\\", "/")
        rel_info = os.path.relpath(r.info_path, outdir).replace("\\", "/")
        rows.append(
            f"""
            <div class="card">
              <div class="title">{html.escape(r.title)}</div>
              <div class="query">query: <code>{html.escape(r.query)}</code></div>
              <a href="{html.escape(rel_png)}" target="_blank"><img src="{html.escape(rel_png)}" loading="lazy"/></a>
              <div class="meta">
                <a href="{html.escape(rel_info)}" target="_blank">info.json</a>
              </div>
            </div>
            """
        )

    doc = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Checkpoint Compare</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 24px; background: #0b0f14; color: #e6edf3; }}
    .header {{ max-width: 1100px; margin: 0 auto 18px; }}
    .header pre {{ background: #111826; padding: 12px; border-radius: 10px; overflow: auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; max-width: 1100px; margin: 0 auto; }}
    .card {{ background: #0f1623; border: 1px solid #1f2a3a; border-radius: 14px; padding: 12px; }}
    .title {{ font-weight: 700; margin-bottom: 6px; }}
    .query {{ opacity: 0.85; margin-bottom: 10px; font-size: 12px; }}
    img {{ width: 100%; height: auto; border-radius: 10px; border: 1px solid #223044; }}
    a {{ color: #79c0ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ background: #111826; padding: 2px 6px; border-radius: 8px; }}
    .meta {{ margin-top: 8px; font-size: 12px; opacity: 0.9; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>Checkpoint Compare</h2>
    <div style="opacity:0.9">生成条件（固定）</div>
    <pre>{html.escape(json.dumps(header, ensure_ascii=False, indent=2))}</pre>
  </div>
  <div class="grid">
    {''.join(rows)}
  </div>
</body>
</html>
"""
    out_path = os.path.join(outdir, "compare.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:7860", help="WebUIのURL（例: http://127.0.0.1:7860 ）")
    p.add_argument("--api-user", default=None, help="--api-auth を設定している場合のユーザー名")
    p.add_argument("--api-pass", default=None, help="--api-auth を設定している場合のパスワード")
    p.add_argument("--timeout", type=float, default=600.0)

    p.add_argument("--list-models", action="store_true", help="APIから利用可能なチェックポイント一覧を表示して終了")
    p.add_argument("--all-models", action="store_true", help="APIが認識しているモデルを全て比較対象にする（フィルタ併用推奨）")
    p.add_argument("--models-under", action="append", default=[], help="モデルの filename に含まれるパス部分で絞り込み（複数指定可）例: models/Stable-diffusion")
    p.add_argument("--include", action="append", default=[], help="title/filename の部分一致で追加絞り込み（複数指定可）")
    p.add_argument("--exclude", action="append", default=[], help="title/filename の部分一致で除外（複数指定可）")
    p.add_argument("--limit", type=int, default=None, help="対象モデル数の上限（多すぎる時の安全弁）")
    p.add_argument("--checkpoint", action="append", default=[], help="比較したいチェックポイント（複数指定可）")
    p.add_argument("--checkpoint-file", default=None, help="チェックポイント名を1行1つで書いたファイル（任意）")

    p.add_argument("--prompt", default=None, help="プロンプト（--list-models の時は不要）")
    p.add_argument("--negative", default="", help="ネガティブプロンプト")
    p.add_argument("--steps", type=int, default=30)
    p.add_argument("--cfg-scale", type=float, default=6.0)
    p.add_argument("--sampler", default="DPM++ 2M", help="sampler_index（例: DPM++ 2M, Euler など）")
    p.add_argument("--seed", type=int, default=12345, help="同条件比較のため固定推奨（-1でランダム）")
    p.add_argument("--width", type=int, default=1024)
    p.add_argument("--height", type=int, default=1024)

    p.add_argument("--outdir", default=None, help="出力先フォルダ（省略時は自動作成）")
    p.add_argument("--prefix", default="cmp", help="出力ファイル名の接頭辞")

    args = p.parse_args()

    base_url = _normalize_base_url(args.base_url)

    auth = None
    if args.api_user is not None or args.api_pass is not None:
        auth = (args.api_user or "", args.api_pass or "")

    models = _api_get(base_url, "/sdapi/v1/sd-models", auth=auth, timeout=args.timeout)
    if args.list_models:
        for m in models:
            print(m.get("title", ""))
        return 0

    if not args.prompt:
        raise SystemExit("--prompt が必要です（--list-models の場合を除く）")

    def model_matches(m: dict[str, Any]) -> bool:
        title = str(m.get("title", ""))
        filename = str(m.get("filename", ""))
        hay = _norm_pathish(title + "\n" + filename)

        # models-under は「どれか1つでも含まれていればOK」
        if args.models_under:
            ok = False
            for u in args.models_under:
                if _norm_pathish(u) in _norm_pathish(filename):
                    ok = True
                    break
            if not ok:
                return False

        for ex in args.exclude:
            if _norm_pathish(ex) in hay:
                return False

        for inc in args.include:
            if _norm_pathish(inc) not in hay:
                return False

        return True

    queries: list[str] = []
    if args.all_models:
        picked = [m for m in models if model_matches(m)]
        picked.sort(key=lambda x: str(x.get("title", "")))
        if args.limit is not None:
            picked = picked[: max(0, args.limit)]
        queries = [str(m.get("title", "")) for m in picked]
    else:
        queries = list(args.checkpoint or [])
    if args.checkpoint_file:
        with open(args.checkpoint_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                queries.append(line)

    # --checkpoint を「a,b,c」みたいに書く人もいるので分割もする
    expanded: list[str] = []
    for q in queries:
        expanded.extend([x.strip() for x in q.split(",") if x.strip()])
    queries = expanded

    if len(queries) < 2:
        raise SystemExit("比較には対象モデルが2つ以上必要です（--checkpoint / --checkpoint-file / --all-models を確認）")

    ts = time.strftime("%Y%m%d-%H%M%S")
    outdir = args.outdir or os.path.join(os.getcwd(), f"compare-{ts}")
    os.makedirs(outdir, exist_ok=True)

    header = {
        "base_url": base_url,
        "prompt": args.prompt,
        "negative_prompt": args.negative,
        "steps": args.steps,
        "cfg_scale": args.cfg_scale,
        "sampler_index": args.sampler,
        "seed": args.seed,
        "width": args.width,
        "height": args.height,
    }
    with open(os.path.join(outdir, "compare.request.json"), "w", encoding="utf-8") as f:
        json.dump(header, f, ensure_ascii=False, indent=2)

    results: list[Result] = []
    for idx, q in enumerate(queries, start=1):
        title = _pick_checkpoint_title(models, q)
        _api_post(
            base_url,
            "/sdapi/v1/options",
            {"sd_model_checkpoint": title},
            auth=auth,
            timeout=args.timeout,
        )

        payload: dict[str, Any] = {
            "prompt": args.prompt,
            "negative_prompt": args.negative,
            "steps": args.steps,
            "cfg_scale": args.cfg_scale,
            "sampler_index": args.sampler,
            "seed": args.seed,
            "width": args.width,
            "height": args.height,
            "batch_size": 1,
            "n_iter": 1,
            "send_images": True,
            "save_images": False,
        }
        data = _api_post(base_url, "/sdapi/v1/txt2img", payload, auth=auth, timeout=args.timeout)

        images = data.get("images") or []
        if not images:
            raise RuntimeError(f"APIレスポンスに images がありません: keys={list(data.keys())}")

        safe_title = _sanitize_filename(title) or f"model-{idx}"
        stem = f"{args.prefix}-{idx:02d}-{safe_title}"
        png_path = os.path.join(outdir, stem + ".png")
        info_path = os.path.join(outdir, stem + ".info.json")

        img_bytes = _decode_base64_image(images[0])
        with open(png_path, "wb") as f:
            f.write(img_bytes)

        info_obj = _safe_json_loads(data.get("info", ""))
        meta = {
            "query": q,
            "title": title,
            "request": header,
            "parameters": data.get("parameters", {}),
            "info": info_obj,
        }
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"[{idx}/{len(queries)}] Saved: {png_path}")
        results.append(Result(query=q, title=title, png_path=png_path, info_path=info_path, meta=meta))

    html_path = _write_compare_html(outdir, results, header=header)
    print(f"Report: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

