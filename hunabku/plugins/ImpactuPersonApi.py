from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId
from pymongo import ASCENDING,DESCENDING

class ImpactuPersonApi(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    def get_production(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort=None,direction=None):
        total = 0
        papers=[]
        if start_year:
            try:
                start_year=int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year=int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        search_dict={}

        if idx:
            search_dict["authors.id"]=ObjectId(idx)
                
        if start_year or end_year:
            search_dict["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year
        
        cursor=self.colav_db["works"].find(search_dict)
        total=self.colav_db["works"].count_documents(search_dict)

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
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count.count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count.count",DESCENDING)])
        if sort=="year" and direction=="ascending":
            cursor.sort([("year_published",ASCENDING)])
        if sort=="year" and direction=="descending":
            cursor.sort([("year_published",DESCENDING)])

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            for paper in cursor:
                entry=paper.copy()
                subjects=[]
                for subject in entry["subjects"]:
                    sub_entry=subject.copy()
                    sub_entry["subjects"]=[]
                    for sub in subject["subjects"]:
                        name=None
                        lang=None
                        for n in sub["names"]:
                            if n["lang"]=="es":
                                name=n["name"]
                                lang=n["lang"]
                                break
                            elif n["lang"]=="en":
                                name=n["name"]
                                lang=n["lang"]
                        
                        sub["names"]=[{"name":name,"lang":lang}]
                        sub_entry["subjects"].append(sub)
                    subjects.append(sub_entry)
                source=self.colav_db["sources"].find_one({"_id":paper["source"]["id"]})
                if source:
                    entry["source"]={
                        "id":source["_id"],
                        "names":source["names"],
                        "ranking":source["ranking"],
                        "apc":source["apc"]
                    }
                authors=[]
                for author in paper["authors"]:
                    au_entry=author
                    if not "affiliations" in au_entry.keys():
                        au_entry["affiliations"]=[]
                    author_db=None
                    if "id" in author.keys():
                        author_db=self.colav_db["person"].find_one({"_id":author["id"]})
                    if author_db:
                        au_entry=author_db
                    affiliations=[]
                    for aff in author["affiliations"]:
                        if not "names" in aff.keys():
                            if "id" in author.keys():
                                print("Author {} has no names in aff".format(author["id"]))
                            continue
                        name=""
                        lang=""
                        for n in aff["names"]:
                            if n["lang"]=="es":
                                name=n["name"]
                                lang=n["lang"]
                                break
                            elif n["lang"]=="en":
                                name=n["name"]
                                lang=n["lang"]
                        del(aff["names"])
                        aff["names"]=[{"name":name,"lang":lang}]
                        affiliations.append(aff)
                    au_entry["affiliations"]=affiliations
                    authors.append(au_entry)
                entry["authors"]=authors
                papers.append(entry)

            return {"data":papers,
                    "count":len(papers),
                    "page":page,
                    "total_results":total
                }
        else:
            return None
    
    def get_info(self,idx):
        author = self.colav_db['person'].find_one({"_id":ObjectId(idx)})
        if author:
            entry=author.copy()
            del(entry["_id"])
            entry["affiliations"]=[]
            for aff in author["affiliations"]:
                if not "names" in aff.keys():
                    print("Author {} has no names in aff".format(author["_id"]))
                    continue
                name=""
                lang=""
                for n in aff["names"]:
                    if n["lang"]=="es":
                        name=n["name"]
                        lang=n["lang"]
                        break
                    elif n["lang"]=="en":
                        name=n["name"]
                        lang=n["lang"]
                del(aff["names"])
                aff["names"]=[{"name":name,"lang":lang}]
                entry["affiliations"].append(aff)

            return entry
        else:
            return None

    @endpoint('/api/person', methods=['GET'])
    def api_person(self):
        data = self.request.args.get('data')
    
        if not self.valid_apikey():
            return self.apikey_error()

        if data=="info":
            idx = self.request.args.get('id')
            result = self.get_info(idx)
        elif data=="production":
            idx = self.request.args.get('id')
            max_results=self.request.args.get('max')
            page=self.request.args.get('page')
            start_year=self.request.args.get('start_year')
            end_year=self.request.args.get('end_year')
            sort=self.request.args.get('sort')
            result=self.get_production(
                idx=idx,
                max_results=max_results,
                page=page,
                start_year=start_year,
                end_year=end_year,
                sort=sort,
                direction="ascending"
            )
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