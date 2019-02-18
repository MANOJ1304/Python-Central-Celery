"""make html file."""
import json
from jinja2 import Template


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
    a = t.render(item=data)
    config_file = {}
    config_file['newsletter_html'] = a
    config_file['subject'] = data.get('alarm_message', "Error Alert.")
    return config_file
