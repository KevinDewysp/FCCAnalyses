import ROOT

# global parameters
intLumi = 10.8
intLumiLabel = "L = 10.8 ab^{-1}"
ana_tex = "e^{+}e^{-} #rightarrow ZH #rightarrow ij + X"
delphesVersion = "3.4.2"
energy = 240.0
collider = "FCC-ee"
inputDir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/final/"
formats = ["png", "pdf"]
outdir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/plot/"
plotStatUnc = True

colors = {}
colors["ZH"] = ROOT.kRed
colors["ZZ"] = ROOT.kGreen + 2
colors["WW"] = ROOT.kBlue + 2
colors["Zqq"] = ROOT.kOrange + 2

procs = {}
procs["signal"] = {"ZH": ["wzp6_ee_qqH_ecm240"]}
procs["backgrounds"] = {"ZZ": ["p8_ee_ZZ_ecm240"],
                        "WW": ["p8_ee_WW_ecm240"],
                        "Zqq": ["p8_ee_Zqq_ecm240"]}

legend = {}
legend["ZH"] = "ZH"
legend["ZZ"] = "ZZ"
legend["WW"] = "WW"
legend["Zqq"] = "Zqq"

hists = {}

hists["zed_hadronic_recoil_m"] = {
    "output": "zed_hadronic_recoil_m",
    "logy": False,
    "stack": True,
    "rebin": 1,
    "xmin": 0,
    "xmax": 200,
    "ymin": 0,
    "ymax": 2000,
    "xtitle": "Recoil (GeV)",
    "ytitle": "Events / 1 MeV",
}

hists["Z_hadronic_m"] = {
    "output": "Z_hadronic_m",
    "logy": False,
    "stack": True,
    "rebin": 1,
    "xmin": 0,
    "xmax": 200,
    "ymin": 0,
    "ymax": 4000,
    "xtitle": "Z_hadronic_m (GeV)",
    "ytitle": "Events / 2 GeV",
}

# hists["scoresum_B"] = {
#     "output": "scoresum_B",
#     "logy": True,
#     "stack": False,
#     "rebin": 1,
#     "xmin": 0,
#     "xmax": 2.0,
#     "ymin": 1,
#     "ymax": 100000,
#     "xtitle": "p_{1}(B) + p_{2}(B)",
#     "ytitle": "Events",
# }