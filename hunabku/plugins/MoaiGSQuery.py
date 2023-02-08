from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId


class MoaiGSQuery(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/query/cache/submit', methods=['GET'])
    def gsquery_cache_submit(self):
        """
        @api {get} /moai/gs/query/cache/submit Submit query cache
        @apiName GSQuery
        @apiGroup Moai GSQuery
        @apiDescription Allows to submit query cache to the collection cache_cites in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with cite data
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            self.db['cache_queries'].insert(self.json.loads(data))
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/query/cache/checkpoint', methods=['GET'])
    def gsquery_cache_read(self):
        """
        @api {get} /moai/gs/query/cache/checkpoint GSQuery cache checkpoint
        @apiName GSQuery
        @apiGroup Moai GSQuery
        @apiDescription Allow to know the cuerrent status of the collection cache_cites for the given db
                        Return the registers for cites not dowloaded yet.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String[]}  Resgisters from cache with urls to download.

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            cursor = self.db['cache_queries'].find(
                {'downloaded': 0, 'empty': 0})
            data = []
            for i in cursor:
                data.append(i)
            response = self.app.response_class(
                response=self.json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/query/cache/update', methods=['GET'])
    def gsquery_cache_update(self):
        """
        @api {get} /moai/gs/query/cache/update Update GSQuery cache
        @apiName GSQuery
        @apiGroup Moai GSQuery
        @apiDescription Allow to updated query cache and check if it was downloaded or if it and empty page

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} _id  Cite id to update
        @apiParam {String} empty  Status, to check if the page is empty
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        _id = self.request.args.get('_id')
        empty = self.request.args.get('empty')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            # self.db['cache_queries'].update_one({"_id":ObjectId(_id)},{"$set":self.json.loads(data)})
            self.db['cache_queries'].update_one({'_id': ObjectId(_id)}, {
                "$set": {'downloaded': 1, 'empty': empty}})
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
