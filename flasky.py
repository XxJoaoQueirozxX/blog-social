import os
import click

from flask_migrate import Migrate
from dotenv import load_dotenv

from app import create_app, db
from app.models import User, Role, Permission


load_dotenv()

app = create_app(os.getenv("FLASK_CONFIG") or 'default')
migrate = Migrate(app, db)


@app.before_first_request
def gerar_banco():
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
