"""make html file."""
import json
from jinja2 import Template
from tasks.mail_sender_logs.api_get import ApiRequest


def make_html_file(data):
    """html file """
    # print('kkkd... ', data, type(data))
    if isinstance(data, str):
        data = json.loads(data)

    # print(data.keys())
    # print(data.values())
    # print(('\n\n########\n data items:..  {}\n##___##__##__##\n').format(data))

    t = Template(
        '''<html>
                <head>
                    <style>
                        table,
                        th,
                        td {
                            border: .5px solid black;
                            border-collapse: collapse;
                        }

                        th,
                        td {
                            padding: 5px;
                            text-align: center;
                        }

                        .custom_color {
                            background-color: #cccccc;
                        }
                    </style>
                </head>

                <body>
                    <h2>{{item.alarm_message}}</h2>
                    <table style="width:100%">
                        <tr class="custom_color">
                            <th>alarm_message</th>
                            <td>{{item.alarm_message or \'N/A\'}}</td>
                        </tr>
                        <tr>
                            <th>venue name</th>
                            <td>{{item.ve_name or \'N/A\'}}</td>
                        </tr>
                        <tr>
                            <th>alarm_name</th>
                            <td>{{item.alarm_name or \'N/A\'}}</td>
                        </tr>
                        <tr class="custom_color">
                            <th>alarm_threshold</th>
                            <td>{{item.alarm_threshold or \'N/A\'}}</td>
                        </tr>
                        <tr>
                            <th>cluster_id</th>
                            <td>{{item.cluster_id or \'N/A\'}}</td>
                        </tr>
                        <tr class="custom_color">
                            <th>timestamp</th>
                            <td>{{item.timestamp or \'N/A\'}}</td>
                        </tr>
                        <tr>
                            <th>veId</th>
                            <td>{{item.veId or \'N/A\'}}</td>
                        </tr>
                    </table>
                </body>
            </html>
                '''
    )
    api_obj = ApiRequest()
    ve_name = api_obj.get_venue_info(data['veId'])
    data['ve_name'] = ve_name
    a = t.render(item=data)
    config_file = {}
    config_file['newsletter_html'] = a
    config_file['subject'] = data.get('alarm_message', "Error Alert.")
    return config_file
