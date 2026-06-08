import os
from dotenv import load_dotenv
from pathlib import Path
print('cwd', Path.cwd())
print('exists', Path('.env').exists())
print('raw', Path('.env').read_text(encoding='utf-8'))
load_dotenv(dotenv_path=Path('.env'), override=True)
print('BOT_TOKEN', repr(os.getenv('BOT_TOKEN')))
print('ADMIN_ID', repr(os.getenv('ADMIN_ID')))
