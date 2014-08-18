from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from django.db import models
from django.db.models import Model
from django.core import serializers
import importlib


def _get_data(obj):
    """
    fetch all the data of the object.
    follow the sets etc.
    """
    if not isinstance(obj, models.Model):
        raise Exception('Not a model')

    ans = [obj]
    meta = obj.__class__._meta
    fields = meta.fields
    for field in fields:
        try:
            item = getattr(obj, field.name)
        except:
            pass
        if item and isinstance(field, models.ForeignKey):
            ans.append(item)

    sets_to_fetch = [s for s in dir(obj) if s.endswith("_set")]
    for set_to_fetch in sets_to_fetch:
        set_objs = getattr(obj, set_to_fetch).all()
        for set_obj in set_objs:
            ans += _get_data(set_obj)

    return ans


def generate_data(obj):
    ans = []
    if not isinstance(obj, Model):
        raise Exception('No a model to follow')
    else:
        ans += _get_data(obj)

    return ans


class Command(BaseCommand):
    args = '<app>.<Model> <id_object>'
    help = """
           Generate fixtures
           for a given object, generate json fixtures to rediret
           to a file in order to have full hierarchy of models
           from this parent object.

           syntax example:
               python manage.py generate_fixtures 'core.models.Client' 364 > ./core/fixtures/test_fixtures.json
           """

    def handle(self, *args, **options):
        if len(args) == 2:
            app_model = args[0]
            pk = args[1]
            self.stderr.write("this is app_model: {}\n".format(app_model))
            module_name = '.'.join(app_model.split('.')[0:-1])
            model_name = app_model.split('.')[-1]
            module = importlib.import_module(module_name)
            if module:
                model = getattr(module, model_name)
                parent_obj = model.objects.get(pk=pk)

                if not parent_obj:
                    raise CommandError("didnt find the object with the pk {}".format(pk))

                data = generate_data(parent_obj)

                self.stdout.write(
                    serializers.serialize("json", data, indent=4)
                )
                self.stderr.write("done\n\n")
            else:
                raise CommandError("no module named {}".format(module_name))
        else:
            raise CommandError("Wrong syntax. <app>")
