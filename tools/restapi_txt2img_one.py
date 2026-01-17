"""
Forge (A1111系) のREST APIを使って txt2img を1枚生成して保存する最小スクリプト。

前提:
- WebUI/Forge を起動していること（通常 http://127.0.0.1:7860 ）
- APIが有効であること（起動オプションに `--api` を付ける）

実行例:
  python tools/restapi_txt2img_one.py --prompt "a scenic landscape, ultra detailed" --out out.png

認証がある場合:
  python tools/restapi_txt2img_one.py --api-user user --api-pass pass --out out.png

モデル指定（チェックポイント切替）:
  python tools/restapi_txt2img_one.py --checkpoint "animagineXLV31_v31.safetensors" --prompt "..." --out out.png

モデル一覧:
  python tools/restapi_txt2img_one.py --list-models
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
from typing import Any

import requests


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _decode_base64_image(b64: str) -> bytes:
    # 稀に "data:image/png;base64,..." 形式で来る可能性に備える
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
            "- Forgeを `--api` 付きで起動してください（例: webui-user.bat の COMMANDLINE_ARGS に --api を追加）\n"
            "- `--subpath` を使っている場合は `--base-url http://127.0.0.1:7860/<subpath>` を指定してください\n"
            f"- URL: {url}\n"
        )
    r.raise_for_status()
    # /options は空bodyのこともあるのでJSON変換は保険
    try:
        return r.json()
    except Exception:
        return {}


def _pick_checkpoint_title(models: list[dict[str, Any]], query: str) -> str:
    q = query.strip().lower()
    if not q:
        raise ValueError("checkpoint名が空です")

    # まず title の完全一致（大小無視）
    for m in models:
        title = str(m.get("title", ""))
        if title.lower() == q:
            return title

    # 次にファイル名（末尾一致）を許容
    suffix_matches = []
    for m in models:
        title = str(m.get("title", ""))
        if title.lower().endswith(q):
            suffix_matches.append(title)
    if len(suffix_matches) == 1:
        return suffix_matches[0]

    # 次に部分一致（候補が1つだけなら採用）
    contains_matches = []
    for m in models:
        title = str(m.get("title", ""))
        if q in title.lower():
            contains_matches.append(title)
    if len(contains_matches) == 1:
        return contains_matches[0]

    # 見つからない or 候補が複数
    candidates = suffix_matches or contains_matches
    if not candidates:
        raise RuntimeError(
            f"checkpoint '{query}' が見つかりません。--list-models で一覧を確認してください。"
        )
    preview = "\n".join(f"- {c}" for c in candidates[:30])
    raise RuntimeError(
        f"checkpoint '{query}' の候補が複数あります（より具体的に指定してください）:\n{preview}"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:7860", help="WebUIのURL（例: http://127.0.0.1:7860 ）")
    p.add_argument("--api-user", default=None, help="--api-auth を設定している場合のユーザー名")
    p.add_argument("--api-pass", default=None, help="--api-auth を設定している場合のパスワード")

    p.add_argument("--list-models", action="store_true", help="APIから利用可能なチェックポイント一覧を表示して終了")
    p.add_argument("--checkpoint", default=None, help="生成前に切り替えるチェックポイント（title/ファイル名の一部でも可）")

    p.add_argument("--prompt", required=True, help="プロンプト")
    p.add_argument("--negative", default="", help="ネガティブプロンプト")

    p.add_argument("--steps", type=int, default=28)
    p.add_argument("--cfg-scale", type=float, default=7.0)
    p.add_argument("--sampler", default="Euler", help="sampler_index（例: Euler, DPM++ 2M など）")
    p.add_argument("--seed", type=int, default=-1, help="-1 でランダム")

    p.add_argument("--width", type=int, default=768)
    p.add_argument("--height", type=int, default=768)

    p.add_argument("--out", default=None, help="出力PNGパス（省略時は自動命名）")
    p.add_argument("--timeout", type=float, default=600.0)

    args = p.parse_args()

    base_url = _normalize_base_url(args.base_url)

    auth = None
    if args.api_user is not None or args.api_pass is not None:
        auth = (args.api_user or "", args.api_pass or "")

    if args.list_models:
        models = _api_get(base_url, "/sdapi/v1/sd-models", auth=auth, timeout=args.timeout)
        # title だけ出す（長いので必要最低限）
        for m in models:
            print(m.get("title", ""))
        return 0

    # 生成前にチェックポイントを切り替えたい場合
    if args.checkpoint:
        models = _api_get(base_url, "/sdapi/v1/sd-models", auth=auth, timeout=args.timeout)
        title = _pick_checkpoint_title(models, args.checkpoint)
        _api_post(
            base_url,
            "/sdapi/v1/options",
            {"sd_model_checkpoint": title},
            auth=auth,
            timeout=args.timeout,
        )
        print(f"Checkpoint set: {title}")

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

    out_path = args.out
    if not out_path:
        ts = time.strftime("%Y%m%d-%H%M%S")
        out_path = os.path.join(os.getcwd(), f"txt2img-{ts}.png")

    img_bytes = _decode_base64_image(images[0])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(img_bytes)

    # 生成情報（あれば）を横に保存（A1111系は info がJSON文字列のことが多い）
    info_obj = _safe_json_loads(data.get("info", ""))
    info_path = os.path.splitext(out_path)[0] + ".info.json"
    try:
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info_obj, f, ensure_ascii=False, indent=2)
    except Exception:
        # infoが巨大/壊れている場合でも画像保存は成功させる
        pass

    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

