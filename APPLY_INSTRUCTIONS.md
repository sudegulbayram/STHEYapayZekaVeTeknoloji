# How to apply these changes to your own repo clone

## Brand new files — just copy them in as-is:
- backend/Modelfile
- backend/README_LLM.md
- app/lib/api.ts   (new folder: app/lib/)
- .env.local.example (repo root)

## Fully-replaced files — overwrite your existing copy with these:
- backend/main.py
- backend/llm_service.py  (was empty in your repo — now has the SLM integration)
- backend/requirements.txt
- backend/.gitignore
- app/page.tsx

## Reference diffs (if you want to see exactly what changed instead of overwriting)
- page.tsx.diff
- main.py.diff
- requirements.txt.diff
- gitignore.diff

## Also, separately (goes in your TRAINING folder, not this app repo):
- export_gguf.py  -> put this inside veribootcamp/ (next to "local finetune.py")

## After training finishes:
1. Run export_gguf.py in your training folder -> produces output/hukuk_model_gguf/*.gguf
2. Copy that .gguf file into THIS repo's backend/ folder, named: hukuk_model_lora.gguf
   (must sit next to Modelfile)
3. cd backend && ollama create hukuk-danismani-slm -f Modelfile
