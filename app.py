import plotly_express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
#import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
import pandas as pd
import flask
import os
import dash_table
import plotly.graph_objs as go
import base64
import dash_bio as dashbio
from six import PY3

#### Load data ########################################

deep=pd.read_csv("data/deep_with_tax_levels.tsv",sep='\t')
deep=deep[['#ARG','ORF_ID','contig_id', 'predicted_ARG-class','probability','plasmid','taxon_name_kaiju','expressed','class',
           'order','phylum','family', 'genus', 'species','All ARGs in contig','# ARGs in contig',"description"]]

deep[' index'] = range(1, len(deep) + 1)

# selector = "#ARG"
# selector = "predicted_ARG-class"


env=pd.read_csv("data/table_env.tsv",sep='\t')


arg_count=len(set(deep["#ARG"]))
class_count=len(set(deep["predicted_ARG-class"]))


PAGE_SIZE = 20


col_options = [dict(label=x, value=x) for x in env.columns[0:-45]]
col_options2=[dict(label=x, value=x) for x in ['Marine_provinces','Environmental_Feature',
                                               'Ocean_sea_regions', 'Biogeographic_biomes'
                                               ]]

col_options3=[dict(label=x, value=x) for x in ['Mean_Lat*','Mean_Long*','Mean_Depth [m]*','Mean_Temperature [deg C]*',
                                               'Mean_Salinity [PSU]*', 'Mean_Oxygen [umol/kg]*', 'Mean_Nitrates[umol/L]*',
                                                'NO2 [umol/L]**', 'PO4 [umol/L]**', 'NO2NO3 [umol/L]**', 'SI [umol/L]**',                                                                    'miTAG.SILVA.Taxo.Richness','miTAG.SILVA.Phylo.Diversity', 'miTAG.SILVA.Chao',
                                                'miTAG.SILVA.ace', 'miTAG.SILVA.Shannon', 'OG.Shannon', 'OG.Richness', 'OG.Evenness',
                                                'FC - heterotrophs [cells/mL]', 'FC - autotrophs [cells/mL]', 'FC - bacteria [cells/mL]',
                                                'FC - picoeukaryotes [cells/mL]', 'minimum generation time [h]']]

dimensions = ["ARG"]
dimensions2= ["Feature"]
dimensions3= [ "Environmental parameters"]

image_filename = 'images/resistomedblogo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
# with open('data/ptn/aligned/MCR1.edit.fasta' ,'r') as content_file:
#          data = content_file.read()
#######################################################

app = dash.Dash(__name__)
server = app.server

######### Create app layout ###############   

app.layout = html.Div(
    [   # app header

        html.Div(className="pretty_container",
        children=[
        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
        ]),
        html.Br(),

        html.Div(className="pretty_container",
        children=[

        html.H4("Global ocean resistome revealed: exploring Antibiotic Resistance Genes (ARGs) abundance and distribution on TARA oceans samples through machine learning tools."),
        html.P("This app allows the user to explore and visualize the Antibiotic Resistance Genes (ARGs) found on Tara Oceans samples."),
        html.P("In short, Tara Oceans contigs (from regional samples co-assembled) \
        were used to screening for ARGs using deepARG tool. Then, the results were manually curated in order to remove false positives and miss annotations. \
        The extracted environmental ARGs were then used as reference for mapping reads from individual Tara Oceans samples and the read counts were normalized \
        by average genome size, sequencing sample deep  (number of reads) and size of ARG (expressed in RPKG - reads per kb per genome equivalent)."),
        dcc.Markdown("Please cite: [Cuadrat at al. 2019](https://doi.org/10.1101/765446)")
        ]),
        html.Div(
                [
                html.P([d + ":", dcc.Dropdown(id="arg", options=col_options,value='MCR-1')])
                for d in dimensions
            ],
            className="pretty_container",
            style={"width": "25%", "float": "left"},
                ),

        html.Div(
                 [
                html.P([d2 + ":", dcc.Dropdown(id="feat", options=col_options2,value='Environmental_Feature')])
                for d2 in dimensions2
            ],
            className="pretty_container",
            style={"width": "25%", "float": "left"},
                ),

        # html.Div(
        #     [
        #         dcc.Markdown("**Total Antibiotic Resistance Genes (ARGs):** "+ str(arg_count)),
        #         dcc.Markdown("**Total  antibiotic classes: **" + str(class_count))
        #     ],
        #     className="pretty_container",
        #     style={"width": "25%","float": "right"},
        #         ),
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
                dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),

                ]),

        html.Div(
                className="pretty_container",
                children=[
                dcc.Graph(id="graph2", style={"width": "75%", "display": "inline-block"})
                ]),

        html.Div(
                className="pretty_container",
                children=[
                html.H5('   Taxonomic level:'),
                html.P(dcc.Slider(id="slider",min=1,max=6,marks={1:"Phylum",2:"Order",3:"Class",4:"Family",5:"Genus",6:"Species"},value=4),
                style={"width": "95%", "display": "inline-block",'marginBottom': '1.0em','marginLeft':'1.5em'}),



                dcc.Graph(id="graph3", style={"width": "75%", "display": "inline-block",'marginBottom': '2.5em'}),
                ]),

        html.Div(
            className="pretty_container",
            children=[
                html.P([d3 + ":", dcc.Dropdown(id="env_var", options=col_options3,value='PO4 [umol/L]**')])
                for d3 in dimensions3
            ],
            style={"width": "25%", "float": "left"},
                ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),

        html.Div(className="pretty_container",
            children=[
            dcc.Graph(id="graph4", style={"width": "75%", "display": "inline-block"}),
            ]),
        html.Br(),


        html.Div(
        className="pretty_container",
        children=[html.H4('Tara Ocean ORFs extracted from co-assembled contigs (from Oceanic regions), annotated by deepARG.'
               ),

        dash_table.DataTable(
        id='datatable-paging',
        columns=[
        {"name": i, "id": i} for i in deep.drop([" index",'order','phylum','family', 'genus', 'species','class','description'],axis=1).columns
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

        dcc.Markdown("Columns description: 'ORF_ID': identifier of the ORF predicted from Tara Ocean co-assembly; 'contig_id': ID of the contig; 'predicted_ARG-class': \
        antibiotic class; 'probability': DeepARG probability of the ARG annotation; 'plasmid': yes when the ARG was predicted to be in a plasmid by PlasFlow tool; \
        'taxon_name_kaiju': taxonomic classification of the ARG by Kaiju tool (in the deeptest level possible); 'expressed': yes if FPKM > 5 in at least one metatranscriptomic \
        sample from TARA Oceans; 'All ARGs in contig': all the ARGs in that contig; '# ARGs in contig': total of ARGs in that contig"),
        html.Br(),
        html.A(id='download-link', children='Download Protein Fasta File',style={'marginBottom': '1.5em'},
               ),
        ]),
      #html.Div(html.A(id='download-link2', children='Download Nucleotide Fasta File',style={'marginBottom': '1.5em'},
        #))

        # html.Div(id='alignment-viewer-output')

        # html.Div([
        #     dashbio.AlignmentChart(
        #         id='my-alignment-viewer',
        #         extension="clustal",
        #         data=data
        #     ),
        # ])


    ]
)
#########################################################################################################

######### Create callbacks ###########

@app.callback(Output("desc", "children"), [Input("arg", "value")])
def get_desc(desc):
        desctext=deep[deep["#ARG"]==desc][["#ARG","description"]].drop_duplicates()["description"]
        return desctext


@app.callback(Output("graph", "figure"), [Input("arg", "value"),Input("feat","value")])
def make_figure_box(size,feat):
        fig = px.scatter_geo(
        env,
        size=size,
        lat="Latitude [degrees North]",lon="Longitude [degrees East]", color=feat,hover_name="Marine_provinces",projection='equirectangular',
        title=str(size)+" distribution and abundance (RPKG)").for_each_trace(lambda t: t.update(name=t.name.replace(str(feat)+"=","")))
        fig.update_layout(plot_bgcolor="#F9F9F9",paper_bgcolor="#F9F9F9",titlefont={
    "size": 18})
        fig.update_layout(autosize=True)
        return fig

@app.callback(Output("graph2", "figure"), [Input("arg", "value"),Input("feat","value")])
def make_figure(size,feat):

    fig= px.box(
        env,
        x=feat,
        y=size,
        notched=True,
        labels={size:size+"  RPKG"},template='plotly_white',title="ARGs abundance on "+str(feat)+"."
    ).for_each_trace(lambda t: t.update(name=t.name.replace(str(feat)+"=","")))
    fig.update_layout(plot_bgcolor="#F9F9F9",paper_bgcolor="#F9F9F9",titlefont={
    "size": 18})
    fig.update_layout(autosize=True)
    return fig

@app.callback(Output('download-link', 'href'),
              [Input('arg', 'value')])

def update_href(dropdown_value):
    dropdown_value=str(dropdown_value).replace("-","").replace("(","").replace(")","").replace("''","").replace("'","").replace("_","")
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

##
# @app.callback(Output('download-link2', 'href'),
#               [Input('arg', 'value')])

# def update_href2(dropdown_value):
#     dropdown_value=str(dropdown_value).replace("-","").replace("(","").replace(")","").replace("''","").replace("'","").replace("_","")
#     relative_filename = os.path.join(
#         'bit_resistome/ARGs_fastas/nt',
#         '{}.fasta'.format(dropdown_value)
#     )
#     absolute_filename = relative_filename

#     return '/{}'.format(relative_filename)


# @app.server.route('/bit_resistome/ARGs_fastas/nt/<path:path>')
# def serve_static2(path):
#     root_dir = os.getcwd()
#     return flask.send_from_directory(
#         os.path.join(root_dir, 'bit_resistome/ARGs_fastas/nt'), path
#     )

##

@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size"),
     Input('arg','value')])
def update_table(page_current,page_size,arg):
    a=deep[deep["#ARG"]==arg]
    return a.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

@app.callback(
    Output('graph3', 'figure'),
    [Input('arg','value'),
     Input('slider','value')])
def make_fig2(arg,taxlevel):
    levels={1:"phylum",2:"order",3:"class",4:"family",5:"genus",6:"species"}
    a=deep[deep["#ARG"]==arg]
    b=a.groupby(levels[taxlevel]).count()[["#ARG"]]
    b.index = b.index.str.replace("-", "Not Classified").str.replace("0", "Not Classified")
    # not use colors if level is species (too many colors)
    if taxlevel==6:
        fig = go.Figure(px.bar(b.reset_index(),y="#ARG",x=levels[taxlevel],template='plotly_white',title="Number of ARGs found per taxonomic group.").for_each_trace(lambda t: t.update(name=t.name.replace(str(levels[taxlevel])+"=",""))))
    else:
        fig = go.Figure(px.bar(b.reset_index(),y="#ARG",x=levels[taxlevel],template='plotly_white',color=levels[taxlevel],title="Number of ARGs found per taxonomic group.").for_each_trace(lambda t: t.update(name=t.name.replace(str(levels[taxlevel])+"=",""))))

    fig.update_xaxes(title_text=None)
    fig.update_layout(autosize=True,titlefont={
    "size": 18},

    margin=go.layout.Margin(
        b=300
    )
)
    fig.update_layout(plot_bgcolor="#F9F9F9",paper_bgcolor="#F9F9F9")
    return fig

@app.callback(
    Output('graph4', 'figure'),
    [Input('arg','value'),
     Input('env_var','value'),
     Input('feat','value')])
def make_env_fig(arg,env_var2,feat22):
    fig = px.scatter(env, x=arg, y=env_var2,  marginal_y="violin",title="ARG vs. parameters.",
           marginal_x="violin", trendline="ols",template='plotly_white').for_each_trace(lambda t: t.update(name=t.name.replace(str(feat22)+"=","")))
    fig.update_layout(plot_bgcolor="#F9F9F9",paper_bgcolor="#F9F9F9")
    fig.update_layout(autosize=True,titlefont={
    "size": 18},

    )
    return fig


# @app.callback(
#     Output('alignment-viewer-output','children'),
#     [Input('arg', 'value')]
# )
# def alig(arg):
#     dropdown_value = str(arg).replace("-", "").replace("(", "").replace(")", "").replace("''", "").replace(
#         "'", "").replace("_", "")
#     relative_filename = os.path.join(
#         'data/ptn/aligned',
#         '{}.edit.fasta'.format(dropdown_value))
#     with open(relative_filename, 'r') as content_file:
#         data = content_file.read()
#
#     if len(data)==0:
#         return ''
#     else:
#         return dashbio.AlignmentChart(
#
#         data=data,
#         extension="clustal",
#         overview="slider",
#
#
#     )


if __name__ == '__main__':
        app.run_server(debug=True,host='0.0.0.0')
