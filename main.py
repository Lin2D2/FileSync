import asyncio
from package.app import App

if __name__ == "__main__":
    app = App()
    asyncio.run(app.start())
