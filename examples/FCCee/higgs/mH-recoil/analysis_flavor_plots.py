import ROOT

# Global parameters
intLumi = 10.8
intLumiLabel = "L = 10.8 ab^{-1}"
ana_tex = "e^{+}e^{-} #rightarrow ZH #rightarrow ij + X"
delphesVersion = '3.4.2'
energy         = 240.0
collider       = 'FCC-ee'
inputDir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/final/"
formats        = ['png', 'pdf']
yaxis          = ['lin', 'log']
stacksig       = ['stack', 'nostack']
outdir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/plots/"
plotStatUnc    = True

variables = ['Z_hadronic_m',
             'zed_hadronic_recoil_m']
rebin = [1, 1]  # uniform rebin per variable (optional)

# Dictionary with the list of selections to be plotted for this analysis. The
# name of the selections should be the same than in the final selection
selections = {}
selections['ZH'] = ["sel0", "sel1"]
selections['ZH_2'] = ["sel0", "sel1"]
selections['ZH_3'] = ["sel0", "sel1"]
selections['ZH_4'] = ["sel0", "sel1"]
selections['ZH_5'] = ["sel0", "sel1"]

extralabel = {}
extralabel['sel0'] = "Selection: N_{Z} = 1"
extralabel['sel1'] = "Selection: N_{Z} = 1; 80 GeV < m_{Z} < 100 GeV"

colors = {}
colors['ZH'] = ROOT.kRed
colors['WW'] = ROOT.kBlue+1
colors['ZZ'] = ROOT.kGreen+2
colors['VV'] = ROOT.kGreen+3

plots = {}
plots['ZH'] = {'signal': {'ZH': ['MySample_p8_ee_ZH_ecm240']},
               'backgrounds': {'WW': ['p8_ee_WW_ecm240'],
                               'ZZ': ['p8_ee_ZZ_ecm240']}}

plots['ZH_2'] = {'signal': {'ZH': ['MySample_p8_ee_ZH_ecm240']},
                 'backgrounds': {'VV': ['p8_ee_WW_ecm240', 'p8_ee_ZZ_ecm240']}}

plots['ZH_3'] = {'signal': {'ZH': ['MySample_p8_ee_ZH_ecm240']}}

plots['ZH_4'] = {'backgrounds': {'VV': ['p8_ee_WW_ecm240', 'p8_ee_ZZ_ecm240']}}

plots['ZH_5'] = {'backgrounds': {'WW': ['p8_ee_WW_ecm240'],
                                 'ZZ': ['p8_ee_ZZ_ecm240']}}

legend = {}
legend['ZH'] = 'ZH'
legend['WW'] = 'WW'
legend['ZZ'] = 'ZZ'
legend['VV'] = 'VV boson'