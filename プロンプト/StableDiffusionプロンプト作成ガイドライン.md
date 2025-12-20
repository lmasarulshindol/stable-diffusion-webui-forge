# StableDiffusionプロンプト作成ガイドライン

## 基本原則

### 1. 明確性と具体性
- 曖昧な表現を避け、具体的なタグを使用する
- シチュエーション、ポーズ、表情、服装などを明確に指定する
- 複数の要素を組み合わせる場合は、優先順位を考慮する

### 2. 一貫性の維持
- キャラクター設定やシチュエーションを統一する
- 矛盾するタグを同時に使用しない（例：`lying on back`と`standing`）

### 3. 品質タグの適切な使用
- 基本品質タグは必須：`high quality`, `detailed`, `best quality`, `masterpiece`
- 解像度タグ：`8k`, `high definition`（必要に応じて）
- スタイルタグ：`anime style`（アニメ風の場合）

---

## 精液が垂れる描写に関する重要ルール

### ⚠️ 必須：垂れる場所を明確に指定する

精液が垂れる描写を記述する際は、**必ず「どこから垂れているのか」を明確に書くこと**。曖昧な表現は避ける。

### ✅ 正しい例

#### 膣から垂れる場合
```
cum dripping from vagina, cum dripping from pussy, semen dripping from pussy, cum leaking from vagina, cum flowing from pussy, cum oozing from pussy
```

#### 口から垂れる場合
```
cum dripping from mouth, cum dripping from lips, semen dripping from mouth, cum leaking from mouth, cum flowing from lips, cum oozing from mouth
```

#### ペニスの先端から垂れる場合
```
cum dripping from penis tip, cum dripping from cock tip, semen dripping from penis, cum leaking from penis tip, precum dripping from penis
```

#### 顔から垂れる場合
```
cum dripping from face, cum dripping down face, semen dripping from cheek, cum dripping from chin, cum dripping from nose, cum dripping from forehead
```

#### 胸から垂れる場合
```
cum dripping from chest, cum dripping from breasts, semen dripping down breasts, cum dripping from nipples, cum dripping from cleavage
```

#### 太ももから垂れる場合
```
cum dripping from thighs, cum dripping down thighs, semen dripping from inner thighs, cum flowing down legs
```

#### 複数の場所から垂れる場合
```
cum dripping from vagina, cum dripping from mouth, cum dripping from face, semen dripping from pussy, cum dripping down thighs
```

### ❌ 間違った例（避けるべき表現）

```
cum dripping, semen dripping, cum leaking, cum flowing
```
→ **問題点**: どこから垂れているのかが不明確

```
dripping cum, leaking semen
```
→ **問題点**: 場所の指定がない

### 推奨タグの組み合わせ

精液が垂れる描写をより明確にするために、以下のような組み合わせを推奨：

```
cum dripping from vagina, cum leaking from pussy, semen dripping from pussy, visible cum, white liquid, thick cum, cum trail, cum stream
```

#### 追加の詳細タグ
- `visible cum` - 精液が見える
- `white liquid` - 白い液体
- `thick cum` - 濃い精液
- `cum trail` - 精液の跡
- `cum stream` - 精液の流れ
- `cum dripping down` - 下に垂れる
- `cum flowing out` - 外に流れ出る
- `cum oozing` - 精液がにじみ出る

---

## プロンプト構造の推奨順序

### 推奨される順序

1. **ポーズ・シチュエーション**
   - `doggy style`, `missionary position`, `standing sex` など

2. **身体の状態・位置**
   - `on all fours`, `lying on back`, `kneeling` など

3. **服装・外見**
   - `school uniform`, `white dress`, `nude` など

4. **性行為の状態**
   - `penetration`, `insertion`, `penis visible` など

5. **精液・射精の描写**（該当する場合）
   - **必ず「どこから」を明確に指定**
   - `cum dripping from vagina`, `cum dripping from mouth` など

6. **表情・反応**
   - `blushing face`, `moaning expression`, `tears` など

7. **身体の反応**
   - `body shaking`, `sweat`, `hair disheveled` など

8. **環境・背景**
   - `on bed`, `bedroom setting`, `studio setting` など

9. **品質タグ**
   - `anime style`, `high quality`, `detailed`, `best quality`, `masterpiece`

10. **構図・視点**
    - `from behind`, `from side angle`, `close-up` など

---

## ネガティブプロンプトの基本

### 必須項目

```
lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, deformed, ugly, bad proportions, duplicate, morbid, mutated, extra limbs, bad body, bad face, bad eyes, out of frame, long neck, bad arms, bad legs, bad perspective, bad angle, bad lighting, oversaturated, underexposed, grainy, pixelated, distorted, blurry, multiple people, extra people, extra characters
```

### シチュエーションに応じた追加

- 年齢設定が重要な場合：`adult woman`, `mature body`, `developed breasts` など
- 性的コンテンツの場合：必要に応じて特定の要素を除外

---

## よくある間違いと対処法

### 1. 精液の描写が曖昧
- ❌ `cum dripping`
- ✅ `cum dripping from vagina` または `cum dripping from mouth`

### 2. 矛盾するポーズ
- ❌ `lying on back, standing`
- ✅ `lying on back` または `standing`（どちらか一方）

### 3. 品質タグの不足
- ❌ 品質タグなし
- ✅ `high quality, detailed, best quality, masterpiece` を必ず含める

### 4. 過剰なタグの使用
- ❌ 100個以上のタグを詰め込む
- ✅ 必要な要素に絞り、20-50個程度を目安にする

### 5. キャラクター設定の不一致
- ❌ 同じキャラクターで年齢や外見が異なる
- ✅ キャラクター設定ファイルを参照し、一貫性を保つ

---

## プロンプト作成チェックリスト

プロンプトを作成したら、以下を確認：

- [ ] 精液が垂れる描写がある場合、「どこから垂れているのか」を明確に指定しているか
- [ ] ポーズやシチュエーションが明確か
- [ ] 矛盾するタグがないか
- [ ] 品質タグが含まれているか
- [ ] ネガティブプロンプトが適切に設定されているか
- [ ] キャラクター設定が一貫しているか
- [ ] 必要な要素がすべて含まれているか

---

## 精液描写の詳細な例

### シーン別の推奨プロンプト

#### 中出し後の後背位（膣から垂れる）
```
doggy style, rear entry, on all fours, hands and knees, on bed,
penis pulled out, after penetration,
cum dripping from vagina, cum dripping from pussy, semen dripping from pussy, cum leaking from pussy, cum flowing from pussy, visible cum, white liquid,
blushing face, panting, heavy breathing, body trembling,
anime style, high quality, detailed, best quality, masterpiece
```

#### フェラチオ後の顔射（顔から垂れる）
```
kneeling on floor, looking up,
cum dripping from face, cum dripping down face, semen dripping from cheek, cum dripping from chin, cum dripping from nose, cum dripping from forehead, cum dripping from lips, visible cum, white liquid, cum on face,
blushing face, surprised expression, eyes wide open,
anime style, high quality, detailed face, best quality, masterpiece
```

#### 口内射精後（口から垂れる）
```
kneeling on floor, performing oral sex,
penis pulled out, after ejaculation,
cum dripping from mouth, cum dripping from lips, semen dripping from mouth, cum leaking from mouth, cum flowing from lips, visible cum, white liquid, cum trail,
blushing face, mouth open, innocent expression,
anime style, high quality, detailed face, best quality, masterpiece
```

#### 複数箇所から垂れる（顔射＋膣から）
```
lying on back, legs spread,
cum dripping from vagina, cum dripping from pussy, cum dripping from face, cum dripping down face, semen dripping from pussy, cum dripping from mouth, visible cum, white liquid, cum trail,
blushing face, panting, body trembling,
anime style, high quality, detailed, best quality, masterpiece
```

---

## 推奨設定

### 基本設定
- **Aspect Ratio:** 2:3 または 3:4（縦長）、または 16:9（横長）
- **Resolution:** 512x768 以上推奨（縦長）、または 768x512 以上（横長）
- **Steps:** 25-35（詳細な描写のため）
- **CFG Scale:** 8-10（シチュエーションを明確に）
- **Sampler:** DPM++ 2M Karras または Euler a
- **Face Restoration:** 必要に応じて（表情の詳細化）

---

## まとめ

1. **精液が垂れる描写は必ず「どこから垂れているのか」を明確に指定する**
2. プロンプトは明確で具体的に記述する
3. 品質タグを必ず含める
4. 矛盾するタグを使用しない
5. キャラクター設定の一貫性を保つ
6. ネガティブプロンプトを適切に設定する

このガイドラインに従うことで、より正確で意図した通りの画像生成が可能になります。

