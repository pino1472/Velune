# Velune

リヴェルナ・オンラインをスマートフォンで読むための、GitHub Pages / PWA リーダーです。

## 仕組み

- 公開リポジトリ **pino1472/Velune** はリーダーのコードだけを保存します。
- 非公開リポジトリ **pino1472/Revalna** の `main:story/prose/` から、手動公開時だけ `第[数字]話.md` を取得します。
- 生成時に先頭の管理情報（frontmatter）を捨て、各話の **最初のH1見出しから下**をHTML化します。
- **`story/prose/INDEX.md` は公開しません。** 管理用の `canon/`, `state/`, `story/plot/` も公開しません。
- 全話を毎回検出するため、話数の増減や改題は次回の手動公開で反映されます。
- 8書体プリセット（Meiryo UI 等）、14色＋任意背景色、文字サイズ、行間、本文幅、目次検索、途中再開、キャッシュ／一括オフライン保存。
- なろう・カクヨムなど外部作品の機能はありません。

## 初回設定（GitHub UIで行う操作）

### 1. 非公開原稿を読むためのトークン

GitHubアカウントで **Fine-grained personal access token** を発行します。

- Resource owner: `pino1472`
- Repository access: **Only select repositories** → `Revalna` のみ
- Repository permissions: **Contents: Read-only**（Metadata: Read-only は自動付与）
- 有効期限は適切な期間を設定

作成したトークンは、このチャットやソースコードに貼らないでください。

Veluneの **Settings → Secrets and variables → Actions → New repository secret** で以下を登録します。

- Name: **`REVALNA_READ_TOKEN`**
- Secret: 発行したトークン

公開リポジトリ内のコードにトークンを書かず、Actions実行中だけ認証に使います。

### 2. Pagesの有効化

Veluneの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定します。

### 3. 公開

Veluneの **Actions → Publish Velune reader → Run workflow** を選びます。

原稿のコミット時には自動起動しません。公開したい時だけ操作します。

成功後の標準URLは **https://pino1472.github.io/Velune/** です。実際の公開URLはPages設定とActions実行結果を確認してください。

## 開発時のテスト

```sh
python -m pip install -r requirements.txt
python reader/test_build.py
```

ローカルで原稿を取り込む場合、`_source/story/prose/` にファイルを置いて `python reader/build.py` を実行します。生成物は `dist/` です。

## 安全性とオフライン

- GitHub Pagesでは **生成した小説本文は一般公開** されます（元リポジトリはPrivateのまま）。
- Actionsは `_source` から本文だけスパースチェックアウトします。公開するのは `dist/` のみです。
- 最初にサイトをオンラインで開くと読書画面をキャッシュし、開いた話は自動保存します。目次の「全話を保存」も使えます。
- オフラインキャッシュはブラウザのストレージ管理で削除される場合があります。旅行前などに保存件数と機内モードで動作確認してください。
- 未検証のまま「公開済み」「オフライン動作保証」とはみなしません。

公式参考資料:
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://github.com/actions/checkout
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
