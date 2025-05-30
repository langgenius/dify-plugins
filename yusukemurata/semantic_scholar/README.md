# Dify Semantic Scholar Search Plugin

**Author:** yusukemurata  
**Version:** 0.0.1  
**Type:** Tool Plugin  
**Category:** Search

## Overview

This plugin provides comprehensive academic paper search capabilities using the Semantic Scholar API. It enables researchers, developers, and analysts to discover and analyze academic papers with advanced search features, detailed paper information retrieval, and intelligent snippet extraction.

## Key Features

### 🔍 Advanced Paper Search
- **Intelligent Search**: Enhanced search capabilities with venue and date filtering
- **Flexible Results**: Configurable result limits (1-50 papers)
- **Multi-language Support**: Works with queries in multiple languages
- **Venue Filtering**: Search within specific journals or conferences
- **Date Range Filtering**: Filter papers by publication year range

### 📚 Detailed Paper Information
- **Comprehensive Data**: Title, authors, abstract, citation count, publication details
- **Citation Analysis**: View latest citing papers and key references  
- **TL;DR Summaries**: Concise paper summaries when available
- **Open Access Links**: Direct links to free PDF versions when available
- **Publication Metadata**: Venue, publication date, external IDs

### 📝 Snippet Extraction
- **Context-Aware Search**: Find specific text snippets within papers
- **Relevance Scoring**: Results ranked by relevance to your query
- **Full-Text Display**: Complete snippet content without truncation
- **Source Attribution**: Clear linking back to original papers
  - Impermanent Loss
  - Governance Tokens

## 技術仕様

### API統合
- **Semantic Scholar Graph API**: 最新のv1 APIを使用
- **レート制限対応**: APIキー使用で高い制限値を設定可能
- **エラーハンドリング**: 堅牢なエラー処理とユーザーフレンドリーなメッセージ

### 認証設定
```yaml
credentials_for_provider:
  api_key:
    type: secret-input
    required: false  # APIキーはオプション
```

## インストールと設定

### 1. 環境要件
- Python 3.12+
- Dify Plugin SDK
- requests ライブラリ

### 2. プラグインのインストール
```bash
# プラグインのパッケージ化
dify plugin package ./semantic_scholar

# Difyプラットフォームでインストール
```

### 3. API設定（オプション）
1. [Semantic Scholar API](https://www.semanticscholar.org/product/api)でAPIキーを取得
2. Difyプラットフォームでプラグイン設定にAPIキーを入力
3. より高いレート制限でAPIを利用可能

## 使用方法

### セマンティック検索
```
Query: "smart contract security vulnerabilities"
Max Results: 20
Include Snippets: true
```

### 論文詳細取得
```
Paper ID: "204e3073870fae3d05bcbc2f6a8e263d9b72e776"
Include Citations: true
Include Abstract: true
```

## 出力例

### 検索結果
```json
{
  "query": "liquidity pools",
  "total_results": 15,
  "papers": [
    {
      "paperId": "...",
      "title": "An Analysis of Liquidity in Decentralized Exchanges",
      "authors": "Smith, J., Johnson, A.",
      "year": 2023,
      "citationCount": 42,
      "abstract": "This paper analyzes...",
      "Dify_snippets": [
        "Liquidity pools are fundamental to AMM protocols",
        "Impermanent loss affects liquidity providers..."
      ]
    }
  ]
}
```

## 開発とデバッグ

### ローカル開発環境
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 開発モードで実行
python -m main
```

### リモートデバッグ
1. `.env`ファイルでリモートデバッグキーを設定
2. `INSTALL_METHOD=remote`に設定
3. Difyプラットフォームでプラグインをテスト

## ライセンス

このプラグインはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。Dify研究コミュニティの発展に貢献しましょう。

---

**開発者:** yusukemurata  
**GitHub:** [プロジェクトリポジトリ]  
**Dify Marketplace:** [プラグインページ]



