from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING

class ImpactuSearchApi(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    def search_person(self,keywords="",institutions="",groups="",country="",max_results=100,page=1,sort="citations"):
        search_dict={"external_ids":{"$ne":[]}}
        aff_list=[]
        if institutions:
            aff_list.extend([ObjectId(inst) for inst in institutions.split()])
        if groups:
            aff_list.extend([ObjectId(grp) for grp in groups.split()])
        if len(aff_list)!=0:
            search_dict["affiliations.id"]={"$in":aff_list}

        if keywords:
            search_dict["$text"]={"$search":keywords}
            filter_cursor=self.colav_db['person'].find({"$text":{"$search":keywords},"external_ids":{"$ne":[]}},{ "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" } )])
        else:
            filter_cursor=self.colav_db['person'].find({"external_ids":{"$ne":[]}})

        cursor=self.colav_db['person'].find(search_dict,{"score":{"$meta":"textScore"}})

        institution_filters = []
        group_filters=[]
        institution_ids=[]
        groups_ids=[]

        for author in filter_cursor:
            if "affiliations" in author.keys():
                if len(author["affiliations"])>0:
                    for aff in author["affiliations"]:
                        if "types" in aff.keys():
                            for typ in aff["types"]: 
                                if typ["type"]=="group":
                                    if not str(aff["id"]) in groups_ids:
                                        groups_ids.append(str(aff["id"]))
                                        group_filters.append({
                                            "id":str(aff["id"]),
                                            "name":aff["name"]
                                        })
                                else:
                                    if not str(aff["id"]) in institution_ids:
                                        institution_ids.append(str(aff["id"]))
                                        entry = {"id":str(aff["id"]),"name":aff["name"]}
                                        institution_filters.append(entry)


        
        cursor.sort([("score", { "$meta": "textScore" } )])


        total=cursor.count()
        if not page:
            page=1
        else:
            try:
                page=int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results=100
        else:
            try:
                max_results=int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            author_list=[]
            keywords=[]
            group_name = ""
            group_id = ""
            for author in cursor:
                entry={
                    "id":author["_id"],
                    "name":author["full_name"],
                    "affiliation":{"institution":{"name":"","id":""}}
                }
                if "affiliations" in author.keys():
                    if len(author["affiliations"])>0:
                        for aff in author["affiliations"]:
                            if "types" in aff.keys():
                                for typ in aff["types"]:
                                    if typ["type"]=="group":
                                        if groups:
                                            if aff["id"] in aff_list:
                                                entry["affiliation"]["group"]={
                                                    "name":aff["name"],
                                                    "id":aff["id"]
                                                }
                                        else:
                                            entry["affiliation"]["group"]={
                                                "name":aff["name"],
                                                "id":aff["id"]
                                            }
                                    else:
                                        if institutions:
                                            if aff["id"] in aff_list:
                                                entry["affiliation"]["institution"]["name"]=aff["name"]
                                                entry["affiliation"]["institution"]["id"]  =aff["id"]
                                        else:    
                                            entry["affiliation"]["institution"]["name"]=aff["name"]
                                            entry["affiliation"]["institution"]["id"]  =aff["id"]

                author_list.append(entry)
    
            return {
                    "total_results":total,
                    "count":len(author_list),
                    "page":page,
                    "filters":{"institutions":institution_filters,"groups":group_filters},
                    "data":author_list
                }
        else:
            return None

    @endpoint('/api/search', methods=['GET'])
    def api_search(self):
        data = self.request.args.get('data')
        if not self.valid_apikey():
            return self.apikey_error()

        if data=="person":
            max_results=self.request.args.get('max') if 'max' in self.request.args else 100
            page=self.request.args.get('page') if 'page' in self.request.args else 1
            keywords = self.request.args.get('keywords') if "keywords" in self.request.args else ""
            sort = self.request.args.get('sort') if "sort" in self.request.args else "citations"
            groups = self.request.args.get('groups') if "groups" in self.request.args else None
            institutions = self.request.args.get('institutions') if "institutions" in self.request.args else None
            result=self.search_author(keywords=keywords,max_results=max_results,page=page,sort=sort,
                groups=groups,institutions=institutions)
        else:
            result=None

        if result:
            response = self.app.response_class(
            response=self.json.dumps(result),
            status=200,
            mimetype='application/json'
            )
        else:
            response = self.app.response_class(
            response=self.json.dumps({}),
            status=204,
            mimetype='application/json'
            )
        
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response