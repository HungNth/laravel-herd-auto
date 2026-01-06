import asyncio


async def main():
    from container import wp
    latest_version = wp.wp_latest_version()
    print(f"Latest WordPress version: {latest_version}")


if __name__ == '__main__':
    asyncio.run(main())
