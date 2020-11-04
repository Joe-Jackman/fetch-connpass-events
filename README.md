# create compass schedule

# アプリの目的
コンパスから特定のキーワードでイベントを取得してGoogleカレンダーに追加します。

# 設定
- GoogleのOauth認証を行うための設定をお願いします。
  - 詳しくはこちら → https://cloud.google.com/iap/docs/authentication-howto?hl=ja
- credentials.sample.jsonのファイル名を変更し、credentials.jsonに変更してください。
- Googleで作成した内容をcredentials.jsonに記載してください
- credential.jsonの中のKEYWORD変数を変更して必要なキーワードに変更してください
- 実行すれば該当のキーワードのイベントを取得してカレンダーに登録します