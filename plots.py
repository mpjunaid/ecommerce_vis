import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly
import pandas as pd
import numpy as np
import json 

df_all = pd.read_csv('df_all.csv')
df_per_order = pd.read_csv('df_per_order.csv')
df_geo_new = pd.read_csv('df_geo_new.csv')
df_geo_new = df_geo_new[df_geo_new['customer_amount']>0]
df_seller = pd.read_csv('df_seller.csv')
df_customer = pd.read_csv('df_customer.csv')
df_duration = pd.read_csv('df_duration.csv')
df_geo_all_lock = df_geo_new.groupby('geolocation_state').mean().reset_index()


with open('mapbox_tkn.txt', 'r') as f: 
    mapbox_key = f.read().strip()

def get_cities():
    dlist = df_geo_new['geolocation_city'].unique().tolist()
    dlist.sort()
    return dlist

def get_states():
    dlist = df_geo_new['geolocation_state'].unique().tolist()
    dlist.sort()
    return dlist

def get_state_names():
    dlist = [
        'All',
        'Acre',
        'Alagaos',
        'Amazonas',
        'Amapa',
        'Bahia',
        'Ceara',
        'Distrito Federal',
        'Espirito Santo',
        'Golas',
        'Maranhao',
        'Minas Gerais',
        'MatoGrosso do Sul',
        'MatoGrosso',
        'Para',
        'Paraiba',
        'Pernambuco',
        'Piaui',
        'Parana',
        'Rio de Jenairo',
        'Rio Grande do Norte',
        'Rondonia',
        'Roraima',
        'Rio Grande do Sul',
        'Santa Catarina',
        'Sergipe',
        'Sao Paulo',
        'Tocantins'
    ]
    return dlist

def get_product_categories():
    dlist = df_all['product_category_name_english'].unique().tolist()
    dlist.sort()
    return dlist

def distplot(col):
    df = data_mobil()
    fig = px.histogram(df, x=col, marginal="rug", hover_data=df.columns)
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def mapbox(location='none',product='none',subject='customer', hue='price'):
    col2s = subject
    if location=='none':
        df_geo_all = df_geo_all_lock
        col1 = 'geolocation_state'
        col2 = col2s + '_state'
        zoom = 3
    elif location in get_cities():
        df_geo_all = df_geo_new[df_geo_new['geolocation_city']==location]
        col1 = 'geolocation_zip_code_prefix'
        col2 = col2s + '_zip_code_prefix'
        zoom = 9
    elif location in get_states():
        df_geo_all = df_geo_new[df_geo_new['geolocation_state']==location]
        col1 = 'geolocation_city'
        col2 = col2s + '_city'
        df_geo_all = df_geo_all.groupby('geolocation_city').mean().reset_index()
        zoom = 6

    if product!='none':
        df_prod = df_all[df_all['product_category_name_english']==product]
        pr_quantity = []
        for item in df_geo_all[col1]:
            if item in df_prod[col2].unique().tolist():
                pr_quantity.append(1)
            else:
                pr_quantity.append(0)

        df_geo_all['pr_quantity'] = pr_quantity
        df_geo_all = df_geo_all[df_geo_all['pr_quantity']>0]
    
    if hue=='price':
        color_col = 'mean_order_price'
        df_geo_all = df_geo_all[df_geo_all[color_col] > 0]
        seq_col = px.colors.sequential.Burg
    elif hue=='rating':
        color_col = 'review_score'
        df_geo_all.dropna(inplace=True)
        seq_col = px.colors.sequential.RdBu


    fig = px.scatter_mapbox(df_geo_all, lat="geolocation_lat", lon="geolocation_lng", zoom=zoom,
                        size=col2s+"_amount", color=color_col, color_continuous_scale=seq_col,
                        hover_name=col1, width=750, height=600)

    fig.update_layout(title='Customer distribution per location', mapbox_style="light", mapbox_accesstoken=mapbox_key, margin = go.layout.Margin(l=0, r=0, b=0, t=40))
    # fig.show()
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def bar_seller(get='city',location='none',product='none'):
    if location=='none':
        df_loc = df_all
        ss = ''
    elif location in get_cities():
        df_loc = df_all[df_all['customer_city']==location]
        ss = ' in ' + location.capitalize()
    elif location in get_states():
        df_loc = df_all[df_all['customer_state']==location]
        ss = ' in ' + location

    ss2=''
    if product!='none':
        df_loc = df_loc[df_loc['product_category_name_english']==product]
        ss2=' for '+product.replace('_',' ').capitalize()

    df_res = pd.DataFrame(df_loc['seller_'+get].value_counts()).reset_index().rename(columns={'seller_'+get:'freq','index':'seller_'+get})
    
    fig = px.bar(df_res.head(5).iloc[::-1], y='seller_'+get, x='freq', orientation='h', width=325, height=125)
    fig.update_xaxes(title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(title='Top seller '+get+' origin'+ss+ss2, title_font_size=12, font_size=10 , margin = go.layout.Margin(l=0, r=0, b=0, t=30) )
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def bar_rating(location='none'):
    if location=='none':
        df_loc = df_all
        ss = ''
    elif location in get_cities():
        df_loc = df_all[df_all['customer_city']==location]
        ss = ' in ' + location.capitalize()
    elif location in get_states():
        df_loc = df_all[df_all['customer_state']==location]
        ss = ' in ' + location
    
    df_review = df_loc.groupby('product_category_name_english').mean().sort_values('review_score',ascending=False)[['review_score']].reset_index()
    df_review_amount = df_loc.groupby('product_category_name_english').count().sort_values('order_id',ascending=False)[['order_id']].reset_index().rename(columns={'order_id':'review_amount'})
    df_review = df_review.set_index('product_category_name_english').join(df_review_amount.set_index('product_category_name_english')).reset_index()

    m = df_review['review_amount'].quantile(q=0.25)
    c = df_review['review_score'].mean()
    df_review['WR'] = df_review.apply(lambda x: (x['review_score']*(x['review_amount']/(x['review_amount']+m))) + (c*(m/(x['review_amount']+m))), axis=1)
    df_review = df_review.sort_values('WR',ascending=False).head(5)

    fig = px.bar(df_review.iloc[::-1], y='product_category_name_english', x='WR', orientation='h', width=325, height=125, hover_data=['review_amount','review_score'])
    fig.update_xaxes(title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(title='Highest Rating Product Categories'+ss, title_font_size=11, font_size=10 , margin = go.layout.Margin(l=0, r=0, b=0, t=18) )
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def bar_category(location='none'):
    if location=='none':
        df_loc = df_all
        ss = ''
    elif location in get_cities():
        df_loc = df_all[df_all['customer_city']==location]
        ss = ' in ' + location.capitalize()
    elif location in get_states():
        df_loc = df_all[df_all['customer_state']==location]
        ss = ' in ' + location

    df_loc = df_loc.groupby('product_category_name_english').count().sort_values('order_id',ascending=False).head(5)[['order_id']].reset_index()
    df_loc.rename(columns={'order_id':'quantity'},inplace=True)
    fig = px.bar(df_loc.iloc[::-1], y='product_category_name_english', x='quantity', orientation='h', width=325, height=125)
    fig.update_xaxes(title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(title='Most Popular Product Categories'+ss, title_font_size=11, font_size=10 , margin = go.layout.Margin(l=0, r=0, b=0, t=18) )
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json


def bar_time_order(location='none', product='none'):
    if location=='none':
        df_loc = df_per_order
        ss = ''
    elif location in get_cities():
        df_loc = df_per_order[df_per_order['customer_city']==location]
        ss = ' in ' + location.capitalize()
    elif location in get_states():
        df_loc = df_per_order[df_per_order['customer_state']==location]
        ss = ' in ' + location

    ss2 = ''
    if product!='none':
        ss2 = ' of '+ product.replace("_"," ").capitalize()
        df_prod = df_all[df_all['product_category_name_english']==product]
        pr_quantity = []
        for item in df_loc['customer_zip_code_prefix']:
            if item in df_prod['customer_zip_code_prefix'].unique().tolist():
                pr_quantity.append(1)
            else:
                pr_quantity.append(0)
            # pr_quantity.append(len(df_prod[(df_prod['customer_zip_code_prefix']==item)]))
        df_loc['pr_quantity'] = pr_quantity
        df_loc = df_loc[df_loc['pr_quantity']>0]

    fig = px.histogram(df_loc, x="order_date", width=375, height=250)
    fig.update_traces(xbins_size="M1")
    fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y",title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(bargap=0.1, title='Amount of Orders'+ss2+' over time'+ss, title_font_size=12, font_size=12 , margin = go.layout.Margin(l=0, r=0, b=0, t=40))
    # fig.add_trace(go.Scatter(mode="markers", x=df_all["order_purchase_date"], name="daily"))
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def hist_duration(location='none',product='none'):
    new_df = df_duration
    ss = ''
    if location in get_cities():
        new_df = new_df[new_df['customer_city']==location]
        ss = ' in ' + location.capitalize()
    elif location in get_states():
        new_df = new_df[new_df['customer_state']==location]
        ss = ' in ' + location

    ss2=''
    new_df.dropna(inplace=True)
    # if product!='none':
    #     df_all[['order_id','product_category_name_english']]
    #     new_df = new_df.set_index('order_id').join(df_all[[]].set_index('order_id')).reset_index()
    try:
        fig = ff.create_distplot([new_df['order_duration_day'].values,new_df['estimated_duration_day'].values],['actual','estimated'], show_rug=False)
    # fig.update_layout(bargap=0.1, title='Amount of Orders'+ss2+' over time'+ss, title_font_size=12, font_size=12 , margin = go.layout.Margin(l=0, r=0, b=0, t=40))
        fig.update_layout(title='Delivery-time distribution'+ss2+ss+' (days)', title_font_size=12, font_size=11, margin = go.layout.Margin(l=0, r=0, b=0, t=40), width=325, height=200)
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ))
    except:
        fig = px.histogram(pd.DataFrame([np.nan]))
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        fig.update_layout(title='Delivery-time distribution'+ss2+ss+' (days)', title_font_size=12, font_size=11, margin = go.layout.Margin(l=0, r=0, b=0, t=40), width=325, height=200)
    fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json
    # return 

# def bar_time_order_state(state, product='none'):
#     if state=='null':
#         df_state = df_per_order
#         ss = ''
#     else:
#         df_state = df_per_order[df_per_order['customer_state']==state]
#         ss = ' in ' + state

#     ss2=''
#     if product!='none':
#         ss2 = ' of '+ product.replace("_"," ").capitalize()
#         df_prod = df_all[df_all['product_category_name_english']==product]
#         pr_quantity = []
#         for item in df_state['customer_zip_code_prefix']:
#             if item in df_prod['customer_zip_code_prefix'].unique().tolist():
#                 pr_quantity.append(1)
#             else:
#                 pr_quantity.append(0)
#             # pr_quantity.append(len(df_prod[(df_prod['customer_zip_code_prefix']==item)]))
#         df_state['pr_quantity'] = pr_quantity
#         df_state = df_state[df_state['pr_quantity']>0]

#     fig = px.histogram(df_state, x="order_date", width=450, height=300)
#     fig.update_traces(xbins_size="M1")
#     fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y")
#     fig.update_yaxes(title='', visible=True, showticklabels=True)
#     fig.update_layout(bargap=0.1,title='Amount of Orders'+ss2+' over time'+ss, title_font_size=12, font_size=12 , margin = go.layout.Margin(l=0, r=0, b=0, t=40))
#     # fig.add_trace(go.Scatter(mode="markers", x=df_all["order_purchase_date"], name="daily"))
#     fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
#     return fig_json



# def mapbox_city(city, product='none'):
#     df_cities = df_geo_new[df_geo_new['geolocation_city']==city]

#     if product!='none':
#         df_prod = df_all[df_all['product_category_name_english']==product]
#         pr_quantity = []
#         for item in df_cities['geolocation_zip_code_prefix']:
#             if item in df_prod['customer_zip_code_prefix'].unique().tolist():
#                 pr_quantity.append(1)
#             else:
#                 pr_quantity.append(0)

#             # pr_quantity.append(len(df_prod[(df_prod['customer_zip_code_prefix']==item)]))

#         df_cities['pr_quantity'] = pr_quantity
#         df_cities = df_cities[df_cities['pr_quantity']>0]

#     fig = px.scatter_mapbox(df_cities, lat="geolocation_lat", lon="geolocation_lng",
#                         zoom=9, size="customer_amount", color='mean_order_price', color_continuous_scale=px.colors.sequential.Burg,
#                         hover_name='geolocation_zip_code_prefix', width=1000, height=650, hover_data=['geolocation_state','geolocation_city'])

#     fig.update_layout(title='Order distribution per location', mapbox_style="light", mapbox_accesstoken=mapbox_key, margin = go.layout.Margin(l=0, r=0, b=0, t=40))
#     fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
#     return fig_json

# def mapbox_state(state, product='none'):
#     df_states = df_geo_new[df_geo_new['geolocation_state']==state]

#     if product!='none':
#         df_prod = df_all[df_all['product_category_name_english']==product]
#         pr_quantity = []
#         for item in df_states['geolocation_zip_code_prefix']:
#             if item in df_prod['customer_zip_code_prefix'].unique().tolist():
#                 pr_quantity.append(1)
#             else:
#                 pr_quantity.append(0)
#             # pr_quantity.append(len(df_prod[(df_prod['customer_zip_code_prefix']==item)]))
#         df_states['pr_quantity'] = pr_quantity
#         df_states = df_states[df_states['pr_quantity']>0]

#     fig = px.scatter_mapbox(df_states, lat="geolocation_lat", lon="geolocation_lng",
#                         zoom=5, size="customer_amount", color='mean_order_price', color_continuous_scale=px.colors.sequential.Burg,
#                         hover_name='geolocation_zip_code_prefix', width=1000, height=600, hover_data=['geolocation_state','geolocation_city'])

#     fig.update_layout(title='Order distribution per location', mapbox_style="light", mapbox_accesstoken=mapbox_key, margin = go.layout.Margin(l=0, r=0, b=0, t=40))
#     fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
#     return fig_json


# def bar_state(state):
#     if state=='null':
#         df_state = df_all
#         ss = ''
#     else:
#         df_state = df_all[df_all['customer_state']==state]
#         ss = ' in ' + state
#     df_state = df_state.groupby('product_category_name_english').count().sort_values('order_id',ascending=False).head(5)[['order_id']].reset_index()
#     df_state.rename(columns={'order_id':'quantity'},inplace=True)
#     fig = px.bar(df_state.iloc[::-1], y='product_category_name_english', x='quantity', orientation='h', width=450, height=200)
#     fig.update_xaxes(title='', visible=True, showticklabels=True)
#     fig.update_yaxes(title='', visible=True, showticklabels=True)
#     fig.update_layout(title='Most Popular Product Category'+ss, title_font_size=12, font_size=12 , margin = go.layout.Margin(l=0, r=0, b=0, t=40) )
#     fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
#     return fig_json


# def bar_stats(location='none',product='none'):
#     if product=='none':
#         ss2 = ''
#         if location=='none':
#             odr = len(df_all['order_id'].unique())
#             sel = len(df_seller)
#             cus = len(df_customer)
#             ss = ''
#         elif location in get_cities():
#             odr = len(df_all[df_all['customer_city']==location]['order_id'].unique())
#             sel = len(df_seller[df_seller['seller_city']==location])
#             cus = len(df_customer[df_customer['customer_city']==location])
#             ss = ' in ' + location.capitalize()
#         elif location in get_states():
#             odr = len(df_all[df_all['customer_state']==location]['order_id'].unique())
#             sel = len(df_seller[df_seller['seller_state']==location])
#             cus = len(df_customer[df_customer['customer_state']==location])
#             ss = ' in ' + location
#     else:
#         ss2 = ' of '+product.replace('_',' ').capitalize()
#         if location=='none':
#             odr = len(df_all[df_all['product_category_name_english']==product]['order_id'].unique())
#             sel = len(df_all[df_all['product_category_name_english']==product]['seller_id'].unique())
#             cus = len(df_all[df_all['product_category_name_english']==product]['customer_id'].unique())
#             ss = ''
#         elif location in get_cities():
#             odr = len(df_all[(df_all['customer_city']==location)&(df_all['product_category_name_english']==product)]['order_id'].unique())
#             sel = len(df_all[(df_all['seller_city']==location)&(df_all['product_category_name_english']==product)]['seller_id'].unique())
#             cus = len(df_all[(df_all['customer_city']==location)&(df_all['product_category_name_english']==product)]['customer_id'].unique())
#             ss = ' in ' + location.capitalize()
#         elif location in get_states():
#             odr = len(df_all[(df_all['customer_state']==location)&(df_all['product_category_name_english']==product)]['order_id'].unique())
#             sel = len(df_all[(df_all['seller_state']==location)&(df_all['product_category_name_english']==product)]['seller_id'].unique())
#             cus = len(df_all[(df_all['customer_state']==location)&(df_all['product_category_name_english']==product)]['customer_id'].unique())
#             ss = ' in ' + location


#     obj = ['Orders','Customers','Sellers']
#     val = [odr, cus, sel]
#     df_loc = pd.DataFrame([obj,val]).transpose()

#     fig = px.bar(df_loc.iloc[::-1], x=1, y=0, orientation='h', width=265, height=200)
#     fig.update_xaxes(title='', visible=True, showticklabels=True)
#     fig.update_yaxes(title='', visible=True, showticklabels=True)
#     fig.update_layout(title='Amounts of data'+ss2+ss, title_font_size=12, font_size=12 , margin = go.layout.Margin(l=0, r=0, b=0, t=30) )
#     fig_json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
#     return fig_json
