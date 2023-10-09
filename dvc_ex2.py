import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_file, save, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter, \
    HoverTool, LinearAxis, NumeralTickFormatter, Range1d, RangeTool


# The weekly stock data of META, AAPL, GOOGL, MSFT, AMZN (MAGMA) from 1/1/2019 to 27/12/2022
stock_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM1scE44za7xyuheW_FrUkdSdOKipDgDOWa_03ixmJCWK_ReSqhjzax66nNHyDKARXWIXgFI_EW9X/pub?gid=1661368486&single=true&output=csv'
stock = pd.read_csv(stock_url)

# The financial metrics 'PE Ratio' and 'EPS Growth' of MAGMA from 2019 Q1 to 2022 Q4
metrics_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRDaf4y17OWjQqxODuxA4q4hsvXRkSqN0na1KtTIpvOZUdc7xHbrkhcygFfDIyVQWI2UbC3YcKUbser/pub?gid=981872466&single=true&output=csv'
metrics = pd.read_csv(metrics_url)

stock['Date'] = pd.to_datetime(stock['Date'])
metrics['Quarter Ended'] = pd.to_datetime(metrics['Quarter Ended'])

#  function that create a candlestick chart for a company
def create_candlestick_chart(symbol):

    source = ColumnDataSource(data=stock[stock['Symbol']==symbol])

    p = figure(
        width=1000,
        height=500,
        title=symbol,
        # Specify the x range to be (min date, max date)
        # so that you can refer to this range in other plots
        x_range=(min(source.data['Date']),max(source.data['Date'])),
        # Set the x axis to show date time
        x_axis_type='datetime',
        # Put the x axis to be at the top of the plot
        x_axis_location='above',
        background_fill_color = '#fbfbfb',
        tools='pan,box_select, zoom_in, zoom_out, save, reset',
        toolbar_location='right')

    p.xgrid.grid_line_color='#e5e5e5'
    p.ygrid.grid_line_alpha=0.5
    p.xaxis.major_label_text_font_size = '10px'
    p.yaxis.axis_label = 'Stock Price in USD'
    p.yaxis.formatter = NumeralTickFormatter(format='0.0')

    p.y_range.start = 0.9 * min(source.data['Low'])
    p.y_range.end = 1.1 * max(source.data['High'])

    inc = [True if Open < Close else False for Open, Close in zip(source.data['Open'], source.data['Close'])]
    dec = [True if Open > Close else False for Open, Close in zip(source.data['Open'], source.data['Close'])]

    inc_view = CDSView(filter=BooleanFilter(inc))
    dec_view = CDSView(filter=BooleanFilter(dec))

    w = 7*24*60*60*1000

    stock_segment = p.segment(
        source.data['Date'],
        source.data['High'],
        source.data['Date'],
        source.data['Low'],
        color='black',
        width=0.8)

    stock_inc = p.vbar(x='Date',
                       top='Close',
                       bottom='Open',
                       width=0.9*w,
                       fill_color='green',
                       line_color='green',
                       source=source,
                       view=inc_view)

    stock_dec = p.vbar(x='Date',
                       top='Open',
                       bottom='Close',
                       width=0.9*w,
                       fill_color='red',
                       line_color='red',
                       source=source,
                       view=dec_view)

    y_volume = source.data['Volume']
    p.extra_y_ranges['Volume'] = Range1d(0, 1.1*max(y_volume))

    y_volume_axis = LinearAxis(y_range_name='Volume', axis_label='Volume', formatter=NumeralTickFormatter(format="0a"))
    p.add_layout(y_volume_axis, 'right')

    stock_volume = p.vbar(x='Date',
                          top='Volume',
                          bottom=0,
                          width= 0.25*w,
                          fill_color='#dfe1e6',
                          line_color='#dfe1e6',
                          alpha = 0.9,
                          source = source,
                          level='underlay',
                          y_range_name='Volume')


    hover_stock = HoverTool()
    hover_stock.tooltips=[('Date', '@Date{%F}'),
                          ('Open', '@Open{0.00}'),
                          ('Close', '@Close{0.00}'),
                          ("High", '@High{0.00}'),
                          ('Low', '@Low{0.00}'),
                          ('Volume', '@Volume')]

    hover_stock.formatters= {'@Date': 'datetime'}
    hover_stock.renderers = [stock_inc, stock_dec, stock_volume]
    p.add_tools(hover_stock)
    p.output_backend = 'svg'

    return p

def add_metrics_plot(main_plot):

    p = main_plot
    symbol = p.title.text
    source = ColumnDataSource(data=metrics[metrics['Symbol'] == symbol])

    y_pe = source.data['PE Ratio']
    y_eps = source.data['EPS Growth']

    p.extra_y_ranges['PE Ratio'] = Range1d(0.9 * min(y_pe), 1.1 * max(y_pe))
    p.extra_y_ranges['EPS Growth'] = Range1d(0.9 * min(y_eps), 1.1 * max(y_eps))
    y_pe_axis = LinearAxis(y_range_name='PE Ratio',axis_label = 'PE Ratio')
    y_eps_axis = LinearAxis(y_range_name='EPS Growth',axis_label = 'EPS Growth')
    #p.add_layout(y_pe_axis, 'right')
    #p.add_layout(y_eps_axis, 'right')

    pe_l = p.line( x='Quarter Ended',
                   y='PE Ratio',
                   line_width=1,
                   line_color='#292b30',
                   line_alpha=0.3,
                   line_dash='dotted',
                   source=source,
                   y_range_name='PE Ratio',
                   legend_label='PE Ratio')

    pe_c = p.circle(x='Quarter Ended',
                    y='PE Ratio',
                    size=6,
                    fill_color='gray',
                    line_color='#292b30',
                    fill_alpha=0.3,
                    line_alpha=0.3,
                    source=source,
                    y_range_name='PE Ratio',
                    legend_label='PE Ratio')

    eps_l = p.line(x='Quarter Ended',
                   y='EPS Growth',
                   line_width=1,
                   line_color='#91949c',
                   line_alpha=0.8,
                   line_dash='dotted',
                   source=source,
                   y_range_name='EPS Growth',
                   legend_label='EPS Growth')

    eps_c = p.circle(x='Quarter Ended',
                     y='EPS Growth',
                     size=6,
                     fill_color='white',
                     fill_alpha=1,
                     line_alpha=0.8,
                     line_color="#91949c",
                     source=source,
                     y_range_name='EPS Growth',
                     legend_label='EPS Growth')

    p.legend.click_policy='hide'
    p.legend.label_height = 20
    p.legend.glyph_height = 20
    p.legend.location = 'top_left'
    p.legend.orientation = 'horizontal'
    p.legend.background_fill_alpha = 0
    p.legend.border_line_alpha = 0
    p.legend.label_text_font_size = '10px'
    p.legend.glyph_width = 16
    p.output_backend = 'svg'
    ## 3.4: Add a hovertool for the scatter glyphs
    metrics_hover = HoverTool()
    metrics_hover.tooltips=[('Quarter Ended', '@{Quarter Ended}{%F}'),
                            ('EPS Growth', '@{EPS Growth}{0.0000}'),
                            ('PE Ratio', '@{PE Ratio}{0.00}')]

    metrics_hover.formatters={'@{Quarter Ended}': 'datetime'}
    metrics_hover.mode='mouse'
    metrics_hover.renderers = [pe_c, eps_c, pe_l, eps_l]
    p.add_tools(metrics_hover)

    return p

def add_select_range(main_plot):

    p = main_plot
    symbol = p.title.text
    source = ColumnDataSource(data=stock[stock['Symbol'] == symbol])

    select = figure(width=1000,
                    height=130,
                    x_range=(min(source.data['Date']), max(source.data['Date'])),
                    x_axis_type='datetime',
                    y_axis_type=None,
                    tools="",
                    x_axis_location='below',
                    background_fill_color='#efefef',
                    toolbar_location=None)

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = 'navy'
    range_tool.overlay.fill_alpha = 0.2

    select.line(x='Date',
                y='Low',
                line_width=1,
                line_color='blue',
                alpha=0.6,
                source=source)

    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool
    select.output_backend = 'svg'

    _p = column(p, select)

    return _p

p = create_candlestick_chart('AAPL')
p = add_metrics_plot(p)
p = add_select_range(p)

output_file('dvc_ex2.html')
save(p)
