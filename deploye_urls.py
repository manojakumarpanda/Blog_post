"""icaap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from django.conf.urls import include,url
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('access/', include('usermanagement.urls')),
    path('materiality-assessment/', include('materiality_assessment.urls')),
    path('business-plan/',include('business_plan.urls')),
    path('pillar1/',include('pillar1.urls')),
    path('pillar2/',include('pillar2.urls')),
    path('stress-testing/',include('stress_testing.urls')),
    path('capital-planning/',include('capital_planing.urls')),
    path('reporting/',include('reporting.urls')),
    url(r'^$', RedirectView.as_view(url='login')),
    url(r'^login$', TemplateView.as_view(template_name='login/login.html')),
    url(r'^forgot-password$', TemplateView.as_view(template_name='login/forgot-password.html')),
	url(r'^recover-password$', TemplateView.as_view(template_name='login/new_password.html')),
###app_setting
url(r'^app-config$', TemplateView.as_view(template_name='app config/config_app.html')),

###Sidebar
url(r'^icaap_sidebar-sidebar$', TemplateView.as_view(template_name='icaap_sidebar/sidebar.html')),

###topbar
url(r'^icaap_topbar-topbar$', TemplateView.as_view(template_name='icaap_topbar/topbar.html')),

###profilepopup
url(r'^icaap_profile-popup$', TemplateView.as_view(template_name='profile_popup/profile_popup.html')),

###footer
url(r'^icaap_footer-footer$', TemplateView.as_view(template_name='icaap_footer/footer.html')),

###Materiality Assessment
    url(r'^governance-materiality-assessment$', TemplateView.as_view(template_name='material_assesment/Materiality_Assesment.html')),	
    url(r'^governance-new-assessment$', TemplateView.as_view(template_name='material_assesment/new_assesment.html')),	
    url(r'^governance-materiality-assessment-riskmapping$', TemplateView.as_view(template_name='material_assesment/activity_risk.html')),	
    url(r'^governance-materiality-assessment-approvals$', TemplateView.as_view(template_name='material_assesment/approval.html')),	
    url(r'^governance-materiality-assessment-assessment$', TemplateView.as_view(template_name='material_assesment/assesment.html')),	
    url(r'^governance-materiality-assessment-materialriskuniverse$', TemplateView.as_view(template_name='material_assesment/material_risk_universe.html')),	
    url(r'^governance-materiality-assessment-riskconfig$', TemplateView.as_view(template_name='material_assesment/risk_config.html')),	
    url(r'^governance-materiality-assessment-riskfactor$', TemplateView.as_view(template_name='material_assesment/risk_factor.html')),	
    url(r'^governance-materiality-assessment-riskfactorconfig$', TemplateView.as_view(template_name='material_assesment/risk_factor_config.html')),	
    url(r'^governance-materiality-assessment-risktree$', TemplateView.as_view(template_name='material_assesment/risk_tree.html')),	
    url(r'^governance-materiality-assessment-significantactivities$', TemplateView.as_view(template_name='material_assesment/significant_activity.html')),	
    url(r'^governance-materiality-assessment-reviewignificantactivies$', TemplateView.as_view(template_name='material_assesment/significant_output.html')),	
    url(r'^governance-materiality-assessment-summary$', TemplateView.as_view(template_name='material_assesment/summary.html')),
### Business Plan
    url(r'^business-plan$', TemplateView.as_view(template_name='bussiness_plan/bussiness.html')),		
    url(r'^business-plan-assessment-approvals$', TemplateView.as_view(template_name='bussiness_plan/bussiness_approval.html')),	
    url(r'^business-plan-assessment$', TemplateView.as_view(template_name='bussiness_plan/bussiness_assesment.html')),	
    url(r'^business-plan-new-assessment$', TemplateView.as_view(template_name='bussiness_plan/new-assesment.html')),	
    url(r'^business-plan-input-configuration$', TemplateView.as_view(template_name='bussiness_plan/input_configuration.html')),	
    url(r'^business-plan-pl-items$', TemplateView.as_view(template_name='bussiness_plan/pl_items.html')),	
    url(r'^business-plan-bs-items$', TemplateView.as_view(template_name='bussiness_plan/bs_items.html')),	
    url(r'^business-plan-review$', TemplateView.as_view(template_name='bussiness_plan/review.html')),	
    url(r'^business-plan-output$', TemplateView.as_view(template_name='bussiness_plan/output.html')),	
    url(r'^business-plan-summary$', TemplateView.as_view(template_name='bussiness_plan/bussiness_summary.html')),	   
	
## Pilar2
url(r'^pillar2$', TemplateView.as_view(template_name='pillar2/landing_page.html')),
url(r'^pillar2-past-assessment$', TemplateView.as_view(template_name='pillar2/past_assessment.html')),
url(r'^pillar2-residual-credit-risk-output$', TemplateView.as_view(template_name='pillar2/residual_risk_output.html')),
url(r'^pillar2-residual-credit-risk$', TemplateView.as_view(template_name='pillar2/residual_credit_risk.html')),
url(r'^pillar2-concentration-risk-loan-book-config$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab1.html')),
url(r'^pillar2-irrbb$', TemplateView.as_view(template_name='pillar2/irrbb.html')),
url(r'^pillar2-model-risk$', TemplateView.as_view(template_name='pillar2/model_risk.html')),
url(r'^pillar2-model-risk-output$', TemplateView.as_view(template_name='pillar2/model_risk_output.html')),
url(r'^pillar2-technology-risk$', TemplateView.as_view(template_name='pillar2/technology_risk.html')),
url(r'^pillar2-technology-risk-output$', TemplateView.as_view(template_name='pillar2/technology_risk_output.html')),
url(r'^pillar2-liquidity-risk-structural-statement$', TemplateView.as_view(template_name='pillar2/structural_liquidity_statement.html')),
url(r'^pillar2-liquidity-risk-structural-statement-output$', TemplateView.as_view(template_name='pillar2/structural_liquidity_statement_output.html')),
url(r'^pillar2-liquidity-risk-scorecard$', TemplateView.as_view(template_name='pillar2/liquidity_risk_scorecard.html')),
url(r'^pillar2-liquidity-risk-output$', TemplateView.as_view(template_name='pillar2/liquidity_risk_output.html')),
url(r'^pillar2-compliance-risk$', TemplateView.as_view(template_name='pillar2/compliance_risk.html')),
url(r'^pillar2-compliance-risk-output$', TemplateView.as_view(template_name='pillar2/compliance_risk_output.html')),
url(r'^pillar2-reputation-risk$', TemplateView.as_view(template_name='pillar2/reputation_risk.html')),
url(r'^pillar2-reputation-risk-output$', TemplateView.as_view(template_name='pillar2/reputation_risk_output.html')),
url(r'^pillar2-conduct-risk$', TemplateView.as_view(template_name='pillar2/conduct_risk.html')),
url(r'^pillar2-conduct-risk-output$', TemplateView.as_view(template_name='pillar2/conduct_risk_output.html')),
url(r'^pillar2-settlement-risk$', TemplateView.as_view(template_name='pillar2/settlement_risk.html')),
url(r'^pillar2-settlement-risk-output$', TemplateView.as_view(template_name='pillar2/settlement_risk_output.html')),
url(r'^pillar2-strategic-risk$', TemplateView.as_view(template_name='pillar2/strategic_risk.html')),
url(r'^pillar2-strategic-risk-output$', TemplateView.as_view(template_name='pillar2/strategic_risk_output.html')),
url(r'^pillar2-concentration-risk-loan-book-summary$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab_2.html')),
url(r'^pillar2-concentration-risk-loan-book-output$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab_3.html')),
url(r'^pillar2-concentration-risk-proprietary-trading-config$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab_4.html')),
url(r'^pillar2-concentration-risk-proprietary-trading-summary$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab_5.html')),
url(r'^pillar2-concentration-risk-proprietary-trading-output$', TemplateView.as_view(template_name='pillar2/concentration_risk_tab_6.html')),
##standardizedapproch
url(r'^pillar2-irrbb-config$', TemplateView.as_view(template_name='pillar2/standardized_approach_landing.html')), # slide 1 / 5
url(r'^pillar2-irrbb-yield-summary$', TemplateView.as_view(template_name='pillar2/standardized_approach_tab1.html')), # slide 2/6
url(r'^pillar2-irrbb-shock-types$', TemplateView.as_view(template_name='pillar2/standardized_approach_tab2.html')), # slide 3 / 7
url(r'^pillar2-irrbb-standardized-approach-shockwise-exposure$', TemplateView.as_view(template_name='pillar2/standardized_approach_tab3.html')),
url(r'^pillar2-irrbb-output$', TemplateView.as_view(template_name='pillar2/standardized_approach_output.html')),# slide 5 / 9

##duration_gap
url(r'^pillar2-irrbb-duration-gap-config$', TemplateView.as_view(template_name='pillar2/duration_gap_landing.html')), # slide 9
url(r'^pillar2-irrbb-duration-gap-yield-summary$', TemplateView.as_view(template_name='pillar2/duration_gap_tab1.html')), # slide 10
url(r'^pillar2-irrbb-duration-gap-summary$', TemplateView.as_view(template_name='pillar2/duration_gap_tab2.html')), # slide 11
url(r'^pillar2-irrbb-duration-gap-shock-types$', TemplateView.as_view(template_name='pillar2/duration_gap_tab3.html')), # slide 14
url(r'^pillar2-irrbb-duration-gap-shockwise-exposure$', TemplateView.as_view(template_name='pillar2/duration_gap_tab4.html')),
url(r'^pillar2-irrbb-duration-output$', TemplateView.as_view(template_name='pillar2/duration_gap_output.html')), # slide 16

url(r'^pillar2-summary$', TemplateView.as_view(template_name='pillar2/rwa_summary.html')),
url(r'^pillar2-testing$', TemplateView.as_view(template_name='pillar2/demo.html')),
url(r'^pillar2-tab1$', TemplateView.as_view(template_name='pillar2/demo.html')),

##pillar1
url(r'^pillar1$', TemplateView.as_view(template_name='pillar1/landing_page.html')),
url(r'^pillar1-credit-risk-on-blancesheet$', TemplateView.as_view(template_name='pillar1/credit_risk_on_balancesheet.html')), # Tab 1
url(r'^pillar1-credit-risk-off-balancesheet$', TemplateView.as_view(template_name='pillar1/credit_risk_off_balancesheet.html')), #Tab 2
url(r'^pillar1-credit-risk-crm-parameters$', TemplateView.as_view(template_name='pillar1/credit_risk_crm_parameters.html')), # Tab 3
url(r'^pillar1-credit-risk-output$', TemplateView.as_view(template_name='pillar1/credit_risk_output.html')),
url(r'^pillar1-credit-risk-dashboard$', TemplateView.as_view(template_name='pillar1/credit_risk_dashboard.html')),
url(r'^pillar1-past-assessment$', TemplateView.as_view(template_name='pillar1/past_assessment.html')),
## Pillar 1 - Market Risk
url(r'^pillar1-market-risk-interest-rate-risk$', TemplateView.as_view(template_name='pillar1/market_risk_interest_rate_risk.html')),
url(r'^pillar1-market-risk-forex-risk$', TemplateView.as_view(template_name='pillar1/market_risk_forex_risk.html')),
url(r'^pillar1-market-risk-equity-price-risk$', TemplateView.as_view(template_name='pillar1/market_risk_equity_price_risk.html')),
url(r'^pillar1-market-risk-output$', TemplateView.as_view(template_name='pillar1/market_risk_output.html')), 	
url(r'^pillar1-market-risk-dashboard$', TemplateView.as_view(template_name='pillar1/market_risk_dashboard.html')), 	
## Pillar 1 - Operational Risk
url(r'^pillar1-operational-risk-indicator-approach-input-configuration$', TemplateView.as_view(template_name='pillar1/operational_risk_indicator_approach_input_conf.html')),
url(r'^pillar1-operational-risk-indicator-approach-output$', TemplateView.as_view(template_name='pillar1/operational_risk_indicator_approach_output.html')),
url(r'^pillar1-operational-risk-indicator-approach-dashboard$', TemplateView.as_view(template_name='pillar1/operational_risk_indicator_approach_dashboard.html')),
url(r'^pillar1-operational-risk-standardized-approach-input-configuration$', TemplateView.as_view(template_name='pillar1/operational_risk_standardized_approach_input_conf.html')),
url(r'^pillar1-operational-risk-standardized-approach-summary$', TemplateView.as_view(template_name='pillar1/operational_risk_standardized_approach_summary.html')),
url(r'^pillar1-operational-risk-standardized-approach-output$', TemplateView.as_view(template_name='pillar1/operational_risk_standardized_approach_output.html')),
url(r'^pillar1-operational-risk-standardized-approach-dashboard$', TemplateView.as_view(template_name='pillar1/operational_risk_standardized_approach_dashboard.html')),
url(r'^pillar1-rwa-forecasting$', TemplateView.as_view(template_name='pillar1/rwa_forecasting.html')),


### capital plan
    url(r'^capital-managment$', TemplateView.as_view(template_name='capital_planning/capital.html')),		
    url(r'^capital-managment-assessment-approvals$', TemplateView.as_view(template_name='capital_planning/capital_approval.html')),	
    url(r'^capital-managment-assessment$', TemplateView.as_view(template_name='capital_planning/capital_assesment.html')),	
    url(r'^capital-managment-new-assessment$', TemplateView.as_view(template_name='capital_planning/new_assessment.html')),	
    url(r'^capital-managment-rwa-configuration$', TemplateView.as_view(template_name='capital_planning/RWA_config.html')),	
    url(r'^capital-managment-capital-computation$', TemplateView.as_view(template_name='capital_planning/capital_computation.html')),	
    url(r'^capital-managment-summary$', TemplateView.as_view(template_name='capital_planning/capital_summary.html')),	
    url(r'^capital-bussiness-plan$', TemplateView.as_view(template_name='capital_planning/bussiness_plan_details.html')),	
	

### stress-testing plan
	
 url(r'^stress-testing$', TemplateView.as_view(template_name='stress_testing/stress_landing.html')),  
 url(r'^stress-past-assesment$', TemplateView.as_view(template_name='stress_testing/stress_past_assesment.html')), 
 ### stress-testing pillar2
 url(r'^stress-testing-pillar2-IRRBB-duration-gap-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_duration_gap_input.html')),
 url(r'^stress-testing-pillar2-IRRBB-duration-gap-output$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_duration_gap_output.html')),
 url(r'^stress-testing-pillar2-IRRBB-standardized-basel-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_standarized_basel_input.html')),
 url(r'^stress-testing-pillar2-IRRBB-standardized-basel-output$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_standarized_basel_output.html')), 
 url(r'^stress-testing-pillar2-IRRBB-standardized-manual-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_standarized_manual_input.html')),
 url(r'^stress-testing-pillar2-IRRBB-standardized-manual-output$', TemplateView.as_view(template_name='stress_testing/pillar2-irrbb_standarized_manual_output.html')), 
 url(r'^stress-testing-pillar2-scorecard-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-stress_scorecard.html')),
 url(r'^stress-testing-pillar2-concentration-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-stress_concentration_risk.html')), 
 url(r'^stress-testing-pillar2-residual-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-residual_input.html')), 
 url(r'^stress-testing-pillar2-residual-output$', TemplateView.as_view(template_name='stress_testing/pillar2-residual_output.html')), 
 url(r'^stress-testing-pillar2-liquidity-SLS-statement-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_SLS_statement_inputconfig.html')),
 url(r'^stress-testing-pillar2-liquidity-SLS-statement-value$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_SLS_statement_inputconfig_value.html')),
 url(r'^stress-testing-pillar2-liquidity-SLS-statement-output$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_SLS_statement_output.html')),
 url(r'^stress-testing-pillar2-liquidity-SLS-output$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_SLS_output.html')),
 url(r'^stress-testing-pillar2-liquidity-LCR-statement-input-configuration$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_LCR_statement_inputconfig.html')), 
 url(r'^stress-testing-pillar2-liquidity-LCR-cashflow$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_risk_LCR_inflow_outflow.html')),
 url(r'^stress-testing-pillar2-liquidity-output$', TemplateView.as_view(template_name='stress_testing/pillar2-liquidity_output.html')), 
 url(r'^stress-testing-summary$', TemplateView.as_view(template_name='stress_testing/stress_testing_summary.html')),
  ### stress-testing credit risk pillar1
   url(r'^stress-testing-pillar1-credit_risk$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_aggregator.html')),
   url(r'^stress-testing-pillar1-credit_shock1$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_1.html')),
   url(r'^stress-testing-pillar1-credit_shock2$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_2.html')),
   url(r'^stress-testing-pillar1-credit_shock3$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_3.html')),
   url(r'^stress-testing-pillar1-credit_shock4$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_4.html')),
   url(r'^stress-testing-pillar1-credit_shock5$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_5.html')),
   url(r'^stress-testing-pillar1-credit_shock6$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_shock_6.html')),
   url(r'^stress-testing-pillar1-credit_output$', TemplateView.as_view(template_name='stress_testing/pillar1_credit_risk_output.html')),
     ### stress-testing market risk pillar1
     url(r'^stress-testing-pillar1-market_risk$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_ aggregator.html')),
   url(r'^stress-testing-pillar1-market_shock1$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_1.html')),
   url(r'^stress-testing-pillar1-market_shock2$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_2.html')),
   url(r'^stress-testing-pillar1-market_shock3$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_3.html')),
   url(r'^stress-testing-pillar1-market_shock4$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_4.html')),
   url(r'^stress-testing-pillar1-market_shock5$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_5.html')),
   url(r'^stress-testing-pillar1-market_shock6$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_shock_6.html')),
   url(r'^stress-testing-pillar1-market_output$', TemplateView.as_view(template_name='stress_testing/pillar1_market_risk_output.html')),
   
        ### stress-testing operational risk pillar1
		   url(r'^stress-testing-operational-risk$', TemplateView.as_view(template_name='stress_testing/operational_risk_shock.html')),
		   url(r'^stress-testing-operational-risk-output$', TemplateView.as_view(template_name='stress_testing/operational_risk_shock_output.html')),   
		    ### stress-testing  pillar1 summary
		   url(r'^stress-testing-pillar1-summary$', TemplateView.as_view(template_name='stress_testing/pillar1_summary.html')), 

		   ### reporting
		   url(r'^reporting$', TemplateView.as_view(template_name='reporting/reporting_landing.html')),
		   url(r'^reporting-past-assessment$', TemplateView.as_view(template_name='reporting/reporting_past_assessment.html')),	
		   url(r'^reporting-risk-quantification$', TemplateView.as_view(template_name='reporting/reporting_risk_quantification.html')),
		   url(r'^reporting-stress-testing$', TemplateView.as_view(template_name='reporting/reporting_stress_testing.html')),
		   url(r'^reporting-capital-management$', TemplateView.as_view(template_name='reporting/reporting_capital_management.html')),

]
