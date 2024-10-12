
# list of processes (mandatory)
processList = {
    # Signal
    'wzp6_ee_qqH_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    # Background
    'p8_ee_ZZ_ecm240': {'fraction': 0.001 ,'chunks': 1, },
    'p8_ee_WW_ecm240': {'fraction': 0.001 ,'chunks': 1,},
    'p8_ee_Zqq_ecm240': {'fraction': 0.001 ,'chunks': 1,},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
#prodTag = "FCCee/winter2023/IDEA/"

# Link to the dictonary that contains all the cross section informations etc... (mandatory)
procDict = "FCCee_procDict_winter2023_IDEA.json"

# Define the input dir (optional)
inputDir    = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/"

# Optional: output directory, default is local running directory
outputDir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq/final_1/"


# optional: ncpus, default is 4, -1 uses all cores available
nCPUS = -1

# scale the histograms with the cross-section and integrated luminosity
doScale = True
intLumi = 10800000  # 10.8 /ab


# define some binning for various histograms
bins_p_mu = (2, 0, 200)  # 100 MeV bins
bins_p_ll = (2, 0, 200)  # 100 MeV bins
bins_cosThetaMiss = (10000, 0, 1)

bins_m_jj = (100, 50, 150)  # 1 GeV bins
bins_score = (50, 0, 2.0)  #

bins_theta = (500, -5, 5)
bins_eta = (600, -3, 3)
bins_phi = (500, -5, 5)

bins_count = (50, 0, 50)
bins_charge = (10, -5, 5)
bins_iso = (500, 0, 5)


######
bins_m_ll = (200, 0, 200)  # 100 MeV bins
bins_m_ll_1 = (20, 86, 96)  # 100 MeV bins
bins_recoil = (60, 0, 200)  # 1 MeV bins
bins_recoil_1 = (60, 100, 160)  # 1 MeV bins
bins_recoil_2 = (40, 120, 140)  # 1 MeV bins
bins_recoil_3 = (200, 0, 300)  # 1 MeV bins


# build_graph function that contains the analysis logic, cuts and histograms (mandatory)
def build_graph(df, dataset):

    results = []
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")

    #########
    ### CUT 4: Z mass window
    #########
    df = df.Filter("Z_hadronic_m > 86 && Z_hadronic_m < 96")

    #########
    ### CUT 5: Z momentum
    #########
    # df = df.Filter("zmumu_p > 20 && zmumu_p < 70")

    #########
    ### CUT 6: recoil mass window
    #########
    # df = df.Filter("zed_hadronic_recoil_m < 160 && zed_hadronic_recoil_m > 100")

    #########
    ### CUT 7: cut on the jet tagging score to select H->bb events
    #########
    # df = df.Define("scoresum_B", "recojet_isB[0] + recojet_isB[1]")
    # results.append(df.Histo1D(("scoresum_B", "", *bins_score), "scoresum_B"))

    # df = df.Filter("scoresum_B > 1.0")

    results.append(df.Histo1D(("Z_hadronic_m", "", *bins_m_ll), "Z_hadronic_m"))
    results.append(df.Histo1D(("Z_hadronic_m_zoom1", "", *bins_m_ll_1), "Z_hadronic_m"))
    results.append(
        df.Histo1D(("zed_hadronic_recoil_m", "", *bins_recoil), "zed_hadronic_recoil_m")
    )
    results.append(
        df.Histo1D(("zed_hadronic_recoil_m_zoom1", "", *bins_recoil_1), "zed_hadronic_recoil_m")
    )
    results.append(
        df.Histo1D(("zed_hadronic_recoil_m_zoom2", "", *bins_recoil_2), "zed_hadronic_recoil_m")
    )
    results.append(
        df.Histo1D(("zed_hadronic_recoil_m_zoom3", "", *bins_recoil_3), "zed_hadronic_recoil_m")
    )
    # results.append(df.Histo1D(("zmumu_p", "", *bins_p_ll), "zmumu_p"))
    # results.append(df.Histo1D(("jj_m", "", *bins_m_jj), "jj_m"))

    return results, weightsum