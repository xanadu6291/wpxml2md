[Japanese](README_J.md) | [English](README.md)

# wpxml2md

## 概要
WordPress エクスポート XML を Obsidian 向け Markdown に変換するツールです。

## 主な特徴
- WordPress XML の記事を 1記事1Markdown に変換
- Pandoc を利用した HTML→Markdown 変換
- Obsidian 向け front matter 出力
- タグ正規化
- 増分/更新分インポート
- コードブロック・画像リンク対応

## 必要なもの
 - Pandoc 3.x+
 - Python 3.9+
 - WordPressのエクスポート XML ファイル
 
  [Pandoc](https://pandoc.org/) が必要です。インストールしていない場合、[こちら](https://pandoc.org/installing.html) からダウンロードして下さい。  
  [Python](https://www.python.org/) が必要です。インストールしていない場合、[こちら](https://www.python.org/downloads/) からダウンロードして下さい。なお、macOS の場合 Tahoe 26.x 同梱の Python v3.9.6 でも動作確認済みです。
 
## 使い方
1. メディアファイルの準備  
   WordPress で用いているメディアファイル（画像、動画など）は、Obsidian Vault 内の適切な場所にコピーを用意するか、メディアファイルフォルダへのシンボリックリンクを張ります。  
2. ユーザー設定項目  
   スクリプトをテキストエディタで開き、スクリプト冒頭の **User Settings** を、お使いの環境に合わせて変更します。  
   `DEFAULT_OUT_DIR`：変換した Markdown のデフォルト出力先。デフォルトでは、筆者の環境に合わせたパスが設定されています。  
   `DEFAULT_SKIP_EXISTING`：出力済みファイルをスキップするかどうか。デフォルトでは、`True` すなわち、スキップするが設定されています。  
3. スクリプト実行権の付与  
    ```bash
    chmod +x wpxml2md.py
    ```
4. 実行例  
    基本  
    ```bash
    ./wpxml2md.py WordPress.xml
    ```
    
    全件再生成  
    ```bash
    ./wpxml2md.py WordPress.xml --force
    ```
    
    出力先指定  
    ```bash
    ./wpxml2md.py WordPress.xml --out ~/Desktop/Import
    ```
    
5. オプション  
   スクリプトには以下のオプションがあります。  
    ```text
    --include-pages       固定ページも出力する
    --all-status          公開以外も出力する
    --debug-title DEBUG_TITLE
                          指定文字列を含むタイトルだけ出力する
    --force               既存ファイルも再生成する
    --out OUT             出力先フォルダ（省略時はスクリプト内の既定値）
    ```

## 動作確認済み環境
- macOS Tahoe 26.x
- Python 3.9.6
- Python 3.14.5
- Pandoc 3.8.2
- Pandoc 3.10

スクリプトは Python だけで書かれているので、macOS 以外（Windows、Linux など）でも動作するはずです。

## 補足
### 出力済みファイルについて
   同じ `wordpress_post_id` を持つ記事は、`wordpress_post_modified` が同じ場合はスキップし、更新されている場合は上書き更新します。
### 画像リンクについて
   同一画像への自己リンク（WordPress の Lightbox 等）は、Obsidian では不要なため画像のみへ変換します。画像以外へのリンクや外部リンクは保持します。

## 終わりに
このスクリプトは、ChatGPT との対話を通じて設計・改善を行いました。最終的な仕様決定、検証、および環境への適用は筆者が行っています。

## ライセンス
このスクリプトには MIT License を採用しています。詳細は [LICENSE](LICENSE) をご確認ください。
