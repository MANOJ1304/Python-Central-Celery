from pyecharts.charts import Bar, CMap, Geo, Map, Grid, Line
from pyecharts import options as opts
# from snapshot_phantomjs import snapshot as driver
from snapshot_selenium import snapshot as driver
import logging
import io
import pyecharts.charts
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.commons import utils
from pyecharts.render.snapshot import make_snapshot
from pyecharts.globals import ChartType
import pandas as pd 
import numpy as np
import json
import re
import time
from pyecharts.commons.utils import JsCode
import math

class MjsCode(JsCode):
    def replace(self, pattern: str, repl: str):
        # print(self.js_code)
        # self.js_code = re.sub(pattern, repl, self.js_code)
        # self.js_code = re.sub("newline", "\\n", self.js_code)
        # print(self.js_code)
        return self

class Base():
    

    def __init__(self):
        self.desired_width = 520
        colors = ['#B7990D', '#3D2C2E', "#276FBF", "#183059"]
        text_colors = ["#333", "#efefef", "#efefef", "#efefef"]
        self.line_colors = [ opts.ItemStyleOpts(color=i) for i in colors ]
        self.bar_colors = [ opts.ItemStyleOpts(color=i) for i in colors ]
        self.bar_label_text_colors = text_colors
        # [ opts.LabelOpts(is_show=True, color=i, vertical_align= 'middle', horizontal_align="center",) for i in text_colors ]


        self.label_style = {

            "style1": opts.LabelOpts(
                vertical_align= 'middle',
                horizontal_align="center",
                color='#666',
                position=None,
                font_size=9,
                formatter=MjsCode(""" function(x){ var numberValue = Math.abs(x.data.value) > 999 ? Math.sign(x.data.value)*((Math.abs(x.data.value)/1000).toFixed(1)) + 'k' : Math.sign(x.data.value)*Math.abs(x.data.value);  var value = Number(x.data.value).toLocaleString('en-US'); var perecentage =  '(' + Number(x.data.percent * 100).toFixed() + '%' + ')'; return  numberValue  +'\n'+ perecentage; }"""
                 ) ,
            ),
             "single_value": opts.LabelOpts(
                horizontal_align="center",
                color='#666',
                position=None,
                font_size=10,
                
                vertical_align= "middle",
                
                formatter=JsCode(""" function(x){ var numberValue = Math.abs(x.data[1]) > 999 ? Math.sign(x.data[1])*((Math.abs(x.data[1])/1000).toFixed(1)) + 'k' : Math.sign(x.data[1])*Math.abs(x.data[1]); var value = Number(x.data[1]).toLocaleString('en-US'); return  value ; } """
                 ) ,
            ),
             "single_value_k": opts.LabelOpts(
                horizontal_align="center",
                color='#666',
                position=None,
                font_size=10,
                
                vertical_align= "middle",
                
                formatter=JsCode(""" function(x){ var numberValue = Math.abs(x.data[1]) > 999 ? Math.sign(x.data[1])*((Math.abs(x.data[1])/1000).toFixed(1)) + 'k' : Math.sign(x.data[1])*Math.abs(x.data[1]); var value = Number(x.data[1]).toLocaleString('en-US'); return  numberValue ; } """
                 ) ,
            ),
            "percent": opts.LabelOpts(
                vertical_align= 'middle',
                horizontal_align="center",
                position="right",
                font_size=10,
                formatter=JsCode("function(x){ return  Number(x.data.value).toLocaleString('US-en') + '\n(' + Number(x.data.percent * 100).toFixed() + '%' + ')';} "),
            ),
            "k_format_yaxis" : opts.LabelOpts (
                vertical_align = 'middle',
                horizontal_align = "center",
                position = "right",
                margin = 15,
                font_size = 12,
                formatter= JsCode(" function (value, index) { var val = value; var numberValue = Math.abs(val) > 999 ? Math.sign(val)*((Math.abs(val)/1000).toFixed(1)) + 'k' : Math.sign(val)*Math.abs(val); return numberValue + ' '; }")
            ),
             "x_data": opts.LabelOpts(
                vertical_align="middle",
                color='#fff',
                position='insideBottom',
                font_size=8,
                rotate=90,
                margin=15,
                horizontal_align='top',
                formatter=JsCode(""" function(x){ console.log(x); var value = Number(x.data).toLocaleString('en-US'); return  value ; } """
                 ) ,
            )
        }
        
        range_colors = [
            "#fedd63",
            "#fcaf5d",
            "#ff6666"
            ]
        # range_colors.reverse()
        self.visual_map_options = {
            "count" : opts.VisualMapOpts(
                    is_piecewise=True,
                    orient= 'horizontal',
                    min_=  0,
                    range_text = ['0'],
                    is_calculable = True,
                    range_color = range_colors,
                    item_width = 40,                 
                    item_height = 5,
                    pos_left= '10%'
                ),
            "dwell" : opts.VisualMapOpts(
                    is_piecewise=True,
                    orient= 'horizontal',
                    min_=  0,

                    
                    range_text = ['0'],
                    is_calculable = True,
                    range_color = range_colors,
                    item_width = 20,                 
                    item_height = 5,
                    pos_left= '10%'
                    # formatter= JsCode("function (low, high) { function timeLapse(timeDiff) { var timeStamp = []; var hours = timeDiff / 3660; if (Math.round(hours) > 0){  hours = Math.round(hours); timeStamp.push(hours+  'h');timeDiff = timeDiff % 3660;}var minutes = timeDiff / 60; if (Math.round(minutes) > 0){ timeStamp.push(Math.round(minutes) + 'm'); timeDiff = timeDiff % 60; } var seconds = Math.round(timeDiff);seconds = timeDiff; if (Math.round(seconds) > 0 ) { timeStamp.push(Math.round(seconds) + 's'); } return timeStamp.join(''); } return timeLapse(low) + ' - ' + timeLapse(high) }")
                )
        }

        self.visual_map_formatter = {
            "count":
            {
                "formatter": JsCode("function(low,high){  return  Number(parseInt(high,10)).toLocaleString('US-en'); }")
            },
            "dwell":
            {
                "formatter": JsCode("function (low, high) { function timeLapse(timeDiff) { var timeStamp = []; var hours = timeDiff / 3660; if (Math.floor(hours) > 0){  hours = Math.round(hours); timeStamp.push(hours+  'h');timeDiff = timeDiff % 3660;}var minutes = timeDiff / 60; if (Math.floor(minutes) > 0){ timeStamp.push(Math.round(minutes) + 'm'); timeDiff = timeDiff % 60; } var seconds = Math.round(timeDiff);seconds = timeDiff; if (Math.floor(seconds) > 1 ) { /*timeStamp.push(Math.round(seconds) + 's');*/ } return timeStamp.join(''); } return  timeLapse(high) }")
            }
        }

        self.yaxis_details = opts.AxisOpts(
                    name="Visitor's Count", 
                    name_location="middle",
                    name_gap= 40,
                    splitline_opts=opts.SplitLineOpts(is_show = False, 
                                                      linestyle_opts=opts.LineStyleOpts(
                                                      color="#dddddd"
                                                      )
                                    ),
                    axislabel_opts= self.label_style["k_format_yaxis"]
                )

        self.global_opts = {
            "default" : {
                "xaxis_opts":opts.AxisOpts(
                    
                    axislabel_opts=opts.LabelOpts(rotate=-15, font_size=12)
                ),
                "yaxis_opts":self.yaxis_details,
                "title_opts":opts.TitleOpts(title="", subtitle="")
            }
        }
        self.chart = {}


    def set_add_global_options(self, options:dict ={}):
        self.chart.options.update(options)

    def set_globl_option(self, options: dict = {}):
        # options["label_opts"] = self.label_style[options.get('label_opts')]  if  not options.get('label_opts') == None else self.global_opts
        self.chart.set_global_opts( **self.global_opts["default"] )
        
        return self

    def get_chart_instance(self):
        return self.chart

    def generate(self, file_name:str = "render.html", image_name: str = "example.png" ):
        
        self.chart.render(file_name)
        make_snapshot(   driver, file_name, image_name, pixel_ratio=1.5)
    
    def calculate_desired_height(self, map_width, map_height):
        return  self.desired_width * (map_height / map_width)



class BarChart(Base):

    def __init__(self, bar_title: str, width:str ="540px", height:str = "300px"):
        super(BarChart, self).__init__()
        self.chart = Bar(init_opts=opts.InitOpts(width=width, height=height, animation_opts=opts.AnimationOpts(animation=False)))
        self.configuration = {}
        self.set_globl_option()

    def xaxis(self, data: list):
        self.chart.add_xaxis( data)
        return self 

    def ydata(self, title: str,  data: list, options: dict = {}):
        # print("Label Options", self.bar_label_text_colors.pop())
        # print("Options ", options)
        self.chart.add_yaxis(title, data, category_gap="60%", itemstyle_opts=self.bar_colors.pop(),  **options )

        return self

    def set_option(self, options: dict = {}, xaixs: dict = {}, yaxis: dict = {}):

        # print("List", self.bar_label_text_colors.pop())
        self.label_style[options['label_opts']].update(color = self.bar_label_text_colors.pop())
        options["label_opts"] = self.label_style[options['label_opts']]

        options["linestyle_opts"] = opts.LineStyleOpts({"shadowOffsetY":-5 })
        options["axislabel_opts"] = self.label_style["k_format_yaxis"]
        self.yaxis_details.opts.update(**yaxis)
        self.set_globl_option()
        self.chart.set_series_opts(
            **options
        )
        return self


class LineChart(Base):
    def __init__(self, bar_title: str):
        super(LineChart, self).__init__()
        self.chart = Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(animation=False)))
        self.configuration = {}
        self.set_globl_option()

    def xaxis(self, data: list):    
        self.chart.add_xaxis( data)
        return self 

    def ydata(self, title: str,  data: list):
        self.chart.add_yaxis(title, data, color="#666", xaxis_index=0, itemstyle_opts=self.line_colors.pop()  )
        
        return self

    def set_option(self, options: dict = {}):
        options["label_opts"] = self.label_style[options['label_opts']]

        self.chart.set_series_opts(
            **options
        )
        return self

class OverLap(Base):
    
    def __init__(self, width:str, height:str, **kwargs):
        super(OverLap, self).__init__()
        self.chart  =  Grid(init_opts=opts.InitOpts(width=width, height=height, animation_opts=opts.AnimationOpts(animation=False)))
        
    
    def add(self, overlap, is_control_axis_index=False):
        self.chart.add(overlap,  grid_opts=opts.GridOpts(pos_left="10%"), is_control_axis_index=True)
        return self


class CustomMap(Base):

    def __init__(self, map_name:str = "", map_stats_type:str="count",  label_show:str=False, width: str = "540px", height: str= "300px", bounding:dict ={}, options:dict = {}):
        super(CustomMap, self).__init__()

        # self.width = bounding.get('width', 0)
        # self.height = bounding.get('height', 0)
        self.width = self.desired_width
        self.height = self.calculate_desired_height(bounding.get('width', 0), bounding.get('height', 0))

        self.map_initial_opts = {"width":width, "height":height, "animation_opts":opts.AnimationOpts(animation=False), "showLegendSymbol": True, "boundingCoords":bounding} 
        # print("Map",self.map_initial_opts, )
        self.chart  =  CMap( init_opts=self.map_initial_opts)
        self.map_name = map_name
        self.is_label = label_show
        self.stats_type = map_stats_type
        label = "function(params){  return '\n' + params.name + '\n Visitors:' + (new Intl.NumberFormat('en-UK', { maximumFractionDigits: 0 }).format(params.value)) + '\n'}"

        
        
        self.js_code_label = MjsCode(label)

    def schema(self, data):
        self.chart.add_schema(self.map_name, data)
        return self
    
    def set_data(self, data):
        df = pd.DataFrame(data)
        # print("Max Value",df[1].max())
        # self.visual_map_options[self.stats_type].update(**{"max_": df[1].max(), "min_":0} )
        # self.visual_map_options[self.stats_type].update()
        self.visual_map_options[self.stats_type].update(**self.visual_map_formatter[self.stats_type], max = math.ceil(df[1].max()))

        self.global_opts["default"].update({
                "visualmap_opts": self.visual_map_options[self.stats_type]
        })
        
        self.set_globl_option()
        label_opts = opts.LabelOpts(
            formatter=self.js_code_label, 
            is_show= self.is_label, 
            position= "inside", 
            color='#666666',
            background_color="#eeeeeea2",
            border_radius=2,
            border_color="#666666",
            font_size=10
        )
        label_opts.update(padding=1)
        self.chart.add("", data, maptype=self.map_name ,  
        label_opts=label_opts, is_map_symbol_show=False,
            zoom=1
        )
        return self



class StatsMap(Base):

    def __init__(self, map_name:str = "", width: str = "540px", height: str= "300px", options:dict = {}, bounding: dict = {}):
        super(StatsMap, self).__init__()
        print('bounding ' , bounding)
        # self.width = bounding.get('width', 0)
        # self.height = bounding.get('height', 0)

        self.width = self.desired_width
        self.height = self.calculate_desired_height(bounding.get('width', 0), bounding.get('height', 0))

        label = "function(params){ return '\n' + params.name + '\n Visitors:' + (new Intl.NumberFormat('en-UK', { maximumFractionDigits: 0 }).format(params.value)) + '\n'}"


        self.map_initial_opts = {
                            "geo": {
                            "aspectScale": 1,
                            "roam": False,
                            # "boundingCoords": [
                            # [
                            #     0,
                            #     0
                            # ],
                            # [
                            #     260,
                            #     120
                            # ]
                            # ]
                            }
                        }
        self.chart_type = {
            'scatter': ChartType.SCATTER,
            'map' : ChartType.SCATTER,
            'geo': ChartType.LINES
        }
        fn = "function(val) { var maxSize = Math.round(30 + (10 * (val[2] / 300))); return maxSize; }"
        js_code = utils.JsCode(fn)


        self.symbol_size = {
            'map': 5,
            'scatter' : js_code
        }
        self.is_label = {
            'map': {'show': True, 'position': 'top'},
            'scatter' : { 'show': True, 'position': 'inside' },
            'geo': { 'show': False, 'position': 'top'}
        }
        self.map_initial_opts.update({"width":width, "height":height, "animation_opts":opts.AnimationOpts(animation=False) })
        self.chart  =  Geo( custom=True, init_opts=self.map_initial_opts)
        self.map_name = map_name
        self.js_code_label = utils.JsCode(label)

    def schema(self, data):
        self.chart.add_schema(maptype=self.map_name , map_data=data, zoom=1, itemstyle_opts = opts.ItemStyleOpts(area_color="#D1F5FF", border_color = "#A0C1D1", border_width= 1, opacity= 0.3))
        return self

    def coordinates(self, area_coordinates:dict):
        # print("Area Coordinates", area_coordinates)
        [self.chart.add_coordinate(k, i[0], i[1]) for k,i in area_coordinates.items()]
        return self
    
    def set_data(self, data,  stats = "scatter", type_ = 'scatter', color="#42597A"):
        df = pd.DataFrame(data)
        # print("Max Value",data)
        # self.global_opts["default"]["visualmap_opts"].update(**{"max": df[1].max(), "min_":0} )
        if type_ == 'scatter': 
            self.global_opts["default"].update({
                    "visualmap_opts": opts.VisualMapOpts(
                        is_piecewise=True,
                        orient= 'horizontal',
                        min_=  0,
                        max_ =  int(df[1].max()),
                        
                        range_text = ["High", "Low"],
                        is_calculable = True,
                        range_color = [
                                        "#79de7c",
                                        "#fedd63",
                                        "#fcaf5d",
                                        "#ff6666"
                                        ],
                        item_width=70,                 
                        item_height=5
                    )
            })


        label_opts = opts.LabelOpts(
            formatter="{b}\n{c}", 
            is_show= True, 
            position= "left", 
            color='#666666',
            background_color="#eeeeee",
            border_radius=5,
            border_color="#666666",
            font_size=10
        )
        label_opts.update(padding=5, lineHeight=13)

        label = "function(val) {  return val.data.name + '\n'+ val.data.value.splice(-1,1)[0]; }"
        js_code_label = MjsCode(label)
        
        self.chart.add(stats,  data, 
            type_=  self.chart_type.get(type_), 
            symbol_size=self.symbol_size.get(type_), 
            is_large=False, 
            effect_opts=opts.EffectOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(curve=0.2, width=1, color=color),
            itemstyle_opts=self.bar_colors.pop(),
            label_opts=opts.LabelOpts(
                is_show=self.is_label.get(type_).get('show'),
                formatter=js_code_label,
                position= self.is_label.get(type_).get('position'),
                font_size=9
            )
        )
        return self

if __name__ == '__main__':

    b = (BarChart("Test")
    .xaxis( Faker.choose())
    .ydata("A",Faker.values())
    .ydata("B",Faker.values())
    .generate(file_name="visualization/test/html/render.html", image_name="visualization/test/images/example.png"))
    