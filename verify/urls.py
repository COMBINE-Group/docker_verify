from django.urls import path

from . import views

urlpatterns = [
    path('', views.verify_documentation, name='verify_documentation'),
    path('verify_sobol_analysis/', views.verify_sobol, name='verify_sobol_analysis'),
    path('verify_smoothness/', views.verify_smoothness, name='verify_smoothness_analysis'),
    path('verify_time_step/', views.verify_time_step, name='verify_timestep_analysis'),
    path('verify_existence_unique/', views.verify_unique_exist, name='verify_existence_unique'),
    path('runTime_step_analysis/', views.time_step_analysis, name='run-time_step_analysis'),
    path('runUniqueness_analysis/', views.uniqueness_analysis, name='run-uniqueness_analysis'),
    path('runSmoothness_analysis/', views.smoothness_analysis, name='run-smoothness_analysis'),
    path('checkSimulationVerify/', views.check_simulations, name='check-simulations-verify'),
    path('deleteSimulationVerify/', views.delete_simulations, name='delete-simulations-verify'),
    path('readInfoSimulationVerify/', views.read_info_simulation, name='read-info-simulation-verify'),
    path('runSobol_analysis/', views.sobol_generates_sample, name='sobol_generates_sample'),
    path('runSobol_analyze/', views.sobol_analyze, name='sobol-analyze'),
    path('verify_lhs-prcc/', views.verify_lhs_prcc, name='verify_lhs_prcc'),
    path('runLHS/', views.lhs_analysis, name='run_lhs'),
    path('runPRCC/', views.prcc_analysis, name='run_prcc'),
    path('runPRCCts/', views.prcc_analysis_specific_ts, name='url_run_prcc_analysis_specific_ts'),

]
