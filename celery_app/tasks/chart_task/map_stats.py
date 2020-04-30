from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap, CustomMap, StatsMap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import dpath
import copy


log = logging.getLogger(__name__)


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}
class PlotMapAndStats(BaseChartTask):
    name = 'Map Statistics'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(PlotMapAndStats, self).__init__()
        self.map_image = "scatterplot"
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()
        if not self.dev:    
            data = self.__get_areas(**kwargs["creds"], **kwargs["data_params"])
            venue_data = self.__process_venue_data(kwargs["creds"]["username"], kwargs["creds"]["password"], kwargs["data_params"]["venue_id"], kwargs["data_params"]["cfg"] )
            map_info = venue_data.get("building")[0].get("floor")[0].get("map_info")
            map_bounding = {"width": map_info.get("dim_x")*2, "height": map_info.get("dim_y")*2 }
            
            self.__draw_chart(data[0], data[3], data[1], bounding=map_bounding)
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
        # [print(item[1]) for item in research(d["_items"], query=lambda p, k, v: k == 'name' )]
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
        adata = [[list(v.keys())[:1][0], v.get("value")] for v in analytics.get("analytic_data")[0].get("series")]
        print("Analytics", adata)
        return self.__reproces(list(zip(area_polygons, building_ids, floor_ids, zone_ids, area_ids, names, centroids )), map_data_object, adata)

    def __reproces(self, data, obj, analytics_data):
        # area_polygon = []
        area_polygon = []
        centroid_p = {}
        area_name = {}
        
        for item in data:
            #  print(item)
             cent = {item[5]: item[6]}
             anames = {item[5]: item[5]}
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
            if i[0] in list(area_name.keys()):
                ddd.append([area_name[i[0]], i[1]])
        return { "type": 'FeatureCollection', "features": area_polygon}, centroid_p, area_name, ddd

    def __draw_chart(self, map_data, data:dict = {}, area_coordinates: list = [], bounding:dict = {}):
        # print(json.dumps(map_data, indent=4))
        # print(json.dumps(data, indent=4))
        map = StatsMap("makemymap", bounding=bounding)
        map.coordinates(area_coordinates)
        map.schema(map_data) 
        map.set_data(data,"Entrance Count")
        map.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image))   

    def __process_analytics(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list):
        log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        # d = (w.venues()
        # .analytics(venue_id=venue_id)
        # .area_heatmap()
        # .set_filter(date_range, agg_type, elasttic_filters, exclude_params)
        # .request())
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .store_count()
        .set_filter(date_range, agg_type, elasttic_filters, exclude_params)
        .request())
        print("Stats" , d)
        return d

    def __process_analytics_journey(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list, pre_compute: bool =True, pre_compute_filter: dict = {"type": "sorted_cross_shopping"}):
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
            .set_filter(date_range, "", elasttic_filters, exclude_params, pre_compute=True, pre_compute_filter={"type": "cross_shopping"})
            .request())
        
        return d

    def __process_data(self, data:dict):
        return data

    def __process_venue_data(self, username, password, venue_id:str,  cfg:dict) :
        w =  WildfireApi(username, password, cfg)
        data = (w.venues() 
        .get_one(venue_id))

        return data