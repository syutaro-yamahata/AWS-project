# AWS企業プロジェクト（見守り・相談チャットBot）

## 概要
LINEから中高生の悩み相談を匿名で受け付け、Bedrockで応答生成し、保存前に個人情報をマスキングしてDynamoDBへ保存します。

## 全体構成
LINE → API Gateway → Lambda → Bedrock → Lambda(マスキング) → DynamoDB(TTL) → CloudWatch

## ディレクトリ構成
- input-handler/ : LINE Webhook受信〜イベント整形（岩﨑）
- ai-handler/    : AI応答生成・分類ロジック（山端）
- save-handler/  : マスキング・保存・TTL・監査ログ（小西）
- shared/        : 共通モジュール（任意）
- infrastructure/: IaC（CDK/SAM/Terraform 任意）
