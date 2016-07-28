from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from django.db import models
from django.db.models import Model
from django.core import serializers
import importlib


seen = []


def _get_data(obj):
    """
    fetch all the data of the object.
    follow the sets etc.
    """
    if not isinstance(obj, models.Model):
        raise Exception('Not a model')

    ans = []
    uid = repr(obj)
    if uid in seen:
        return ans
    seen.append(uid)

    # adding the reverse set
    for d in [d for d in dir(obj) if not d.startswith('_')]:
        try:
            attribut = getattr(obj, d)
        except:
            pass

        fields = [field.name for field in obj.__class__._meta.fields]
        fields += [field.name for field in obj.__class__._meta.many_to_many]
        if d in fields and isinstance(attribut, models.Manager):
            set_objs = attribut.all()
            for set_obj in set_objs:
                ans += _get_data(set_obj)

        if isinstance(attribut, models.Model):
            ans += _get_data(attribut)

    ans.append(obj)

    return ans


def generate_data(obj):
    ans = []
    if not isinstance(obj, Model):
        raise Exception('No a model to follow')
    else:
        ans += _get_data(obj)

    return ans


class Command(BaseCommand):
    args = '<app>.<Model> <id_object> [<max_depth>]'
    help = """
           Generate fixtures
           for a given object, generate json fixtures to rediret
           to a file in order to have full hierarchy of models
           from this parent object.

           syntax example:
               python manage.py generate_fixtures 'core.models.Client' 364
           """

    def handle(self, *args, **options):
        if len(args) == 2:
            app_model = args[0]
            pk = args[1]
            module_name = '.'.join(app_model.split('.')[0:-1])
            model_name = app_model.split('.')[-1]
            module = importlib.import_module(module_name)
            if module:
                model = getattr(module, model_name)
                try:
                    parent_obj = model.objects.get(pk=pk)
                    self.stderr.write(
                        "fetched the parent obj {}\n".format(parent_obj))
                except:
                    raise CommandError(
                        "didnt find the object with the pk {}".format(pk))

                data = generate_data(parent_obj)

                self.stdout.write(
                    serializers.serialize("json", data, indent=4)
                )
                self.stderr.write("done\n\n")
            else:
                raise CommandError("no module named {}".format(module_name))
        else:
            raise CommandError("Wrong syntax. <app>")
