from CB_service import create_app

app = create_app()

if __name__ == '__main__':
	app.app_context().push()
	app.run(debug=True, host='0.0.0.0', port=7000)