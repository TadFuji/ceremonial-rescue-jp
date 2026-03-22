# Contributing to 冠婚葬祭レスキュー (ceremonial-rescue-jp)

まずは、このプロジェクトに興味を持っていただきありがとうございます！
どんな形の貢献でも歓迎します。

## 💬 参加の方法

### バグ報告 / 機能提案

- **バグ報告**: [Bug Report テンプレート](../../issues/new?template=bug_report.yml) を使用してください
- **機能提案**: [Feature Request テンプレート](../../issues/new?template=feature_request.yml) を使用してください

### コードの貢献

1. このリポジトリを **Fork** する
2. フィーチャーブランチを作成する (`git checkout -b feature/amazing-feature`)
3. 変更をコミットする (`git commit -m 'feat: add amazing feature'`)
4. ブランチにプッシュする (`git push origin feature/amazing-feature`)
5. **Pull Request** を作成する

## 📏 コーディング規約

### Python

- **Python 3.8+** との互換性を維持してください
- 外部ライブラリへの依存を追加しないでください（標準ライブラリのみ）
- `flake8 --max-line-length=120` でエラーが出ないこと
- 関数には docstring を記述してください
- 型ヒント（type hints）の使用を推奨します

### Markdown

- UTF-8 エンコーディングを使用してください
- 行末の空白を残さないでください

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) 形式に従ってください:

```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメントのみの変更
test: テストの追加・修正
refactor: 機能変更を伴わないコード修正
chore: ビルドプロセスやツールの変更
```

## 🧪 テストの実行

```bash
# 包括テスト (68チェック)
python ceremonial-rescue-jp/scripts/test_comprehensive.py

# 実プロンプトテスト (66チェック)
python ceremonial-rescue-jp/scripts/test_50_prompts.py
```

すべてのテストがパスすることを確認してから PR を作成してください。

## 📝 文化的コンテンツの貢献

冠婚葬祭のマナーは地域や宗派によって異なります。以下の点に注意してください:

- **出典を明記**: マナーや相場の情報には、可能な限り出典（書籍名・URL）を添えてください
- **地域差を考慮**: 「全国共通」なのか「地域限定」なのかを区別してください
- **宗派への配慮**: 特定の宗派を否定・軽視する表現を避けてください
- **断定を避ける**: 「〜が正しい」ではなく「〜が一般的です」「〜とされています」のように表現してください

## 🔍 レビュープロセス

1. PR が作成されると、CI で自動テストが実行されます
2. コードレビューを経て、問題がなければマージされます
3. テストが全パスしない PR はマージできません

## 📋 SKILL.md の行数制限

`SKILL.md` は **500行以下** を維持する必要があります（Agent Skills プラットフォームの制約）。
現在 354行です。大幅な追加を行う場合は、`references/` ディレクトリへの分離を検討してください。

## ❓ 質問がある場合

Issue を作成してください。ラベル `question` を付けていただけると助かります。

---

このプロジェクトに参加するすべての方は、[行動規範 (Code of Conduct)](CODE_OF_CONDUCT.md) に同意していただく必要があります。
