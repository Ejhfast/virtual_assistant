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
	
	display_data = {'user_input': user_input}

	# if direct match, execute the query
	is_match, vals = assistant.execute(user_input)
	if is_match:
		display_data.update({'is_match': is_match, 'vals': vals})
		return {'display_data': display_data}
	
	is_confident, cmds = assistant.predict(user_input)
	display_data.update({'is_confident': is_confident, 'cmds': cmds})

	if is_confident:
		cmd = cmds[0]

		# extract required parameters to ask user to specify
		args = assistant.mappings[cmd]['args']

		display_data.update({'cmd': cmd, 'args': args})
		return {'display_data': display_data}
	return {'display_data': display_data}

async def event_trigger(request):
	data = await request.json()
	print(data)
	return web.Response()

app = web.Application()
app.router.add_static('/js', 'js/')
app.router.add_static('/css', 'css/')
app.router.add_static('/fonts', 'fonts/')
app.router.add_route('GET', '/', handle)
app.router.add_route('POST', '/user_input', user_input)
app.router.add_route('POST', '/event_trigger', event_trigger)
aiohttp_jinja2.setup(app,
    loader=aiohttp_jinja2.jinja2.FileSystemLoader('./'))

web.run_app(app)