from hunabku.HunabkuBase import HunabkuPluginBase, endpoint


class MoaiGSCites(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/cites/cache/checkpoint', methods=['GET'])
    def checkpoint_cites_endpoint(self):
        """
        @api {get} /moai/gs/cites/cache/checkpoint GSCites checkpoint
        @apiName GSCites
        @apiGroup Moai GSCites
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
            cursor = self.db['cache_cites'].find({'downloaded': 0, 'empty': 0})
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

    @endpoint('/moai/gs/cites/cache/ids', methods=['GET'])
    def cites_cache_ids(self):  # this is the checkpoint for cache not for cites itself
        """
        @api {get} /moai/gs/cites/cache/ids Retrieve cache ids
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allow to download the register ids from collection cache_cites

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} ids  Paper ids to retrieve
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {Object}  json  all the register ids from cache_cites collection in a json dump

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            cursor = self.db['cache_cites'].find({}, {'_id': 1})
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

    @endpoint('/moai/gs/cites/cache/update', methods=['GET'])
    def cites_cache_update(self):
        """
        @api {get} /moai/gs/cites/cache/update Update GSCites cache
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allow to updated cites cache and check if it was downloaded or if it and empty page

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} _id  Cite id to update
        @apiParam {String} empty  Status, to check if the page is empty
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        _id = self.request.args.get('_id')  # object id
        empty = self.request.args.get('empty')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            self.db['cache_cites'].update_one({'_id': self.json.loads(_id)}, {
                                              "$set": {'downloaded': 1, 'empty': empty}})
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/cites/submit', methods=['GET'])
    def stage_cites_submit(self):
        """
        @api {get} /moai/gs/cites/submit Submit Cite
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allows to submit cites to the collection stage_cites in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with cite data
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            self.db['stage_cites'].insert(self.json.loads(data),check_keys=False)
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/cites/cache/submit', methods=['GET'])
    def cites_cache_submit(self):
        """
        @api {get} /moai/gs/cites/cache/submit Submit cites cache
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allows to submit cites cache to the collection cache_cites in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with cite data
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            self.db['cache_cites'].insert(self.json.loads(data))
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/cites/invalid', methods=['GET'])
    def invalid_stage_cites_submit(self):
        """
        @api {get} /moai/gs/cites/invalid Submit Invalid Cite
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allows to submit invalid cites to the collection stage_cites_invalid in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with cite data
        @apiParam {String} apikey  Credential for authentication

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            self.db['stage_cites_invalid'].insert(self.json.loads(data))
            response = self.app.response_class(
                response=self.json.dumps({}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
