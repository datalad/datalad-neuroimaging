from os.path import dirname
from os.path import join as opj




# create ds????
# import shit
# edit specs

class Pork(object):
    import cherrypy
    from cherrypy import tools

    _webapp_dir = dirname(__file__)
    _webapp_staticdir = 'static'
    _webapp_config = opj(_webapp_dir, 'app.conf')

    def __init__(self, dataset):
        from datalad.distribution.dataset import require_dataset

        # TODO: Doe we really require a dataset?
        # For create we need to be able to go with None
        self.ds = require_dataset(
            dataset, check_installed=True, purpose='serving')

    @cherrypy.expose
    def index(self):

        return """<html>
          <head></head>
          <body>
            <a href="edit">Edit</a>          
            <a href="import_dicoms">Import DICOMs</a>
            <a href="import_additional">Import additional data</a>
          </body>
        </html>"""

    @cherrypy.expose
    def edit(self, session=None):

        spec = self.get_study_spec(session)
        input_div = self.get_form_from_spec(spec)

        return """
        <html>
          <head>
            <link href="/style.css" rel="stylesheet">
            <script src="/scripts.js"></script>
          </head>
          <body>
            {inputs}
            <button id=\"submit_spec\" onclick=\"submit_spec('{session}')\">Save</button>
          </body>
        </html>""".format(inputs=input_div, session=session)

    @staticmethod
    def get_form_from_spec(spec):

        spec_form = "<div id=\"spec_form\">\n"
        for spec_dict in spec:
            spec_form += "<div class=\"spec_section\">\n"
            for k in spec_dict.keys():
                label = k
                if isinstance(spec_dict[k], dict):
                    value = spec_dict[k]['value']
                    approved = spec_dict[k]['approved']
                else:
                    value = spec_dict[k]
                    approved = None

                if approved is not None:
                    box = "<input type=\"checkbox\" name=\"approved\" {}>\n" \
                          "".format("checked" if approved else "")
                else:
                    box = ""
                spec_form += "<div class=\"key\">{key}: <input type=\"text\" name=\"{key}\" " \
                             "value=\"{val}\"> {box}<br></div>\n".format(
                                key=label,
                                val=value,
                                box=box)
            spec_form += "</div>\n"
        spec_form += "</div>\n"
        return spec_form

    def get_study_spec(self, session=None):
        import os.path
        import json
        # TODO: Do we want to read uncommitted things here? Or use
        #       self.ds.repo.get_file_content() instead?

        if not session:
            # join study spec snippets:
            spec_files = [opj(self.ds.path, 'studyspec.json')]
            spec_files.extend([opj(self.ds.path, d, 'studyspec.json')
                               for d in os.listdir(self.ds.path)
                               if os.path.isdir(d) and not d.startswith('.')])
        else:
            # single session only
            spec_files = [opj(self.ds.path, session, 'studyspec.json')]

        spec = []
        for f in spec_files:
            if os.path.exists(f):
                spec.extend(json.load(open(f, 'r')))

        return spec

    @cherrypy.expose
    @tools.json_in()
    def save(self, ses):

        # TODO: session and actual save!
        import cherrypy
        import json
        input_json = cherrypy.request.json
        json.dump(input_json, open("TestDump.json", "w"))

        import pdb;pdb.set_trace()
        print(ses)
        return "/index"

    def import_dicoms(self):

        raise NotImplemented

    def import_additional(self):

        raise NotImplemented
