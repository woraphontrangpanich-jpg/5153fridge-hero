# 5153fridge-hero
Empowering Zero-Waste Cooking through RAG-Driven Recipe Retrieval   and Intelligent Substitutions   BT5153 Applied Machine Learning for Business Analytics  |  Group 9

Due to GitHub file size limits, large assets are hosted externally:
https://drive.google.com/drive/folders/14sl190npA_72KZpkaZbQJlzZPX-1lIz2?usp=sharing

Contents include:

1. /data
- Original source datasets from the Food.com Kaggle dataset
- Includes raw input files used in the project
- Some files are original datasets, while some are cleaned/derived preprocessing outputs

2. /output
- Generated processed outputs (e.g. cleaned recipe data, enriched profiles)

3. /chroma_recipes (ChromaDB)
- Persisted vector database used for semantic recipe retrieval
- Includes embeddings and collection files needed to run retrieval without rebuilding

## Notebooks overview

notebook_01_customer_profile.ipynb
Builds enriched user profiles from raw interactions + recipes.
It computes behavior stats per user, runs LLM inference for dietary preferences, and saves:
output/user_profile_enriched.csv
output/eval_user_ids.csv (users prioritized for NB3 evaluation)
notebook_02_2_recipe_knowledge_base.ipynb
Builds the recipe retrieval knowledge base.
It cleans recipes, creates SBERT embeddings, stores them in ChromaDB, and saves:
output/recipe_clean.csv
chromadb/ collection (recipes)
output/substitution.json (ingredient substitutions from cleaned Food.com substitution data)
notebook_03_pipeline_eval_ui.ipynb
End-to-end pipeline notebook: EDA + KMeans + NCF + hybrid RAG ranking + evaluation + Gradio app.
It consumes outputs from NB1/NB2, trains/evaluates models, writes evaluation artifacts, and launches the UI.
Run order
NB1 -> NB2 -> NB3

## How to run
Python 3.11.x recommended
cd fridgehero
Install notebook dependencies (if not already installed):
pip install jupyter pandas numpy matplotlib seaborn scikit-learn torch tqdm requests sentence-transformers chromadb gradio ragas langchain-community
Start Ollama in another terminal:
ollama serve
Pull models used by notebooks:
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
Launch Jupyter:
jupyter lab
Open each notebook and run all cells in order (Restart Kernel and Run All recommended).