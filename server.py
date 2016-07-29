from aiohttp import web
import aiohttp_jinja2

@aiohttp_jinja2.template('index.html')
async def handle(request):
    return {}

async def shirish(request):
	data = await request.json()
	print(data)
	return web.Response()

app = web.Application()
app.router.add_route('GET', '/', handle)
app.router.add_route('POST', '/shirish', shirish)
aiohttp_jinja2.setup(app,
    loader=aiohttp_jinja2.jinja2.FileSystemLoader('./'))

web.run_app(app)