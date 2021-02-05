import json
from pymongo import MongoClient
from bson import ObjectId
import sys
from collections import Counter
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
import random
import math

## Example topic queries
"""
# general topics
physics
mathematics
computer science
quantitative biology
quantitative finance
statistics
EESS (electrical engineering and systems science)
economics

# some subtopics
"astrophysics", "high energy physics","geophysics",
"condensed matter","quantum physics","general relativity",
"nonlinear sciences"
"""

query_str = "physics"
dbg_prefix = "\n*******"

## Convenience functions
def style_plots(fig):
    fig.toolbar.logo = None
    fig.outline_line_color = None
    fig.xgrid.grid_line_color = "gray"
    fig.ygrid.grid_line_color = "gray"
    fig.xgrid.grid_line_alpha = 0.2
    fig.ygrid.grid_line_alpha = 0.2
    fig.yaxis.minor_tick_line_alpha = 0
    fig.xaxis.major_tick_line_color = "gray"
    fig.yaxis.major_tick_line_color = "gray"
    fig.yaxis.axis_line_color = "gray"
    fig.xaxis.axis_line_color = "gray"
    fig.yaxis.axis_line_alpha = 0.2
    fig.xaxis.axis_line_alpha = 0.2
    fig.title.text_font_size = "12pt"
    fig.title.text_font_style = "normal"
    fig.title.text_color = "black"
    fig.yaxis.major_label_text_color = "gray"
    fig.xaxis.major_label_text_color = "gray"
    fig.xaxis.major_label_text_font_size = "8pt"
    fig.yaxis.major_label_text_font_size = "8pt"
    return fig


def debug_print(var, var_name):
    print(f"\n************** {var_name} **************")
    print(var)
    print("\n")


## Define mongo client
client = MongoClient()
if "arxiv" not in client.list_database_names():
    print(f"{dbg_prefix} No arxiv database available...")
db = client["arxiv"]
records = db["records"]

## Example calls from the monogodb
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def printCursor(cursor):
    json_res = []
    for document in cursor:
        encoded_reponse = JSONEncoder().encode(document)
        print(json.dumps(json.loads(encoded_reponse), indent=4))
        print("------------------------------------")
        json_res.append(json.loads(encoded_reponse))
    return json_res


# Should I assign colors and positioning here?
colors = [
    "#BF1573",
    "#242F73",
    "#A3BFD9",
    "#D9D16A",
    "#D95829",
    "#b75c61",
    "#eaa775",
    "#ef879a",
    "#827bf7",
    "#a6a9f9"
    ]
# ["#97778e",
# "#a18e68",
# "#ef879a",
# "#e0d490",
# "#9ad6fb",
# "#b75c61",
# "#eaa775",
# "#ef879a",
# "#827bf7",
# "#a6a9f9"]
color_dict = {
    "statistics":               colors[0],
    "finance":                  colors[1],
    "physics":                  colors[2],
    "mathematics":              colors[3],
    "electrical engineering":   colors[4],
    "economics":                colors[5],
    "nonlinear sciences":       colors[6],
    "astrophysics":             colors[7],
    "biology":                  colors[8],
    "computer science":         colors[9],
}
sector_dict = {}
for i in range(0, len(list(color_dict.keys()))):
    sector_dict[list(color_dict.keys())[i]] = [i * ((2*math.pi)/10), (i+1) * ((2*math.pi)/10)]

def jitter(l):
    return random.uniform(-l, l)

def getCursor(cursor):
    json_res = []
    for document in cursor:
        encoded_reponse = JSONEncoder().encode(document)
        json_elem = json.loads(encoded_reponse)
        # Split topic and sub topic into two fields
        topic = json_elem["subject"].split("-")
        if ("-" in json_elem["subject"]) and (topic[0].strip() in list(color_dict.keys())):
            json_elem["sec_since_epoch"] = (
                pd.to_datetime(json_elem["date"]) - pd.Timestamp("1970-01-01")
            ) // pd.Timedelta("1s")
            json_elem["desc_len"] = len(json_elem["description"])
            json_elem["topic"] = topic[0].strip()
            json_elem["topic_sub"] = topic[1].strip()

            # Assign random r, theta for now
            # json_elem["p_radius"] = random.uniform(1, 260)
            json_elem["p_radius"] = ((json_elem["sec_since_epoch"]/10000000) * 1.5) + jitter(5)
            # json_elem["p_theta"] = random.uniform(0, 6.2)  # Javascript takes angle in radians
            lower_lim = sector_dict[json_elem["topic"]][0] + jitter(.16)
            upper_lim = sector_dict[json_elem["topic"]][1] + jitter(.16)
            json_elem["p_theta"] = random.uniform(lower_lim, upper_lim)

            # Assign color
            json_elem['p_color'] = color_dict[json_elem["topic"]]

            json_res.append(json_elem)
    
    return json_res


def query(q, query_str):
    res = records.find(q)
    json_res = printCursor(res)
    print(f"{dbg_prefix} Number of results matching '{query_str}': {len(json_res)}\n")
    return json_res

def getTimeseries(res):
    all_dates = [pd.to_datetime(res[i]["date"]) for i in range(len(res))]
    df = pd.DataFrame.from_dict(Counter(all_dates), orient="index").reset_index()
    df.columns = ["date", "record_count"]
    df = df.sort_values(by=["date"]).reset_index().drop(["index"], axis=1)
    df["date"] = [x.strftime('%Y-%m-%d') for x in df["date"]]
    return json.dumps(json.loads(df.reset_index().to_json(orient='records')))

def timeseries(res, flag, query_str):
    json_res = getCursor(res)
    all_dates = [pd.to_datetime(json_res[i]["date"]) for i in range(len(json_res))]
    df = pd.DataFrame.from_dict(Counter(all_dates), orient="index").reset_index()
    df.columns = ["date", "record_count"]
    df = df.sort_values(by=["date"]).reset_index().drop(["index"], axis=1)
    print(df)
    # df["record_count"] = np.log(df["record_count"])
    # df.loc[df["record_count"] == 0, "record_count"] = 1
    plot_height = 650
    color = "#BF5E49"
    p = figure(
        plot_height=plot_height,
        plot_width=plot_height * 2,
        # title=f"publication date counts // log scale // {flag} includes: {query_str}",
        title=f"publication date counts // {flag} includes: {query_str}",
        x_axis_type="datetime",
        tools="box_zoom,xpan,save,reset",
    )
    p.vbar(
        x="date",
        top="record_count",
        fill_color=color,
        line_color=color,
        source=ColumnDataSource(data=df),
    )
    p.varea(
        x="date",
        y1=0,
        y2="record_count",
        fill_color=color,
        source=ColumnDataSource(data=df),
        fill_alpha=0.2,
    )
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    show(style_plots(p))


## Grab command line query if there is one
if len(sys.argv) == 3:
    query_str = sys.argv[2].lower()
    flag = sys.argv[1].lower()
    if "topic" in flag:
        res = query({"subject": {"$regex": f".*{query_str}.*"}}, query_str)
        timeseries(res, "topic", query_str)
    elif "author" in flag:
        res = query({"creator": {"$regex": f".*{query_str}.*"}}, query_str)
        timeseries(res, "author", query_str)
    else:
        print(
            f"Did not recognize the flag '{flag}'. Did you mean '-topic' or '-author'?"
        )


## Can I normalize by total pubs submitted that day or that year?
