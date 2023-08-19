from django.shortcuts import render
from bokeh.plotting import figure, output_file, show

from bokeh.layouts import grid, row, column
from bokeh.models import ColumnDataSource, CategoricalColorMapper, annotations, LinearColorMapper, HoverTool, BooleanFilter, CDSView, Select, CustomJS, LinearAxis, Legend, LegendItem
from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter
from bokeh.plotting import figure, output_notebook, show, output_file, save
from bokeh.transform import linear_cmap
from bokeh.models import ColorBar

colors = ["#6EC8BE","#BE2369","#FFC30F","#694691","#EB1E23","#7682A4","#373C50","#A7DDD8",]

from bokeh.embed import components
import pandas as pd

# Create your views here.
def homepage(request):
    # data was previously manipulated to generate html strings of png images inserted directly into pandas df
    df=pd.read_csv("/home/apaulson/akpau/Repos/bokeh_django/bokeh_django/bokehsite/data/for_bokeh_test.csv")
    # standalone bokeh code
    x = 'x'
    y = 'y'
    x2='x2'
    y2='y2'
    color = 'lib'

    hover = HoverTool(line_policy='interp', point_policy='follow_mouse', attachment='vertical')

    hover.tooltips = """
        <div>
            <div>
                @mol_html{safe}<br>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">@Compound: @lib</span><br>
                <span style="font-size: 12px;">SARS IC50 (uM): @IC50_avg_SARS</span><br>
                <span style="font-size: 12px;">MERS IC50 (uM): @IC50_avg_MERS</span><br>

            </div>
        </div>
    """

    # Shared source
    source = ColumnDataSource(df)

    # create figure & colors
    fig = figure(title="Explore SARS/MERS MPro DR molecules",  height=400,
                 sizing_mode="stretch_width",
                 tools='box_select,lasso_select,tap,pan,wheel_zoom,box_zoom,save,reset,help')
    fig.add_tools(hover)
    colormapper = CategoricalColorMapper(factors=df[color].value_counts().index, palette=colors)
    fig.scatter(x=x, y=y, source=source, size='marker_size', color={'field':color, 'transform':colormapper}, muted_alpha=0.2,legend_field=color)
    fig.xaxis.axis_label='cluster'
    fig.yaxis.axis_label='pIC50_SARS'

    # create legend
    legend1=fig.legend[0]

    event_radius_dummy_1 = fig.circle(1,1,radius=0,fill_alpha=0.0, line_color='black', name='event_radius_dummy_1')

    legend2 = Legend(items=[
    LegendItem(label='MERS hit', renderers=[event_radius_dummy_1])],
    location=(95,50), label_standoff=5, label_height=3)

    legend3 = Legend(items=[
    LegendItem(label='not MERS hit', renderers=[event_radius_dummy_1])],
    location=(195,25), label_standoff=2)

    fig.add_layout(legend1, 'left')
    fig.add_layout(legend2, 'left')
    fig.add_layout(legend3, 'left')

    size_list = [30, 30,12]
    index_list = [0,1,2]

    for index, size in zip(index_list, size_list):
        fig.legend[index].glyph_height = size
        fig.legend[index].glyph_width = size
        fig.legend[index].padding = 0
        fig.legend[index].margin = 0
        fig.legend[index].border_line_alpha = 0
        fig.legend[index].background_fill_alpha = 0


    # fig.min_border_top = 75
    # fig.min_border_left = 150
    # fig.min_border_right = 150

    # create Select menus for x and y axes
    options = ["pIC50_avg_MERS","pIC50_avg_SARS","IC50_avg_MERS","IC50_avg_SARS","cluster"]
    selx=Select(title='X axis:', value='cluster', options=options, width=300)
    sely=Select(title='Y axis:', value='pIC50_avg_SARS', options=options, width=300)

    # define a callback function to update the plot when the Select widget values change
    # I Cannot get this to work if I try to update both axes in the same callback.
    # Only referring to cb_obj.value works, for some reason if you pass the
    # Select object as an arg, accessing that object or value does not work.
    callbackx = CustomJS(args=dict(source=source, xaxis=fig.xaxis[0]),
                        code="""
                            source.data['x'] = source.data[cb_obj.value];
                            source.change.emit();
                            xaxis.axis_label=cb_obj.value;
                        """)
    callbacky = CustomJS(args=dict(source=source, yaxis=fig.yaxis[0]),
                        code="""
                            source.data['y'] = source.data[cb_obj.value];
                            source.change.emit();
                            yaxis.axis_label=cb_obj.value;
                        """)
    # add the callback function to the Select widgets
    selx.js_on_change('value', callbackx)
    sely.js_on_change('value', callbacky)

    # For HTML in DataTable
    html_template = HTMLTemplateFormatter(template='<%= value %>')

    columns = [
               TableColumn(field='lib', title='Library', width=1),
               TableColumn(field='cluster', title='cluster', width=1),
               TableColumn(field="Compound", title='SMDC ID', width=1),
               TableColumn(field="mol_html", formatter=html_template, title='Mol', width=100),
               TableColumn(field="curve_html", formatter=html_template, title='Curves', width=200),
               TableColumn(field="curve_repeat_html", formatter=html_template, title='Repeat curves', width=200),
               TableColumn(field='IC50_avg_MERS', title='IC50_MERS_avg_uM', width=1),
               TableColumn(field='IC50_avg_SARS', title='IC50_SARS_avg_uM', width=1),
               TableColumn(field='pIC50_avg_MERS', title='pIC50_MERS_avg', width=1),
               TableColumn(field='pIC50_avg_SARS', title='pIC50_SARS_avg', width=1),
               TableColumn(field='hitc_MERS', title='MERS_hitc', width=1),
               # TableColumn(field='hitc_repeat_MERS', title='MERS_hitc_rep'),
               TableColumn(field='hitc_SARS', title='SARS_hitc', width=1),
               # TableColumn(field='hitc_repeat_SARS', title='SARS_hitc_rep'),
               # TableColumn(field='MolWt', title='MolWt', ),
               # TableColumn(field='NumHDonors', title='NumHDon'),
               # TableColumn(field='NumHAcceptors', title='NumHAcc'),
               # TableColumn(field='MolLogP', title='MolLogP'),
               # TableColumn(field='HeavyAtomCount', title='HeavAtmCt'),
               # TableColumn(field='NumRotatableBonds', title='NumRotBonds'),
               # TableColumn(field='TPSA', title='TPSA'),
               # TableColumn(field='FractionCSP3', title='FracCSP3')
              ]

    table = DataTable(source=source, columns=columns, row_height=200,
                      sizing_mode='stretch_width',
                      selectable='checkbox',
                      height=600,
                      # width=1500,
                      # autosize_mode='fit_columns'
                     )

    # Show
    selectors = row(selx,sely)
    g = column(selectors, fig, table,
               sizing_mode="stretch_width"
              )
    script, div = components(g)
    # script_sel, div_sel = components(selectors)
    # script_fig, div_fig = components(fig)
    # script_table, div_table = components(table)

    return render(request, 'pages/base.html', {'script':script, 'div':div}
    # {'script_sel':script_sel, 'div_sel':div_sel,
    # 'script_fig':script_fig, 'div_fig':div_fig,
    # 'script_table':script_table, 'div_table':div_table
    # }
                 )
