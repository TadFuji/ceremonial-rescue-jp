# ceremonial-rescue-jp Changelog

## v3.0 — 2026-03-22: ハイブリッドアーキテクチャ転換

### 概要
v2.1（全Web検索）→ v3（不変知識は静的DB + 変動情報のみWeb検索）

### 新規ファイル
- `references/etiquette.md` — のし袋、焼香手順、口頭セリフ、服装、招待状返信、行動NG、スピーチ構成、地域差
- `references/company_mode.md` — 会社対応3層フレーム、社内通知テンプレート、HR確認チェックリスト
- `references/ng_words.md` — NGワード統合辞書（弔事/慶事/お祝い/宗派別）+ 代替表現
- `scripts/test_50_prompts.py` — 50件リアルプロンプトテスト

### 変更ファイル
- `SKILL.md` — §6を「Hybrid Knowledge Strategy」に改修、ステップ8+9を統合し354行に最適化

### 変更なし
- `scripts/amount_validator.py`, `ng_word_checker.py`, `date_validator.py`, `test_comprehensive.py`
- `assets/templates/` 12ファイル

### 検証
- test_comprehensive.py: 68/68 全パス
- test_50_prompts.py: 66/66 全パス（50シナリオ + 3 references検証）
- 合計134チェック全パス

---

## v2.1 — 2026-03-22: イベント拡張

### 概要
6つの新イベント追加: お中元、お歳暮、年賀状、快気祝い、入学祝い、還暦祝い

### 新規テンプレート
- `seasonal_gift.md`, `new_year_card.md`, `celebration_message.md`

### 変更ファイル
- `SKILL.md` — §3 分類表拡張、§6 検索パターン追加
- `amount_validator.py` — gift_ranges 追加（お中元/お歳暮/快気祝い/入学祝い/七五三/還暦）
- `ng_word_checker.py` — celebration タイプ追加（快気祝い向けNG）

### 検証
- test_comprehensive.py: 68/68 全パス（52→68に拡張）

---

## v2.0 — 2026-03-22: Web検索ベースへの全面転換

### 概要
静的DB（references/ 6ファイル）→ リアルタイムWeb検索ベースに全面置換

### 削除
- 旧 `references/` 6ファイル

### 変更ファイル
- `SKILL.md` — §6を「Web Research Strategy」に変更

---

## v1.0 — 2026-03-22: 初版

### 概要
冠婚葬祭レスキュースキル初版。葬儀・結婚式に対応。

### ファイル構成
- `SKILL.md` — 9ステップワークフロー
- `references/` — 6ファイル（作法、金額、NGワード等）
- `scripts/` — 3本（amount_validator.py, ng_word_checker.py, date_validator.py）
- `assets/templates/` — 9テンプレート
