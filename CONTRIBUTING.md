# Git / PR 運用ルール（project-root）

このリポジトリは **1つのリポジトリ（monorepo）** で、以下のLambdaを同居させて管理します。

- `input-handler/`（A担当）
- `ai-handler/`（B担当）
- `save-handler/`（C担当）
- `shared/`（共通コード：必要になったら）
- `infrastructure/`（CDK/SAM/Terraform など）

---

## 1. 基本方針

- `main` ブランチは **常にデプロイ可能な状態** を保つ
- `main` への **直pushは禁止**（必ずPR）
- 原則 **1作業 = 1ブランチ = 1PR**
- 生成物（zip等）・Secrets（APIキー等）は **絶対にコミットしない**

---

## 2. ブランチ運用

### 2.1 ブランチの種類
- `main`：安定版（保護対象）
- `feature/*`：機能追加
- `fix/*`：バグ修正
- `chore/*`：設定変更、依存更新、整理
- `docs/*`：ドキュメント更新
- `refactor/*`：仕様変更なしのリファクタ

### 2.2 ブランチ名の例
- `feature/input-validate-signature`
- `feature/ai-danger-score-v1`
- `fix/save-mask-phone`
- `chore/update-deps`

---

## 3. PR（Pull Request）ルール

### 3.1 PRのサイズ
- 「PRの説明が1文で言える」粒度を目安に **小さく**
- リファクタ（整理）と仕様変更（動作変更）は **混ぜない**

### 3.2 マージ条件（最小）
- CI（Lint/テスト）が通る
- レビュー承認（最低1人）
- 影響範囲が明記されている（特にスキーマ変更）

### 3.3 mainの取り込み
PRを出す前に、できるだけ **最新のmain** を取り込む（初心者はmerge推奨）。

```bash
git checkout main
git pull
git checkout feature/your-branch
git merge main
```

---

## 4. このプロジェクト特有の注意（事故防止）

### 4.1 “同じファイルを触ってなくても壊れる”問題
`input → ai → save` で **イベント形式（キー/型）** がズレると、別ファイルでも実行時に壊れます。

**ルール**
- イベントスキーマ（input→ai / ai→save）の変更があるPRは、PR本文で必ず `スキーマ変更：あり` と明記
- 破壊的変更は可能なら段階的に（例：新キー追加 → 両対応 → 旧キー削除）

### 4.2 shared/ や infrastructure/ の変更
影響が広いので **レビュー必須**（CODEOWNERS推奨）。

---

## 5. コミットメッセージ規約（推奨）

- `feat:` 機能追加
- `fix:` バグ修正
- `chore:` 雑務（設定/依存/整理）
- `docs:` ドキュメント
- `refactor:` 仕様変更なしの整理

例：
- `feat: add input payload validation`
- `fix: correct danger score threshold`
- `chore: update ai-handler dependencies`

---

## 6. 推奨：マージ方法
- **Squash merge** 推奨（`main` の履歴がPR単位で綺麗になる）

---

## 7. 作業の基本手順（型）

```bash
# 1) mainを最新化
git checkout main
git pull

# 2) ブランチ作成
git checkout -b feature/your-work

# 3) 作業 → コミット
git add .
git commit -m "feat: your change"

# 4) push → PR作成
git push -u origin feature/your-work
```

---

## 8. 追加で入れると強い（任意）
- `.github/CODEOWNERS`：担当ディレクトリの自動レビュワー指定
- `.github/workflows/ci.yml`：Lint/テストの自動実行
- `docs/contracts/*`：イベント契約（スキーマ）ドキュメント
