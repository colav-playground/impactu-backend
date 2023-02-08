from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from flask import (
    render_template,
)


class ApiDoc(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/apidoc', methods=['GET'])
    def index(self):
        return render_template('apidoc.html', apidoc_link='/apidoc/index.html')

    @endpoint('/apidoc/', methods=['GET'])
    def index_slash(self):
        return render_template('apidoc.html', apidoc_link='/apidoc/index.html')

    @endpoint('/apidoc/update', methods=['GET'])
    def update(self):
        """
        @api {get} /apidoc/update Update ApiDoc Documentation
        @apiName ApiDoc
        @apiGroup ApiDoc
        """
        if self.valid_apikey():
            self.hunabku.generate_doc()
            response = self.app.response_class(
                response=self.json.dumps({'status': 'apidoc updated'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
