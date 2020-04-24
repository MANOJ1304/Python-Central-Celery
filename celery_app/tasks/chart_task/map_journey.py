from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap, CustomMap, StatsMap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import pandas as pd 
import logging
import json
import dateparser
import dpath
import copy


log = logging.getLogger(__name__)


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}
class MapJourney(BaseChartTask):
    name = 'Map Journey'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(MapJourney, self).__init__()
        self.map_image = "journey"


        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()

        if not self.dev:
            venue_data = self.__process_venue_data(kwargs["creds"]["username"], kwargs["creds"]["password"], kwargs["data_params"]["venue_id"], kwargs["data_params"]["cfg"] )
            map_info = venue_data.get("building")[0].get("floor")[0].get("map_info")
            map_bounding = { "width": map_info.get("dim_x")*2, "height": map_info.get("dim_y")*2 }

            data = self.__get_areas(**kwargs["creds"], **kwargs["data_params"])
            
            self.__draw_chart(data[0], data[3], data[1], map_bounding)
        
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(kwargs['config']['base_url'], self.report_path_image, self.map_image) 
        return kwargs['output']

        # bar.generate(file_name="visualization/html/render.html", image_name="visualization/images/example.png")


    def __get_areas(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, exclude_params:list, agg_type:str):
        log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        d = (w.venues() 
            .get(venue_id) 
            .pois() 
            .lists(search={"type": "area"}, pagination=True))

        # print(json.dumps(d))
        area_polygons   = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'polygon' )]
        building_ids    = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'building_id' )]
        floor_ids       = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'floor_id' )]
        zone_ids        = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'zone_id' )]
        area_ids        = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'area_id' )]
        names           = [item[1][0]["text"] for item in research(d["_items"], query=lambda p, k, v: k == 'name' ) if isinstance(item[1], list)]
        centroids       = [item[1] for item in research(d["_items"], query=lambda p, k, v: k == 'centroide' )]

        map_data_object = {
            "geometry": {

            }, 
            "properties":{
                "text":         {},
                "name":         {},
                "floor_id":     {},
                "building_id":  {},
                "zone_id":      {},
                "area_id":      {}
            }
        }

        # print(self.__reproces(list(zip(area_polygons, building_ids, floor_ids, zone_ids, area_ids, names, centroids )), map_data_object))
        
        # journey = self.__process_analytics_journey(username, password, cfg, venue_id, elasttic_filters, date_range, agg_type, exclude_params)
        # print(json.dumps(journey, indent=4))
        analytics = self.__process_analytics(username, password, cfg, venue_id, elasttic_filters, date_range, agg_type, exclude_params)
        adata = analytics.get("analytic_data")[0].get("aggregation_data").get("links")
        # print("Analytics", adata)
        return self.__reproces(list(zip(area_polygons, building_ids, floor_ids, zone_ids, area_ids, names, centroids )), map_data_object, adata)

    def __reproces(self, data, obj, analytics_data):
        # area_polygon = []
        area_polygon = []
        centroid_p = {}
        area_name = {}
        
        for item in data:
            #  print(item)
             cent = {item[5]: item[6]}
             anames = {item[4]: item[5]}
             dpath.util.set(obj, "geometry", item[0])
             dpath.util.set(obj, "properties/building_id", item[1])
             dpath.util.set(obj, "properties/floor_id", item[2])
             dpath.util.set(obj, "properties/zone_id", item[3])
             dpath.util.set(obj, "properties/area_id", item[5])
             dpath.util.set(obj, "properties/text", item[5])
             dpath.util.set(obj, "properties/name", item[5])
             o = copy.deepcopy(obj)
             area_polygon.append(dict(o))
            #  print()
             centroid_p.update(copy.deepcopy(cent))
             area_name.update(copy.deepcopy(anames))
        # print(json.dumps(area_name))
        ddd = []
        for i in analytics_data:
            if i.get('source') in list(area_name.keys()):
                i.update({'source': area_name[i.get('source')], 'target': area_name[i.get('target')]})
                ddd.append(i)
        return { "type": 'FeatureCollection', "features": area_polygon}, centroid_p, area_name, ddd

    def __draw_chart(self, map_data, data:dict = {}, area_coordinates: list = [], bounding:dict={}):
        # print(json.dumps(map_data, indent=4))
        # print(json.dumps(data, indent=4))
        df = pd.DataFrame(data)
        def get_stats(data, field, journey_type="origins"):
            count_stats = []
            link_stats = [] 
            ds = df.loc[df.groupby(field)['value'].idxmax()] 
            ds = ds.sort_values(by=["value"], ascending= False) 
            for r,i in ds.iterrows():  
                # count_stats.append((i.source, "")) 
                if journey_type == "origins":
                    count_stats.append((i.target, i.value))
                    count_stats.append((i.source, ""))  
                    link_stats.append((i.source,i.target)) 
                    
                else:
                    count_stats.append((i.source, i.value)) 
                    count_stats.append((i.target, "")) 
                    link_stats.append((i.target,i.source)) 
                    
            return   count_stats,  link_stats 

        source = self.find_top_places(df, "source")
        target = self.find_top_places(df, "target")
        # print(source[0])
        print(target[0])
        map = StatsMap("makemymap")
        map.coordinates(area_coordinates)
        map.schema(map_data) 
        map.set_add_global_options(bounding) 
        map.set_data(source[0][:10], "", type_= 'map',   color="#0197F6")
        map.set_data(source[1][:5], "Top 5 Origins", type_= 'geo',  color="#0197F6")
        map.set_data(target[0][:10], "", type_= 'map', color="#271033")
        map.set_data(target[1][:5], "Top 5 Destinations", type_= 'geo',  color="#271033")
        # print(map.get_chart_instance().dump_options())
        map.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image))   


    def __process_analytics(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list, pre_compute: bool =True, pre_compute_filter: dict = {"type": "cross_shopping"}):
        log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        # d = (w.venues()
        # .analytics(venue_id=venue_id)
        # .area_heatmap()
        # .set_filter(date_range, agg_type, elasttic_filters, exclude_params)
        # .request())
        d = (w.venues()
            .analytics(venue_id=venue_id)
            .map_journey()
            .set_filter(date_range, "", elasttic_filters, exclude_params, pre_compute, pre_compute_filter)
            .request())
        
        return d

    def __process_data(self, data:dict):
        return data
    
    def find_top_places(self, df, palce_type):
        def toptrafficplace(data, type_):
            def appl(x):
                # print("adas",x)
                f = {
                    "count": x.count()
                }
                return pd.DataFrame(f)
        
            # ds = df.loc[df.groupby("target")['value'].idxmax()] 
            dg = df[[type_]].groupby(type_).apply(appl)
            dg = dg.reindex().sort_values(["count"], ascending= False)
            areas = []
            for  r,i in dg.head(5).iterrows(): 
                # print(r)
                areas.append(r[0])

            return areas

        # dg = df.loc[df['count'].idxmax()] 
        # dg = dg.reindex().sort_values(["count"], ascending= False)
        # dg.loc[dg.groupby("source")['value'].idxmax()] 
        # ds = ds.sort_values(by=["value"], ascending= False) 
        # ['72de0ac8c9774e8bb1bbe02829c34a79', 'f18e4a48df214700a1aad8704955bc78', 'bc671d58a9754b5093e050d0709a957c', '9586546f3386460c947b87d3a9abfb56', '3692a6ea35914ec6bef270701b9c4c9c']
        # ['fb286aae96414d09a2fa55823e3b2b98', '534c21da29bd49d583919d58f476a027', 'd1181384dbba4004abcfc1bcfab958aa', 'bc671d58a9754b5093e050d0709a957c', '291922e7bade4ba9a3eb59e3c403f483']

        # print(toptrafficplace(df, palce_type))
        palces = toptrafficplace(df, palce_type)
        # print(palces)
        # origins = toptrafficplace(df, "source")
        # dss =  df[df[palce_type].isin(palces)]
        frames = []
        for i in palces:
            dss = df[df[palce_type].isin([i])]
            final_data = dss.loc[dss.groupby(palce_type)['value'].idxmax()].sort_values(["value"], ascending=False)[["source", "target", "value"]].head(1)
            frames.append(final_data)
        # print(dss)
        count_stats = []
        link_stats = []
        for r, i in pd.concat(frames).iterrows():
            count_stats.append((i[palce_type], i.value)) 
            if palce_type == "source":
                count_stats.append((i.target, "")) 
            elif palce_type == "target":
                count_stats.append((i.source, "")) 
            link_stats.append((i.source,i.target)) 
        return count_stats, link_stats


    def __process_venue_data(self, username, password, venue_id:str,  cfg:dict) :
        w =  WildfireApi(username, password, cfg)
        data = (w.venues() 
        .get_one(venue_id))

        return data