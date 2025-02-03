import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

async def main(app: Dict[str, Any]):
    pass

if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    asyncio.run(main())