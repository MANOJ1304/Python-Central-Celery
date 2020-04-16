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
            data = self.__get_areas(**kwargs["creds"], **kwargs["data_params"])
            
            self.__draw_chart(data[0], data[3], data[1])
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

    def __draw_chart(self, map_data, data:dict = {}, area_coordinates: list = []):
        # print(json.dumps(map_data, indent=4))
        # print(json.dumps(data, indent=4))
        df = pd.DataFrame(data)
        def get_stats(data, field):
            count_stats = []
            link_stats = [] 
            ds = df.loc[df.groupby(field)['value'].idxmax()] 
            ds = ds.sort_values(by=["value"], ascending= False) 
            for r,i in ds.iterrows():  
                count_stats.append((i.source, i.value)) 
                link_stats.append((i.source,i.target)) 
            return   count_stats,  link_stats 

        source = get_stats(df, "source")
        target = get_stats(df, "target")
        map = StatsMap("makemymap")
        map.coordinates(area_coordinates)
        map.schema(map_data) 
        map.set_data(source[0][:5], "", type_= 'map', )
        map.set_data(source[1][:5], "", type_= 'geo',  color="#42597A")
        map.set_data(target[0][:5], "", type_= 'map', )
        map.set_data(target[1][:5], "", type_= 'geo',  color="#3090B5")
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