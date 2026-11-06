# 引き継ぎ: un-pko-deployments の作り方と基準

このリポジトリは、Hugging Face のデータセット [yuiseki/un-pko-deployments](https://huggingface.co/datasets/yuiseki/un-pko-deployments) を作るためのスクリプトである。データそのものは Hugging Face にだけ置き、このリポジトリには入れない (`data/` は git の管理外)。

国連の平和維持活動 (PKO) の部隊配置図 (PDF) から、部隊の位置を点として取り出したものを、年ごとのサブセットにして公開する。取り出しは、別のリポジトリ [Geo-Ref-skills](https://github.com/yuiseki/Geo-Ref-skills) のスキルで行う。LLM と VLM は使わない。

このマシン固有のパス、動いているプロセス、使い捨てのスクリプトは、`tmp/` (git の管理外) に書いてある。

## 全体の流れ

1 つの年を足すときの流れは次のとおりである。

1. 位置合わせ: Geo-Ref-skills の `deployment-batch` で、その年の PDF を位置合わせする。地名で基準点を作り (`name-gcps`)、合わなければ枠の経緯度の目盛りか UTM の方眼で作る (`graticule-gcps`)。どちらも関門 (`georef-gates`) を通った答えだけを使う。
2. 部隊の読み取りと GeoJSON: `deployment-geojson` が、部隊の記号を読み (`unit-symbols`)、位置合わせの変換で経緯度にし、公開できる形の GeoJSON を地図ごとに書く。
3. 確かめ: 点がミッションの範囲に収まるか、町の位置と合うかを確かめる (下の「確かめ方」)。
4. 選ぶ: 公開しない地図を除く (下の「入れない基準」)。
5. 組み立て: `scripts/build.py` で `data/<年>/` を作る。
6. カード: `data/README.md` に、その年の config と表を足す。
7. 公開: `data/` を Hugging Face に上げ、上がったものを取り直して確かめる。

## 位置合わせの基準

- 関門は緩めない。関門を通らない地図は、通らないまま記録する。
- 地図全体の答えが関門を全て通ったら、その地図の点を全て使う。
- 点の広がりの関門だけで落ちた地図 (拡大図、町が一部に偏る地図) は、点ごとに確かめた点だけを使う。基準点の凸包の中 (3 px の余裕) にあり、基準点を 1 つずつ抜いたときの動きが 3 px 以下の点である。
- 経緯度の目盛りから基準点を作るのは、交点の広がりが 3 度以内の地図だけである。MINUSMA の 2024 年の図 (15 度) は、関門を通ったのに Bamako を 20 km ずらした。
- UTM の方眼の図は帯を書いていない。帯はミッションごとの表 (`deployment-batch` の `UTM_ZONES`、UNIFIL は 36N) で与える。帯を間違えると、関門は通ったまま経度 6 度ずれる。

## 確かめ方

関門は、基準点どうしの一致を確かめるだけで、真の位置の正しさは確かめない。公開の前に、関門とは別に次を確かめる。

- ミッションごとに、点の経緯度の範囲を出し、作戦地域に収まるかを見る。2024 年と 2025 年の範囲は次のとおりだった。

  | ミッション | 経度 | 緯度 |
  | --- | --- | --- |
  | MINUSCA | 14.6〜26.5 | 3.5〜10.3 |
  | MONUSCO | 15.5〜30.3 | -5.1〜1.6 |
  | UNMISS | 27.4〜33.7 | 4.1〜11.7 |
  | UNIFIL | 35.1〜35.7 | 33.1〜33.4 |
  | UNDOF | 35.8〜36.2 | 32.8〜33.4 |
  | UNFICYP | 32.7〜34.0 | 35.0〜35.2 |
  | UNMIK | 20.9〜21.2 | 42.8〜42.9 |

- 新しい種類の地図、新しい基準点の作り方 (目盛り、方眼) を使った地図は、町の印と、自前の Nominatim (地名検索) が返す町の位置を比べる。名前の一致する町の多くが数百 m 以内に入ればよい。名前の取り違え (同名の別の町) で数十 km 以上になる行は無視する。UNDOF は 30〜130 m、UNIFIL は 40〜450 m だった。
- 点の数が前の版から大きく変わった地図は、部隊の読み取りを絵に描いて (`unit_symbols.py --debug`)、引き出し線が正しい町に付いているかを目で見る。
- 地図の作図上のずれは、そのまま残る。MONUSCO の Kinshasa の印は、Brazzaville の印と重ならないよう、東へ約 0.35 度ずらして描かれている。

## 入れない基準

- 位置合わせができなかった地図 (関門を通らず、点ごとの確かめも通らない)。2024 年と 2025 年の UNISFA、2024 年の MINURSO。
- 確かめで、町から大きくずれた点が見つかった地図。2024 年の MINUSMA (Bamako の点が約 20 km ずれ)。
- 部隊が 1 つも読めなかった地図 (中身が空の GeoJSON)。2024 年の UNMOGIP。
- 入れなかった地図と理由は、必ずカードに書く。

位置が読めなかった部隊は、推測で補わずに除く。地図ごとの内訳 (位置なし、凸包の外、不確か) は、Geo-Ref-skills の `summary.jsonl` に残る。

## 公開の形 (国連の地図の利用条件)

国連の地図から作った派生物として扱う。

- 各ファイルに "Based on United Nations map" と書く。
- 国連の地図の参照番号 (4 桁か 5 桁の数) は、ファイル名、属性、カードのどこにも入れない。`build.py` は、`--refs` で渡した番号が出力のどこかにあれば、何も書かずに止まる。番号は、その年の PDF のファイル名と題名にある 4〜5 桁の数を全て渡す (年を表す 20xx は除く)。
- 元の PDF の SHA-256 と、取り出したツールのコミットを入れる。
- 正確性は一切保証しないことを、カードの冒頭 (日本語と英語)、各ファイルの `disclaimer`、各点の `no_warranty` に書く。
- 日付 (`map_date`) は PDF の作成日で、地図が表す日付とは限らないことを、カードに書く。

## 組み立てと公開のコマンド

```sh
# data/<年>/ を作る (geojson/ と points.jsonl)
python scripts/build.py --src <公開する GeoJSON だけを置いたディレクトリ> --year 2024 --refs <参照番号...> --out data

# テスト
uvx --with pytest pytest -q tests

# Hugging Face に上げる (data/ の中身がデータセットの根になる)
uvx --from huggingface_hub hf upload yuiseki/un-pko-deployments data . --repo-type dataset --commit-message "<年>: ..."

# 上がったものを取り直して確かめる
curl -sL https://huggingface.co/datasets/yuiseki/un-pko-deployments/resolve/main/<年>/points.jsonl | wc -l
curl -sL https://huggingface.co/datasets/yuiseki/un-pko-deployments/resolve/main/README.md | grep -c "正確性は一切保証しません"
```

`points.jsonl` は 1 件 1 行で、並びは固定 (ミッション、日付、ファイル、積み、ラベル、略語、経度、緯度の順) である。同じ入力からは同じファイルができる。

## カードの書き方

- 年ごとに config (`"2024"` など) を足し、`data_files` をその年の `points.jsonl` にする。
- 冒頭の無保証の注記は消さない。
- 年ごとに、ミッション、地図の数、地図上の部隊数、位置が付いた部隊数、基準点の作り方の表を書く。
- 入れなかった地図とその理由を書く。

カードは `data/README.md` にあり、`data/` ごと git の管理外である。カードの変更は Hugging Face の履歴にだけ残る。

## 気をつけること

- 実データを読む処理は、メモリと CPU に上限を掛けて流す (`systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 -p CPUQuota=400%`)。
- 地名検索や地図のタイルに、OpenStreetMap の公開サーバーを使わない。自前のサーバーだけを使う。
- 作業ディレクトリの中のファイルは消さない。やり直すときは、新しいディレクトリ (`geojson-v2`、`runs-v2` など) に書く。
- 位置合わせのバッチを、別のエージェントと同時に流さない。スキルを直すと、走っている処理の途中で中身が変わる。
- スキルの不具合は、データを足す前にスキルとテストを直し、Geo-Ref-skills の `docs/failures/` に失敗の記録を残す。
- 新しい年の地図は、道具を直すときに見てしまうと、その年の数字は評価にならない。直すために見た地図は、カードかスキルの記録にそう書く。
