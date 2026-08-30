from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
bronze_dir = PROJECT_ROOT / "data" / "0_bronze"
silver_dir = PROJECT_ROOT / "data" / "1_silver"
gold_dir   = PROJECT_ROOT / "data" / "2_gold"

RAW_ASSOCIADOS_PATH = bronze_dir / "raw_associados.xlsx"

SHEET_ASSOCIADOS = "Associados"
SHEET_PRODUTOS = "Produtos"
SHEET_MOVIMENTACAO = "Movimentacao"

KEY_COLUMN = "CHAVE"
