from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap, CustomMap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import dpath
import copy
import pathlib

log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}
class MapVisual(BaseChartTask):
    name = 'Map Visual'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(MapVisual, self).__init__()
        # self.map_image = "area_heatmap"
        self.map_image = "area_heatmap_"
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])

        self.report_details = kwargs["report"]
        self.build_dir()
        # self.map_image =  self.map_image + self.report_details["stats_type"]

        if not self.dev:    

            venue_data = self.__process_venue_data(kwargs["creds"]["username"], kwargs["creds"]["password"], kwargs["data_params"]["venue_id"], kwargs["data_params"]["cfg"] )
            map_info = venue_data.get("building")[0].get("floor")[0].get("map_info")
            map_bounding = {"width": map_info.get("dim_x")*2, "height": map_info.get("dim_y")*2 }

            data = self.__get_areas(**kwargs["creds"], **kwargs["data_params"])
            
            self.__draw_chart(data[0], map_bounding, data[3])
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(kwargs['config']['base_url'],
                self.report_path_image, self.map_image + self.report_details["stats_type"])

        return kwargs['output']

        # bar.generate(file_name="visualization/html/render.html", image_name="visualization/[xzX]/images/example.png")


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
        names           = [item[1][0].get("text") for item in research(d["_items"], query=lambda p, k, v: k == 'name' ) if isinstance(item[1], list)]
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
        analytics = self.__process_analytics(username, password, cfg, venue_id, elasttic_filters, date_range, agg_type, exclude_params)
        
        adata = [[k, v.get(self.report_details["stats_type"]).get("value")]for k,v in analytics.get("analytic_data")[0].get("aggregation_data").items()]
        print("Stats", json.dumps(adata))
        return self.__reproces(list(zip(area_polygons, building_ids, floor_ids, zone_ids, area_ids, names, centroids )), map_data_object, adata)

    def __reproces(self, data, obj, analytics_data):
        # area_polygon = []
        area_polygon = []
        centroid_p = {}
        area_name = {}
        
        for item in data:
            #  print(item)
             cent = {item[4]: item[5]}
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
            if i[0] in list(area_name.keys()):
                ddd.append([area_name[i[0]], i[1]])
        print("Areas",json.dumps(area_name))
        return { "type": 'FeatureCollection', "features": area_polygon}, centroid_p, area_name, ddd

    def __draw_chart(self, map_data, bounding, data:dict = {}, ):
        # print(json.dumps(map_data, indent=4))
        


        map = CustomMap("makemymap", self.report_details["stats_type"], )
        map.schema(map_data)
        map.set_add_global_options(bounding) 
        map.set_data(data)
        # print(map.get_chart_instance().dump_options())

        map.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image + self.report_details["stats_type"]),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image + self.report_details["stats_type"]))   


    def __process_analytics(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list):
        log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .area_heatmap()
        .set_filter(date_range, agg_type, elasttic_filters, exclude_params)
        .request())
        
        return d

    def __process_venue_data(self, username, password, venue_id:str,  cfg:dict) :
        w =  WildfireApi(username, password, cfg)
        data = (w.venues() 
        .get_one(venue_id))

        return data