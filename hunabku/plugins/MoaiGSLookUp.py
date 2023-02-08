from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId


class MoaiGSLookUp(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/lookup/data', methods=['GET'])
    def data_endpoint(self):
        """
        @api {get} /moai/gs/lookup/data Retrieve data by ids
        @apiName GSLookUp
        @apiGroup Moai GSLookUp
        @apiDescription Allow to download the registers from collection data for given ids

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} ids  Paper ids to retrieve
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {Object}  json  all the registers from data collection in a json dump

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        ids = self.json.loads(self.request.args.get('ids').replace("'", "\""))
        oids = [ObjectId(iid) for iid in ids]
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            cursor = self.db['data'].find({'_id': {'$in': oids}})
            data = []
            for i in cursor:
                data.append(i)
            print(data)
            response = self.app.response_class(
                response=self.json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/lookup/not_found', methods=['GET'])
    def not_found(self):
        """
        @api {get} /moai/gs/lookup/not_found GSLookUp not found
        @apiName GSLookUp
        @apiGroup Moai GSLookUp
        @apiDescription Allow to move the register from data when not found for gslookup to the collection gslookup_not_found

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} id  Paper id to move
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  Message

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """

        _id = self.request.args.get('_id')
        oid = ObjectId(_id)
        db = self.request.args.get('db')
        url = self.request.args.get('url')

        if self.valid_apikey():
            self.db = self.dbclient[db]
            cursor = self.db['data'].find({'_id': oid})
            data = []
            for i in cursor:
                data.append(i)
            data[0]['url'] = url
            self.db['gslookup_not_found'].insert(data)
            self.db['data'].delete_one({'_id': oid})
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'register {} moved from data to gslookup_not_data'.format(_id)}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/lookup/checkpoint', methods=['GET'])
    def stage_checkpoint(self):
        """
        @api {get} /moai/gs/lookup/checkpoint GSLookUp checkpoint
        @apiName GSLookUp
        @apiGroup Moai GSLookUp
        @apiDescription Allow to know the cuerrent status of the collection data for the given dataset in db
                        Return the ids of papers not dowloaded yet comparing the ids from data and stage collections using set.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {Bool}  checkpoint  if true then there are more ids to download
        @apiSuccess {String[]}  ids if true then there are more ids to download
        @apiSuccess {Bool}  error  if true then there is an error to handle the ids ex: not collection data to get ids
        @apiSuccess {String} msg Message with the explanation of the error in case error tag is true.

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        if self.valid_apikey():
            db = self.request.args.get('db')
            self.db = self.dbclient[db]
            ckeckpoint = True  # False if any error or all was dowloaded
            error = False
            msg = ""
            ckp_ids = []  # _id(s) for checkpoint

            # reading collection data
            try:
                data_ids = set([str(reg["_id"])
                                for reg in self.db['data'].find({}, {"_id": 1})])
            except BaseException:
                data_ids = []
            npapers = len(data_ids)
            if npapers == 0:
                error = True
                ckeckpoint = False
                msg = "No elements found in database " + db + ' collection data'
                response = self.app.response_class(
                    response=self.json.dumps(
                        {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            try:
                stage_ids = set([str(reg["_id"])
                                 for reg in self.db['stage'].find({}, {'_id': 1})])
            except BaseException:
                stage_ids = []

            try:
                quarantine_ids = set(
                    [str(reg["_id"]) for reg in self.db['quarantine'].find({}, {'_id': 1})])
            except BaseException:
                quarantine_ids = set([])

            try:
                invalid_ids = set(
                    [str(reg["_id"]) for reg in self.db['stage_invalid'].find({}, {'_id': 1})])
            except BaseException:
                invalid_ids = set([])

            if len(stage_ids) + \
                    len(quarantine_ids) == npapers:  # all the papers were downloaded
                ckeckpoint = False
                msg = "All papers already downloaded for database " + db + ' collection data'
                response = self.app.response_class(
                    response=self.json.dumps(
                        {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            if len(stage_ids) == 0 and len(quarantine_ids) == 0 and len(invalid_ids) == 0:
                ckp_ids = list(data_ids)
                msg = 'stage, stage_invalid and quarantine in database ' + db + ' is empty'
                response = self.app.response_class(
                    response=self.json.dumps(
                        {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            ckp_ids = list(data_ids - data_ids.intersection(stage_ids) - data_ids.intersection(quarantine_ids) - data_ids.intersection(invalid_ids))  # noqa: E501,E261
            msg = 'missing values for stage and quarantine with database ' + db + ' collection data'
            response = self.app.response_class(
                response=self.json.dumps(
                    {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            return self.apikey_error()

    @endpoint('/moai/gs/lookup/quarantine', methods=['GET'])
    def quarantine_submit(self):
        """
        @api {get} /moai/gs/lookup/quarantine Submit Paper in Quarantine collection
        @apiName  Moai GSLookUp
        @apiGroup Moai GSLookUp
        @apiDescription Allows to submit papers to the collection quarantine in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with paper data
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  GSLookUp paper inserted in quarantine
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            jdata = self.json.loads(data)
            jdata["_id"] = ObjectId(jdata["_id"])
            self.db['quarantine'].insert(jdata, check_keys=False)
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'GSLookUp Paper inserted in quarantine'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/lookup/stage_invalid', methods=['GET'])
    def invalid_submit(self):
        """
        @api {get} /moai/gs/lookup/invalid Submit Paper to Stage Invalid collection
        @apiName  Moai GSLookUp
        @apiGroup Moai GSLookUp
        @apiDescription Allows to submit papers to the collection invalid in the given database db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with paper data
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  GSLookUp paper inserted in invalid collection
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            jdata = self.json.loads(data)
            jdata["_id"] = ObjectId(jdata["_id"])
            self.db['stage_invalid'].insert(jdata, check_keys=False)
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'GSLookUp Paper inserted in stage invalid'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
