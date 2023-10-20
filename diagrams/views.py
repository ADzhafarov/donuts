from django.shortcuts import HttpResponse, render
from jinja2 import Environment, PackageLoader, select_autoescape
from diagrams.models import Datasets, Molecules
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import io
import base64



def donuts(request):
    env = Environment(
        loader=PackageLoader("diagrams"),
        autoescape=select_autoescape()
    )
    context = {}

    # extracing all datasamples names to render dropdown list in html template
    datasets = [dataset.name for dataset in list(Datasets.objects.all())]
    context['datasets'] = datasets


    if 'sample' in request.GET.keys():
        #if request url specifies sample name via query params render matplotlib pie-chart 

        #flag for jinja conditions in template
        context['sample'] = True


        dataset = request.GET["sample"]
        #if there's no such sample stored in database, return 404
        if dataset not in datasets:
            return render(request, '404.html')
        
        #calculating aggregate functions of interest: abundances and unique moleculs grouped by RNA type
        df = pd.DataFrame(list(Molecules.objects.filter(dataset=dataset).values('rna_type', 'unnormalized_read_counts')))
        agg_func_with_abundances = {
            'unnormalized_read_counts': ['sum']
        }
        agg_func_unique = {
            'unnormalized_read_counts': ['count']
        }
        df_stat_with_abundances = df.groupby(['rna_type']).agg(agg_func_with_abundances)
        df_stat_unique = df.groupby(['rna_type']).agg(agg_func_unique)

        #converting results into lists
        labels = df_stat_with_abundances.index.values.tolist()
        abundances = df_stat_with_abundances["unnormalized_read_counts"].values.reshape(1, -1).tolist()[0]
        unique_values = df_stat_unique["unnormalized_read_counts"].values.reshape(1, -1).tolist()[0]

        #generating pie-charts based on calculated aggregate functions
        plot = base64_plot(labels, abundances, unique_values, dataset)

        #passing results to jinja environment to use it in html template
        context['plot'] = plot
        context['samplename'] = dataset
    else:
        context['sample'] = False
        context['samplename'] = ''
    
    #rendering template
    template = env.get_template("donuts.html")
    return HttpResponse(template.render(**context))


def base64_plot(x, y, z, dataset):

    #generating different colors based on the number of types of RNA found in samle
    num_groups = len(x)
    colors = [plt.cm.viridis(i / num_groups) for i in range(num_groups)]

    #initializing the figure with grid
    fig = plt.figure(figsize=(14, 8))
    gs = GridSpec(1, 3, width_ratios=[3, 3, 1])

    #adding 2 pie-charts to the figure
    wedges1 = add_pie_chart(gs, fig, x, y, colors, '% sequences/molecules across types\n\n', 0)
    wedges2 = add_pie_chart(gs, fig, x, z, colors, '% \'unique\' sequences/molecule across types\n\n', 1)

    #addomg legend to the figure
    ax = fig.add_subplot(gs[2])
    ax.legend(wedges2, x, title='Legend', loc='center', bbox_to_anchor=(0.5, 0.5))
    ax.set_axis_off()
    
    #setting a title to the figure
    plt.suptitle('Sample: ' + dataset, fontsize=16)

    #obtaining a png-file for the diagram
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    #returning b64-string for the png
    return base64.b64encode(img.read()).decode()


def add_pie_chart(gs, fig, x, y, colors, title, position):

    #making a hole in pir-chart
    wedgeprops = {
        "width": 0.5,
        "edgecolor": "w",
    }

    #adding a subplot
    ax = fig.add_subplot(gs[position])

    #drawing a pie-chart
    wedges, texts, autotexts = ax.pie(y, labels=x, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.75, wedgeprops=wedgeprops)

    #setting a title to the pie-chart
    ax.set_title(title)

    #excluding from rendering labels for small results so that they don't overlap
    for i, (value, text, autotext) in enumerate(zip(y, texts, autotexts)):
        percentage = (value / sum(y)) * 100
        if percentage < 1:
            texts[i].set_text('')
            autotext.set_text('')

    #modify the color of the percents texts depending on the background color
    for autotext, color in zip(autotexts, colors):
        autotext.set_color('white' if sum(color[:3]) < 1.0 else 'black')
    
    return wedges