# Activate the bokeh environment
# You may refer to:
# bokeh tutorial 00 - Introduction and Setup - Getting set up
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, NumeralTickFormatter
from bokeh.layouts import gridplot
from bokeh.transform import factor_cmap
from bokeh.models.annotations import Label
from bokeh.palettes import Blues3 as palette
import ssl

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Task 1: Prepare the Data

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQdNgN-88U31tk1yQytaJdmoLrxuFn1LnbwTubwCd8se2aHh8656xLLHzxHSoiaXMUu8rIcu6gMj5Oq/pub?gid=1242961990&single=true&output=csv'
MAGMA_financials = pd.read_csv("MAGMA_financials.csv", header=0, sep=';')

subset = ['Selling, General & Admin', 'Research & Development', 'Operating Expenses', 'Operating Income']
years = ['2019', '2020', '2021', '2022']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

# this creates [ ('2019', 'Q1', 'item 1'),  ('2019', 'Q1', 'item 2'), ...]
x = [(year, quarter, item) for year in years for quarter in quarters for item in subset]


## 1.4: Use ColumnDataSource to generate data sources

def create_source(symbol):
    data = MAGMA_financials[MAGMA_financials['Symbol'] == symbol][subset]
    df = pd.DataFrame(data)
    y = list(df.to_numpy().flatten())
    x_label = 16 * subset

    return ColumnDataSource(data=dict(x=x, y=y, label=x_label))


symbols = MAGMA_financials.Symbol.unique()
sources = {symbol: create_source(symbol) for symbol in symbols}


def draw_bar_chart(symbol):
    p = figure(
        x_range=FactorRange(*x),
        title=symbol,
        width=1200,
        height=350,
        tools=''
    )

    # Hide the x grid line
    p.xgrid.grid_line_color = None
    # Pad the x range
    p.x_range.range_padding = 0.1
    # Hide the labels on x axis
    p.xaxis.major_label_text_font_size = "0px"
    # Hide the x major tick line
    p.xaxis.major_tick_line_color = None
    # Set the y axis label to 'millions USD'
    p.yaxis.axis_label = 'millions USD'
    # Use NumeralTickFormatter to a comma as the thousand separator
    p.yaxis.formatter = NumeralTickFormatter(format=",")

    ## 2.2: Configure the bar glyphs

    p.vbar(
        # Draw the bars from the source corresponding to the company symbol
        x="x", top="y", width=0.9,
        source=sources[symbol],
        legend_group='label',
        line_color="white",

        fill_color=factor_cmap(
            "x", palette=palette,
            factors=subset,
            start=2, end=3
        )
    )

    ## 2.3: Add a hover tool

    p.add_tools(HoverTool(tooltips=[('','@x: @y{,000}')],
    ))

    ## 2.4: Add a legend

    p.legend.label_text_font_size = '10pt'
    p.legend.label_height = 20
    p.legend.glyph_height = 20
    p.legend.glyph_width = 20

    # Set the legend orientation and location
    p.legend.orientation = "horizontal"
    p.legend.location = "top_left"

    # Set the output_backend to 'svg' to preserve the resolution when zooming in
    p.output_backend = "svg"

    return p


def make_label(time, number):
    label = Label(
        # Set the postion of the label (x, y) using screen units
        x=1000,
        y=100,
        x_units="screen",
        y_units="screen",

        # Set the text content, font size, color, align, background
        text=f'{time}\nlayoffs\n{number}',
        text_font_size="10px",
        text_font_style="italic",
        text_color="gray",
        text_align="right",
        background_fill_color="white",
        background_fill_alpha=0.8
    )

    return label


# Make a dictionary of the text labels with the provided time and number information

labels = {
    'AMZN': make_label('Jan 2023', '18,000'),
    'META': make_label('Nov 2022', '11,000'),
    'GOOGL': make_label('Jan 2023', '12,000'),
    'MSFT': make_label('Jan 2023', '10,000'),
}

# Draw a bar chart with label
p_META = draw_bar_chart('META')
p_META.add_layout(labels['META'])

p_GOOGL = draw_bar_chart('GOOGL')
p_GOOGL.add_layout(labels['GOOGL'])

p_MSFT = draw_bar_chart('MSFT')
p_MSFT.add_layout(labels['MSFT'])

p_AMZN = draw_bar_chart('AMZN')
p_AMZN.add_layout(labels['AMZN'])

p = gridplot([[p_AMZN, p_MSFT], [p_GOOGL, p_META]], toolbar_location=None)

output_file('dvc_ex1.html')
save(p)
