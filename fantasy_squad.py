import os
import click
from flask_migrate import Migrate, upgrade, MigrateCommand 
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, GameDetails

app = create_app(os.getenv('FLASK_CONFIG') or 'default') 
manager=Manager(app)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role) 

manager.add_command("shell",Shell(make_context=make_shell_context)) 
manager.add_command('db', MigrateCommand)


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

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision  
    print ('i have been deployed')
    upgrade()

    # create or update user roles
    #Role.insert_roles()

    # ensure all users are following themselves
    #User.add_self_follows()

#if __name__=="__main__": 
#    app.run()
