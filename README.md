# un-pko-deployments

Build scripts for the Hugging Face dataset [yuiseki/un-pko-deployments](https://huggingface.co/datasets/yuiseki/un-pko-deployments): UN peacekeeping deployments as points, read from the UN deployment maps by [Geo-Ref-skills](https://github.com/yuiseki/Geo-Ref-skills).

ABSOLUTELY NO WARRANTY. No accuracy is guaranteed (正確性は一切保証しません). The data are not in this repository; `data/` is uploaded to Hugging Face.

```sh
python scripts/build.py --src <Geo-Ref-skills GeoJSON dir> --year 2025 --refs <UN map numbers> --out data
hf upload yuiseki/un-pko-deployments data . --repo-type dataset
uvx --with pytest pytest -q tests
```

How it is made, and by what rules: [docs/handover.md](docs/handover.md) (Japanese).
