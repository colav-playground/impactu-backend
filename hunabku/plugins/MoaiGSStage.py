from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId


class MoaiGSStage(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/stage/submit', methods=['GET'])
    def stage_submit(self):
        """
        @api {get} /moai/gs/stage/submit Submit Paper
        @apiName  Moai Stage
        @apiGroup Moai GSStage
        @apiDescription Allows to submit papers to the collection stage in the given databse db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with paper data
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  GSLookUp paper inserted in stage
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            jdata = self.json.loads(data)
            jdata["_id"] = ObjectId(jdata["_id"])
            self.db['stage'].insert(jdata, check_keys=False)
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'GSLookUp Paper inserted in stage'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/stage/read', methods=['GET'])
    def stage_read(self):
        """
        @api {get} /moai/gs/stage/read Retrieve data from stage
        @apiName Moai Stage
        @apiGroup Moai GSStage
        @apiDescription Allow to retrieve data from stage, criteria to send if by chunks is not defined yet

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} ids  Paper ids to retrieve
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {Object}  json  all the registers from stage collection in a json dump

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            cursor = self.db['stage'].find()

            data = list(cursor)
            response = self.app.response_class(
                response=self.json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
