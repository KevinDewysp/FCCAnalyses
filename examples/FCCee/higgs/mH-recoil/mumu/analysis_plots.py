import ROOT

# global parameters
intLumi        = 10.8e+06 #in pb-1
ana_tex        = "e^{+}e^{-} #rightarrow ZH #rightarrow ij + X"
delphesVersion = '3.4.2'
energy         = 240.0
collider       = 'FCC-ee'
inputDir       = '/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq/final_1/'
formats        = ['png','pdf']
yaxis          = ['lin','log']
stacksig       = ['stack','nostack']
outdir         = '/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq/plots_adapted/'
plotStatUnc    = True

variables = ['Z_hadronic_m', 'Z_hadronic_m_zoom1', 'zed_hadronic_recoil_m', 'zed_hadronic_recoil_m_zoom1', 'zed_hadronic_recoil_m_zoom2', 'zed_hadronic_recoil_m_zoom3']
rebin = [1, 1, 1, 1, 1, 1] # uniform rebin per variable (optional)

###Dictonnary with the analysis name as a key, and the list of selections to be plotted for this analysis. The name of the selections should be the same than in the final selection
selections = {}
selections['ZH']   = ["sel0","sel1","sel2"]
# selections['ZH_2'] = ["sel0"]

extralabel = {}
extralabel['sel0'] = "No_selection"
extralabel['sel1'] = "Selection: 86 GeV < m_{Z} < 96 GeV; 100 GeV < m_rec < 160 GeV;"
extralabel['sel2'] = "Selection: 86 GeV < m_{Z} < 96 GeV"

colors = {}
colors['ZH'] = ROOT.kRed
colors['WW'] = ROOT.kBlue+1
colors['ZZ'] = ROOT.kGreen+2
colors['Zqq'] = ROOT.kOrange+2

plots = {}
plots['ZH'] = {'signal':{'ZH':['wzp6_ee_qqH_ecm240']},
               'backgrounds':{'WW':['p8_ee_WW_ecm240'],
                              'ZZ':['p8_ee_ZZ_ecm240'],
                              'Zqq':['p8_ee_Zqq_ecm240'],}
           }


# plots['ZH_2'] = {'signal':{'ZH':['wzp6_ee_qqH_ecm240']},
#                  'backgrounds':{'VV':['p8_ee_WW_ecm240','p8_ee_ZZ_ecm240']}
#              }

legend = {}
legend['ZH'] = 'Z(qq)H'
legend['WW'] = 'WW'
legend['ZZ'] = 'ZZ'
legend['Zqq'] = 'Zqq'
