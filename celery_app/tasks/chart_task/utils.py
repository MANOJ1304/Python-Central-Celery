from datetime import datetime, timedelta
import pytz
import jwt
import calendar
from datetime import datetime


def time_to_utc(input_time, zone_name):
    local = pytz.timezone(zone_name)
    local_dt = local.localize(input_time.replace(tzinfo=None))
    return local_dt.astimezone(pytz.utc)
def utc_to_time(input_time, zone_name):
    return input_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(zone_name))

def get_ts(from_date):
    return  datetime.timestamp(from_date) * 1000

# zone_name = 'America/Chicago'
def get_week_dates(from_date_str, to_date_str, zone_name):
    
    start_date  = datetime.strptime(from_date_str + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_date  = datetime.strptime(to_date_str + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    
    start_date = time_to_utc(start_date, zone_name)
    end_date = time_to_utc(end_date, zone_name)
    
    prev_week_start = start_date - timedelta(days=7)
    prev_week_end = end_date - timedelta(days=7)
    
    prev_month_week_start = datetime.strptime( '{}-{}-{} {}:{}:{}'.format(start_date.year, start_date.month - 1,
        start_date.day, start_date.hour, start_date.minute, start_date.second), "%Y-%m-%d %H:%M:%S")
    prev_month_week_end = datetime.strptime( '{}-{}-{} {}:{}:{}'.format(end_date.year, end_date.month - 1,
        end_date.day, end_date.hour, end_date.minute, end_date.second), "%Y-%m-%d %H:%M:%S")
    
    prev_year_week_start = datetime.strptime( '{}-{}-{} {}:{}:{}'.format(start_date.year - 1, start_date.month,
        start_date.day, start_date.hour, start_date.minute, start_date.second), "%Y-%m-%d %H:%M:%S")
    prev_year_week_end = datetime.strptime( '{}-{}-{} {}:{}:{}'.format(end_date.year - 1, end_date.month,
        end_date.day, end_date.hour, end_date.minute, end_date.second), "%Y-%m-%d %H:%M:%S")
    
    # print('current ', start_date, end_date)
    # print('last week  ', prev_week_start, prev_week_end)
    # print('month week  ', prev_month_week_start, prev_month_week_end)
    # print('year week  ', prev_year_week_start, prev_year_week_end)
    return [[ get_ts(start_date) , get_ts(end_date)],
            [get_ts(prev_week_start), get_ts(prev_week_end)],
            [get_ts(prev_month_week_start), get_ts(prev_month_week_end)],
            [get_ts(prev_year_week_start), get_ts(prev_year_week_end)]]


# Format - "2020-03-23T00:00:00.000-07:00"
def get_date(str_date):
    return datetime.strptime(str_date[:-10], "%Y-%m-%dT%H:%M:%S")

def get_day_of_week(cr_date):
    # my_date = date.today()
    return calendar.day_name[cr_date.weekday()][:3]

def day_of_week(str_date):
    dt = get_date(str_date)
    return get_day_of_week(dt)

def get_month_name(date_obj):
    return calendar.month_name[date_obj.month]

def get_week_number(date_obj):
    return date_obj.isocalendar()[1]

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def get_display_date(dt_in_str):
    dt = datetime.strptime(dt_in_str, "%Y-%m-%d")
    # dt = datetime.fromtimestamp(dt_in_ms / 1000)
    return custom_strftime('%B {S}, %Y', dt)

def get_date_with_format(dt_in_str):
    return datetime.strptime(dt_in_str, "%Y-%m-%d")

def get_12_hour(str_hour):
    d = datetime.strptime(str_hour, "%H:%M:%S")
    return d.strftime("%I %p" )


# print custom_strftime('%B {S}, %Y', dt.now())


def prepare_report_data(visitors_summmary_info, header_info, chart_info, footer_info, base_url):
    report_data = {}
    report_data['header_info'] = header_info
    report_data['visitors_info'] = []
    report_data['events'] = []
    visitors_trend_title = ["Current Week", "Previous Week", "Same Week, Previous Month", "Same Week, Previous Year"]
    chart_names = ['current_week', 'last_week', 'last_month', 'last_year']
    for i, visitor_data in enumerate(visitors_summmary_info):
        if len(visitor_data['analytic_data']) > 0:
            if i == 0:
                # Build data for current week
                report_data['visitors_count'] = [format(i, ',d') for i in visitor_data['analytic_data'][0]['series'][3]['total_visitor']]
                report_data["weather_info"] = visitor_data['analytic_data'][0]['series'][3]['weather']
                # for event in visitor_data['analytic_data'][0]['series'][0]['holiday']:
                #     if 'event' in event.get('kind', ''):
                #         report_data['events'].append(event)

            visitor_info = {}
            visitor_info['title'] = visitors_trend_title[i]
            visitor_info['count'] = format(visitor_data['analytic_data'][0]['series'][2]['value'], ',d')
            visitor_info['avg_change'] = str(visitor_data['analytic_data'][0]['series'][2]['avg_change']) + '%'
            # visitor_info['img_url'] = '{}{}.png'.format(base_url, chart_names[i])
            visitor_info['img_url'] = visitor_data['img_url']
            report_data['visitors_info'].append(visitor_info)
    # if len(visitors_summmary_info) > 0:
    #     report_data["weather_info"] = visitors_summmary_info[0]['analytic_data'][0]['series'][3]['weather']
    
    report_data['chart_info'] = chart_info
    report_data['footer_info'] = footer_info
    return report_data
