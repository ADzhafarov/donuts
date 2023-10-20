from django.shortcuts import HttpResponse
from jinja2 import Environment, PackageLoader, select_autoescape
from diagrams.models import Datasets, Molecules
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import random
import io
import base64
import json


def donuts(request):
    env = Environment(
        loader=PackageLoader("diagrams"),
        autoescape=select_autoescape()
    )
    context = {}

    datasets = [dataset.name for dataset in list(Datasets.objects.all())]
    context['datasets'] = datasets
    if 'sample' in request.GET.keys():
        context['sample'] = True
        dataset = request.GET["sample"]
        df = pd.DataFrame(list(Molecules.objects.filter(dataset=dataset).values('rna_type', 'unnormalized_read_counts')))
        agg_func_with_abundances = {
            'unnormalized_read_counts': ['sum']
        }
        agg_func_unique = {
            'unnormalized_read_counts': ['count']
        }
        df_stat_with_abundances = df.groupby(['rna_type']).agg(agg_func_with_abundances)
        df_stat_unique = df.groupby(['rna_type']).agg(agg_func_unique)

        array = [1, 2, 3, 4]
        labels = df_stat_with_abundances.index.values.tolist()
        abundances = df_stat_with_abundances["unnormalized_read_counts"].values.reshape(1, -1).tolist()[0]
        unique_values = df_stat_unique["unnormalized_read_counts"].values.reshape(1, -1).tolist()[0]

        plot = base64_plot(labels, abundances, unique_values, dataset)
        context['plot'] = plot
        context['results'] = json.dumps(todict(labels, abundances, unique_values))
        context['samplename'] = dataset
    else:
        context['sample'] = False
        context['samplename'] = ''
    template = env.get_template("donuts.html")
    return HttpResponse(template.render(**context))    


def base64_plot(x, y, z, dataset):
    num_groups = len(x)
    colors = [plt.cm.viridis(i / num_groups) for i in range(num_groups)]

    fig = plt.figure(figsize=(14, 8))
    gs = GridSpec(1, 3, width_ratios=[3, 3, 1])

    explode = [0.05 for i in range(num_groups)]

    wedgeprops = {
        "width": 0.5,
        "edgecolor": "w",
    }

    ax1 = fig.add_subplot(gs[0])
    wedges1, texts1, autotexts1 = ax1.pie(y, labels=x, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.75, wedgeprops=wedgeprops)
    ax1.set_title('% sequences/molecules across types\n\n')

    for i, (value, text, autotext) in enumerate(zip(y, texts1, autotexts1)):
        percentage = (value / sum(y)) * 100
        if percentage < 1:
            texts1[i].set_text('')
            autotext.set_text('')
            
    for autotext, color in zip(autotexts1, colors):
        autotext.set_color('white' if sum(color[:3]) < 1.0 else 'black')

    ax2 = fig.add_subplot(gs[1])
    wedges2, texts2, autotexts2 = ax2.pie(z, labels=x, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.75, wedgeprops=wedgeprops)
    ax2.set_title('% \'unique\' sequences/molecule across types\n\n')

    for i, (value, text, autotext) in enumerate(zip(z, texts2, autotexts2)):
        percentage = (value / sum(z)) * 100
        if percentage < 1:
            texts2[i].set_text('')
            autotext.set_text('')
    
    for autotext, color in zip(autotexts2, colors):
        autotext.set_color('white' if sum(color[:3]) < 1.0 else 'black')

    ax3 = fig.add_subplot(gs[2])
    ax3.legend(wedges2, x, title='Legend', loc='center', bbox_to_anchor=(0.5, 0.5))
    ax3.set_axis_off()
    
    plt.suptitle('Sample: ' + dataset, fontsize=16)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.read()).decode()

def todict(labels, abundances, unique_values):
    ab = {}
    un = {}
    for i in range(len(labels)):
        ab[i] = {labels[i]: abundances[i]}
        un[i] = {labels[i]: unique_values[i]}
    return {"abundances": ab, "unique": un}
