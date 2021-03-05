from django.conf import settings
from django.shortcuts import render
from utilities.tools import check_status_simulation, check_content_type, create_simulation_folder, \
    get_plot_trends_convergence_corr
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
import os
import threading


def verify_lhs_prcc(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_lhs_prcc_gen.html', data)


def verify_sobol(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_sobol_gen.html', data)


def verify(response):
    data = {
        'appname': 'verify',
        'title': 'VERIFY',
        'media_path': settings.MEDIA_URL,
    }

    return render(response, 'verify/verify_gen.html', data)


def check_simulations(request):
    if request.method == 'POST':
        return check_status_simulation(settings.BASE_DIR_VERIFY, settings.MEDIA_DIR_VERIFY, request.user.username,
                                       request.POST['name_analysis'])


def read_info_simulation(request):
    return None


def time_step_analysis(request):
    if request.method == 'POST':
        if len(request.FILES.getlist('file')) >= 2:
            if check_content_type(request.FILES.getlist('file'), 'text/csv,application/octet-stream'):
                starttime = 0

                fs = FileSystemStorage()
                create_simulation_folder(settings.MEDIA_DIR_VERIFY, 'Anonymous', request.POST['name_analysis'])

                list_files_uploaded = []
                for f in request.FILES.getlist('file'):
                    fs.save(os.path.join(os.getcwd(), f.name), f)
                    list_files_uploaded.append(f.name)

                new_list_files = []
                for i, f in enumerate(list_files_uploaded):
                    df = pd.read_csv(f, comment='#', sep='\s+', header=None, engine='c', na_filter=False,
                                     low_memory=False)
                    if df.shape[1] == 1:
                        df = pd.read_csv(f, comment='#', sep=',', header=None, engine='c', na_filter=False,
                                         low_memory=False)
                        df.to_csv(os.path.join(os.getcwd(), f'file_convert_{i + 1}.csv'), sep='\t', mode='w',
                                  header=False, index=False)
                        new_list_files.append(os.path.join(os.getcwd(), f'file_convert_{i + 1}.csv'))
                    else:
                        new_list_files.append(os.path.join(os.getcwd(), f))

                col = int(request.POST['column_select'])
                if col > 1:
                    col = col - 1

                thread = threading.Thread(
                    target=get_plot_trends_convergence_corr('fig', new_list_files, col, starttime))
                thread.start()

                os.chdir(settings.BASE_DIR_VERIFY)

                return JsonResponse({'status': 1, 'type': 'success', 'title': '<u>Completed</u>',
                                     'mess': ''})
            else:
                return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                     'mess': 'There was a problem during execution!'})
        else:
            return JsonResponse({'status': 0, 'type': 'error', 'title': 'Error!',
                                 'mess': 'You need to select more than two files'})
