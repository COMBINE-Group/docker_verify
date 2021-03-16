from django.urls import path
from . import views

urlpatterns = [
    path('', views.verify, name='verify'),
    path('verify_sobol_analysis/', views.verify_sobol, name='verify_sobol_analysis'),
    path('runTime_step_analysis/', views.time_step_analysis, name='run-time_step_analysis'),
    path('runUniqueness_analysis/', views.uniqueness_analysis, name='run-uniqueness_analysis'),
    path('runSmoothness_analysis/', views.smoothness_analysis, name='run-smoothness_analysis'),
    path('checkSimulationVerify/', views.check_simulations, name='check-simulations-verify'),
    path('readInfoSimulationVerify/', views.read_info_simulation, name='read-info-simulation-verify'),
    path('runSobol_analysis/', views.sobol_generates_sample, name='sobol_generates_sample'),
    path('runSobol_analyze/', views.sobol_analyze, name='sobol-analyze'),
    path('verify_lhs-prcc/', views.verify_lhs_prcc, name='verify_lhs_prcc'),
    path('runLHS/', views.lhs_analysis, name='run_lhs'),
    path('runPRCC/', views.prcc_analysis, name='run_prcc'),

]
