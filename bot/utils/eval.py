import async_tio


async def eval_python(code: str) -> str:
    """Evaluate Python 3 code and return the output."""
    async with async_tio.Tio() as runner:
        output = await runner.execute(code, language="python3")
        return output.stdout
