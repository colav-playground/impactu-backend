from hunabku.HunabkuBase import HunabkuPluginBase, endpoint


class MoaiGSProfile(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/profile/checkpoint', methods=['GET'])
    def profile_checkpoint(self):
        """
        @api {get} /moai/gs/profile/checkpoint GSProfile checkpoint
        @apiName GSProfile
        @apiGroup Moai GSProfile
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
            stage = self.db['stage']
            stage_cites  = self.db['stage_cites']
            profiles = self.db['profiles']
            profiles_private = self.db['profiles_private']
            ckeckpoint = True  # False if any error or all was dowloaded
            error = False
            msg = ""
            ckp_ids = []  # _id(s) for checkpoint

            # reading collection data
            try:
                profiles_s = stage.find({'profiles':{'$ne':{}}},{'_id':0,'profiles':1})
                profiles_c = stage_cites.find({'cite.profiles':{'$ne':{}}},{'_id':0,'cite.profiles':1})
                profiles_cites = list(profiles_c)
                profiles_stage = list(profiles_s)
                for i in range(len(profiles_cites)):
                    profiles_stage.append(profiles_cites[i]["cite"])

                profiles_p = profiles.find({}, {'_id': 1})
                profiles_pv = profiles_private.find({}, {'_id': 1})

                profiles_stage_ids = []
                for profile in profiles_stage:
                    for user in profile['profiles']:
                        profiles_stage_ids.append(profile['profiles'][user])

                profiles_stage_ids = set(profiles_stage_ids)
                profiles_collection = list(profiles_p) + list(profiles_pv)
                profiles_ids = []
                for profile in profiles_collection:
                    profiles_ids.append(profile['_id'])
                profiles_ids = set(profiles_ids)
                ckp_ids = list(profiles_stage_ids - profiles_ids)

            except BaseException:
                ckp_ids = []

            msg = 'ids for profiles in database ' + db + \
                ' collection stage still not downloaded'
            response = self.app.response_class(
                response=self.json.dumps(
                    {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            return self.apikey_error()

    @endpoint('/moai/gs/profile/submit', methods=['GET'])
    def profile_submit(self):
        """
        @api {get} /moai/gs/profile/submit Submit profile
        @apiName  Moai profile
        @apiGroup Moai GSProfile
        @apiDescription Allows to submit papers to the collection profile in the given databse db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with paper data
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  GSProifle profile inserted
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            data = self.json.loads(data)
            self.db['profiles'].insert(data)
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'GSProfile user inserted in profile'}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/profile/not_found', methods=['GET'])
    def profile_not_found(self):
        """
        @api {get} /moai/gs/profile/not_found GSProfile not found
        @apiName GSProfile
        @apiGroup Moai GSProfile
        @apiDescription Allow to register profiles not found

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} id  Paper id to move
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  Message

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """

        _id = self.request.args.get('_id')
        db = self.request.args.get('db')
        url = self.request.args.get('url')

        if self.valid_apikey():
            self.db = self.dbclient[db]
            self.db['profiles_not_found'].insert({'_id': _id, 'url': url})
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'register {} moved from data to gsprofile_not_data'.format(_id)}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/profile/private', methods=['GET'])
    def profile_private(self):
        """
        @api {get} /moai/gs/profile/private GSProfile private
        @apiName GSProfile
        @apiGroup Moai GSProfile
        @apiDescription Allows to register private profiles

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} id  Paper id to move
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String}  msg  Message

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """

        _id = self.request.args.get('_id')
        db = self.request.args.get('db')
        url = self.request.args.get('url')

        if self.valid_apikey():
            self.db = self.dbclient[db]
            self.db['profiles_private'].insert({'_id': _id, 'url': url})
            response = self.app.response_class(
                response=self.json.dumps(
                    {'msg': 'register {} moved from data to gsprofile_not_data'.format(_id)}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            return self.apikey_error()
