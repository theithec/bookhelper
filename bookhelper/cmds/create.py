import json
from . import Action

class CreateAction(Action):

    def validate(self):
        print("C", self.conf)
        jsrc = getattr(self.conf, "json_source", None)
        if not jsrc:
            self.errors.append("No json source")
            return

        try:
            self.bookdata = json.loads(jsrc)
            print(self.bookdata)
        except json.decoder.JSONDecodeError as e:
            self.errors.append(str(e))

    def run(self):
        pass
