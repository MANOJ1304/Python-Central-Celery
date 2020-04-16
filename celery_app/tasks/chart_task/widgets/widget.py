from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Gauge
from pyecharts.render import make_snapshot
from pyecharts.faker import Collector, Faker
from snapshot_phantomjs import snapshot
widget_config  = [
    {
        "title": "Visitors",
        "charts" : [

        ]
    }
]

charts = [
                    {
                       "type":"bar",
                       "plotting": "echart|plotly",   
                        "title": {
                            "heading": "ABC",
                            "sub_heading": "xyz"
                        },
                        "data":[
                            {
                                "legend": {
                                    "data": 'asdsa',
                                    "x": ''
                                },
                                "grid": {

                                },
                                "xAxis": {
                                    "type" : 'category',
                                    "boundaryGap" : False,
                                    "axisLine": {"onZero": True},
                                    "data": [
                                        'a', 'b', 'c', 'd', 'e', 'f'
                                    ]
                                },
                                "yAxis": {
                                    "name" : '流量(m^3/s)',
                                    "type" : 'value',
                                    "max" : 500
                                },
                                "series": {
                                    "name":'流量',
                                    "type":'line',
                                    "symbolSize": 8,
                                    "hoverAnimation": False,
                                    "data":[
                                        5, 20, 36, 10, 75, 90
                                    ]
                                }
                            },
                            {
                                "legend": {
                                    "data": 'rete',
                                    "x": ''
                                },
                                "grid": {

                                },
                                "xAxis": {
                                    "type" : 'category',
                                    "boundaryGap" : False,
                                    "axisLine": {"onZero": True},
                                    "data": [
                                        'a', 'b', 'c', 'd', 'e', 'f'
                                    ]
                                },
                                "yAxis": {
                                    "name" : '流量(m^3/s)',
                                    "type" : 'value',
                                    "max" : 500
                                },
                                "series": {
                                    "name":'流量',
                                    "type":'line',
                                    "symbolSize": 8,
                                    "hoverAnimation": False,
                                    "data":[
                                        5, 10, 26, 20, 35, 40
                                    ]
                                }
                            }
                        ]
                },
                {
                    "type":"gauge",
                    "title": {
                        "heading": "Memory",
                        "sub_heading": "xyz"
                    },
                    "data":[
                        {
                            "legend": {
                                "data": '',
                                "x": ''
                            },
                            "grid": {

                            },
                            "xAxis": {
                                "type" : 'category',
                                "boundaryGap" : False,
                                "axisLine": {"onZero": True},
                                "data": 'a'
                            },
                            "yAxis": {
                                "name" : '流量(m^3/s)',
                                "type" : 'value',
                                "max" : 500
                            },
                            "series": {
                                "name":'流量',
                                "type":'line',
                                "symbolSize": 8,
                                "hoverAnimation": False,
                                "data": 70
                            }
                        }
                    ]
            }
]

def bar(data):
    bar = Bar().set_global_opts(title_opts=opts.TitleOpts(title="sdasd", subtitle="sadsa"))

    # bar = Bar(data['title']['heading'], data['title']['sub_heading'], width=600, title_pos= 'center',title_top='top')
    for item in chart_info['data']:
        bar.add_xaxis( item['xAxis']['data'])
        bar.add_yaxis(item['legend']['data'], item['series']['data'])
    
    print("{0}.png".format(data['title']['heading']).lower())
    make_snapshot(snapshot, bar.render(), "../data/{0}.png".format(data['title']['heading']).lower())

def gauge(data):
    gauge = Gauge(data['title']['heading'], width=600, title_pos= 'center',title_top='top')
    for item in chart_info['data']:
        gauge.add(item['legend']['data'], item['xAxis']['data'], item['series']['data'])
    gauge.render()
    make_snapshot('render.html', "{0}.png".format(data['title']['heading']).lower())

def create_chart(chart):
    print(chart)
    type_of_chart = chart['type'].lower()
    if 'bar' in type_of_chart:
        bar(chart)
    # elif 'gauge' in type_of_chart:
    #     gauge(chart)

for chart_info in charts:
    create_chart(chart_info)

if __name__ == '__main__':
 pass