from aiohttp import web
import aiohttp_jinja2
from core import Assistant
import demo_commands

@aiohttp_jinja2.template('index.html')
async def handle(request):
    return {}

@aiohttp_jinja2.template('feedback.html')
async def user_input(request):
	data = await request.post()
	user_input = data['user_input']
	
	# register commands
	assistant = demo_commands.commands(Assistant())
	
	# if direct match, execute the query
	is_match, vals = assistant.execute(user_input)
	if is_match:
		return {'user_input': user_input, 'is_match': is_match, 'vals': vals}
	
	is_confident, cmds = assistant.predict(user_input)
	if is_confident:
		cmd = cmds[0]

		# extract required parameters to ask user to specify
		args = assistant.mappings[cmd]['args']

		return {'user_input': user_input, 'is_confident': is_confident, 'cmds': cmds, 'cmd': cmd, 'args': args}
	return {'user_input': user_input, 'is_confident': is_confident, 'cmds': cmds}

async def event_trigger(request):
	data = await request.json()
	print(data)
	return web.Response()

app = web.Application()
app.router.add_route('GET', '/', handle)
app.router.add_route('POST', '/user_input', user_input)
app.router.add_route('POST', '/event_trigger', event_trigger)
aiohttp_jinja2.setup(app,
    loader=aiohttp_jinja2.jinja2.FileSystemLoader('./'))

web.run_app(app)