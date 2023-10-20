from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
import pandas as pd
from rest_framework import views, serializers
from diagrams.models import Molecules, Datasets
from datetime import datetime

class MoleculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecules
        fields = [
            "dataset",
            "rna_type",
            "length",
            "name",
            "license_plate",
            "unnormalized_read_counts",
        ]

class DeleteAllDatasetsView(views.APIView):
    def delete(self, request):
        Datasets.objects.all().delete()
        Molecules.objects.all().delete()
        return Response({})

class DeleteDatasetView(views.APIView):
    def delete(self, request, datasetname):
        Datasets.objects.filter(name=datasetname).delete()
        Molecules.objects.filter(dataset=datasetname).delete()
        return Response({})


class UploadDatasetView(views.APIView):

    parser_classes = [FileUploadParser]
    
    # Creates dataset object and uploads data from .tsv file into the database
    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        raw_df = pd.read_csv(file_obj, sep='\t')
        df = pd.DataFrame()

        #parsing RNA's type, lenght and 'name'
        df[["rna_type", "length", "name"]] = raw_df["License Plate"].str.split(n=3, pat="-", expand=True)
        df[["license_plate", "unnormalized_read_counts"]] = raw_df[["License Plate", "Unnormalized read counts"]]


        Datasets.objects.create(name=filename)


        dicts = df.to_dict(orient='records')
        successfull = 0
        unsuccessfull = 0
        start = datetime.now()
        for dict in dicts:
            dict["dataset"] = filename
            serializer = MoleculeSerializer(data=dict)
            if serializer.is_valid():
                Molecules.objects.create(**serializer.validated_data)
                successfull += 1
            else:
                unsuccessfull +=1
        finish = datetime.now()
        delta = finish - start
        return Response({"successfully added molecules": successfull, "unsuccessfully added molecules": unsuccessfull, "time spent": delta.total_seconds()})

# class ExportResultsView(views.APIView):
#     def post(self, request, )