from flask import Flask, render_template, request
from plots import distplot, mapbox, get_cities, get_states, get_product_categories, get_state_names
from plots import bar_category, bar_time_order, hist_duration, bar_seller, bar_rating

location_lock = 'All'
city_lock = 'All'
state_lock = 'All'
product_lock = 'All'
subject_lock = 'customer'
hue_lock = 'price'

# variable app untuk akses ke Flask
app = Flask(__name__)

# untuk proses panggil template dari masing2 html
@app.route('/')
def home() :
    return render_template('home.html')

@app.route('/plots')
def plots() :
    global location_lock
    global city_lock 
    global state_lock
    global product_lock
    global subject_lock
    global hue_lock
    cities = ['All']
    cities.extend(get_cities())
    states = ['All']
    states.extend(get_states())
    products = ['All']
    products.extend(get_product_categories())
    state_names = get_state_names()

    location_type = 'All'
    subject_selected = 'customer'
    hue_selected = 'price'
    data1 = mapbox()
    data2 = bar_category()
    data2a = bar_rating()
    data3 = bar_time_order()
    data4 = bar_seller('city')
    data5 = bar_seller('state')
    data6 = hist_duration()
    return render_template('plots.html', data1=data1, data2=data2, data2a=data2a, data3=data3, data4=data4, data5=data5, data6=data6, subject_selected=subject_selected,
    hue_selected=hue_selected, cities=cities, states=states, products=products, state_names=state_names, location_type=location_type)

@app.route("/plots" , methods=['GET','POST'])
def test():
    listOfGlobals = globals()
    cities = ['All']
    cities.extend(get_cities())
    states = ['All']
    states.extend(get_states())
    products = ['All']
    products.extend(get_product_categories())
    state_names = get_state_names()

    view = str(request.args.get('view'))
    if (view=="None"):
        city_selected = str(request.form.get('comp_select'))
        state_selected = str(request.form.get('comp_select2'))
        product_selected = str(request.form.get('comp_select3'))
        listOfGlobals['city_lock'] = city_selected
        listOfGlobals['state_lock'] = state_selected
        listOfGlobals['product_lock'] = product_selected
        subject_selected = subject_lock
        hue_selected = hue_lock
    else:
        city_selected = city_lock
        state_selected = state_lock
        product_selected = product_lock
        subject_selected = str(request.form.get('comp_select4'))
        hue_selected = str(request.form.get('comp_select5'))
        listOfGlobals['subject_lock'] = subject_selected
        listOfGlobals['hue_lock'] = hue_selected

    if request.args.get('type')=="Product":
        if product_selected=='All':
            product='none'
        else:
            product = product_selected 
    else:
        product = product_lock
        if product=='All':
            product='none'

    args = str(request.args.get('location'))
    if (args=='None') and (view!='None'):
        args = location_lock
    
    if args=="City":
        if city_selected=='All':
            args = 'All'
        else:
            data1 = mapbox(city_selected, product, subject_selected, hue_selected)
            data2 = bar_category(city_selected)
            data2a = bar_rating(city_selected)
            data3 = bar_time_order(city_selected, product)
            data4 = bar_seller('city',city_selected,product)
            data5 = bar_seller('state',city_selected,product)
            data6 = hist_duration(city_selected,product)
            location_type = 'City'
    elif args=="State":
        if state_selected=='All':
            args = 'All'
        else:
            data1 = mapbox(state_selected, product, subject_selected, hue_selected)
            data2 = bar_category(state_selected)
            data2a = bar_rating(state_selected)
            data3 = bar_time_order(state_selected, product)
            data4 = bar_seller('city',state_selected,product)
            data5 = bar_seller('state',state_selected,product)
            data6 = hist_duration(state_selected,product)
            location_type = 'State'

    if (args=="All"):
        data1 = mapbox('none', product, subject_selected, hue_selected)
        data2 = bar_category()
        data2a = bar_rating()
        data3 = bar_time_order('none',product)
        data4 = bar_seller('city','none',product)
        data5 = bar_seller('state','none',product)
        data6 = hist_duration('none',product)
        location_type = 'All'

    listOfGlobals['location_lock'] = location_type
    return render_template('plots.html', data1=data1, data2=data2, data2a=data2a, data3=data3, data4=data4, data5=data5, data6=data6,cities=cities, states=states, products=products,
                            city_selected=city_selected, state_selected=state_selected, product_selected=product_selected, subject_selected=subject_selected,
                            hue_selected=hue_selected, location_type=location_type, state_names=state_names)

# proses running dari html
if __name__ == '__main__' :
    app.run(debug=True,port=2000)