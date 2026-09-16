# Executive workbench (web)

Interactive six-page supply-chain dashboard that reads `public/data/dashboard.json` produced by `python scripts/run_pipeline.py`.

This is a demonstration surface. The interview-facing BI layer is still Power BI Desktop using `data/processed/powerbi/*.csv` — see `dashboard/powerbi/`.

```bash
cd web
npm install
npm run dev
```

Opens on `http://127.0.0.1:43125`.
