from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileSerializer
from .models import *
import scipy as sp
from scipy.io.wavfile import read
from scipy.io.wavfile import write     # Imported libaries such as numpy, scipy(read, write), matplotlib.pyplot
from scipy import signal
import glob
import os
import numpy
from file_upload_drf import settings


def noise_reduction(wavFile):
    print(wavFile)
    try:
        (Frequency, samples)=read(wavFile)
        print(Frequency)
        FourierTransformation = sp.fft.fft(samples) # Calculating the fourier transformation of the signal
        scale = numpy.linspace(0, Frequency, len(samples))
        b,a = signal.butter(5, 1000/(Frequency/2), btype='highpass') # ButterWorth filter 4350
        filteredSignal = signal.lfilter(b,a,samples)
        c,d = signal.butter(5, 600/(Frequency/2), btype='lowpass') # ButterWorth low-filter
        newFilteredSignal = signal.lfilter(c,d,filteredSignal) # Applying the filter to the signal
        write(f"{settings.MEDIA_ROOT}\\reduce_noise.wav", Frequency, newFilteredSignal)
        return f"{settings.MEDIA_ROOT}\\reduce_noise.wav"
    except Exceptions as e:
        return "Error"


class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            print(file_serializer.data['file'])# get the file name
            modified_filePath = noise_reduction(settings.MEDIA_ROOT + file_serializer.data['file'].replace('media','').replace('/','\\'))
            data = file_serializer.data
            data['NoiseReduce_file'] = modified_filePath
            print(data)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


