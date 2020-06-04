import plotly_express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import flask
from flask import Flask
import os
import dash_table
import plotly.graph_objs as go
import base64
import dash_bio as dashbio

#### Load data ########################################

deep = pd.read_csv("data/deep_with_tax_levels.tsv", sep='\t')
deep = deep[
    ['#ARG', 'ORF_ID', 'contig_id', 'predicted_ARG-class', 'probability', 'plasmid', 'taxon_name_kaiju',
     'class',
     'order', 'phylum', 'family', 'genus', 'species', 'All ARGs in contig', '# ARGs in contig', "description"]]

deep[' index'] = range(1, len(deep) + 1)

#######################################################

tabs_styles = {
    'height': '40px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}


env = pd.read_csv("data/table_env.tsv", sep='\t')
dimensions = ["ARG"]
default = "MCR-1"
append_text = "ARG"

env_class = pd.read_csv("data/table_env_class.tsv", sep="\t")
dimensions_class = ["Antibiotic Class"]
default_class = "polymyxin"

arg_count = len(set(deep["#ARG"]))
class_count = len(set(deep["predicted_ARG-class"]))

PAGE_SIZE = 20

col_options = [dict(label=x, value=x) for x in env.columns[0:-45]]
col_options_class = [dict(label=x, value=x) for x in env_class.columns[0:-45]]

col_options2 = [dict(label=x, value=x) for x in ['Marine_provinces', 'Environmental_Feature',
                                                 'Ocean_sea_regions', 'Biogeographic_biomes'
                                                 ]]

col_options3 = [dict(label=x, value=x) for x in
                ['Latitude [degrees North]', 'Longitude [degrees East]', 'Sampling depth [m]', 'Mean_Temperature [deg C]*',
                 'Mean_Salinity [PSU]*', 'Mean_Oxygen [umol/kg]*', 'Mean_Nitrates[umol/L]*',
                 'NO2 [umol/L]**', 'PO4 [umol/L]**', 'NO2NO3 [umol/L]**', 'SI [umol/L]**', 'miTAG.SILVA.Taxo.Richness',
                 'miTAG.SILVA.Phylo.Diversity', 'miTAG.SILVA.Chao',
                 'miTAG.SILVA.ace', 'miTAG.SILVA.Shannon', 'OG.Shannon', 'OG.Richness', 'OG.Evenness',
                 'FC - heterotrophs [cells/mL]', 'FC - autotrophs [cells/mL]', 'FC - bacteria [cells/mL]',
                 'FC - picoeukaryotes [cells/mL]', 'minimum generation time [h]']]

dimensions2 = ["Feature"]
dimensions3 = ["Environmental parameters"]

image_filename = 'images/resistomedblogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

###
app = dash.Dash(__name__)
server = app.server
app.title = "ResistomeDB"

#server = Flask(_name_)
#app = dash.Dash(_name_, server=server)
#app.title = "ResistomeDB"

app.layout = html.Div(children =[html.Div(className="pretty_container",
                                children=[
                                    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
                                ]),
                       html.Br(),

                       html.Div(className="pretty_container",
                                children=[
                                    html.H4(
                                        "Global ocean resistome revealed: exploring Antibiotic Resistance Gene (ARGs) abundance and distribution on TARA oceans samples"),
                                    dcc.Markdown("[Cuadrat at al. 2020](https://doi.org/10.1093/gigascience/giaa046)"),
                                    html.P("This app allows the user to explore and visualize the Antibiotic Resistance Genes (ARGs) found on Tara Oceans samples. In short, Tara Oceans contigs (co-assembled by oceanic region) \
        were screened for ARGs using deepARG tool. Then, the results were manually curated to remove false positives and miss annotations. \
        The extracted environmental ARGs were then used as reference for mapping reads from individual Tara Oceans samples and the read counts were normalized \
        by average genome size, sequencing sample deep  (number of reads) and size of ARG (expressed in RPKG - reads per kb per genome equivalent). " + "We found a total of "+str(arg_count)
                                           + " ARGs conferring resistance to " + str(class_count) + " antibitotic classes. You can explore it by individual ARG or grouped  by antibiotic class."),
                        dcc.Markdown("Github code and data for this dashboard: [https://github.com/rcuadrat/resistome_dash](https://github.com/rcuadrat/resistome_dash)"),
                                ]),
                       dcc.Tabs(className='pretty_container',children=[
                           dcc.Tab(label='Explore by ARG', style=tab_style, selected_style=tab_selected_style, children=[
                               html.Div(
                                   [
                                       html.P(["Please, select the ARG:",
                                               dcc.Dropdown(id="arg", options=col_options, value=default)])
                                       for d in dimensions
                                   ],
                                   className="pretty_container",
                                   style={"width": "25%", "float": "left"},
                               ),

                               html.Div(
                                   [
                                       html.P(["Please, select the feature:",
                                               dcc.Dropdown(id="feat", options=col_options2,
                                                            value='Environmental_Feature')])
                                       for d2 in dimensions2
                                   ],
                                   className="pretty_container",
                                   style={"width": "25%", "float": "left"},
                               ),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Div(className="pretty_container",
                                        children=[
                                            html.P("Description of the selected ARG:"),
                                            html.P(id="desc"),
                                        ]),
                               html.Br(),
                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       dcc.Graph(id="graph", config={"displayModeBar": False}),

                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       dcc.Graph(id="graph2", config={"displayModeBar": False})
                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       html.H5('   Taxonomic level:'),
                                       html.P(dcc.Slider(id="slider", min=1, max=6,
                                                         marks={1: "Phylum", 2: "Class", 3: "Order", 4: "Family",
                                                                5: "Genus", 6: "Species"}, value=4),
                                              style={"width": "95%", "display": "inline-block", 'marginBottom': '1.0em',
                                                     'marginLeft': '1.5em'}),


                                       dcc.Graph(id="graph3", style={'marginBottom': '1.5em'},
                                                 config={"displayModeBar": False}),
                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       html.P(["Please, select the environmental parameter:",
                                               dcc.Dropdown(id="env_var", options=col_options3, value='Latitude [degrees North]')])
                                       for d3 in dimensions3
                                   ],
                                   style={"width": "35%", "float": "left",'marginBottom': '1.0em'},
                               ),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),

                               html.Div(className="pretty_container",
                                        children=[
                                            dcc.Graph(id="graph4", config={"displayModeBar": False}),
                                    dash_table.DataTable(

                                    id = 'ols',
                                    columns =  [{"name": i, "id": i, } for i in ["-","Coef.","Std.Err.","t",	"P>|t|",	"[0.025",	"0.975]"]]

                                )
                                        ]),
                               html.Br(),

                               html.Div(
                                   className="pretty_container",
                                   children=[html.H4(
                                       'Tara Ocean ORFs extracted from co-assembled contigs (from Oceanic regions), annotated by deepARG.'
                                       ),

                                             dash_table.DataTable(
                                                 id='datatable-paging',
                                                 columns=[
                                                     {"name": i, "id": i} for i in deep.drop(
                                                         [" index", 'order', 'phylum', 'family', 'genus', 'species',
                                                          'class', 'description'], axis=1).columns
                                                 ],
                                                 page_current=0,
                                                 page_size=PAGE_SIZE,
                                                 page_action='custom',
                                                 style_table={'overflowX': 'scroll'},
                                                 style_cell={
                                                     'height': 'auto',
                                                     'minWidth': '0px', 'maxWidth': '180px',
                                                     'whiteSpace': 'normal'
                                                 }
                                             ),
                                             html.Br(),

                                             dcc.Markdown("**ORF_ID**: identifier of the ORF predicted from Tara Ocean co-assembly; **contig_id**: ID of the contig; **predicted_ARG-class**: \
        antibiotic class; **probability**: DeepARG probability of the ARG annotation; **plasmid**: yes when the ARG was predicted to be in a plasmid by PlasFlow tool; \
        **taxon_name_kaiju**: taxonomic classification of the ARG by Kaiju tool (in the deeptest level possible); **All ARGs in contig**: all the ARGs in that contig; **# ARGs in contig**: total of ARGs in that contig."),
                                             html.Br(),
                                             html.A(id='download-link', children='Download Protein Fasta File',
                                                    style={'marginBottom': '1.5em'},
                                                    ),
                                            html.Br(),
                                            html.Br(),
                                             ]),
                               html.Div(id='alignment-viewer-output'),
                           ]),
                           dcc.Tab(label='Explore by antibiotic class', style=tab_style, selected_style=tab_selected_style,children=[
                               html.Div(
                                   [
                                       html.P(["Please, select the class:",
                                               dcc.Dropdown(id="class", options=col_options_class, value=default_class)])
                                       for d in dimensions_class
                                   ],
                                   className="pretty_container",
                                   style={"width": "25%", "float": "left"},
                               ),

                               html.Div(
                                   [
                                       html.P(["Please, select the feature:",
                                               dcc.Dropdown(id="feat2", options=col_options2,
                                                            value='Environmental_Feature')])
                                       for d2 in dimensions2
                                   ],
                                   className="pretty_container",
                                   style={"width": "25%", "float": "left"},
                               ),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),

                               html.Br(),
                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       dcc.Graph(id="graph_class", config={"displayModeBar": False}),

                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       dcc.Graph(id="graph2_class", config={"displayModeBar": False})
                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       html.H5('   Taxonomic level:'),
                                       html.P(dcc.Slider(id="slider2", min=1, max=6,
                                                         marks={1: "Phylum", 2: "Class", 3: "Order", 4: "Family",
                                                                5: "Genus", 6: "Species"}, value=4),
                                              style={"width": "95%", "display": "inline-block", 'marginBottom': '1.0em',
                                                     'marginLeft': '1.5em'}),

                                       dcc.Graph(id="graph3_class", style={'marginBottom': '2.5em'},
                                                 config={"displayModeBar": False}),
                                   ]),

                               html.Div(
                                   className="pretty_container",
                                   children=[
                                       html.P(["Please, select the environmental parameter:",
                                               dcc.Dropdown(id="env_var_class", options=col_options3, value='Latitude [degrees North]')])
                                       for d3 in dimensions3
                                   ],
                                   style={"width": "35%", "float": "left"},
                               ),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),
                               html.Br(),

                               html.Div(className="pretty_container",
                                        children=[
                                        dcc.Graph(id="graph4_class", config={"displayModeBar": False}),
                                    dash_table.DataTable(

                                    id = 'ols22',
                                    columns =  [{"name": i, "id": i, } for i in ["-","Coef.","Std.Err.","t",	"P>|t|",	"[0.025",	"0.975]"]]

                                )
                                        ]),
                               html.Div(
                                   className="pretty_container",
                                   children=[html.H4(
                                       'Tara Ocean ORFs extracted from co-assembled contigs (from Oceanic regions), annotated by deepARG.'
                                   ),

                                       dash_table.DataTable(
                                           id='datatable-paging_class',
                                           columns=[
                                               {"name": i, "id": i} for i in deep.drop(
                                                   [" index", 'order', 'phylum', 'family', 'genus', 'species',
                                                    'class', 'description'], axis=1).columns
                                           ],
                                           page_current=0,
                                           page_size=PAGE_SIZE,
                                           page_action='custom',
                                           style_table={'overflowX': 'scroll'},
                                           style_cell={
                                               'height': 'auto',
                                               'minWidth': '0px', 'maxWidth': '180px',
                                               'whiteSpace': 'normal'
                                           }
                                       ),
                                       html.Br(),

                                       dcc.Markdown("**ORF_ID**: identifier of ORF; **contig_id**: ID of the contig; **predicted_ARG-class**: \
antibiotic class; **probability**: DeepARG probability; **plasmid**: yes if the ARG was predicted to be in a plasmid by PlasFlow; \
**taxon_name_kaiju**: taxonomic classification of the ARG by Kaiju tool (in the deepest level); **All ARGs in contig**: all the ARGs in the contig; **# ARGs in contig**: total of ARGs in the contig."),
                                       html.Br(),

                                   ]),
                               html.Br(),

                           ])
                       ])
                       ])

@app.callback(Output("desc", "children"), [Input("arg", "value")])
def get_desc(desc):
    desctext = deep[deep["#ARG"] == desc][["#ARG", "description"]].drop_duplicates()["description"]
    return desctext

@app.callback(Output("graph", "figure"), [Input("arg", "value"), Input("feat", "value")])
def make_figure_box(size, feat):
    fig = px.scatter_mapbox(
        env,
        size=size,
        zoom=0.5,
        lat="Latitude [degrees North]", lon="Longitude [degrees East]", color=feat, hover_name="Marine_provinces",
        title=str(size) + " distribution and abundance (RPKG) on Tara Oceans.").for_each_trace(
        lambda t: t.update(name=t.name.replace(str(feat) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9", titlefont={
        "size": 20})
    fig.update_layout(autosize=True)
    fig.update_yaxes(automargin=True)
    fig.update_layout(mapbox_style="open-street-map")
    return fig

@app.callback(Output("graph_class", "figure"), [Input("class", "value"), Input("feat2", "value")])
def make_figure_box(size, feat):
    fig = px.scatter_mapbox(
        env_class,
        size=size,
        opacity=0.7,
        size_max=25,
        zoom=0.5,
        lat="Latitude [degrees North]", lon="Longitude [degrees East]", color=feat, hover_name="Marine_provinces",
        title=str(size).capitalize() + " resistance genes distribution and abundance (RPKG) on Tara Oceans.").for_each_trace(
        lambda t: t.update(name=t.name.replace(str(feat) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9", titlefont={
        "size": 20})
    fig.update_layout(autosize=True)
    fig.update_yaxes(automargin=True)
    fig.update_layout(mapbox_style="open-street-map")
    return fig

@app.callback(Output("graph2", "figure"), [Input("arg", "value"), Input("feat", "value")])
def make_figure(size, feat):
    fig = px.box(
        env,
        x=feat,
        y=size,
        notched=True,
        labels={size: size + "  RPKG"}, template='plotly_white',
        title=str(size) + " abundance by " + str(feat).replace("_", " ") + "."
    ).for_each_trace(lambda t: t.update(name=t.name.replace(str(feat) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9", titlefont={
        "size": 20})
    fig.update_layout(autosize=True)
    fig.update_yaxes(automargin=True)
    return fig

@app.callback(Output("graph2_class", "figure"), [Input("class", "value"), Input("feat2", "value")])
def make_figure(size, feat):
    fig = px.box(
        env_class,
        x=feat,
        y=size,
        notched=True,
        labels={size: size + "  RPKG"}, template='plotly_white',
        title=str(size).capitalize() + " resistance genes abundance by " + str(feat).replace("_", " ") + "."
    ).for_each_trace(lambda t: t.update(name=t.name.replace(str(feat) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9", titlefont={
        "size": 20})
    fig.update_layout(autosize=True)
    fig.update_yaxes(automargin=True)
    return fig

@app.callback(Output('download-link', 'href'),
              [Input('arg', 'value')])
def update_href(dropdown_value):
    dropdown_value = str(dropdown_value).replace("-", "").replace("(", "").replace(")", "").replace("''", "").replace(
        "'", "").replace("_", "")
    relative_filename = os.path.join(
        'data/ptn',
        '{}.edit.fasta'.format(dropdown_value)
    )

    return '/{}'.format(relative_filename)

@app.server.route('/data/ptn/<path:path>')
def serve_static(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(
        os.path.join(root_dir, 'data/ptn'), path
    )

@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size"),
     Input('arg', 'value')])
def update_table(page_current, page_size, arg):
    a = deep[deep["#ARG"] == arg]
    return a.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')

@app.callback(
    Output('datatable-paging_class', 'data'),
    [Input('datatable-paging_class', "page_current"),
     Input('datatable-paging_class', "page_size"),
     Input('class', 'value')])
def update_table(page_current, page_size, arg):
    a = deep[deep["predicted_ARG-class"] == arg]
    return a.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')

@app.callback(
    Output('graph3', 'figure'),
    [Input('arg', 'value'),
     Input('slider', 'value')])
def make_fig2(arg, taxlevel):
    levels = {1: "phylum", 2: "class", 3: "order", 4: "family", 5: "genus", 6: "species"}
    a = deep[deep["#ARG"] == arg]
    b = a.groupby(levels[taxlevel]).count()[["#ARG"]]
    # not use colors if level is species (too many colors)
    if taxlevel == 6:
        fig = go.Figure(px.bar(b.reset_index(), y="#ARG", x=levels[taxlevel], template='plotly_white',
                               title="Number of " + str(arg) +" resistance genes found per " + str(levels[taxlevel])).for_each_trace(
            lambda t: t.update(name=t.name.replace(str(levels[taxlevel]) + "=", ""))))
        fig.update_layout(margin=go.layout.Margin(b=200, l=0, r=0))

    else:
        fig = go.Figure(
            px.bar(b.reset_index(), y="#ARG", x=levels[taxlevel], template='plotly_white', color=levels[taxlevel],
                   title="Number of " + str(arg) +" resistance genes found per " + str(levels[taxlevel])).for_each_trace(
                lambda t: t.update(name=t.name.replace(str(levels[taxlevel]) + "=", ""))))
        fig.update_layout(margin=go.layout.Margin(b=0, l=0, r=0))

    fig.update_xaxes(title_text=None,automargin=True)
    fig.update_yaxes(title_text="Number of ORFs",automargin=True)
    fig.update_layout(autosize=True, titlefont={"size": 20})
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9")

    return fig

@app.callback(
    Output('graph3_class', 'figure'),
    [Input('class', 'value'),
     Input('slider2', 'value')])
def make_fig2(arg, taxlevel):
    levels = {1: "phylum", 2: "class", 3: "order", 4: "family", 5: "genus", 6: "species"}
    a = deep[deep["predicted_ARG-class"] == arg]
    b = a.groupby(levels[taxlevel]).count()[["predicted_ARG-class"]]
    # not use colors if level is species (too many colors)
    if taxlevel == 6:
        fig = go.Figure(px.bar(b.reset_index(), y="predicted_ARG-class", x=levels[taxlevel], template='plotly_white',
                               title="Number of " + str(arg) +" resistance genes found per " + str(levels[taxlevel])).for_each_trace(
            lambda t: t.update(name=t.name.replace(str(levels[taxlevel]) + "=", ""))))
        fig.update_layout(margin=go.layout.Margin(b=200, l=0, r=0))
    else:
        fig = go.Figure(
            px.bar(b.reset_index(), y="predicted_ARG-class", x=levels[taxlevel], template='plotly_white', color=levels[taxlevel],
                   title="Number of " + str(arg) +" resistance genes found per " + str(levels[taxlevel])).for_each_trace(
                lambda t: t.update(name=t.name.replace(str(levels[taxlevel]) + "=", ""))))
        fig.update_layout(margin=go.layout.Margin(b=0, l=0, r=0))

    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text="Number of ORFs")

    fig.update_layout(autosize=True, titlefont={"size": 20})
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9")
    return fig


@app.callback(
     [Output('graph4', 'figure'),
    Output('ols', 'data')],
    [Input('arg', 'value'),
     Input('env_var', 'value'),
     Input('feat', 'value')])
def make_env_fig(arg, env_var2, feat22):
    tmp=env[[arg,env_var2]]

    fig = px.scatter(tmp.dropna(), x=arg, y=env_var2, marginal_y="violin",
                     title=str(arg) + " vs. " + str(env_var2) + " scatterplot with OLS",
                     marginal_x="violin", trendline="ols", template='plotly_white').for_each_trace(
        lambda t: t.update(name=t.name.replace(str(feat22) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9")
    fig.update_layout(autosize=True, titlefont={
        "size": 20},
                      )
    results = px.get_trendline_results(fig)
    res = results.px_fit_results.iloc[0].summary2()
    df = res.tables[1].reset_index()
    df.rename(columns={"index": "-"}, inplace=True)

    return fig, df.to_dict('rows')





@app.callback(
    [Output('graph4_class', 'figure'),
    Output('ols22', 'data')],
    [Input('class', 'value'),
     Input('env_var_class', 'value'),
     Input('feat', 'value')])
def make_env_fig(arg, env_var2, feat22):
    tmp = env_class[[arg, env_var2]]
    fig = px.scatter(tmp.dropna(), x=arg, y=env_var2, marginal_y="violin",
                     title=str(arg) + " vs. " + str(env_var2) + " scatterplot with OLS",
                     marginal_x="violin", trendline="ols", template='plotly_white').for_each_trace(
        lambda t: t.update(name=t.name.replace(str(feat22) + "=", "")))
    fig.update_layout(plot_bgcolor="#F9F9F9", paper_bgcolor="#F9F9F9")
    fig.update_layout(autosize=True, titlefont={
        "size": 20},

                      )

    results = px.get_trendline_results(fig)
    res = results.px_fit_results.iloc[0].summary2()
    df =res.tables[1].reset_index()
    df.rename(columns={"index":"-"},inplace=True)

    return fig, df.to_dict('rows')




@app.callback(
    Output('alignment-viewer-output', 'children'),
    [Input('arg', 'value')]
)
def alig(arg):
    dropdown_value = str(arg).replace("-", "").replace("(", "").replace(")", "").replace("''", "").replace(
        "'", "").replace("_", "")
    relative_filename = os.path.join(
        'data/ptn/aligned',
        '{}.edit.fasta'.format(dropdown_value))
    try:
        with open(relative_filename, 'r') as content_file:

            data = content_file.read()
    except:
        data=[]

    if len(data) == 0:
        return 'Too few sequences for display alignment'
    if len(data) > 100000:
        return 'Too many sequences for display alignment'

    # if len(data) < 18000:
    #     return dashbio.AlignmentChart(
    #         data=data,
    #         showconsensus=False,
    #         extension="clustal",
    #         overview="slider",
    #         height=500,
    #     ),
    else:
        return dashbio.AlignmentChart(
                data=data,
                showconsensus=False,
                extension="clustal",
                overview="slider",
                height=1700,
                ),



if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")

#if _name_ == '_main_':
 #   app.run_server(debug=True, port=8055)