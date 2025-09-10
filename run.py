from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Use gunicorn in production (e.g., Render), Flask debug server locally
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('RENDER', 'False') == 'True':
        from gunicorn.app.base import Application

        class StandaloneApplication(Application):
            def init(self, parser, opts, args):
                return {
                    'wsgi': app,
                    'bind': f'0.0.0.0:{port}',
                    'workers': 1,
                }

            def load(self):
                return app

        StandaloneApplication().run()
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
